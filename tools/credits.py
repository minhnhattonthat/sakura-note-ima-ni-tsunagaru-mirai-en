"""credits.py: the staff roll's line positions (arm9 overlay 1) and their re-centring for the English (docs/re/credits.md).

    python -X utf8 tools/credits.py            # list every credits line call: index, x, y gap, JP / EN

The ending overlay (NitroFS file 1, loaded at 0x021C29C0) builds the roll in code: per line
`mov r1, #<2604 index>; mov r2, #<x>; mov r3, #<y gap>; str r6, [sp]; bl LINE_CTOR`. The ctor stores x at
obj+0x28, which becomes the left edge of the line's row of 32x16 sprites (the text is drawn from pen x 0 of the
line's own buffer). So each x is an ARM `mov r2, #imm` immediate; centring the English = rewriting those immediates
from the English width (vwf.text_width of the entry's widest line). The text engine itself centres each line of an
entry inside its widest line (measured: an unpadded "Aki Ota" under "Masayuki Hashimoto" sits centred), so x is
the only change. 2604:76-78 have no call: never shown.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

OVERLAY = 1           # NitroFS file id of the ending overlay
OV_BASE = 0x021C29C0
LINE_CTOR = 0x021D0928
CENTRE = 128          # screen centre (the JP lines are pre-centred about here)
MAX_PX = 224          # widest JP line = 7 sprites of 32 px; English lines stay within it
MSG = 2604


def arm_imm(w):
    """Value of an ARM data-processing immediate operand."""
    rot, imm = (w >> 8) & 0xF, w & 0xFF
    return ((imm >> (2 * rot)) | (imm << (32 - 2 * rot))) & 0xFFFFFFFF


def mov_imm(w, rd):
    """imm if w is `mov rd, #imm` (cond AL, no S), else None."""
    if w & 0xFFF0F000 == 0xE3A00000 | (rd << 12) and (w >> 16) & 0xF == 0:
        return arm_imm(w)
    return None


def encode_mov(rd, value):
    """`mov rd, #value` for 0 <= value < 256."""
    assert 0 <= value < 256, value
    return 0xE3A00000 | (rd << 12) | value


def bl_target(w, addr):
    if w >> 24 != 0xEB:
        return None
    off = w & 0xFFFFFF
    off -= (off & 0x800000) << 1
    return addr + 8 + (off << 2)


def calls(ov):
    """[(bl file offset, 2604 index, x file offset, x, y gap)] for every LINE_CTOR call; raises if a call's
    arguments aren't the expected immediates."""
    out = []
    for p in range(0, len(ov) - 3, 4):
        w = struct.unpack_from("<I", ov, p)[0]
        if bl_target(w, OV_BASE + p) != LINE_CTOR:
            continue
        idx = xoff = x = y = None
        y_is_r1 = False
        for q in range(p - 4, p - 28, -4):
            v = struct.unpack_from("<I", ov, q)[0]
            if v >> 24 in (0xEB, 0xEA, 0x0A, 0x1A) or v >> 25 == 0x7D:  # bl/b/beq/bne/blx: the previous call
                break
            if idx is None and (i := mov_imm(v, 1)) is not None:
                idx = i
            elif xoff is None and (i := mov_imm(v, 2)) is not None:
                xoff, x = q, i
            elif y is None and (i := mov_imm(v, 3)) is not None:
                y = i
            elif y is None and v == 0xE1A03001:  # mov r3, r1
                y_is_r1 = True
        if y_is_r1 and y is None:
            y = idx
        if None in (idx, xoff, y):
            raise ValueError(f"credits call at {OV_BASE + p:#x}: arguments not all immediates")
        out.append((p, idx, xoff, x, y))
    return out


def line_widths(text):
    import vwf
    import batches
    return [vwf.text_width(batches.TOKEN.sub("", ln), batches.GLYPHS) for ln in text.split("{n}")]


def centred_x(text):
    w = max(line_widths(text))
    if w > MAX_PX:
        raise ValueError(f"credits line {text!r}: {w} px > {MAX_PX}")
    return CENTRE - (w + 1) // 2


def patch_overlay(ov, rows, log=None):
    """Overlay bytes with every translated line's x re-centred (writelog entries in log, overlay offsets)."""
    from writelog import put
    out = bytearray(ov)
    byid = {r["id"]: r for r in rows}
    for p, idx, xoff, x, y in calls(ov):
        r = byid[f"{MSG}:{idx}"]
        if not r.get("en"):
            continue
        new = centred_x(r["en"])
        if new != x:
            put(out, xoff, struct.pack("<I", encode_mov(2, new)), f"credits x {MSG}:{idx}", log,
                struct.pack("<I", encode_mov(2, x)))
    return bytes(out)


def main():
    import romfs
    import script
    ov = bytes(romfs.load().files[OVERLAY])
    rows = {r["id"]: r for r in script.load(f"msg_{MSG}.json")}
    cs = calls(ov)
    for p, idx, xoff, x, y in cs:
        r = rows[f"{MSG}:{idx}"]
        en = r.get("en", "")
        print(f"{OV_BASE + p:08X} {MSG}:{idx:<3} x={x:<3} gap={y:<3} new_x={centred_x(en) if en else '-':<4} "
              f"{en.replace('{n}', ' / ')}")
    print(f"{len(cs)} calls, {len({c[1] for c in cs})} distinct indices, {len(rows)} entries in {MSG}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
