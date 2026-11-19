"""forcecover.py: text coverage for strings no scene reaches, by forcing them into a host scene's own text box.

    python -X utf8 tools/debug/forcecover.py [ROM] [--host event] [--files 2495-2603] [--chunk 50] [--jobs 4]
        [--out work/qa/cover/force] [--dry]

Lists every string of build/strings.tsv that no log under work/qa/cover shows and docs/text_unshown.tsv doesn't
waive, keeps those in --files, and plays them in chunks: each run warps to the host scene with
tools/debug/forcemsg.lua, which rewrites the message fetch (file id + index) so each message the host fetches is the
next string of the chunk instead, drawn by the engine in the host's box; tools/debug/textlog.lua logs it. Logs
<out>/<host>_<first id>/log.txt (+ final.png, FORCE lines). A run whose log exists is skipped; the missing list is
recomputed every time, so a re-run only plays what is still missing.

Hosts (HOSTS below): 'event' = event 1938 played in the opening map (evcover.py's SWAP trick; ~60 messages, header
fetch 0x0203742C), for dialogue, narration and any string with the 4-byte header. The forced string keeps its own
header (speaker tag, voice), so the box is the dialogue box: this proves the engine reaches and expands the string;
its own screen's layout is judged by the width lint and the tour sheets.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
from make_save import blank_save  # noqa: E402

sys.path.insert(0, str(Path(SKILL) / "scripts"))
import textcover  # noqa: E402

EV_KEYS = "f2612 w30 a w120 a w100 a w100 a w300 " + " ".join(["a w30"] * 200)
HOSTS = {
    "event": dict(scene=f"debug:{EV_KEYS}", swap="1943:1938", fetch="a", host="2495-2616", frames=18000, sav=None),
}


def missing(strings, waive, cover):
    table = {r[0]: int(r[1], 16) for r in textcover.read_rows(strings)}
    waived = {r[0] for r in textcover.read_rows(waive) if len(r) > 1 and r[1].strip()}
    seen = textcover.shown(str(cover), 0xFFFFFFFF)
    return [i for i, a in table.items() if a not in seen and i not in waived]


def in_files(sid, spec):
    f = sid.split(":")[0]
    if not f.isdigit():
        return False
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        if int(lo) <= int(f) <= int(hi or lo):
            return True
    return False


def run(rom, out, host, ids):
    h = HOSTS[host]
    d = out / f"{host}_{ids[0].replace(':', '_')}"
    if (d / "log.txt").exists():
        return d.name, "skip"
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--script", str(ROOT / "tools" / "debug" / "textlog.lua"),
           "--script", str(ROOT / "tools" / "debug" / "forcemsg.lua"),
           "--var", f"SCENE='{h['scene']}'", "--var", f"FORCE='{','.join(ids)}'",
           "--var", f"HOST='{h['host']}'", "--var", f"FETCH='{h['fetch']}'", "--var", "STOP_AFTER=10",
           "--frames", str(h["frames"]), "--timeout", "420", "--shot-every", "600",
           "--sav", str(h["sav"] or blank_save())]
    if h["swap"]:
        cmd += ["--var", f"SWAP='{h['swap']}'"]
    pr = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    if not (d / "final.png").exists() and (d / "log.txt").exists():
        (d / "log.txt").rename(d / "log.incomplete.txt")  # a frozen run is re-played next time
    return d.name, f"exit {pr.returncode} forced {log.count('FORCE ')}/{len(ids)} text {log.count('TEXT ')}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "sakuranote_en.nds"))
    ap.add_argument("--host", default="event", choices=sorted(HOSTS))
    ap.add_argument("--files", default="2495-2616")
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "cover" / "force"))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    todo = [i for i in missing(ROOT / "build" / "strings.tsv", ROOT / "docs" / "text_unshown.tsv",
                               ROOT / "work" / "qa" / "cover") if in_files(i, a.files)]
    chunks = [todo[k:k + a.chunk] for k in range(0, len(todo), a.chunk)]
    print(f"{len(todo)} strings to force in {len(chunks)} runs", flush=True)
    if a.dry:
        return
    out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for tag, res in ex.map(lambda c: run(a.rom, out, a.host, c), chunks):
            print(tag, res, flush=True)


if __name__ == "__main__":
    main()
