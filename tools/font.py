"""font.py: the dialogue font, FILEDATA entry 860 (RGCN, 4bpp, 256x1792 px = 16 x 112 cells of 16x16).

Code n (the u16 text code) is cell n: row n // 16, column n % 16, tiles in a 32-tile-wide sheet.
Pixel values: 1 = stroke, 15 = drop shadow, 0 = clear (verified: code 0x10 decodes to あ, docs/re/font.md).

    python -X utf8 tools/font.py sheet OUT.png [--from 0x140] [--count 256] [--zoom 3] [--labels jp.tbl]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filedata  # noqa: E402
import romfs  # noqa: E402

FONT_ID = 860
HDR = 0x30
CELLS = 1792


def load_font_bytes():
    rom = romfs.load()
    return filedata.files(bytes(rom.getFileByName("FILEDATA.BIN")))[FONT_ID]


def glyph(font, code):
    """16x16 list of pixel values for a code."""
    d = font[HDR:] if font[:4] == b"RGCN" else font
    r, c = divmod(code, 16)
    out = []
    for y in range(16):
        row = []
        for x in range(16):
            t = (2 * r + y // 8) * 32 + (2 * c + x // 8)
            i = t * 64 + (y % 8) * 8 + (x % 8)
            b = d[i // 2]
            row.append((b >> 4) if i & 1 else (b & 15))
        out.append(row)
    return out


def stroke(g):
    return [[1 if v == 1 else 0 for v in row] for row in g]


def is_blank(g):
    return not any(v for row in g for v in row)


def sheet(font, out, start, count, zoom, labels=None, cols=16):
    from PIL import Image, ImageDraw, ImageFont
    cell = 16 * zoom
    lab_h = 12
    lf = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 12) if labels else ImageFont.load_default()
    rows = (count + cols - 1) // cols
    img = Image.new("RGB", (cols * (cell + 4), rows * (cell + lab_h + 4)), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    for k in range(count):
        code = start + k
        if code >= CELLS:
            break
        g = glyph(font, code)
        ox, oy = (k % cols) * (cell + 4), (k // cols) * (cell + lab_h + 4)
        for y in range(16):
            for x in range(16):
                v = g[y][x]
                col = (0, 0, 0) if v == 1 else (190, 190, 190) if v else (255, 255, 255)
                if v:
                    dr.rectangle([ox + x * zoom, oy + y * zoom, ox + x * zoom + zoom - 1, oy + y * zoom + zoom - 1], fill=col)
        txt = f"{code:03X}" + (" " + labels.get(code, "?") if labels else "")
        dr.text((ox, oy + cell + 1), txt, fill=(200, 0, 0), font=lf)
    img.save(out)


def read_tbl(path):
    m = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            m[int(k, 16)] = v
    return m


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet")
    s.add_argument("out")
    s.add_argument("--from", dest="start", type=lambda x: int(x, 0), default=0)
    s.add_argument("--count", type=lambda x: int(x, 0), default=256)
    s.add_argument("--zoom", type=int, default=3)
    s.add_argument("--labels")
    a = ap.parse_args()
    font = load_font_bytes()
    sheet(font, a.out, a.start, a.count, a.zoom, read_tbl(a.labels) if a.labels else None)


if __name__ == "__main__":
    sys.exit(main())
