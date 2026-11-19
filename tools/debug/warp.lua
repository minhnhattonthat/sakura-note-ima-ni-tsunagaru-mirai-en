-- warp.lua: cold boot straight into any scene of tools/debug/scenes.tsv (Sakura Note, NDS).
--
--   emu.py ROM --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='ending'" --frames 900 --sheet
--   SCENE may also be a raw key program: --var "SCENE='debug:a a w60 a'"
--
-- How it works (docs/re/debug.md): the boot script is FILEDATA 2477 (title). When the game opens it, this hook
-- swaps the id for 2494, the leftover debug script, whose StartScript draws the developers' debug menu (scene,
-- battle, BG, OBJ, sound, opening, ending, game over, event, extras). Scenes with mode "title" boot normally.
-- The key program then walks the menus. Tokens (space separated):
--   a b x y l r start select up down left right   press 6 frames, then release 40 (menus drop faster presses)
--   tX,Y        touch the bottom screen at X,Y (6 frames)
--   wN          wait N frames
--   fID         wait until FILEDATA entry ID is opened at or after the last press (or boot when none yet),
--               so "a f984" also passes when the load happened during a wait between them (timeout 3000 -> WARP_FAIL)
--   down*N      repeat a press N times
--   hKEY:N      hold KEY for N frames, no release gap (walking: hleft:50 hdown:80)
-- When the program ends the log gets "WARP_OK <scene> frame <n>"; the scene's `expect` file id (if any) must have
-- loaded by then or the run exits 3 with WARP_FAIL. Opt-in: STOP_AFTER=N ends the run N frames later (final.png,
-- --state-out); tools/debug/warp_all.py runs every scene that way. FILELOG=1 logs every file open.

local REPO = OUT:match("^(.*)/work/") or error("warp.lua: --out must be under <repo>/work/")
local TSV = SCENES or (REPO .. "/tools/debug/scenes.tsv")
local BOOT_SCRIPT, DEBUG_SCRIPT = 2477, 2494
local FILE_OPEN_PC = 0x0202D158 -- inside the FILEDATA entry-open routine, r4 = entry id (docs/re/debug.md)

local function load_scenes()
  local t, n = {}, 0
  for line in io.lines(TSV) do
    n = n + 1
    if n > 1 and line ~= "" and line:sub(1, 1) ~= "#" then
      local c = {}
      for f in (line .. "\t"):gmatch("([^\t]*)\t") do c[#c + 1] = f end
      t[c[1]] = { mode = c[2], keys = c[3], expect = tonumber(c[4]) }
    end
  end
  return t
end

local name = SCENE or error("warp.lua: pass --var \"SCENE='name'\"")
local sc
local raw_mode, raw_keys = name:match("^(%a+):(.*)$")
if raw_mode then
  sc = { mode = raw_mode, keys = raw_keys }
else
  sc = load_scenes()[name] or error("warp.lua: unknown scene " .. name .. " (see " .. TSV .. ")")
end

-- file-open log + boot-script swap
local opened = {}
L.on_exec(FILE_OPEN_PC, function()
  local id = memory.getregister("arm9.r4")
  if sc.mode == "debug" and id == BOOT_SCRIPT then
    memory.setregister("arm9.r4", DEBUG_SCRIPT)
    id = DEBUG_SCRIPT
  end
  opened[id] = L.frame -- last open
  if FILELOG then L.log(string.format("FILE %d %d", L.frame, id)) end
end)

-- key program
local prog = {}
for tok in sc.keys:gmatch("%S+") do
  local base, rep = tok:match("^(.-)%*(%d+)$")
  for _ = 1, tonumber(rep or 1) do prog[#prog + 1] = base or tok end
end

local pc, wait_until, wait_file, wait_since, wait_start, last_press, done, done_at = 1, 0, nil, 0, 0, 0, false, 0
local function step()
  while pc <= #prog do
    local tok = prog[pc]
    pc = pc + 1
    local n = tok:match("^w(%d+)$")
    if n then wait_until = L.frame + tonumber(n); return end
    local f = tok:match("^f(%d+)$")
    if f then wait_file = tonumber(f); wait_since = last_press; wait_start = L.frame; return end
    last_press = L.frame
    local hk, hn = tok:match("^h(%a+):(%d+)$")
    if hk then L.press(hk, tonumber(hn)); wait_until = L.frame + tonumber(hn); return end
    L.press(tok, 6); L.press("-", 40); wait_until = L.frame + 46
    return
  end
  done = true
  if sc.expect and not opened[sc.expect] then
    L.log(string.format("WARP_FAIL %s: file %d never opened", name, sc.expect))
    L.finish(3)
  end
  L.log(string.format("WARP_OK %s frame %d", name, L.frame))
  done_at = L.frame
end

L.on_frame(function()
  if done then
    -- STOP_AFTER=N: end the run N frames after the program (final.png + --state-out, as at the frame limit)
    if STOP_AFTER and L.frame >= done_at + STOP_AFTER then
      L.shot("final.png")
      if STATE_OUT then savestate.save(STATE_OUT) end
      L.finish(0)
    end
    return
  end
  if wait_file then
    if (opened[wait_file] or -1) >= wait_since then wait_file = nil
    elseif L.frame - wait_start > 3000 then
      L.log(string.format("WARP_FAIL %s: waited 3000 frames for file %d", name, wait_file))
      L.finish(3)
    else return end
  end
  if L.frame < wait_until or not L.route_done() then return end
  step()
end)
