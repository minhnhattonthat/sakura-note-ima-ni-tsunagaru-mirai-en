# Debug tool (phase 2)

## How the warp works - verified (original ROM, `tools/debug/warp_all.py`, 29/29 scenes)
- **FILEDATA entry open:** arm9 routine around 0x0202D140-0x0202D188 opens one FILEDATA.BIN entry: r4 = entry id,
  seeks the file handle at 0x020AF4E8 to `0x10 + id*8` and reads the {offset/4, size} pair. An exec hook at
  **0x0202D158** sees every load (`tools/debug/fileid.lua` logs them; works under JIT on the QA fork).
- **Boot script:** at frame ~12 the game opens 2626 (common script library: Event, FlagOn, FadeIn ...) then **2477**
  (StartScript = logos, title, file select; also holds `Credit`). Setting r4 = **2494** at that hook swaps in the
  leftover debug script, whose StartScript draws the developers' **debug menu** (loads 2612, the debug-font labels):
  シーン / バトル / ＢＧ / ＯＢＪ / サウンド / オープニング / エンディング / ゲームオーバー / イベント / おまけ.
  The menu wraps (up from シーン = おまけ). No ROM change; the release build is untouched.
- Other debug scripts: 1142 and 2837 (`DebugScenario`, `DbScenario1-4_Boy/Dog/Cat`, `EpisodeSelect_Test`) start
  on the same boy/dog/cat select; 2494 is the complete one (adds DebugBattle/Bg/Obj/Sound/Event/Map).

## Debug menu items (what each reaches)
| item | result |
|---|---|
| シーン | boy / dog / cat select (left/right), then シナリオ1-4, then a paged map list (ページN, right = next page); A warps into the map with its scenario state (scenario 1 starts the opening dialogue in front of the house) |
| バトル | player select, then a paged battle list (シンシャーボーク, ミテソン ...); A starts the battle |
| ＢＧ / ＯＢＪ | BG and sprite viewers |
| サウンド | BGM / ambient / SE / stream / voice test lists |
| オープニング | nothing visible (black, back to the menu): the opening may need data the debug path skips - **guess** |
| エンディング | ending sequence: petal wall on top, ending stills on the bottom (files 145-149 at start, then 112-144 in groups of 3 every ~1,080 frames); from frame ~13,500 the **staff roll** scrolls on the top screen as font text from message file **2604** (scene `credits`) |
| ゲームオーバー | game over screen |
| イベント | per-chapter extras list (第一章 おまけ1-3 ... 第四章); A opens the character profile page |
| おまけ | player select (extras for boy/dog/cat) |

Debug labels (file 2612) are never shown to players: not translated. **Note for phase 4:** `msg.py dump` of 2612
and of the credits file 2604 prints many `[00xx]` codes and wrong kana, though the credits on screen are readable
Japanese: these files use another font or code mapping than `jp.tbl` (the roundtrip test passes because `[XXXX]`
escapes re-encode). Find the font the credits use before extracting 2604.

## Normal flow (no swap)
Title (1139) → START → file select (1126) → A on slot 1 → はじめから popup (2607) → A → name entry (984; Enter key
= touch 230,160): boy surname, given name, dog (994), cat (991) → episode board for chapter 1 (2615, header
第一章 トオル編 いつもと同じ日常) → A → "start this episode?" → A → chapter card + intro (2630 EpisodeStart).
Script 2478 holds `Chapter1-4` and `DisplayIntro` (the profile page); 2627 `GameOverScript`; 2630 `EpisodeStart`.

## Saves
32 KiB EEPROM (`.dsv` = raw + DeSmuME footer). A game-initialised save with no slots used: header 0x00-0x40, six
0x18-byte blocks at 0xA28 + n*0xA00 (3 slots x 2 copies, **guess**). A blank all-0xFF EEPROM is initialised to
exactly this (verified byte-equal), so `warp_all.py` boots every warp with a generated `work/saves/blank.sav`. DeSmuME's own `tools/desmume/desmume-qa/Battery/*.dsv` is shared between runs: never rely on it.
Slot layout, checksum and `save.py`: **not done** (needs a save written in game: find where the game saves).
