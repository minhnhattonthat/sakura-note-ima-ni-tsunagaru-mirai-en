# Translation reviewer brief - Sakura Note: Ima ni Tsunagaru Mirai

You review one batch of a JP->English fan translation of a gentle, funny, sometimes sad DS adventure for children
(a boy, his family's cat and Nanami's dog meet yokai in a small town). Read-only. Mechanical validity (ids, control
codes, characters, pixel widths) is already enforced by the check tool: judge translation quality. Everything you
need is in this prompt: this brief, the style reference, the synopsis, the batch's glossary rows and the pairs.

## Inputs
- Pairs: every entry as `>> id | speaker | JP` then `   EN: ...`, in story order. `{n}` = line break, `{page}` =
  next page, `{var_XX}{slot}...` = a drawn name (EF boy, F0 surname, ED dog, EE cat), `{col_..}` = colour codes.
  Judge every pair.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; honorifics kept as the JP has them (-chan, -kun, -san, -sensei);
  family words as Mom/Dad/Grandma; voice matches the style reference.
- What players catch that reviewers miss: jokes/wordplay losing their punch; a suffix glued onto a name variable;
  abbreviated names or terms; awkward stock phrases ("... GET!").
- Voice: each speaker against their row in the style reference. Register markers (old-man じゃ/のう/わし, rough
  ぜ/ねぇ, feminine かしら/わよ/のね, children's whines, animal tics) must come through in English, not be normalised
  into neutral prose. A flattened voice is Important, not Minor.
- Reveals: nothing may give away a later reveal (synopsis "Reveal protection").
- Naturalness: easy English a 10-year-old can read.

## Report (reply with only this)
### Critical
### Important
### Minor
Each line: `id - JP gist - problem - suggested EN` (the suggested EN complete, with the same control codes; keep it
about as long as the current EN so it still fits). Write "none" under an empty heading.
### Assessment
Approved | Needs fixes - one sentence why.
