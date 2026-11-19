# Phase 6 reviewer pass

Reviewer: `codex exec` read-only per batch (`tools/review_run.py`, brief `docs/reviewer-brief.md`); reports in
`work/tl/review/bNNN.md` (gitignored), counts via `review_run.py --summary`. All 37 batches reviewed, 2026-11-19.

Result: **0 Critical** in every batch. Every Important finding was applied or rejected with a reason below, so none
is left open.

## Applied

| id | change |
|---|---|
| 2496:118 | "each visitor something different" (visitor-specific clues) |
| 2505:4 | dropped the added "about Nanami-chan" |
| 2512:25, 2512:51 | full names Nanami Yoshida / Takako Yoshida restored (2512:51 split onto its own page) |
| 2512:150 | short form "Yokai Academy" (glossary row split: 妖怪学園 alone = Yokai Academy) |
| 2512:190 | スカレ abbreviation: "\"Skyscraper\" to its friends" instead of repeating the full name |
| 2516:27, 2517:0 | unnamed "teachers" (no added Nobiyo-sensei) |
| 2520:92 | "put his Cell Phone in the trash can" (location clue) |
| 2520:195 | "A present for pyou!" |
| 2525:32 | "we can't... leave things like this" |
| 2550:1 | "That's too much for paws" |
| 2561:19 | "That's not my problem!" |
| 2565:30 | "She'd cry, darn it." |
| 2600:39 | "Nanami... Nanami... Sniff..." (broken appeal, not addressed to Nanami) |
| 2611:65 | the "fool" nickname belongs to his dad |

Consistency sweep after the reviews (glossary variants the lint does not enforce in the Guidance section):
Okashita -> Lower Hill (2513:103, 2611:15), Takadai -> Hilltop (2571:56), Silvervine -> Silver Vine (2608:30),
Grimy/Dishrag -> Grubby/Dust Rag (2611:52), Pitchy -> Chirpy (2611:67), "Enter Super Nazkaiser!" -> "Super
Nazkaiser Arrives!" (2605:7).

## Rejected

| id | finding | reason |
|---|---|---|
| 2610:* (b001) | no JP to check | the batch file held the tag ids only; the tags were translated from 2610 directly and are binding glossary names |
| 2553:1, 2553:11 | use "Joshu-sensei" | glossary: Dr. Joshu |
| 2537:18 | space before -kun | translator brief: honorific written straight after the name variable |
| 2608:31-32, 47-48, 63-64, 76-77 | `'s` glued to a drawn name | the no-suffix rule is for ordinals; `'s` reads right after any name and matches the chapter cards |
| 2611:14 | "In her twenties" as present | the JP lists life stages (10代 then 20代); past reading kept |
| arm9:0941C0 | "Toru K." -> full name | 9-code slot; full name needs the pointer moved (phase 7) |
| 2604:78 | "Marvelous Ent." -> full name | 125 px > the 120 px credits cap; flagged in glossary. Phase 7: credits re-centred (cap 224), full name restored (2604:78 is never shown anyway) |
| 2608:31-32, 47-48, 63-64, 76-77 | "Saw All of X's Story" -> "Finished X's Story" | phase 8 stress: 163 px > 160 with a 9 x W name (the lint now counts a name as 72 px, D13) |
| 2611:45, 2611:54 | lines re-wrapped, same words | phase 8 stress: 237-246 px > 228 with a 9 x W name; now 8 and 10 lines (profile cap 10) |

## Story pass (phase 9)

Round 1 (2026-11-20): one codex read-only reviewer per chapter file (`tools/story_run.py`, brief
`docs/story-reviewer-brief.md`, chapters from `tools/pairs.py chapters`), reports in `work/qa/story/reports/`.
Critical: none. Important, all fixed:

| id | finding | fix |
|---|---|---|
| 2500:55, 2502:59, 2537:18, 2571:55, 2575:18, 2507:7 | Nanami's surname dropped from her introductions; 2516:8 "I'm not used to Yoshida" needs it | "Nanami Yoshida" restored |
| 2545:26 | Kikichi's surname dropped just before Takashi Sakura's introduction | "I'm Kikichi Sakura." |
| 2510:22 | unframed first-person thought in third-person narration | "He was worried about Nanami. He should hurry back to everyone." |
| 2561:21 | "Even if they'd met" lost who met whom | "Even if he'd come to me, that's too much for a dog to handle." |
| 2554:1/6 | the pi/ki bird-sound joke lost its link to 《気》 | the bird now says "Kee!" (energy), echoing "pee" / "kee" |
| 2608:37 | おじさんにコンタクト contact/contact-lens pun lost | "Make Contact with the Man" |
| 2611:64 | 過程/家庭 pun flattened | "trouble grew in his dealings and his dwellings" |
| 4033:19 | Great dropped from Great Sakura Mochi | waived for fit (docs/polish.md) |
