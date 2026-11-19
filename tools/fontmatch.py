"""fontmatch.py: first-guess character for every font cell, by matching against MS Gothic 12 px (JIS X 0208 set).

A first guess only: verify by eye (`font.py sheet --labels`) and by script context before code depends on it.
Writes TSV: code, best char, score, 2nd char, 2nd score.

    python -X utf8 tools/fontmatch.py OUT.tsv [--font C:/Windows/Fonts/msgothic.ttc] [--size 12]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font as gfont  # noqa: E402


def jis_chars():
    out = []
    for hi in list(range(0x81, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                ch = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            out.append(ch)
    return out


def render(ch, f, size):
    img = Image.new("L", (16, 16), 0)
    ImageDraw.Draw(img).text((0, 0), ch, fill=255, font=f)
    a = (np.array(img) > 96).astype(np.float32)
    return a


def norm(a):
    """Crop to the ink box and place at the top-left of a 16x16 frame, return (array, box h, box w)."""
    ys, xs = np.nonzero(a)
    if len(ys) == 0:
        return None
    c = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = np.zeros((16, 16), np.float32)
    out[:c.shape[0], :c.shape[1]] = c[:16, :16]
    return out


def score(a, b):
    """Dice-like overlap with +-1 px shift tolerance."""
    best = 0.0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            s = np.roll(np.roll(b, dy, 0), dx, 1)
            inter = (a * s).sum()
            best = max(best, 2 * inter / (a.sum() + s.sum() + 1e-6))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--font", default="C:/Windows/Fonts/msgothic.ttc")
    ap.add_argument("--size", type=int, default=12)
    ap.add_argument("--start", type=lambda x: int(x, 0), default=0)
    a = ap.parse_args()
    f = ImageFont.truetype(a.font, a.size)
    chars = jis_chars()
    refs = []
    for ch in chars:
        r = norm(render(ch, f, a.size))
        if r is not None:
            refs.append((ch, r))
    R = np.stack([r for _, r in refs])  # n,16,16
    fb = gfont.load_font_bytes()
    lines = []
    for code in range(a.start, gfont.CELLS):
        g = gfont.glyph(fb, code)
        if gfont.is_blank(g):
            continue
        q = norm(np.array(gfont.stroke(g), np.float32))
        if q is None:
            continue
        # coarse rank by plain overlap, refine top 40 with shifts
        inter = (R * q).reshape(len(R), -1).sum(1)
        coarse = 2 * inter / (R.reshape(len(R), -1).sum(1) + q.sum())
        top = np.argsort(-coarse)[:40]
        sc = sorted(((score(q, R[i]), refs[i][0]) for i in top), reverse=True)
        lines.append(f"{code:03X}\t{sc[0][1]}\t{sc[0][0]:.3f}\t{sc[1][1]}\t{sc[1][0]:.3f}")
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(lines)} cells -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
