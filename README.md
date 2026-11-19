# Sakura Note: Ima ni Tsunagaru Mirai English translation

Unofficial English fan translation of **Sakura Note: Ima ni Tsunagaru Mirai** (Nintendo DS, Marvelous
Entertainment, 2009): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue, narration, story (boy, cat and dog routes, bonus episodes) | Translated |
| Menus, items, objectives, profiles, tutorials, save/load, sound test | Translated |
| Graphics with text (pause tabs, status and item panels, banners, choice buttons, name-entry prompts) | Translated; the title logo and the Nazkaiser logo are left in Japanese, as are small signs in background art |
| Name entry | Names up to 9 letters; the keyboard opens on the kana page (an abc page is there) |
| Credits | Translated |

Known issues: pause tabs read "Ch. 1".."Ch. 4" (the tab is too narrow); a few choice buttons are shortened to fit.
None other known; see [Issues](../../issues).

Base ROM (No-Intro): `Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds`, 67,108,864 bytes, CRC32 `006C9EF3`,
MD5 `6c98fc0f19dd67d11a660c7d8b75b82a`, SHA-1 `911782fa06c3006cd66818914c7684d6422d200c`. Tested in DeSmuME;
start from a cold boot with a new save.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `gfx/labels.tsv` | Graphics-text redraws (English lettering drawn into the game's art by the build). |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ (ndspy, Pillow; pytest for the checks) and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/sakura-note-ima-ni-tsunagaru-mirai-en
cd sakura-note-ima-ni-tsunagaru-mirai-en
# copy your dump to: rom/Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds
#   (67108864 bytes, SHA-1 911782fa06c3006cd66818914c7684d6422d200c; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/sakuranote_en.nds
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Marvelous Entertainment's and is
included only so the translation can be checked against it. Sakura Note: Ima ni Tsunagaru Mirai is (c) 2009
Marvelous Entertainment; this project is not affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic, Codex by OpenAI). Corrections are very
welcome.
