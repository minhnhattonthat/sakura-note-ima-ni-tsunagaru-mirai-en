# Glossary - Sakura Note: Ima ni Tsunagaru Mirai

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Sakura-chan). Name order: Western (given name first).
- Romanisation source: official English names where they exist, else an earlier fan patch, else Hepburn without macrons.
- Credits: English.
- Register / flavour: keep light JP flavour (honorifics, school terms, yokai). Sound effects and interjections:
  natural English (ドキドキ -> "ba-dump"), never romaji (D9).
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening; dialogue that runs long
  gets an extra `{page}` instead of cuts.
- No official English names exist (Japan-only game): names are Hepburn without macrons; descriptive and pun names
  (yokai, NPC labels) are given English names (D10).
- Player-named characters: `{var_EF}` = the boy, `{var_F0}` = the family surname, `{var_ED}` = the dog, `{var_EE}`
  = the cat (survey reading; translators confirm from context).

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...' (or just the colour-coded words), ・・・/…… -> ..., ！？ -> !?,
  ～ -> drop or stretch the word. American spelling.
- Voices: `docs/style-reference.md`. Generic-looking rows (shrine, tears, key...) are in the Guidance section: use
  them where the sense matches; only the tables above Guidance are lint-enforced.

## Characters

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ミシラヌイヌ | Strange Dog | tag 18 | the player's dog before it is named |  |
| ハルカ | Haruka | tag 18 | Boy's mother, 37; adopted the cat. |  |
| カナメ | Kaname | tag 18 | Boy's father, 39; game producer and Nazkaiser fan. |  |
| ナナミ / 七海 / 吉田七海 | Nanami | tag 18 | full name Nanami Yoshida (吉田七海) |  |
| タカコ / 吉田タカコ | Takako | tag 18 | full name Takako Yoshida |  |
| タカシ / 佐倉タカシ / 佐倉さん / 佐倉 | Takashi / Sakura | tag 18 | Takashi Sakura; 佐倉さん = Mr. Sakura or Sakura-san |  |
| キキチ / 木吉 / 木吉さん / 佐倉木吉 | Kikichi | tag 18 | tree doctor and Nanami's ancestor; full name Kikichi Sakura | Kiyoshi |
| ガンタ / 岩田ショウマ | Ganta / Shoma Iwata | tag 18 | the boy's best friend; real name Shoma Iwata (dossier) |  |
| キイチ / 笹木キイチ | Kiichi | tag 18 | full name Kiichi Sasaki; not Kikichi |  |
| コジマ / コジマくん / 小島タカヒロ | Kojima | tag 18 | full name Takahiro Kojima |  |
| ポークジンジャー | Ginger Pork | tag 18 | Pig yokai; natural English dish name preserves food jokes. |  |
| キテンソ | Kitenso | tag 18 | Bat yokai formed from rejection by birds and animals; derivation unconfirmed. |  |
| ガランリュウ | Garanryu | tag 18 | Underground-water yokai; commands school attack; derivation unconfirmed. |  |
| ゲーロン | Croakmire | tag 18 | Swamp/pollution yokai; English name carries croaking and stagnant-water identity. |  |
| キマヨイ | Waverwood | tag 18 | Regret and possession yokai; localizes tree/mental-wavering pun. Energy sense of ki needs contextual wordplay. |  |
| ノビヨせんせい / ノビヨ先生 / ノビヨ | Nobiyo | tag 18 | school yokai, tutorial host; tag Nobiyo-sensei | Professor Nobiyo |
| ヨツダメメミ / メメミ | Mememi | tag 18 | school ghost; full name Mememi Yotsuda |  |
| Dr．ジョウシュウ / 上州先生 / 上州ケンサク / ジョウシュウ | Joshu | tag 18 | vet, 42; Dr. Joshu; full name Kensaku Joshu | Joushuu |
| ギャース | Squawks | tag 18 | Loud parakeet and interpreter; descriptive English screech name replaces Gyas/Gyasu variants. |  |
| クロ | Kuro | tag 18 | Black cat, 7; established Japanese pet name. |  |
| シロスケ / シロ助 | Shirosuke | tag 18 | white cat; nicknames グレイ Gray, ヨゴレ Grubby, ダスティ Dusty, ゾウキン Dust Rag |  |
| ガッツ | Guts | tag 18 | Food-minded cat, 4; restores the borrowed English word instead of Gattsu. |  |
| ホッホロー / ホッホロー様 | Coojudge | tag 18 | pigeon magistrate (トリぶぎょう = Bird Magistrate tag, ハト = Pigeon tag) |  |
| ヨウカイ / 妖怪 | yokai | tag 18 | tags ヨウカイA-E = Yokai A-E |  |
| ナスカイザー / なすかいざあ | Nazkaiser | tag 18 | TV superhero (Nazca theme) | Nasu Kaiser |
| アスカイザー | Askaiser |  | Film rival; Waverwood's apparent model, not a confirmed fixed identity. |  |
| NSKファン | Nazkaiser Fan | tag 18 | Playacting child; retain distinction from other fan labels. |  |
| NSKマニア | Nazkaiser Buff | tag 18 | Enthusiastic viewer and errand contact. |  |
| NSKフリーク | Nazkaiser Superfan | tag 18 | DVD-carrying enthusiast; 18-character tag. |  |
| 茜-AKANE- | AKANE |  | theme-song singer |  |
| 野島一成 | Kazushige Nojima |  | Story and lyrics credit. |  |
| 植松伸夫 | Nobuo Uematsu |  | Music and composition credit. |  |

