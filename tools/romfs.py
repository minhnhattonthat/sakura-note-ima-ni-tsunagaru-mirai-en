"""romfs.py: list the NitroFS of the original ROM (header, overlays, every file with size and magic).

    python -X utf8 tools/romfs.py [--grep TEXT]
"""
import argparse
import sys
from pathlib import Path

import ndspy.rom

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"


def load():
    return ndspy.rom.NintendoDSRom.fromFile(str(ROM))


def files(rom):
    """Yield (fid, path, data) for every file in the filesystem."""
    def walk(folder, prefix):
        for i, name in enumerate(folder.files):
            fid = folder.firstID + i
            yield fid, prefix + name, rom.files[fid]
        for name, sub in folder.folders:
            yield from walk(sub, prefix + name + "/")
    yield from walk(rom.filenames, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grep", default="")
    a = ap.parse_args()
    rom = load()
    print(f"title {rom.name!r} code {rom.idCode!r} arm9 {len(rom.arm9):#x} arm7 {len(rom.arm7):#x}"
          f" arm9 entry {rom.arm9EntryAddress:#x} ram {rom.arm9RamAddress:#x}")
    print(f"overlays arm9: {len(rom.arm9OverlayTable)//32}  files: {len(rom.files)}")
    for fid, path, data in files(rom):
        if a.grep and a.grep not in path:
            continue
        print(f"{fid:5d} {len(data):9d} {data[:4]!r:12} {path}")


if __name__ == "__main__":
    sys.exit(main())
