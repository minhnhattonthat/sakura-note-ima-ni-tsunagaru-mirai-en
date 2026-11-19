-- readlog.lua: log each distinct reader pc (with lr, frame, address, registers) for reads of LO..HI from frame FROM.
--   emu.py ROM ... --script tools/debug/readlog.lua --var LO=0x021BC4CA --var HI=0x021BC4F2 [--var FROM=1700 --var MAX=100]
-- Finds which routine reads a buffer (e.g. the name-entry field drawer reading the name being edited).
local lo, hi = assert(LO, "LO"), assert(HI, "HI")
local max, from, n, seen = MAX or 100, FROM or 0, 0, {}
L.on_read(lo, hi, function(addr, size)
  if L.frame < from then return end
  local pc = L.pc()
  if seen[pc] then return end
  seen[pc] = true
  n = n + 1
  if n > max then return end
  L.log(string.format("f%d pc=%08X lr=%08X addr=%08X r0=%08X r1=%08X r2=%08X r3=%08X r4=%08X r5=%08X", L.frame, pc,
    memory.getregister("arm9.r14"), addr, memory.getregister("arm9.r0"), memory.getregister("arm9.r1"),
    memory.getregister("arm9.r2"), memory.getregister("arm9.r3"), memory.getregister("arm9.r4"),
    memory.getregister("arm9.r5")))
end)