## Places

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 咲谷 / 咲谷町 | Sakuya / Sakuya Town |  | Explicit readings in opening and 2562 override provisional guesses. | Sakitani; Sakiya |
| 咲谷小学校 | Sakuya Elementary School |  | Boy's school. |  |
| 咲谷駅 | Sakuya Station |  | Departure location; follows established town reading. | Sakiya Station |
| 桐谷 / 桐谷町 / キリヤチョウ | Kiriya / Kiriya Town |  | Explicit kiriya reading overrides provisional Kiritani. | Kiritani |
| 歩奥神社 | Pork Shrine |  | read ぽーく: a pork pun tying to Ginger Pork |  |
| 丘下 / 丘下地区 | Lower Hill / Lower Hill District |  | Map context supports descriptive geography over provisional Okashita. |  |
| 桜ヶ丘 | Sakuragaoka |  | Location of Kiriya's cherry tree. |  |
| 桐谷精巧 | Kiriya Precision |  | Takashi's factory/company; follows explicit town reading. | Kiritani Precision |
| マルケン / スーパーマルケン / マルケンスーパー | Maruken Supermarket |  | Kiichi's family business; JP word-order variants name one store. |  |
| ローマ動物病院 | Roma Veterinary Clinic |  | Dr. Joshu's clinic; retains supplied name and Rome association. |  |
| 元祖ヒルズアイスクリーム | Original Hills Ice Cream |  | Vendor claims to be the originator; distinct from rival's claim. |  |
| 本家ヒルズジェラート | Authentic Hills Gelato |  | Rival claims authenticity; do not also call it Original. |  |
| 冥界大学付属妖怪学園 | Yokai Academy, Underworld University |  | Full affiliation. |  |
| 妖怪学園 | Yokai Academy |  | Short form; use when the JP has only 妖怪学園. |  |
| スカイスクレーパーレコード / スカレ | Skyscraper Records |  | Imported-record retailer; abbreviated JP refers to same shop. |  |
| 川村レコード | Kawamura Records |  | Local record shop. |  |

