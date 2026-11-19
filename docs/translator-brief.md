# Translator brief - Sakura Note: Ima ni Tsunagaru Mirai (NDS, 2009)

You translate part of the Japanese script of Sakura Note: Ima ni Tsunagaru Mirai into English for a fan patch. It is
a gentle, funny and sometimes sad adventure for children: a schoolchild (the player, named by the player) meets
yokai, talking animals and the townsfolk of a small Japanese town, and follows a story about the present linking to
the future. Most text is short dialogue in a two-line box.

This brief is given to you inside the prompt, followed by the style reference, the synopsis, the glossary rows for
the batch and the batch itself. You cannot run tools; the controller checks your output and sends back any problems.

## Input
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`, in story order: use the neighbouring lines for context.
- speaker: the name tag shown above the box (JP, with the English once known); `-` = none (narration, menus).
- form: dlg (dialogue box) | narration (white text on black, centred) | menu | button | panel | item | card |
  credits | profile | tag (a speaker name tag) | slot (fixed-size string).
- limit: the box's real pixel budget.

## Output (reply with only this, no prose, no code fence)
One line per input id, same order, every id exactly once: `id<TAB>English`. Plain ASCII plus the allowed symbols
`… — é ♪ ♥` (prefer ASCII `...`). No tabs inside the English, no Japanese or fullwidth characters, no `\uXXXX`.
After the last line you may add report lines starting with `#`: `# NEW TERM: jp -> en`, `# UNSURE: id - note`,
`# LONG: id - note`.

## Control codes (copy exactly)
- `{n}` = line break, `{page}` = next page (waits for a button). You place these yourself in English; the
  Japanese positions don't bind you, except where the form says "same line count" or "keep blank lines blank".
- `{var_ED}{slot}{slot}{slot}{slot}{slot}` (and var_EE, var_EF, var_F0) = a name the game draws (the player's given
  name, surname, the dog's or the cat's name; work out which from context). Copy the whole run exactly, as many
  times as the Japanese has it. Never glue a suffix to it ("{...}'s" is fine; "{...}th" is not); no "a/an" before it.
  Keep the honorific the JP puts after it: `{var_ED}{slot}x5ちゃん` -> `{var_ED}{slot}x5-chan` (written out in full).
- `{col_F8}` ... `{col_FC}` etc. = colour on/off: keep every one, around the English words that match the JP span.
- `{sp}` = narrow space: you may drop or keep it.

## Fitting (the controller's check is the hard gate; overflow comes back to you)
Widths in the variable-width font: most letters and digits 6 px, space 4 px, `i l . , ! : ; '` about 2-4 px,
`m w M W` 8 px; a drawn name counts 40 px.
Ordinary English averages about 5.3 px per character.
- dlg: 2 lines per page; line 1 <= 228 px (about 40-42 characters), the page's last line <= 218 px (about 38-40).
  When the English needs more room, add a page: `line 1{n}line 2{page}line 3{n}line 4`. Prefer 1-2 pages; never cut
  meaning to fit.
- narration: centred, up to 7 lines of 240 px (about 44 characters); a 6- or 7-line page has line 6 <= 190 px.
- menu/button: one line; button 160 px (about 28 characters).
- card (chapter title card): same line count as JP, title 200 px, blank lines stay blank.
- item: `{col_F8}Name{n}{n}{col_FC}description` - name line, blank line, then up to 5 description lines of 216 px.
- tag: at most 18 characters; letters, digits, space, `. ! ? '` only (no `) , " : ; -`).
- slot: the fixed code count in limit.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible. JP register markers carry voice and must become English devices, not vanish: old men's
  じゃ/のう/わし ("eh?", "my boy"), rough speech ぜ/ねぇ/っス ("ain't", "ya", clipped grammar), feminine
  かしら/わよ/のね ("I wonder...", "you know"), children's whines and drawls, animal verbal tics (keep a tic as a
  consistent English tic). A line any speaker could have said is a mistake.
- Natural, easy English a 10-year-old can read: short sentences, contractions, no archaic or stiff phrasing.
- Names and terms exactly as in the glossary rows given. Honorifics are kept, hyphenated, as written in Japanese
  (Nanami-chan, Kiichi-kun, Sakura-san, Nobiyo-sensei); given name first. Family words (お母さん, おばあちゃん) become
  Mom, Grandma, etc., not honorifics.
- Punctuation: 「」 -> "...", 『』 -> '...' (or the colour-coded term on its own), ・・・ and …… -> `...`,
  ！？ -> `!?`, ～ at a word end -> stretch the word or drop it ("Wowww", "Hey~" is not allowed: `~` only if needed).
- Sound effects and interjections: natural English (ドキドキ -> "Ba-dump", えーっ -> "Whaaat?!"), not romaji.
- Don't abbreviate words to fit; add a page instead (dlg) or rephrase.

## Consistency
For a recurring name or term not in the glossary rows, pick a form, use it consistently, and report it as NEW TERM.

## Notes from earlier batches
(added by the controller between waves)
