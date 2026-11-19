"""vqa_run.py: visual-QA verdicts by `codex exec` read-only, one call per chunk (the Orca-worker stand-in for the
visual-qa subagent: Orca refuses nested workers).

    python -X utf8 tools/vqa_run.py CHUNK.txt [CHUNK.txt ...] [--jobs 3] [--model M]

A chunk is `qa_gate.py todo` output (`id<TAB>path`). The sheets are attached as images (codex's read-only sandbox
gets the prompt and the images only), the prompt is docs/visual-qa-brief.md + the glossary's Characters and
Places tables + the id list. The answer's `id<TAB>ok|issue<TAB>note` lines go to work/qa/verdicts/<chunk stem>.tsv;
the raw answer to work/qa/vqa_raw/<chunk stem>.md. Exit 1 if a run failed or an id got no verdict (no file is
written for that chunk then, so the gate keeps failing).
"""
import argparse
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERDICTS = ROOT / "work" / "qa" / "verdicts"
RAW = ROOT / "work" / "qa" / "vqa_raw"
LINE = re.compile(r"^\s*`?([\w.\-]+)`?\s*\t\s*(ok|issue)\s*\t(.*)$")


def glossary_names():
    text = (ROOT / "glossary.md").read_text(encoding="utf-8")
    out, keep = [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            keep = ln[3:].strip() in ("Characters", "Places")
        if keep:
            out.append(ln)
    return "\n".join(out)


def prompt(rows):
    brief = (ROOT / "docs" / "visual-qa-brief.md").read_text(encoding="utf-8")
    ids = "\n".join(f"{n + 1}. {i}" for n, (i, _) in enumerate(rows))
    return (f"{brief}\n\n## This dispatch\nYou cannot run tools or open files: everything is in this prompt. The "
            f"{len(rows)} attached images are the sheets, in this order (image n = id n):\n{ids}\n\n"
            f"## Glossary (names)\n{glossary_names()}\n\n"
            "## Answer format\nFor each id, one line `id<TAB>ok|issue<TAB>note` (a real tab character). For an issue "
            "say which half (English left / original right), which screen and what is wrong. No other lines.\n")


def run(chunk, model):
    rows = [ln.split("\t") for ln in Path(chunk).read_text(encoding="utf-8").splitlines() if ln.strip()]
    rows = [(r[0], r[1]) for r in rows]
    RAW.mkdir(parents=True, exist_ok=True)
    raw = RAW / f"{Path(chunk).stem}.md"
    raw.unlink(missing_ok=True)
    cmd = [shutil.which("codex"), "exec", "-s", "read-only", "--skip-git-repo-check", "-o", str(raw)]
    if model:
        cmd += ["-m", model]
    for _, p in rows:
        cmd += ["-i", str(ROOT / p) if not Path(p).is_absolute() else p]
    r = subprocess.run(cmd + ["-"], input=prompt(rows), text=True, encoding="utf-8", capture_output=True)
    if r.returncode or not raw.exists():
        return f"{chunk}: codex exit {r.returncode}: {r.stderr[-400:]}"
    got = {}
    for ln in raw.read_text(encoding="utf-8").splitlines():
        m = LINE.match(ln)
        if m:
            key = m[1]
            if key.isdigit() and 1 <= int(key) <= len(rows):  # answered by image number instead of id
                key = rows[int(key) - 1][0]
            got[key] = (m[2], m[3].strip().replace("\t", " "))
    lost = [i for i, _ in rows if i not in got]
    if lost:
        return f"{chunk}: no verdict for {lost}"
    VERDICTS.mkdir(parents=True, exist_ok=True)
    out = VERDICTS / f"{Path(chunk).stem}.tsv"
    out.write_text("".join(f"{i}\t{got[i][0]}\t{got[i][1]}\n" for i, _ in rows), encoding="utf-8", newline="\n")
    n_issue = sum(got[i][0] == "issue" for i, _ in rows)
    return f"{chunk}: {len(rows)} verdicts, {n_issue} issue(s) -> {out.name}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chunks", nargs="+")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--model")
    a = ap.parse_args()
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda c: run(c, a.model), a.chunks))
    for r in res:
        print(r)
    return 0 if all("verdicts," in r for r in res) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
