"""gfx.py: graphics-text redraws (phase 8, docs/re/graphics.md, docs/re/gfx.md).

Works in palette indices, never RGB, so a redraw cannot pick a colour the palette lacks or blur an edge.
- sprite sheets (RGCN + RECN, tiled or linear 0x101): a cell is read into an index grid through its OBJs and
  written back through the same OBJs (`cell_grid` / `put_cell_grid`);
- lettering with the project's own glyphs (fonts/vwf_glyphs.txt, MIT, 8 px cap height; `letter`);
- redraw rows in gfx/labels.tsv, applied by the build (`apply`): per row, a FILEDATA RGCN, its RECN and a cell,
  a clear rect in cell pixels, the fill / ink / shadow indices, the alignment and the English.

    python -X utf8 tools/gfx.py cells RGCN RECN [--pal RLCN] [--zoom 3] --out DIR   # every cell, labelled PNGs
    python -X utf8 tools/gfx.py preview [--out work/gfx/preview]                   # original | English per row
"""
import argparse
import csv
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import filedata  # noqa: E402
import gfxsweep as G  # noqa: E402
import romfs  # noqa: E402

LABELS = ROOT / "gfx" / "labels.tsv"
COLS = ["id", "recn", "cell", "rect", "fill", "ink", "shadow", "align", "dy", "en", "note"]
SPACE = 1  # px between glyphs (the advance is width + 1, as in tools/vwf.py)


def unpack(p):
    """(payload, was_lz10)."""
    return G.unpack(p)


def repack(p, compressed):
    from ndspy import lz10
    return lz10.compress(p) if compressed else p


def char_data(p):
    """(start, size) of the RGCN pixel data inside the RGCN file."""
    size, off = struct.unpack_from("<II", p, 0x18 + 16)
    return 0x18 + off, size


