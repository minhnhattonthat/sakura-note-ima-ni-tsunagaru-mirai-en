"""script/ roundtrips to the original bytes, and the extracted ranges cover every string the ROM holds."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_script_roundtrip():
    """Every script/ entry re-encodes (header + jp + FFFD) to the original string bytes; ids match the files."""
    import script
    assert script.verify() == []


@needs_rom
def test_message_files_fully_covered():
    """Each message file = offset table (4 * count bytes) + its strings back to back to the end: no gap bytes."""
    import filedata
    import msg
    import romfs
    rom = romfs.load()
    fs = filedata.files(bytes(rom.getFileByName("FILEDATA.BIN")))
    for fid in range(msg.FIRST, msg.LAST + 1):
        d = fs[fid]
        ms = msg.parse(d)
        assert ms, fid
        assert 4 * len(ms) + sum(2 * len(w) for w in ms) == len(d), fid
        offs = struct.unpack_from("<%dI" % len(ms), d)
        assert offs[0] == 4 * len(ms), fid


@needs_rom
def test_arm9_strings_all_listed():
    """A scan of arm9 + overlays for FFFD-terminated runs of table codes with 2+ kana/kanji finds only the listed
    slots: nothing outside the message files is left unextracted."""
    import romfs
    import script
    rom = romfs.load()
    blobs = [("arm9", bytes(rom.arm9))] + [(f"ov{i}", bytes(rom.files[o.fileID]))
                                            for i, o in rom.loadArm9Overlays().items()]
    found = set()
    for name, b in blobs:
        w = struct.unpack_from("<%dH" % (len(b) // 2), b)
        for i, x in enumerate(w):
            if x != 0xFFFD:
                continue
            j = i
            while j > 0 and (w[j - 1] <= 0x662 or 0xFF00 <= w[j - 1] < 0xFFFD or w[j - 1] == 0xFFFF):
                j -= 1
            if sum(1 for c in w[j:i] if 0x10 <= c <= 0x662) >= 2:
                while w[j] == 0:  # zero pad from the previous slot (cell 0 is never text)
                    j += 1
                found.add((name, 2 * j))
    assert found == {("arm9", off) for off, _, _ in script.ARM9_SLOTS}
