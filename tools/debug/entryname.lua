-- entryname.lua: chosen object scripts start at another function than StartScript (text coverage of NPC talk).
--   --script tools/debug/warp.lua --script tools/debug/entryname.lua --var "NPCS='1144,1145'"
--   [--var "ENTRY='NearScript'"] [--var "NPCFILE='work/qa/npcs.txt'"]
-- The engine finds a script's entry function by name, in the same frame the script's FILEDATA entry opens. When one
-- of the NPCS ids (or the ids listed in NPCFILE, whitespace separated) opens, this writes ENTRY (at most 11
-- characters) over every arm9 copy of "StartScript" and restores them on the next frame, so that object runs ENTRY
-- (an NPC's NearScript holds its talk text) as soon as it spawns. Patching later than the open frame is too late;
-- patching during the map script's own start breaks the map. Logs "ENTRY <id> <frame>".
local ORIG_NAME = "StartScript"
local COPIES = { 0x02096298, 0x020962B4, 0x020962C8, 0x020962D4, 0x020A4514, 0x020A4520 }
local entry = ENTRY or "NearScript"
assert(#entry <= #ORIG_NAME, "entryname.lua: ENTRY longer than StartScript")
local want = {}
for id in (NPCS or ""):gmatch("%d+") do want[tonumber(id)] = true end
if NPCFILE then
  local f = assert(io.open(NPCFILE, "r"))
  for id in f:read("*a"):gmatch("%d+") do want[tonumber(id)] = true end
  f:close()
end
local restore_at

local function put(s)
  for _, at in ipairs(COPIES) do
    for i = 1, #ORIG_NAME + 1 do
      memory.writebyte(at + i - 1, i <= #s and s:byte(i) or 0)
    end
  end
end

L.on_exec(0x0202D158, function()
  local id = memory.getregister("arm9.r4")
  if want[id] then
    put(entry)
    restore_at = L.frame + 1
    L.log(string.format("ENTRY %d %d", id, L.frame))
  end
end)

L.on_frame(function(n)
  if restore_at and n >= restore_at then
    put(ORIG_NAME)
    restore_at = nil
  end
end)
