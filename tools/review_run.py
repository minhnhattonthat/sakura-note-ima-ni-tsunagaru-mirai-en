"""Review translated batches with `codex exec` read-only (docs/reviewer-brief.md); reports to work/tl/review/.

    python -X utf8 tools/review_run.py b002 b003 ... [--jobs 4]
    python -X utf8 tools/review_run.py --summary          counts of Critical/Important/Minor per report

The pairs come from the batch's .out.tsv (so a batch can be reviewed before it is merged). Each report is
work/tl/review/bNNN.md; the summary line per batch is `bNNN<TAB>critical<TAB>important<TAB>minor<TAB>assessment`.
Exit 1 if any reviewer run failed (nonzero codex exit, or a missing/empty report without the four headings);
a completed review with findings is not a failure. --summary exits 1 if any stored report is invalid.
"""
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import codex_run  # noqa: E402

TL = ROOT / "work/tl"
REV = TL / "review"


def pairs(name):
    rows = [line.split("\t") for line in (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines() if line]
    out = dict(line.split("\t", 1) for line in (TL / f"{name}.out.tsv").read_text(encoding="utf-8").splitlines()
               if "\t" in line)
    return "\n".join(f">> {r[0]} | {r[1]} | {r[4]}\n   EN: {out.get(r[0], '(missing)')}" for r in rows)


def review(name):
    REV.mkdir(parents=True, exist_ok=True)
    parts = []
    for doc in ("docs/reviewer-brief.md", "docs/style-reference.md", "docs/synopsis.md"):
        parts.append(f"=== {doc} ===\n" + (ROOT / doc).read_text(encoding="utf-8"))
    terms = ROOT / f"build/terms_{name}.txt"
    parts.append("=== glossary rows ===\n" + (terms.read_text(encoding="utf-8") if terms.exists()
                                                else (ROOT / "glossary.md").read_text(encoding="utf-8")))
    parts.append(f"=== pairs {name} ===\n" + pairs(name))
    pf = REV / f"{name}.prompt.txt"
    pf.write_text("\n\n".join(parts), encoding="utf-8", newline="\n")
    rc = codex_run.main([str(REV / f"{name}.md"), str(pf)])
    problem = report_problem(name)
    if rc and not problem:
        problem = f"reviewer exit {rc}"
    return (False, f"{name}\t-\t-\t-\tFAILED: {problem}") if problem else (True, summary_line(name))


def report_problem(name):
    """Why bNNN.md is not a completed review (None if it is). Findings are not a problem; a broken run is."""
    p = REV / f"{name}.md"
    if not p.exists():
        return "no report"
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        return "empty report"
    missing = [h for h in ("Critical", "Important", "Minor", "Assessment")
               if not re.search(rf"^#+\s*{h}\b", text, re.I | re.M)]
    if missing:
        return "report lacks " + ", ".join(missing)
    if counts(text)[1] == "?":
        return "empty Assessment"
    return None


def counts(text):
    sec, c = None, {"critical": 0, "important": 0, "minor": 0}
    for line in text.splitlines():
        h = re.match(r"#+\s*(Critical|Important|Minor|Assessment)", line, re.I)
        if h:
            sec = h[1].lower()
            continue
        if sec in c and re.match(r"\s*[-*]?\s*`?(\d+|arm9):[0-9A-Fa-f]+", line):
            c[sec] += 1
    a = re.search(r"#+\s*Assessment\s*\n+\s*(.+)", text)
    return c, (a[1].strip() if a else "?")


def summary_line(name):
    p = REV / f"{name}.md"
    if not p.exists():
        return f"{name}\t-\t-\t-\tNO REPORT"
    c, a = counts(p.read_text(encoding="utf-8"))
    return f"{name}\t{c['critical']}\t{c['important']}\t{c['minor']}\t{a}"


def main(argv):
    if argv == ["--summary"]:
        bad = 0
        for p in sorted(REV.glob("b[0-9][0-9][0-9].md")):
            problem = report_problem(p.stem)
            bad += bool(problem)
            print(f"{p.stem}\t-\t-\t-\tINVALID: {problem}" if problem else summary_line(p.stem))
        return 1 if bad else 0
    names = [a for a in argv if re.fullmatch(r"b\d{3}", a)]
    if not names:
        sys.exit(__doc__)
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 4
    failed = []
    with ThreadPoolExecutor(jobs) as ex:
        for name, (ok, line) in zip(names, ex.map(review, names)):
            print(line, flush=True)
            if not ok:
                failed.append(name)
    if failed:
        print(f"{len(failed)} review(s) failed: {' '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
