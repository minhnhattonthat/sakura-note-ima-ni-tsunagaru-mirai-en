"""build.py: build the patched ROM from the pinned dump.

    python -X utf8 tools/build.py [--out build/sakuranote_en.nds] [--marker | --identity]

Steps: check the dump against rom.sha1, unpack FILEDATA.BIN, apply edits, repack FILEDATA and the NitroFS with ndspy,
then undo ndspy's two non-exact habits (size word at 0x1000, no 0xFF pad to the cartridge size). The arm9 write
and overlay write logs go next to the output (`<out>.writes.txt`); `tools/romcheck.py` audits the build with them.

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
    import gfx
    import insert
    return gfx.apply(insert.payloads(payloads, marker_build=mode == "marker"))[0]


def edit_arm9(arm9, mode, log=None):
    """arm9.bin after the edits; every write into section 0 goes into log (tools/writelog.py)."""
    if mode == "identity":
        return arm9
    import insert
    import script
    import vwf
    import ndspy.code
    import namefield
    a9 = insert.patch_arm9_strings(arm9, script.load("arm9.json"), marker_build=mode == "marker", log=log)
    a9 = ndspy.code.MainCodeFile(vwf.patch_arm9(a9, log=log), vwf.ARM9_BASE)
    s0 = bytearray(a9.sections[0].data)
    namefield.patch(s0, log)  # name entry: 9 characters at a 12 px pitch (English default names)
    a9.sections[0].data = bytes(s0)
    return a9.save(compress=False)


def fix_ndspy(orig, built):
    """ndspy writes a size word into the zero gap at 0x1000 and doesn't pad to the cartridge size."""
    out = bytearray(built)
    out[0x1000:0x1004] = orig[0x1000:0x1004]
    if len(out) > len(orig):
        sys.exit(f"built ROM {len(out):#x} bytes, larger than the cartridge {len(orig):#x}")
    out += b"\xff" * (len(orig) - len(out))
    return bytes(out)


def edit_overlays(rom, mode, writes):
    """Ending overlay: credits line x re-centred for the English (tools/credits.py)."""
    if mode == "identity":
        return
    import credits
    import insert
    import script
    log = writes.setdefault("overlay1", []) if writes is not None else None
    ctx = insert.Ctx()

    def text_of(r):  # the same text message insertion writes for this entry (QA overrides, marker)
        text, table = insert.entry_text(r, mode == "marker", ctx)
        return None if table is ctx.jp else text
    rom.files[credits.OVERLAY] = credits.patch_overlay(bytes(rom.files[credits.OVERLAY]),
                                                       script.load(f"msg_{credits.MSG}.json"), log, text_of)


def build(orig_bytes=None, mode="identity", writes=None):
    """Return the built ROM bytes. writes: dict that receives the write logs per target ("arm9", "overlay1")
    for tools/romcheck.py."""
    assert mode in MODES, mode
    orig = orig_bytes if orig_bytes is not None else romfs.ROM.read_bytes()
    rom = ndspy.rom.NintendoDSRom(orig)
    fid = rom.filenames.idOf("FILEDATA.BIN")
    blob = bytes(rom.files[fid])
    payloads = edit_payloads(filedata.files(blob), mode)
    rom.files[fid] = filedata.build(blob, payloads)
    rom.arm9 = edit_arm9(bytes(rom.arm9), mode, writes.setdefault("arm9", []) if writes is not None else None)
    edit_overlays(rom, mode, writes)
    return fix_ndspy(orig, rom.save())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--marker", action="store_true")
    g.add_argument("--identity", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT",
                    help="override one entry's text (width tests), e.g. --qa \"2499:0=Wide{n}line\"")
    ap.add_argument("--qa-file", action="append", default=[], metavar="TSV",
                    help="--qa overrides from a file: one 'ID<TAB>TEXT' per line, # comments (tools/qa/*.tsv)")
    a = ap.parse_args()
    mode = "marker" if a.marker else "identity" if a.identity else "en"
    qa = [q.partition("=")[::2] for q in a.qa]
    for f in a.qa_file:
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                k, _, v = line.partition("\t")
                qa.append((k.strip(), v.strip()))
    if qa:
        import insert
        insert.QA.update(qa)
    check_rom.check()
    writes = {}
    data = build(mode=mode, writes=writes)
    out = Path(a.out or (OUT_MARKER if mode == "marker" else OUT))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    import writelog
    out.with_suffix(".writes.txt").write_text(writelog.dump(writes), encoding="utf-8", newline="\n")
    if mode == "en" and not qa and not a.out:
        import textcover_keys  # text coverage keys of this build (tools/debug/textlog.lua logs the same hash)
        textcover_keys.write(data, out.parent / "strings.tsv")
    same = data == romfs.ROM.read_bytes()
    print(f"{out} ({mode}) {len(data):#x} bytes sha1 {hashlib.sha1(data).hexdigest()}"
          f"{' (identical to the dump)' if same else ''}")


if __name__ == "__main__":
    sys.exit(main())
