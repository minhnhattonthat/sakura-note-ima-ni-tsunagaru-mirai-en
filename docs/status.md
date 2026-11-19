# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (warps done, 30/30 scenes; save editor and chapter 2-4 cards left). Last build: none yet.
- **Done:**
  - Step 0: repo setup. DeSmuME QA fork in `tools/desmume/`, original ROM smoke boot ok, scripted start + touch input
    work, pre-commit rejects a failing test, guard hook blocks `sed -i`, `rom.sha1` pinned.
  - Phase 1 recon (`docs/re/`): FILEDATA.BIN "LF 2" archive (`tools/filedata.py`), message files 2495-2616
    (`tools/msg.py`), control codes, dialogue font 860, `tbl/jp.tbl` roundtrip test, arm9 strings, free space,
    graphics-text sweep (`tools/gfxsweep.py`, `docs/re/graphics_sweep.tsv`, summary in `docs/re/graphics.md`).
  - Phase 2 warps (`docs/re/debug.md`): exec hook on the FILEDATA entry-open routine (0x0202D158, r4 = id) swaps the
    boot script 2477 for the leftover debug script 2494 = the developers' debug menu (scene/map warp per scenario 1-4
    and boy/dog/cat, battles, BG/OBJ viewers, sound test, ending, game over, extras/profile pages). No ROM change.
    `tools/debug/warp.lua` (key program with waits on file loads), `tools/debug/scenes.tsv` (30 scenes: title, file
    select, new-game popup, name entry x3, episode board, chapter 1 card, debug menu, fields s1-s4 boy + s1 dog/cat,
    battle, viewers, sound, game over, ending, ending stills, credits, extras, profile), `tools/debug/warp_all.py`
    (runs all, checks WARP_OK, shots `work/qa/scenes/`, states `work/states/<scene>.dst`): 30/30 ok on the original
    ROM. `tools/debug/fileid.lua` logs every file load. Every warp boots with a blank 0xFF EEPROM (`--sav`
    work/saves/blank.sav, generated), never the emulator's shared Battery file.
- **Next:**
  1. Finish phase 2: `tools/debug/save.py`. Get a game-written save with data (find where the game saves: likely
     the episode board or the end of an episode; try warping to `chapter1_card`, play the episode with a `--mash`
     tour, and diff `<out>/*.dsv` against the empty save a blank EEPROM becomes), map slot layout + checksum (`watch.lua` on the EEPROM write
     routine), edit chapter/flags so the episode board shows chapters 2-4 (chapter cards 2-4 are not reachable yet),
     and prove an edited save loads with no corruption message. Add `episode_ch2..4` / `chapter2..4_card` scenes.
  2. Phase 3: identity repack of FILEDATA (keep original inter-entry padding; `filedata.build()` currently differs).
- **Open bugs:** none.
- **Notes for later phases:**
  - Message files 2604 (credits) and 2612 (debug labels) decode to `[00xx]` codes with `jp.tbl` though the credits
    read as Japanese on screen: another font/mapping. Fix before extracting 2604 (phase 4). 2612 needs no translation.
  - The debug menu's オープニング item shows nothing; the title/opening is reached by normal boot instead.
- **Waiting on the user:**
  - (non-blocking) Small scenery signs in background art (コンビニ, 寿司, たばこ, ゆ, restroom 女 ...; ids in
    `docs/re/graphics.md`): default is to leave them as art and translate only signs the story refers to.
