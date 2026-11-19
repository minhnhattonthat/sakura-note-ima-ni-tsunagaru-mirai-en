# Story reviewer brief - Sakura Note: Ima ni Tsunagaru Mirai (NDS)

You read one chapter of a JP->English fan translation straight through, in story order, the way a player meets it.
Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs (all pasted below this brief)
- `docs/synopsis.md` (plot, who is who, late reveals: the "Reveal protection" paragraph is binding),
  `docs/style-reference.md` (voice per character), `glossary.md` (rulings at the top, then terms).
- The chapter file: every line of the chapter in story order, `>> id | speaker | JP` then `   EN: ...`.
  `## file N` starts a new message file (usually a new scene). Speaker `-` = narration or no name tag;
  `?FFxx` = a header value whose speaker is not mapped (often a yokai, crowd or the same speaker as nearby lines):
  infer it from context, do not report it. Read ALL of it before judging.
- Text codes in braces are engine codes, already checked by a linter: `{n}` line break, `{page}` next page,
  `{col_XX}` colour, `{sp}` narrow space, `{num_F6}` a number. `{var_ED}{slot}{slot}{slot}{slot}{slot}` (also
  var_EE, var_EF, var_F0) is a name the game draws: the player-named boy, his surname, the cat or the dog (see the
  glossary); read it as that name.
- Box limits: dialogue lines are short (about 38 characters per line, 2 lines per page). Do not suggest an EN line
  much longer than the one it replaces; if a fix needs more room, say so and split it with `{page}`.

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others. Name the line where a voice drifts or goes neutral. A flattened quirk is
  Important, not Minor.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline;
  puns are kept or replaced by an English pun.
- Names and terms match the glossary; ordinals and numbers read right ("1st", not "1th"); no awkward stock phrases
  ("TIPS ... GET!").
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`. Use the exact id from the `>>` line.
### Assessment
First line exactly `ok` (no Critical/Important) or `issue - <one sentence why>`. The controller writes this word into
the chapter's verdict.

---
