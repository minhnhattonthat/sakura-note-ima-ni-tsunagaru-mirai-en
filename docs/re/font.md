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
- Risk: other rarely used kanji may still be misread. Phase 4 should list every code used 1-2 times with its
  context for one more check.
