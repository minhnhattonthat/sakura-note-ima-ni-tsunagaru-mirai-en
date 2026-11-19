"""romcheck.py: audit a built ROM against the dump, leaf by leaf (phase 7 checks, docs/re/checks.md).

    python -X utf8 tools/romcheck.py [BUILT]        default build/sakuranote_en.nds + its .writes.txt

A raw byte diff is useless here (arm9 grows, so NitroFS shifts every file), so the check compares what the build
may change, piece by piece, and fails on anything else:
- header: only the offset/size fields ndspy relays out and the header CRC (which must be valid) differ;
- arm7, both overlay tables, overlay 0, the banner, the file names and every other NitroFS file: identical;
- overlay 1 (ending): only the logged credits-x writes, each exactly one instruction at a credits call's
  `mov r2, #x` (tools/credits.py), replaced by `mov r2, #x` with x the centred x of the script English; every
  entry whose x must move has its write;
- arm9: the same autoload sections plus one new block at vwf.HOOK equal to vwf.hook_block(); every logged
  section-0 write lies inside one interval of arm9_allowed() (string slots, hook sites, arena literal, fixed
  independently of the log); section 0 passes romdiff.check with the build's write log (original bytes as logged, no overlap, nothing overwritten, no changed
  byte without a write) apart from the module-params words ndspy rewrites; no branch in section 0 lands strictly
  inside a hook span;
- FILEDATA: same entry count, only the two fonts and the message files differ; font bytes change only inside the
  cells of the English codes;
- message files: same string count and header words; no Japanese string is left without English unless it is
  status `data` (never shown, reason in its notes); an untranslated (or `data`) string keeps its original
  bytes; a translated one decodes back to exactly its script/ English, keeps the JP's control codes (layout codes
  {n} {page} {sp} aside) and passes the width/line lint (batches.width_problems);
- arm9 string slots decode back to their English.
Exit 1 with one line per problem; else prints the counts.
"""
import struct
import sys
from collections import Counter
from pathlib import Path

import ndspy.code
import ndspy.rom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import credits  # noqa: E402
import filedata  # noqa: E402
import insert  # noqa: E402
import msg  # noqa: E402
import romdiff  # noqa: E402
import romfs  # noqa: E402
import script  # noqa: E402
import vwf  # noqa: E402
import writelog  # noqa: E402

BUILT = ROOT / "build" / "sakuranote_en.nds"
# header words ndspy recomputes when it lays the ROM out again (arm9 grows): offsets and sizes, then the CRC
HEADER_FIELDS = {0x2C: "arm9 size", 0x30: "arm7 offset", 0x40: "FNT offset", 0x44: "FNT size", 0x48: "FAT offset",
                 0x4C: "FAT size", 0x50: "arm9 overlay table offset", 0x58: "arm7 overlay table offset",
                 0x68: "banner offset", 0x80: "used ROM size"}
HEADER_CRC = 0x15E
FREE = batches.FREE


def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def check_header(o, n, errs):
    allowed = set()
    for off in HEADER_FIELDS:
        allowed.update(range(off, off + 4))
    allowed.update((HEADER_CRC, HEADER_CRC + 1))
    for i in range(0x200):
        if o[i] != n[i] and i not in allowed:
            errs.append(f"header 0x{i:03X}: {o[i]:02X} -> {n[i]:02X} (not a relaid offset/size field)")
    if struct.unpack_from("<H", n, HEADER_CRC)[0] != crc16(n[:HEADER_CRC]):
        errs.append("header CRC16 is wrong")


def check_containers(ro, rn, errs):
    for attr in ("arm7", "arm9OverlayTable", "arm7OverlayTable", "iconBanner", "arm9RamAddress", "arm9EntryAddress",
                 "arm7RamAddress", "arm7EntryAddress", "name", "idCode"):
        if getattr(ro, attr) != getattr(rn, attr):
            errs.append(f"{attr} differs")
    if str(ro.filenames) != str(rn.filenames):
        errs.append("file name table differs")
    fid = ro.filenames.idOf("FILEDATA.BIN")
    ov = {o.fileID for o in ro.loadArm9Overlays().values()} if hasattr(ro, "loadArm9Overlays") else set()
    if len(ro.files) != len(rn.files):
        errs.append(f"NitroFS file count {len(ro.files)} -> {len(rn.files)}")
    for i, (a, b) in enumerate(zip(ro.files, rn.files)):
        if i not in (fid, credits.OVERLAY) and a != b:
            errs.append(f"NitroFS file {i}{' (overlay)' if i in ov else ''} differs")
    return fid


