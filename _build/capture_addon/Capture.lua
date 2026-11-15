local _, ns = ...

--[[
Easy BIS capture: a developer's tool, not a part of the published addon.

ForeverDB's data lacks the healing and spell damage of most caster weapons
(Easy BIS, _build/corrections.py). This reads the tooltip of every item
listed in Ids.lua as the game shows it and keeps the text in
EasyBISCaptureDB, which `python -I _build/build.py --check-capture` compares
with the data and `--import-capture` turns into corrections. It is installed
next to Easy BIS by `python -I _build/build.py --capture-tool`, which also
writes Ids.lua.

  /ebiscapture          read the items not read yet (goes on where it stopped)
  /ebiscapture all      forget what was read and start again
  /ebiscapture stop     stop
  /ebiscapture status   say where it is

The saved variable is plain text, so the generator reads it without running it:
  EasyBISCaptureDB = {
      meta = "format|game version|build|locale|date",
      items = { [item id] = "line\nline\n...\n#stats KEY=value;KEY=value" },
      missing = "id id id",        -- the items the game did not show
  }
A line is a tooltip line: its left text, then a tab and its right text when it
has one. The stats are the game's own item stat table (C_Item.GetItemStats).
]]

local FORMAT = 1
local BATCH = 8      -- items looked at per step
local STEP = 0.25    -- seconds between two steps
local PASSES = 4     -- times an item the game has not loaded yet is asked for
local PAUSE = 3      -- seconds to let the game answer before asking again
local EVERY = 500    -- items between two progress lines

local PREFIX = "|cff33ff99Easy BIS capture|r: "

local function Say(text)
    print(PREFIX .. text)
end

---------------------------------------------------------------------------
-- Reading one item
---------------------------------------------------------------------------

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo

-- A piece of text the tooltip may hand out (the game hides some values in combat).
local function Text(value)
    if issecretvalue and issecretvalue(value) then return nil end
    if type(value) ~= "string" or value == "" then return nil end
    return (value:gsub("[\r\n\t]+", " "))
end

local function Join(left, right)
    left, right = Text(left), Text(right)
    if not left then return nil end
    return right and (left .. "\t" .. right) or left
end

local scanner

