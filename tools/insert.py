"""insert.py: script/*.json -> message-file and arm9 bytes for the build.

Per entry: a translation in `en` is encoded with the English table (vwf.en_table(); speaker tags in file 2610 with
vwf.tag_table(), the 8x8 tag font's codes); entries without one keep their original Japanese bytes, or, in the
marker build, become a marker: `[id]` + a ruler of digits up to MARKER_PX on each line (line breaks, pages and
control codes kept), so every box shows which string it is and how far a full line reaches. Tags get `T<index>` +
letters. Status `data` entries always keep the original bytes.

Message files are rebuilt whole (u32 offset table + strings): offsets are file-relative, so strings may grow.
arm9 strings stay in their fixed slots (script.ARM9_SLOTS); a translation longer than its slot is an error.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import script  # noqa: E402
import vwf  # noqa: E402
from tbl import Table  # noqa: E402

LANG = "en"
TAG_FILE = 2610       # speaker tags: index = message header word0, drawn in the 8x8 font (vwf.py)
TAG_FIRST = 5         # 2610:0-4 = player-name placeholders
MARKER_PX = 240
TAG_MARKER_PX = 200
RULER = "1234567890"
TAG_RULER = "abcdefghijklmnopqrstuvwxyz"
BREAK = re.compile(r"(\{n\}|\{page\})")
TOKEN = re.compile(r"\{[^}]*\}")


def with_jp_fallback(t, jp):
    """t plus the Japanese glyphs (for symbols an English line keeps); t's own entries win."""
    lines = [f"{k.hex().upper()}={chr(92) + 's' if v == ' ' else v}" for k, v in t.dec.items()]
    lines += [f"{k.hex().upper()}={v}" for k, v in jp.dec.items()]
    lines += [f"{k.hex().upper()}={{{n}{':' + str(a) if a else ''}}}" for k, (n, a) in jp.ctrl.items()]
    return Table(lines)


class Ctx:
    """Tables and width functions, built once per build."""

    def __init__(self):
        self.jp = script.table()
        self.en = with_jp_fallback(vwf.en_table(), self.jp)
        self.tag = vwf.tag_table()
        self.glyphs = vwf.load_glyphs()
        self.small = vwf.small_widths()

    def width(self, text, tag=False):
        return vwf.tag_width(text, self.small) if tag else vwf.text_width(text, self.glyphs)


def ruler(prefix, px, width, chars, maxlen=999):
    s, k = prefix, 0
    while len(s) < maxlen and width(s + chars[k % len(chars)]) <= px:
        s += chars[k % len(chars)]
        k += 1
    return s


def marker(eid, jp, ctx, tag=False):
    """Marker text for one entry: each line -> prefix + ruler, its control tokens kept after the text."""
    px = TAG_MARKER_PX if tag else MARKER_PX
    chars = TAG_RULER if tag else RULER
    first = f"T{eid.split(':')[1]} " if tag else f"[{eid}] "
    out, line_no = [], 0
    for p in BREAK.split(jp):
        if BREAK.fullmatch(p):
            out.append(p)
            continue
        toks = "".join(TOKEN.findall(p))
        lead = re.match(r"(\{[^}]*\})*", p)[0]  # tokens before the first character stay in front
        rest = toks[len(lead):] if toks.startswith(lead) else toks
        prefix = first if line_no == 0 else ""
        maxlen = 2 * vwf.TAG_FILE_SLOTS if tag else 999
        out.append(lead + ruler(prefix, px, lambda s: ctx.width(s, tag), chars, maxlen) + rest)
        line_no += 1
    return "".join(out)


QA = {}  # id -> text: single-entry overrides for width tests (build.py --qa ID=TEXT)
QA_FILL = re.compile(r"@(\d+(?:,\d+)*)(?:x(\d+))?")
FILL_CHARS = "234567890"


def fill(px, width):
    """A line exactly px wide: '|' + digits + '|', closed with 2-px '.' and one 5-px 'k' for an odd width.
    The bars mark both ends, so a zoomed shot shows whether the last column still draws."""
    s = "|"
    k = 0
    while width(s + FILL_CHARS[k % len(FILL_CHARS)] + "|") <= px - 2:
        s += FILL_CHARS[k % len(FILL_CHARS)]
        k += 1
    if (px - width(s + "|")) % 2:
        s += "k"
    while width(s + "|") < px:
        s += "."
    s += "|"
    if width(s) != px:
        sys.exit(f"--qa fill: cannot make exactly {px} px (got {width(s)})")
    return s


