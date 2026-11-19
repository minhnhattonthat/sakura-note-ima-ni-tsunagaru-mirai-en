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
- arm9 (u16 codes, FFFD-terminated): 0x0927A4 `はじめから`, 0x0927C4 save date template `--/--/--　--:--`,
  0x0941CE-0x09421C default names クロサワトオル / クロサワ / トオル / トロイメライ / ラインホルト. Pointers not found yet.
- No Shift-JIS or UTF-16 game text anywhere (scan: `tools/sjisscan.py`); overlays and SCR0 scripts hold none.
- Script function names are ASCII (engine identifiers, not shown).

## Text ranges for extraction
- FILEDATA 2495-2616: all strings.
- arm9 0x0927A4-0x0927E0 and 0x0941C0-0x094230.