def module_params(a9):
    """Offsets of the 3 autoload words ndspy rewrites (list start, list end, autoload start) in arm9.bin."""
    i = a9.find(bytes.fromhex("2106c0dedec00621"))
    assert i > 0, "nitrocode magic not found"
    base = i - 0x1C
    return range(base, base + 12)


def branch_targets(code, base):
    """(site, target) for ARM B/BL/BLX and Thumb BL/BLX pairs in code loaded at base."""
    out = []
    for p in range(0, len(code) - 3, 4):
        w = struct.unpack_from("<I", code, p)[0]
        if (w >> 25) & 7 == 5:
            imm = w & 0xFFFFFF
            imm -= (imm & 0x800000) << 1
            t = base + p + 8 + (imm << 2) + ((w >> 23) & 2 if w >> 28 == 0xF else 0)
            out.append((base + p, t))
    for p in range(0, len(code) - 3, 2):
        hi, lo = struct.unpack_from("<HH", code, p)
        if hi >> 11 == 0b11110 and lo >> 11 in (0b11111, 0b11101):
            off = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
            off -= (off & 0x400000) << 1
            out.append((base + p, base + p + 4 + off))
    return out


def arm9_allowed():
    """Section-0 intervals (arm9.bin offsets, [lo, hi)) a build may write, fixed independently of the write log:
    the string slots, the two 8-byte hook sites (ldr pc + literal) and the arena-lo literal."""
    out = [(off, off + slot, f"string slot arm9:{off:06X}") for off, slot, _ in script.ARM9_SLOTS]
    out += [(vwf.ADV_FUNC - vwf.ARM9_BASE, vwf.ADV_FUNC - vwf.ARM9_BASE + 8, "advance hook site"),
            (vwf.TAG_LOOP - vwf.ARM9_BASE, vwf.TAG_LOOP - vwf.ARM9_BASE + 8, "tag hook site"),
            (vwf.ARENA_LIT - vwf.ARM9_BASE, vwf.ARENA_LIT - vwf.ARM9_BASE + 4, "arena lo literal")]
    return out


def check_arm9_regions(writes, errs):
    """Every logged write lies entirely inside one allowed interval."""
    allowed = arm9_allowed()
    for off, old, new, by in writes:
        end = off + max(len(old), len(new))
        if len(old) != len(new) or not any(lo <= off and end <= hi for lo, hi, _ in allowed):
            errs.append(f"arm9 write {off:#x}-{end:#x} ({by}) is not inside a string slot or hook site")


def check_arm9(o9, n9, writes, errs):
    check_arm9_regions(writes, errs)
    a, b =ndspy.code.MainCodeFile(o9, vwf.ARM9_BASE), ndspy.code.MainCodeFile(n9, vwf.ARM9_BASE)
    sa, sb = a.sections, b.sections
    old = [(s.ramAddress, s.data, s.bssSize) for s in sa[1:]]
    new = [(s.ramAddress, s.data, s.bssSize) for s in sb[1:] if s.ramAddress != vwf.HOOK]
    if old != new:
        errs.append("arm9 autoload sections other than the hook block differ")
    hook = [s for s in sb if s.ramAddress == vwf.HOOK]
    if len(hook) != 1 or hook[0].data != vwf.hook_block()[0]:
        errs.append("arm9 hook block missing or not vwf.hook_block()")
    s0o, s0n = sa[0].data, sb[0].data
    if len(s0o) != len(s0n):
        errs.append(f"arm9 section 0 size {len(s0o):#x} -> {len(s0n):#x}")
    e, ok = romdiff.check(s0o, s0n, [module_params(o9)], writes)
    errs += [f"arm9 section 0 {x}" for x in e]
    spans = [(vwf.ARM9_BASE + off, vwf.ARM9_BASE + off + len(new)) for off, _, new, by in writes if "hook" in by]
    for site, t in branch_targets(s0o, vwf.ARM9_BASE):
        for lo, hi in spans:
            if lo < t < hi and not lo <= site < hi:
                errs.append(f"branch at {site:#010x} lands inside hook span {lo:#010x}-{hi:#010x}")
    return ok


