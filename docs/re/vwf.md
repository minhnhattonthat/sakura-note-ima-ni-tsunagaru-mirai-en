# Text renderer and the English VWF (phase 5)

## Dialogue renderer - verified (breakpoints + marker build)
- Text is drawn pixel by pixel onto a bitmap canvas made of 64x64 panels (OBJ): `ctx+0x1E4` panels across,
  `ctx+0x1E8` down, `ctx+0x1EC/0x1F0` panel w/h. The dialogue canvas (`ctx` 0x021EAA34 in field_s1_boy) is 4x1
  panels = 256 px wide; its x 0 sits at screen x 14, so a line can show 242 px before the screen edge.
- `0x0203A480`-ish per-character state machine (jump table on code + 0x23 for the FFDD-FFFF controls, around
  0x0203A240) calls one of three blits, then adds the advance to the pen x at `ctx+0x228`:
  - `0x02037FA0` (normal; `ctx+0x24 != 0`), `0x020382D0`, `0x020385E4` (other modes): args r0 ctx, r1 [ctx+0x20],
    r2 colour [ctx+0x248], r3 code, [sp] x, [sp+4] y. The cell is `font + (code>>4)*0x800 + (code&15)*0x40`
    (16x16, 4bpp, 32-tile-wide sheet), font chosen by `ctx+0x54` (control codes FFxx copy ctx+0x40..0x50 into it).
  - Pixel plot `0x02037E8C`: value 0 is skipped (transparent), x < 0 or > 255 dropped, x wraps into the next panel.
- **Advance**: `0x02037A00(ctx, code, metrics=ctx+0x1F4) -> px`: `{sp}` (FFF4) = metrics[4]/2; in metric modes 1/3
  codes < 0x100 get metrics[0xC]; otherwise metrics[4] (12 in dialogue, 15 in the debug menu). Ten callers (the
  four draw paths + width measures 0x02037BE0/0x02037D2C/0x0203AB30...), so one hook covers drawing and centring.

## Speaker tags - verified
- Header word0 of a dialogue string = speaker index into FILEDATA 2610 (0x0A32). `0x020360F4` loads 2610, memcpys
  0x14 bytes (10 u16) of the indexed string to `ctx+0x1BC`, forces FFFD at u16 9 when longer, frees the file.
  Indices 0-4 come from the save's name slots instead (`0x02036248`: +0x1F7E full, +0x1F42, +0x1F2E, +0x1F56,
  +0x1F6A), so 2610:0-4 are placeholders. Only this routine references 0x0A32 (arm9/overlays/SCR0 scanned).
- `0x02039090` draws the tag: up to 16 codes, fixed 8 px step, `0x02038648` per code (8x8 font FILEDATA 872, RGCN
  4bpp, 256 cells 32 per row, codes <= 0x100; stroke 8, shadow 15 right and below). Font 872 already has A-Z a-z 0-9
  and some punctuation at the name-entry codes 0xB0-0xFD.

## The patch (`tools/vwf.py`, built by `tools/build.py`)
- Encoding: letters/digits and `< > ; : ' + - * / = % & @ ( )` keep the codes the Japanese table gives them
  (0xB0-0xFD = name-entry Latin), every other ASCII char = 0x680 + (c - 0x20), `…—é♪♥` from 0x6DF. Big-font cells
  get the glyphs of `fonts/vwf_glyphs.txt` (hand-drawn, 8 px caps, x-height 6, 2 px descenders, rows at cell y 2-11,
  shadow added one row below). Small-font cells of the shared codes are shifted flush left; widths from their ink.
- Hook block = new arm9 autoload section at 0x021D6540 (the old main arena lo; `OS_GetInitArenaLo(0)` literal at
  0x0200E284 raised past it). `0x02037A00` -> `ldr pc,[pc,#-4]` to `adv_hook` (width-table byte for 0xB0-0xFF and
  0x680-0x6FF, else the original body). `0x020390C4` -> `tag_hook`: walks the tag as bytes (two codes per u16, low
  first, 0xFF pad; stop at a byte >= 0xFD) or as u16 for speakers 0-4, advancing by the small-font width table.
- Tags: up to 18 codes (9 u16 survive the copy). `insert.encode_tag` packs 2610:5+ (English or Japanese).
- Marker build (`build.py --marker`): every todo entry -> `[id]` + digit ruler to 240 px per line, tokens kept;
  tags `T<index>` + letters (18 codes); arm9 slots `a<k>`.

## Measured budgets (width gate) - see docs/re/boxes.md
