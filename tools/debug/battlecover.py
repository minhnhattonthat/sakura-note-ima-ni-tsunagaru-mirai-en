"""battlecover.py: text coverage for battles: every row of the debug battle list, mashed, with textlog.lua.

    python -X utf8 tools/debug/battlecover.py [ROM] [--pages 4] [--chars 0,1,2] [--jobs 8] [--out work/qa/cover/battle]

Debug menu -> バトル -> player select (right*C) -> battle list page P (right*(P-1)), row R (5 rows a page) -> A.
Then a fixed pattern of A/B/X/Y, taps on the field and walking for --frames, so bosses talk, use their arts and the
battle ends (either way). Battle text (2495, 2496 ...) is drawn by engine code, not by scripts (tools/scrrefs.py
finds no script naming it). Logs <out>/c<C>p<P>r<R>/log.txt; existing logs are skipped.
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

PATTERN = ["a w20", "t128,90 w20", "hleft:30", "y w10", "a w20", "t160,100 w20", "hright:30", "x w10", "b w10",
           "t96,120 w20", "hup:20", "a w20", "hdown:20", "t200,80 w20"]


def program(c, p, r, rounds):
    keys = ["f2612 w30 down a w120"]
    if c:
        keys.append(f"right*{c}")
    keys.append("a w150")
    if p > 1:
        keys.append(f"right*{p - 1} w30")
    if r:
        keys.append(f"down*{r}")
    keys.append("a w400")
    keys += PATTERN * rounds
    return "debug:" + " ".join(keys)


def run(rom, out, c, p, r, rounds):
    d = out / f"c{c}p{p}r{r}"
    if (d / "log.txt").exists():
        return d.name, "skip"
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--script", str(ROOT / "tools" / "debug" / "textlog.lua"),
           "--var", f"SCENE='debug:{program(c, p, r, rounds)[6:]}'", "--var", "STOP_AFTER=10",
           "--frames", str(rounds * 500 + 2000), "--timeout", "420",  # a full run takes 100-140 s
           "--shot-every", "1500",
           "--sav", str(blank_save())]
    pr = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    return d.name, f"exit {pr.returncode} text {log.count('TEXT ')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "sakuranote_en.nds"))
    ap.add_argument("--pages", type=int, default=4)
    ap.add_argument("--chars", default="0,1,2")
    ap.add_argument("--rounds", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "cover" / "battle"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(c, p, r) for c in map(int, a.chars.split(",")) for p in range(1, a.pages + 1) for r in range(5)]
    with ThreadPoolExecutor(a.jobs) as ex:
        for tag, res in ex.map(lambda j: run(a.rom, out, *j, a.rounds), jobs):
            print(tag, res, flush=True)


if __name__ == "__main__":
    main()
