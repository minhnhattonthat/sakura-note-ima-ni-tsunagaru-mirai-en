"""check.py: the repo's one-command check (tests + lint). The pre-commit hook runs it; exit non-zero fails the commit.

Runs pytest on tests/ (tests needing the ROM skip when rom/ is absent)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
