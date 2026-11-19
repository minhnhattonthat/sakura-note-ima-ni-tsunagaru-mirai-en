# Name entry and player names

Found 2026-11-20 (phase 8 stress saves) with `tools/debug/readlog.lua`, `writerlog.lua`, `ramdump.lua`; patch in
`tools/namefield.py` (D13), test `tests/test_namefield.py`.

## Name-entry screen (FILEDATA 984 key sheet, 2482 = key-neighbour table, not a script)

Code in arm9 0x020794D0-0x02079BD4. Object (r4 in the handlers; 0x021E6F58 in a cold-boot run):
- +0x428: 10 u16 font codes, FFFD = empty cell. +0x448: cursor index. +0x43C / +0x444: field canvas and its size.
- 0x02079898 load: copies the stored name until FFFD (at most 10), cursor = min(len, 5). 0x02079970 store: copies
  all 10 cells back.
- 0x020795E0 key press: buf[cur] = code, buf[cur + 1] = FFFD, cur++ while cur < 5 (`cmp r0, #5`).
- 0x020794D0 Backspace (r1 = 0x3E8): at cur == 5 with a letter there, clear it in place; otherwise cur--, clear.
- 0x02079B88 redraw: clears the canvas, then for i in 0..9 draws every cell that isn't FFFD at x = i * 16
  (0x02079B38 -> 0x02036478), so a cell past the terminator is still drawn. The canvas shows 7 cells (112 px).
- 0x02079A98 cursor sprite: x = (cur * 16 + 0x50) << 12.

Original: 6 characters. The English defaults (Kurosawa, Traumerei, Reinhold) are 8-9 letters, so the field showed
"Kurosaw", and Backspace from the cap left a stale letter. Patched (D13): cap 8 (9 characters, the save field's
size: 0x14 bytes = 9 codes + FFFD), pitch 12 px (9 cells = 108 px), cursor x to match. Kana typed on the kana tab
touch at 12 px; Latin fits with a gap.

The keys: tab bar at bottom-screen y 39 (L / R buttons also switch tabs); key row 1 at y 63, rows 20 px apart,
columns 16 px from x 12; BackSpace (20,160), Enter (230,160).

## Name record and substitution

The entry stores into the live name record at **0x021BC4CA**: surname, given name, field 3, field 4, 0x14 bytes
each (the save struct 0x021C0830 + 0x2A4 gets a copy when the game saves). Variables: `{var_F0}` surname,
`{var_EF}` given name, `{var_ED}` / `{var_EE}` the pets (docs/re/text.md). The text engine substitutes the whole
name: a forced 9 x W name prints in full in dialogue ("Welcome home, WWWWWWWWW."), in the episode-board header
and in the profile header, although the Japanese reserves 6 cells (var + 5 `{slot}`). The lint therefore
counts a drawn name as 72 px (9 x W; `tools/batches.py` NAME_PX).

## File select / load popup / save screen name line

Builder 0x0207F290 (r0 = file-select object, r1 = slot): fills a 20-cell field at +0x212C with FFF9 (colour),
the surname, 000F (gap), the given name (each at most 10), then FFFD only below cell 20. The text engine copies it
into a 40-byte heap block. 9 + 9 letters fill all 20 cells with no terminator: the copy runs into the words after
the field (live data) and past the heap block, and the name vanished. Patched (D13): the given-name loop stops at
cell 18 (`cmp r1, #18`), so cell 19 is always FFFD. A 9-letter given name after a 9-letter surname loses its last
letter on this line only.

## Stress scenes (tools/debug/scenes.tsv, all `stress_*`)

`stress_names` fixture (`make_save.py`): every item, chapters 1-4, all four names 9 x W. Scenes: file select,
load popup, episode board, STATUS (full Key Items grid), item description, NEWEXP, field save screen; plus
`stress_dialogue` and `stress_profile`, which force the names in RAM with the warp token `names:C6:9`, and
`stress_name_entry` (9 W typed). Not covered yet: a full NEWEXP list (its unlock flags are unmapped; the 2608
rows are width-linted with the 72 px name).
