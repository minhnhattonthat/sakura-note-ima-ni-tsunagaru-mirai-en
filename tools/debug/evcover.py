"""evcover.py: text coverage for event scripts: play every event the scripts start with Event(N), one run each.

    python -X utf8 tools/debug/evcover.py [ROM] [--only 2000,2001] [--jobs 8] [--presses 200] [--out work/qa/cover/ev]

Each run warps into the scenario-1 opening map (debug scene list row 1), whose StartScript calls Event(1943); warp.lua
SWAP='1943:N' makes that open load event script N instead, so the engine plays event N for real (its own
SetMessageFile and message calls). A-mash advances the text; tools/debug/textlog.lua logs every expanded string to
<out>/e<N>/log.txt for textcover.py. The event ids come from the Event(N) calls tools/scrrefs.py finds. Mobs the
event expects may be missing from this map, so the staging can look wrong: this proves the strings are reached and
expanded by the engine; the sheets judge layout. Runs whose log.txt exists are skipped.
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
import romfs  # noqa: E402
import filedata  # noqa: E402
import scrrefs  # noqa: E402

OPENING_EVENT = 1943


def event_ids():
    ids = set()
    for data in filedata.files(romfs.load().getFileByName("FILEDATA.BIN")):
        if data[:4] == b"SCR0":
            for _, nm, args in scrrefs.calls(data):
                if nm == "Event" and isinstance(args[0], int):
                    ids.add(args[0])
    return sorted(ids)


def run(rom, out, ev, presses):
    d = out / f"e{ev}"
    if (d / "log.txt").exists():
        return d.name, "skip"
    keys = "f2612 w30 a w120 a w100 a w100 a w300 " + " ".join(["a w30"] * presses)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--script", str(ROOT / "tools" / "debug" / "textlog.lua"),
           "--var", f"SCENE='debug:{keys}'", "--var", f"SWAP='{OPENING_EVENT}:{ev}'", "--var", "FILELOG=1",
           "--var", "STOP_AFTER=10", "--frames", str(presses * 80 + 2000), "--timeout", "1200",
           "--shot-every", "600", "--sav", str(blank_save())]
    pr = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    return d.name, f"exit {pr.returncode} text {log.count('TEXT ')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "sakuranote_en.nds"))
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--presses", type=int, default=200)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "cover" / "ev"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ids = [int(x) for x in a.only.split(",")] if a.only else event_ids()
    with ThreadPoolExecutor(a.jobs) as ex:
        for tag, res in ex.map(lambda e: run(a.rom, out, e, a.presses), ids):
            print(tag, res, flush=True)


if __name__ == "__main__":
    main()
