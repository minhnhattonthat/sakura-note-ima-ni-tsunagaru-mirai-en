"""namefield.py: name-entry field holds 9 characters (the save field's size) instead of 6, drawn at a 12 px pitch.

The English default names are up to 9 letters (Kurosawa, Traumerei, Reinhold); the game's name entry caps the
cursor at index 5 (6 characters) and draws each cell at x = i * 16 on a canvas about 112 px wide, so the defaults
showed as "Kurosaw" / "Traumer" and Backspace from a default left a stale letter. Name-entry object (r4, e.g.
0x021E6F58): +0x428 = 10 u16 codes (FFFD = empty), +0x448 = cursor index (docs/re/nameentry.md).

Patched (arm9 section 0, ARM code, each word checked against the dump; tests/test_namefield.py disassembles them):
- 0x020794F8 Backspace: `cmp r1, #5` (cursor at the last cell) -> #8
- 0x0207961C type a key: `cmp r0, #5` (advance while below the last cell) -> #8
- 0x020798C0/C4 load a name: cursor = min(len, 5) -> min(len, 8)
- 0x02079B40-4C cell x: `lsl r2, r1, #4; str r2, [sp]; mov r3, #0; str r3, [sp, #4]` (x = i * 16, y = 0) ->
  `add r2, r1, r1, lsl #1; lsl r2, r2, #2; mov r3, #0; strd r2, r3, [sp]` (x = i * 12, y = 0)
- 0x02079ABC-C4 cursor sprite x: `(c * 16 + 0x50) << 12` -> `(c * 3 + 0x14) << 14` = (c * 12 + 0x50) << 12
- 0x0207F32C file-select / load name line (builder 0x0207F290): it fills a 20-cell field (struct +0x212C) with
  FFF9 (colour), surname, 000F (gap), given name, then FFFD padding only below cell 20. 9 + 9 letters fill all
  20 cells, leave no terminator, and the copy reads the live words after the field and overruns its 40-byte
  heap block (the name vanished). The given-name loop's `cmp r4, #10` (10 letters) becomes `cmp r1, #18` (stop
  after cell 18), so cell 19 is always FFFD: a 9-letter given name after a 9-letter surname loses its last
  letter on this one line; every shorter pair (up to 17 letters together) shows whole.
"""
import struct

ARM9_BASE = 0x02000000
# (address, original word, new word, what)
PATCHES = [
    (0x020794F8, 0xE3510005, 0xE3510008, "backspace: cmp r1, #8"),
    (0x0207961C, 0xE3500005, 0xE3500008, "type: cmp r0, #8"),
    (0x020798C0, 0xE35C0005, 0xE35C0008, "load: cmp ip, #8"),
    (0x020798C4, 0xA3A0C005, 0xA3A0C008, "load: movge ip, #8"),
    (0x02079B40, 0xE1A02201, 0xE0812081, "cell x: add r2, r1, r1, lsl #1"),
    (0x02079B44, 0xE58D2000, 0xE1A02102, "cell x: lsl r2, r2, #2"),
    (0x02079B48, 0xE3A03000, 0xE3A03000, "cell y: mov r3, #0"),
    (0x02079B4C, 0xE58D3004, 0xE1CD20F0, "cell x, y: strd r2, r3, [sp]"),
    (0x02079ABC, 0xE1A01205, 0xE0851085, "cursor x: add r1, r5, r5, lsl #1"),
    (0x02079AC0, 0xE2811050, 0xE2811014, "cursor x: add r1, r1, #0x14"),
    (0x02079AC4, 0xE1A01601, 0xE1A01701, "cursor x: lsl r1, r1, #14"),
    (0x0207F32C, 0xE354000A, 0xE3510012, "file-select line: cmp r1, #18"),
]
MAX_CHARS = 9  # cursor cap 8 + 1; the save's name fields hold 9 codes + FFFD (tools/debug/save.py NAMES)
PITCH = 12


def allowed():
    """[lo, hi) arm9.bin offsets this module may write (romcheck.arm9_allowed)."""
    return [(a - ARM9_BASE, a - ARM9_BASE + 4, f"name field {what}") for a, _, _, what in PATCHES]


def patch(buf, log=None):
    """Apply PATCHES to arm9 section-0 bytes in place (bytearray), logged through writelog.put."""
    from writelog import put
    for a, old, new, what in PATCHES:
        if old == new:
            continue
        put(buf, a - ARM9_BASE, struct.pack("<I", new), f"name field: {what}", log, struct.pack("<I", old))
