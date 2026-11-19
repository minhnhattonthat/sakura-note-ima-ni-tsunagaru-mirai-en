-- reglog.lua: log r0-r3 and [sp] each time PC reaches ADDR (first MAX hits); R0_WORDS = offsets to read from r0.
--   emu.py ROM ... --script tools/debug/reglog.lua --var ADDR=0x02038684 [--var MAX=20] [--var "R0_WORDS={0x1e4,0x1ec}"]
local addr, max, n = assert(ADDR, "set --var ADDR=0x..."), MAX or 20, 0
local words = R0_WORDS or {}
L.on_exec(addr, function()
  n = n + 1
  if n > max then return end
  local g = function(r) return memory.getregister("arm9." .. r) end
  local extra = {}
  for _, o in ipairs(words) do
    extra[#extra + 1] = string.format("[r0+%X]=%08X", o, memory.readdword(g("r0") + o))
  end
  L.log(string.format("f%d pc=%08X r0=%08X r1=%08X r2=%08X r3=%08X sp0=%08X %s", L.frame, addr, g("r0"), g("r1"),
    g("r2"), g("r3"), memory.readdword(g("r13")), table.concat(extra, " ")))
end)
