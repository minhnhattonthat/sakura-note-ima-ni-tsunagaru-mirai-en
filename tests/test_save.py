"""tools/debug/save.py: checksum, both-copy writes, names; the scene list's shape."""
import csv
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
import save  # noqa: E402
from tbl import Table  # noqa: E402

FIXTURE = ROOT / "work" / "saves" / "s1_living.dsv"


def synthetic():
    """A save shaped like a game-written one: header, slot 1 used in both copies, valid checksums."""
    d = bytearray(b"\xff" * 0x8000)
    d[:0x20] = save.HEADER + b"\x01" + bytes(0x20 - len(save.HEADER) - 1)
    for copy in (0, 1):
        o = save.Save.off(0, copy)
        d[o:o + save.IMGSZ] = bytes(save.IMGSZ)
        d[o] = 1
    sv = save.Save(d)
    sv.fix(0)
    return sv


def test_checksum_matches_game_formula():
    img = bytearray(save.IMGSZ)
    img[0], img[0x10], img[0x99F] = 1, 0xB, 0xFF
    assert save.checksum(img) == (~(1 + 0xB + 0xFF)) & 0xFFFF
    img[0x9A0] = 0x55  # outside the summed range
    assert save.checksum(img) == (~(1 + 0xB + 0xFF)) & 0xFFFF


def test_put_writes_both_copies_and_fixes_sums():
    sv = synthetic()
    sv.put(0, *save.FIELDS["chapters"], 0xF)
    for copy in (0, 1):
        assert sv.slot_valid(0, copy)
        assert struct.unpack_from("<I", sv.image(0, copy), 0x16C)[0] == 0xF


def test_name_roundtrip_and_overflow():
    tbl = Table.load(ROOT / "tbl" / "jp.tbl")
    sv = synthetic()
    sv.set_name(0, "dog", "トオル", tbl)
    assert sv.name(0, "dog", tbl) == "トオル"
    assert sv.slot_valid(0, 0) and sv.slot_valid(0, 1)
    with pytest.raises(ValueError):
        sv.set_name(0, "dog", "トオル" * 4, tbl)


@pytest.mark.skipif(not FIXTURE.exists(), reason="no game-written fixture (tools/debug/make_save.py)")
def test_game_written_fixture_valid():
    sv = save.Save.read(FIXTURE)
    assert sv.slot_valid(0, 0) and sv.slot_valid(0, 1)
    assert sv.image(0, 0) == sv.image(0, 1)


def test_scenes_tsv_shape():
    with open(ROOT / "tools" / "debug" / "scenes.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    assert rows[0] == ["name", "mode", "keys", "expect", "save", "shows"]
    names = [r[0] for r in rows[1:]]
    assert len(names) == len(set(names))
    for r in rows[1:]:
        assert len(r) == 6, r
        assert r[1] in ("title", "debug"), r
        assert r[4] in ("", "s1_living", "all_chapters", "all_items"), r