def qa_text(r, spec, ctx, tag=False):
    """--qa value: literal text, or @W / @WxL = L lines each exactly W px, @W1,W2,W3 = one line per width
    (the original's leading tokens kept)."""
    m = QA_FILL.fullmatch(spec)
    if not m:
        return spec
    lead = re.match(r"(\{[^}]*\})*", r["jp"])[0]
    lead = "".join(t for t in TOKEN.findall(lead) if t not in ("{n}", "{page}"))
    widths = [int(w) for w in m[1].split(",")] * int(m[2] or 1)
    return lead + "{n}".join(fill(w, lambda s: ctx.width(s, tag)) for w in widths)


def entry_text(r, marker_build, ctx, tag=False):
    """(text, table) for one entry."""
    if r["id"] in QA:
        return qa_text(r, QA[r["id"]], ctx, tag), ctx.tag if tag else ctx.en
    if r.get("status") == "data":
        return r["jp"], ctx.jp
    if r.get(LANG):
        return r[LANG], ctx.tag if tag else ctx.en
    if marker_build:
        return marker(r["id"], r["jp"], ctx, tag), ctx.tag if tag else ctx.en
    return r["jp"], ctx.jp


def encode_tag(r, text, t):
    """A tag string: header + codes packed two per u16 (vwf.pack_tag) + FFFD. Tags 0-4 are the player-name
    placeholders, never read from the file (0x02036248 takes the names from the save): kept as they are."""
    k = int(r["id"].split(":")[1])
    if k < TAG_FIRST:
        return script.encode_msg(r["hdr"], text, t)
    b = t.encode(text)
    codes = list(struct.unpack(f"<{len(b) // 2}H", b))
    return script.pack(script.hdr_words(r["hdr"])) + vwf.pack_tag(codes) + script.pack([script.END])


def message_file(fid, rows, marker_build=False, ctx=None):
    """Bytes of one message file from its script rows."""
    ctx = ctx or Ctx()
    strings = []
    for r in rows:
        tag = fid == TAG_FILE
        text, t = entry_text(r, marker_build, ctx, tag)
        strings.append(encode_tag(r, text, t) if tag else script.encode_msg(r["hdr"], text, t))
    offs, pos = [], 4 * len(strings)
    for s in strings:
        offs.append(pos)
        pos += len(s)
    return struct.pack(f"<{len(offs)}I", *offs) + b"".join(strings)


def arm9_marker(k, jp):
    lead = re.match(r"(\{[^}]*\})*", jp)[0]
    if "--/--" in jp:
        return jp  # save date template: digits filled in by code; leave it
    return lead + f"a{k}"


def patch_arm9_strings(arm9, rows, marker_build=False, ctx=None):
    """arm9 bytes with translated (or marker) strings written into their fixed slots."""
    ctx = ctx or Ctx()
    out = bytearray(arm9)
    byid = {r["id"]: r for r in rows}
    for k, (off, slot, _note) in enumerate(script.ARM9_SLOTS):
        r = byid[f"arm9:{off:06X}"]
        if r.get("status") == "data":
            continue
        if r["id"] in QA:
            text = qa_text(r, QA[r["id"]], ctx)
        elif r.get(LANG):
            text = r[LANG]
        elif marker_build:
            text = arm9_marker(k, r["jp"])
        else:
            continue
        b = ctx.en.encode(text) + script.pack([script.END])
        if len(b) > slot:
            raise ValueError(f"{r['id']}: {len(b)} bytes, slot holds {slot}")
        out[off:off + slot] = b + b"\0" * (slot - len(b))
    return bytes(out)


def payloads(payloads, marker_build=False):
    """FILEDATA payloads with both fonts patched and every message file rebuilt from script/."""
    import msg
    ctx = Ctx()
    out = list(payloads)
    out[vwf.BIG_FONT] = vwf.patch_font(out[vwf.BIG_FONT])
    out[vwf.SMALL_FONT] = vwf.patch_small_font(out[vwf.SMALL_FONT])[0]
    for fid in range(msg.FIRST, msg.LAST + 1):
        out[fid] = message_file(fid, script.load(f"msg_{fid}.json"), marker_build, ctx)
    return out
