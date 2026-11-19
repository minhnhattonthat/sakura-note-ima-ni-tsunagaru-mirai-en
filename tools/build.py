"""build.py: build the patched ROM from the pinned dump.

    python -X utf8 tools/build.py [--out build/sakuranote_en.nds] [--marker | --identity]

Steps: check the dump against rom.sha1, unpack FILEDATA.BIN, apply edits, repack FILEDATA and the NitroFS with ndspy,
then undo ndspy's two non-exact habits (size word at 0x1000, no 0xFF pad to the cartridge size).

Modes:
- default: English VWF font + hook (tools/vwf.py), script/ translations inserted (tools/insert.py); untranslated
  entries keep their Japanese bytes.
- --marker: as default, but every untranslated entry shows `[id]` + a digit ruler (the phase 5 marker build);
  default output build/sakuranote_marker.nds.
- --identity: no edits; the output is byte-identical to the dump (tests/test_identity.py).
"""
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
OUT_MARKER = ROOT / "build" / "sakuranote_marker.nds"
MODES = ("identity", "en", "marker")


def edit_payloads(payloads, mode):
    """FILEDATA entries after the edits for this mode."""
    if mode == "identity":
        return payloads
    import insert
    return insert.payloads(payloads, marker_build=mode == "marker")


def edit_arm9(arm9, mode):
    if mode == "identity":
        return arm9
    import insert
    import script
    import vwf
    a9 = insert.patch_arm9_strings(arm9, script.load("arm9.json"), marker_build=mode == "marker")
    return vwf.patch_arm9(a9)


def fix_ndspy(orig, built):
    """ndspy writes a size word into the zero gap at 0x1000 and doesn't pad to the cartridge size."""
    out = bytearray(built)
    out[0x1000:0x1004] = orig[0x1000:0x1004]
    if len(out) > len(orig):
        sys.exit(f"built ROM {len(out):#x} bytes, larger than the cartridge {len(orig):#x}")
    out += b"\xff" * (len(orig) - len(out))
    return bytes(out)


def build(orig_bytes=None, mode="identity"):
    """Return the built ROM bytes."""
    assert mode in MODES, mode
    orig = orig_bytes if orig_bytes is not None else romfs.ROM.read_bytes()
    rom = ndspy.rom.NintendoDSRom(orig)
    fid = rom.filenames.idOf("FILEDATA.BIN")
    blob = bytes(rom.files[fid])
    payloads = edit_payloads(filedata.files(blob), mode)
    rom.files[fid] = filedata.build(blob, payloads)
    rom.arm9 = edit_arm9(bytes(rom.arm9), mode)
    return fix_ndspy(orig, rom.save())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--marker", action="store_true")
    g.add_argument("--identity", action="store_true")
    a = ap.parse_args()
    mode = "marker" if a.marker else "identity" if a.identity else "en"
    check_rom.check()
    data = build(mode=mode)
    out = Path(a.out or (OUT_MARKER if mode == "marker" else OUT))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    same = data == romfs.ROM.read_bytes()
    print(f"{out} ({mode}) {len(data):#x} bytes sha1 {hashlib.sha1(data).hexdigest()}"
          f"{' (identical to the dump)' if same else ''}")


if __name__ == "__main__":
    sys.exit(main())
