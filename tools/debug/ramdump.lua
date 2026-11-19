-- ramdump.lua: dump main RAM (4 MB at 0x02000000) to OUT/ram_f<frame>.bin at frame AT (default: the last frame of
-- the route, i.e. when the route is done), then stop.
--   emu.py ROM --state-in S.dst --route-str "..." --script tools/debug/ramdump.lua [--var AT=120]
local at = AT
L.on_frame(function(n)
  if (at and n >= at) or (not at and L.route_done()) then
    L.dump_ram(string.format("ram_f%d.bin", n))
    L.log(string.format("RAMDUMP f%d", n))
    L.finish(0)
  end
end)
