# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract next (phase 3 identity build done: byte-identical ROM, test in check). Last build:
  2026-11-19 identity build, sha1 911782fa06c3006cd66818914c7684d6422d200c (= the dump), smoke ok.
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
  - Phase 2 saves (`docs/re/save.md`): game saves at field SAVE points (23 map scripts). Slot n copy k at
    0x20 + (2n+k)*0xA00, u16 checksum at +0x9FE = ~bytesum(image[0:0x9A0]); image = RAM state struct 0x021C0830.
    0x16C = chapter-tab bitmask, names at 0x2A4.. `tools/debug/make_save.py` builds the game-written fixture
    `s1_living` (debug warp to the living room 1232, walk to SAVE, save) and `all_chapters` (0x16C=0xF);
    `tools/debug/save.py show|edit` fixes both copies + checksum; edited saves load with no error. New scenes (6th
    column `save` in scenes.tsv): file_select_used, load_popup, episode_ch2-4, chapter2-4_card, save_slots,
    save_confirm. `tools/debug/maplist.py` -> `docs/re/maplist.tsv` (every debug map-list row -> files loaded).
    warp.lua token `hKEY:N` holds a key. 40/40 scenes ok on the original ROM. `tests/test_save.py`.
  - Phase 3 identity (`docs/re/filesystem.md`): `tools/build.py` unpacks FILEDATA, repacks it keeping each entry's
    original (non-zero) alignment pad bytes, rebuilds NitroFS with ndspy and restores 0x1000-0x1003 + the 0xFF tail.
    Output equals the dump; `tests/test_identity.py` (FILEDATA, whole ROM, resized-entry alignment). Edits go in
    `build.edit_payloads()`. Room to grow: the ~1.65 MiB 0xFF tail (dump is the full 64 MiB cart).
- **Next:**
  1. Phase 4: extract the 122 message files (2495-2616) to `script/` JSON with a roundtrip test; fix the 2604
     credits mapping first (see notes below).
  2. Phase 8 stress saves: map more of the 0x28-0x9A0 state (items, hearts, flags) by diffing game-written saves.
- **Open bugs:** none.
- **Notes for later phases:**
  - Message files 2604 (credits) and 2612 (debug labels) decode to `[00xx]` codes with `jp.tbl` though the credits
    read as Japanese on screen: another font/mapping. Fix before extracting 2604 (phase 4). 2612 needs no translation.
  - The debug menu's オープニング item shows nothing; the title/opening is reached by normal boot instead.
  - The field save screen (save_slots/save_confirm) and file select show graphics/font text: in the phase 8 tour.
- **Waiting on the user:**
  - (non-blocking) Small scenery signs in background art (コンビニ, 寿司, たばこ, ゆ, restroom 女 ...; ids in
    `docs/re/graphics.md`): default is to leave them as art and translate only signs the story refers to.
