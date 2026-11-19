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

## Findings so far
- Pause-menu tab sheets 4187 (tiled), 4192 (linear 0x101), 4194 (tiled): 13,312 bytes each, 4bpp, carry
  1章..4章 plus STATUS / MAP / NEWEXP. 4192's RECN is 4193 (next id). 4187 rendered through 4193 comes out
  scrambled, so 4187/4194 use another RECN: **guess** a nearby one (4183-4186 or 4197-4198); find it by rendering
  candidates (`gfx.py cells`) until the tabs read whole, or from an OAM dump of the status_menu scene
  (`tools/debug/oamlog.lua`).
- No row is redrawn yet. Order proposed: pause-menu tabs (pilot: one small label class), status 1040, inventory
  header 1020-1035, NEWEXP panel 1017 and banners 4052-4068, name-entry prompts 988/991/994, collection banner
  1000-1015/4218, choice sprites 4033/4044, map labels 1046, 4028, 2842, minigame panels 70-106, title logo 1139.
