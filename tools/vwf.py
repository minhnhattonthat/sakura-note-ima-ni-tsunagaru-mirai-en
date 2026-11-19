"""vwf.py: English variable-width fonts for dialogue (FILEDATA 860) and speaker tags (FILEDATA 872), and the arm9 hooks.

Dialogue: the text engine draws each code's 16x16 cell pixel by pixel onto a bitmap canvas (0x02037FA0, value 0 =
clear, skipped) and moves the pen by 0x02037A00 (ctx, code, metrics) -> advance px; width measures (centring) call
the same function. Speaker tags (file 2610, index = message header word0): 0x02039090 draws up to 16 codes <= 0x100
from the 8x8 font 872 at a fixed 8 px step (`add sb, sb, #8` at 0x02039104). See docs/re/vwf.md.

Encoding (one table for both fonts, en_table()):
- letters, digits and < > ; : ' + - * / = % & @ ( ) use the codes the Japanese table already gives them (0xB0-0xFD,
  the name-entry keyboard's Latin), so typed names, tags and dialogue share them. Their big-font cells get the VWF
  glyphs; their small-font cells are shifted flush left.
- every other ASCII character at 0x680 + (c - 0x20), EXTRAS from 0x6DF (blank cells in the big font only).
- tags (tag_table()) map space . ! ? to the small font's 0x0F 0x05 0x09 0x0A.

Hooks (new arm9 autoload block at the old main-arena start 0x021D6540; `OS_GetInitArenaLo(0)` literal at 0x0200E284
raised past it):
- 0x02037A00 -> `ldr pc, [pc, #-4]` to adv_hook: width-table byte for codes 0xB0-0xFF and 0x680-0x6FF, else the
  original function.
- 0x02039104 -> `bl tag_hook`: adds the small-font width of the code just drawn, then `cmp r8, #TAG_MAX`.

    python -X utf8 tools/vwf.py sheet OUT.png      # the English big-font cells, zoomed
    python -X utf8 tools/vwf.py tbl OUT.tbl        # write the English table to a file
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GLYPH_FILE = ROOT / "fonts" / "vwf_glyphs.txt"
BIG_FONT, SMALL_FONT = 860, 872
BASE = 0x680          # first English-only cell (big font)
LAST = 0x6FF          # last cell in the big font (1792 cells)
LOW, LOW_END = 0xB0, 0x100  # shared Latin codes (both fonts)
EXTRAS = "…—é♪♥"      # after ASCII, from 0x6DF
CELL_Y = 2            # glyph row 0 sits at cell row 2
ROWS = 10
STROKE, SHADOW = 1, 15
SMALL_STROKE = 8
FONT_HDR = 0x30       # RGCN header + RAHC block header before the tile data
TAG_EXTRA = {" ": 0x0F, ".": 0x05, "!": 0x09, "?": 0x0A}
TAG_SPACE_PX = 3
TAG_MAX = 20          # tag loop limit in codes (was 16; file tags hold at most 18)

ARM9_BASE = 0x02000000
ADV_FUNC = 0x02037A00  # advance(ctx r0, code r1, metrics r2) -> r0
ORIG_ADV = bytes.fromhex("0b00e0e3000051e10300001a040092e5a00f80e0c000a0e11eff2fe1")
TAG_LOOP = 0x020390C4  # tag loop start in 0x02039090 (r0 = tag string, r4 = ctx); replaced by tag_hook
ORIG_TAG = bytes.fromhex("0080a0e30070a0e1")  # mov r8, #0; mov r7, r0
SMALL_DRAW = 0x02038648  # draw one 8x8 code (ctx, [ctx+0x20], colour, code, [sp] = x)
TAG_FILE_SLOTS = 9     # 0x020360F4 copies 10 u16 of the tag (9 + FFFD): packed two codes per u16 = 18 chars
ARENA_LIT = 0x0200E284  # literal returned by OS_GetInitArenaLo(OS_ARENA_MAIN)
HOOK = 0x021D6540      # original main arena lo = our block's RAM address


def load_glyphs(path=GLYPH_FILE):
    """{char: [row strings]} from the glyph file."""
    out, cur = {}, None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("#") and cur is None or not line:
            continue
        if line.startswith("@ "):
            name = line[2:]
            ch = " " if name == "space" else name
            if len(ch) != 1 or ch in out:
                raise ValueError(f"{path.name}:{n}: bad or duplicate glyph name {name!r}")
            cur = out[ch] = []
            continue
        if cur is None:
            continue
        if set(line) - set(".#") or (cur and len(line) != len(cur[0])):
            raise ValueError(f"{path.name}:{n}: bad row {line!r}")
        cur.append(line)
    for ch, rows in out.items():
        if len(rows) != ROWS:
            raise ValueError(f"glyph {ch!r}: {len(rows)} rows, want {ROWS}")
    return out


def jp_table():
    return Table.load(ROOT / "tbl" / "jp.tbl")


def shared_codes():
    """{ascii char: code} for the Latin the Japanese table already maps in 0xB0-0xFF."""
    out = {}
    for k, v in jp_table().dec.items():
        c = int.from_bytes(k, "little")
        if LOW <= c < LOW_END and len(v) == 1 and 0x20 < ord(v) < 0x7F:
            out[v] = c
    return out


def code_map(glyphs=None):
    """{char: big-font code} for every English glyph."""
    glyphs = glyphs or load_glyphs()
    m = {chr(c): BASE + c - 0x20 for c in range(0x20, 0x7F)}
    m.update(shared_codes())
    for i, ch in enumerate(EXTRAS):
        m[ch] = BASE + 0x5F + i
    missing = set(m) - set(glyphs)
    extra = set(glyphs) - set(m)
    if missing or extra:
        raise ValueError(f"glyph file: missing {sorted(missing)}, unmapped {sorted(extra)}")
    assert max(m.values()) <= LAST
    return m


def advance(rows):
    return len(rows[0]) + 1


def width_tables(glyphs=None):
    """(low, high): advance px per code LOW..LOW_END-1 and BASE..LAST (bytes); unused cells get 12 / 6."""
    glyphs = glyphs or load_glyphs()
    low = bytearray([12] * (LOW_END - LOW))
    high = bytearray([6] * (LAST - BASE + 1))
    for ch, code in code_map(glyphs).items():
        if code >= BASE:
            high[code - BASE] = advance(glyphs[ch])
        else:
            low[code - LOW] = advance(glyphs[ch])
    return bytes(low), bytes(high)


def text_width(text, glyphs=None):
    """Pixel width of plain English text (no control codes) in the dialogue font."""
    glyphs = glyphs or load_glyphs()
    return sum(advance(glyphs[c]) for c in text)


def _set_px16(tiles, code, x, y, v):
    r, c = divmod(code, 16)
    t = (2 * r + y // 8) * 32 + (2 * c + x // 8)
    i = t * 64 + (y % 8) * 8 + (x % 8)
    b = tiles[i // 2]
    tiles[i // 2] = (b & 0x0F) | (v << 4) if i & 1 else (b & 0xF0) | v


def patch_font(font):
    """Big-font file bytes with the English glyphs drawn into their cells."""
    assert font[:4] == b"RGCN", font[:4]
    out = bytearray(font)
    tiles = memoryview(out)[FONT_HDR:]
    glyphs = load_glyphs()
    for ch, code in code_map(glyphs).items():
        rows = glyphs[ch]
        for x in range(16):
            for y in range(16):
                _set_px16(tiles, code, x, y, 0)
        for y, row in enumerate(rows):
            for x, p in enumerate(row):
                if p != "#":
                    continue
                _set_px16(tiles, code, x, CELL_Y + y, STROKE)
                below = rows[y + 1][x] if y + 1 < ROWS else "."
                if below != "#":
                    _set_px16(tiles, code, x, CELL_Y + y + 1, SHADOW)
    return bytes(out)


def _small_cell(tiles, c):
    return [[(tiles[(c * 64 + y * 8 + x) // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]


def _put_small_cell(tiles, c, px):
    for y in range(8):
        for x in range(0, 8, 2):
            tiles[(c * 64 + y * 8 + x) // 2] = px[y][x] | (px[y][x + 1] << 4)


def small_codes():
    """{char: small-font code} for English tags."""
    m = dict(shared_codes())
    m.update(TAG_EXTRA)
    return m


def patch_small_font(font):
    """(small-font bytes with the tag Latin cells flush left, 256-byte advance table)."""
    assert font[:4] == b"RGCN", font[:4]
    out = bytearray(font)
    tiles = memoryview(out)[FONT_HDR:]
    widths = bytearray([8] * 256)
    for ch, c in small_codes().items():
        px = _small_cell(tiles, c)
        cols = [x for x in range(8) if any(px[y][x] for y in range(8))]
        if not cols:
            widths[c] = TAG_SPACE_PX
            continue
        lo, hi = min(cols), max(cols)
        _put_small_cell(tiles, c, [row[lo:] + [0] * lo for row in px])
        widths[c] = hi - lo + 1
    return bytes(out), bytes(widths)


def small_widths():
    import filedata
    import romfs
    return patch_small_font(filedata.files(bytes(romfs.load().getFileByName("FILEDATA.BIN")))[SMALL_FONT])[1]


HOOK_ASM = """
adv_hook:
    sub   ip, r1, #{base}
    cmp   ip, #{nhigh}
    blo   adv_high
    sub   ip, r1, #{low}
    cmp   ip, #{nlow}
    bhs   adv_orig
    adr   r0, w_low
    ldrb  r0, [r0, ip]
    bx    lr
