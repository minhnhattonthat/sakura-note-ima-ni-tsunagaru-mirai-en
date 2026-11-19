"""sjisscan.py: count Shift-JIS runs in every FILEDATA entry (LZ10/LZ11 entries decompressed) and in arm9/overlays.

    python -X utf8 tools/sjisscan.py [--min 3] [--show ID]
Prints one line per file with runs: id, kind, compressed?, run count, total chars, first sample.
"""
import argparse
import re
import sys
from pathlib import Path

import ndspy.lz10

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filedata  # noqa: E402
import romfs  # noqa: E402

SJIS = rb"(?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc])"


def unpack(p):
    """Return (data, 'lz10'|'lz11'|'') for a FILEDATA payload."""
    if len(p) > 4 and p[0] in (0x10, 0x11):
        try:
            if p[0] == 0x10:
                return ndspy.lz10.decompress(p), "lz10"
        except Exception as e:
            print(f"  lz10 failed: {e}", file=sys.stderr)
    return p, ""


def runs(d, minlen):
    return [m for m in re.finditer(SJIS + b"{%d,}" % minlen, d)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--show", type=int)
    a = ap.parse_args()
    rom = romfs.load()
    blob = bytes(rom.getFileByName("FILEDATA.BIN"))
    items = [(f"{i:04d}", p) for i, p in enumerate(filedata.files(blob))]
    items += [("arm9", bytes(rom.arm9))] + [(f"ov{i}", bytes(rom.files[o.fileID])) for i, o in rom.loadArm9Overlays().items()]
    for name, p in items:
        if a.show is not None and name != f"{a.show:04d}":
            continue
        d, comp = unpack(p)
        rs = runs(d, a.minlen if hasattr(a, "minlen") else a.min)
        if not rs:
            continue
        chars = sum(len(m.group()) // 2 for m in rs)
        if a.show is not None:
            for m in rs:
                print(f"{m.start():#07x} {m.group().decode('cp932', 'replace')}")
        else:
            print(f"{name} {filedata.kind(p):10} {comp:4} runs {len(rs):5d} chars {chars:6d} "
                  f"{rs[0].group().decode('cp932', 'replace')[:20]}")


if __name__ == "__main__":
    sys.exit(main())
