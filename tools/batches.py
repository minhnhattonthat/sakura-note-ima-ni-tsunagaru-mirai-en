"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/

Copied from the skill's assets/batches.py. Fit the ADAPTER section to this game's text format; the rest is shared.
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
sys.path.insert(0, str(ROOT / "tools"))
import vwf  # noqa: E402  (VWF widths: docs/re/vwf.md; box budgets: docs/re/boxes.md)

TOKEN = re.compile(r"\{[^}]*\}")  # control codes; must survive translation
FREE = {"{n}", "{page}", "{sp}"}  # layout codes the English may place freely (line count is checked per form)
VARIABLE = r"\{slot\}"  # a name the game draws: no suffix glued on
NAME = re.compile(r"\{var_[0-9A-F]{2}\}(?:\{slot\})*")
NAME_PX = 40  # a drawn name: 5 slots; English names are short (phase 8 stress saves re-measure)
HONORIFICS = {"ちゃん": "-chan", "くん": "-kun", "さん": "-san", "先生": "-sensei", "せんせい": "-sensei"}
GLYPHS = vwf.load_glyphs()
EN_CHARS = set(vwf.code_map(GLYPHS))
TAG_CHARS = {c for c, code in vwf.small_codes().items() if code < 0xFD}  # 0xFD ')' = the packed tag's stop byte
SMALL_W = vwf.small_widths()


