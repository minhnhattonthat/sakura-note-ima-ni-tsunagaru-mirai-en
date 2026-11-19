"""release.py: build, gate and package the English patch (references/pipeline.md §Release). Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-smoke]

Steps: default build (English, no --qa/--marker overrides) -> debug tool off (FILEDATA boot script 2477 and the
leftover debug script 2494 identical to the dump: the warp tools are Lua-side, never in the ROM) -> tools/check.py
(tests + lint + romcheck) -> smoke boot -> tools/jp_scan.py (jp_left.py on every text string, 0 runs) ->
qa_gate.py check on every work/qa/**/manifest.tsv (visual tour, story pass) -> textcover.py (0 failing) -> no
unticked line in docs/polish.md -> no template placeholder in README.md, base ROM hashes in it -> xdelta3 patch ->
re-apply to the clean dump and compare -> zip (patch + README.txt, ZIP_STORED) in release/. The playable image stays
in build/sakuranote_en.nds. Refuses to overwrite an existing version's files without --force. Publishing is the
owner's call (never `gh release create` from here).
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ORIG = ROOT / "rom" / "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds"
BUILT = ROOT / "build" / "sakuranote_en.nds"
REL = ROOT / "release"
XDELTA = ROOT / "tools" / "xdelta3" / "xdelta3.exe"
XDELTA_URL = "https://github.com/jmacd/xdelta-gpl/releases/download/v3.1.0/xdelta3-3.1.0-x86_64.exe.zip"
PY = [sys.executable, "-X", "utf8"]
PLACEHOLDER = re.compile(r"<(Game title|platform|publisher|year|repo|file|size|sha1|game|ext)>|<[A-Z][a-z]+ /")
DEBUG_FILES = (2477, 2494)  # boot script, leftover debug-menu script (docs/re/debug.md)


def step(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + (("  " + detail) if detail else ""), flush=True)
    if not ok:
        sys.exit(1)


def run(cmd, **kw):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    return p.returncode, (p.stdout + p.stderr)


def tail(s, n=3):
    return " | ".join(s.strip().splitlines()[-n:])


def hashes(data):
    return {"size": len(data), "crc32": "%08X" % zlib.crc32(data), "md5": hashlib.md5(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest()}


def filedata_entries(rom_bytes):
    import filedata
    import ndspy.rom
    return filedata.files(bytes(ndspy.rom.NintendoDSRom(rom_bytes).getFileByName("FILEDATA.BIN")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    ap.add_argument("--skip-smoke", action="store_true", help="skip the emulator boot (no emulator on this machine)")
    a = ap.parse_args()

    stem = "Sakura_Note_Ima_ni_Tsunagaru_Mirai_EN_v%s" % a.version
    patch, zpath = REL / (stem + ".xdelta"), REL / (stem + ".zip")
    if not a.force and (patch.exists() or zpath.exists()):
        sys.exit("%s already exists: bump --version or pass --force" % (zpath if zpath.exists() else patch))
    from skill import SKILL
    S = Path(SKILL)

    rc, out = run(PY + ["tools/build.py"])
    data = BUILT.read_bytes() if BUILT.exists() else b""
    orig = ORIG.read_bytes()
    step("build (default English, no overrides)", rc == 0 and data and data != orig, tail(out, 1))

    fe, fo = filedata_entries(data), filedata_entries(orig)
    step("debug tool off (boot/debug scripts untouched)", all(fe[i] == fo[i] for i in DEBUG_FILES),
         " ".join(str(i) for i in DEBUG_FILES))

    rc, out = run(PY + ["tools/check.py"], timeout=1800)
    step("check.py (tests, lint, romcheck)", rc == 0, tail(out, 1))
    step("check.py left the build alone", BUILT.read_bytes() == data)

    if not a.skip_smoke:
        rc, out = run(PY + [str(S / "scripts" / "emu.py"), str(BUILT), "--out", "work/qa/release_smoke", "--route",
                            "tools/routes/boot.txt", "--smoke"], timeout=900)
        step("smoke", rc == 0, tail(out, 1))

    rc, out = run(PY + ["tools/jp_scan.py", str(BUILT)])
    step("jp_scan (no Japanese left in the text)", rc == 0 and "\n0 Japanese runs, 0 bytes" in "\n" + out,
         tail(out, 1))

    mans = sorted(p for p in (ROOT / "work" / "qa").rglob("manifest.tsv"))
    step("qa manifests found", len(mans) >= 2, ", ".join(str(m.relative_to(ROOT)) for m in mans))
    for m in mans:
        rc, out = run(PY + [str(S / "scripts" / "qa_gate.py"), "check", str(m), str(m.parent / "verdicts")])
        step("qa_gate check %s" % m.relative_to(ROOT), rc == 0, tail(out, 2))

    rc, out = run(PY + [str(S / "scripts" / "textcover.py"), "work/qa/cover", "build/strings.tsv", "--waive",
                        "docs/text_unshown.tsv"])
    step("textcover (0 failing)", rc == 0, tail(out, 1))

    pol = (ROOT / "docs" / "polish.md").read_text(encoding="utf-8")
    n = len(re.findall(r"^\s*- \[ \]", pol, re.M))
    step("docs/polish.md fully ticked", n == 0, "%d unticked" % n)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    h = hashes(orig)
    step("README.md has no template placeholder", not PLACEHOLDER.search(readme))
    step("README.md has the base ROM hashes", all(h[k] in readme for k in ("crc32", "md5", "sha1")))

    if not XDELTA.exists():
        sys.exit("xdelta3 missing: unzip %s into %s as xdelta3.exe" % (XDELTA_URL, XDELTA.parent))
    REL.mkdir(exist_ok=True)
    rc, out = run([str(XDELTA), "-e", "-9", "-f", "-S", "djw", "-s", str(ORIG), str(BUILT), str(patch)])
    step("xdelta3 patch", rc == 0 and patch.exists(),
         "%s %d bytes" % (patch.name, patch.stat().st_size if patch.exists() else 0))
    check = ROOT / "work" / "release_check.nds"
    rc, out = run([str(XDELTA), "-d", "-f", "-s", str(ORIG), str(patch), str(check)])
    same = rc == 0 and check.exists() and check.read_bytes() == data
    check.unlink(missing_ok=True)
    step("patch re-applied to the clean dump = build", same)

    ph = hashes(data)
    text = (ROOT / "docs" / "release_readme.txt").read_text(encoding="utf-8").format(
        version=a.version, patch=patch.name, pcrc32=ph["crc32"], psha1=ph["sha1"], **h)
    step("zip README has the base ROM hashes", all(str(h[k]) in text for k in ("size", "crc32", "md5", "sha1"))
         and "{" not in text)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", text.replace("\n", "\r\n"))
    names = zipfile.ZipFile(zpath).namelist()
    step("zip = patch + README", sorted(names) == sorted([patch.name, "README.txt"]), "%s %s" % (zpath.name, names))
    print("\nrelease ready: %s (patched CRC32 %s). Publishing is the owner's call." % (zpath, ph["crc32"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
