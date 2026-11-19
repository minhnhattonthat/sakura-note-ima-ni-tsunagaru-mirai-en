"""textcover_keys.py: build/strings.tsv for text coverage, one "id<TAB>key" per string of a built ROM.

    python -X utf8 tools/textcover_keys.py [BUILT.nds] [--out build/strings.tsv]

The message files sit raw in heap RAM, so a string has no fixed address; tools/debug/textlog.lua logs a hash of
the codes the text engine expands instead (r1 at 0x0203764C = the string body after its 2 header words, up to
FFFD). key() is the same hash. Empty bodies are left out (nothing to show). Strings with the same codes share a
key: showing one counts for all (they render the same text). The coverage report:
    python -X utf8 $SKILL/scripts/textcover.py work/qa/cover build/strings.tsv --waive docs/text_unshown.tsv
"""
import argparse
import struct
import sys
from pathlib import Path

import ndspy.code
import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filedata  # noqa: E402
import msg  # noqa: E402
import script  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MOD = 2147483629
ARM9_BASE = 0x02000000


def key(codes):
    """Same as textlog.lua: h = 7; h = (h * 31 + c) mod MOD over the codes before FFFD."""
    h = 7
    for c in codes:
        h = (h * 31 + c) % MOD
    return h


def rows(rom_bytes):
    """[(id, key)] for every non-empty message body and arm9 string slot of the built ROM."""
    rom = ndspy.rom.NintendoDSRom(rom_bytes)
    files = filedata.files(bytes(rom.getFileByName("FILEDATA.BIN")))
    out = []
    for fid in range(msg.FIRST, msg.LAST + 1):
        for i, words in enumerate(msg.parse(files[fid]) or []):
            body = script.split_msg(list(words))[1]
            if body:
                out.append((f"{fid}:{i}", key(body)))
    s0 = ndspy.code.MainCodeFile(rom.arm9, ARM9_BASE).sections[0].data
    for off, size, _ in script.ARM9_SLOTS:
        words = struct.unpack_from(f"<{size // 2}H", s0, off)
        body = list(words[:words.index(0xFFFD)]) if 0xFFFD in words else list(words)
        if body:
            out.append((f"arm9:{off:06X}", key(body)))
    return out


def write(rom_bytes, out):
    r = rows(rom_bytes)
    Path(out).write_text("".join(f"{i}\t{k:08X}\n" for i, k in r), encoding="utf-8", newline="\n")
    return len(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "sakuranote_en.nds"))
    ap.add_argument("--out", default=str(ROOT / "build" / "strings.tsv"))
    a = ap.parse_args()
    print(f"{a.out}: {write(Path(a.rom).read_bytes(), a.out)} strings")


if __name__ == "__main__":
    main()
