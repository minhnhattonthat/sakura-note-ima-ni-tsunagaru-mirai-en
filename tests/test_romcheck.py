"""Phase 7 ROM audit (tools/romcheck.py) on a ROM this test builds itself, plus tampered copies it must reject."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import romfs  # noqa: E402

pytestmark = pytest.mark.skipif(not romfs.ROM.exists(), reason="original ROM not present")


@pytest.fixture(scope="module")
def built():
    import build
    orig = romfs.ROM.read_bytes()
    writes = {}
    return orig, build.build(orig, mode="en", writes=writes), writes


def run(orig, rom, writes):
    import romcheck
    return romcheck.check(orig, rom, writes)[0]


def test_en_build_passes(built):
    assert run(*built) == []


def arm9_rom_offset(rom):
    return struct.unpack_from("<I", rom, 0x20)[0]


def test_stray_arm9_byte_fails(built):
    orig, rom, writes = built
    bad = bytearray(rom)
    bad[arm9_rom_offset(rom) + 0x50000] ^= 0xFF  # section 0, no write there
    assert any("differing bytes outside" in e for e in run(orig, bytes(bad), writes))


def test_write_log_with_wrong_original_fails(built):
    orig, rom, writes = built
    w = list(writes["arm9"])
    off, old, new, by = w[0]
    w[0] = (off, bytes(len(old)), new, by)
    assert any("expects orig" in e for e in run(orig, rom, {**writes, "arm9": w}))


def test_unlogged_write_fails(built):
    orig, rom, writes = built
    w = {**writes, "arm9": [w for w in writes["arm9"] if "hook" not in w[3]]}
    assert any("outside writes" in e for e in run(orig, rom, w))
    w = {**writes, "overlay1": writes["overlay1"][1:]}
    assert any("overlay 1" in e and "outside writes" in e for e in run(orig, rom, w))


def test_logged_arm9_write_outside_allowed_regions_fails(built):
    """A write the log records accurately still fails when it is not in a string slot or hook site."""
    orig, rom, writes = built
    off = 0x50000
    bad = bytearray(rom)
    a9 = arm9_rom_offset(rom)
    old = bytes(bad[a9 + off:a9 + off + 1])
    bad[a9 + off] ^= 0xFF
    w = {**writes, "arm9": writes["arm9"] + [(off, old, bytes(bad[a9 + off:a9 + off + 1]), "stray")]}
    assert any("not inside a string slot or hook site" in e for e in run(orig, bytes(bad), w))


def test_arm9_write_spilling_past_its_slot_fails():
    import romcheck
    import script
    off, slot, _ = script.ARM9_SLOTS[0]
    errs = []
    romcheck.check_arm9_regions([(off, bytes(slot + 2), bytes(slot + 2), "too long")], errs)
    assert errs and "not inside" in errs[0]
    errs = []
    romcheck.check_arm9_regions([(off, bytes(slot), bytes(slot), "fits")], errs)
    assert errs == []


def overlay_tamper(built, new_bytes):
    """Replace the first credits-x write's new bytes in the overlay and its log entry; returns the errors."""
    import ndspy.rom
    import credits
    orig, rom, writes = built
    r = ndspy.rom.NintendoDSRom(rom)
    ov = bytearray(r.files[credits.OVERLAY])
    off, old, _, by = writes["overlay1"][0]
    old = bytes(ndspy.rom.NintendoDSRom(orig).files[credits.OVERLAY][off:off + len(new_bytes)])
    ov[off:off + len(new_bytes)] = new_bytes
    r.files[credits.OVERLAY] = bytes(ov)
    import build
    out = build.fix_ndspy(orig, r.save())
    w = {**writes, "overlay1": [(off, old, new_bytes, by)] + writes["overlay1"][1:]}
    return run(orig, out, w)


def test_credits_write_not_a_mov_fails(built):
    assert any("not `mov r2, #imm`" in e for e in overlay_tamper(built, bytes(4)))


def test_credits_write_wrong_x_fails(built):
    import credits
    assert any("centred x" in e for e in overlay_tamper(built, struct.pack("<I", credits.encode_mov(2, 3))))


def test_credits_write_longer_than_one_instruction_fails(built):
    import ndspy.rom
    import credits
    orig, rom, writes = built
    off = writes["overlay1"][0][0]
    cur = bytes(ndspy.rom.NintendoDSRom(rom).files[credits.OVERLAY][off:off + 8])
    assert any("exactly one instruction" in e for e in overlay_tamper(built, cur[:4] + bytes(4)))


def test_credits_centring_follows_qa_override(monkeypatch):
    """A --qa override's text is what the credits x is centred on (2604:1 at 224 px -> x 16)."""
    import build
    import credits
    import insert
    import ndspy.rom
    monkeypatch.setitem(insert.QA, "2604:1", "@224")
    rom = ndspy.rom.NintendoDSRom(romfs.ROM.read_bytes())
    build.edit_overlays(rom, "en", {})
    xs = {idx: x for _, idx, _, x, _ in credits.calls(bytes(rom.files[credits.OVERLAY]))}
    assert xs[1] == 128 - 112


def test_credits_calls_and_centring():
    import credits
    ov = bytes(romfs.load().files[credits.OVERLAY])
    cs = credits.calls(ov)
    assert len(cs) == 77 and {c[1] for c in cs} == set(range(76))  # 2604:3 twice; 76-78 never shown
    assert [c[3] for c in cs[:7]] == [88, 96, 92, 112, 72, 20, 100]  # the x measured in game (docs/re/boxes.md)
    assert credits.centred_x("Masayuki Hashimoto{n}Aki Ota") == 128 - 49   # widest line 97 px
    assert credits.encode_mov(2, 0x58) == 0xE3A02058 and credits.mov_imm(0xE3A02058, 2) == 0x58
    with pytest.raises(ValueError):
        credits.centred_x("W" * 40)


def test_other_nitrofs_file_change_fails(built):
    import ndspy.rom
    orig, rom, writes = built
    r = ndspy.rom.NintendoDSRom(rom)
    fat = struct.unpack_from("<I", rom, 0x48)[0]
    i = next(k for k in range(len(r.files)) if k != r.filenames.idOf("FILEDATA.BIN"))
    start = struct.unpack_from("<I", rom, fat + 8 * i)[0]
    bad = bytearray(rom)
    bad[start + 16] ^= 1
    assert any(f"NitroFS file {i}" in e for e in run(orig, bytes(bad), writes))


def test_script_mismatch_fails(built, monkeypatch):
    import romcheck
    orig, rom, writes = built
    real = romcheck.script.load

    def load(name):
        rows = real(name)
        if name == "msg_2500.json":
            rows = [dict(r) for r in rows]
            r = next(r for r in rows if r.get("en"))
            r["en"] += "x"
        return rows
    monkeypatch.setattr(romcheck.script, "load", load)
    assert any("!= script" in e for e in run(orig, rom, writes))


def test_branch_into_hook_span_detected():
    import romcheck
    base = 0x02000000
    code = bytearray(16)
    # B from base+0 to base+12: imm24 = (12 - 8) >> 2 = 1
    struct.pack_into("<I", code, 0, 0xEA000001)
    assert (base, base + 12) in romcheck.branch_targets(bytes(code), base)
