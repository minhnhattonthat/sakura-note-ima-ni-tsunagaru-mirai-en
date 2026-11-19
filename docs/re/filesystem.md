# Filesystem and ROM layout

ROM: `BSAJ`, "SAKURA NOTE", 64 MiB cart (0x4000000), header used size 0x3E59580; the tail to 0x4000000
(0x1A6A80 bytes) is all 0xFF. **verified** (`tools/romfs.py`, header read).

## NitroFS (5 files) - verified (`python -X utf8 tools/romfs.py`)

| fid | size | file |
|---|---|---|
| 2 | 40,038,948 | `FILEDATA.BIN` - archive "LF 2", almost every asset |
| 3 | 21,343,776 | `music_data.sdat` |
| 4 | 2,959,232 | `sound_data.sdat` |
| 0, 1 | | arm9 overlays 0 and 1 (both load at 0x021C29C0; not compressed) |

arm9: 0xACC18 bytes at 0x02000000, entry 0x02000800, not compressed (module params footer `2106C0DE`).

## FILEDATA.BIN ("LF 2") - verified (`tools/filedata.py`)

```
0x00 "LF 2"
0x04 u32 first data offset / 4   (0x24B8 -> 0x92E0)
0x08 u32 count                   (0x125A = 4698)
0x0C u32 table offset            (0x10)
0x10 count x { u32 offset / 4, u32 size }
```
No names. Entries are raw (some payloads are LZ10 themselves), 4-byte aligned, back to back; the last ends exactly at
the archive end. `filedata.build()` with the original payloads is **not yet byte-identical** (alignment padding bytes
are probably not zero): phase 3 must keep the original padding per entry.

### What is where (by id; kinds from magic, LZ10 payloads decompressed)

| ids | kind |
|---|---|
| 0-1141, 2840-4697 | graphics: RGCN/RLCN/RCSN/RECN/RNAN raw, 496 LZ10 RGCN (mostly 65,600 B = 256x256 8bpp), 177 LZ10 "QQ" blocks (format unknown) |
| 860 | **dialogue font** (RGCN 4bpp, see `font.md`) |
| 1142-2106, 2477-2479, 2494, 2617, 2619, 2621-2631, 2835-2837, 2839 | `SCR0` compiled scripts (985). Bytecode with u16 ops + named functions (`MessageC`, `SetMessageFile`, `DebugScenario`, `EpisodeSelect_Test`, ...). No text inside. |
| 2495-2616 | **message files** (122 files, 5,413 strings) - see `text.md` |
| 2107-2476, 2480-2493, 2632-2834 | small binary tables / map data (no text found) |
| 2838 | name-entry keyboard table: 256 UTF-16 chars = font codes 0x00-0xFF |

## Free space
FILEDATA is rebuilt whole (ndspy rebuilds NitroFS), so files can grow; the ROM may grow into the 0xFF tail
(1.65 MiB) and beyond up to the 64 MiB cart size only if the header size is updated. **guess** until the identity
and marker builds prove it.
