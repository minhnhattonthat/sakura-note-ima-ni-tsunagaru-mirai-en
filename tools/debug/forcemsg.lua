-- forcemsg.lua: text coverage by forcing. Rewrites the message fetch so a host scene shows chosen strings.
--   emu.py ROM ... --script tools/debug/warp.lua --script tools/debug/textlog.lua --script tools/debug/forcemsg.lua
--     --var "FORCE='2512:11,2512:12'" [--var "HOST='2495-2603'"] [--var "FETCH='a'"]
-- The engine reads every message through 0x0203742C (with the 4-byte header: dialogue, narration) or its twin
-- 0x020374C4 (no header: menus, lists); both take r1 = message file id, r2 = index at entry and load the file
-- themselves (docs/re/scripts.md §Coverage). Each fetch whose original file id lies in HOST gets the next FORCE
-- target instead (r1/r2 rewritten at entry), so the host scene's own box draws it and textlog.lua (hooked later in
-- the same routine) logs the forced string. A repeat of the same original (file, index) within 60 frames keeps the
-- same target (the engine may fetch one message twice). FETCH: 'a' = 0x0203742C only (default), 'b' = the twin
-- only, 'ab' = both. Logs "FORCE <frame> <orig> -> <target>" and "FORCE_DONE" once the queue is empty.
-- FETCHLOG=1 (with FETCH='ab') logs every fetch "FETCH a|b <frame> <file>:<index>" before any rewrite.
local Q = {}
for f, i in (FORCE or ""):gmatch("(%d+):(%d+)") do Q[#Q + 1] = { tonumber(f), tonumber(i) } end
local lo, hi = (HOST or "2495-2603"):match("^(%d+)-(%d+)$")
lo, hi = tonumber(lo), tonumber(hi)
local which = FETCH or "a"
local nxt, last_key, last_frame, last_t = 1, nil, -1000, nil

local function force(tag)
  local f, i = memory.getregister("arm9.r1"), memory.getregister("arm9.r2")
  if FETCHLOG then L.log(string.format("FETCH %s %d %d:%d", tag, L.frame, f, i)) end
  if f < lo or f > hi then return end
  local key = f * 65536 + i
  local t
  if key == last_key and L.frame - last_frame < 60 then
    t = last_t
  elseif nxt <= #Q then
    t = Q[nxt]
    nxt = nxt + 1
    if nxt > #Q then L.log(string.format("FORCE_DONE %d", L.frame)) end
  end
  last_key, last_frame, last_t = key, L.frame, t
  if not t then return end
  memory.setregister("arm9.r1", t[1])
  memory.setregister("arm9.r2", t[2])
  L.log(string.format("FORCE %s %d %d:%d -> %d:%d", tag, L.frame, f, i, t[1], t[2]))
end
if which:find("a") then L.on_exec(0x0203742C, function() force("a") end) end
if which:find("b") then L.on_exec(0x020374C4, function() force("b") end) end
