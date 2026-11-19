"""Story-order text dumps of script/ for translators, reviewers and the story pass.

    python -X utf8 tools/pairs.py dump OUT.txt [--files 2495-2603] [--en]   >> id | speaker | JP  (/ EN with --en)
    python -X utf8 tools/pairs.py speakers                                  speaker index -> JP / EN tag
    python -X utf8 tools/pairs.py chapters work/qa/story/chapters           story-pass chapter files (CHAPTERS)

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


# Story-pass chapters (docs/synopsis.md file map), in story order. The game's chapters 1-4 interleave the boy, cat and
# dog routes; the script files group by route, so the pass reads one route segment per file.
CHAPTERS = [
    ("01_opening", "2495-2503", "Opening, first rescue, tutorial and town."),
    ("02_holiday", "2505-2511", "Holiday visits, broken promises, fireworks, second rescue."),
    ("03_school", "2512-2519", "School dungeon, reconciliation, departure. 2512-2513 (dungeon dialogue) play during "
     "the attack in 2517; read them as inserted there."),
    ("04_kiriya", "2520-2527", "Kiriya, factory, failed remedy, Takashi's disappearance; boy-route climax and "
     "one-year epilogue (2526-2527)."),
    ("05_cat", "2528-2546", "Cat viewpoint: arrival, family tension, rescues and tree ancestry."),
    ("06_cat_adults", "2549-2556", "Cat viewpoint: interpretation chain and adult investigation."),
    ("07_afterlife", "2559-2566", "Traffic incident, afterlife, pact revelation and the cat's sacrifice."),
    ("08_dog", "2567-2585", "Dog viewpoint: arrival, rescues and separated family."),
    ("09_dog_departure", "2588-2593", "Dog viewpoint: discoveries and the children's departure."),
    ("10_dog_finale", "2596-2603", "Dog viewpoint: traffic incident, Kiriya and finale."),
    ("11_bonus", "2604-2606", "Credits, inventory, Kaname's four bonus episodes."),
    ("12_system", "2607-2616", "Save/load, objectives, sound menu, labels, dossiers, episode index, tutorials "
     "(not one sequence: judge consistency with the story and voice)."),
]
LABELS = ROOT / "gfx" / "labels.tsv"


def choices_text():
    """The 85 graphic choice buttons (gfx/labels.tsv rows on 4033): JP from the row note, EN as drawn."""
    lines = ["# Choice buttons (graphics, file 4033). Shown as two-button answers inside dialogue; the script picks",
             "# the pair. Translated without scene context: judge tone and fit against the synopsis and voices.",
             "# Button width 56 or 72 px (the drawn EN must fit; do not suggest longer text without saying so).",
             "# Waived for fit (docs/polish.md): 4033:19 'Great Sakura Mochi' is 95 px in a 72 px button, so the",
             "# button reads 'Sakura Mochi' (its pair 'Hilltop flats' lacks SAKURA and MOCHI, so the answer stays",
             "# clear); 4033:49/50 'Dried Sardines' does not fit the 56 px button, so the pair says 'fish'."]
    for row in LABELS.read_text(encoding="utf-8").splitlines():
        c = row.split("\t")
        if row.startswith("#") or len(c) < 12 or c[0] != "4033":
            continue
        jp = c[11].removeprefix("choice ").strip()
        lines.append(f">> 4033:{c[2]} | - | {jp}")
        lines.append(f"   EN: {c[10]}")
    return lines


def chapters(outdir):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.txt"):
        old.unlink()
    for name, spec, note in CHAPTERS:
        p = out / f"{name}.txt"
        dump(p, spec, True)
        body = p.read_text(encoding="utf-8")
        p.write_text(f"# Chapter {name} (files {spec}): {note}\n{body}", encoding="utf-8", newline="\n")
    p = out / "13_choices.txt"
    p.write_text("\n".join(choices_text()) + "\n", encoding="utf-8", newline="\n")
    print(f"{p}: choices")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "chapters" and len(argv) == 2:
        chapters(argv[1])
        return 0
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
