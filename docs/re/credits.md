# Staff roll (credits) layout

**Verified** (2026-11-19, traces on the original ROM from `work/states/credits.dst`, shots of the English build).

- The roll lives in arm9 **overlay 1** (NitroFS file 1, loaded at 0x021C29C0, not compressed). It builds the roll in
  code, one call per entry, 77 calls:
  `mov r1, #<2604 index>; mov r2, #<x>; mov r3, #<y gap>; str r6, [sp]; bl 0x021D0928` (one call has
  `mov r3, r1`). That is why the x values are "not plain data in FILEDATA": they are ARM immediates.
- 0x021D0928 (ctor) stores x at obj+0x28 and y (gap + 0xC0, fx<<12) at obj+0x1C. 0x021D09A4 passes them to
  0x02043618 -> 0x02043368 -> 0x0206F6CC, which stores x as the halfword at sprite object +0x1C (manager 0x021BA59C,
  objects from 0x021BA6D8, stride 0x24; found by searching a RAM dump for the on-screen x values).
- Each entry is drawn by the shared text engine into its own buffer from pen x 0, shown as a row of 32x16 (or
  64x32) sprites whose left edge is x. The engine **centres every line of an entry inside the entry's widest line**
  (an unpadded "Aki Ota" under "Masayuki Hashimoto" sits centred), so one x per entry centres the whole block.
- 2604:3 (Yasuhiro Wada) is called twice; 2604:76-78 are never called (78 is a malformed triple publisher line).

English: `tools/credits.py` rewrites each translated entry's `mov r2` immediate to `128 - widest/2` (vwf widths);
`build.py` applies it, the write log records each (`overlay1` lines), `romcheck.py` allows overlay-1 changes only
at those immediates. Widest line allowed: 224 px (the JP's widest row is 7 sprites). Probes used:
`tools/debug/callerlog.lua` (caller + stack args), `writerlog.lua` (writers of a RAM range), `oamlog.lua` (OAM).
Shots: `work/qa/credits_en/`, `work/qa/credits_en2/` (every entry centred).
