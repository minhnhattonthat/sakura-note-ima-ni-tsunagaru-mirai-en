"""The supported dump is in place and matches rom.sha1."""
import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
def test_rom_sha1():
    want = [l.split()[0] for l in (ROOT / "rom.sha1").read_text().splitlines() if l and not l.startswith("#")][0]
    assert hashlib.sha1(ROM.read_bytes()).hexdigest() == want
