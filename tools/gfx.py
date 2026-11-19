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
COLS = ["id", "recn", "cell", "rect", "fill", "ink", "shadow", "align", "dy", "style", "en", "note"]
STYLES = ("shadow", "outline", "bold", "big")
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
    """[(dx, dy, byte, high_nibble)] for every pixel of OBJ o in cell space (flips applied). 8bpp pixels use the
    whole byte (high_nibble None). 1D mapping: the tile number counts 32-byte units << shift at either depth."""
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
            if g["bpp"] == 8:
                out.append((o["x"] + xx, o["y"] + yy, start + k, None))
            else:
                out.append((o["x"] + xx, o["y"] + yy, start + k // 2, k & 1))
    return out


def cell_xoff(xfer, k):
    """Byte offset of cell k's characters in the RGCN data. RECN per-cell VRAM transfer entries are
    (offset, size); the offset is entry[0] (gfxsweep renders with it too)."""
    return xfer[k][0] if xfer else 0


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


def screen_map(g, scr):
    """BG: {(x, y) screen px: (byte, nibble, subpalette)} through an RCSN screen (flips applied). 8bpp pixels use
    the whole byte (nibble None)."""
    w, h = struct.unpack_from("<HH", scr, 0x18)
    size = struct.unpack_from("<I", scr, 0x20)[0]
    ents = scr[0x24:0x24 + size]
    wt = w // 8
    tb = 32 if g["bpp"] == 4 else 64
    m = {}
    for k in range(len(ents) // 2):
        e = ents[2 * k] | ents[2 * k + 1] << 8
        t, hf, vf, sub = e & 0x3FF, e >> 10 & 1, e >> 11 & 1, e >> 12
        ox, oy = k % wt * 8, k // wt * 8
        if oy >= h or (t + 1) * tb > len(g["data"]):
            continue
        for y in range(8):
            for x in range(8):
                i = y * 8 + x
                xx, yy = ox + (7 - x if hf else x), oy + (7 - y if vf else y)
                if g["bpp"] == 8:
                    m[(xx, yy)] = (t * tb + i, None, 0)
                else:
                    m[(xx, yy)] = (t * tb + i // 2, i & 1, sub)
    return m


def map_grid(g, m):
    d = g["data"]
    return {k: d[b] if hi is None else (d[b] >> 4 if hi else d[b] & 15) for k, (b, hi, _) in m.items()}


def put_map(data, m, px):
    """Write {(x, y): index} into data (bytearray of the RGCN pixel data) through map m; returns the set of bytes
    touched. A pixel whose byte also shows somewhere else (a tile used twice in a screen, an OBJ drawing the same
    characters twice) must get the same value there, or this raises."""
    where = {}
    for k, (b, hi, _) in m.items():
        where.setdefault((b, hi), []).append(k)
    touched = set()
    for k, v in px.items():
        if k not in m:
            raise ValueError(f"pixel {k} is outside the cell or screen")
        b, hi, _ = m[k]
        for other in where[(b, hi)]:
            if other != k and px.get(other, v) != v:
                raise ValueError(f"pixel {k} shares its byte with {other}, which wants another value")
            if other != k and other not in px:
                raise ValueError(f"pixel {k} shares its byte with {other} outside the label (shared tile)")
        if hi is None:
            data[b] = v
        else:
            data[b] = (data[b] & 0x0F) | (v << 4) if hi else (data[b] & 0xF0) | v
        touched.add(b)
    return touched


def cell_grid(g, objs, shift, xoff):
    """(w, h, {(x, y): index}) of one cell."""
    x0, y0, x1, y1 = cell_box(objs)
    return x1 - x0, y1 - y0, map_grid(g, cell_map(g, objs, shift, xoff))


def put_cell_grid(data, g, objs, shift, xoff, px):
    """Write {(x, y): index} into data (bytearray of the RGCN pixel data) through the cell's OBJs; returns the set
    of bytes touched."""
    return put_map(data, cell_map(g, objs, shift, xoff), px)


def row_map(g, src, cell):
    """Pixel map of one labels.tsv row: src = the RECN (sprite cell `cell`) or RCSN (whole BG screen) payload."""
    if src[:4] == b"RCSN":
        return screen_map(g, src)
    objs_all, shift, xfer = G.cells(src)
    return cell_map(g, objs_all[cell], shift, cell_xoff(xfer, cell))


def glyphs():
    import vwf
    return vwf.load_glyphs()


def text_width(text, gl=None):
    gl = gl or glyphs()
    return sum(len(gl[c][0]) + SPACE for c in text) - SPACE if text else 0


def letter(px, rect, text, fill, ink, shadow, align="c", dy=0, gl=None, style="shadow"):
    """Clear rect (x, y, w, h) to fill and draw text in it: ink pixels, then `shadow` (-1 = none) one px below each
    ink pixel that is not ink itself (style "shadow", as the dialogue font does) or on all 8 sides of it (style
    "outline", for white-on-colour labels with a dark rim). Glyph rows 0-7 sit on the cap line; the text is centred
    vertically on the cap height (+dy). Returns the new grid (a copy)."""
    gl = gl or glyphs()
    x, y, w, h = rect
    out = dict(px)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (xx, yy) in out and fill is not None:  # None = draw over what is there (cleared by an earlier row)
                if isinstance(fill, dict):
                    out[(xx, yy)] = fill[(xx, yy)] if (xx, yy) in fill else fill[yy]
                else:
                    out[(xx, yy)] = fill
    rim = 1 if style in ("outline", "big") else 0
    bold = 1 if style == "bold" else 0  # "bold": every ink pixel doubled to the right, glyphs 1 px wider
    k = 2 if style == "big" else 1  # "big": glyphs at 2x (headings), outlined
    tw = k * text_width(text, gl) + 2 * rim + bold * len(text)
    if tw > w:
        raise ValueError(f"{text!r}: {tw} px > rect width {w}")
    cx = x + rim + {"l": 0, "c": (w - tw) // 2, "r": w - tw}[align]
    cy = y + (h - 8 * k) // 2 + dy
    ink_px = set()
    for c in text:
        rows = gl[c]
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch == "#":
                    for a in range(k):
                        for b in range(k):
                            ink_px.add((cx + k * rx + a, cy + k * ry + b))
                    if bold:
                        ink_px.add((cx + rx + 1, cy + ry))
        cx += k * (len(rows[0]) + SPACE) + bold
    for p in ink_px:
        if p not in out or not (x <= p[0] < x + w and y <= p[1] < y + h):
            raise ValueError(f"{text!r}: ink at {p} falls outside the rect or the cell")
        out[p] = ink
    if shadow >= 0:
        around = [(0, 1)] if rim == 0 else [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b]
        for (sx, sy) in ink_px:
            for a, b in around:
                q = (sx + a, sy + b)
                if q not in ink_px and q in out and x <= q[0] < x + w and y <= q[1] < y + h:
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
            "rect": tuple(int(v) for v in r["rect"].split(",")),
            "fill": r["fill"] if r["fill"][:1] in "@~=^" else int(r["fill"]), "ink": int(r["ink"]),
            "shadow": int(r["shadow"]), "align": r["align"], "dy": int(r["dy"] or 0),
            "style": style(r["style"]), "en": r["en"]}


def row_fill(r, px, pal=None, bpp=4, subs=None):
    """fill = an index; "@X": each rect row cleared to the original value at column X of that row (keeps a banded
    or gradient label background); "~T": inpaint (text over art or a translucent panel), see `inpaint`."""
    if isinstance(r["fill"], int):
        return r["fill"]
    x, y, w, h = r["rect"]
    if r["fill"] == "=":
        return None
    if r["fill"].startswith("~"):
        t, _, d = r["fill"][1:].partition("/")
        if t.startswith("h"):  # "~hT": warm (orange/red) letters over green or blue art, R - G > T
            return inpaint(px, r["rect"], int(t[1:]), pal, bpp, int(d) if d else None, hue=True, subs=subs)
        return inpaint(px, r["rect"], int(t), pal, bpp, int(d) if d else None, subs=subs)
    if r["fill"].startswith("^"):  # "^DX,DY": copy the art at that offset (plain art next to the lettering)
        dx, dy = (int(v) for v in r["fill"][1:].split(","))
        return {(xx, yy): px[(xx + dx, yy + dy)] for xx in range(x, x + w) for yy in range(y, y + h)
                if (xx, yy) in px}
    col = int(r["fill"][1:])
    return {yy: px[(col, yy)] for yy in range(y, y + h)}


def luma(c):
    return (c[0] * 299 + c[1] * 587 + c[2] * 114) // 1000


def inpaint(px, rect, thresh, pal, bpp, grow=None, hue=False, subs=None):
    """{(x, y): index} for every pixel of rect with the old lettering removed. Text = pixels with luma > thresh
    (letters), < 24 (their black rim) or chroma > 64 (coloured letters' anti-aliasing), grown by 1 px; each is
    filled, in passes from the outside in, with the
    palette index nearest the mean colour of its known 8-neighbours (rect pixels that are not text, and the pixels
    just outside the rect). subs = {(x, y): sub-palette} (4bpp screens and cells: each pixel is read and refilled
    in its own tile's sub-palette); None = sub-palette 0 everywhere."""
    x, y, w, h = rect
    subs = subs or {}
    colour = lambda s, v: G.colour(pal, bpp, s, v) or (0, 0, 0)
    inside = {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h) if (xx, yy) in px}
    pix = lambda p: colour(subs.get(p, 0), px[p])
    def is_text(c):
        if hue:
            return c[0] - c[1] > thresh
        if thresh < 0:  # "~-T": dark letters (luma < T) on a pale panel or glow
            return luma(c) < -thresh
        if grow is not None:  # "~T/D": white letters only (over colourful art), their soft shadow taken by growing
            return luma(c) > thresh and max(c) - min(c) < 48
        return luma(c) > thresh or luma(c) < 24 or max(c) - min(c) > 64  # bright, rim, or coloured lettering
    text = {p for p in inside if is_text(pix(p))}
    for _ in range(1 if grow is None else grow):
        text |= {(a + i, b + j) for a, b in text for i in (-1, 0, 1) for j in (-1, 0, 1)} & inside
    known = {p: pix(p) for p in px if p not in text}
    cand = {}  # sub-palette -> its usable indices
    near = {}
    out = {}
    todo = set(text)
    while todo:
        step = {}
        for a, b in todo:
            ns = [known[q] for q in ((a + i, b + j) for i in (-1, 0, 1) for j in (-1, 0, 1)) if q in known]
            if len(ns) >= 2 or (ns and len(todo) < 8):
                step[(a, b)] = tuple(sum(c[k] for c in ns) // len(ns) for k in range(3))
        if not step:
            raise ValueError(f"inpaint: {len(todo)} pixels have no known neighbour")
        for p, c in step.items():
            s = subs.get(p, 0)
            if s not in cand:
                cand[s] = [v for v in range(1, 256 if bpp == 8 else 16) if G.colour(pal, bpp, s, v)]
            if (s, c) not in near:
                near[(s, c)] = min(cand[s], key=lambda v: sum((colour(s, v)[k] - c[k]) ** 2 for k in range(3)))
            out[p] = near[(s, c)]
            known[p] = colour(s, out[p])
        todo -= set(step)
    return {p: out.get(p, px[p]) for p in inside}


def style(s):
    s = s or "shadow"
    if s not in STYLES:
        raise ValueError(f"style {s!r} is not one of {STYLES}")
    return s


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
        m = row_map(g, unpack(out[r["recn"]])[0], r["cell"])
        px = map_grid(g, m)
        subs = {k: s for k, (_, _, s) in m.items()} if g["bpp"] == 4 else None
        fill = row_fill(r, px, palette_near(out, r["id"]), g["bpp"], subs)
        new = letter(px, r["rect"], r["en"], fill, r["ink"], r["shadow"], r["align"], r["dy"], gl, r["style"])
        changed = {k: v for k, v in new.items() if px[k] != v}
        touched = put_map(data, m, changed)
        p[start:start + size] = data
        allowed.setdefault(r["id"], set()).update(start + b for b in touched)
    for i, (p, z) in work.items():
        out[i] = repack(bytes(p), z)
    return out, allowed


def render(w, h, px, pal, sub=0, zoom=1, bg=G.BG, bpp=4):
    im = Image.new("RGB", (w, h), bg)
    d = im.load()
    for (x, y), v in px.items():
        c = G.colour(pal, bpp, sub, v)
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
    d = sub.add_parser("dump", help="index grid of a cell (or a BG region) as hex, to read rects and indices off")
    d.add_argument("rgcn", type=int)
    d.add_argument("recn", type=int)
    d.add_argument("cell", type=int, nargs="?", default=0)
    d.add_argument("--region", help="x,y,w,h (BG screens)")
    v = sub.add_parser("preview")
    v.add_argument("--out", default=str(ROOT / "work" / "gfx" / "preview"))
    v.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    fs = files()
    if a.cmd == "dump":
        g = G.rgcn(unpack(fs[a.rgcn])[0])
        px = map_grid(g, row_map(g, unpack(fs[a.recn])[0], a.cell))
        xs, ys = [k[0] for k in px], [k[1] for k in px]
        x0, y0, w, h = (tuple(int(v) for v in a.region.split(",")) if a.region else
                        (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
        fmt = "%02x" if g["bpp"] == 8 else "%x"
        blank = "  " if g["bpp"] == 8 else " "
        print(f"x {x0}..{x0 + w - 1}, y {y0}..{y0 + h - 1}")
        for y in range(y0, y0 + h):
            print(f"{y:3d} " + "".join(fmt % px[(x, y)] if (x, y) in px else blank for x in range(x0, x0 + w)))
        return
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "cells":
        g = G.rgcn(unpack(fs[a.rgcn])[0])
        pal = G.palette(unpack(fs[a.pal])[0]) if a.pal is not None else palette_near(fs, a.rgcn)
        src = unpack(fs[a.recn])[0]
        if src[:4] == b"RCSN":  # BG: the whole screen, 8 px grid ticks on the edge for reading rects off
            m = screen_map(g, src)
            w, h = struct.unpack_from("<HH", src, 0x18)
            im = render(w, h, map_grid(g, m), pal, next(iter(m.values()))[2] if m else 0, a.zoom, bpp=g["bpp"])
            im.save(out / f"{a.rgcn}_screen.png")
            print(f"screen {w}x{h} -> {out}")
            return
        objs_all, shift, xfer = G.cells(src)
        for k, objs in enumerate(objs_all):
            if not objs:
                continue
            w, h, px = cell_grid(g, objs, shift, cell_xoff(xfer, k))
            im = render(w, h, px, pal, subpal(objs), a.zoom, bpp=g["bpp"])
            G.label(im, f"{a.rgcn} cell {k} {w}x{h}", 1).save(out / f"{a.rgcn}_c{k:03d}.png")
        print(f"{len(objs_all)} cells -> {out}")
    else:
        rows = [parse_row(r) for r in load_rows()]
        new, _ = apply(fs)
        for r in rows:
            g0, g1 = G.rgcn(unpack(fs[r["id"]])[0]), G.rgcn(unpack(new[r["id"]])[0])
            src = unpack(fs[r["recn"]])[0]
            pal = palette_near(fs, r["id"])
            ims = []
            for g in (g0, g1):  # the label rect plus a 4 px margin
                m = row_map(g, src, r["cell"])
                x, y, w, h = r["rect"]
                pad = 4
                box = {(px - x + pad, py - y + pad): v for (px, py), v in map_grid(g, m).items()
                       if x - pad <= px < x + w + pad and y - pad <= py < y + h + pad}
                sub = next(iter(m.values()))[2] if m else 0
                ims.append(render(w + 2 * pad, h + 2 * pad, box, pal, sub, a.zoom, bpp=g["bpp"]))
            im = Image.new("RGB", (ims[0].width * 2 + 8, ims[0].height), (255, 255, 255))
            im.paste(ims[0], (0, 0))
            im.paste(ims[1], (ims[0].width + 8, 0))
            x, y = r["rect"][:2]  # BG rows share cell 0: the rect origin keeps names apart
            im.save(out / f"{r['id']}_c{r['cell']:03d}_{y:03d}_{x:03d}.png")
        for i, sc in sorted({(r["id"], r["recn"]) for r in rows}):  # BG: the whole screen, original | English
            src = unpack(fs[sc])[0]
            if src[:4] != b"RCSN":
                continue
            pal = palette_near(fs, i)
            w, h = struct.unpack_from("<HH", src, 0x18)
            ims = []
            for p in (fs[i], new[i]):
                g = G.rgcn(unpack(p)[0])
                ims.append(render(w, h, map_grid(g, screen_map(g, src)), pal, 0, a.zoom, bpp=g["bpp"]))
            im = Image.new("RGB", (ims[0].width * 2 + 8, ims[0].height), (255, 255, 255))
            im.paste(ims[0], (0, 0))
            im.paste(ims[1], (ims[0].width + 8, 0))
            im.save(out / f"{i}_screen.png")
        print(f"{len(rows)} rows -> {out}")


def palette_near(fs, i):
    """The RLCN of RGCN i: the next entry when it is one (RGCN, RLCN, RCSN groups), else the nearest one before
    (an RGCN + RCSN pair sharing the previous group's palette), else the nearest after. An RGCN, RECN, RLCN group
    (4218, 4219, 4220) takes its own RLCN two on."""
    order = [i + 1] + list(range(i - 1, i - 5, -1)) + list(range(i + 2, i + 5))
    if i + 2 < len(fs) and unpack(fs[i + 1])[0][:4] in (b"RECN", b"RCSN") and unpack(fs[i + 2])[0][:4] == b"RLCN":
        order.insert(0, i + 2)
    for j in order:
        if 0 <= j < len(fs) and unpack(fs[j])[0][:4] == b"RLCN":
            return G.palette(unpack(fs[j])[0])
    return []


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
