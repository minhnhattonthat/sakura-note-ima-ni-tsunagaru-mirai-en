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