-- The tooltip's lines through a hidden tooltip, for a client without C_TooltipInfo.
local function ScannedLines(id)
    local lines = {}
    if not scanner then
        scanner = CreateFrame("GameTooltip", "EasyBISCaptureTooltip", nil, "GameTooltipTemplate")
    end
    scanner:SetOwner(WorldFrame, "ANCHOR_NONE")
    scanner:ClearLines()
    if not pcall(scanner.SetHyperlink, scanner, "item:" .. id) then return lines end
    for index = 1, scanner:NumLines() do
        local left = _G["EasyBISCaptureTooltipTextLeft" .. index]
        local right = _G["EasyBISCaptureTooltipTextRight" .. index]
        local line = Join(left and left:GetText(), right and right:GetText())
        if line then lines[#lines + 1] = line end
    end
    scanner:Hide()
    return lines
end

local function TooltipLines(id)
    local lines = {}
    if C_TooltipInfo and C_TooltipInfo.GetItemByID then
        local ok, data = pcall(C_TooltipInfo.GetItemByID, id)
        if ok and type(data) == "table" and type(data.lines) == "table" then
            for _, entry in ipairs(data.lines) do
                local line = Join(entry.leftText, entry.rightText)
                if line then lines[#lines + 1] = line end
            end
        end
        return lines
    end
    return ScannedLines(id)
end

-- "KEY=value;KEY=value", the keys in order: the game's own stat table for the item.
local function Stats(id)
    local stats
    local link = "item:" .. id
    if C_Item and C_Item.GetItemStats then
        local ok, result = pcall(C_Item.GetItemStats, link)
        if ok and type(result) == "table" then stats = result end
    end
    if not stats and GetItemStats then
        local ok, result = pcall(GetItemStats, link)
        if ok and type(result) == "table" then stats = result end
    end
    local out = {}
    for key, value in pairs(stats or {}) do
        if type(key) == "string" and type(value) == "number" then
            out[#out + 1] = key .. "=" .. value
        end
    end
    table.sort(out)
    return table.concat(out, ";")
end

-- Whether the game has the item's data; asking for it starts the request.
local function Loaded(id)
    if C_Item and C_Item.IsItemDataCachedByID then
        local ok, cached = pcall(C_Item.IsItemDataCachedByID, id)
        if ok and cached then return true end
    end
    if GetInfo then
        local ok, name = pcall(GetInfo, id)
        if ok and name ~= nil then return true end
    end
    return false
end

local function Ask(id)
    if C_Item and C_Item.RequestLoadItemDataByID then
        pcall(C_Item.RequestLoadItemDataByID, id)
    end
end

-- Keeps the item's tooltip; false while the game shows nothing but a name.
local function Read(id)
    local lines = TooltipLines(id)
    if #lines < 2 then return false end
    EasyBISCaptureDB.items[id] = table.concat(lines, "\n") .. "\n#stats " .. Stats(id)
    return true
end

---------------------------------------------------------------------------
-- Going through the list, a few weapons at a time
---------------------------------------------------------------------------

local run     -- the capture under way: { list, index, later, pass, wait, read, said }
local driver = CreateFrame("Frame")

local function Count(items)
    local count = 0
    for _ in pairs(items) do count = count + 1 end
    return count
end

local function Finish(stopped)
    driver:SetScript("OnUpdate", nil)
    local missing = run.later
    for index = run.index, #run.list do missing[#missing + 1] = run.list[index] end
    table.sort(missing)
    EasyBISCaptureDB.missing = table.concat(missing, " ")
    Say(("%s: %d items read now, %d in all, %d the game did not show."):format(
        stopped and "stopped" or "done", run.read, Count(EasyBISCaptureDB.items), #missing))
    Say("Type /reload to save, then run: python -I _build/build.py --check-capture")
    run = nil
end

local function Step()
    local handled = 0
    while handled < BATCH and run.index <= #run.list do
        local id = run.list[run.index]
        run.index = run.index + 1
        handled = handled + 1
        if Loaded(id) and Read(id) then
            run.read = run.read + 1
        else
            Ask(id)
            run.later[#run.later + 1] = id
        end
    end
    if run.read - run.said >= EVERY then
        run.said = run.read
        Say(("%d items read..."):format(run.read))
    end
    if run.index > #run.list then
        if #run.later == 0 or run.pass >= PASSES then
            Finish(false)
            return
        end
        Say(("%d items not loaded yet: asking again (%d of %d)."):format(#run.later, run.pass, PASSES - 1))
        run.list, run.later, run.index = run.later, {}, 1
        run.pass, run.wait = run.pass + 1, PAUSE
    end
end

local function OnUpdate(_, elapsed)
    run.wait = run.wait - elapsed
    if run.wait > 0 then return end
    run.wait = STEP
    Step()
end

local function Ids()
    local ids = {}
    for id in (ns.ids or ""):gmatch("%d+") do ids[#ids + 1] = tonumber(id) end
    return ids
end

local function Start(again)
    if run then
        Say("already reading. /ebiscapture stop to stop.")
        return
    end
    if InCombatLockdown and InCombatLockdown() then
        Say("not in combat: the game hides tooltip values there.")
        return
    end
    local version, build = GetBuildInfo()
    local game = table.concat({ version or "?", build or "?", GetLocale and GetLocale() or "?" }, "|")
    local db = EasyBISCaptureDB
    local same = type(db) == "table" and type(db.items) == "table" and type(db.meta) == "string"
        and db.meta:match("^%d+|(.*)|[^|]*$") == game
    if again or not same then db = { items = {} } end   -- another game build: its tooltips may have changed
    db.meta = table.concat({ FORMAT, game, date("%Y-%m-%d %H:%M") }, "|")
    db.missing = ""
    EasyBISCaptureDB = db

    local list = {}
    for _, id in ipairs(Ids()) do
        if not db.items[id] then list[#list + 1] = id end
    end
    if #list == 0 then
        Say("every item of the list is read already. /ebiscapture all starts again.")
        return
    end
    run = { list = list, index = 1, later = {}, pass = 1, wait = 0, read = 0, said = 0 }
    local seconds = math.ceil(#list / BATCH * STEP)
    Say(("reading %d item tooltips, about %s. Stay out of combat."):format(
        #list, seconds > 90 and (math.ceil(seconds / 60) .. " minutes") or (seconds .. " seconds")))
    driver:SetScript("OnUpdate", OnUpdate)
end

SLASH_EASYBISCAPTURE1 = "/ebiscapture"
SlashCmdList["EASYBISCAPTURE"] = function(message)
    local command = (message or ""):lower():match("^%s*(%S*)")
    if command == "" then
        Start(false)
    elseif command == "all" then
        Start(true)
    elseif command == "stop" then
        if run then Finish(true) else Say("not reading.") end
    elseif command == "status" then
        if run then
            Say(("%d read, %d to go (pass %d)."):format(run.read, #run.list - run.index + 1 + #run.later, run.pass))
        else
            local db = EasyBISCaptureDB
            Say(("not reading. %d items kept from the last time."):format(
                type(db) == "table" and type(db.items) == "table" and Count(db.items) or 0))
        end
    else
        Say("/ebiscapture, /ebiscapture all, /ebiscapture stop, /ebiscapture status")
    end
end

ns.Capture = { Start = Start, Step = Step, Ids = Ids }   -- for the tests
