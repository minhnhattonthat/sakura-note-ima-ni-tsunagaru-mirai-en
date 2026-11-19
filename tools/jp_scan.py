"""jp_scan.py: the skill's jp_left.py on the text of a built ROM only (message files and the arm9 string slots).

    python -X utf8 tools/jp_scan.py [BUILT.nds]     exit = jp_left's (0 = no Japanese left)

A whole-ROM scan reads code and graphics as kanji (hundreds of false runs), so this passes --range for every message
file 2495-2616 inside FILEDATA.BIN and for each arm9 string slot (script/arm9.json), all as ROM offsets of the
built image, bodies only (the 2 header words are speaker numbers). Japanese kept on purpose is left out of the
ranges and listed in work/jp_known.txt: every string of status `data` that has Japanese (2612 debug labels, 2614
message test, 2613:2/13 debug-menu lines; docs/status.md).
The arm9 full-name slot 0x0941C0 holds "Toru K." and is never shown (no pointer), so it is scanned like the rest.
Graphics text is not in this scan (docs/re/graphics.md, gfx/labels.tsv).
"""
import runpy
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import filedata  # noqa: E402
import msg  # noqa: E402
import script  # noqa: E402
from skill import SKILL  # noqa: E402

BUILT = ROOT / "build" / "sakuranote_en.nds"
ARM9_BASE = 0x02000000
KNOWN = ROOT / "work" / "jp_known.txt"


def fat_range(rom, fid):
    fat = struct.unpack_from("<I", rom, 0x48)[0]
    return struct.unpack_from("<II", rom, fat + 8 * fid)


def filedata_fid(rom_bytes):
    import ndspy.rom
    return ndspy.rom.NintendoDSRom(rom_bytes).filenames.idOf("FILEDATA.BIN")


def ranges(rom):
    """[(start, end)] ROM offsets of the text, and [(offset, note)] of the Japanese kept on purpose."""
    fd_start, fd_end = fat_range(rom, filedata_fid(rom))
    head = filedata.parse(rom[fd_start:fd_end])
    out, known = [], []
    for f in range(msg.FIRST, msg.LAST + 1):
        off, size = head["entries"][f]
        base = fd_start + off
        entries = script.load(f"msg_{f}.json")
        offs = [struct.unpack_from("<I", rom, base + 4 * i)[0] for i in range(len(entries))] + [size]
        for e, o, end in zip(entries, offs, offs[1:]):
            # the 2 header words are speaker / voice numbers, which the table would read as kana
            body = base + o + (4 if e.get("hdr") else 0)
            if e["status"] == "data" and any("぀" <= ch <= "鿿" for ch in e["jp"]):
                known.append((body, e["id"]))  # kept Japanese: not scanned (a label spans several runs)
            elif body < base + end:
                out.append((body, base + end))
    arm9_off = struct.unpack_from("<I", rom, 0x20)[0]
    for e in script.load("arm9.json"):
        a = int(e["id"].split(":")[1], 16)
        out.append((arm9_off + a, arm9_off + a + e["max"]))
    return out, known


def main(argv):
    built = Path(argv[0]) if argv else BUILT
    rom = built.read_bytes()
    rs, known = ranges(rom)
    KNOWN.parent.mkdir(parents=True, exist_ok=True)
    KNOWN.write_text("".join(f"{o:X} {i} (status data, kept, not scanned)\n" for o, i in known), encoding="utf-8")
    print(f"{len(rs)} text ranges scanned; {len(known)} status-data strings with Japanese kept on purpose "
          f"(listed in {KNOWN.relative_to(ROOT)})", flush=True)
    args = [str(built), "--tbl", str(ROOT / "tbl" / "jp.tbl"), "--min", "2", "--limit", "100"]
    for a, b in rs:
        args += ["--range", f"{a:X}-{b - 1:X}"]
    # in-process: ~5,400 ranges are too long for a Windows command line
    script_path = Path(SKILL) / "scripts" / "jp_left.py"
    sys.argv = [str(script_path)] + args
    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (1 if e.code else 0)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
