# Save file (EEPROM) - phase 2

Tools: `tools/debug/save.py` (show / edit), `tools/debug/make_save.py` (fixtures), `tests/test_save.py`.

## Where the game saves - verified
Field **save points** (a SAVE sign object, `SpawnSavePoint` in the map script). 23 map scripts spawn one:
1225 1226 1232 1386 1393 1398 1399 1412 1429 1430 1433 1438 1452 1601 1602 1611 1615 1620 1710 1712 1716 1720
1723. The debug map list (`docs/re/maplist.tsv`, `tools/debug/maplist.py`) reaches them: scenario 1 page 1 row 1 =
自宅リビング (living room, 1232); the living room is also 1398 (s2 p5 r1) and 1620 (s3 p2 r1), with other spawn points.
Touching the sign opens the save screen: slot list, then セーブする / やっぱりやめる. Chapter play by mashing A never
saves (16,000 frames of chapter 1 left the EEPROM as initialised).

`make_save.py` gets a game-written save with no playthrough: debug warp to 1232, A x1000 frames (arrival dialogue),
walk left 50 / down 80 frames, face right, A through the save screen into slot 1 (`work/saves/s1_living.dsv`).

## Layout - verified (game-written save; RAM struct; load test)
- 32 KiB EEPROM. 0x00-0x20 header: "SAKURA NOTE1J." + 0x01, zero padding (arm9 0x0207E4A4 compares 14 bytes).
- Slot n (0-2), copy k (0, 1): image at **0x20 + (2n + k) * 0xA00**, 0xA00 bytes. A save writes both copies.
- **Checksum:** u16 at image+0x9FE = `~(sum of bytes image[0:0x9A0]) & 0xFFFF` (arm9 0x0207E468; builder 0x020817E8
  stores it, loader 0x020824B8 compares it and falls back to the other copy). Game-written values match the formula.
- The builder copies the game state struct (RAM **0x021C0830** while in the field) into image[0:0x9A0] verbatim,
  then writes the slot index at image+8. So any RAM-side field is at the same offset in the image.
- An initialised but unused slot holds only the slot index (image+8) and is all 0xFF elsewhere.

| offset | size | field | proof |
|---|---|---|---|
| 0x000 | 4 | used = 1 | game-written save |
| 0x008 | 4 | slot index 0-2 | builder code |
| 0x00C-0x024 | 4 each | save date: year (2-digit), month, day, weekday, hour, minute, second (host clock) | file select shows 26/11/19 20:43 |
| 0x15C, 0x160, 0x164, 0x168 | 4 each | per-chapter word; 0x20 in the chapter a debug warp started, 0 elsewhere | RAM diff s1/s2/s3 |
| 0x16C | 4 | **chapter tabs on the episode board**, bitmask (bit 0 = chapter 1) | edit 2/4/8/0xF -> tabs 1-2/1-3/1-4 appear; chapter 2-4 cards play |
| 0x2A4, 0x2B8, 0x2CC, 0x2E0 | 0x14 each | names: boy surname, boy given name, dog, cat; u16 font codes (`tbl/jp.tbl`), 0xFFFD end | クロサワ / トオル / トロイメライ / ラインホルト |
| 0x9FE | 2 | checksum | above |

Everything else in 0x28-0x9A0 (play time? hearts, items, story flags) is **not mapped**: map it by diffing two
game-written saves when phase 8 needs stress saves (inventory, longest names: names are 9 codes max by field size,
the name-entry limit is lower - **guess**).

## Load test - verified
`file_select_used` / `load_popup` (fixture s1_living) show the slot name and date; このファイルで冒険する goes to the
episode board with no error message. Edited saves (`all_chapters`: 0x16C = 0xF) load the same way, and the board's
chapter 2-4 tabs (touch 55,16 / 84,16 / 114,16) lead to the chapter 2-4 cards (`chapter2_card` .. `chapter4_card`).