## Items / skills / terms

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 妖術:歩奥直火焼き | Yokai Art: Flame-Grilled Pork |  | Retains shrine/pork link. |  |
| 妖術:体内ビタミン放出 | Yokai Art: Vitamin Release |  | Ginger Pork's nutrition attack. |  |
| 妖術:ショウガ汁放出 | Yokai Art: Ginger Juice Spray |  | Ginger Pork's food attack. |  |
| 尾場毛団 | Spook Gang |  | Obake sound with delinquent-gang spelling. |  |
| ロッカー研究部 | Locker Research Club |  | Source of mock academic puzzle text. |  |
| 『5つのロッカーの共存について』 | On the Coexistence of Five Lockers |  | Preserve inflated academic tone. |  |
| 『閉・開・閉・開・閉』 | Closed / Open / Closed / Open / Closed |  | Puzzle solution: open lockers 2 and 4. |  |
| 『教員日誌』 | Teacher's Log |  | Reveals Nanami's family circumstances. |  |
| 古代戦士ナスカイザー | Nazkaiser, Ancient Warrior |  | Full franchise title; Nazca association established by dossiers. |  |
| ナスカイザービーム | Nazkaiser Beam |  | Playacting attack. |  |
| ナスカイザーキック | Nazkaiser Kick |  | Playacting attack. |  |
| 超ナスカイザー参上！ | Super Nazkaiser Arrives! |  | Recorded program title. |  |
| 怒りの雨乞い儀式！ | The Furious Rainmaking Ritual! |  | DVD episode title. |  |
| 時空戦士アスカイザー | Askaiser, Warrior of Time and Space |  | Rival hero's full title. |  |
| エジプター | Egyptor |  | Successor hero production; restore natural English coinage. |  |
| ヤマタイザー | Yamataizer |  | Successor hero production. |  |
| メソポタミアン | Mesopotamian |  | Successor hero production. |  |
| 角山プロ | Kadoyama Productions |  | Fictional producer; kanji reading tentative. |  |
| ハカセの未知なコンタクト | The Professor's Uncharted Contact |  | Film title; preserve encounter/contact joke; specific parody unconfirmed. |  |
| 週刊ヨムヨム | Weekly Read Read |  | Publication; natural English repetition carries yomu, "read." |  |
| カッパの手のミイラ | Mummified Kappa Hand |  | Kaname's coveted curiosity. |  |
| 桐谷復興プロジェクト | Kiriya Revival Project |  | Proposed town recovery effort. |  |
| キャラクター大辞典 | Character Encyclopedia |  | Bonus dossiers. |  |
| カナメの日常 | Kaname's Everyday Life |  | Four bonus episodes, including twelve-year aftermath. |  |
| イラストギャラリー | Illustration Gallery |  | Bonus feature. |  |
| 妖怪15パズル | Yokai Sliding Puzzle |  | Fifteen-tile puzzle. |  |
| SOUND TEST | Sound Test |  | 27-track playback menu. |  |
| ナスカイザーのハンカチ | Nazkaiser Handkerchief |  | Lost item links school encounter, tears and hero recognition. |  |
| ミリン風調味料 | Mirin-Style Seasoning |  | Exact inventory item; distinguish from true mirin. |  |
| 大桜餅 / ダイサクラモチ | Great Sakura Mochi |  | Kiriya specialty; Great avoids an unverified size claim implicit in Giant. Contains no cherry ingredient. |  |
| 崖っぷちおはぎ | Last-Ditch Ohagi |  | Seller's desperation and dark-bean jokes support this over neutral Last-Chance. |  |
| ナスカイザー録画DVD | Nazkaiser Recording DVD |  | Recorded TV episode, not necessarily a commercial release. |  |
| ナスカイザーの秘密カード / ナスカイザーひみつカード | Nazkaiser Secret Cards |  | Trading/battle-card line; singular Secret Card for an individual card. |  |
| 涙のオルゴール | Music Box of Tears |  | Sound-test track 27 (2609:26). |  |
| コタツ | kotatsu |  | Heated table; lower case, untranslated (2566:27). |  |
| ナスカイザーカード | Nazkaiser Card |  | Sausage-pack premium; distinct from Secret Cards. |  |
| ナスカイザー大百科 | Nazkaiser Encyclopedia |  | Named book. |  |
| ナスカイザーフィギア / ナスカイザーフィギュア / フィギュア | Nazkaiser Action Figure |  | Movable original-hero figure; spelling variants refer to same item in this context. |  |
| ナスカイザー限定切手 | Limited-Edition Nazkaiser Stamp |  | Stock bought out by adults. |  |
| 落し物のカギ | Lost Key |  | Plain lost key; separate from access keys. |  |
| ほねサク | Bone Crunch |  | Branded dog snack; crunchy-bone pun. |  |
| 参拝のしおり | Shrine Visit Guide |  | Bell purification and offering-box etiquette. |  |
| 回覧板 | Neighborhood Circular |  | Passed among neighbors. |  |
| 空き巣に注意！ | Beware of Burglars! |  | Circular heading; marks identify targeted homes. |  |
| 落し物の手紙 | Lost Letter |  | Delivery note identifies a red mailbox. |  |
| 建設中のビルのカギ | Construction-Site Key |  | Large red ribbon; do not merge with tower or factory keys. |  |
| 雨に濡れた雑誌 | Rain-Soaked Magazine |  | Suggestive adult material seen from a child's perspective. |  |
| 試供品のキャットフード | Cat Food Sample |  | Advertising-style description. |  |
| 子猫の頃の写真 | Kitten Photo |  | Baby and kitten together; family-history clue. |  |
| きれいなメダル | Shiny Medal |  | Resembles foreign currency to narrator. |  |
| キイチの服 | Kiichi's Shirt |  | Inventory establishes promotional shirt, more specific than Clothes. |  |
| キイチの靴 | Kiichi's Shoes |  | Speed-promising sneakers. |  |
| キイチのズボン | Kiichi's Trousers |  | Brother's hand-me-downs; distinct from underwear. |  |
| キイチのパンツ | Kiichi's Boxers |  | Inventory specifies trunks. |  |
| ガンタのメガネ | Ganta's Glasses |  | Plastic lenses. |  |
| ガンタの財布 / ガンタのサイフ | Ganta's Wallet |  | Red nylon with dragon motif. |  |
| ガンタのパンツ | Ganta's Underpants |  | Name written inside. |  |
| メメミのパンツ | Mememi's Underpants |  | Pink, oversized and sheer, with ribbon. |  |
| ピッチィの羽 / ピッチィの羽根 | Chirpy's Feather |  | Same item despite spelling variation; follows localized name. |  |
| プラスドライバー | Phillips Screwdriver |  | Green grip. |  |
| マイナスドライバー | Flathead Screwdriver |  | Red grip. |  |
| モンキーレンチ | Adjustable Wrench |  | Ordinary tool, not a monkey-themed object. |  |
| トルクレンチ | Torque Wrench |  | Applies specified tightening torque. |  |
| 桐谷精巧起業記念限定トルクレンチ | Kiriya Precision Founding Commemorative Torque Wrench |  | Rare collectible in autograph trade quest. |  |
| 銀の鈴 | Silver Bell |  | Cat-collar bell; solid silver unconfirmed. |  |
| 管理室のカギ | Management Office Key |  | Dimpled security key. |  |
| 真空管 / 963A真空管 | Vacuum Tube / 963A Vacuum Tube |  | Specific item is rare Soviet prototype; retain model when present. |  |
| きみと走るとぼくは泣く | Running with You Makes Me Cry |  | Suggested English theme-song title. |  |
| マーベラスエンターテイメント | Marvelous Entertainment / Marvelous Ent. |  | Historical publisher credit; duplicated final entry appears malformed. "Marvelous Ent." is a FLAGGED last resort for credits 2604:78 only (125 px > the 120 px credits cap); restore the full name when phase 7 re-centres the credits (cap 240). |  |

