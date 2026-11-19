"""VWF font, English tables, tag packing and the arm9 hooks (tools/vwf.py, tools/insert.py)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")

import vwf  # noqa: E402

PRINTABLE = "".join(chr(c) for c in range(0x20, 0x7F))


def test_glyph_file_and_code_map():
    g = vwf.load_glyphs()
    m = vwf.code_map(g)
    assert set(PRINTABLE + vwf.EXTRAS) == set(m)
    assert len(set(m.values())) == len(m)  # no two characters share a code
    for ch, code in m.items():
        assert vwf.LOW <= code < vwf.LOW_END or vwf.BASE <= code <= vwf.LAST, (ch, hex(code))
        assert all(len(r) <= 15 for r in g[ch])  # ink + 1 px gap fits the 16 px cell
    assert m["A"] == 0xB0 and m["a"] == 0xD0 and m["0"] == 0xF0  # the name-entry Latin codes
    assert m[" "] == 0x680 and m["!"] == 0x681


def test_en_table_roundtrip_torture_line():
    t = vwf.en_table()
    line = PRINTABLE + "  double  spaces " + vwf.EXTRAS + "{n}{var_EF}{slot}{page}"
    b = t.encode(line)
    assert t.decode(b, 0, len(b))[0] == line


def test_width_tables():
    low, high = vwf.width_tables()
    assert len(low) == vwf.LOW_END - vwf.LOW and len(high) == vwf.LAST - vwf.BASE + 1
    assert high[0] == 4  # space
    assert low[0xBC - vwf.LOW] == 8 and low[0xD8 - vwf.LOW] == 2  # M, i
    assert vwf.text_width("Hi!") == 6 + 2 + 2


def test_pack_tag():
    assert vwf.pack_tag([0xB0, 0xD0, 0xD1]) == bytes([0xB0, 0xD0, 0xD1, 0xFF])
    assert vwf.pack_tag([0xB0, 0xD0]) == bytes([0xB0, 0xD0])
    with pytest.raises(ValueError):
        vwf.pack_tag([0xB0] * 19)
    with pytest.raises(ValueError):
        vwf.pack_tag([0x140])
    # ')' is tag code 0xFD, the packed tag's stop byte (docs/re/boxes.md): rejected, not silently cut
    codes = struct.unpack("<H", vwf.tag_table().encode(")"))
    with pytest.raises(ValueError):
        vwf.pack_tag(list(codes))


def test_qa_fill_exact_widths():
    import insert
    ctx = insert.Ctx()
    for w in (4, 9, 40, 41, 164, 216, 240):  # odd widths need the 5 px 'k': 9 is the smallest
        s = insert.fill(w, ctx.width)
        assert ctx.width(s) == w and s[0] == s[-1] == "|", (w, s)
    r = {"id": "2605:3", "jp": "{col_F8}名前{n}{n}{col_FC}本文"}
    text = insert.qa_text(r, "@216,4,216", ctx)
    assert text.startswith("{col_F8}|") and text.count("{n}") == 2
    assert insert.qa_text(r, "plain text", ctx) == "plain text"


@need_rom
def test_hook_block_tables_and_labels():
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
    blob, lab = vwf.hook_block()
    low, high = vwf.width_tables()
    n = lab["w_low"] - vwf.HOOK
    assert blob[n:n + len(low)] == low
    assert blob[lab["w_high"] - vwf.HOOK:][:len(high)] == high
    assert len(blob) % 32 == 0
    code = list(Cs(CS_ARCH_ARM, CS_MODE_ARM).disasm(blob[:n], vwf.HOOK))
    assert len(code) * 4 == n  # every word disassembles
    # every adr (add rX, pc, #imm) points at a width table
    targets = {i.address + 8 + int(i.op_str.split("#")[1], 16) for i in code
               if i.mnemonic.startswith("add") and ", pc, #" in i.op_str}
    assert targets == {lab["w_low"], lab["w_high"], lab["w_small"]}
    assert any(i.address == lab["tag_hook"] for i in code)


@need_rom
def test_patch_arm9():
    import ndspy.code
    import romfs
    a9 = bytes(romfs.load().arm9)
    new = vwf.patch_arm9(a9)
    m = ndspy.code.MainCodeFile(new, vwf.ARM9_BASE)
    assert m.sections[-1].ramAddress == vwf.HOOK
    s0 = m.sections[0].data
    assert struct.unpack_from("<II", s0, vwf.ADV_FUNC - vwf.ARM9_BASE) == (0xE51FF004, vwf.HOOK)
    lo = struct.unpack_from("<I", s0, vwf.ARENA_LIT - vwf.ARM9_BASE)[0]
    assert lo == vwf.HOOK + len(m.sections[-1].data)
    orig = ndspy.code.MainCodeFile(a9, vwf.ARM9_BASE)
    for a, b in zip(orig.sections[1:], m.sections[1:-1]):  # ITCM / DTCM blocks unchanged
        assert (a.ramAddress, a.data, a.bssSize) == (b.ramAddress, b.data, b.bssSize)


@need_rom
def test_small_font_cells_flush_left():
    import filedata
    import romfs
    font = filedata.files(bytes(romfs.load().getFileByName("FILEDATA.BIN")))[vwf.SMALL_FONT]
    new, widths = vwf.patch_small_font(font)
    tiles = new[vwf.FONT_HDR:]
    for ch, c in vwf.small_codes().items():
        px = vwf._small_cell(tiles, c)
        if ch != " ":
            assert any(px[y][0] for y in range(8)), ch
        assert 1 <= widths[c] <= 8, ch
