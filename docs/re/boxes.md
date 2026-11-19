# Box variants and width budgets (phase 5 width gate)

Widths in px of the English VWF (`tools/vwf.py text_width`, tags `tag_width`; letters are mostly 6 px with the
1 px gap, `i l . ! : '` 2, `m w M W @` 8). Measured from zoomed shots of `build.py --qa-file tools/qa/gateN.tsv`
builds that fill each box to an exact width (`@W` = a line of exactly W px with `|` at both ends, see
`insert.qa_text`), or of the marker build. Translators get the **Budget** column; the phase 7 lint enforces it.

| Variant | Where (files / ids) | Lines | Budget px | Align | State / evidence |
|---|---|---|---|---|---|
| Dialogue box, bottom screen (tag above line 1) | story files 2495-2603, 2606, speaker header != FFFF | 2 per page | 228 per line; **218 on a page's last line** (page arrow x 235-245) | left, x 14 | measured: `--qa 2499:0` exact 228/218, field_s1_boy, `work/qa/w_dlg/` |
| Speaker tag | 2610:5+ (index = header word0) | 1 | **18 codes** (copy limit); 18 x `M` = 144 px draws clear, no art limit | left | measured: gate1 `2610:6`=18 M, field_s1_boy. Tag font has no `" # $ , [ \ ] ^ _ ` { \| } ~ … — é ♪ ♥`; **`)` is code 0xFD = the packed tag's stop byte: never use it**; `:` `;` draw as Japanese-style dots, `-` as a long dash (gate3) |
| Narration (speaker FFFF), full screen white on black | 2498:0-5 intro, location captions (2498:8), 2500:13, 2502:12 ... | up to **7** per page, top-anchored y 74, 16 px pitch | **240** per line; on a 6- or 7-line page **line 6 <= 190** (page arrow x 224-231 sits on it) | centred on x 127 | measured: gate2 `2498:0-5`, scene intro_narration (`work/qa/gate2/narr/` f003500 7 x 240, f004800 248/120/40 centred) |
| Popup buttons (save / load / new game / delete) | 2607:1-4, 6-12 | 1 | **164** hard (fill touches the green highlight's inner edge both sides); 160 recommended | centred | measured: gate1, load_popup / newgame_popup / save_confirm |
| Popup and save-message panel | 2607:0, 5 (prompts), 2607:13-22 (saving / failed / done) | up to 4 (+ blank lines kept as blank) | **216** (panel inner x 16-238) | centred | measured from marker shots `work/qa/ex/s1/f003000` (2607:14, 4 lines) and f003120 (2607:22); prompts 2607:0/5 not shown on any reached screen, same panel: **guess** |
| Popup header bar / empty-slot label | arm9:092798 (はじめから, the empty save slot's name) | 1 | **5 codes** (14-byte arm9 slot: colour token + 5 + FFFD); bar art is ~220 px wide | centred | fixed slot (save_slots, save_confirm show it). "Empty" fits; anything longer needs the pointer moved (phase 7) |
| Episode board header (top screen + board panel) | 2615:3-18 (chapter + name + arc), 2615:19+ (episode titles, orange) | 1 | **216** (board panel inner x 16-240); top-screen copy has no art limit | centred | measured: gate1 `2615:3`=200, `2615:19`=216 fit, episode_ch1 / episode_ch1_confirm |
| Episode board popup | 2613:66-81 (prompt line + はい/いいえ, はじめる/もどる buttons) | 2-4 | prompt **216**; button lines **164** (same highlight as the popups) | centred | measured on 2613:66 (gate1 216/164/164); 2613:67-81 share the panel but need unlock flags to show: same budget |
| Chapter title card | 2613:25-60 (title, blank, number lines) | 3 | **200** title line (tested width; no box art, wider untested); **line 2 must stay blank** (the episode title 2615:19+ draws over it) | centred | measured: gate1 `2613:29`=200 fits, marker intro run shows the overlap (`work/qa/intro/f005300`) |
| Item name + description | 2605 (`{col_F8}name{n}{n}{col_FC}body`) | name, blank, up to **5** body lines | **216** (panel inner x 16-240) | centred | measured: gate4 `2605:3` 216 x 7 lines, scene item_desc (save all_items) |
| New-experience list row | 2608 (every row; locked rows show 2608:18 ？？？？？？) | 1 | **164** hard (lock icon from x 212); 160 recommended | centred on x 128 | measured: gate2 `2608:18`=180 runs into the lock, gate3 150 = x 53-202, newexp_menu |
| Character profile page (bottom) | 2611:1-75 | up to 10 per page | **228** (lines start x 12; line 6 meets the page arrow at x 241, others reach 248) | left | measured: gate1 `2611:1` 236 x 10, profile_ch1 |
| Profile header (top, beside the portrait) | 2611:76-79 (name / age / job lines after the name variable) | 4 | **128** (x 120 to the screen edge, 8 px margin) | left | measured start x from gate1 profile_ch1 (the fill kept the name variable, so its right end is off-screen) |
| Credits (top screen, scrolling) | 2604 | 1-4 per entry | **224** (widest JP row: 7 sprites). Each entry's x is an immediate in overlay 1 (`docs/re/credits.md`); the build re-centres it from the English width (`tools/credits.py`), and the engine centres each line inside the entry's widest line. Was 120 while x was fixed (88, 96, 92, 112, 72, 20, 100 for 2604:4-9) | centred (x 128 - widest/2) | measured: gate1 2604:3-5 = 60/120/200, credits |
| Sound / music track names | 2609 | 1 | **guess** 200 | ? | not reached: the debug sound test uses its own labels; the player-facing list is probably an extras/special episode (needs unlocks). Reach it in phase 8 |
| Touch prompt | 2615:0 (画面をタッチしてください) | 1 | **guess** 216 | ? | not seen on any reached screen |
| Tutorial (ノビヨ) | 2616:5-89 (FFFF, 2 lines), 2616:0-4 titles | 2 | **guess** 218 (dialogue box, no tag) | ? | not reached; renderer shared with dialogue |
| Save date template | arm9:0927A6 | 1 | 32-byte slot, digits filled by code | - | fixed slot: leave |
| Default names | arm9:0941C0.. | 1 | 9 codes (20-byte slot) | - | fixed slot |

Notes for translators and the phase 7 lint:
- Blank lines in the Japanese (`{n}{n}`, full-width-space lines) are layout: keep them blank (chapter card line 2,
  item description line 2, save messages).
- `{` and `}` cannot be text (they open control tokens).
- All printable ASCII and `…—é♪♥` render in the dialogue font with the right advances (glyph torture line, gate3,
  `work/qa/gate3/dlg/f000700`, `f001200`); double spaces are kept.
