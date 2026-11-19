# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (text side done; graphics-text static sweep left). Last build: none yet.
- **Done:**
  - Step 0: repo setup. DeSmuME QA fork in `tools/desmume/`, original ROM smoke boot ok (`work/qa/smoke-orig`), scripted
    start + touch input work, pre-commit rejects a failing test, guard hook blocks `sed -i`, `rom.sha1` pinned.
  - Recon (`docs/re/`): FILEDATA.BIN "LF 2" archive format (`tools/filedata.py`), message files 2495-2616 (u16 codes,
    5,413 strings, `tools/msg.py`), control codes (no args), dialogue font = FILEDATA 860 (`tools/font.py`), full
    `tbl/jp.tbl` (kanji read from font sheets + context) with a passing roundtrip test (`tests/test_text.py`), arm9
    strings and default names, free space (1.65 MiB 0xFF tail).
  - Debug leads for phase 2: SCR0 scripts contain `DebugScenario`, `DbScenario1-4_Boy/Dog/Cat`, `EpisodeSelect_Test`,
    `DbScript_Test` (in FILEDATA 1142 and 2837).
- **Next:**
  1. Finish phase 1: graphics-text static sweep (`docs/re/graphics.md` §To do): render all RGCN + LZ10 RGCN with
     palettes into contact sheets, identify the 177 LZ10 "QQ" blocks, list every Japanese graphic.
  2. Phase 2 debug tool: find how to reach `DebugScenario` / `EpisodeSelect_Test` (script entry from arm9, or a
     Lua RAM hook on the script start), scene list in `tools/debug/scenes.tsv`.
  3. Phase 3: identity repack of FILEDATA (keep original inter-entry padding; `filedata.build()` currently differs).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
