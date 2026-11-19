# Scripts (SCR0) and text coverage

## SCR0 files - verified (`tools/scrrefs.py`)
985 FILEDATA entries start with `SCR0` (1142-2839: map scripts, NPC object scripts, events, system scripts 2477,
2478, 2494, 2626 ...). Layout:
- u16 function count at 0x8, u16 import count at 0xA; u32 offset table at 0x20: the functions, one 0, the imports.
- Function record: u32 code length in u16 words at +0x10, name (16 bytes) at +0x20, code at +0x40.
- Import record: u16 argc at +0x6, name (32 bytes) at +0x20. Imports are the engine's natives (MessageObj,
  SetMessageFile, Event, MobMove ...), called by index.
- Code: a stack machine of u16 words. `40xx` push immediate (4000/4001/4005 one operand, 4002-4004 two), `60xx`
  push variable (one operand), `2102 N` call import N (pops argc, pushes the result), `2002 N` call a local
  function, `A000` pop, `0014` assign, other `00xx` operators, `01xx` flow (`0109` has two operands, `0108` ends).
  **guess** for the operator meanings; the push/call shapes are enough to read immediate arguments.

## How text is shown - verified
- A script calls `SetMessageFile(F)` (F = 2495-2616) and then `MessageObj` / `MessageObjWait` / `MessageAction` /
  `MessageC` / `Jimaku` ... with the string index as the first argument (event 1943: `MessageObjWait(0, 0, ...)`,
  `(1, 0, ...)` = 2499:0 and 2499:1, the opening lines; event 2000: indices 31-37 of 2523, all seen in a run).
- Map scripts (e.g. 1230) start events with `Event(N)`: N is the FILEDATA id of an event script (1909-2106, 1529,
  2478, 2479), whose StartScript plays the cutscene.
- NPCs are object scripts (e.g. 1144 Haruka): StartScript sets the object up, `NearScript` holds the talk (it calls
  SetMessageFile + MessageObj), other callbacks are FarScript, TouchPositive/Negative, ScenePositive/Negative.
  347 object scripts have message calls in NearScript; 56 in TouchNegative, 50 in TouchPositive, 52 map scripts
  in MapExit.
- The engine finds a script's entry function by name, comparing with "StartScript" (six copies in arm9:
  0x02096298, 0x020962B4, 0x020962C8, 0x020962D4, 0x020A4514, 0x020A4520), in the same frame the file opens.

## Coverage tools (phase 8)
- `tools/scrrefs.py`: every (message file, index) a script names with an immediate (`work/qa/scrrefs.tsv`);
  `--unref` lists the dialogue strings (2495-2603) none names: 751 of 4,106. Those are shown by engine code instead
  (battle text 2495-2496, item-get lines "Got X" via GetItem, Tears via NamidaMatome) or are unused.
- `tools/debug/evcover.py`: plays every Event(N) target in the opening map: `warp.lua SWAP='1943:N'` swaps the
  opening event's file open for N, so the engine runs event N's own script (staging can look wrong: mobs may be
  missing). Logs under `work/qa/cover/ev/e<N>/`.
- `tools/debug/mashcover.py`: every debug map-list row x boy/dog/cat, A-mash + walking, with
  `tools/debug/entryname.lua` starting every NPC object script at NearScript (the name copies are patched on that
  file's open and restored the next frame; patching during the map script's own start breaks the map). Logs under
  `work/qa/cover/map/`. `work/qa/cover/mash/` = an earlier plain mash (no NPC patch).
- Report: `textcover.py work/qa/cover build/strings.tsv --waive docs/text_unshown.tsv`.
