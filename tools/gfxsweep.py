"""gfxsweep.py: static graphics-text sweep of FILEDATA.BIN (phase 1 recon, docs/re/graphics.md).

Renders every RGCN (raw and LZ10) into numbered contact-sheet pages, labelled with the FILEDATA id:
  * BG-style RGCN (header gives tile width/height): tiles in order at the header width; composed through the group's
    RCSN screen too when there is one (4bpp palettes taken from the screen entries).
  * sprite RGCN (width/height 0xFFFF): every cell of the group's RECN composed from its OAM entries (1D mapping,
    per-cell VRAM transfer, linear 0x101 data read row-major per OBJ), plus the raw tiles at 32 tiles wide.
Groups are runs of entries between graphics: the palette (RLCN), screen (RCSN) and cells (RECN) used for an RGCN are
the nearest ones within 4 ids, after first, then before. Every RGCN that could not be rendered is printed with the
reason; nothing is dropped silently. QQ blocks (LZ10, "QQ\\0\\0") are tilemaps (u16 entries, no pixels): listed only.

    python -X utf8 tools/gfxsweep.py --out work/sweep [--ids 0-200] [--page 1024x1024]
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from ndspy import lz10

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filedata  # noqa: E402
import romfs  # noqa: E402

NEAR = 4
OBJ_SIZES = {  # (shape, size) -> (w, h)
    (0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64),
    (1, 0): (16, 8), (1, 1): (32, 8), (1, 2): (32, 16), (1, 3): (64, 32),
    (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64),
}


def unpack(p):
    if p[:1] == b"\x10":
        try:
            return lz10.decompress(p), True
        except Exception:
            pass
    return p, False


def palette(p):
    """RLCN -> list of (r,g,b)."""
    # TTLP at 0x10: magic, size, bpp, unk, data size, data offset (from section + 8)
    n, off = struct.unpack_from("<II", p, 0x20)
    d = p[0x18 + off:0x18 + off + n]
    out = []
    for i in range(0, len(d) - 1, 2):
        c = d[i] | d[i + 1] << 8
        out.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))
    return out or [(0, 0, 0)]


def rgcn(p):
    h, w, bpp, mapping, flag, size, off = struct.unpack_from("<HHIIIII", p, 0x18)
    data = p[0x18 + off:0x18 + off + size]  # CHAR at 0x10; data offset counts from section + 8
    return {"h": h, "w": w, "bpp": 4 if bpp == 3 else 8, "flag": flag, "data": data}


def tile_px(data, bpp, t):
    """64 pixel indices of tile t (tiled data)."""
    n = 32 if bpp == 4 else 64
    b = data[t * n:(t + 1) * n]
    if len(b) < n:
        return None
    if bpp == 8:
        return list(b)
    out = []
    for x in b:
        out += [x & 15, x >> 4]
    return out


def lin_px(data, bpp, start, w, h):
    """w*h pixel indices read row-major from byte offset start."""
    n = w * h if bpp == 8 else w * h // 2
    b = data[start:start + n]
    if len(b) < n:
        return None
    if bpp == 8:
        return list(b)
    out = []
    for x in b:
        out += [x & 15, x >> 4]
    return out


def colour(pal, bpp, sub, v):
    if v == 0:
        return None
    i = (sub * 16 + v) if bpp == 4 else v
    if i < len(pal):
        return pal[i]
    g = v * 17 if bpp == 4 else v
    return (g, g, g)


BG = (40, 40, 48)


def render_tiles(g, pal, wt, subs=None):
    nt = len(g["data"]) // (32 if g["bpp"] == 4 else 64)
    wt = max(1, min(wt, nt))
    ht = (nt + wt - 1) // wt
    im = Image.new("RGB", (wt * 8, ht * 8), BG)
    px = im.load()
    for t in range(nt):
        v = tile_px(g["data"], g["bpp"], t)
        sub = (subs or {}).get(t, 0)
        ox, oy = t % wt * 8, t // wt * 8
        for i, c in enumerate(v):
            col = colour(pal, g["bpp"], sub, c)
            if col:
                px[ox + i % 8, oy + i // 8] = col
    return im


def render_screen(g, pal, scr):
    """RCSN screen -> image; also returns the tile -> sub-palette map it implies."""
    w, h = struct.unpack_from("<HH", scr, 0x18)
    size = struct.unpack_from("<I", scr, 0x20)[0]
    ents = scr[0x24:0x24 + size]
    wt = w // 8
    im = Image.new("RGB", (w, h), BG)
    px = im.load()
    subs = {}
    for k in range(len(ents) // 2):
        e = ents[2 * k] | ents[2 * k + 1] << 8
        t, hf, vf, sub = e & 0x3FF, e >> 10 & 1, e >> 11 & 1, e >> 12
        if g["bpp"] == 8:
            sub = 0
        subs.setdefault(t, sub)
        v = tile_px(g["data"], g["bpp"], t)
        if v is None:
            continue
        ox, oy = k % wt * 8, k // wt * 8
        if oy >= h:
            break
        for i, c in enumerate(v):
            x, y = i % 8, i // 8
            if hf:
                x = 7 - x
            if vf:
                y = 7 - y
            col = colour(pal, g["bpp"], sub, c)
            if col:
                px[ox + x, oy + y] = col
    return im, subs


def cells(recn):
    """RECN -> list of cells, each a list of OBJ dicts; plus mapping shift and per-cell char offsets."""
    sec = 0x10
    n, ctype = struct.unpack_from("<HH", recn, sec + 8)
    cdata, mapping, vram = struct.unpack_from("<III", recn, sec + 12)
    base = sec + 8 + cdata
    esz = 16 if ctype == 1 else 8
    oam_base = base + n * esz
    out = []
    for c in range(n):
        nobj, _attr, ooff = struct.unpack_from("<HHI", recn, base + c * esz)
        objs = []
        for k in range(nobj):
            a0, a1, a2 = struct.unpack_from("<HHH", recn, oam_base + ooff + 6 * k)
            y = a0 & 0xFF
            y = y - 256 if y >= 128 else y
            x = a1 & 0x1FF
            x = x - 512 if x >= 256 else x
            shape, size = a0 >> 14, a1 >> 14
            if (shape, size) not in OBJ_SIZES:
                continue
            w, h = OBJ_SIZES[(shape, size)]
            objs.append({"x": x, "y": y, "w": w, "h": h, "t": a2 & 0x3FF, "pal": a2 >> 12,
                         "hf": a1 >> 12 & 1 if not a0 >> 8 & 1 else 0, "vf": a1 >> 13 & 1 if not a0 >> 8 & 1 else 0,
                         "bpp8": a0 >> 13 & 1})
        out.append(objs)
    xfer = None
    if vram:
        vb = sec + 8 + vram
        _maxsz, xo = struct.unpack_from("<II", recn, vb)
        xfer = [struct.unpack_from("<II", recn, vb + xo + 8 * c) for c in range(n)]
    shift = mapping & 0xFF
    return out, shift if shift <= 3 else 0, xfer


def render_cell(g, pal, objs, shift, xoff):
    if not objs:
        return None
    x0 = min(o["x"] for o in objs)
    y0 = min(o["y"] for o in objs)
    x1 = max(o["x"] + o["w"] for o in objs)
    y1 = max(o["y"] + o["h"] for o in objs)
    if x1 - x0 > 512 or y1 - y0 > 512:
        return None
    im = Image.new("RGB", (x1 - x0, y1 - y0), BG)
    px = im.load()
    bpp = g["bpp"]
    tb = 32 if bpp == 4 else 64
    for o in reversed(objs):
        start = xoff + (o["t"] << shift) * 32
        if g["flag"] & 1:
            v = lin_px(g["data"], bpp, start, o["w"], o["h"])
            if v is None:
                continue
            get = (lambda v=v, o=o: lambda x, y: v[y * o["w"] + x])()
        else:
            ntw = o["w"] // 8
            tiles = []
            ok = True
            for ty in range(o["h"] // 8):
                for tx in range(ntw):
                    s = start + (ty * ntw + tx) * tb
                    tv = tile_px(g["data"][s:s + tb], bpp, 0)
                    if tv is None:
                        ok = False
                        break
                    tiles.append(tv)
            if not ok:
                continue
            get = (lambda tiles=tiles, ntw=ntw: lambda x, y: tiles[(y // 8) * ntw + x // 8][(y % 8) * 8 + x % 8])()
        for y in range(o["h"]):
            for x in range(o["w"]):
                c = get(x, y)
                col = colour(pal, bpp, o["pal"], c)
                if col:
                    xx = (o["w"] - 1 - x) if o["hf"] else x
                    yy = (o["h"] - 1 - y) if o["vf"] else y
                    px[o["x"] - x0 + xx, o["y"] - y0 + yy] = col
    return im


def nearest(kinds, i, want, groups=None):
    """Nearest entry of kind `want` within NEAR ids (after first); with groups, same RNAN group first."""
    cand = [i + d for d in list(range(1, NEAR + 1)) + list(range(-1, -NEAR - 1, -1))
            if 0 <= i + d < len(kinds) and kinds[i + d] == want]
    if groups:
        same = [j for j in cand if groups[j] == groups[i]]
        if same:
            return same[0]
    return cand[0] if cand else None


def label(im, text, zoom):
    if zoom > 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    out = Image.new("RGB", (max(im.width, 8 * len(text)), im.height + 12), (0, 0, 0))
    ImageDraw.Draw(out).text((1, 0), text, fill=(255, 255, 0))
    out.paste(im, (0, 12))
    return out


def pages(items, pw, ph, out, prefix):
    """Shelf-pack labelled images into pages; returns list of (page file, [labels])."""
    res = []
    page, x, y, rowh, labs = None, 0, 0, 0, []

    def flush():
        if page is not None:
            f = out / f"{prefix}{len(res):03d}.png"
            page.crop((0, 0, pw, min(ph, y + rowh))).save(f)
            res.append((f.name, list(labs)))

    for lab, im in items:
        if im.width > pw:
            im = im.crop((0, 0, pw, im.height))
        if im.height > ph:
            im = im.crop((0, 0, im.width, ph))
        if page is None:
            page, x, y, rowh, labs = Image.new("RGB", (pw, ph), (64, 0, 64)), 0, 0, 0, []
        if x + im.width > pw:
            x, y, rowh = 0, y + rowh + 4, 0
        if y + im.height > ph:
            flush()
            page, x, y, rowh, labs = Image.new("RGB", (pw, ph), (64, 0, 64)), 0, 0, 0, []
        page.paste(im, (x, y))
        labs.append(lab)
        x += im.width + 4
        rowh = max(rowh, im.height)
    flush()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids", default="0-4697")
    ap.add_argument("--page", default="1024x1024")
    a = ap.parse_args()
    lo, hi = map(int, a.ids.split("-"))
    pw, ph = map(int, a.page.split("x"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    blob = bytes(romfs.load().getFileByName("FILEDATA.BIN"))
    raw = filedata.files(blob)
    ents = [unpack(p) for p in raw]
    kinds = [p[:4] for p, _ in ents]
    groups, gcount = [], 0
    for k in kinds:
        gcount += k == b"RNAN"
        groups.append(gcount)
    items, index, skipped, qq = [], [], [], []
    seen = set()

    def add(lab, im, text, zoom=1):
        key = (im.size, im.tobytes())
        if key in seen:
            return
        seen.add(key)
        items.append((lab, label(im, text, zoom)))

    for i in range(lo, hi + 1):
        p, z = ents[i]
        if kinds[i][:2] == b"QQ":
            qq.append(i)
            continue
        if kinds[i] != b"RGCN":
            continue
        try:
            g = rgcn(p)
        except Exception as e:  # noqa: BLE001
            skipped.append((i, f"header: {e}"))
            continue
        pj = nearest(kinds, i, b"RLCN", groups)
        pal = palette(ents[pj][0]) if pj is not None else []
        tag = f"{i}{'z' if z else ''} {g['bpp']}bpp pal={pj}"
        n_before = len(items)
        n_seen = len(seen)
        if g["w"] != 0xFFFF:
            sj = nearest(kinds, i, b"RCSN") if g["bpp"] == 4 else None
            subs = None
            if sj is not None:
                try:
                    im, subs = render_screen(g, pal, ents[sj][0])
                    add(f"{tag} scr={sj}", im, f"{i} scr{sj}")
                except Exception as e:  # noqa: BLE001
                    skipped.append((i, f"screen {sj}: {e}"))
            add(tag, render_tiles(g, pal, g["w"], subs), f"{i} tiles")
        else:
            cj = nearest(kinds, i, b"RECN", groups)
            if cj is None:
                skipped.append((i, "sprite RGCN without RECN within 4 ids: raw tiles only"))
            else:
                try:
                    cl, shift, xfer = cells(ents[cj][0])
                    for c, objs in enumerate(cl):
                        xo = xfer[c][0] if xfer else 0
                        im = render_cell(g, pal, objs, shift, xo)
                        if im is not None:
                            add(f"{tag} cells={cj} #{c}", im, f"{i}#{c}")
                except Exception as e:  # noqa: BLE001
                    skipped.append((i, f"cells {cj}: {e}"))
            if g["flag"] & 1 == 0:
                add(tag + " raw", render_tiles(g, pal, 32), f"{i} raw")
        if len(items) == n_before and len(seen) == n_seen:
            skipped.append((i, "nothing new rendered (all renders duplicate earlier ones, or none)"))
        index.append(i)
    res = pages(items, pw, ph, out, "p")
    with open(out / "index.tsv", "w", encoding="utf-8") as f:
        f.write("page\titem\n")
        for name, labs in res:
            for lab in labs:
                f.write(f"{name}\t{lab}\n")
    print(f"{len(index)} RGCN -> {len(items)} images on {len(res)} pages in {out}")
    print(f"QQ tilemaps (listed, not rendered): {len(qq)}")
    for i, why in skipped:
        print(f"SKIP/PARTIAL {i}: {why}")


if __name__ == "__main__":
    sys.exit(main())
