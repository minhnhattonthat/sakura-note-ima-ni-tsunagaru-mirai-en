-- callerlog.lua: at ADDR, log lr, r0-r5, STACK words from sp (default 2) and the frame, once per distinct lr (or
-- every hit: ALL=1).
--   emu.py ROM ... --script tools/debug/callerlog.lua --var ADDR=0x02037FA0 [--var ALL=1 --var MAX=200 --var FROM=N]
-- Finds who calls a routine (e.g. which loop draws the credits' glyphs and where its x comes from).
local addr, max, all, n, from = assert(ADDR, "set --var ADDR=0x..."), MAX or 200, ALL, 0, FROM or 0
local seen = {}
L.on_exec(addr, function()
  if L.frame < from then return end
  local g = function(r) return memory.getregister("arm9." .. r) end
  local lr = g("r14")
  if not all and seen[lr] then return end
  seen[lr] = true
  n = n + 1
  if n > max then return end
  local sp = g("r13")
  local st = {}
  for k = 0, (STACK or 2) - 1 do st[#st + 1] = string.format("%08X", memory.readdword(sp + 4 * k)) end
  L.log(string.format("f%d pc=%08X lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X r4=%08X r5=%08X stack=%s", L.frame, addr,
    lr, g("r0"), g("r1"), g("r2"), g("r3"), g("r4"), g("r5"), table.concat(st, " ")))
end)
