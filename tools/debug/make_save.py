"""make_save.py: build the save fixtures in work/saves/ from a cold boot (no playthrough, no user save).

    python -X utf8 tools/debug/make_save.py [NAME ...] [--rom ROM] [--force]     (no NAME = all fixtures)

Fixtures (FIXTURES below):
  s1_living     game-written base: debug warp to scenario 1's living room (map list page 1 row 1, FILEDATA 1232),
                mash A 1000 frames (arrival dialogue), walk left 50 / down 80 frames to the SAVE sign, face right,
                A through the save screen into slot 1. The game writes both copies and the checksum itself;
                then the names are set to the English defaults (en_names), as an English new game has them.
  all_chapters  s1_living edited by tools/debug/save.py: chapters 1-4 unlocked on the episode board (0x16C = 0xF).
Each fixture is checked: slot 1 valid (checksum, used flag). Scenes in tools/debug/scenes.tsv name the fixture in
their `save` column; tools/debug/warp_all.py calls fixture() so a fresh clone gets them on first run.
The walk is tuned to scenario 1's spawn point only (scenario 2/3 living rooms spawn elsewhere): edit saves instead.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
import save  # noqa: E402

ORIG = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"
SAVES = ROOT / "work" / "saves"
STATES = ROOT / "work" / "states"
WARP = "f2612 w30 a w120 a w100 a w100 down a w600"  # debug menu -> シーン -> boy -> scenario 1 -> row 1 (living)
WALK = "10 -;50 left;80 down;6 -;8 right;6 a;150 -;6 a;150 -;6 a;150 -;6 a;400 -;6 a;300 -;6 a;300 -"


def blank_save():
    """32 KiB of 0xFF = a never-used EEPROM; the game initialises it to its empty save (three free slots)."""
    p = SAVES / "blank.sav"
    if not p.exists() or p.read_bytes() != b"\xff" * 0x8000:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\xff" * 0x8000)
    return p


def emu(rom, out, *args):
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           *map(str, args)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(f"emu.py failed ({p.returncode}): {p.stdout[-500:]}{p.stderr[-500:]}")


def make_s1_living(rom, out):
    qa = ROOT / "work" / "qa" / "make_save"
    emu(rom, qa / "1", "--script", ROOT / "tools/debug/warp.lua", "--var", f"SCENE='debug:{WARP}'",
        "--var", "STOP_AFTER=10", "--sav", blank_save(), "--frames", 4000, "--state-out", STATES / "living_s1.dst")
    emu(rom, qa / "2", "--state-in", STATES / "living_s1.dst", "--mash", 30, "--frames", 1000,
        "--state-out", STATES / "living_s1_free.dst")
    emu(rom, qa / "3", "--state-in", STATES / "living_s1_free.dst", "--sav", blank_save(), "--route-str", WALK,
        "--frames", 2200, "--shot-every", 100, "--sheet")
    shutil.copy(next((qa / "3").glob("*.dsv")), out)
    en_names(out)


def en_names(path):
    """Set the English default names (script/arm9.json) in slot 1. The debug warp skips name entry and leaves
    the kana names of its own script, which an English player never sees. Each field keeps its character: the
    field at 0x2CC held トロイメライ, the one at 0x2E0 ラインホルト."""
    import script
    from tbl import Table
    en = {r["id"]: r.get("en") for r in script.load("arm9.json")}
    sv = save.Save.read(path)
    tbl = Table.load(ROOT / "tbl" / "jp.tbl")
    for key, slot in (("boy_surname", "arm9:0941D4"), ("boy_name", "arm9:0941E8"), ("dog", "arm9:0941FC"),
                      ("cat", "arm9:094210")):
        sv.set_name(0, key, en[slot], tbl)
    sv.write(path)


def make_all_chapters(rom, out):
    sv = save.Save.read(fixture("s1_living", rom))
    sv.put(0, *save.FIELDS["chapters"], 0xF)
    sv.write(out)


def make_all_items(rom, out):
    """s1_living with every item-ownership bit set (state +0x120..+0x12F, found by poking RAM: docs/re/save.md)."""
    sv = save.Save.read(fixture("s1_living", rom))
    for off in range(*save.ITEM_BITS):
        sv.put(0, off, 1, 0xFF)
    sv.write(out)


FIXTURES = {"s1_living": make_s1_living, "all_chapters": make_all_chapters, "all_items": make_all_items}


def fixture(name, rom=ORIG, force=False):
    """Path of work/saves/<name>.dsv, built first if missing (or force). Raises if slot 1 isn't valid."""
    out = SAVES / f"{name}.dsv"
    if force or not out.exists():
        SAVES.mkdir(parents=True, exist_ok=True)
        FIXTURES[name](rom, out)
    if not save.Save.read(out).slot_valid(0):
        raise RuntimeError(f"{out}: slot 1 not valid")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="any of " + ", ".join(FIXTURES))
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    bad = set(a.names) - set(FIXTURES)
    if bad:
        ap.error(f"unknown fixtures {sorted(bad)}")
    for n in a.names or FIXTURES:
        print(fixture(n, a.rom, a.force), "slot 1 valid")


if __name__ == "__main__":
    main()