## Guidance (context-dependent: use where it fits; the lint does not enforce these)

### Characters

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| キイチママ | Kiichi's Mom | tag 18 | Supermarket mother. |  |
| キイチパパ | Kiichi's Dad | tag 18 | Supermarket father. |  |
| お松 | Omatsu |  | Kikichi's wife; mentioned only. |  |
| おたね | Otane |  | Kikichi's daughter; owned the pig; joyful tears enabled the pact. |  |
| 六科晃男 | Locker Club Chief | tag 18 | Locker report author; personal-name reading unresolved, so use attested role. |  |
| ピッチィ / ピッチイ様 | Chirpy |  | Merciful bird magistrate; chirp-based English name resolves Pitchy/Pitchi variants. |  |
| よりき / 与力 | Deputy | tag 18 | Bird Shogunate officer; rank, not name. Broader than Constable, more specific than Court Officer. |  |
| エンマ様 | Lord Enma |  | Underworld judge; delegates judgment to birds. |  |
| サクラさん / 桜さん | Sakura-san | tag 18 | the speaking shrine cherry tree; generic 桜 = cherry tree/blossoms |  |
| 赤ダマ | Red Orb |  | a fledgling yokai (幼怪 = Fledgling Yokai) |  |
| コウモリA・B | Bat A / Bat B | tag 18 | Kitenso's companions; separate tags. |  |
| 咲ノ花 | Sakinohana |  | Sumo wrestler whose resentment helped form Ginger Pork; reading tentative. |  |
| ブーマ | Buma |  | Ancient evil inhabiting Nazkaiser's human host. |  |
| ヤドリギ・ジョー | Joe Yadorigi |  | Surveyor and Nazkaiser host; retain personal name, note host/parasite association. |  |
| 高田欣吾 | Kingo Takada |  | Fictional original Joe actor; kanji reading tentative. |  |
| 藤本翔太 | Shota Fujimoto |  | Fictional replacement Joe actor; kanji reading tentative. |  |
| 山崎推子 | Suiko Yamazaki |  | Fictional idol guest; kanji reading tentative. |  |
| 吉村 | Yoshimura |  | Name in Nobiyo's lecture; reading provisional. |  |
| 山崎 | Yamazaki |  | Name in Nobiyo's lecture; not automatically the fictional actor. |  |
| 藤本 | Fujimoto |  | Name in Nobiyo's lecture; not automatically the fictional actor. |  |
| 安藤 | Ando |  | Name in Nobiyo's lecture. |  |
| 辻 | Tsuji |  | Name in Nobiyo's lecture. |  |
| 西川 | Nishikawa |  | Name in Nobiyo's lecture. |  |
| 浜田 | Hamada |  | Name in Nobiyo's lecture. |  |
| ホセ | Jose |  | Name in Nobiyo's lecture. |  |
| 佐伯 | Saeki |  | Nobiyo's helpful school friend; reading provisional. |  |
| まごおもいのじじ | Doting Grandpa | tag 18 | Wants to play heroes with his grandchild. |  |
| うっかりおじさん | Forgetful Man | tag 18 | Lost-property NPC; later identified as mail carrier's father. |  |
| うっかりむすめ | Forgetful Girl | tag 18 | Lost-property NPC; use daughter wording only when relation is established. |  |
| うっかりおばさん | Forgetful Woman | tag 18 | Mislaid groceries. |  |
| こくはくじょし | Girl with a Crush | tag 18 | Confession sidequest. |  |
| ラブラブだんし | Lovestruck Boy | tag 18 | Confession sidequest. |  |
| ふりょう | Delinquent | tag 18 | Shakedown and intimidation encounters. |  |
| ふりょうのおかん | Delinquent's Mom | tag 18 | Forceful mother; label alone does not establish a dialect. |  |
| となりのおばさん | Neighbor Lady | tag 18 | Circular quest and family commentary. |  |
| おとなりおばあさん | Elderly Neighbor | tag 18 | Circular, flowerbed and repair encounters. |  |
| おとなりおねえさん | Neighbor's Girl | tag 18 | Neighbor's daughter; shortened role label fits tag. |  |
| こどくなろうじん | Lonely Old Man | tag 18 | Aloof with humans, doting toward a cat. |  |
| イネムリさん / いねむりお兄さん | Sleepyhead-san | tag 18 | Drowsy neighborhood man. |  |
| ダイエットマニア | Diet Fanatic | tag 18 | Fad diets conflict with snacking. |  |
| せんせい | Teacher | tag 18 | Ordinary schoolteacher; distinct from Nobiyo. |  |
| てんいん | Clerk | tag 18 | Reused service role; not one character. |  |
| まちあわせむすめ | Waiting Girl | tag 18 | Meeting mix-up; preserve scene-specific relationship evidence. |  |
| まちあわせママ | Waiting Mom | tag 18 | Adult in meeting mix-up. |  |
| つかれたせいねん | Tired Young Man | tag 18 | Shopping boyfriend in relevant encounter; broader tag retained. |  |
| たそがれせいねん | Pensive Young Man | tag 18 | Distinct descriptive label. |  |
| かいものかのじょ | Shopping Girl | tag 18 | Shopping girlfriend; shortened tag. |  |
| まようおじさん | Indecisive Man | tag 18 | Cannot choose between options. |  |
| しんし | Gentleman | tag 18 | Formal older-sounding approval. |  |
| おしゃれせいねん | Stylish Young Man | tag 18 | Designer with emphatic fashion advice. |  |
| アイスや | Ice Cream Seller | tag 18 | Rival vendor; survey quest. |  |
| ジェラートや | Gelato Seller | tag 18 | Rival vendor; polished service speech. |  |
| ぼんやりがくせい | Daydreamer | tag 18 | Student watching the river. |  |
| ゆうびんやさん | Mail Carrier | tag 18 | Lost-letter quest; Forgetful Man's son. |  |
| つりびと | Angler | tag 18 | Fishing encounters. |  |
| わがしやさん | Sweets Seller | tag 18 | Desperate to invent a local specialty. |  |
| イヌずきだんし | Dog Lover | tag 18 | Encourages reluctant dog to visit the clinic. |  |
| かんぬしさん | Shrine Priest | tag 18 | Denies yokai are present. |  |
| バーテンダー | Bartender | tag 18 | Tough-guy pose and sentimental reminiscence. |  |
| だいくさん | Carpenter | tag 18 | Repair-related tradesman. |  |
| こういん | Factory Worker | tag 18 | Reused worker role. |  |
| しんじんこういん | New Worker | tag 18 | Junior factory worker. |  |
| おやっさん / 親方 | Foreman | tag 18 | Senior factory authority; combines role and affectionate address. |  |
| ミーハーこういん | Starstruck Worker | tag 18 | Autograph enthusiast; more specific than Trend-Chasing Worker. |  |
| エリートこういん | Ace Engineer | tag 18 | Inventive factory worker; function supports engineer wording. |  |
| ネコすきこういん | Cat-Loving Worker | tag 18 | Gentle worker seeking cats. |  |
| こうぐコレクター | Tool Collector | tag 18 | Obsessive tool enthusiast. |  |
| おにいさん | Young Man | tag 18 | Reused generic label; includes possessed driver in relevant scenes. |  |
| おねえさん | Young Woman | tag 18 | Reused generic label. |  |
| おじさん | Man | tag 18 | Reused generic label. |  |
| おばさん | Woman | tag 18 | Reused generic label. |  |
| おじいさん | Old Man | tag 18 | Reused generic label. |  |
| おばあさん | Old Woman | tag 18 | Reused generic label. |  |
| おとこのこ | Boy | tag 18 | Reused generic child label. |  |
| おんなのこ | Girl | tag 18 | Reused generic child label. |  |
| イヌ | Dog | tag 18 | Incidental animals; distinguish from named dog. |  |
| いやがるイヌ | Reluctant Dog | tag 18 | Clinic-related descriptive animal label. |  |
| ネコ | Cat | tag 18 | Incidental animals; distinguish from named cat. |  |
| トリぶぎょう | Bird Magistrate | tag 18 | concealed tag of Coojudge |  |
| ハト | Pigeon | tag 18 | pigeon (also a concealed tag) |  |
| ヘンなおじさん / 変なおじさん | Strange Man | tag 18 | Kikichi before he is named |  |
| ヨウカイA | Yokai A | tag 18 | A-E tags likewise |  |

