# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (tour + first verdict round done; graphics redraws: 165 rows
  in `gfx/labels.tsv`, most graphics-text rows English; minigame panels, 4218 and the re-tour still to do).
  Last build: 2026-11-20 `build/sakuranote_en.nds` (default en build), sha1 5238a2aa3b8882e620c2587e566c34e1f1c78349,
  romcheck ok, check ok; status_menu/newexp_menu/item_desc/name_boy/cat/dog warped ok on the 6bdfc0e build.
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
  - Phase 5 so far (`docs/re/vwf.md`): dialogue VWF = hook on the advance function 0x02037A00 (new arm9 autoload
    block at 0x021D6540, arena-lo raised); hand-drawn glyphs `fonts/vwf_glyphs.txt` in font 860 (Latin at the
    name-entry codes 0xB0-0xFD, rest at 0x680+); speaker tags (2610, index = header word0) drawn from 8x8 font 872 by a
    replacement tag loop with VWF widths, tags packed two codes per u16 so 18 chars fit the game's 10-u16 copy.
    `build.py` modes: default (en), `--marker`, `--identity`, `--qa ID=TEXT`. Grown message files load fine.
    `tests/test_vwf.py`. Debug probes: `tools/debug/glyphlog.lua` (every glyph: ctx, font, code, x, y),
    `reglog.lua`, `ramdump.lua`. Dialogue budget measured: 228 px/line, 218 on a page's last line, 2 lines/page.
  - Phase 5 width gate (`docs/re/boxes.md`): `build.py --qa ID=@W` / `@W1,W2` / `@WxN` fills a line to exactly W px
    with `|` at both ends, `--qa-file tools/qa/gateN.tsv` for a batch (arm9 slots too). Measured: dialogue 228/218,
    tag 18 codes, narration 240 x 7 lines centred (line 6 <= 190 on 6-7 line pages), popup buttons 164, popup and
    save-message panel 216, board 216 / buttons 164, chapter card 200 (line 2 stays blank), items 216 x name +
    blank + 5, NEWEXP rows 164, profile 228 (header 128), credits 120 (fixed per-line x). Glyph torture line ok in
    the dialogue font; tag font: `)` = stop byte 0xFD (rejected by `vwf.pack_tag`, tested), `:;` odd glyphs. New
    scenes: intro_narration, status_menu, newexp_menu, item_desc (fixture `all_items`: state +0x120..0x12F = item
    bits, found with `tools/debug/poke.lua`). Marker sheets: the only Japanese left is graphics (name-entry
    prompts, status/NEWEXP panels: all in `docs/re/graphics.md`), save data names, and debug-only labels (2612).
  - Phase 6 translate: 37 batches (`tools/batches.py split|check|merge`), translated by `codex exec`
    (`tools/tl_run.py`, brief `docs/translator-brief.md` + style reference + synopsis + per-batch glossary rows) and
    reviewed by `codex exec` read-only (`tools/review_run.py`, `docs/reviewer-brief.md`). Dispositions:
    `docs/review-log.md`. Checker fixes: chapter cards treat full-width-space JP lines as blank, and cards/credits
    take the JP line count as the cap (2613:45-60 have 4 lines with END); `tests/test_batches.py`.
    Phase 6 review fix: `tools/review_run.py` exits 1 on a failed reviewer run (nonzero codex exit, missing or
    malformed report); `tests/test_review_run.py`.
  - Phase 7 checks (`docs/re/checks.md`): `tools/romcheck.py` audits the build leaf by leaf (header fields, arm7,
    overlays, banner, NitroFS files, arm9 sections + `romdiff.check` with the write log, branch-into-hook scan,
    FILEDATA entries, font cells, every message string decoded back to its script English with the JP's control
    codes and the width lint, no Japanese left outside status `data`); every fixed-binary write goes through
    `tools/writelog.py` (`build/<out>.writes.txt`); `tests/test_romcheck.py` builds its own ROM and tampers with it.
    Text lint gained label-form blank matching and stub last lines. Credits (`docs/re/credits.md`): x per entry
    is a `mov r2` immediate in overlay 1; `tools/credits.py` re-centres all 76 from the English width (cap 224);
    "Marvelous Entertainment" restored. arm9:0941C0 (full default name "Toru K.") has no pointer: the game
    composes the full name, so it is never shown. Cat = Traumerei, dog = Reinhold (set_name index 3/4, name_cat
    shot). Chapter card line 2 as ASCII spaces renders fine (chapter1_card shot). New probes in `tools/debug/`:
    `callerlog.lua`, `writerlog.lua`, `oamlog.lua`.
    Phase 7 review fixes: romcheck confines every logged arm9 write to `romcheck.arm9_allowed()` (string slots,
    hook sites, arena literal; fixed independently of the log) and checks each credits write is exactly one
    `mov r2, #x` with the centred x; the build centres credits on the text it inserts (QA overrides, marker).
  - Phase 8 so far: tour = `warp_all.py build/sakuranote_en.nds --out work/qa/tour` + the same on the original
    into `work/qa/tour_jp` (`--no-states`), then `tools/tour_cmp.py` -> `work/qa/tour_cmp/<scene>_sheet.png`
    (English | original). Gate: `qa_gate.py init work/qa/manifest.tsv work/qa/tour_cmp --build
    build/sakuranote_en.nds`, `todo ... --size 8 --out-dir work/qa/chunks`, verdicts by `tools/vqa_run.py CHUNKS`
    (`codex exec` read-only with the sheets attached; brief `docs/visual-qa-brief.md`) into `work/qa/verdicts/`.
    Save fixtures now carry the English default names (`make_save.en_names`; the debug warp left kana names).
    Graphics: `tools/gfx.py` + `gfx/labels.tsv` + `docs/re/gfx.md` (cell codec in palette indices, lettering with
    the project's VWF glyphs, applied by the build, audited by romcheck; `tests/test_gfx.py`).
    Redraws (2026-11-20, details in `docs/re/gfx.md`): fixed the RECN transfer-offset bug (tabs were scrambled),
    added BG screens (RCSN), shared-tile guard, styles shadow/outline/bold, fills index/@X/~T/~T/D/=, `gfx.py dump`.
    English now: pause tabs Ch. 1-4 (4187/4192/4194), status 1040, Key Items 1020-1035, NEWEXP panel 1017,
    collection banner 1000-1015, name-entry prompts 988/991/994, banners New Episode! 4052/4056 and New
    Experience 4060-4068, choice buttons 4044, 85 choice labels 4033, Tears message 4028, map labels 1046.
- **Next:**
  1. Phase 8 graphics left: minigame panels 70-106 (15-puzzle, ramen, Nasukaiser: `docs/re/graphics.md` rows;
     look with `gfx.py cells`/`dump`, add rows, `gfx.py preview`), collection sprite 4218 (8bpp linear 0x101:
     `obj_pixels` asserts 4bpp, add 8bpp), 2842 (three 8x8 glyphs from a shared tile, not ゴミ箱 as the sweep
     guessed: find where it shows before redrawing). Title logo 1139 stays Japanese (D5). The 4033 choice labels
     were translated without scene context (no script reference): check them when their scenes are toured.
     Then a cold-boot tour of all scenes (`warp_all.py` on the new build, `tour_cmp.py`, `qa_gate.py init`,
     `todo`, verdicts with `vqa_run.py`), then `inkbox.py` on every choice/centred box (popups, save confirm,
     episode confirm), stress saves (longest names `WWWWWWWWW` via `save.py edit --name`, full item grid =
     `all_items`), `textcover.py` (needs a `TEXT` log from the message hook and `build/strings.tsv`).
  2. Title menu arm9:092798 shows "Start" (slot: 5 chars). Its one pointer is the literal at arm9 0x0207F28C: if
     the title screen wants "New Game", put the string in the VWF autoload block and repoint that literal (log the
     write). Decide when the title screen is in the tour.
  3. The glossary lint skips `## Guidance` rows, so variant spellings slipped through there (Okashita, Pitchy...;
     swept by hand, see review-log). A phase 8 story pass should grep EN against Guidance rows too.
  4. Width rows still **guess** (not reached by any warp): 2609 track names (player-facing list, probably an
     extras/special episode), 2615:0 touch prompt, 2616 tutorial (Nobiyo; presumed dialogue box without tag),
     2607:0/5 save/load prompts (same panel as the measured save messages), 2613:67-81 (same board panel, need
     unlock flags). Reach them in phase 8 and re-measure; translators keep these short meanwhile.
  5. `docs/polish.md`: profile bullet indents (2611:31, 59-75).
  6. Phase 8 stress saves: map more of the 0x28-0x9A0 state (hearts, flags, per-item bits) by diffing saves.
- **Open bugs:** visual-QA round 1 (7 not ok, all graphics text): name_boy/cat/dog, status_menu, item_desc and
  newexp_menu are redrawn now (need the re-tour + new verdicts); title (logo 1139) stays Japanese by D5: waive it
  with that reason in the next round. Name entry opens on the kana tab (the abc tab exists): non-blocking, see
  Waiting on the user. extras_list = debug-only, ok in `verdicts/recheck_1.tsv`.
  Flagged abbreviation (D4 last resort): pause tabs "Ch. 1".."Ch. 4" (37 px tab, "Chapter 1" = 46 px).
- **Notes for later phases:**
  - 2612 (debug labels) and 2614 (message test) are status `data`: not translated. Speaker for `hdr` word0 = 2610
    index (verified): give translators the speaker name from 2610 as context.
  - English letters share the name-entry codes, so the name-entry key cells now show left-aligned VWF Latin (big
    font): check the name-entry screen in phase 8 and re-centre if needed.
  - arm9 default names (20-byte slots, 9 chars + FFFD; the save's name fields are the same size, so 9 is the real
    limit) and `はじめから` (14 bytes): in place. Pointers: names from 0x02035F18 (set_name 1-4), はじめから from
    0x0207F28C; the full-name slot 0x020941C0 has none.
  - The debug menu's オープニング item shows nothing; the title/opening is reached by normal boot instead.
  - The field save screen (save_slots/save_confirm) and file select show graphics/font text: in the phase 8 tour.
- **Waiting on the user:**
  - (non-blocking) Name entry opens on the kana keyboard tab; English players can switch to the abc tab. Default:
    leave the game's default tab (changing it is engine work); default names are already English.
  - (non-blocking) Small scenery signs in background art (コンビニ, 寿司, たばこ, ゆ, restroom 女 ...; ids in
    `docs/re/graphics.md`): default is to leave them as art and translate only signs the story refers to.
