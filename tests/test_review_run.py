"""review_run.py: a failed reviewer run (nonzero exit, missing or malformed report) fails the runner; findings don't."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import review_run  # noqa: E402

GOOD = "### Critical\nnone\n### Important\n- 2500:3 wrong name\n### Minor\nnone\n### Assessment\nNeeds fixes.\n"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    tl = tmp_path / "tl"
    tl.mkdir()
    (tl / "b999.tsv").write_text("2500:3\tjp\t-\t-\tctx\n", encoding="utf-8")
    (tl / "b999.out.tsv").write_text("2500:3\tEN line\n", encoding="utf-8")
    monkeypatch.setattr(review_run, "TL", tl)
    monkeypatch.setattr(review_run, "REV", tl / "review")

    def fake(rc, report):
        def run(argv):
            if report is not None:
                Path(argv[0]).write_text(report, encoding="utf-8")
            return rc
        monkeypatch.setattr(review_run.codex_run, "main", run)
    return fake


@pytest.mark.parametrize("rc, report", [
    (1, None),                                     # reviewer failed, no report
    (0, None),                                     # exit 0 but no report
    (0, ""),                                       # empty report
    (0, "Sorry, I could not review this."),        # no headings
    (0, GOOD.replace("Needs fixes.", "")),         # Assessment empty
    (1, GOOD),                                     # report written but run failed
])
def test_failed_run_fails(sandbox, rc, report, capsys):
    sandbox(rc, report)
    assert review_run.main(["b999", "--jobs", "1"]) == 1
    assert "FAILED" in capsys.readouterr().out


def test_review_with_findings_succeeds(sandbox, capsys):
    sandbox(0, GOOD)
    assert review_run.main(["b999", "--jobs", "1"]) == 0
    assert "b999\t0\t1\t0\tNeeds fixes." in capsys.readouterr().out


def test_summary_flags_invalid(sandbox):
    sandbox(0, GOOD)
    review_run.main(["b999", "--jobs", "1"])
    assert review_run.main(["--summary"]) == 0
    (review_run.REV / "b999.md").write_text("", encoding="utf-8")
    assert review_run.main(["--summary"]) == 1