def obj_pixels(g, o, shift, xoff):
    """[(dx, dy, byte, high_nibble)] for every pixel of OBJ o in cell space (flips applied), 4bpp only."""
    assert g["bpp"] == 4, "8bpp sprite sheets: add when one carries text"
    start = xoff + (o["t"] << shift) * 32
    out = []
    ntw = o["w"] // 8
    for y in range(o["h"]):
        for x in range(o["w"]):
            if g["flag"] & 1:  # linear: row-major over the whole OBJ
                k = y * o["w"] + x
            else:
                t = (y // 8) * ntw + x // 8
                k = t * 64 + (y % 8) * 8 + x % 8
            xx = (o["w"] - 1 - x) if o["hf"] else x
            yy = (o["h"] - 1 - y) if o["vf"] else y
            out.append((o["x"] + xx, o["y"] + yy, start + k // 2, k & 1))
    return out


def cell_box(objs):
    return (min(o["x"] for o in objs), min(o["y"] for o in objs),
            max(o["x"] + o["w"] for o in objs), max(o["y"] + o["h"] for o in objs))


def cell_map(g, objs, shift, xoff):
    """{(x, y) cell-local: (byte, nibble, subpalette)}; the topmost OBJ (first in the list) wins."""
    x0, y0, _, _ = cell_box(objs)
    m = {}
    for o in reversed(objs):
        for dx, dy, b, hi in obj_pixels(g, o, shift, xoff):
            if b < len(g["data"]):
                m[(dx - x0, dy - y0)] = (b, hi, o["pal"])
    return m


def cell_grid(g, objs, shift, xoff):
    """(w, h, {(x, y): index}) of one cell."""
    x0, y0, x1, y1 = cell_box(objs)
    m = cell_map(g, objs, shift, xoff)
    px = {k: (g["data"][b] >> 4 if hi else g["data"][b] & 15) for k, (b, hi, _) in m.items()}
    return x1 - x0, y1 - y0, px


def put_cell_grid(data, g, objs, shift, xoff, px):
    """Write {(x, y): index} into data (bytearray of the RGCN pixel data) through the cell's OBJs; returns the set
    of bytes touched."""
    m = cell_map(g, objs, shift, xoff)
    touched = set()
    for k, v in px.items():
        if k not in m:
            raise ValueError(f"pixel {k} is outside the cell's OBJs")
        b, hi, _ = m[k]
        data[b] = (data[b] & 0x0F) | (v << 4) if hi else (data[b] & 0xF0) | v
        touched.add(b)
    return touched


def glyphs():
    import vwf
    return vwf.load_glyphs()


def text_width(text, gl=None):
    gl = gl or glyphs()
    return sum(len(gl[c][0]) + SPACE for c in text) - SPACE if text else 0


def letter(px, rect, text, fill, ink, shadow, align="c", dy=0, gl=None):
    """Clear rect (x, y, w, h) to fill and draw text in it: ink pixels, shadow one px below each ink pixel that is
    not ink itself (as the dialogue font does; shadow -1 = none). Glyph rows 0-7 sit on the cap line; the text is
    centred vertically on the cap height (+dy). Returns the new grid (a copy)."""
    gl = gl or glyphs()
    x, y, w, h = rect
    out = dict(px)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx, yy) in out:
                out[(xx, yy)] = fill
    tw = text_width(text, gl)
    if tw > w:
        raise ValueError(f"{text!r}: {tw} px > rect width {w}")
    cx = x + {"l": 0, "c": (w - tw) // 2, "r": w - tw}[align]
    cy = y + (h - 8) // 2 + dy
    ink_px = set()
    for c in text:
        rows = gl[c]
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch == "#":
                    ink_px.add((cx + rx, cy + ry))
        cx += len(rows[0]) + SPACE
    for p in ink_px:
        if p not in out or not (x <= p[0] < x + w and y <= p[1] < y + h):
            raise ValueError(f"{text!r}: ink at {p} falls outside the rect or the cell")
        out[p] = ink
    if shadow >= 0:
        for (sx, sy) in ink_px:
            q = (sx, sy + 1)
            if q not in ink_px and q in out and y <= q[1] < y + h:
                out[q] = shadow
    return out


def load_rows(path=LABELS):
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t"))
    for r in rows:
        if list(r) != COLS or None in r.values():
            raise ValueError(f"{path.name}: row {r} does not have the columns {COLS}")
    return rows


def parse_row(r):
    return {"id": int(r["id"]), "recn": int(r["recn"]), "cell": int(r["cell"]),
            "rect": tuple(int(v) for v in r["rect"].split(",")), "fill": int(r["fill"]), "ink": int(r["ink"]),
            "shadow": int(r["shadow"]), "align": r["align"], "dy": int(r["dy"] or 0), "en": r["en"]}


def apply(payloads, rows=None):
    """FILEDATA payloads with every labels.tsv row drawn; also {id: set of pixel-data byte offsets allowed to
    change} for tools/romcheck.py."""
    rows = [parse_row(r) for r in (load_rows() if rows is None else rows)]
    out = list(payloads)
    allowed = {}
    gl = glyphs()
    work = {}
    for r in rows:
        if r["id"] not in work:
            p, z = unpack(out[r["id"]])
            work[r["id"]] = (bytearray(p), z)
        p, _ = work[r["id"]]
        g = G.rgcn(bytes(p))
        start, size = char_data(p)
        data = bytearray(g["data"])
        objs_all, shift, xfer = G.cells(unpack(out[r["recn"]])[0])
        objs = objs_all[r["cell"]]
        xoff = xfer[r["cell"]][1] if xfer else 0
        w, h, px = cell_grid(g, objs, shift, xoff)
        new = letter(px, r["rect"], r["en"], r["fill"], r["ink"], r["shadow"], r["align"], r["dy"], gl)
        changed = {k: v for k, v in new.items() if px[k] != v}
        touched = put_cell_grid(data, g, objs, shift, xoff, changed)
        p[start:start + size] = data
        allowed.setdefault(r["id"], set()).update(start + b for b in touched)
    for i, (p, z) in work.items():
        out[i] = repack(bytes(p), z)
    return out, allowed


def render(w, h, px, pal, sub=0, zoom=1, bg=G.BG):
    im = Image.new("RGB", (w, h), bg)
    d = im.load()
    for (x, y), v in px.items():
        c = G.colour(pal, 4, sub, v)
        if c:
            d[x, y] = c
    return im.resize((w * zoom, h * zoom), Image.NEAREST) if zoom > 1 else im


def subpal(objs):
    return objs[0]["pal"] if objs else 0


def files():
    return filedata.files(bytes(romfs.load().getFileByName("FILEDATA.BIN")))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cells")
    c.add_argument("rgcn", type=int)
    c.add_argument("recn", type=int)
    c.add_argument("--pal", type=int)
    c.add_argument("--zoom", type=int, default=3)
    c.add_argument("--out", required=True)
    v = sub.add_parser("preview")
    v.add_argument("--out", default=str(ROOT / "work" / "gfx" / "preview"))
    v.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    fs = files()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "cells":
        g = G.rgcn(unpack(fs[a.rgcn])[0])
        pal = G.palette(unpack(fs[a.pal])[0]) if a.pal is not None else []
        objs_all, shift, xfer = G.cells(unpack(fs[a.recn])[0])
        for k, objs in enumerate(objs_all):
            if not objs:
                continue
            w, h, px = cell_grid(g, objs, shift, xfer[k][1] if xfer else 0)
            im = render(w, h, px, pal, subpal(objs), a.zoom)
            G.label(im, f"{a.rgcn} cell {k} {w}x{h}", 1).save(out / f"{a.rgcn}_c{k:03d}.png")
        print(f"{len(objs_all)} cells -> {out}")
    else:
        rows = [parse_row(r) for r in load_rows()]
        new, _ = apply(fs)
        for r in rows:
            g0, g1 = G.rgcn(unpack(fs[r["id"]])[0]), G.rgcn(unpack(new[r["id"]])[0])
            objs_all, shift, xfer = G.cells(unpack(fs[r["recn"]])[0])
            objs = objs_all[r["cell"]]
            xoff = xfer[r["cell"]][1] if xfer else 0
            pal = G.palette(unpack(fs[r["pal"]])[0]) if r.get("pal") else palette_near(fs, r["id"])
            ims = [render(*cell_grid(g, objs, shift, xoff), pal, subpal(objs), a.zoom) for g in (g0, g1)]
            im = Image.new("RGB", (ims[0].width * 2 + 8, ims[0].height), (255, 255, 255))
            im.paste(ims[0], (0, 0))
            im.paste(ims[1], (ims[0].width + 8, 0))
            im.save(out / f"{r['id']}_c{r['cell']:03d}.png")
        print(f"{len(rows)} rows -> {out}")


def palette_near(fs, i):
    for j in list(range(i + 1, i + 5)) + list(range(i - 1, i - 5, -1)):
        if 0 <= j < len(fs) and unpack(fs[j])[0][:4] == b"RLCN":
            return G.palette(unpack(fs[j])[0])
    return []


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
