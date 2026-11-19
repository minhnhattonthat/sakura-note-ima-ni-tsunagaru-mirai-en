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


def test_chapter_card_layout():
    card = {"id": "2613:25", "hdr": "FFFF", "jp": "第一章{n}　　　　　　{n}{num_F6}"}  # full-width-space line = blank
    assert batches.width_problems(card, "Chapter 1{n}{n}{num_F6}") == []
    assert batches.width_problems(card, "Chapter 1{n}x{n}{num_F6}")            # blank line filled
    end = {"id": "2613:57", "hdr": "FFFF", "jp": "第一章{sp}スペシャル{n}{n}{num_F6}{n}END"}  # 4-line JP card
    assert batches.width_problems(end, "Chapter 1: Special{n}{n}{num_F6}{n}END") == []
    assert batches.width_problems(end, "Chapter 1: Special{n}{num_F6}{n}{n}END")  # blank moved


def test_honorific_after_katakana_only():
    e = {"id": "2500:1", "hdr": "000D 0010", "jp": "ナナミちゃんがおじさんと{n}ちゃんと話す"}  # ちゃんと = properly
    assert any("-chan" in p for p in batches.problems(e, "Nanami and the man", []))
    assert not any("-san" in p for p in batches.problems(e, "Nanami-chan and the man", []))


def test_label_blanks_kept():
    menu = {"id": "2608:3", "hdr": "FFFF FFFF", "jp": "　アイテム"}  # leading full-width space = cursor room
    assert batches.layout_problems(menu, " Items") == []
    assert batches.layout_problems(menu, "Items")
    assert batches.layout_problems({**menu, "jp": "アイテム"}, "Items ")
    dlg = {"id": "2500:0", "hdr": "000D 0010", "jp": "　あいうえお"}  # dialogue indent: typography, not checked
    assert batches.layout_problems(dlg, "Hello") == []


def test_stub_last_line():
    dlg = {"id": "2500:0", "hdr": "000D 0010", "jp": "x"}
    assert batches.layout_problems(dlg, "This line runs on long enough to need{n}help.")
    assert batches.layout_problems(dlg, "This line runs on long enough{n}to need help.") == []
    assert batches.layout_problems(dlg, "Let's go home now, shall we,{n}{var_ED}{slot}{slot}.") == []  # name = 5


def test_shipped_english_passes():
    entries, terms = batches.index(), batches.glossary()
    bad = [(i, p) for i, e in entries.items() if e.get("en") for p in batches.problems(e, e["en"], terms)]
    assert not bad, bad[:20]
