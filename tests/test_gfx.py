"""tools/gfx.py: the cell codec reads and writes the same pixels (tiled and linear sheets, flips), and lettering
stays inside its rect."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402


def sheet(flag):
    data = bytes((i * 7 + 3) & 0xFF for i in range(32 * 8))
    return {"bpp": 4, "flag": flag, "data": data, "h": 0xFFFF, "w": 0xFFFF}


OBJS = [{"x": -8, "y": -4, "w": 16, "h": 8, "t": 0, "pal": 2, "hf": 0, "vf": 0, "bpp8": 0},
        {"x": 8, "y": -4, "w": 8, "h": 8, "t": 2, "pal": 2, "hf": 1, "vf": 1, "bpp8": 0}]


@pytest.mark.parametrize("flag", [0x100, 0x101])
def test_roundtrip_identity(flag):
    g = sheet(flag)
    w, h, px = gfx.cell_grid(g, OBJS, 0, 0)
    assert (w, h) == (24, 8) and len(px) == 24 * 8
    data = bytearray(g["data"])
    gfx.put_cell_grid(data, g, OBJS, 0, 0, px)
    assert bytes(data) == g["data"]


@pytest.mark.parametrize("flag", [0x100, 0x101])
def test_write_then_read(flag):
    g = sheet(flag)
    w, h, px = gfx.cell_grid(g, OBJS, 0, 0)
    new = {k: (k[0] + k[1]) % 16 for k in px}
    data = bytearray(g["data"])
    touched = gfx.put_cell_grid(data, g, OBJS, 0, 0, new)
    assert max(touched) < 32 * 3  # three tiles: the 16x8 OBJ and the 8x8 one
    assert gfx.cell_grid({**g, "data": bytes(data)}, OBJS, 0, 0)[2] == new


def test_flip_maps_corner():
    g = sheet(0x100)
    _, _, px = gfx.cell_grid(g, OBJS, 0, 0)
    t2 = g["data"][64:96]
    first = t2[0] & 15  # tile 2 pixel (0, 0) shows at the flipped OBJ's bottom-right
    assert px[(23, 7)] == first


def test_letter_inside_rect():
    px = {(x, y): 0 for x in range(40) for y in range(12)}
    out = gfx.letter(px, (2, 1, 36, 10), "Ch.1", fill=1, ink=15, shadow=14)
    ink = [k for k, v in out.items() if v == 15]
    assert ink and all(2 <= x < 38 and 1 <= y < 11 for x, y in ink)
    assert all(v == 0 for (x, y), v in out.items() if not (2 <= x < 38 and 1 <= y < 11))
    with pytest.raises(ValueError):
        gfx.letter(px, (0, 0, 10, 10), "Chapter", 1, 15, 14)


def test_xfer_offset_is_entry_0():
    # RECN per-cell VRAM transfer entries are (offset, size): reading through entry[1] scrambled 4187/4194
    assert gfx.cell_xoff([(0, 2304), (2304, 512)], 1) == 2304
    assert gfx.cell_xoff(None, 3) == 0


def screen(entries, w=16, h=8):
    import struct
    ents = b"".join(struct.pack("<H", e) for e in entries)
    return b"RCSN" + bytes(0x14) + struct.pack("<HHII", w, h, 0, len(ents)) + ents


def test_screen_roundtrip_and_flip():
    g = {"bpp": 8, "flag": 0, "data": bytes(range(128)), "h": 1, "w": 2}
    scr = screen([0, 1 | 1 << 10])  # tile 0, then tile 1 h-flipped
    m = gfx.screen_map(g, scr)
    px = gfx.map_grid(g, m)
    assert px[(0, 0)] == 0 and px[(15, 0)] == 64 and px[(8, 0)] == 71
    data = bytearray(g["data"])
    gfx.put_map(data, m, {(15, 0): 200})
    assert data[64] == 200


def test_shared_tile_refused():
    g = {"bpp": 8, "flag": 0, "data": bytes(64), "h": 1, "w": 2}
    m = gfx.screen_map(g, screen([0, 0]))  # one tile shown twice
    with pytest.raises(ValueError):
        gfx.put_map(bytearray(g["data"]), m, {(0, 0): 5})
    data = bytearray(g["data"])
    gfx.put_map(data, m, {(0, 0): 5, (8, 0): 5})  # both copies agree: fine
    assert data[0] == 5


def test_outline_and_row_fill():
    px = {(x, y): y for x in range(40) for y in range(14)}
    r = {"rect": (2, 1, 36, 12), "fill": "@0"}
    fill = gfx.row_fill(r, px)
    out = gfx.letter(px, r["rect"], "Ab", fill, ink=15, shadow=14, style="outline")
    ink = {k for k, v in out.items() if v == 15}
    rim = {k for k, v in out.items() if v == 14}
    assert ink and rim
    for (x, y) in ink:  # every ink pixel is ringed by ink or rim
        assert all((x + a, y + b) in ink | rim for a in (-1, 0, 1) for b in (-1, 0, 1))
    assert all(out[(30, y)] == y for y in range(1, 13))  # cleared rows keep their own value


def test_inpaint_removes_bright_text():
    pal = [(0, 0, 0)] + [(10 * i, 10 * i, 10 * i) for i in range(1, 16)]
    px = {(x, y): 3 for x in range(20) for y in range(10)}
    for x in range(5, 15):
        px[(x, 5)] = 15  # a white stroke
    out = gfx.inpaint(px, (2, 2, 16, 6), 100, pal, 4)
    assert all(v == 3 for v in out.values())


def test_inpaint_dark_text():  # "~-T": letters darker than T on a pale panel
    pal = [(0, 0, 0)] + [(16 * i, 16 * i, 16 * i) for i in range(1, 16)]
    px = {(x, y): 13 for x in range(20) for y in range(10)}
    for x in range(5, 15):
        px[(x, 5)] = 3  # a dark stroke (luma 48: not the < 24 rim of bright text)
    px[(3, 3)] = 12  # panel texture away from the stroke stays as it is
    r = {"rect": (2, 2, 16, 6), "fill": "~-60"}
    out = gfx.row_fill(r, px, pal, 4)
    assert out.pop((3, 3)) == 12
    assert all(v == 13 for v in out.values())


def test_inpaint_warm_text_over_green():  # "~hT": R - G > T
    pal = [(0, 0, 0), (40, 160, 40), (60, 180, 60), (230, 140, 40), (120, 60, 10)]
    px = {(x, y): 1 + (x + y) % 2 for x in range(20) for y in range(10)}
    for x in range(5, 15):
        px[(x, 5)], px[(x, 6)] = 3, 4  # orange stroke, brown rim
    r = {"rect": (2, 2, 16, 6), "fill": "~h30"}
    out = gfx.row_fill(r, px, pal, 4)
    assert set(out.values()) <= {1, 2}


def test_inpaint_reads_each_tiles_subpalette():  # 4bpp: index 5 is white in sub-palette 1, grey in 0
    pal = [(0, 0, 0)] + [(40, 40, 40)] * 15 + [(0, 0, 0)] + [(40, 40, 40)] * 4 + [(255, 255, 255)] + [(40, 40, 40)] * 10
    px = {(x, y): 3 for x in range(20) for y in range(10)}
    for x in range(5, 15):
        px[(x, 5)] = 5
    subs = {k: 1 for k in px}
    assert all(v == 3 for v in gfx.inpaint(px, (2, 2, 16, 6), 100, pal, 4).values()) is False
    out = gfx.inpaint(px, (2, 2, 16, 6), 100, pal, 4, subs=subs)
    assert all(gfx.G.colour(pal, 4, 1, v) == (40, 40, 40) for v in out.values())


def test_offset_fill_copies_art():  # "^DX,DY": each rect pixel from (x+DX, y+DY)
    px = {(x, y): (x * 7 + y) % 16 for x in range(40) for y in range(10)}
    r = {"rect": (2, 1, 10, 6), "fill": "^20,2"}
    fill = gfx.row_fill(r, px)
    assert fill == {(x, y): px[(x + 20, y + 2)] for x in range(2, 12) for y in range(1, 7)}
    out = gfx.letter(px, r["rect"], "", fill, ink=15, shadow=-1)
    assert all(out[(x, y)] == px[(x + 20, y + 2)] for x in range(2, 12) for y in range(1, 7))


def test_big_style_doubles_glyphs():
    gl = gfx.glyphs()
    px = {(x, y): 0 for x in range(120) for y in range(24)}
    out = gfx.letter(px, (0, 0, 120, 24), "Ab", 0, ink=15, shadow=14, style="big")
    ink = {k for k, v in out.items() if v == 15}
    n = sum(row.count("#") for c in "Ab" for row in gl[c])
    assert len(ink) == 4 * n
    xs, ys = [k[0] for k in ink], [k[1] for k in ink]
    assert max(ys) - min(ys) + 1 <= 16
    assert max(xs) - min(xs) + 1 <= 2 * gfx.text_width("Ab", gl)
    rim = {k for k, v in out.items() if v == 14}
    for (x, y) in ink:
        assert all((x + a, y + b) in ink | rim for a in (-1, 0, 1) for b in (-1, 0, 1))
