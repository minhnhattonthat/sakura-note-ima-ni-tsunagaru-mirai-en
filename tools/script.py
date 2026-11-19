"""script.py: the translation text in script/ (JSON) <-> the ROM's string bytes.

    python -X utf8 tools/script.py extract [--lang en]   # write/refresh script/*.json from the original ROM
    python -X utf8 tools/script.py verify                # roundtrip + coverage against the original ROM
    python -X utf8 tools/script.py stats [--lang en]     # entries / translated per file

Sources (docs/re/text.md):
- message files FILEDATA 2495-2616 -> script/msg_NNNN.json. Each string = 2 header words (speaker, face) + body +
  0xFFFD. `hdr` keeps the header as hex ("0010 0012"); `jp` is the body decoded with tbl/jp.tbl.
- arm9 strings (title menu, save date template, default names) -> script/arm9.json, fixed slots: `max` = bytes the
  slot holds up to the next string (in place; phase 7 decides relocation).

Entry fields: id (stable: "2495:0", "arm9:092798"), hdr, jp, <lang> (the translation, "" until done), status
(todo | data: not shown in the release, needs no translation), notes. `max` for fixed slots.

Extract never clobbers a translation: an existing file keeps every entry's translation, status and notes; only `jp`
and `hdr` are refreshed, and ids whose jp changed are printed (re-check their translations).
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import msg  # noqa: E402
import romfs  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
END = 0xFFFD

# Strings that never reach the player in the release (status "data", left as the original bytes).
DATA_FILES = {
    2612: "debug menu labels (leftover debug script 2494; not reachable in the release)",
    2614: "developers' message test (メッセージのテスト); no script shows it",
}
DATA_RANGES = {2613: (range(0, 23), "copy of the 2612 debug labels at the head of the system-text file")}
JP = re.compile(r"[、-ヿ一-鿿！-｠①-⓿・…―～]")


def auto_status(fid, k, text):
    """(status, note) for a freshly extracted string."""
    if fid in DATA_FILES:
        return "data", DATA_FILES[fid] if k == 0 else ""
    if fid in DATA_RANGES and k in DATA_RANGES[fid][0]:
        return "data", DATA_RANGES[fid][1] if k == 0 else ""
    if not JP.search(re.sub(r"\{[^}]*\}", "", text)):
        return "data", "no Japanese text: insert the original"
    return "todo", ""

# arm9 string slots: (offset, slot bytes incl. terminator and the zero pad up to the next slot). Found by scanning
# arm9 + overlays for FFFD-terminated runs of table codes (tests/test_script.py repeats the scan).
ARM9_SLOTS = [
    (0x092798, 0x0E, "title menu item (New Game)"),
    (0x0927A6, 0x20, "save slot date template"),
    (0x0941C0, 0x14, "default full name (surname + given)"),
    (0x0941D4, 0x14, "default surname"),
    (0x0941E8, 0x14, "default given name"),
    (0x0941FC, 0x14, "default pet name (dog or cat: guess)"),
    (0x094210, 0x14, "default pet name (dog or cat: guess)"),
]


def table():
    return Table.load(ROOT / "tbl" / "jp.tbl")


def pack(words):
    return struct.pack("<%dH" % len(words), *words)


def split_msg(words):
    """(header words, body words) of one message string (words end in FFFD)."""
    assert len(words) >= 3 and words[-1] == END, words
    return words[:2], words[2:-1]


def hdr_str(h):
    return " ".join(f"{w:04X}" for w in h)


def hdr_words(s):
    return [int(x, 16) for x in s.split()]


def encode_msg(hdr, text, tbl):
    """Bytes of one message string: header + encoded text + FFFD."""
    return pack(hdr_words(hdr)) + tbl.encode(text) + pack([END])


def arm9_strings(a9, tbl):
    """Yield (offset, slot, text, raw bytes through FFFD) for each arm9 slot."""
    for off, slot, note in ARM9_SLOTS:
        txt, used = tbl.decode(a9, off)
        yield off, slot, note, txt, a9[off:off + used]


def fresh_entries(tbl, rom=None):
    """{filename: [entry, ...]} decoded from the original ROM (no translations)."""
    rom = rom or romfs.load()
    out = {}
    for fid, ms in msg.all_files().items():
        rows = []
        for k, w in enumerate(ms):
            h, body = split_msg(w)
            b = pack(body)
            text = tbl.decode(b, 0, len(b))[0]
            status, note = auto_status(fid, k, text)
            rows.append({"id": f"{fid}:{k}", "hdr": hdr_str(h), "jp": text, "status": status, "notes": note})
        out[f"msg_{fid}.json"] = rows
    a9 = bytes(rom.arm9)
    rows = []
    for off, slot, note, txt, raw in arm9_strings(a9, tbl):
        assert txt.endswith("{end}"), txt
        rows.append({"id": f"arm9:{off:06X}", "jp": txt[:-len("{end}")], "max": slot, "status": "todo",
                     "notes": note})
    out["arm9.json"] = rows
    return out


def load(name):
    return json.loads((SCRIPT / name).read_text(encoding="utf-8"))


def save(name, rows):
    SCRIPT.mkdir(exist_ok=True)
    (SCRIPT / name).write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def extract(lang):
    tbl = table()
    changed = []
    for name, rows in fresh_entries(tbl).items():
        old = {r["id"]: r for r in load(name)} if (SCRIPT / name).is_file() else {}
        merged = []
        for r in rows:
            o = old.get(r["id"])
            new = dict(r)
            new[lang] = ""
            if o:
                if o.get("jp") != r["jp"] and o.get(lang):
                    changed.append(r["id"])
                for key in (lang, "status", "notes"):
                    if key in o:
                        new[key] = o[key]
            # field order: id hdr jp <lang> max status notes
            order = ["id", "hdr", "jp", lang, "max", "status", "notes"]
            merged.append({k: new[k] for k in order if k in new})
        lost = set(old) - {r["id"] for r in rows}
        if lost:
            sys.exit(f"{name}: existing ids no longer in the ROM: {sorted(lost)[:5]}...; not overwriting")
        save(name, merged)
    print(f"script/: {len(list(SCRIPT.glob('*.json')))} files")
    for i in changed:
        print("jp changed under an existing translation:", i)


def verify():
    """Roundtrip every script/ entry's jp to the original bytes; message files fully covered. Returns error list."""
    tbl = table()
    rom = romfs.load()
    errs = []
    for fid, ms in msg.all_files().items():
        name = f"msg_{fid}.json"
        if not (SCRIPT / name).is_file():
            errs.append(f"{name} missing")
            continue
        rows = load(name)
        if [r["id"] for r in rows] != [f"{fid}:{k}" for k in range(len(ms))]:
            errs.append(f"{name}: ids don't match the file's {len(ms)} strings")
            continue
        for r, w in zip(rows, ms):
            if END in w[:-1]:
                errs.append(f"{r['id']}: a second FFFD inside the string (an entry point the table misses)")
            if encode_msg(r["hdr"], r["jp"], tbl) != pack(w):
                errs.append(f"{r['id']}: jp does not re-encode to the original bytes")
    a9 = bytes(rom.arm9)
    rows = {r["id"]: r for r in load("arm9.json")} if (SCRIPT / "arm9.json").is_file() else {}
    for off, slot, note, txt, raw in arm9_strings(a9, tbl):
        r = rows.get(f"arm9:{off:06X}")
        if not r or tbl.encode(r["jp"]) + pack([END]) != raw:
            errs.append(f"arm9:{off:06X}: missing or does not roundtrip")
        elif any(a9[off + len(raw):off + slot]):
            errs.append(f"arm9:{off:06X}: slot pad not zero")
    return errs


def stats(lang):
    for p in sorted(SCRIPT.glob("*.json")):
        rows = load(p.name)
        todo = [r for r in rows if r.get("status") != "data"]
        done = sum(1 for r in todo if r.get(lang))
        print(f"{p.name}\t{len(rows)}\t{done}/{len(todo)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("extract", "stats"):
        s = sub.add_parser(c)
        s.add_argument("--lang", default="en")
    sub.add_parser("verify")
    a = ap.parse_args()
    if a.cmd == "extract":
        extract(a.lang)
    elif a.cmd == "stats":
        stats(a.lang)
    else:
        errs = verify()
        for e in errs:
            print(e)
        print("verify:", "ok" if not errs else f"{len(errs)} errors")
        return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
