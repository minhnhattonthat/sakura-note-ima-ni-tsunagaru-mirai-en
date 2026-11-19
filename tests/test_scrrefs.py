"""tools/scrrefs.py: SCR0 parse and message references, against facts seen in the emulator (docs/re/scripts.md)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import scrrefs  # noqa: E402

ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"


def synthetic():
    """One function StartScript: SetMessageFile(2499); MessageObjWait(5, 0, var, 3, var, 0); return."""
    code = [0x4001, 2499, 0x2102, 0, 0xA000,
            0x4000, 5, 0x4000, 0, 0x601A, 4, 0x4000, 3, 0x601A, 5, 0x4000, 0, 0x2102, 1, 0xA000, 0x0108]
    d = bytearray(0x200)
    d[:4] = b"SCR0"
    struct.pack_into("<HH", d, 8, 1, 2)
    struct.pack_into("<4I", d, 0x20, 0x40, 0, 0x100, 0x140)
    struct.pack_into("<I", d, 0x40 + 0x10, len(code))
    d[0x60:0x6B] = b"StartScript"
    struct.pack_into(f"<{len(code)}H", d, 0x80, *code)
    for o, name, argc in ((0x100, b"SetMessageFile", 1), (0x140, b"MessageObjWait", 6)):
        struct.pack_into("<H", d, o + 6, argc)
        d[o + 0x20:o + 0x20 + len(name)] = name
    return bytes(d)


def test_synthetic_call_args():
    got = [(fn, nm, args) for fn, nm, args in scrrefs.calls(synthetic())]
    assert got[0] == ("StartScript", "SetMessageFile", [2499])
    assert got[1] == ("StartScript", "MessageObjWait", [5, 0, None, 3, None, 0])


@pytest.mark.skipif(not ROM.exists(), reason="needs the original ROM")
def test_seen_in_emulator():
    import filedata
    import romfs
    files = filedata.files(romfs.load().getFileByName("FILEDATA.BIN"))
    r = scrrefs.refs(files)
    # event 1943 (opening) showed 2499:0-1, event 2000 showed 2523:31-37, NPC 1144's NearScript showed 2499:2
    assert all(1943 in r[(2499, i)] for i in (0, 1))
    assert all(2000 in r[(2523, i)] for i in range(31, 38))
    assert 1144 in r[(2499, 2)]
    events = {a[0] for fn, nm, a in scrrefs.calls(files[1230]) if nm == "Event"}
    assert 1943 in events
