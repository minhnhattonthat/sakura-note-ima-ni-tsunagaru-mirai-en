"""scrrefs.py: which message strings the game's scripts (SCR0 files in FILEDATA) can display.

    python -X utf8 tools/scrrefs.py [--out work/qa/scrrefs.tsv] [--unref]

SCR0 layout (docs/re/scripts.md): u16 function count at 8, import count at 0xA, u32 offset table at 0x20 (functions,
a 0, imports). A function record: u32 code length (u16 words) at +0x10, name at +0x20, code at +0x40; an import
record: u16 argc at +6, name at +0x20. Code is a stack machine: 40xx push immediate (4000/4001/4005 one operand word,
4002-4004 two), 60xx push variable (one word), 2102 N call import N (pops argc), 2002 N call local, A000 pop,
01xx flow (0109 has two operand words), other 00xx operators.

The scan simulates the stack and records, per script function, the last immediate `SetMessageFile(F)` and each
message call's immediate index arguments. Message calls take the index as their first argument (verified:
MessageObjWait(0, 0, ...) and (1, 0, ...) in event 1943 show 2499:0 and 2499:1); the simulation can drift by one
around complex expressions, so the first two integer arguments both count. That makes the referenced set a
superset: a string outside it is one no script names with an immediate. Writes `file:index<TAB>script fid` rows.
--unref prints the message strings (files 2495-2603) no script references.
"""
import argparse
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import filedata  # noqa: E402

MSG_CALLS = {"MessageObj", "MessageObjWait", "MessageAction", "MessageC", "MessageIC", "MessageMC", "MessageObjM",
             "MessageWaitC", "MessageXY", "Jimaku", "Jimaku2"}
DIALOGUE = range(2495, 2604)


def parse(d):
    nf, ni = struct.unpack_from("<HH", d, 8)
    offs = struct.unpack_from(f"<{nf + 1 + ni}I", d, 0x20)
    funcs, imps = [], []
    for o in offs[:nf]:
        if o:
            n = struct.unpack_from("<I", d, o + 0x10)[0]
            funcs.append((d[o + 0x20:o + 0x30].split(b"\0")[0].decode(), struct.unpack_from(f"<{n}H", d, o + 0x40)))
    for o in offs[nf + 1:]:
        imps.append((d[o + 0x20:o + 0x40].split(b"\0")[0].decode(), struct.unpack_from("<H", d, o + 6)[0]))
    return funcs, imps


def calls(d):
    """Yield (function, import name, args) with args int (immediate) or None."""
    funcs, imps = parse(d)
    for fname, w in funcs:
        st, i = [], 0
        while i < len(w):
            op, hi = w[i], w[i] >> 8
            if op in (0x4000, 0x4001, 0x4005):
                st.append(w[i + 1]); i += 2
            elif op in (0x4002, 0x4003, 0x4004):
                st.append(None); i += 3
            elif hi == 0x60:
                st.append(None); i += 2
            elif op == 0x2102:
                nm, argc = imps[w[i + 1]]
                args = ([None] * argc + st)[-argc:] if argc else []
                del st[len(st) - min(argc, len(st)):]
                yield fname, nm, args
                st.append(None); i += 2
            elif op == 0x2002:
                st = [None]; i += 2
            elif op == 0xA000:
                st and st.pop(); i += 1
            elif op == 0x0109:
                i += 3
            elif hi == 0x01:
                st = []; i += 1
            elif hi == 0x00:
                del st[-2:]
                st.append(None); i += 1
            else:
                break


def refs(files):
    """files = FILEDATA payloads by id -> {(msgfile, index): set(script fids)}"""
    out = defaultdict(set)
    for fid, data in enumerate(files):
        if data[:4] != b"SCR0":
            continue
        file_default = None
        found = list(calls(data))
        for _, nm, args in found:
            if nm == "SetMessageFile" and isinstance(args[0], int):
                file_default = args[0]
                break
        cur = {}
        for fname, nm, args in found:
            if nm == "SetMessageFile":
                cur[fname] = args[0] if isinstance(args[0], int) else None
            elif nm in MSG_CALLS:
                mf = cur.get(fname, file_default)
                if mf is None:
                    continue
                for a in [x for x in args if isinstance(x, int)][:2]:
                    out[(mf, a)].add(fid)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "scrrefs.tsv"))
    ap.add_argument("--unref", action="store_true")
    a = ap.parse_args()
    import romfs
    r = refs(filedata.files(romfs.load().getFileByName("FILEDATA.BIN")))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        for (mf, i), fids in sorted(r.items()):
            f.write(f"{mf}:{i}\t{' '.join(map(str, sorted(fids)))}\n")
    total = unref = 0
    for mf in DIALOGUE:
        entries = json.loads((ROOT / "script" / f"msg_{mf}.json").read_text(encoding="utf-8"))
        entries = entries if isinstance(entries, list) else entries["entries"]
        for e in entries:
            total += 1
            idx = int(e["id"].split(":")[1])
            if (mf, idx) not in r:
                unref += 1
                if a.unref:
                    print(e["id"], e["en"][:70].replace("\n", " "))
    print(f"{len(r)} referenced (file, index) pairs -> {a.out}; dialogue files 2495-2603: {total - unref}/{total} "
          f"referenced, {unref} not", file=sys.stderr)


if __name__ == "__main__":
    main()