def docs():
    """(path, doc, entries) per script file; entries hold id, jp, en, and optionally speaker, box, max, dup."""
    for path in sorted(SCRIPT.rglob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        yield path, doc, doc["entries"] if isinstance(doc, dict) else doc


def needs_english(entry):
    """Empty JP isn't "untranslated": it would be re-queued forever. status data = never translated."""
    return bool(entry.get("jp")) and not entry.get("en") and entry.get("status") != "data"


def group_of(entry):
    """One message file stays together in story order where it fits (split() cuts at the size limit)."""
    return entry.get("dup") or entry["id"]


def entry_key(entry):
    return entry["id"]


def _fid(entry):
    a = entry["id"].split(":") + [""]
    return (int(a[0]) if a[0].isdigit() else 0), (int(a[1]) if a[1].isdigit() else -1)


def box(entry):
    """(form, per-line px list or None, max lines per page or None, note) from docs/re/boxes.md."""
    f, i = _fid(entry)
    w0 = entry.get("hdr", "FFFF").split()[0]
    if entry["id"].startswith("arm9"):
        m = entry.get("max", 0)
        return "slot", None, 1, f"fixed slot: at most {(m - 2) // 2} codes incl. control codes (each char = 1)"
    if f <= 2603 or f == 2606:
        if w0 == "FFFF":
            return "narration", [240] * 7, 7, "240px/line centred, <=7 lines, line 6 <=190 on a 6-7 line page"
        return "dlg", [228, 218], 2, "2 lines/page: 228px, last line of a page 218px; add {page} for more"
    if f == 2604:
        return "credits", [120] * 4, 4, "120px/line, same line count as JP"
    if f == 2605:
        return "item", [216] * 7, 7, "name{n}{n}body: 216px, body <=5 lines"
    if f == 2607:
        if i in (1, 2, 3, 4) or 6 <= i <= 12:
            return "button", [160], 1, "160px button"
        return "panel", [216] * 4, 4, "216px popup panel, centred, <=4 lines"
    if f == 2608:
        return "menu", [160], 1, "160px list row"
    if f == 2609:
        return "menu", [200], 1, "200px track name (guess)"
    if f == 2610:
        return "tag", None, 1, "speaker tag: <=18 chars, no ) , \" ; : - in tags"
    if f == 2611:
        if i >= 76:
            return "profile", [128] * 4, 4, "128px header line"
        return "profile", [228] * 10, 10, "228px/line, <=10 lines"
    if f == 2613:
        if 25 <= i <= 60:
            return "card", [200] * 3, 3, "chapter card: 200px, keep blank lines blank"
        if 66 <= i <= 81:
            return "panel", [216, 160, 160, 160], 4, "prompt 216px, button lines 160px"
        return "panel", [216] * 4, 4, "216px system text"
    if f == 2615:
        return "menu", [216] * 4, 4, "216px board text"
    if f == 2616:
        if i <= 4:
            return "menu", [216], 1, "216px title"
        return "dlg", [228, 218], 2, "tutorial: 2 lines/page 228/218px; add {page} for more"
    return "menu", [216] * 4, 4, "216px"


def limit_label(entry):
    return box(entry)[3]


_TAGS = {}


def speaker(entry):
    """Speaker tag name (2610 index = header word0), JP plus the English once translated; '-' = none."""
    if not _TAGS and (SCRIPT / "msg_2610.json").exists():
        for e in json.loads((SCRIPT / "msg_2610.json").read_text(encoding="utf-8")):
            _TAGS[int(e["id"].split(":")[1])] = e["jp"] + (f" ({e['en']})" if e.get("en") else "")
    f = _fid(entry)[0]
    if "hdr" not in entry or f == 0 or (f >= 2604 and f not in (2606, 2616)):
        return "-"
    w0 = int(entry["hdr"].split()[0], 16)
    return _TAGS.get(w0, "-") if w0 not in (0xFFFF, 0x00FF) else "-"


def line_width(line):
    px = NAME_PX * len(NAME.findall(line))
    return px + vwf.text_width(TOKEN.sub("", NAME.sub("", line)), GLYPHS)


def width_problems(entry, en):
    form, px, lines, _ = box(entry)
    jp = entry["jp"]
    if form == "tag":
        bad = sorted({c for c in en if c not in TAG_CHARS})
        return ([f"tag: characters not in the tag font {bad}"] if bad else []) + \
               ([f"tag: {len(en)} chars > 18"] if len(en) > 18 else [])
    if form == "slot":
        n = len(TOKEN.sub("", en)) + len(TOKEN.findall(en))
        cap = (entry.get("max", 0) - 2) // 2
        return [f"slot: {n} codes > {cap}"] if cap and n > cap else []
    out = []
    if form in ("card", "credits", "button") and jp.count("{n}") != en.count("{n}"):
        out.append(f"{form}: keep the JP line count ({jp.count('{n}') + 1} lines)")
    if form == "card" and [r == "" for r in jp.split("{n}")] != [TOKEN.sub("", r).strip() == "" for r in en.split("{n}")]:
        out.append("card: blank lines must stay where the JP has them")
    if form == "item" and "{n}{n}" in jp and "{n}{n}" not in en:
        out.append("item: keep name{n}{n}body")
    for p, page in enumerate(en.split("{page}")):
        rows = page.split("{n}")
        if lines and len(rows) > lines:
            out.append(f"page {p + 1}: {len(rows)} lines > {lines}")
        for k, row in enumerate(rows):
            if form == "dlg":
                cap = px[1] if k == len(rows) - 1 else px[0]
            elif form == "narration" and len(rows) >= 6 and k == 5:
                cap = 190
            else:
                cap = px[min(k, len(px) - 1)]
            w = line_width(row)
            if w > cap:
                out.append(f"page {p + 1} line {k + 1}: {w}px > {cap}px")
    return out


def encodable(char):
    return char in EN_CHARS
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    jp = jp.replace(" / ", "")
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary(guidance=False):
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    enforced = True
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            enforced = "guidance" not in line.lower()  # "## Guidance ..." tables: context-dependent, not linted
        if not enforced and not guidance:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one line of English."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en:
        out.append("escape sequence or tab in the English")
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (rephrase: no suffix glued onto a name)')
    jp_plain = TOKEN.sub("", jp)
    en_terms = " ".join(TOKEN.sub(lambda m: " " if m[0] in FREE else m[0], en).replace("\\n", " ").split()).lower()
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(" ".join(e.split()).lower() in en_terms for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_form, en_form in HONORIFICS.items():  # only after a drawn name or a katakana name (not おじさん)
        if re.search(rf"(\}}|[ァ-ヺ]){jp_form}", jp) and en_form.lower() not in en.lower():
            out.append(f"honorific {jp_form} needs {en_form}")
    return out + width_problems(entry, en)


def index():
    result = {}
    for _, _, entries in docs():
        for e in entries:
            key = entry_key(e)
            if key in result:
                raise ValueError(f"duplicate batch key {key!r}: supply a unique addr or adapt entry_key")
            result[key] = e
    return result


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    index()  # reject ambiguous ids before writing any batches
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and entry_key(e) not in taken:
                groups.setdefault(group_of(e), []).append(e)
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary(guidance=True)  # translators also get the context-dependent rows
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{entry_key(e)}\t{speaker(e)}\t{box(e)[0]}\t{limit_label(e)}\t{e['jp']}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = [(j, " / ".join(ens)) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if entry_key(e) in new and e.get("en") and e["en"] != new[entry_key(e)]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            if entry_key(e) in new and e.get("en") != new[entry_key(e)]:
                e["en"], e["status"] = new[entry_key(e)], "done"
                touched = True
                changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        print(f"{len(entries)} entries, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    failed = 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
        if cmd == "merge" and not bad:
            merge(rows, overwrite)
    return 1 if failed else 0


def _selftest():
    import tempfile
    global ROOT, TL, SCRIPT, GLOSSARY
    with tempfile.TemporaryDirectory() as d:
        ROOT = Path(d)
        TL, SCRIPT, GLOSSARY = ROOT / "work/tl", ROOT / "script", ROOT / "glossary.md"
        SCRIPT.mkdir()
        GLOSSARY.write_text("| JP | EN | max | notes | Avoid |\n|---|---|---|---|---|\n| ミン | Min | | | Minn |\n", encoding="utf-8")
        script = [{"id": "a", "jp": "ミンが来た{n}", "en": ""}, {"id": "b", "jp": "タイミング", "en": ""},
                  {"id": "c", "jp": "", "en": ""}, {"id": "d", "jp": "{slot}番", "en": ""}]
        (SCRIPT / "s.json").write_text(json.dumps(script), encoding="utf-8")
        assert main(["split"]) is None
        assert [r[0] for r in read_tsv(TL / "b001.tsv")] == ["a", "b", "d"]  # c has no JP
        assert "ミン\tMin" in (ROOT / "build/terms_b001.txt").read_text(encoding="utf-8")
        split(3500)
        assert len(existing()) == 1  # a repeat run makes no duplicate batch
        out = TL / "b001.out.tsv"
        out.write_text("a\tHe came\nb\tTiming\n", encoding="utf-8")
        assert main(["check", "b001"]) == 1  # d missing, a lacks the glossary term
        out.write_text("a\tMin came\nb\tTiming\nd\t{slot}th\n", encoding="utf-8")
        assert main(["merge", "b001"]) == 1  # ordinal after a variable: nothing written
        assert index()["a"]["en"] == ""
        out.write_text("a\tMinn and Min came\nb\tTiming\nd\tNo. {slot}\n", encoding="utf-8")
        assert main(["check", "b001"]) == 1  # the Avoid spelling
        out.write_text("a\tMin came\nb\tThe timing\nd\tNo. {slot}\n", encoding="utf-8")
        assert main(["merge", "b001"]) == 0 and index()["b"]["en"] == "The timing"
        assert main(["check"]) == 0
        out.write_text("a\tMin arrived\nb\tThe timing\nd\tNo. {slot}\n", encoding="utf-8")
        try:
            main(["merge", "b001"])
            raise AssertionError("merge replaced English")
        except SystemExit:
            pass
        assert main(["merge", "b001", "--overwrite"]) == 0 and index()["a"]["en"] == "Min arrived"
    print("selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
