"""Translate batches with `codex exec` (Orca workers have no translator subagents): prompt, check, fix rounds.

    python -X utf8 tools/tl_run.py b001 b002 ... [--jobs 4] [--rounds 3] [--fix-only]

Per batch: the prompt is docs/translator-brief.md + docs/style-reference.md + docs/synopsis.md + the batch's glossary
rows (build/terms_bNNN.txt) + work/tl/bNNN.tsv. The answer becomes work/tl/bNNN.out.tsv (report lines starting with
'#' go to bNNN.report.txt), then `batches.py check` runs; problems go back to codex with the current output for up
to --rounds fix rounds. --fix-only starts from an existing .out.tsv. Prints one status line per batch; exit 1 if any
batch still fails. Prompts and answers stay in work/tl/run/ for inspection.
"""
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import codex_run  # noqa: E402

TL = ROOT / "work/tl"
RUN = TL / "run"
ROW = re.compile(r"^((?:\d+|arm9):[0-9A-Fa-f]+)(?:\t| {2,}|\t+)(.*)$")


def context():
    parts = []
    for name in ("docs/translator-brief.md", "docs/style-reference.md", "docs/synopsis.md"):
        p = ROOT / name
        if p.exists():
            parts.append(f"=== {name} ===\n" + p.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def parse(answer, want):
    rows, report = {}, []
    for line in answer.splitlines():
        line = line.rstrip("\r")
        if line.startswith("#"):
            report.append(line)
            continue
        m = ROW.match(line.strip("`"))
        if m and m[1] in want and m[1] not in rows:
            rows[m[1]] = m[2].strip()
    return rows, report


def ask(name, tag, prompt):
    RUN.mkdir(parents=True, exist_ok=True)
    pf, out = RUN / f"{name}.{tag}.prompt.txt", RUN / f"{name}.{tag}.answer.txt"
    pf.write_text(prompt, encoding="utf-8", newline="\n")
    codex_run.main([str(out), str(pf)])
    return out.read_text(encoding="utf-8") if out.exists() else ""


def write_out(name, order, rows):
    lines = [f"{i}\t{rows[i]}" for i in order if i in rows]
    (TL / f"{name}.out.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(name, rounds, fix_only):
    batch = (TL / f"{name}.tsv").read_text(encoding="utf-8")
    order = [line.split("\t")[0] for line in batch.splitlines() if line.strip()]
    terms = (ROOT / f"build/terms_{name}.txt").read_text(encoding="utf-8")
    head = context() + f"\n\n=== glossary rows for {name} (JP<TAB>EN, binding) ===\n{terms}"
    report = []
    if fix_only:
        rows = dict(line.split("\t", 1) for line in (TL / f"{name}.out.tsv").read_text(encoding="utf-8").splitlines()
                    if "\t" in line)
    else:
        rows, report = parse(ask(name, "r0", head + f"\n\n=== batch {name} (translate every row) ===\n{batch}"),
                             set(order))
        write_out(name, order, rows)
    entries, gl = batches.index(), batches.glossary()
    for r in range(1, rounds + 1):
        bad, _ = batches.check_batch(name, entries, gl)
        if not bad:
            break
        current = (TL / f"{name}.out.tsv").read_text(encoding="utf-8")
        prompt = (head + f"\n\n=== batch {name} (input) ===\n{batch}\n\n=== your current output ===\n{current}\n\n"
                  "=== problems found by the checker (fix every one; widths are hard limits: rephrase or add a "
                  "{page} in dlg rather than cut meaning) ===\n" + "\n".join(bad) +
                  "\n\nReply with the COMPLETE corrected output: every input id once, same order, id<TAB>English.")
        fixed, rep = parse(ask(name, f"r{r}", prompt), set(order))
        report += rep
        rows.update(fixed)
        write_out(name, order, rows)
    if report:
        with open(TL / f"{name}.report.txt", "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(report) + "\n")
    bad, _ = batches.check_batch(name, entries, gl)
    status = "OK" if not bad else f"{len(bad)} problems"
    print(f"{name}: {status} ({len(rows)}/{len(order)} rows)", flush=True)
    return not bad


def main(argv):
    names = [a for a in argv if re.fullmatch(r"b\d{3}", a)]
    if not names:
        sys.exit(__doc__)
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 4
    rounds = int(argv[argv.index("--rounds") + 1]) if "--rounds" in argv else 3
    with ThreadPoolExecutor(jobs) as ex:
        ok = list(ex.map(lambda n: run(n, rounds, "--fix-only" in argv), names))
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
