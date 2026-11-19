"""warp_all.py: run every scene of tools/debug/scenes.tsv from a cold boot, check it, keep a shot and a savestate.

    python -X utf8 tools/debug/warp_all.py [ROM] [--only a,b] [--jobs 4] [--out work/qa/scenes] [--no-states]

ROM defaults to the original dump. Each scene runs `emu.py --script tools/debug/warp.lua --var SCENE='<name>'`,
must log WARP_OK (warp.lua exits 3 on WARP_FAIL: its `expect` file never loaded, or an fID wait timed out), and
ends 30 frames after the key program. Every run boots with a blank EEPROM (work/saves/blank.sav, all 0xFF, which
the game initialises to three empty slots), never DeSmuME's shared Battery file. Results: <out>/<name>.png (both screens), <out>/sheet.png, and
work/states/<name>.dst (regenerate after every engine, font or graphics change; states keep old VRAM and code).
Exit 1 if any scene failed.
"""
import argparse
import csv
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ORIG = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"


def scenes():
    with open(ROOT / "tools" / "debug" / "scenes.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        assert len(r) == 5 and None not in r.values(), f"scenes.tsv: bad row {r}"
    return rows


def blank_save():
    """32 KiB of 0xFF = a never-used EEPROM; the game initialises it to its empty save (three free slots)."""
    p = ROOT / "work" / "saves" / "blank.sav"
    if not p.exists() or p.read_bytes() != b"\xff" * 0x8000:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\xff" * 0x8000)
    return p


def run(rom, name, out, states):
    d = out / "runs" / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{name}'",
           "--var", "STOP_AFTER=30", "--frames", "20000", "--timeout", "1500",
           "--sav", str(blank_save())]  # same title menu every run
    if states:
        cmd += ["--state-out", str(ROOT / "work" / "states" / f"{name}.dst")]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    ok = p.returncode == 0 and f"WARP_OK {name} " in log
    shot = d / "final.png"
    if shot.exists():
        shutil.copy(shot, out / f"{name}.png")
    why = "" if ok else ([l for l in log.splitlines() if "WARP_FAIL" in l] or [f"exit {p.returncode}"])[0]
    return name, ok, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ORIG))
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "scenes"))
    ap.add_argument("--no-states", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = [r["name"] for r in scenes()]
    if a.only:
        want = a.only.split(",")
        unknown = set(want) - set(names)
        assert not unknown, f"unknown scenes: {sorted(unknown)}"
        names = [n for n in names if n in want]
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda n: run(a.rom, n, out, not a.no_states), names))
    bad = 0
    for name, ok, why in results:
        print(f"{'ok  ' if ok else 'FAIL'} {name} {why}")
        bad += not ok
    shots = [str(out / f"{n}.png") for n in names if (out / f"{n}.png").exists()]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *shots,
                        "--cols", "6", "--out", str(out / "sheet.png")], check=False)
    print(f"{len(results) - bad}/{len(results)} scenes ok; shots in {out}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