adv_high:
    adr   r0, w_high
    ldrb  r0, [r0, ip]
    bx    lr
adv_orig:
    mvn   r0, #0xb
    cmp   r1, r0
    bne   adv_notsp
    ldr   r0, [r2, #4]
    add   r0, r0, r0, lsr #31
    asr   r0, r0, #1
    bx    lr
adv_notsp:
    ldr   r0, [r2]
    cmp   r0, #1
    cmpne r0, #3
    bne   adv_full
    cmp   r1, #0x100
    ldrlt r0, [r2, #0xc]
    ldrge r0, [r2, #4]
    bx    lr
adv_full:
    ldr   r0, [r2, #4]
    bx    lr
tag_hook:
    mov   r7, r0
    mov   r8, #0
    mov   sb, #0
    ldr   r5, [r4, #0x148]
    cmp   r5, #4
    movls r5, #1
    movhi r5, #0
tag_next:
    cmp   r8, #{tag_max}
    bge   tag_done
    cmp   r5, #0
    bne   tag_u16
    ldrb  r3, [r7, r8]
    cmp   r3, #0xfd
    bhs   tag_done
    b     tag_draw
tag_u16:
    add   r0, r7, r8, lsl #1
    ldrsh r3, [r0]
    cmn   r3, #3
    beq   tag_done
tag_draw:
    mov   r6, r3
    str   sb, [sp]
    ldr   r1, [r4, #0x20]
    mov   r0, r4
    mov   r2, #0
    bl    #{small_draw}
    mov   ip, #8
    cmp   r6, #0x100
    adrlo r0, w_small
    ldrblo ip, [r0, r6]
    add   sb, sb, ip
    add   r8, r8, #1
    b     tag_next
tag_done:
    pop   {{r3, r4, r5, r6, r7, r8, sb, pc}}
"""


def hook_block():
    """(bytes of the autoload block at HOOK, {label: address})."""
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM
    low, high = width_tables()
    small = small_widths()
    src = HOOK_ASM.format(base=hex(BASE), nhigh=hex(LAST - BASE + 1), low=hex(LOW), nlow=hex(LOW_END - LOW),
                          tag_max=hex(TAG_MAX), small_draw=hex(SMALL_DRAW))
    ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)
    tables = [("w_low", low), ("w_high", high), ("w_small", small)]
    data = "".join(f"{name}:\n" + "".join(f".byte {','.join(str(b) for b in t[i:i + 16])}\n"
                                          for i in range(0, len(t), 16)) for name, t in tables)
    code, _ = ks.asm(src + data, HOOK)
    blob = bytes(code)
    n = len(blob) - sum(len(t) for _, t in tables)
    assert blob[n:] == low + high + small
    labels = {"adv_hook": HOOK, "w_low": HOOK + n}
    labels["w_high"] = labels["w_low"] + len(low)
    labels["w_small"] = labels["w_high"] + len(high)
    pre, _ = ks.asm(src.split("tag_hook:")[0] + "tag_hook:\n" + data, HOOK)
    labels["tag_hook"] = HOOK + len(pre) - len(low + high + small)
    return blob + b"\0" * (-len(blob) % 32), labels


def pack_tag(codes):
    """Tag body bytes: small-font codes two per u16 (low byte first), 0xFF pad; the caller adds FFFD."""
    if any(not 0 <= c < 0xFD for c in codes):
        raise ValueError(f"tag code outside the small font's 0x00-0xFC: {[hex(c) for c in codes]}")
    if len(codes) > 2 * TAG_FILE_SLOTS:
        raise ValueError(f"tag of {len(codes)} codes; at most {2 * TAG_FILE_SLOTS} fit")
    b = bytes(codes)
    return b + b"\xff" * (len(b) % 2)


def patch_arm9(arm9):
    """arm9.bin bytes with the advance and tag hooks and their autoload block added."""
    import ndspy.code
    a9 = ndspy.code.MainCodeFile(arm9, ARM9_BASE)
    s0 = a9.sections[0]
    d = bytearray(s0.data)
    off = ADV_FUNC - ARM9_BASE
    toff = TAG_LOOP - ARM9_BASE
    if d[off:off + len(ORIG_ADV)] != ORIG_ADV or d[toff:toff + len(ORIG_TAG)] != ORIG_TAG:
        raise ValueError("hook sites differ from the dump")
    if struct.unpack_from("<I", d, ARENA_LIT - ARM9_BASE)[0] != HOOK:
        raise ValueError("arena-lo literal differs from the dump")
    block, labels = hook_block()
    struct.pack_into("<II", d, off, 0xE51FF004, labels["adv_hook"])  # ldr pc, [pc, #-4]; .word adv_hook
    struct.pack_into("<II", d, toff, 0xE51FF004, labels["tag_hook"])
    struct.pack_into("<I", d, ARENA_LIT - ARM9_BASE, HOOK + len(block))
    s0.data = bytes(d)
    a9.sections.append(ndspy.code.MainCodeFile.Section(block, HOOK, 0))
    return a9.save(compress=False)


def _ctrl_lines():
    return [ln for ln in (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines()
            if "={" in ln and not ln.startswith("#")]


def _line(ch, code):
    return f"{struct.pack('<H', code).hex().upper()}={chr(92) + 's' if ch == ' ' else ch}"


def en_table():
    """Table for English dialogue: the jp table's control codes + the English glyphs."""
    return Table(_ctrl_lines() + [_line(ch, code) for ch, code in code_map().items()])


def tag_table():
    """Table for English speaker tags (file 2610): small-font codes only."""
    return Table(_ctrl_lines() + [_line(ch, code) for ch, code in small_codes().items()])


def tag_width(text, widths=None):
    widths = widths or small_widths()
    m = small_codes()
    return sum(widths[m[c]] for c in text)


def sheet(out):
    from PIL import Image
    import filedata
    import font as fontmod
    import romfs
    glyphs = load_glyphs()
    m = code_map(glyphs)
    pal = {0: (40, 40, 60), STROKE: (255, 255, 255), SHADOW: (120, 120, 140)}
    font = patch_font(filedata.files(bytes(romfs.load().getFileByName("FILEDATA.BIN")))[BIG_FONT])
    chars = sorted(m, key=m.get)
    cols = 16
    img = Image.new("RGB", (cols * 17, ((len(chars) + cols - 1) // cols) * 17), (0, 0, 0))
    for k, ch in enumerate(chars):
        g = fontmod.glyph(font, m[ch])
        for y in range(16):
            for x in range(16):
                img.putpixel(((k % cols) * 17 + x, (k // cols) * 17 + y), pal.get(g[y][x], (255, 0, 0)))
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sheet").add_argument("out")
    sub.add_parser("tbl").add_argument("out")
    a = ap.parse_args()
    if a.cmd == "sheet":
        sheet(a.out)
    else:
        t = en_table()
        Path(a.out).write_text("".join(f"{k.hex().upper()}={v}\n" for k, v in t.dec.items()), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
