"""filedata.py: the FILEDATA.BIN archive ("LF 2") that holds almost every game asset.

Layout (verified: parse covers the archive to its last byte, every entry is contiguous, see docs/re/filesystem.md):
  0x00 "LF 2"   0x04 u32 first-data offset / 4   0x08 u32 count   0x0C u32 table offset (0x10)
  0x10 count x {u32 offset / 4, u32 size}; files are stored raw, 4-byte aligned, back to back.

    python -X utf8 tools/filedata.py [--out DIR]   # list (and optionally extract) every entry
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import romfs  # noqa: E402

MAGIC = b"LF 2"


def parse(blob):
    """Return the list of entry payloads (bytes) and the header fields."""
    assert blob[:4] == MAGIC, blob[:4]
    first, count, table = struct.unpack_from("<III", blob, 4)
    entries = []
    for i in range(count):
        off4, size = struct.unpack_from("<II", blob, table + 8 * i)
        entries.append((off4 * 4, size))
    return {"first": first, "count": count, "table": table, "entries": entries}


def files(blob):
    h = parse(blob)
    return [blob[o:o + s] for o, s in h["entries"]]


def build(blob, payloads):
    """Rebuild the archive: same header, entries packed back to back, 4-byte aligned (pad 0x00)."""
    h = parse(blob)
    out = bytearray(blob[:h["first"] * 4])
    for i, p in enumerate(payloads):
        while len(out) % 4:
            out.append(0)
        struct.pack_into("<II", out, h["table"] + 8 * i, len(out) // 4, len(p))
        out += p
    return bytes(out)


def kind(p):
    m = p[:4]
    if len(p) >= 4 and all(32 <= c < 127 for c in m):
        return m.decode()
    return "?" + m.hex()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    rom = romfs.load()
    blob = bytes(rom.getFileByName("FILEDATA.BIN"))
    for i, p in enumerate(files(blob)):
        print(f"{i:5d} {len(p):8d} {kind(p)}")
        if a.out:
            Path(a.out).mkdir(parents=True, exist_ok=True)
            (Path(a.out) / f"{i:04d}.bin").write_bytes(p)


if __name__ == "__main__":
    sys.exit(main())
