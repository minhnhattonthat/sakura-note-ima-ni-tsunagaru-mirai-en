-- writerlog.lua: log each distinct writer pc (with lr, frame, address, value) for writes to LO..HI.
--   emu.py ROM ... --script tools/debug/writerlog.lua --var LO=0x021BA6D8 --var HI=0x021BA8D8 [--var ALL=1 --var MAX=100]
local lo, hi = assert(LO, "LO"), assert(HI, "HI")
local max, all, n, seen = MAX or 100, ALL, 0, {}
L.on_write(lo, hi, function(addr, size)
  local pc = L.pc()
  local key = pc .. ":" .. (all and addr or 0)
  if seen[key] then return end
  seen[key] = true
  n = n + 1
  if n > max then return end
  L.log(string.format("f%d pc=%08X lr=%08X addr=%08X val=%04X r0=%08X r1=%08X r2=%08X r3=%08X", L.frame, pc,
    memory.getregister("arm9.r14"), addr, memory.readword(addr), memory.getregister("arm9.r0"),
    memory.getregister("arm9.r1"), memory.getregister("arm9.r2"), memory.getregister("arm9.r3")))
end)
