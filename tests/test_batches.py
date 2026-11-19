"""Translation tooling: batches.py rules (selftest) and every shipped English line passing the batch check."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def test_selftest():
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/batches.py"), "--selftest"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


def test_widths():
    dlg = {"id": "2500:0", "hdr": "000D 0010", "jp": "x"}
    assert batches.width_problems(dlg, "a" * 36) == []                   # 216 px: fits a page's last line
    assert batches.width_problems(dlg, "a" * 38)                         # 228 px alone = last line > 218
    assert batches.width_problems(dlg, "a" * 38 + "{n}" + "a" * 36) == []  # line 1 228, line 2 216
    assert batches.width_problems(dlg, "a" * 36 + "{n}" + "a" * 37)      # line 2 222 > 218
    assert batches.width_problems(dlg, "a{n}b{n}c")                       # 3 lines on one page
    assert batches.width_problems(dlg, "a{n}b{page}c") == []


def test_tag_chars():
    tag = {"id": "2610:7", "hdr": "FF05 00FF", "jp": "ナナミ"}
    assert batches.width_problems(tag, "Nanami") == []
    assert batches.width_problems(tag, "Dr. Joshu (old)")


def test_honorific_after_katakana_only():
    e = {"id": "2500:1", "hdr": "000D 0010", "jp": "ナナミちゃんとおじさん"}
    assert any("-chan" in p for p in batches.problems(e, "Nanami and the man", []))
    assert not any("-san" in p for p in batches.problems(e, "Nanami-chan and the man", []))


def test_shipped_english_passes():
    entries, terms = batches.index(), batches.glossary()
    bad = [(i, p) for i, e in entries.items() if e.get("en") for p in batches.problems(e, e["en"], terms)]
    assert not bad, bad[:20]
