# Build checks (phase 7)

All run from `python -X utf8 tools/check.py` (the pre-commit hook); the ROM-level audit builds its own ROM in
`tests/test_romcheck.py`, so a stale `build/` file can't pass it.

**Text lint** (`tools/batches.py check`, every shipped English line; `tests/test_batches.py`):
pixel width per box form from the VWF widths (`docs/re/boxes.md`), lines per page, control-code multiset JP == EN
(layout codes `{n} {page} {sp}` free), encodable characters, glossary terms and Avoid spellings, honorifics, no
suffix glued onto a drawn name, leading/trailing blanks kept in label forms (menu, button, panel, slot, tag: room
for a cursor or padding; full-width indents in dialogue/profile/credits are typography and not checked), no page
of a paragraph ending on a stub line under 6 characters (a drawn name counts 5).

**ROM audit** (`tools/romcheck.py [BUILT]`, uses `<built>.writes.txt`): a raw byte diff is useless (arm9 grows, so
NitroFS moves every file), so it compares leaf by leaf:
- header: only the offset/size words ndspy relays out and a valid header CRC differ;
- arm7, overlay tables, overlay 0, banner, file names, every other NitroFS file: identical;
- overlay 1: only the credits-x writes, each at a credits call's `mov r2` (`docs/re/credits.md`);
- arm9: same autoload sections + the VWF block (= `vwf.hook_block()`); section 0 passes `romdiff.check` with the
  write log (original bytes as logged, no overlap, nothing overwritten, no unlogged change) apart from the
  module-params autoload words ndspy rewrites; no branch lands strictly inside a hook span;
- FILEDATA: same entry count, only fonts 860/872 and message files 2495-2616 change; font bytes only inside the
  English cells;
- message files: same string count and header words; no Japanese string without English unless status `data`;
  untranslated strings byte-identical; each translated string decodes back to exactly its script English, keeps
  the JP's control codes and passes the width lint;
- arm9 string slots decode back to their English.

Every write into a fixed binary goes through `tools/writelog.put()` (`TARGET OFFSET ORIG NEW writer` lines).
Tampering tests in `tests/test_romcheck.py`: a stray arm9 byte, a wrong logged original, an unlogged hook or
credits write, a changed NitroFS file, a script/ROM text mismatch.
