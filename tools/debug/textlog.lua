-- textlog.lua: text coverage probe. Logs "TEXT <hash>" once per distinct string the text engine expands.
--   emu.py ROM ... --script tools/debug/textlog.lua [--var RAW=1]
-- Hook: 0x0203764C, the text engine's expand routine (variables, codes), r1 = the source string (u16 codes up to
-- FFFD; docs/re/nameentry.md). The message files sit raw in heap RAM, so addresses move; the key is a hash of the
-- string's codes instead, the same one tools/textcover_keys.py computes from the build (build/strings.tsv):
--   h = 7; for each u16 code c before FFFD: h = (h * 31 + c) mod 2147483629; key = h, as 8 hex digits.
-- RAW=1 also logs the first 8 codes (to compare with the build's encoding).
-- Second hook: 0x02037448 inside the message fetch 0x0203742C (r1 = message file id, r2 = index; it loads the file
-- with 0x0202D4C8 and copies one string out): r4 = file base, r6 = index, body = r4 + [r4 + 4*r6] + 4 (after the
-- 2-word header). Item names, map names, menu and board text are fetched there without passing the expand routine.
local SEEN, MOD = {}, 2147483629
local function hash_at(p, tag)
  local h, n = 7, 0
  local first = {}
  while n < 1024 do
    local c = memory.readword(p + 2 * n)
    if c == 0xFFFD then break end
    h = (h * 31 + c) % MOD
    if n < 8 then first[#first + 1] = string.format("%04X", c) end
    n = n + 1
  end
  local key = string.format("%08X", h)
  if SEEN[key] then return end
  SEEN[key] = true
  if RAW then
    L.log(string.format("TEXT %s %s f%d p=%08X n=%d %s", key, tag, L.frame, p, n, table.concat(first, " ")))
  else
    L.log("TEXT " .. key)
  end
end
L.on_exec(0x0203764C, function() hash_at(memory.getregister("arm9.r1"), "x") end)
L.on_exec(0x02037448, function()
  local base, i = memory.getregister("arm9.r4"), memory.getregister("arm9.r6")
  hash_at(base + memory.readdword(base + 4 * i) + 4, "m")
end)
-- The twin fetch 0x020374C4 (same shape, other registers): r5 = base, r4 = index at 0x020374DC.
L.on_exec(0x020374DC, function()
  local base, i = memory.getregister("arm9.r5"), memory.getregister("arm9.r4")
  hash_at(base + memory.readdword(base + 4 * i) + 4, "m")
end)
-- Third hook: 0x020361F0 in the speaker-tag loader 0x020360F4 (2610 by header word0; indices 0-4 come from the save's
-- names instead): r4 = 2610's base, r6 = index, same body formula.
L.on_exec(0x020361F0, function()
  local base, i = memory.getregister("arm9.r4"), memory.getregister("arm9.r6")
  hash_at(base + memory.readdword(base + 4 * i) + 4, "t")
end)
