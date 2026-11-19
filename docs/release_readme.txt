Sakura Note: Ima ni Tsunagaru Mirai - English translation v{version}
========================================================================

Unofficial English fan translation of Sakura Note: Ima ni Tsunagaru Mirai (Nintendo DS, Marvelous Entertainment,
2009). This zip holds only a patch. No ROM is included; never ask for or share patched ROMs.

Source, bug reports: https://github.com/minhnhattonthat/sakura-note-ima-ni-tsunagaru-mirai-en

BASE ROM (Japan), No-Intro: Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds, game code BSAJ
  Size    {size} bytes
  CRC32   {crc32}
  MD5     {md5}
  SHA-1   {sha1}
Any other dump (other revision, trimmed, already patched) will not work.

PATCHED ROM
  CRC32   {pcrc32}
  SHA-1   {psha1}

HOW TO PATCH
  The patch is xdelta3 ({patch}).
  - Windows: Delta Patcher, or xdelta UI: original = your untouched .nds, patch = {patch}.
  - Command line: xdelta3 -d -s "Sakura Note - Ima ni Tsunagaru Mirai (Japan).nds" {patch} sakuranote_en.nds
  - Browser: Rom Patcher JS (https://www.marcrobledo.com/RomPatcher.js/) also applies xdelta files.
  Check the patched CRC32 above.

PLAYING
  Tested in DeSmuME. Start the game from a cold boot (not from a savestate made with the Japanese ROM).
  Start a new save: names in a Japanese save stay in kana.

TRANSLATION STATUS
  Dialogue, narration, story (boy, cat and dog routes, bonus episodes): translated
  Menus, items, objectives, profiles, tutorials, save/load, sound test: translated
  Graphics with text (pause tabs, status and item panels, banners, choice buttons, name-entry prompts): translated
  Title logo and the in-game Nazkaiser logo: left in Japanese (logos)
  Small signs drawn into background scenery: left as art
  Name entry: names up to 9 letters; the keyboard opens on the kana page (switch to the abc page)
  Credits: translated

KNOWN ISSUES
  The pause-menu chapter tabs read "Ch. 1".."Ch. 4" (the tab is too narrow for "Chapter 1").
  A few choice buttons are shortened to fit (e.g. "Sakura Mochi" for Great Sakura Mochi).
  Report bugs at the GitHub address above, with a savestate if you can.

CREDITS
  Translation, hacking and tools: minhnhattonthat.
  Made with extensive AI assistance (Claude by Anthropic, with Codex by OpenAI for translation and reviews).
  Sakura Note (c) 2009 Marvelous Entertainment. This is an unofficial fan work, not affiliated with them.
