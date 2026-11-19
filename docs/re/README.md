# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| `filesystem.md` | NitroFS, FILEDATA.BIN "LF 2" archive, id map, free space | verified (identity repack pending) |
| `text.md` | u16 encoding, message files, header words, control codes, arm9 strings, text ranges | encoding verified; code meanings partly guessed |
| `font.md` | dialogue font (FILEDATA 860), kanji map | verified layout; kanji map read by eye + context |
| `graphics.md` | graphics-text survey (static sweep `tools/gfxsweep.py`, rows in `graphics_sweep.tsv`), NDS banner | sweep done; RGCN/RECN/RCSN layouts verified by renders; QQ = tilemap guess |
| `debug.md` | FILEDATA load hook, boot-script swap to the debug menu (2477 -> 2494), menu map, normal new-game flow, save file | warp verified (29 scenes); save layout to do |

Prior work (one web search, 2026-11-19): no released English patch or tools found. A NeoGAF thread on unlocalized
DS RPGs (https://www.neogaf.com/threads/unlocalized-ds-rpgs-from-nintendo.933358/page-2) mentions a fan
translation that was abandoned halfway; no files or notes from it were found. Publisher: Marvelous Entertainment.
