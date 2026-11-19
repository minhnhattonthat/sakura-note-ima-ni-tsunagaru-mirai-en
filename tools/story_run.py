"""Story pass by `codex exec` read-only (the Orca-worker stand-in for the story-reviewer subagent).

    python -X utf8 tools/story_run.py [CHAPTER ...] [--jobs 3] [--model M] [--tag r1]

Chapters default to those `qa_gate.py todo work/qa/story/manifest.tsv work/qa/story/verdicts` would list (no current
verdict). Prompt = docs/story-reviewer-brief.md + synopsis + style reference + glossary + the chapter file. Report ->
work/qa/story/reports/<chapter>.<tag>.md; the Assessment word -> work/qa/story/verdicts/<chapter>.<tag>.tsv
(`chapter<TAB>ok|issue<TAB>note`). A run with no report or no Assessment writes no verdict and exits 1.
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / "work" / "qa" / "story"
CHAPTERS = STORY / "chapters"
PARTS = [ROOT / "docs" / "story-reviewer-brief.md", ROOT / "docs" / "synopsis.md",
         ROOT / "docs" / "style-reference.md", ROOT / "glossary.md"]


def todo():
    """Chapters with no current verdict, from the manifest (id<TAB>path<TAB>sha1<TAB>changed) and verdict files."""
    manifest = STORY / "manifest.tsv"
    changed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        c = line.split("\t")
        if len(c) >= 4:
            changed[c[0]] = float(c[3])
    good = set()
    for v in sorted((STORY / "verdicts").glob("*.tsv"), key=lambda p: p.stat().st_mtime):
        for line in v.read_text(encoding="utf-8").splitlines():
            c = line.split("\t")
            if len(c) >= 2 and c[0] in changed:
                if v.stat().st_mtime >= changed[c[0]] and c[1] in ("ok", "fixed"):
                    good.add(c[0])
                else:
                    good.discard(c[0])
    return [k for k in changed if k not in good]


def assessment(report):
    m = re.search(r"#+\s*Assessment\s*\n+(.+)", report)
    if not m:
        return None
    first = m.group(1).strip().strip("`*").strip()
    word = first.split()[0].strip("`*.:-").lower() if first else ""
    if word not in ("ok", "issue"):
        return None
    return word, first


def run(ch, model, tag):
    reports = STORY / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    out = reports / f"{ch}.{tag}.md"
    cmd = [sys.executable, "-X", "utf8", str(ROOT / "tools" / "codex_run.py"), str(out)]
    cmd += [str(p) for p in PARTS] + [str(CHAPTERS / f"{ch}.txt")]
    if model:
        cmd += ["--model", model]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if not out.exists():
        return ch, f"FAILED rc={r.returncode} {r.stdout.strip()} {r.stderr.strip()[-300:]}"
    a = assessment(out.read_text(encoding="utf-8"))
    if not a:
        return ch, f"NO ASSESSMENT in {out}"
    word, note = a
    vd = STORY / "verdicts"
    vd.mkdir(parents=True, exist_ok=True)
    (vd / f"{ch}.{tag}.tsv").write_text(f"{ch}\t{word}\t{note.replace(chr(9), ' ')}\n", encoding="utf-8")
    return ch, word


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapters", nargs="*")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--model")
    ap.add_argument("--tag", default="r1")
    a = ap.parse_args()
    chs = a.chapters or todo()
    print(f"{len(chs)} chapters: {' '.join(chs)}", flush=True)
    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for ch, res in ex.map(lambda c: run(c, a.model, a.tag), chs):
            print(f"{ch}: {res}", flush=True)
            bad += res not in ("ok", "issue")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
