-- glyphlog.lua: log every glyph the text engine draws: blit entry, font handle (ctx+0x54), code, x, y.
--   emu.py ROM --script tools/debug/glyphlog.lua [--var FROM=0 --var TO=1e9]
-- Blit routines (docs/re/vwf.md): 0x02037FA0 (normal), 0x020382D0, 0x020385E4 (other draw modes); args r0 ctx,
-- r3 code, [sp] x, [sp+4] y.
local from, to = FROM or 0, TO or math.huge
local function rd(a) return memory.readdword(a) end
for _, fn in ipairs({ 0x02037FA0, 0x020382D0, 0x020385E4 }) do
  L.on_exec(fn, function()
    if L.frame < from or L.frame > to then return end
    local r0 = memory.getregister("arm9.r0")
    local r3 = memory.getregister("arm9.r3")
    local sp = memory.getregister("arm9.r13")
    L.log(string.format("f%d blit=%08X ctx=%08X font=%d code=%04X x=%d y=%d", L.frame, fn, r0,
      rd(r0 + 0x54), r3 % 0x10000, rd(sp), rd(sp + 4)))
  end)
end
