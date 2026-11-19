"""msg.py: message files (FILEDATA 2495-2616): u32 offset table (first offset / 4 = count), then u16 strings.

Each string ends in 0xFFFD. Codes 0x000-0x662 are font cells (tbl/jp.tbl); 0xFF00-0xFFFF are control codes
(docs/re/text.md). Verified: every string of all 122 files parses and ends in FFFD.

    python -X utf8 tools/msg.py dump [--file N] [--grep CODEHEX]   # decoded text
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filedata  # noqa: E402
import romfs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIRST, LAST = 2495, 2616


def parse(d):
    """Return list of u16 tuples, or None if d isn't a message file."""
    if len(d) < 8:
        return None
    first = struct.unpack_from("<I", d, 0)[0]
    if first % 4 or first < 4 or first > len(d):
        return None
    n = first // 4
    offs = [struct.unpack_from("<I", d, 4 * i)[0] for i in range(n)]
    if any(b < a for a, b in zip(offs, offs[1:])) or offs[-1] > len(d):
        return None
    out = []
    for a, b in zip(offs, offs[1:] + [len(d)]):
        if (b - a) % 2:
            return None
        out.append(struct.unpack_from("<%dH" % ((b - a) // 2), d, a))
    if not all(w and w[-1] == 0xFFFD for w in out):
        return None
    return out


def load_tbl(path=ROOT / "tbl" / "jp.tbl"):
    from tbl import Table
    return Table.load(path)


def decode(words, tbl):
    """Decode u16 words with a tbl.Table (keys are little-endian bytes: code 0x0010 = key 1000)."""
    b = struct.pack("<%dH" % len(words), *words)
    return tbl.decode(b, 0, len(b))[0]


def all_files():
    rom = romfs.load()
    fs = filedata.files(bytes(rom.getFileByName("FILEDATA.BIN")))
    return {i: parse(fs[i]) for i in range(FIRST, LAST + 1)}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("dump")
    s.add_argument("--file", type=int)
    s.add_argument("--grep", type=lambda x: int(x, 16))
    s.add_argument("--tbl", default=str(ROOT / "tbl" / "jp.tbl"))
    a = ap.parse_args()
    tbl = load_tbl(a.tbl)
    for fid, ms in all_files().items():
        if a.file is not None and fid != a.file:
            continue
        for k, w in enumerate(ms):
            if a.grep is not None and a.grep not in w:
                continue
            print(f"{fid}:{k}\t" + decode(w, tbl))


if __name__ == "__main__":
    sys.exit(main())
