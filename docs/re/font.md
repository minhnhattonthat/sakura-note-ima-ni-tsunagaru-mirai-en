# Dialogue font

FILEDATA 860: RGCN, 4bpp, tiled, sheet 32 tiles (256 px) wide x 224 tiles high = 16 x 112 cells of 16x16 px
(1792 cells; 0x663-0x6FF blank). Glyph ink is 11x11 at x 0-10, y 1-11. Pixel values: 1 = stroke, 15 = drop shadow.
**verified**: cell 0x10 decodes to あ, cells 0x00-0xFF match the name-entry table FILEDATA 2838 in order, and the
font sits in RAM at 0x023A5F60 while text is on screen. Text code n = cell n.

Fixed-width: every glyph is drawn in a 12 px (guess) cell; whether the renderer has per-glyph widths (VWF) is for
the phase 5 engine spike.

## Character map (`tbl/jp.tbl`)
- 0x000-0x0FF: name-entry table 2838 (kana, ASCII-like letters and digits as full-size glyphs, punctuation); 0x06
  is the katakana middle dot ・ (2838 lists U+2022). 0x0F = full-width space. 0xCF/0xFE/0xFF are blank and unused.
- 0x100-0x13F: circled ①-⑳, Ⓐ-Ⓩ, ⓐ-ⓡ (button icons).
- 0x140-0x662: kanji in a custom order (first-use order, 手入第一話二三四終了...). Transcribed by eye from zoomed
  sheets (`python -X utf8 tools/font.py sheet OUT.png --from 0x140 --labels tbl/jp.tbl`), then checked in context:
  look-alikes fixed by script context: 191 層 (vs 286 届), 1CF 違 (vs 29A 遅), 1F8 聞 (vs 25B 開), 201 魔 (vs 653 廃),
  209 告 (vs 2F3 吉), 23D 襲 (vs 315 顔), 2EB 鳴 (vs 49F 嗚), 4D9 充 (vs 535 究), 586 営 (vs 621 堂, 650 菅),
  434 箝 (箝口令), 467 茶, 592 〆. MS Gothic pixel matching (`tools/fontmatch.py`) got under 50% right on 176
  hand-read cells, so it is not used.
- Phase 4 context check (`tools/rarekanji.py` -> `docs/re/rare_kanji.tsv`: every kanji cell used 1-2 times with
  context, all 606 rows read; then every use of each suspect cell): fixed 2FE 葉 (was 棄: 言葉, 観葉, 皆葉英夫),
  36D 漠 (漢: 漠然), 398 警 (誓: 警備員, 警戒), 3D5 質 (貿: 良質, 鳥質), 4AB 干 (千: 若干, 干した), 508 基 (墓:
  基本的, 秘密基地), 59F 濡 (需), 5C6 含 (宮), 603 尽 (凧: 愛想が尽き), 620 遺 (遭: 遺産). Each verified by every
  use of the cell reading as a real word. Then all 1,631 distinct kanji compounds in the todo text went to an independent `codex exec` read for
  look-alike misreads: one more, 446 条 (柔: 条件, 8 uses). Single kanji between kana were not covered by that pass.