### Places

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 神社 / 境内 | shrine / shrine grounds |  | Generic location wording; use named shrine only where warranted. |  |
| 高台 / 高台地区 | Hilltop / Hilltop District |  | Descriptive district rendering; avoids unsupported Takadai reading. |  |
| 高台3丁目 | Hilltop, Block 3 |  | Nanami's address; consistent with district name. |  |
| 住宅街 | Residential Area |  | Lower Hill map area. |  |
| 神社街 | Shrine Quarter |  | Lower Hill map area. |  |
| 駅前 | Station Front |  | Lower Hill map area. |  |
| 工場地帯 | Industrial District |  | Kiriya factory area. |  |
| 塔 / マンション | tower / apartment building |  | Spirits call Nanami's apartment building a tower. | mansion |
| 建設中のビル | building under construction |  | Separate exploration location; not automatically Nanami's tower. |  |
| ヒルズ | Hills |  | Shopping destination; not automatically the apartment tower. |  |
| CVS | CVS |  | In-game convenience-store branding; real US chain unconfirmed. |  |
| ビバーク | Bivouac |  | Named establishment; type not established by reports. |  |
| 西ブロック | West Wing |  | School navigation. |  |
| 東ブロック | East Wing |  | School navigation. |  |
| 奉行所 | magistrate's court |  | Bird Shogunate afterlife court. |  |
| ナスカ / ナスカ平原 | Nazca / Nazca Plain |  | Ancient hero setting and afterlife scenery. |  |
| 地上絵 | geoglyphs |  | Nazca landscape; wolf's eyes mark return point. |  |
| 極楽 | paradise |  | Possible afterlife destination; Buddhist coloring. |  |
| 地獄 | hell |  | Possible afterlife destination. |  |
| 目黒川の桜 | Meguro River cherry blossoms |  | Real-world credits acknowledgement. |  |

