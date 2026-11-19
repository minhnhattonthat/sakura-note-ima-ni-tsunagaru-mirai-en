"""rarekanji.py: kanji cells (0x140-0x662) used at most N times in script/, with their context, for a misread check.

    python -X utf8 tools/rarekanji.py [--max 2] [--out docs/re/rare_kanji.tsv]

Columns: code, glyph (jp.tbl), uses, id, context (10 chars each side). Pair it with a zoomed font sheet
(`tools/font.py sheet OUT.png --from 0xNNN --labels tbl/jp.tbl`) to re-read a suspicious cell.
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def kanji_codes():
    m = {}
    for line in (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#") and len(line.split("=", 1)[0]) == 4:
            k, v = line.split("=", 1)
            code = int(k[2:4] + k[0:2], 16)
            if 0x140 <= code <= 0x662 and len(v) == 1:
                m[v] = code
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "docs" / "re" / "rare_kanji.tsv"))
    a = ap.parse_args()
    km = kanji_codes()
    uses = collections.defaultdict(list)
    for p in sorted((ROOT / "script").glob("*.json")):
        for r in json.loads(p.read_text(encoding="utf-8")):
            t = r["jp"]
            for i, ch in enumerate(t):
                if ch in km:
                    uses[ch].append((r["id"], t[max(0, i - 10):i + 11].replace("{n}", "/")))
    rows = []
    for ch, us in uses.items():
        if len(us) <= a.max:
            for i, ctx in us:
                rows.append((f"{km[ch]:03X}", ch, len(us), i, ctx))
    rows.sort()
    unused = sorted(f"{c:03X}{ch}" for ch, c in km.items() if ch not in uses)
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["code", "glyph", "uses", "id", "context"])
        w.writerows(rows)
    print(f"{len({r[0] for r in rows})} cells used <= {a.max} times, {len(rows)} rows -> {a.out}; "
          f"{len(unused)} kanji cells unused in script/")


if __name__ == "__main__":
    sys.exit(main())