def font_cells(fid):
    """Byte offsets a font patch may change: the tiles of the English cells."""
    out = set()
    if fid == vwf.BIG_FONT:
        for code in vwf.code_map().values():
            r, c = divmod(code, 16)
            for dy in (0, 1):
                for dx in (0, 1):
                    t = (2 * r + dy) * 32 + 2 * c + dx
                    out.update(range(vwf.FONT_HDR + 32 * t, vwf.FONT_HDR + 32 * t + 32))
    else:
        for code in vwf.small_codes().values():
            out.update(range(vwf.FONT_HDR + 32 * code, vwf.FONT_HDR + 32 * code + 32))
    return out


def decode_tag(words, ctx):
    codes = [b for b in struct.pack(f"<{len(words)}H", *words) if b != 0xFF]
    b = struct.pack(f"<{len(codes)}H", *codes)
    return ctx.tag.decode(b, 0, len(b))[0]


def tokens(text):
    return Counter(t for t in batches.TOKEN.findall(text) if t not in FREE)


def check_message(fid, o, n, ctx, errs):
    po, pn = msg.parse(o), msg.parse(n)
    if pn is None:
        errs.append(f"msg {fid}: built file does not parse")
        return 0
    rows = script.load(f"msg_{fid}.json")
    if not (len(po) == len(pn) == len(rows)):
        errs.append(f"msg {fid}: {len(po)} strings in the dump, {len(pn)} built, {len(rows)} in script/")
        return 0
    done = 0
    for r, wo, wn in zip(rows, po, pn):
        eid = r["id"]
        if wo[:2] != wn[:2]:
            errs.append(f"{eid}: header words {script.hdr_str(wo[:2])} -> {script.hdr_str(wn[:2])}")
        en = r.get(insert.LANG)
        tag = fid == insert.TAG_FILE and int(eid.split(":")[1]) >= insert.TAG_FIRST
        if r.get("status") == "data" or not en:
            if r.get("status") != "data" and script.JP.search(batches.TOKEN.sub("", r["jp"])):
                errs.append(f"{eid}: Japanese with no English (translate it, or mark it status data with a reason)")
            if wo != wn:
                errs.append(f"{eid}: untranslated string changed")
            continue
        body = wn[2:-1]
        if tag:
            text = decode_tag(body, ctx)
        else:  # tags 0-4 (name placeholders, never drawn from the file) stay unpacked, in tag codes
            b = script.pack(body)
            text = (ctx.tag if fid == insert.TAG_FILE else ctx.en).decode(b, 0, len(b))[0]
        if text != en:
            errs.append(f"{eid}: built text {text!r} != script {en!r}")
            continue
        if tokens(text) != tokens(r["jp"]):
            errs.append(f"{eid}: control codes JP {dict(tokens(r['jp']))} built {dict(tokens(text))}")
        errs += [f"{eid}: {p}" for p in batches.width_problems(r, text)]
        done += 1
    return done


def check_filedata(ob, nb, errs):
    fo, fn = filedata.files(ob), filedata.files(nb)
    if len(fo) != len(fn):
        errs.append(f"FILEDATA entry count {len(fo)} -> {len(fn)}")
        return 0
    ctx = insert.Ctx()
    lines = 0
    for i, (a, b) in enumerate(zip(fo, fn)):
        if i in (vwf.BIG_FONT, vwf.SMALL_FONT):
            cells = font_cells(i)
            if len(a) != len(b):
                errs.append(f"font {i}: size {len(a)} -> {len(b)}")
            elif bad := [k for k in range(len(a)) if a[k] != b[k] and k not in cells]:
                errs.append(f"font {i}: {len(bad)} bytes changed outside the English cells (first {bad[0]:#x})")
        elif msg.FIRST <= i <= msg.LAST:
            lines += check_message(i, a, b, ctx, errs)
        elif a != b:
            errs.append(f"FILEDATA {i} changed (not a font or message file)")
    return lines