### Items / skills / terms

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| はじまりの日 | The Beginning Day |  | Explicit opening title; retained across reports. |  |
| いまにつながるみらい | The Future That Connects to Now |  | Subtitle, episode and track title; preserve time-direction paradox. |  |
| 5年2組 / 5-2 | Class 5-2 |  | Fifth-grade class; quiz answer. |  |
| 桜 / サクラ / 桜の木 | cherry tree / cherry blossoms |  | Context determines tree or blossoms; do not confuse with family surname. |  |
| 散らない桜 / 神社の桜 / 歩奥神社の桜 | shrine cherry tree |  | Out-of-season, persistent blossoms; "ever-blooming" describes appearance, not immortality. |  |
| 桐谷の桜 | Kiriya cherry tree |  | Offspring of shrine tree; disclose relationship only when source does. |  |
| 《気》 / 気 / 桜の《気》 | spiritual energy |  | Sustains trees and manifests yokai; ordinary emotional uses of ki need contextual translation. |  |
| 精気 | vitality |  | Drained life force; related to, but not identical with, spiritual energy. |  |
| 精 / 精霊 | spirit |  | Dormant beings awakened by energy. |  |
| 幼怪 | Fledgling Yokai |  | Deliberate immature-stage wordplay, not a typo. |  |
| 《思い》 / 思い | feelings |  | Emotions, wishes and resentments can linger and manifest. |  |
| 気の迷い / キノマヨイ / 木が迷う | a wavering impulse / a wavering tree |  | Coordinate with Waverwood; preserves mental/tree link without explaining it prematurely. |  |
| 妖術 | Yokai Art |  | Battle-technique prefix. |  |
| 結界 | barrier |  | Supernatural boundary; belief matters to the boy's ability to break it. |  |
| 封印 | seal |  | Supernatural restraint or door seal; distinguish from physical obstruction. |  |
| ヒーロー / 正義の味方 | hero / defender of justice |  | Recognition, responsibility and protection link all viewpoints. |  |
| ヒロイン | heroine |  | Nanami and Haruka's thematic roles; retain context. |  |
| 勇気 | courage |  | Emotional theme; do not assume an unconfirmed numeric resource. |  |
| 縁 / ご縁 | bond / connection |  | Context determines fateful or ordinary sense; not automatically romance. |  |
| 恩 / 恩返し | kindness / repaying kindness |  | Cat-family motif; preserve paired buying/selling-favors jokes. |  |
| 契約 / 契約更新 / 契約の更新 | pact / pact renewal |  | Supernatural agreement; retain legalistic humor in dialogue. |  |
| 一番愛する者の涙 / 最愛の人 | tears of the person you love most / person dearest to you |  | Exact relationship condition; do not add joy before its reveal. |  |
| 佐倉家 / 佐倉の血 | Sakura family / Sakura bloodline |  | Family name, not the generic cherry tree. |  |
| 樹医 | tree doctor |  | Kikichi's profession; distinct from veterinarian. |  |
| 患木 | ailing tree |  | Medical metaphor applied to trees. |  |
| 植木屋 / 植木職人 | gardener |  | Kikichi's local work. |  |
| 挿し木 | cutting |  | Propagation establishes the trees' parent-child relationship. |  |
| 木々養生 | Caring for Trees |  | Kikichi's neglected book. |  |
| たたり / たたる / たたり猫 | curse / to curse / curse-bringing cat |  | Yokai fear cats; this cat does not know how to curse. |  |
| 9回目の命 | ninth life |  | Cat's final life, sacrificed for the boy. |  |
| 生まれ変わる | be reborn |  | Reincarnation; do not erase afterlife restrictions with casual nine-lives jokes. |  |
| 犬魂 / 犬の根性 | canine spirit / a dog's determination |  | Comic bravery language paid off in dog's finale. |  |
| 亡者 | departed soul |  | Dead beings; distinguish from yokai. |  |
| 鳥幕府 / トリバクフ / 幕府 | Bird Shogunate |  | Governs birds, human contact and afterlife judgment. |  |
| 鳥奉行 / 奉行 / お奉行 / お奉行様 | bird magistrate / magistrate |  | Office held by Coojudge or Chirpy; not a personal name. |  |
| 仏の奉行 / ホトケのピッチィ | Merciful Magistrate / Chirpy the Merciful |  | Compassionate epithet, not literal Buddhahood. |  |
| 御法度 | forbidden by law |  | Kikichi's pact violates afterlife rules. |  |
| 鳥質（とりじち） | bird hostage |  | Bird-based hostage pun; Takashi coerces Coojudge. |  |
| ハトおやじ | Pigeon Dad |  | Kaname's later nickname; feeding-pigeons bargain payoff. |  |
| 鳥愛会 | Bird Lovers' Society |  | Joshu's birdwatching group. |  |
| NSK | NSK |  | In-world abbreviation retained despite English spelling. |  |
| 正義の超人！ナスカイザー！！ | Superhero of Justice! Nazkaiser! |  | Grand hero introduction. |  |
| この世界を守るために、我々は出会ったのだ！ | We met to protect this world! |  | Quoted hero line; more theatrical than Nanami's normal speech. |  |
| 世界の秩序を守るため…ナスカイザー、変身！ | To preserve order in the world... Nazkaiser, transform! |  | Supplied portion of transformation oath; preserve wider time/bond motif. |  |
| ヒーローは孤独なのだ！ | A hero stands alone! |  | Kaname's pose, later answered by his heroine partnership. |  |
| 戦闘員 / 戦闘員タイプ | henchman / henchman material |  | Superhero-show foot soldiers. |  |
| 必殺技 | finishing move |  | Kaname submitted ideas used by the show. |  |
| 記憶食い | Memory Eater |  | Kaname's proposed explanation, not a confirmed culprit. |  |
| 忘却魔 | Forgetfulness Fiend |  | Kaname's proposed explanation, not a confirmed culprit. |  |
| くじごしんぼう | Nine-Syllable Protection Rite |  | Occult practice taught before ordinary father-son games. |  |
| こっくりさん | Kokkuri-san |  | Divination game; Takako's incident is explained as self-suggestion. |  |
| 花火大会 | fireworks festival |  | Shared backdrop to promises, searches and family tension. |  |
| 神社レース | race to the shrine |  | Boys' competition; losses incur a drink debt. |  |
| バグ | bug |  | Software fault imagined as Dad's enemy. |  |
| ナミダ / 涙 | Tears |  | Episode-unlock resource; lowercase for ordinary tears. |  |
| 七海のナミダ / 七海の涙 | Nanami's Tears |  | Item is her tear-soaked handkerchief. |  |
| 妖怪の涙 | Yokai Tears |  | Collectible tears. |  |
| ハルカの涙 | Haruka's Tears |  | Character-specific tears. |  |
| かなしいナミダ / 悲しい涙 | Tears of Sorrow |  | Nanami's tears when Takashi falls; unifies Sad Tears with descriptive wording. |  |
| うれしいナミダ / うれし涙 / うれしい涙 | Tears of Joy |  | Dog-birth tears retrieved from the past; decisive late reveal. |  |
| ハート / 体力 | Hearts / health |  | Hearts represent health; use ordinary health wording where appropriate. |  |
| 新しい経験 | New Experiences |  | Completion pages grant power-ups; not numeric EXP. |  |
| 逃避 | Escape |  | Named battle action/challenge; preserve avoidance motif. |  |
| ノーダメージ / ノーダメ | No Damage |  | Challenge condition. |  |
| エピソード / エピソード選択 | Episode / Episode Select |  | Unlockable viewpoint segments and menu. |  |
| 第1話-第4話 / 最終話 | Episode 1-4 / Final Episode |  | Save labels; not proof of a fifth chapter. |  |
| 第一章-第四章 / 第2章 | Chapter 1-4 / Chapter 2 |  | Four-chapter structure; earlier Kitenso battle identified as Chapter 2. |  |
| 編 / スペシャル | Story / Special |  | Viewpoint and bonus route labels. |  |
| セーブポイント | Save Point |  | Persistent restart location. |  |
| 中断データ | Suspend Data |  | Temporary save consumed on resumption; chapter restrictions apply. |  |
| クリアデータ | Clear Data |  | Post-completion save. |  |
| インコの謎 | Parakeet Mystery |  | Recurring side-objective series. |  |
| 猫会議 | Cat Meeting |  | Information-sharing encounters. |  |
| 変身ポーズ | Transformation Pose |  | Lesson objectives have start and completion states. |  |
| ミリン | mirin |  | Cooking ingredient in dialogue. |  |
| ダイ / サクラ / モチ | GREAT / SAKURA / MOCHI |  | Quiz fragments must assemble into Great Sakura Mochi; quoted keyword use differs from ordinary サクラ. |  |
| キーワード | keyword |  | Quiz terminology. |  |
| ジンジャーポーク | Pork Ginger |  | Deliberately reversed quiz distractor; distinct from correct Ginger Pork. |  |
| ジュース | Soda |  | Inventory explicitly carbonated; translate generic dialogue as drink where needed. |  |
| にぼし | Dried Sardines |  | Cat snack. |  |
| またたび | Silver Vine |  | Cat-attracting plant. | catnip |
| 虫の死骸 | Dead Bug |  | Cat's unwelcome gift. |  |
| アイス | Ice Pop |  | Inventory prize-stick item; broader seller dialogue can mean ice cream. |  |
| パンフレット | Pamphlet |  | Informational item. |  |
| フライングディスク | Flying Disc |  | Dog's toy, unused since Takashi left. |  |
| 牛乳 | Milk |  | Bottled delivery. |  |
| コンタクト | Contact Lens |  | Retrieval item; related objective also plays on making contact. |  |
| サンダル | Sandal |  | Fishing junk. |  |
| 野球のボール | Baseball |  | Worn covering exposes thread. |  |
| とかげ | Lizard |  | Cat's unwelcome gift. |  |
| 洗濯物 | Laundry |  | Specifically a damp, muddy shirt. |  |
| ボールペン | Ballpoint Pen |  | Ice cream survey prize. |  |
| コースター | Coaster |  | Clover design. |  |
| 老眼鏡 | Reading Glasses |  | Broken frame, intact lenses; reveals tiny notes. |  |
| 5種のフルーツ | Five Kinds of Fruit |  | Assortment; related objective counts five fruits. |  |
| トンカチ / ハンマー | Hammer |  | Repair tool; variants identify same tool in relevant quest. |  |
| いたきれ | Wooden Board |  | Practical repair material. |  |
| お年玉 | New Year's Gift Money |  | Boy's hidden savings finance trip. |  |
| 切符 | Train Ticket |  | Child fare to Kiriya. |  |
| 電車賃 | train fare |  | Reserved travel money. |  |
| 曲がったスプーン | Bent Spoon |  | Alleged psychic feat treated skeptically. |  |
| 定期入れ | Commuter Pass Holder |  | Container, not the pass itself. |  |
| 定期券 | Commuter Pass |  | Contents, distinct from holder. |  |
| ドライバー | Screwdriver |  | Generic tool wording; preserve specified type when supplied. |  |
| タイムカプセル | Time Capsule |  | Durable burial container. |  |
| カギ | key |  | Generic; identify location from context rather than merging all keys. |  |
| ねこじゃらし / エノコログサ | Foxtail Grass |  | Actual plant used to attract cats. |  |
| ネコグッズ | cat toy |  | Generic cat-related item wording; distinguish from named plant. |  |
| 携帯電話 | Cell Phone |  | Discarded sticky flip phone. |  |
| 豆電球 | Miniature Light Bulb |  | Distinct from vacuum tube. |  |
| どんぐり | Acorn |  | Out-of-season find; polluted-water objective. |  |
| 軍手 | Work Glove |  | Single discarded glove. |  |
| ラジオ | radio |  | Repair quest and analog motif. |  |
| シャッター | shutter |  | Factory access mechanism. |  |
| スイッチA・B・C・D | Switch A / B / C / D |  | Separate labeled machinery switches. |  |
| ポンプ | pump |  | Factory machinery; malfunction timing matters to plot. |  |
| 浄化槽 | treatment tank |  | Factory water-treatment equipment. |  |

## Decisions from earlier batches
- (none yet)
