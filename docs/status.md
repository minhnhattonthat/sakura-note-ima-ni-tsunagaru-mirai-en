# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9. Release done (2026-11-20): `release/Sakura_Note_Ima_ni_Tsunagaru_Mirai_EN_v1.0.zip` built and
  verified by `tools/release.py` (every gate ok, log `work/release_v1.0.log`). Published 2026-11-20 at the owner's
  request (D14): repo public, GitHub release v1.0 (tag on babc2bd) with the zip, sha256 42a4ee1b...dadc5e0.
  Next: player bug reports (`gh issue list --label bug`).
  Build: `build/sakuranote_en.nds` sha1 4c19bf46780c9bda5254a2e0e74ef78c8beb8844, patched CRC32 DB61296F; patch
  `Sakura_Note_Ima_ni_Tsunagaru_Mirai_EN_v1.0.xdelta` 199,649 bytes, re-applied to the clean dump = build.
  Gates on this build: visual tour 57/57 (re-toured, 6 changed sheets re-verdicted ok), story pass 13/13, textcover
  5,254/5,343 shown, 89 waived, 0 failing, jp_scan 0 runs, polish all ticked, debug scripts 2477/2494 untouched.
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
    Second graphics session (2026-11-20, `docs/re/gfx.md` §Findings): minigames reached from the debug イベント
    list (new scenes `puzzle_info`, `puzzle`, `nazkaiser_info`): puzzle frame 70 "B Button: Back", puzzle panel 73,
    Nazkaiser controls 106; NEWEXP bottom box 4218 (8bpp sprites now supported). `gfx.py` gained `~-T` (dark
    letters), `~hT` (warm letters), `^DX,DY` (offset copy), style `big`, per-tile sub-palettes for 4bpp inpaint;
    `tools/gfxprobe.py` reads a region's indices and text lines. Ramen panels 80-91 and 2842 (ナナミ) are unused
    (D12); the Nazkaiser logo 109 stays Japanese like the title logo (D5).
    Re-tour 2026-11-20: 47/47 scenes on the build, sheets in `work/qa/tour_cmp`, verdicts round 2-3 by codex
    (`work/qa/verdicts/`), `recheck_2.tsv` = name entry kana keyboard ok by D11. `inkbox.py` on newgame_popup,
    save_confirm, load_popup, episode_ch1_confirm: every button and line centred within 2 px; the popup title bar
    text sits 12 px right of the bar centre in the original too (the game's own layout, not a bug).
  - Phase 8 stress saves (2026-11-20, `docs/re/nameentry.md`, D13): the name entry capped names at 6 characters
    while the English defaults are 8-9 letters (field showed "Kurosaw", Backspace left a stale letter).
    `tools/namefield.py` (applied by the build, allowed by romcheck, `tests/test_namefield.py`): cap 9 (the save
    field's size), 12 px cell pitch, cursor x to match; the file-select name line builder (0x0207F290) no longer
    loses its terminator with 9 + 9 letters (the name vanished and the copy overran a heap block). Fixture
    `stress_names` (all items, chapters 1-4, names 9 x W) and 10 `stress_*` scenes (file select, load popup,
    episode board, status grid, item description, NEWEXP, save screen, dialogue, profile, name entry); warp.lua
    token `names:C6:9` forces names in RAM (name record 0x021BC4CA). Long names print in full in dialogue,
    board header and profile. Lint `NAME_PX` 40 -> 72 (9 x W); 10 lines re-worded (review-log). Shots in
    `work/qa/stress/` all looked right by eye (not yet through the gate).
  - Text coverage plumbing: `tools/debug/textlog.lua` hooks the text engine's expand routine 0x0203764C (r1 =
    string body) and logs `TEXT <hash>`; `tools/textcover_keys.py` writes `build/strings.tsv` (5,343 keys, every
    default build regenerates it); `warp_all.py --script tools/debug/textlog.lua` adds the probe to every run.
    Keys verified against an in-game log (2499:0, 2612 labels). Baseline 2026-11-20: the 58 warp scenes show
    64/5,343 strings (`work/qa/cover.txt`).
  - Text coverage runners (2026-11-20, `docs/re/scripts.md`): SCR0 script format read; `tools/scrrefs.py` lists
    every (message file, index) a script names (`work/qa/scrrefs.tsv`; 3,355/4,106 dialogue strings; `--unref`
    lists the rest: battle text, GetItem "Got X" lines, Tears, and 16 one-line "Oh, Fugeiji-chan. Hello." files
    no script sets). Runners, logs under `work/qa/cover/<runner>/<run>/log.txt` (+ `final.png` when complete):
    `tools/debug/evcover.py` (every Event(N) target played in the opening map via `warp.lua SWAP='1943:N'`),
    `tools/debug/mashcover.py` (every map-list row x boy/dog/cat, A-mash + walking, NPC object scripts started at
    NearScript by `tools/debug/entryname.lua`), `tools/debug/battlecover.py` (debug battle list x chars x 4
    pages). `work/qa/cover/mash/` = an older plain mash; `work/qa/cover/runs/` = the 58 warp scenes.
    `tests/test_scrrefs.py`. `vqa_run.py` labels stress sheets (single image, scene note from scenes.tsv).
  - Text coverage complete (2026-11-20): `tools/debug/forcemsg.lua` + `tools/debug/forcecover.py` forced every
    string no scene reached through the message fetch of event 1938 (77 runs, all 50/50 forced, exit 0).
    `textcover.py work/qa/cover build/strings.tsv --waive docs/text_unshown.tsv` exits 0: 5,254/5,343 shown, 89
    waived (2612/2614 debug-only, 2610:0-4 placeholders, arm9 default names), 0 failing. Phase 8 done.
  - Phase 9 (2026-11-20): story pass = `tools/pairs.py chapters work/qa/story/chapters` (13 files: 11 story
    segments from the synopsis file map, 12_system, 13_choices = the 4033 buttons) + `qa_gate.py init
    work/qa/story/manifest.tsv ... --glob "*.txt"` + `tools/story_run.py --tag rN` (codex read-only per chapter,
    brief `docs/story-reviewer-brief.md`; reports `work/qa/story/reports/`, verdicts `work/qa/story/verdicts/`).
    Rounds 1-4: Important fixes (Nanami Yoshida / Kikichi Sakura surnames the 2516:8 clue needs, pi/ki bird joke,
    contact pun, 過程/家庭 pun, 4033:71) in `docs/review-log.md` §Story pass; every Minor fixed or waived in
    `docs/polish.md` (all ticked). Re-force after each text change: `forcecover.py --jobs 2` (textcover 0 failing).
    `tools/jp_scan.py`: jp_left.py on every string body + arm9 slot (status data left out, listed in
    work/jp_known.txt): 0 runs on the build, 10,641 on the dump. `tools/release.py` (all gates, xdelta3 in
    `tools/xdelta3/`, gitignored, copied from the upstream 3.1.0 release), `docs/release_readme.txt`, README filled.
- **Next:**
  1. Publishing v1.0 is the owner's call (zip in `release/`). After any fix: rebuild, re-force coverage, re-tour,
     re-run the story pass on changed chapters, then `tools/release.py --version 1.1`.
     The forcing pass draws forced strings in the dialogue box: it proves the engine reaches them, not their own
     screen's layout (that is the width lint + tour sheets). The 4033 choice labels were reviewed as a list
     (13_choices), without scene context; waived wording ideas are in `docs/polish.md` for player feedback.
     Coverage notes (done 2026-11-20): logs in `work/qa/cover/` (runs2 = warp scenes, ev = 48 events, force = 77
     forcing runs, all exit 0). Re-run `forcecover.py --jobs 2` after any text change that adds strings (host
     memory is tight: ~1.3 GB free; `--jobs 2` was fine).
  2. Title menu arm9:092798 shows "Start" (slot: 5 chars). Its one pointer is the literal at arm9 0x0207F28C: if
     the title screen wants "New Game", put the string in the VWF autoload block and repoint that literal (log the
     write). Decide when the title screen is in the tour.
  3. (done 2026-11-20, see 1) The glossary lint skips `## Guidance` rows; a phase 9 story pass may still re-check.
  4. Width rows still **guess** (not reached by any warp): 2609 track names (player-facing list, probably an
     extras/special episode), 2615:0 touch prompt, 2616 tutorial (Nobiyo; presumed dialogue box without tag),
     2607:0/5 save/load prompts (same panel as the measured save messages), 2613:67-81 (same board panel, need
     unlock flags). Reach them in phase 8 and re-measure; translators keep these short meanwhile.
  5. (done 2026-11-20) `docs/polish.md`: profile bullet indents, story-pass Minors; all ticked.
  6. Phase 8 stress saves: map more of the 0x28-0x9A0 state (hearts, flags, per-item bits) by diffing saves.
- **Open bugs:** none from visual QA (gate passes). Flagged abbreviation (D4 last resort): pause tabs
  "Ch. 1".."Ch. 4" (37 px tab, "Chapter 1" = 46 px). Puzzle frame "B Button: Back": two 1-px pale specks may
  remain where sub-palette 2 has no light blue (codex: ok).
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
    leave the game's default tab (changing it is engine work); default names are already English. The kana keys
    and the あいう / アイウ tab labels stay as they are (D11); say if the tabs should read e.g. "Hiragana".
  - (non-blocking) decisions.md had lost rows D9/D10 that the glossary cites; restored from the glossary wording
    (sound effects in natural English; English names for descriptive yokai/NPC names). Correct them if wrong.
  - (non-blocking) Small scenery signs in background art (コンビニ, 寿司, たばこ, ゆ, restroom 女 ...; ids in
    `docs/re/graphics.md`): default is to leave them as art and translate only signs the story refers to.
