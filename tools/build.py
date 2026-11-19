"""build.py: build the patched ROM from the pinned dump.

    python -X utf8 tools/build.py [--out build/sakuranote_en.nds]

Steps: check the dump against rom.sha1, unpack FILEDATA.BIN, apply edits (none yet: the identity build),
repack FILEDATA and the NitroFS with ndspy, then undo ndspy's two non-exact habits (size word at 0x1000,
no 0xFF pad to the cartridge size). With no edits the output is byte-identical to the dump
(tests/test_identity.py)."""
import argparse
import hashlib
import sys
from pathlib import Path

import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_rom  # noqa: E402
import filedata  # noqa: E402
import romfs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "sakuranote_en.nds"


def edit_payloads(payloads):
    """Apply translation edits to FILEDATA entries in place. Phase 3: none (identity)."""
    return payloads


def fix_ndspy(orig, built):
    """ndspy writes a size word into the zero gap at 0x1000 and doesn't pad to the cartridge size."""
    out = bytearray(built)
    out[0x1000:0x1004] = orig[0x1000:0x1004]
    if len(out) > len(orig):
        sys.exit(f"built ROM {len(out):#x} bytes, larger than the cartridge {len(orig):#x}")
    out += b"\xff" * (len(orig) - len(out))
    return bytes(out)


def build(orig_bytes=None):
    """Return the built ROM bytes."""
    orig = orig_bytes if orig_bytes is not None else romfs.ROM.read_bytes()
    rom = ndspy.rom.NintendoDSRom(orig)
    fid = rom.filenames.idOf("FILEDATA.BIN")
    blob = bytes(rom.files[fid])
    payloads = edit_payloads(filedata.files(blob))
    rom.files[fid] = filedata.build(blob, payloads)
    return fix_ndspy(orig, rom.save())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    check_rom.check()
    data = build()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    same = data == romfs.ROM.read_bytes()
    print(f"{out} {len(data):#x} bytes sha1 {hashlib.sha1(data).hexdigest()}"
          f"{' (identical to the dump)' if same else ''}")


if __name__ == "__main__":
    sys.exit(main())
