# Text engine

## Encoding - verified
u16 little-endian codes. 0x000-0x662 = cell of the dialogue font (`font.md`), 0xFF00-0xFFFF = control codes.
`tbl/jp.tbl` holds it in `tbl.py` form (key = the code's two bytes little-endian, e.g. あ = 0x0010 -> `1000`).
Verified: every one of the 5,413 strings decodes with no unknown code and `encode(decode(x)) == x`; the player's
default surname クロサワ is stored in RAM 0x020941C0 as the same codes (0x67 0x8A 0x6A 0x8B); decoded strings read
as natural Japanese across all files (kanji duplicates resolved by context, see `font.md`).

## Message files - verified (`tools/msg.py`)
FILEDATA 2495-2616 (122 files). Layout: u32 offset table (first offset / 4 = string count), then the strings back to
back; every string ends with 0xFFFD. Offsets are file-relative bytes, so strings can grow freely when the file is
rebuilt (no external pointers into the strings found yet: scripts call `SetMessageFile` + message index - **guess**,
confirm in phase 4/5 with a marker build).

Dialogue strings start with a 2-word header: word0 = speaker (small number, 0x00FF, 0xFFFF = none, or 0xFF00-0xFF2D
in list files such as 2610), word1 = expression/voice (0x00FF = none). Narration: `FFFF 00FF`. List/menu files (2604,
2605, 2610-2613...) also use it. **guess** for the meaning of the values; the split is consistent (5,413/5,413 strings
have either a header or start with a control code).

## Control codes - no arguments (verified: the next word is always ordinary text, a code, or FFFD)
| code | name in jp.tbl | meaning (guess unless noted) | count |
|---|---|---|---|
| FFFF | `{n}` | newline (verified from layout of decoded lines) | 5855 |
| FFFE | `{page}` | page break / wait for input | 97 |
| FFFD | `{end}` | end of string (verified) | 5413 |
| FFF4 | `{sp}` | narrow space / separator (塔内{sp}第一階層) | 544 |
| FFE2 | `{slot}` | one character slot of a variable; follows FFED-FFF0 x5 | 2330 |
| FFED, FFEE, FFEF, FFF0 | `{var_..}` | name variables (player given name before ちゃん/くん, surname, pet names) | 99/49/296/23 |
| FFF5, FFF6 | `{num_..}` | number printing in debug screens (file 2612) | 28/52 |
| FFF7-FFFC | `{col_..}` | colour on/off: FFF8/FFFA before animal speech "(...)" translations, FFF9...FFFC around keywords in 『』 | |
| FF00-FF2D | `{spk_..}` | speaker values used as header word0 in name/list files | |

## Text outside the message files
- arm9 (u16 codes, FFFD-terminated): 0x092798 `はじめから`, 0x0927A6 save date template `--/--/--　--:--`,
  0x0941CE-0x09421C default names クロサワトオル / クロサワ / トオル / トロイメライ / ラインホルト. Pointers not found yet.
- No Shift-JIS or UTF-16 game text anywhere (scan: `tools/sjisscan.py`); overlays and SCR0 scripts hold none.
- Script function names are ASCII (engine identifiers, not shown).

## Text ranges for extraction - verified (`tests/test_script.py`)
- FILEDATA 2495-2616: all strings. Each file is exactly its offset table + its strings back to back (no gap bytes),
  and no string holds a second FFFD.
- arm9: 7 slots, `tools/script.py` `ARM9_SLOTS`: 0x092798 `{col_F7}はじめから` (14 bytes), 0x0927A6 save date
  template (32), 0x0941C0/D4/E8/FC/0x094210 default names (20 bytes each, zero-padded). A scan of arm9 + all
  overlays for FFFD-terminated runs of table codes finds exactly these (test). Earlier notes said 0x0927A4: the
  string starts at 0x092798.
- Every message string has the 2-word header (5,413/5,413: word1 is 0x0C-0x27 or 0x00FF). `script/` keeps it as `hdr`.

## script/ (phase 4, `tools/script.py`)
One JSON per message file (`msg_NNNN.json`) + `arm9.json`; fields id, hdr, jp, en, max (arm9 slots), status, notes.
`verify` re-encodes hdr + jp + FFFD to the original bytes for every entry. status `data` (265 entries, never
translated, inserted as the original bytes): 2612 debug labels, 2614 the developers' message test, 2613:0-22 (a copy
of the 2612 labels at the head of the system-text file), and strings with no Japanese at all (72 empty strings in
2607, `NO DATA`, page counters `1/8`, `%`, number formats). 2613:23+ is real system text: item-get line, chapter
board (第一章 {var}編), episode start/continue prompts, save prompts.

File contents (first lines read, guess where not played): 2495-2603 scene dialogue (one file per map/event; the
one-string files 2497, 2504, ... `あら付迎字ちゃん/こんにちは` look like per-chapter placeholders), 2604 credits,
2605 item names + descriptions, 2606 story text, 2607 save/load menu, 2608 map names, 2609 sound test track
names, 2610 name entry, 2611 character profiles, 2613 system text, 2615 touch/help prompts, 2616 how-to-play.
