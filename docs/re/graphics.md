# Graphics-text survey

Status: **static sweep done** (phase 1). The marker-build tour (phase 5/8) and debug-tool warps to chapter cards,
game over, ending and credits (phase 2/8) add what the sweep could not see (runtime-drawn or palette-hidden text).

## Method (reproducible)
`python -X utf8 tools/gfxsweep.py --out work/sweep` renders all 1,072 RGCN in FILEDATA (576 raw + 496 LZ10) into 120
contact-sheet pages (`work/sweep/pNNN.png`, labels = FILEDATA id; `index.tsv` maps labels to pages):
- BG RGCN: tiles in order at the header width (4bpp also composed through the nearest RCSN screen for palettes);
- sprite RGCN (dims 0xFFFF): every RECN cell composed from its OAM (1D mapping shift, per-cell VRAM transfer,
  0x101 = linear row-major per OBJ, verified by readable renders), plus raw tiles for tiled ones;
- palette/cells = nearest RLCN/RECN within 4 ids, same RNAN group first. Identical renders are drawn once; 19 RGCN
  whose renders all duplicate earlier ones are printed by the tool (none dropped silently).
- **QQ blocks** (177, LZ10, magic `QQ` + u16 flags, u16 0x40, u16 0x20, then u16 values 0,0x20,1,2,3...): tilemap-like
  (tile indexes, no pixel data) - **guess**; they cannot carry text pixels themselves, the RGCN they index were swept.

Pages were read by a read-only Codex vision pass (6 pages per call); every row it reported is in
`docs/re/graphics_sweep.tsv` (373 rows, JA and EN). Spot-checked by eye: p003 (ids 70-89), p062 (1125-1139, 2842).

Outside FILEDATA: the **NDS banner title** (all 6 languages) is `サクラノート / ～いまにつながるみらい～ /
マーベラスエンターテイメント` (UTF-16 in the icon/banner block) - text, not tiles; translate at build time.

## Japanese graphics text (sweep result, by FILEDATA id)
| id(s) | screen / use | text |
|---|---|---|
| 1139 | title screen logo (BG) | サクラノート / ～いまにつながるみらい～ |
| 109 | leftover title (other game?) | サクラノート logo + English lines; probably unused |
| 70, 72 | 15-puzzle frame | Bボタン：もどる |
| 73 | 15-puzzle instructions | 妖怪15パズル / 十字ボタンを使い、ピースを空いているスペースに移動します。/ どんなオリジナル妖怪が出てくるかは、お楽しみ。 |
| 86, 89 | ramen minigame (crossover) | 操作説明 / Aボタン：麺を喰らう / マイクに向かって息を吹く：冷ます / TEMPメーター... 8杯完食... ; 小遊戯　丼【ラーメン大喰い】 |
| 106 | Nasukaiser minigame | 操作説明 / 十字ボタン：ナスカイザーを左右移動 / Aボタン / Yボタン：ナスカイザービーム / Bボタン：ジャンプ |
| 860, 863, 866, 869, 872 | font sheets (860 = dialogue font; others font atlases / previews) | glyphs - text work, not graphics (863/866 contain test sample lines from other titles; check if used) |
| 981, 984 | name entry | NAME ENTRY bar, tabs あいう/アイウ/abc (Latin already), kana key sheet |
| 988, 991, 994 | name entry prompts | 少年の「苗字」と「名前」を決めましょう / 猫の「名前」を決めましょう / 犬の「名前」を決めましょう |
| 1000, 1005, 1010, 1015, 4218 | collection screen banner | 全部そろったらプレゼント！ |
| 1017 | "new experience" tutorial panel | 新しい経験!! / いくつかの「新しい経験」を / 1ページ分そろえると… / 体力（ハートの数アップ）/ 攻撃力（敵へのダメージアップ）/ すばやさ（攻撃速度アップ）/ 足の速さ（移動速度アップ）/ どれかひとつをプレゼント！/ これで妖怪とも互角に戦える!? |
| 1020, 1025, 1030, 1035 | inventory header | だいじなもの |
| 1040 | status screen | ステータス / 体力 / 攻撃力 / すばやさ / 足の速さ |
| 1046 | map labels | 咲谷町 / 桐谷町 |
| 2842 | small sprite label | ゴミ箱 |
| 4015, 4017 | reaction / emote icons | …, ！, ？, 1UP, POWER, SP, ZZZ (mostly symbols/Latin) |
| 4028 | message sprite | もうナミダは出ないようだ… |
| 4033 | choice / dialogue-option sprites (many) | あけてみよう, いいことしちゃお, いいよ, いい話だな, いっきに！, いやダメだ…, う～んダメかも, おれだけの力で, お金が落ちてる！, ... (full list: render 4033 and transcribe in phase 5) |
| 4044 | choice buttons | A / B / おもしろい！ / タイクツだ… |
| 4052, 4056 | notification banner | エピソード出現！ |
| 4060, 4064, 4068 | notification banner | 新しい経験!! |
| 4187, 4192, 4194 | pause-menu tabs | 1章 / 2章 / 3章 / 4章 (STATUS / MAP / NEWEXP. already Latin) |

Background art with small signs (shops, stations, restrooms), mostly illegible at native size: 269, 277, 278 (たばこ),
283 (寿司 / 営業中), 323-324 (女 restroom), 397, 398/403 (ゆ bathhouse), 464-465, 535, 554, 569-570, 614, 621,
644-645, 649-650, 657-658/661 (コンビニ), 660 (青果), 664-665, 3758. **Proposed default:** leave scenery signs
as art (legible ones are single words a player reads as decoration); revisit any that a story line refers to.

## Seen on screen so far (original ROM, cold boot; shots in work/qa/explore1-2)
| screen | text | source |
|---|---|---|
| title | logo サクラノート + subtitle, two menu buttons (START GAME / audio SETTING, Latin) | RGCN 1139 / 1136 |
| file select | three slot banners (pink header label on each slot), はじめから / つづきからはじめる popup | slot banners: SAVE FILE (1129, Latin); popup labels may be font text (arm9 0x0927A4 はじめから) |
| name entry | "NAME ENTRY" bar, tab bar, BackSpace / Enter keys | RGCN 981 (Latin already); keys are font cells from table 2838 |

## Still to add (later phases)
Reached by the debug tool (phase 2, `tools/debug/scenes.tsv`; shots from `warp_all.py` in `work/qa/scenes/`):
chapter 1 card + episode board (`episode_ch1`, `chapter1_card`: 第一章 トオル編 / いつもと同じ日常, likely font text),
game over (`gameover`: GAME OVER sprite, Latin), ending (`ending`, `ending_stills`: no text seen), credits
(`credits`: font text from message file 2604, not graphics), character profile (`profile_ch1`). Chapter 2-4 cards
need story progress (save editor, not done). The marker tour (phase 5) lists any screen whose Japanese did not change.
