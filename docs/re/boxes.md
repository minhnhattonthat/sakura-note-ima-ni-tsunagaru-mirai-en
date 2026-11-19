# Box variants and width budgets (phase 5 width gate)

Widths in px of the English VWF (`tools/vwf.py text_width`, tags `tag_width`). Measure from a zoomed shot of the
marker build or a `build.py --qa ID=TEXT` build that fills the box to the limit exactly; tag each row measured
(shot) or guess. Translators get these limits; the phase 7 lint enforces them.

| Variant | Where (files / ids) | Lines per page | Budget px | State |
|---|---|---|---|---|
| Dialogue box, bottom screen (tag above line 1) | story files 2495-2603, 2606 with speaker header | 2 | 228 per line; 218 on the page's last line (page arrow at x 235-245) | **measured**: `--qa 2499:0` exact 228/218 lines, field_s1_boy, `work/qa/w_dlg/` |
| Speaker tag | 2610:5+ (index = header word0) | 1 | 18 codes max (hard: copy limit); width ~120 guess (box art) | codes measured (`T6` marker showed 18); px guess |
| Popup menu buttons (save/load/new game) | 2607 | 1 | ~170 (green button art x 42-215) | guess from marker shot `work/qa/marker/newgame_popup.png` |
| Popup header bar | arm9:092798 (はじめから), 2615:1-2 | 1 | ? | todo |
| Episode board text | 2615:3+, 2615:19 (orange), 2613:66 | 1 | ? | todo (`episode_ch1_confirm`) |
| Chapter card | 2613:29-30 | 2 | ? | todo (`chapter1_card`, shot was mid-fade: take a later frame) |
| Narration (speaker FFFF) | story files, up to 7 lines (2500:49, 2502:12) | up to 7 | ? | todo: no warp scene shows one yet |
| Item descriptions | 2605 (name {n}{n} text) | 4-6 | ? | todo |
| Profile pages | 2611 | up to 10 | ? | todo (`profile_ch1`) |
| Episode titles / lists | 2608, 2609 | 1 | ? | todo (`extras_list`) |
| Help / tutorial | 2616 | ? | ? | todo |
| Credits | 2604 | ? | ? | todo (`credits`) |
| Save date template | arm9:0927A6 | 1 | slot 32 bytes | fixed slot |
| Default names | arm9:0941C0.. | 1 | 9 codes (slot 20 bytes) | fixed slot |
