"""tour_cmp.py: one comparison sheet per scene (English shot | original shot) for the visual-QA gate.

    python -X utf8 tools/tour_cmp.py [--en work/qa/tour] [--jp work/qa/tour_jp] [--out work/qa/tour_cmp] [--zoom 2]

Inputs are warp_all.py outputs (`<scene>.png`, both screens). Writes `<out>/<scene>_sheet.png`; the gate:
    python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/manifest.tsv work/qa/tour_cmp --build build/sakuranote_en.nds
Exit 1 if a scene has no original shot.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--en", default=str(ROOT / "work" / "qa" / "tour"))
    ap.add_argument("--jp", default=str(ROOT / "work" / "qa" / "tour_jp"))
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "tour_cmp"))
    ap.add_argument("--zoom", default="2")
    a = ap.parse_args()
    en, jp, out = Path(a.en), Path(a.jp), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    missing = []
    shots = sorted(p for p in en.glob("*.png") if not p.stem.startswith("sheet"))
    for p in shots:
        q = jp / p.name
        if not q.exists():
            missing.append(p.stem)
            continue
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(p), "--compare",
                        str(q), "--zoom", a.zoom, "--out", str(out / f"{p.stem}_sheet.png")],
                       check=True, stdout=subprocess.DEVNULL)
    print(f"{len(shots) - len(missing)} sheets -> {out}")
    for m in missing:
        print(f"no original shot: {m}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
