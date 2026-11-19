"""Name-entry field patch (tools/namefield.py): 9 characters at a 12 px pitch."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"
need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")

import namefield  # noqa: E402

# what each patched word must disassemble to (capstone)
WANT = {
    0x020794F8: "cmp r1, #8", 0x0207961C: "cmp r0, #8", 0x020798C0: "cmp ip, #8", 0x020798C4: "movge ip, #8",
    0x02079B40: "add r2, r1, r1, lsl #1", 0x02079B44: "lsl r2, r2, #2", 0x02079B48: "mov r3, #0",
    0x02079B4C: "strd r2, r3, [sp]", 0x02079ABC: "add r1, r5, r5, lsl #1", 0x02079AC0: "add r1, r1, #0x14",
    0x02079AC4: "lsl r1, r1, #0xe", 0x0207F32C: "cmp r1, #0x12",
}


def test_words_disassemble():
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
    assert {a for a, *_ in namefield.PATCHES} == set(WANT)
    for a, _, new, _ in namefield.PATCHES:
        ins = next(md.disasm(struct.pack("<I", new), a))
        assert f"{ins.mnemonic} {ins.op_str}" == WANT[a], hex(a)


def test_pitch_fits_canvas():
    # the field canvas shows 7 cells of 16 px (112 px); 9 cells must fit at the new pitch
    assert namefield.MAX_CHARS * namefield.PITCH <= 7 * 16
    # cursor x for cell c: (c * 3 + 0x14) << 14 == (c * 12 + 0x50) << 12
    for c in range(namefield.MAX_CHARS):
        assert (c * 3 + 0x14) << 14 == (c * namefield.PITCH + 0x50) << 12


@need_rom
def test_patch_on_dump():
    import ndspy.code
    import romfs
    a9 = ndspy.code.MainCodeFile(bytes(romfs.load().arm9), namefield.ARM9_BASE)
    s0 = bytearray(a9.sections[0].data)
    log = []
    namefield.patch(s0, log)
    assert len(log) == sum(old != new for _, old, new, _ in namefield.PATCHES)
    for a, _, new, _ in namefield.PATCHES:
        assert struct.unpack_from("<I", s0, a - namefield.ARM9_BASE)[0] == new
    lo_hi = namefield.allowed()
    for off, old, new, _ in log:
        assert any(lo <= off and off + 4 <= hi for lo, hi, _ in lo_hi)
