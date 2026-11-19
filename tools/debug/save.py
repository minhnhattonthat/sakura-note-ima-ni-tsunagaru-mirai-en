"""save.py: read and edit Sakura Note EEPROM saves (.dsv / raw .sav), fixing both copies and the checksum.

    python -X utf8 tools/debug/save.py show SAVE [--slot 1]
    python -X utf8 tools/debug/save.py edit SAVE OUT [--slot 1] [--chapters 0xF] [--name boy_surname=ナマエ ...]
                                       [--set 0x40=7 --set 0x48:1=2 ...]

Layout (docs/re/save.md, verified on game-written saves from tools/debug/make_save.py):
- 32 KiB EEPROM. 0x00-0x20 header "SAKURA NOTE1J." + version byte.
- Slot n (0-2) is stored twice: image k (0, 1) at 0x20 + (2n + k) * 0xA00, 0xA00 bytes each.
- image u16 at 0x9FE = ~(byte sum of image[0:0x9A0]) & 0xFFFF (arm9 0x0207E468, called from the save builder
  0x020817E8 and the loader 0x020824B8). The builder copies the game state struct verbatim into image[0:0x9A0],
  then puts the slot index at image+8.
- Fields: see FIELDS and NAMES below; `--set OFF[:SIZE]=VALUE` writes any other little-endian field (SIZE 1/2/4).
Edits start from a game-written file (never zeros); a DeSmuME footer after 0x8000 is kept as is.
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

EEPROM = 0x8000
HEADER = b"SAKURA NOTE1J."
IMG0, IMGSZ, SUMLEN, SUMOFF = 0x20, 0xA00, 0x9A0, 0x9FE
# name: (offset, size) of u16 strings ended by 0xFFFD; codes are dialogue-font cells (tbl/jp.tbl)
NAMES = {"boy_surname": (0x2A4, 0x14), "boy_name": (0x2B8, 0x14), "dog": (0x2CC, 0x14), "cat": (0x2E0, 0x14)}
# [lo, hi) of the item-ownership bytes (だいじなもの grid): 0xFF in all of them shows a full grid. Found by poking
# the live state struct in 16-byte chunks (tools/debug/poke.lua); bit order per item not mapped yet.
ITEM_BITS = (0x120, 0x130)
# name: (offset, size). Date = when the slot was saved (shown on the file select).
FIELDS = {
    "used": (0x00, 4), "slot": (0x08, 4),
    "year": (0x0C, 4), "month": (0x10, 4), "day": (0x14, 4), "weekday": (0x18, 4),
    "hour": (0x1C, 4), "minute": (0x20, 4), "second": (0x24, 4),
    # per-chapter word, 0x20 in a debug-warped chapter; meaning beyond that unknown (docs/re/save.md)
    "ch1_state": (0x15C, 4), "ch2_state": (0x160, 4), "ch3_state": (0x164, 4), "ch4_state": (0x168, 4),
    "chapters": (0x16C, 4),  # bitmask of chapter tabs on the episode board (bit 0 = chapter 1); verified
}
FMT = {1: "<B", 2: "<H", 4: "<I"}


def checksum(img):
    return ~sum(img[:SUMLEN]) & 0xFFFF


class Save:
    def __init__(self, data):
        self.data = bytearray(data)
        if len(self.data) < EEPROM:
            raise ValueError(f"save is {len(self.data):#x} bytes, want at least {EEPROM:#x}")
        if bytes(self.data[:len(HEADER)]) != HEADER:
            raise ValueError("no SAKURA NOTE header: not a save the game has initialised")

    @classmethod
    def read(cls, path):
        return cls(Path(path).read_bytes())

    def write(self, path):
        Path(path).write_bytes(bytes(self.data))

    @staticmethod
    def off(slot, copy):
        return IMG0 + (2 * slot + copy) * IMGSZ

    def image(self, slot, copy=0):
        o = self.off(slot, copy)
        return self.data[o:o + IMGSZ]

    def slot_valid(self, slot, copy=0):
        img = self.image(slot, copy)
        return struct.unpack_from("<H", img, SUMOFF)[0] == checksum(img) and img[0] == 1

    def get(self, slot, off, size):
        return struct.unpack_from(FMT[size], self.image(slot), off)[0]

    def put(self, slot, off, size, value):
        """Write to both copies of the slot and refresh both checksums."""
        for copy in (0, 1):
            o = self.off(slot, copy)
            struct.pack_into(FMT[size], self.data, o + off, value)
        self.fix(slot)

    def fix(self, slot):
        for copy in (0, 1):
            o = self.off(slot, copy)
            struct.pack_into("<H", self.data, o + SUMOFF, checksum(self.data[o:o + IMGSZ]))

    def name(self, slot, key, tbl):
        off, size = NAMES[key]
        img = self.image(slot)
        out = bytearray()
        for i in range(0, size, 2):
            c = struct.unpack_from("<H", img, off + i)[0]
            if c == 0xFFFD:
                break
            out += struct.pack("<H", c)
        return tbl.decode(out, 0, len(out))[0]

    def set_name(self, slot, key, text, tbl):
        off, size = NAMES[key]
        raw = tbl.encode(text) + b"\xfd\xff"
        if len(raw) % 2 or len(raw) > size:
            raise ValueError(f"{key}: {text!r} needs {len(raw)} bytes, field holds {size} (incl. terminator)")
        raw += bytes(size - len(raw))
        for copy in (0, 1):
            o = self.off(slot, copy) + off
            self.data[o:o + size] = raw
        self.fix(slot)


def show(sv, slot, tbl):
    print(f"slot {slot + 1}: copy0 {'ok' if sv.slot_valid(slot, 0) else 'BAD'}, "
          f"copy1 {'ok' if sv.slot_valid(slot, 1) else 'BAD'}")
    for k, (o, n) in FIELDS.items():
        print(f"  {k:8} @{o:#05x} = {sv.get(slot, o, n)}")
    for k in NAMES:
        print(f"  {k:12} = {sv.name(slot, k, tbl)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show")
    s.add_argument("save")
    s.add_argument("--slot", type=int, default=1)
    e = sub.add_parser("edit")
    e.add_argument("save")
    e.add_argument("out")
    e.add_argument("--slot", type=int, default=1)
    e.add_argument("--chapters", type=lambda x: int(x, 0), help="tab bitmask, e.g. 0xF = chapters 1-4")
    e.add_argument("--name", action="append", default=[], help="key=text, key in " + ",".join(NAMES))
    e.add_argument("--set", action="append", default=[], help="OFF[:SIZE]=VALUE (hex or decimal)")
    a = ap.parse_args()
    tbl = Table.load(ROOT / "tbl" / "jp.tbl")
    sv = Save.read(a.save)
    slot = a.slot - 1
    if a.cmd == "show":
        show(sv, slot, tbl)
        return
    if not sv.slot_valid(slot):
        sys.exit(f"slot {a.slot} of {a.save} is empty or corrupt: start from a game-written save")
    if a.chapters is not None:
        sv.put(slot, *FIELDS["chapters"], a.chapters)
    for item in a.name:
        k, _, v = item.partition("=")
        sv.set_name(slot, k, v, tbl)
    for item in a.set:
        k, _, v = item.partition("=")
        off, _, size = k.partition(":")
        sv.put(slot, int(off, 0), int(size or 4), int(v, 0))
    sv.write(a.out)
    show(sv, slot, tbl)


if __name__ == "__main__":
    main()
