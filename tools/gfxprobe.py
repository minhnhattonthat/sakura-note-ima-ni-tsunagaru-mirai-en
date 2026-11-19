"""Summarise a BG screen region for writing gfx/labels.tsv rows (phase 8 graphics).

    python -X utf8 tools/gfxprobe.py RGCN RCSN X,Y,W,H [--thresh LUMA]

Prints the region's index histogram (with RGB and luma), then the text lines found in it: runs of rows with
pixels brighter (or, with a negative --thresh, darker) than the threshold, each with its x/y extent and the
indices of those pixels. Read rect, fill and ink columns off it instead of a raw hex dump.
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
import gfxsweep as G  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rgcn", type=int)
    ap.add_argument("rcsn", type=int)
    ap.add_argument("region")
    ap.add_argument("--thresh", type=float, default=200)
    ap.add_argument("--cell", type=int, default=0)
    a = ap.parse_args()
    fs = gfx.files()
    g = G.rgcn(gfx.unpack(fs[a.rgcn])[0])
    pal = gfx.palette_near(fs, a.rgcn)
    px = gfx.map_grid(g, gfx.row_map(g, gfx.unpack(fs[a.rcsn])[0], a.cell))
    x0, y0, w, h = (int(v) for v in a.region.split(","))
    hist = collections.Counter(px.get((x, y)) for y in range(y0, y0 + h) for x in range(x0, x0 + w))
    print("indices (count idx rgb luma):")
    for v, n in hist.most_common(16):
        c = pal[v] if v is not None and v < len(pal) else None
        print(f"  {n:6d} {v} {c} {gfx.luma(c) if c else ''}")

    def hit(v):
        if v is None or v >= len(pal):
            return False
        lu = gfx.luma(pal[v])
        return lu > a.thresh if a.thresh >= 0 else lu < -a.thresh

    rows = [y for y in range(y0, y0 + h) if any(hit(px.get((x, y))) for x in range(x0, x0 + w))]
    runs = []
    for y in rows:
        if runs and y == runs[-1][-1] + 1:
            runs[-1].append(y)
        else:
            runs.append([y])
    print("text lines (y0-y1, x0-x1, indices):")
    for r in runs:
        xs = [x for y in r for x in range(x0, x0 + w) if hit(px.get((x, y)))]
        ink = collections.Counter(px[(x, y)] for y in r for x in range(x0, x0 + w) if hit(px.get((x, y))))
        print(f"  y {r[0]}-{r[-1]}  x {min(xs)}-{max(xs)}  {ink.most_common(5)}")


if __name__ == "__main__":
    main()
