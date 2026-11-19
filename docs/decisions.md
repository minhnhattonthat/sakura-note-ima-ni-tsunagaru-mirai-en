# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-19 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-19 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-19 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-19 | Abbreviations | engine work first (default), abbreviate | Default: engine work first; abbreviate only as a flagged last resort. |
| D5 | 2026-11-19 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-19 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint without asking. |
| D7 | 2026-11-19 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-19 | Git identity | ask | Already set by new-game.ps1 (minhnhattonthat); do not change it. |
| D9 | 2026-11-19 | Sound effects and interjections | romaji, natural English | Natural English (ドキドキ -> "ba-dump"), never romaji. (Row restored 2026-11-20 from the glossary ruling that cites it.) |
| D10 | 2026-11-19 | Names with no official English (Japan-only game) | Hepburn for all, English for descriptive names | Hepburn without macrons for names; descriptive and pun names (yokai, NPC labels) get English names. (Row restored 2026-11-20 from the glossary ruling.) |
| D11 | 2026-11-20 | Name-entry keyboard (kana key sheet 984, tabs あいう / アイウ) | translate the tab labels, leave | **Agent default under D6, owner may override** (non-blocking note in `docs/status.md`): leave. The keys are the characters the player types and the tabs name those kana sets; the abc tab gives English letters and the default names are English. Visual QA counts them as ok. |
| D12 | 2026-11-20 | Unused graphics (ramen minigame panels 80-91, ナナミ sprite 2842) | redraw, leave | Agent default under D6: leave; nothing in the game loads them (evidence in `docs/re/gfx.md`). |
| D13 | 2026-11-20 | Name entry caps names at 6 characters, but the English defaults are 8-9 letters (field showed "Kurosaw") | shorter default names; raise the cap | Agent default under D4/D6 (engine work over cuts): raise the cap to 9 (the save field's size) and draw the field at a 12 px pitch so 9 cells fit (`tools/namefield.py`, `docs/re/nameentry.md`). The file-select name line has room for 17 letters together; a 9 + 9 pair drops the last letter of the given name there only (it used to make the line vanish and overrun a heap block). |
