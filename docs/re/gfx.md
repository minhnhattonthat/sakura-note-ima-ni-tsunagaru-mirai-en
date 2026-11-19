# Graphics redraws (phase 8)

Pipeline (`tools/gfx.py`, tests `tests/test_gfx.py`):
- Rows live in `gfx/labels.tsv` (one clear-rect + English label per row, in palette indices). `tools/build.py`
  applies them after message insertion (`gfx.apply`); `tools/romcheck.py` re-derives from the same rows which
  pixel-data bytes may change and fails on any other changed byte of those FILEDATA entries (LZ10 entries are
  compared unpacked and recompressed by the build).
- Sprite sheets: a cell is read through its RECN OBJs into an index grid (`cell_grid`) and written back through
  the same OBJs (`put_cell_grid`), tiled (flag 0x100) and linear (0x101) alike, flips applied. A linear and a
  tiled twin of one image need a row each.
- Lettering: the project's own VWF glyphs (`fonts/vwf_glyphs.txt`, MIT, 8 px cap), ink + one-px drop shadow, as
  in the dialogue font. No outside font is used, so `docs/fonts.md` needs no new licence for these.
- Look at the cells first: `python -X utf8 tools/gfx.py cells RGCN RECN --pal RLCN --out work/gfx/cN`, then
  `sheet.py` over the PNGs. After adding rows: `tools/gfx.py preview` (original | English per row), build, warp
  the scene, zoom the cold-boot shot.

- BG screens (RGCN + RCSN, 256x192, mostly 8bpp full-screen bitmaps): the row's `recn` is the RCSN; the screen is
  read through its entries (`screen_map`, flips applied). A write to a tile that also shows elsewhere on the screen
  is refused (`put_map`) unless every copy gets the same value.
- Fills: flat index; `@X` per-row copy (banded pills); `~T` / `~T/D` inpaint for text over art or translucent
  panels (fills each text pixel from its known neighbours with the nearest palette colour). Styles: `shadow`
  (drop, as the dialogue font) and `outline` (8-way rim, for white-on-colour labels).
- Which files a screen uses: run the warp with `--script tools/debug/fileid.lua` too and read `FILE` lines.
- Palette of an RGCN: the next entry if it is an RLCN, else the nearest before (`palette_near`).

## Findings so far
- RECN per-cell VRAM transfer entries are (offset, size); `gfx.py` read the size as the offset at first, which
  scrambled 4187/4192/4194 (fixed: `cell_xoff`). Tabs: 4187 + RECN 4186, 4192 + 4193 (linear), 4194 + 4193
  (status_menu loads 4193/4191/4194/4195). Cells 6-9 = active 1章-4章, 10-13 inactive.
- Done (rows in `gfx/labels.tsv`): pause tabs "Ch. 1-4" (the tab is 37 px; "Chapter 1" is 46: flagged
  abbreviation, decision D4), status 1040 (Status / Health / Attack / Agility / Footspeed: すばやさ is attack speed
  and 足の速さ movement speed, per the NEWEXP panel), Key Items 1020/1025/1030/1035, NEWEXP panel 1017 (top
  banner + 8 lines), collection banner 1000/1005/1010/1015, name-entry prompts 988/991/994.
- Still Japanese: banners 4052-4068 (sprites), choice sprites 4033/4044, 4028, 2842, map labels 1046, collection
  8bpp linear sprite 4218 (needs 8bpp sprite support in `obj_pixels`), minigame panels 70-106. Title logo 1139:
  stays Japanese (D5: no official English logo).
