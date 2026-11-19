"""mashcover.py: text-coverage sweep over the debug map list (scene -> boy/dog/cat -> scenario -> page -> row).

    python -X utf8 tools/debug/mashcover.py [ROM] [--chars 0,1,2] [--scenarios 1,2,3,4] [--extra-pages 2]
                                           [--jobs 8] [--out work/qa/cover_mash] [--presses 60]

Each run warps into one map-list row (the program of tools/debug/maplist.py, with right*C on the character select),
then mashes A and walks in a fixed pattern (map-entry events, nearby NPCs, exits), with tools/debug/textlog.lua
logging every string the text engine expands, and tools/debug/entryname.lua starting every NPC object script
(NearScript with a message call, listed in <out>/npcs.txt) at its NearScript, so the NPCs say their lines as they
spawn (--no-npc: plain mash). Every run has its own <out>/<tag>/log.txt, so textcover.py reads the whole
directory: `textcover.py work/qa/cover build/strings.tsv`. Pages per scenario come from docs/re/maplist.tsv (boy);
dog and cat get --extra-pages more (their lists wrap, repeats only cost time). Runs whose log.txt exists are skipped
(delete the directory to redo).
"""
import argparse
import csv
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
from make_save import blank_save  # noqa: E402

WALK = ["hup:40", "hleft:40", "hdown:40", "hright:40", "hup:80", "hright:80", "hdown:80", "hleft:80"]


def program(c, s, p, r, presses):
    keys = ["f2612 w30 a w120"]
    if c:
        keys.append(f"right*{c}")
    keys.append("a w100")
    if s > 1:
        keys.append(f"down*{s - 1}")
    keys.append("a w100")
    if p > 1:
        keys.append(f"right*{p - 1} w30")
    if r:
        keys.append(f"down*{r}")
    keys.append("a w400")
    keys += ["a w20"] * presses
    for i in range(presses // 2):
        keys += [WALK[i % len(WALK)], "a w20", "a w20"]
    return "debug:" + " ".join(keys)


def npc_ids():
    """Object scripts whose NearScript calls a message function (their talk text)."""
    import filedata
    import romfs
    import scrrefs
    out = []
    for fid, data in enumerate(filedata.files(romfs.load().getFileByName("FILEDATA.BIN"))):
        if data[:4] == b"SCR0" and any(fn == "NearScript" and nm in scrrefs.MSG_CALLS
                                       for fn, nm, _ in scrrefs.calls(data)):
            out.append(fid)
    return out


def run(rom, out, c, s, p, r, presses, npcfile=None):
    d = out / f"c{c}s{s}p{p}r{r}"
    if (d / "log.txt").exists():
        return d.name, "skip"
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--script", str(ROOT / "tools" / "debug" / "textlog.lua"),
           *(["--script", str(ROOT / "tools" / "debug" / "entryname.lua"),
              "--var", f"NPCFILE='{npcfile.as_posix()}'"] if npcfile else []),
           "--var", f"SCENE='{program(c, s, p, r, presses)}'",
           "--var", "STOP_AFTER=10", "--frames", "16000", "--timeout", "300",  # a full run takes 45-80 s
 "--sav", str(blank_save())]
    pr = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    return d.name, f"exit {pr.returncode} text {log.count('TEXT ')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "sakuranote_en.nds"))
    ap.add_argument("--chars", default="0,1,2")
    ap.add_argument("--scenarios", default="1,2,3,4")
    ap.add_argument("--extra-pages", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--presses", type=int, default=60)
    ap.add_argument("--no-npc", action="store_true", help="leave NPC scripts at StartScript (plain mash)")
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "cover" / "map"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    npcfile = None
    if not a.no_npc:
        npcfile = out / "npcs.txt"
        npcfile.write_text(" ".join(map(str, npc_ids())) + "\n", encoding="utf-8")
    with open(ROOT / "docs" / "re" / "maplist.tsv", encoding="utf-8", newline="") as f:
        pages = Counter(int(row["scenario"]) for row in csv.DictReader(f, delimiter="\t"))
    jobs = []
    for c in [int(x) for x in a.chars.split(",")]:
        for s in [int(x) for x in a.scenarios.split(",")]:
            n = pages[s] // 6 + (a.extra_pages if c else 0)
            jobs += [(c, s, p, r) for p in range(1, n + 1) for r in range(6)]
    with ThreadPoolExecutor(a.jobs) as ex:
        for tag, res in ex.map(lambda j: run(a.rom, out, *j, a.presses, npcfile), jobs):
            print(tag, res, flush=True)


if __name__ == "__main__":
    main()
