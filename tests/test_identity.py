"""Identity build: unpack and repack with no edits gives the dump byte for byte (FILEDATA and whole ROM)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import filedata  # noqa: E402
import romfs  # noqa: E402

pytestmark = pytest.mark.skipif(not romfs.ROM.is_file(), reason="no ROM dump in rom/")


def test_filedata_identity():
    blob = bytes(romfs.load().getFileByName("FILEDATA.BIN"))
    assert filedata.build(blob, filedata.files(blob)) == blob


def test_filedata_resized_entry_stays_aligned():
    blob = bytes(romfs.load().getFileByName("FILEDATA.BIN"))
    p = filedata.files(blob)
    p[5] = p[5] + b"\x01"
    new = filedata.build(blob, p)
    h = filedata.parse(new)
    assert all(o % 4 == 0 for o, _ in h["entries"])
    assert filedata.files(new)[5] == p[5] and filedata.files(new)[6] == p[6]


def test_rom_identity():
    orig = romfs.ROM.read_bytes()
    assert build.build(orig) == orig
