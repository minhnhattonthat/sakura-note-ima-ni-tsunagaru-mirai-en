-- textlog.lua: text coverage probe. Logs "TEXT <hash>" once per distinct string the text engine expands.
--   emu.py ROM ... --script tools/debug/textlog.lua [--var RAW=1]
-- Hook: 0x0203764C, the text engine's expand routine (variables, codes), r1 = the source string (u16 codes up to
-- FFFD; docs/re/nameentry.md). The message files sit raw in heap RAM, so addresses move; the key is a hash of the
-- string's codes instead, the same one tools/textcover_keys.py computes from the build (build/strings.tsv):
--   h = 7; for each u16 code c before FFFD: h = (h * 31 + c) mod 2147483629; key = h, as 8 hex digits.
-- RAW=1 also logs the first 8 codes (to compare with the build's encoding).
local SEEN, MOD = {}, 2147483629
L.on_exec(0x0203764C, function()
  local p = memory.getregister("arm9.r1")
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
    L.log(string.format("TEXT %s f%d p=%08X n=%d %s", key, L.frame, p, n, table.concat(first, " ")))
  else
    L.log("TEXT " .. key)
  end
end)
