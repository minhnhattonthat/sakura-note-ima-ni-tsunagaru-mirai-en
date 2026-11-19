"""Message files parse and the jp table roundtrips every string byte-exactly with no unknown code."""
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
def test_jp_table_roundtrip():
    import msg
    from tbl import Table
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    files = msg.all_files()
    assert all(files.values())
    n = 0
    for ms in files.values():
        for w in ms:
            b = struct.pack("<%dH" % len(w), *w)
            txt, used = t.decode(b, 0, len(b))
            assert not re.search(r"\[[0-9A-F]{2}\]", txt), txt
            assert t.encode(txt) == b
            n += 1
    assert n == 5413
