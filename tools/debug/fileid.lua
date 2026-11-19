-- fileid.lua: log every FILEDATA.BIN entry the game opens (frame, file id), and optionally swap one.
-- 0x0202D158 sits inside the entry-open routine, before it seeks to 0x10 + id*8; r4 = file id.
--   emu.py ROM --out DIR --route r.txt --script tools/debug/fileid.lua [--var SWAP_FROM=2477 --var SWAP_TO=2494]
L.on_exec(0x0202D158, function()
  local id = memory.getregister("arm9.r4")
  if SWAP_FROM and id == SWAP_FROM then
    memory.setregister("arm9.r4", SWAP_TO)
    L.log(string.format("SWAP %d %d -> %d", L.frame, id, SWAP_TO))
    id = SWAP_TO
  end
  L.log(string.format("FILE %d %d", L.frame, id))
end)
