"""Run `codex exec` read-only on prompt files (the Orca-worker stand-in for translator/reviewer subagents).

    python -X utf8 tools/codex_run.py OUT.md PART.txt [PART.txt ...] [--model M]

The parts are concatenated into the prompt (codex's sandbox can't read repo files, so everything goes in the prompt).
OUT.md is deleted first, so a failed run never leaves the previous run's answer behind. Exit code = codex's.
"""
import shutil
import subprocess
import sys
from pathlib import Path


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    model = None
    if "--model" in argv:
        i = argv.index("--model")
        model = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    out, parts = Path(argv[0]), [Path(p) for p in argv[1:]]
    prompt = "\n\n".join(p.read_text(encoding="utf-8") for p in parts)
    out.unlink(missing_ok=True)
    codex = shutil.which("codex")
    if not codex:
        sys.exit("codex not on PATH")
    cmd = [codex, "exec", "-s", "read-only", "--skip-git-repo-check", "-o", str(out)]
    if model:
        cmd += ["-m", model]
    cmd.append("-")
    log = out.with_suffix(".log")
    with open(log, "w", encoding="utf-8") as fh:
        r = subprocess.run(cmd, input=prompt.encode("utf-8"), stdout=fh, stderr=subprocess.STDOUT)
    ok = out.exists() and out.stat().st_size > 0
    print(f"{out}: rc={r.returncode} {'ok' if ok else 'NO OUTPUT'} (log {log})")
    return r.returncode if ok else (r.returncode or 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
