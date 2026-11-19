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
  panels (fills each text pixel from its known neighbours with the nearest palette colour; 4bpp reads and refills
  each pixel in its own tile's sub-palette), `~-T` dark letters, `~hT` warm letters over green art, `^DX,DY` copy
  plain art from an offset. Styles: `shadow` (drop, as the dialogue font), `outline` (8-way rim, for
  white-on-colour labels), `bold`, `big` (2x glyphs, outlined: headings).
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
- Also done: banners 4052-4068, choice sprites 4033/4044, 4028, map labels 1046 (2026-11-20, first session).
- Minigames (2026-11-20): reached from the debug イベント list (scenes `puzzle_info`, `puzzle`, `nazkaiser_info`).
  Yokai Sliding Puzzle = ov1 code loading 76-78 (top) + 73-75 (instructions, bottom), then 70-72 (frame, top);
  Nazkaiser = 109-111 (title logo, top: a logo, left Japanese by D5) + 106-108 (controls, bottom). Redrawn: 70
  "B: Back" (4bpp, ~245/3 inpaint read per tile sub-palette), 73 title + 4 lines, 106 "Controls" (big style over a
  warm-hue inpaint) + 3 lines (dark-letter inpaint on the glow pills).
- NEWEXP tab bottom box 4218 cell 4 (8bpp linear sprite; its palette is 4220, two on: `palette_near` takes the RLCN
  after an RGCN + RECN pair): "Collect them all for a gift!" as on the 1000-1015 banners.
- **Unused, not redrawn** (evidence): ramen minigame panels 80-91 (86 controls, 89 title 小遊戯 丼【ラーメン大喰い】):
  no `C_MG_*` class for it in ov1 (Robot = Nazkaiser, Slider = puzzle, Sound, Viewer, EndRoll), no `mov` immediate
  of 80-91 that loads them in arm9/ov0/ov1, no debug extra or episode opens them (all 12 extras logged with
  `FILELOG=1`). 2842 (ナナミ in three 8x8 glyphs, 2840-2843 group): only the boot-mode script 2839 sits next to it
  (arm9 0x02041D28 switch, empty StartScript), no script or code word holds 2840-2843.
- Title logo 1139 and the Nazkaiser logo 109: stay Japanese (D5: no official English logo).
- Tool: `tools/gfxprobe.py RGCN RECN|RCSN X,Y,W,H [--cell N] [--thresh L]` prints the index histogram and the text
  lines (bright, or dark with a negative threshold) of a region, to read rect/fill/ink off.
