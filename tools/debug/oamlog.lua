-- oamlog.lua: at frames OAM_AT (list), log every visible OAM entry of engine A (0x07000000) or B (ENGINE='B':
-- 0x07000400): index, x, y, shape/size bits, tile, palette.
--   emu.py ROM ... --script tools/debug/oamlog.lua --var "OAM_AT={100,200}"
local base = (ENGINE == "B") and 0x07000400 or 0x07000000
local at = {}
for _, f in ipairs(OAM_AT or { 60 }) do at[f] = true end
L.on_frame(function(n)
  if not at[n] then return end
  for i = 0, 127 do
    local a0 = memory.readword(base + i * 8)
    local a1 = memory.readword(base + i * 8 + 2)
    local a2 = memory.readword(base + i * 8 + 4)
    local hidden = math.floor(a0 / 256) % 4 == 2  -- Lua 5.1: no bit operators
    if not hidden then
      local y, x = a0 % 256, a1 % 512
      if x >= 256 then x = x - 512 end
      L.log(string.format("f%d oam%d x=%d y=%d shape=%d size=%d tile=%d pal=%d a0=%04X a1=%04X a2=%04X", n, i, x, y,
        math.floor(a0 / 16384), math.floor(a1 / 16384), a2 % 1024, math.floor(a2 / 4096), a0, a1, a2))
    end
  end
end)
