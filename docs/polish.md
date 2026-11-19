# Polish list

Small fixes found along the way; every line must be ticked before release (phase 9 gate).

- [x] Profiles 2611: bullet continuation lines are indented two spaces in 57 of 74 bulleted entries (as the JP's
  full-width indent), but not in 2611:31 and 59-75. Indent those too (all still fit 228 px; checked 2026-11-19).
  Fixed 2026-11-20: 59-75 indented (75 opens on a continuation line, as the JP); 2611:31 has no continuation lines.

Story pass round 1 (2026-11-20, `work/qa/story/reports/*.r1.md`, codex read-only). Critical/Important fixes are in
`docs/review-log.md` §Story pass; the Minors:

- [x] 2503:187 - Squawks' buzzer call "Bzz-cheep!" vs "Boo-cheep!" at 2496:123. Fixed: "Boo-cheep! Too bad!".
- [x] 2506:115 - "She was fine" hides the repeated 普通 answer (2506:120 "Ordinary, huh..."). Fixed: "She seemed ordinary."
- [x] 2512:23 - locker report says "Shut"; glossary: Closed / Open. Fixed in both sequences (pun lines unchanged).
- [x] 2512:101 - "Lord Garanryu" vs Garanryu-sama at 2517:24. Fixed: "Oh, Garanryu-sama."
- [x] 2512:211 - "Kya ha ha" kept a JP vocalisation. Fixed: "Hee hee hee hee!!".
- [x] 2520:49 - "I cried Tears" read as the item. Fixed: "I cried because I was happy." (glossary: lowercase for ordinary tears).
- [x] 2523:37 - "Let's go see the cherry tree?" Fixed: "Shall we go see the cherry tree?".
- [x] 2527:18 - "Wait just a moment?" Fixed: "Wait just a moment...".
- [x] 2555:0 - "It's your friend" sounded like an identification. Fixed: "This is your friend's business, Kaname-kun."
- [x] 2561:15, 2565:5 - Kikichi's surname dropped. Fixed: "Kikichi Sakura", "Kikichi Sakura-san?".
- [x] 2584:8 - "I can't make my feelings understood" stiff. Fixed: "I can't tell you how I feel...".
- [x] 2599:19, 2599:20 - -sama dropped on Chirpy/Coojudge. Fixed.
- [x] 2606:143 - "Pigeon" capitalised. Fixed: "a pigeon".
- [x] 2608:28 - "How Ends?" Fixed: "A Girl in Love: How Will It End?" (the suggested "Schoolgirl's" wording is 163-173 px > 160).
- [x] 2608:39 - "Ice Pop vs. Gelato" (inventory term). Fixed: "Ice Cream vs. Gelato".
- [x] 2611:40 - generic "spirit-board game"; glossary: Kokkuri-san. Fixed in both bullets.
- [x] 2611:76-80 - family dossier headers surname first. Fixed: given name first (as 2611:84 Nanami / Yoshida).
- [x] 2615:18 - "Chapter 4 Special" lacks the colon. Fixed.
- [x] 2616:59 - first "Tears" should be ordinary tears. Fixed: "much like tears".
- [x] 4033:2, 6, 7, 35, 39, 40 - choice buttons: "Maybe not...", "Buy a soda" (glossary Soda), "Sure did!", "Won't
  help!", "Hello!", "Look at me!" (no tildes). Fixed in `gfx/labels.tsv`, all fit their 56/72 px buttons.
- [x] 4033:49, 4033:50 - "Take fish" / "Skip the fish" vs glossary Dried Sardines. Waived: "Take sardines" is 67 px in
  the 56 px button; the pair keeps one word.
- [x] 4033:19 (filed Important) - "Sakura Mochi" drops Great. Waived: "Great Sakura Mochi" is 95 px in the 72 px
  button and the 16 px button has no room for two lines; the other answer ("Hilltop flats") has neither SAKURA nor
  MOCHI, so the quiz answer stays clear.

Story pass round 2 (2026-11-20, `*.r2.md`): every chapter `ok`; the Minors:

- [x] 2501:10, 2501:31 - "braised" vs "stewed pork belly" (2499:1, 2501:6). Fixed: stewed.
- [x] 2501:50 - "I'm counting on you, please!" Fixed: "Please, I'm counting on you!".
- [x] 2506:115, 2506:120 - "ordinary" read as personality. Fixed: "She seemed normal." / "Normal, huh...".
- [x] 2512:61 - "only had eyes for you" added romance. Fixed: "kept looking at you, Mom".
- [x] 2520:163, 2520:165 - "let's go?", "gave a little ache". Fixed: "shall we go?", "my heart ached...".
- [x] 2543:15 - "this Hilltop". Fixed: "We usually watch from up here."
- [x] 2550:1 - "too much for paws". Fixed: "That's beyond a cat's paws." (猫の手 idiom kept).
- [x] 2565:21, 31, 39 - ordinary tears capitalised. Fixed: lowercase.
- [x] 2578:24 - "Do you want something with my son?" Fixed: "...What do you want with my son?".
- [x] 2580:4 - abandoned "I was so..." before 2580:5. Fixed: "...-kun about this...".
- [x] 2605:52 - "felt no gratitude" shifts the joke. Fixed: "To the boy, of course, it was just a feather."
- [x] 2608:60, 2608:61 - "Music"/"Science" without "Room". Waived: "Music Room: ..." is 170 px, "Science Room: ..."
  180 px > the 160 px objective line; the shortened room names stay clear in the school list.
- [x] 2611:64 - "dealings and dwellings" reads as property. Waived: round 1 asked for the 過程/家庭 pun; the pun stays.
- [x] 4033:46 - "Lend it" for ちょっとかして. Fixed: "Borrow it" (45 px in the 64 px button).
- [x] 4033:48 - "All in!" vs "In one go!". Waived: "In one go!" is 49 px in the 40 px button.
