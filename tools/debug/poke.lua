-- poke.lua: write bytes into RAM at frame AT (default 10), e.g. to find which state bytes a menu reads.
--   emu.py ROM --state-in S.dst --route-str "..." --script tools/debug/poke.lua --var LO=0x021C0900 --var HI=0x021C0940
--   [--var VAL=0xFF] [--var AT=10]
-- Writes VAL to every byte in [LO, HI) once, logs "POKE lo hi val".
local at, val = AT or 10, VAL or 0xFF
local done = false
L.on_frame(function(n)
  if not done and n >= at then
    for a = LO, HI - 1 do memory.writebyte(a, val) end
    L.log(string.format("POKE %08X %08X %02X", LO, HI, val))
    done = true
  end
end)
