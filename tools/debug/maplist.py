"""maplist.py: map every entry of the debug menu's scene/map list to the FILEDATA files its warp loads.

    python -X utf8 tools/debug/maplist.py [--scenarios 1,2,3,4] [--pages 12] [--jobs 6] [--out work/qa/maplist]

For each scenario (boy), page and row (6 rows a page) it warps with tools/debug/warp.lua (raw debug program, FILELOG=1)
and records the map-range file ids (1143-1899) opened after the final A. Pages wrap: a scenario's scan stops at the
first page whose row 0 loads the same files as page 1 row 0. Writes docs/re/maplist.tsv
(scenario, page, row, files) and keeps each run's final.png in <out>/s<S>p<P>r<R>.png.
"""
import argparse
import csv
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
from make_save import ORIG, blank_save  # noqa: E402

LO, HI = 1143, 1899


def program(s, p, r):
    keys = ["f2612 w30 a w120 a w100"]
    if s > 1:
        keys.append(f"down*{s - 1}")
    keys.append("a w100")
    if p > 1:
        keys.append(f"right*{p - 1} w30")
    if r:
        keys.append(f"down*{r}")
    keys.append("a w400")
    return "debug:" + " ".join(keys)


def run(out, s, p, r):
    tag = f"s{s}p{p}r{r}"
    d = out / "runs" / tag
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(ORIG), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{program(s, p, r)}'",
           "--var", "STOP_AFTER=10", "--var", "FILELOG=1", "--frames", "6000", "--timeout", "600",
           "--sav", str(blank_save())]
    subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    # files opened after the debug list was drawn: the list itself loads nothing in the map range
    ids = []
    for f, i in re.findall(r"FILE (\d+) (\d+)", log):
        i = int(i)
        if LO <= i <= HI and i not in ids:
            ids.append(i)
    if (d / "final.png").exists():
        shutil.copy(d / "final.png", out / f"{tag}.png")
    return s, p, r, ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="1,2,3,4")
    ap.add_argument("--pages", type=int, default=12)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "maplist"))
    a = ap.parse_args()
    out = Path(a.out)
    (out / "runs").mkdir(parents=True, exist_ok=True)
    rows = []
    with ThreadPoolExecutor(a.jobs) as ex:
        for s in [int(x) for x in a.scenarios.split(",")]:
            first = None
            for p in range(1, a.pages + 1):
                res = list(ex.map(lambda r: run(out, s, p, r), range(6)))
                if p == 1:
                    first = res[0][3]
                elif res[0][3] == first:
                    break
                for row in res:
                    print(*row[:3], " ".join(map(str, row[3])), flush=True)
                    rows.append(row)
    tsv = ROOT / "docs" / "re" / "maplist.tsv"
    with open(tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["scenario", "page", "row", "files"])
        for s, p, r, ids in rows:
            w.writerow([s, p, r, " ".join(map(str, ids))])
    print("wrote", tsv)


if __name__ == "__main__":
    main()
