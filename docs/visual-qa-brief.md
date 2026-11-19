# Visual-QA reviewer brief - Sakura Note: Ima ni Tsunagaru Mirai (NDS)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents. Read long files in parts (offset/limit):
an output-trimming plugin returns a stub for whole-file reads above ~4 KB.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Each sheet is one scene: the English build on the left, the original Japanese ROM on the right, both DS screens
  stacked (top screen above, touch screen below), at 2x.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- `glossary.md` (names), `docs/re/graphics.md` (Japanese drawn into graphics, not text: a known redraw list).

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 2 --out <scratch>.png` and read that.
- Compare with the right half: if the original shows the same thing, it is the game's own behaviour: `ok`, with a
  note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible (say whether it is font text or a graphics row from `docs/re/graphics.md`);
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's half (Latin labels such as START GAME, STATUS, MAP, NEWEXP., GAME OVER are
  the original's own English);
- the debug menu, BG/OBJ viewers, sound test, extras list (extras_list, extras_player) and battle list (debug-only screens, labels from file 2612 are left
  in Japanese on purpose: status `data`);
- player-entered names on the save/file screens are save data (the fixtures were made on the original ROM).

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which half/screen, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
