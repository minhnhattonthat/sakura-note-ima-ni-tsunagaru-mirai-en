# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next (phase 1 recon done). Last build: none yet.
- **Done:**
  - Step 0: repo setup. DeSmuME QA fork in `tools/desmume/`, original ROM smoke boot ok (`work/qa/smoke-orig`), scripted
    start + touch input work, pre-commit rejects a failing test, guard hook blocks `sed -i`, `rom.sha1` pinned.
  - Phase 1 recon (`docs/re/`): FILEDATA.BIN "LF 2" archive format (`tools/filedata.py`), message files 2495-2616
    (u16 codes, 5,413 strings, `tools/msg.py`), control codes (no args), dialogue font = FILEDATA 860
    (`tools/font.py`), full `tbl/jp.tbl` with a passing roundtrip test (`tests/test_text.py`), arm9 strings and
    default names, free space (1.65 MiB 0xFF tail).
  - Graphics-text static sweep: `tools/gfxsweep.py` renders all 1,072 RGCN (BG, RCSN screens, RECN sprite cells incl.
    linear 0x101 and per-cell VRAM transfer) into 120 pages; a read-only Codex vision pass (`tools/sweep_review.sh`)
    listed the text: `docs/re/graphics_sweep.tsv`, summary table in `docs/re/graphics.md` (~35 Japanese UI graphics:
    title logo, minigame instructions, name-entry prompts, status/inventory headers, banners, choice sprites 4033/4044,
    chapter tabs). NDS banner title is Japanese UTF-16 (translate at build). QQ blocks = tilemaps (guess).
  - Debug leads for phase 2: SCR0 scripts contain `DebugScenario`, `DbScenario1-4_Boy/Dog/Cat`, `EpisodeSelect_Test`,
    `DbScript_Test` (in FILEDATA 1142 and 2837).
- **Next:**
  1. Phase 2 debug tool: find how to reach `DebugScenario` / `EpisodeSelect_Test` (script entry from arm9, or a
     Lua RAM hook on the script start), scene list in `tools/debug/scenes.tsv` incl. chapter cards, game over,
     ending, credits; add what they show to `docs/re/graphics.md`.
  2. Phase 3: identity repack of FILEDATA (keep original inter-entry padding; `filedata.build()` currently differs).
- **Open bugs:** none.
- **Waiting on the user:**
  - (non-blocking) Small scenery signs in background art (コンビニ, 寿司, たばこ, ゆ, restroom 女 ...; ids in
    `docs/re/graphics.md`): default is to leave them as art and translate only signs the story refers to.
