# Skill gotchas (one line each: reference file, then the fact)

- references/emulator-qa.md §emu.py: `--mash` presses from frame 0 when a `--script` drives input with `L.press` and `--route` is empty (mash runs whenever emu.py's own route is done); it typed into a name entry. Don't combine `--mash` with a script-driven key program.
- references/emulator-qa.md §DeSmuME: without `--sav`, the QA fork reads and writes `tools/desmume/desmume-qa/Battery/<rom>.dsv`, shared by every run; a run that saves changes the next run's title/file menus. Pass a fixed `--sav` fixture for warps.
- references/emulator-qa.md §Debug tool (NDS): an exec hook on the game's archive entry-open routine that rewrites the entry id register can swap the boot script for a leftover debug script, with no ROM patch (Sakura Note: 2477 -> 2494 gave the full debug menu).
- references/emulator-qa.md §DeSmuME: after `--state-in` with JIT, menu screens stayed grey for 100+ frames even after a touch; `--debugger` rendered them at once.
