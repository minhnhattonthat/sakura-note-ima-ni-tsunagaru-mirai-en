# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build next (phase 4 extract done: script/ roundtrip + coverage tests).
  Last build: 2026-11-19 identity build, sha1 911782fa06c3006cd66818914c7684d6422d200c (= the dump), smoke ok.
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
  - Phase 4 extract (`docs/re/text.md` §script/): `tools/script.py extract|verify|stats` -> `script/` (122
    `msg_NNNN.json` + `arm9.json`, 5,420 entries: 5,155 todo, 265 `data`). Header words kept as `hdr`; extract keeps
    existing translations/status/notes and lists ids whose jp changed. `tests/test_script.py`: every entry
    re-encodes to the original bytes, each message file is fully covered (table + strings, no gap), and an arm9 +
    overlay scan finds only the 7 listed slots. The old "2604 credits mapping" note was a bug in `msg.py`'s own
    decoder (byte-swapped table keys); fixed, the credits decode fine. Kanji check: 11 misread cells fixed in
    `tbl/jp.tbl` (`docs/re/font.md`), `tools/rarekanji.py` lists the rare cells.
- **Next:**
  1. Phase 5: font/VWF spike (font 860, 16x16 cells, 12 px advance guess) and the marker build: replace every
     todo string with `[id]` markers via `build.edit_payloads()` (message files can grow: offsets are file-relative),
     warp through the scenes, find which box variants exist and measure their widths (width gate). Confirm the
     header-word meanings (speaker/face) and that scripts address messages by index only.
  2. Phase 8 stress saves: map more of the 0x28-0x9A0 state (items, hearts, flags) by diffing game-written saves.
- **Open bugs:** none.
- **Notes for later phases:**
  - 2612 (debug labels) and 2614 (message test) are status `data`: not translated. Speaker names for `hdr` word0
    are not mapped yet (translators get context from the text; map them in phase 5 if the marker build shows them).
  - arm9 default names (20-byte slots, 9 chars + FFFD) and `はじめから` (14 bytes): in-place limits unless phase 7
    finds their pointers. Which of トロイメライ/ラインホルト is the dog and which the cat is a guess.
  - The debug menu's オープニング item shows nothing; the title/opening is reached by normal boot instead.
  - The field save screen (save_slots/save_confirm) and file select show graphics/font text: in the phase 8 tour.
- **Waiting on the user:**
  - (non-blocking) Small scenery signs in background art (コンビニ, 寿司, たばこ, ゆ, restroom 女 ...; ids in
    `docs/re/graphics.md`): default is to leave them as art and translate only signs the story refers to.