def check_arm9_strings(n9, ctx, errs):
    rows = {r["id"]: r for r in script.load("arm9.json")}
    done = 0
    for off, slot, _ in script.ARM9_SLOTS:
        r = rows[f"arm9:{off:06X}"]
        if r.get("status") == "data" or not r.get(insert.LANG):
            continue
        text = ctx.en.decode(n9, off)[0]
        if text != r[insert.LANG] + "{end}":
            errs.append(f"{r['id']}: built {text!r} != script {r[insert.LANG]!r}")
        done += 1
    return done


def check_overlay(ro, rn, writes, errs):
    """The ending overlay: only the logged credits-x writes, each a `mov r2, #x` at a credits call."""
    a, b = bytes(ro.files[credits.OVERLAY]), bytes(rn.files[credits.OVERLAY])
    if len(a) != len(b):
        errs.append(f"overlay {credits.OVERLAY}: size {len(a)} -> {len(b)}")
        return 0
    e, ok = romdiff.check(a, b, [], writes)
    errs += [f"overlay {credits.OVERLAY} {x}" for x in e]
    rows = {r["id"]: r for r in script.load(f"msg_{credits.MSG}.json")}
    sites = {xoff: idx for _, idx, xoff, _, _ in credits.calls(a)}
    for off, old, new, by in writes:
        where = f"overlay {credits.OVERLAY} write at {off:#x} ({by})"
        if off not in sites:
            errs.append(f"{where} is not a credits x immediate")
            continue
        if len(old) != 4 or len(new) != 4:
            errs.append(f"{where}: {len(old)}/{len(new)} bytes, a credits x write is exactly one instruction")
            continue
        x = credits.mov_imm(struct.unpack("<I", new)[0], 2)
        r = rows.get(f"{credits.MSG}:{sites[off]}")
        want = credits.centred_x(r[insert.LANG]) if r and r.get(insert.LANG) else None
        if x is None:
            errs.append(f"{where}: new instruction {new.hex()} is not `mov r2, #imm`")
        elif x != want:
            errs.append(f"{where}: x {x}, the centred x for the script English is {want}")
    written = {off for off, _, _, _ in writes}
    for _, idx, xoff, x, _ in credits.calls(a):
        r = rows.get(f"{credits.MSG}:{idx}")
        if r and r.get(insert.LANG) and credits.centred_x(r[insert.LANG]) != x and xoff not in written:
            errs.append(f"overlay {credits.OVERLAY}: credits {credits.MSG}:{idx} at {xoff:#x} not re-centred")
    return ok


def check(orig, built, writes):
    """List of problems (empty = ok) and a one-line summary. writes: {target: log} (writelog.load)."""
    errs = []
    check_header(orig, built, errs)
    ro, rn = ndspy.rom.NintendoDSRom(orig), ndspy.rom.NintendoDSRom(built)
    fid = check_containers(ro, rn, errs)
    w9, wov = writes.get("arm9", []), writes.get("overlay1", [])
    ok9 = check_arm9(bytes(ro.arm9), bytes(rn.arm9), w9, errs)
    okov = check_overlay(ro, rn, wov, errs)
    lines = check_filedata(bytes(ro.files[fid]), bytes(rn.files[fid]), errs)
    slots = check_arm9_strings(bytes(rn.arm9), insert.Ctx(), errs)
    if len(built) != len(orig) or built[len(built) - 0x100:] != b"\xff" * 0x100:
        errs.append("built ROM is not padded to the cartridge size with 0xFF")
    unknown = set(writes) - {"arm9", "overlay1"}
    if unknown:
        errs.append(f"write log targets romcheck does not audit: {sorted(unknown)}")
    return errs, (f"{lines} translated strings + {slots} arm9 slots checked, {len(w9)} arm9 writes ({ok9} bytes), "
                  f"{len(wov)} credits-x writes ({okov} bytes), header/arm7/banner/other files unchanged")


def main(argv):
    built = Path(argv[0]) if argv else BUILT
    wpath = built.with_suffix(".writes.txt")
    if not wpath.exists():
        sys.exit(f"{wpath} missing: rebuild with tools/build.py")
    errs, summary = check(romfs.ROM.read_bytes(), built.read_bytes(), writelog.load(wpath))
    for e in errs[:200]:
        print(e)
    if errs:
        print(f"{len(errs)} problem(s)")
        return 1
    print(f"ok: {summary}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
