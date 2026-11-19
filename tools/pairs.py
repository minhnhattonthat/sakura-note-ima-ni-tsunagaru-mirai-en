"""Story-order text dumps of script/ for translators, reviewers and the story pass.

    python -X utf8 tools/pairs.py dump OUT.txt [--files 2495-2603] [--en]   >> id | speaker | JP  (/ EN with --en)
    python -X utf8 tools/pairs.py speakers                                  speaker index -> JP / EN tag

Speaker = message header word0 = index into 2610 (docs/re/text.md); FFFF/00FF = narration or no tag.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"


def load(fid):
    return json.loads((SCRIPT / f"msg_{fid}.json").read_text(encoding="utf-8"))


def speakers():
    """{word0: (jp, en)} from 2610; word0 is the entry index."""
    out = {}
    for e in load(2610):
        i = int(e["id"].split(":")[1])
        out[i] = (e["jp"], e.get("en", ""))
    return out


def speaker_of(entry, names):
    w0 = int(entry["hdr"].split()[0], 16)
    if w0 in (0xFFFF, 0x00FF):
        return "-"
    jp, en = names.get(w0, (f"?{w0:X}", ""))
    return f"{jp} ({en})" if en else jp


def files(spec):
    a, b = (int(x) for x in spec.split("-")) if "-" in spec else (int(spec), int(spec))
    return [f for f in range(a, b + 1) if (SCRIPT / f"msg_{f}.json").exists()]


def dump(out, spec, with_en):
    names = speakers()
    lines = []
    for f in files(spec):
        lines.append(f"## file {f}")
        for e in load(f):
            if e["status"] == "data" or not e["jp"]:
                continue
            lines.append(f">> {e['id']} | {speaker_of(e, names)} | {e['jp']}")
            if with_en:
                lines.append(f"   EN: {e.get('en', '')}")
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{out}: {len(lines)} lines")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "speakers":
        for i, (jp, en) in sorted(speakers().items()):
            print(f"{i}\t{jp}\t{en}")
        return 0
    if argv[0] == "dump" and len(argv) >= 2:
        spec = argv[argv.index("--files") + 1] if "--files" in argv else "2495-2616"
        dump(argv[1], spec, "--en" in argv)
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
