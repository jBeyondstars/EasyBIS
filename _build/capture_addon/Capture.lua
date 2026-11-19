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

The game gets an item's data from the server when it is asked for, and it
does not always answer: on 2026-11-15 two runs that asked for 8,600 items got
nothing back for half an hour, and a third, an hour later, got them all at 32
a second. The cause is not known. Nor does it ever answer for an item it
does not have, though the client's own table lists it: on 2026-11-18 and
2026-11-19 every capture stopped on such items, so Ids.lua puts the groups
they are in last (capture.ORDER). So only a few items are waited for at a
time, and a few asked for per second. When nothing has arrived for STALL
seconds the capture says so, waits and tries again; after GIVE_UP seconds of
silence it stops by itself. What was read is kept: /ebiscapture goes on from
there, later.

The saved variable is plain text, so the generator reads it without running it:
  EasyBISCaptureDB = {
      meta = "format|game version|build|locale|date",
      items = { [item id] = "line\nline\n...\n#use spell\tname\tdescription\n#stats KEY=value;KEY=value" },
      missing = "id id id",        -- the items of the list that were not read
      absent = "id id id",         -- of those, the ones the game's own item table does not list: not asked for
      sample = "asked:answered",   -- a few of the absent ones were asked for all the same, as a check
      log = "hour clock:read:asked:unanswered:quiet ...",   -- how the game answered, every LOG seconds
  }
A line is a tooltip line: its left text, then a tab and its right text when it
has one. The stats are the game's own item stat table (C_Item.GetItemStats).
The #use line is there for an item that casts a spell when used, when the game
says which: what a consumable does is that spell's description.

Opening the window of a vendor who takes something else than money keeps what
it shows, without a command. `python -I _build/build.py --import-prices` lays
that over _build/corrections/costs.json. In the same saved variable:
  vendors = { ["v<npc id>"] = "format|game version|build|locale|date|vendor's name\n<row>\n<row>..." }
A row is: item id, tab, name, tab, price in copper, tab, what else it costs, by
semicolons: i<item id>:<amount>, c<currency id>:<amount>, or n<name>:<amount>
when the game gives nothing but a name. A window may show a class only what it
can use, so the rows read in one game build add up from one window to the next.
]]

local FORMAT = 1
local VENDOR_FORMAT = 1
local VENDOR_TRIES = 8    -- times a window is read again while the game fetches what it shows
local VENDOR_WAIT = 0.5   -- seconds between two of them
local STEP = 0.25     -- seconds between two steps
local WINDOW = 8      -- items asked for and not answered yet, at most
local ASKS = 3        -- items asked for per step, at most: 12 a second
local LOOK = 40       -- items looked at per step, at most: the ones the game has already are read at once
local TIMEOUT = 12    -- seconds an item is waited for before another takes its place
local STALL = 45      -- seconds without anything read after which the game is taken not to answer
local QUIET = { 15, 30, 60, 120 }   -- seconds waited before trying again, longer each time
local GIVE_UP = 300   -- seconds without anything read after which the capture stops
local RETRY = 200     -- items not answered for that are asked for once more at the end, when no more than this
local SAMPLE = 16     -- items the game's table does not list that are asked for all the same
local SAY = 30        -- seconds between two progress lines
local LOG = 10        -- seconds between two entries of the log
local SPELL_TRIES = 8 -- steps an item waits for the description of the spell it casts, at most: 2 seconds

local PREFIX = "|cff33ff99Easy BIS capture|r: "

local function Say(text)
    print(PREFIX .. text)
end

---------------------------------------------------------------------------
-- Reading one item
---------------------------------------------------------------------------

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetInstant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant
local IsCached = C_Item and C_Item.IsItemDataCachedByID

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

-- Whether the game's own item table lists the item. It answers at once, without the server.
local function Listed(id)
    if not GetInstant then return true end
    local ok, known = pcall(GetInstant, id)
    return not ok or known ~= nil
end

-- Whether the game has the item's data. GetItemInfo sends a request of its own for an item the
-- game does not have, so it is only used on an item that was asked for (`asked`).
local function Loaded(id, asked)
    if IsCached then
        local ok, cached = pcall(IsCached, id)
        if ok then return cached == true end
    end
    if asked and GetInfo then
        local ok, name = pcall(GetInfo, id)
        return ok and name ~= nil
    end
    return false
end

local function Ask(id)
    if C_Item and C_Item.RequestLoadItemDataByID then
        pcall(C_Item.RequestLoadItemDataByID, id)
    elseif GetInfo then
        pcall(GetInfo, id)
    end
end

local GetSpell = (C_Item and C_Item.GetItemSpell) or GetItemSpell
local Describe = (C_Spell and C_Spell.GetSpellDescription) or GetSpellDescription
local LoadSpell = C_Spell and C_Spell.RequestLoadSpellData
local spellTries = {}

-- The "#use" line of an item that casts a spell, or nil; and false while the description is on its way.
local function UseLine(id)
    if not GetSpell then return nil, true end
    local ok, name, spell = pcall(GetSpell, id)
    if not ok or type(spell) ~= "number" then return nil, true end
    local description
    if Describe then
        local done, text = pcall(Describe, spell)
        description = done and Text(text) or nil
    end
    if not description and Describe then
        spellTries[id] = (spellTries[id] or 0) + 1
        if spellTries[id] <= SPELL_TRIES then
            if LoadSpell then pcall(LoadSpell, spell) end
            return nil, false
        end
    end
    return "#use " .. spell .. "\t" .. (Text(name) or "") .. "\t" .. (description or ""), true
end

-- Keeps the item's tooltip; false while the game shows nothing but a name, or has not said yet what the
-- spell it casts does.
local function Read(id)
    local lines = TooltipLines(id)
    if #lines < 2 then return false end
    local use, ready = UseLine(id)
    if not ready then return false end
    if use then lines[#lines + 1] = use end
    EasyBISCaptureDB.items[id] = table.concat(lines, "\n") .. "\n#stats " .. Stats(id)
    spellTries[id] = nil
    return true
end

---------------------------------------------------------------------------
-- Going through the list, a few items at a time
---------------------------------------------------------------------------

--[[ The capture under way:
  ids      the whole list                    absent   the ones the game's table does not list
  queue    what is gone through now, `next` the place in it, `stage` "list", "again" or "sample"
  out      { id, when asked } of the items asked for and waited for
  later    the items not answered for
  clock    seconds of capture, out of combat  wait     seconds to the next step
  heard    when something was last read (or the capture last started asking); answer: the same, kept
           through the waits, for GIVE_UP
  quiet    0 while the game answers, else the place in QUIET; hold: the clock at which to try again
  read, asked, lost   items read, asked for, not answered for
]]
local run
local driver = CreateFrame("Frame")
local SILENT = "stopped, the game does not answer"

local function Count(items)
    local count = 0
    for _ in pairs(items) do count = count + 1 end
    return count
end

local function Duration(seconds)
    if seconds > 90 then return math.ceil(seconds / 60) .. " minutes" end
    return math.ceil(seconds) .. " seconds"
end

local function Log()
    EasyBISCaptureDB.log = EasyBISCaptureDB.log .. (" %d:%d:%d:%d:%d"):format(
        math.floor(run.clock), run.read, run.asked, run.lost, run.quiet)
end

local function Finish(why)
    driver:SetScript("OnUpdate", nil)
    local db = EasyBISCaptureDB
    Log()
    if run.before then db.sample = #run.queue .. ":" .. (run.read - run.before) end
    local missing = {}
    for _, id in ipairs(run.ids) do
        if not db.items[id] then missing[#missing + 1] = id end
    end
    table.sort(missing)
    db.missing = table.concat(missing, " ")
    Say(("%s: %d items read now, %d in all, %d not read."):format(why, run.read, Count(db.items), #missing))
    if why == SILENT then
        Say("What was read is kept. Type /reload to save. To go on: /ebiscapture again later.")
    else
        Say("Type /reload to save, then run: python -I _build/build.py --check-capture")
    end
    run = nil
end

-- The list is gone through: the items not answered for once more when they are few, then a few of
-- the items the game's table does not list, to learn whether that table can be trusted.
local function Next()
    if run.quiet > 0 then   -- the list ended while the game was not answering
        Finish(SILENT)
        return
    end
    if run.stage == "list" and #run.later > 0 and #run.later <= RETRY then
        run.stage = "again"
        run.queue, run.later, run.next = run.later, {}, 1
        Say(("%d items were not answered for: asking once more."):format(#run.queue))
    elseif run.stage ~= "sample" and #run.absent > 0 then
        run.stage = "sample"
        run.queue, run.next, run.before = {}, 1, run.read
        local count = math.min(SAMPLE, #run.absent)
        for index = 1, count do
            run.queue[index] = run.absent[math.floor((index - 1) * #run.absent / count) + 1]
        end
    else
        Finish("done")
        return
    end
    run.heard = run.clock
end

local function Step()
    local now = run.clock
    -- what was asked for: read what has arrived, let go of what was waited for too long
    local waiting = {}
    for _, entry in ipairs(run.out) do
        local id = entry[1]
        if Loaded(id, true) and Read(id) then
            run.read = run.read + 1
            run.heard, run.answer = now, now
            if run.quiet > 0 then
                run.quiet = 0
                Say("the game answers again.")
            end
        elseif now - entry[2] >= TIMEOUT then
            run.later[#run.later + 1] = id
            run.lost = run.lost + 1
        else
            waiting[#waiting + 1] = entry
        end
    end
    run.out = waiting

    if run.hold then
        if now < run.hold then return end
        run.hold, run.heard = nil, now
    end

    -- nothing has arrived for a while: wait before asking again, longer each time, then stop
    if run.stage ~= "sample" and now - run.heard >= STALL then
        local silence = math.floor(now - run.answer)
        local pause = QUIET[math.min(run.quiet + 1, #QUIET)]
        if silence + pause >= GIVE_UP then
            Finish(SILENT)
            return
        end
        for _, entry in ipairs(run.out) do run.later[#run.later + 1] = entry[1] end
        run.lost, run.out = run.lost + #run.out, {}
        run.quiet = math.min(run.quiet + 1, #QUIET)
        run.hold = now + pause
        Say(("the game has not answered for %d seconds (%d read so far): trying again in %d seconds."):format(
            silence, run.read, pause))
        return
    end

    local looked, asked = 0, 0
    while #run.out < WINDOW and asked < ASKS and looked < LOOK and run.next <= #run.queue do
        local id = run.queue[run.next]
        run.next = run.next + 1
        looked = looked + 1
        if Loaded(id) and Read(id) then   -- the game had it already: nothing to ask for
            run.read = run.read + 1
            run.heard, run.answer = now, now
        else
            Ask(id)
            asked = asked + 1
            run.asked = run.asked + 1
            run.out[#run.out + 1] = { id, now }
        end
    end
    if run.next > #run.queue and #run.out == 0 then Next() end
end

local function Progress()
    local now = run.clock
    local pace = (run.read - run.saidRead) / (now - run.said)   -- items a second since the last line
    local left = #run.queue - run.next + 1 + #run.out
    run.said, run.saidRead = now, run.read
    if pace > 0 then
        Say(("%d read, %d to go: %d a minute, about %s left."):format(
            run.read, left, math.floor(pace * 60 + 0.5), Duration(left / pace)))
    else
        Say(("%d read, %d to go: nothing came in the last %d seconds."):format(run.read, left, SAY))
    end
end

local function OnUpdate(_, elapsed)
    if InCombatLockdown and InCombatLockdown() then   -- the game hides tooltip values there
        if not run.combat then
            run.combat = true
            Say("in combat: waiting for its end.")
        end
        return
    end
    run.combat = nil
    if elapsed > 1 then elapsed = 1 end   -- a loading screen is not a silence of the game
    run.clock = run.clock + elapsed
    run.wait = run.wait - elapsed
    if run.wait > 0 then return end
    run.wait = STEP
    Step()
    if not run then return end
    if run.clock - run.logged >= LOG then
        run.logged = run.clock
        Log()
    end
    if run.clock - run.said >= SAY and not run.hold then Progress() end
end

local function Ids()
    local ids = {}
    for id in (ns.ids or ""):gmatch("%d+") do ids[#ids + 1] = tonumber(id) end
    return ids
end

-- "version|build|locale": the game a reading holds for.
local function GameLabel()
    local version, build = GetBuildInfo()
    return table.concat({ version or "?", build or "?", GetLocale and GetLocale() or "?" }, "|")
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
    local game = GameLabel()
    local db = EasyBISCaptureDB
    local same = type(db) == "table" and type(db.items) == "table" and type(db.meta) == "string"
        and db.meta:match("^%d+|(.*)|[^|]*$") == game
    if again or not same then   -- another game build: its tooltips may have changed. The vendors' prices stay.
        db = { items = {}, vendors = type(db) == "table" and db.vendors or nil }
    end
    db.meta = table.concat({ FORMAT, game, date("%Y-%m-%d %H:%M") }, "|")
    db.missing = ""
    db.log = (type(db.log) == "string" and #db.log < 20000 and (db.log .. "\n") or "") .. date("%H:%M")
    EasyBISCaptureDB = db

    local ids, queue, absent, kept = Ids(), {}, {}, 0
    for _, id in ipairs(ids) do
        if db.items[id] then
            kept = kept + 1
        elseif Listed(id) then
            queue[#queue + 1] = id
        else
            absent[#absent + 1] = id
        end
    end
    -- the game's table is of no help in this game: every item is asked for. What was read already counts
    -- for the table, or a list that grew after a whole capture would ask again for what the game lacks.
    if #absent > #queue + kept then
        for _, id in ipairs(absent) do queue[#queue + 1] = id end
        absent = {}
    end
    local sorted = {}
    for index, id in ipairs(absent) do sorted[index] = id end
    table.sort(sorted)
    db.absent = table.concat(sorted, " ")
    if #queue == 0 then
        Say(("every item of the list is read already%s. /ebiscapture all starts again."):format(
            #absent > 0 and (", but for " .. #absent .. " the game's item table does not list") or ""))
        return
    end
    run = { ids = ids, queue = queue, next = 1, out = {}, later = {}, absent = absent, stage = "list",
            clock = 0, wait = 0, heard = 0, answer = 0, quiet = 0, said = 0, saidRead = 0, logged = 0,
            read = 0, asked = 0, lost = 0 }
    Say(("reading %d items, a few at a time, about %s if the game answers well. A line says where it is "
        .. "every %d seconds. Stay out of combat."):format(#queue, Duration(#queue / ASKS * STEP), SAY))
    if #absent > 0 then
        Say(("%d more are not in the game's item table: they are not asked for."):format(#absent))
    end
    driver:SetScript("OnUpdate", OnUpdate)
end

---------------------------------------------------------------------------
-- What the vendors ask
---------------------------------------------------------------------------

local function VendorId()
    local guid = UnitGUID and UnitGUID("npc")
    if (issecretvalue and issecretvalue(guid)) or type(guid) ~= "string" then return nil end
    return guid:match("^Creature%-%d+%-%d+%-%d+%-%d+%-(%d+)%-")
end

local function MerchantItem(index)
    local id = GetMerchantItemID and GetMerchantItemID(index)
    if id then return id end
    local link = GetMerchantItemLink and GetMerchantItemLink(index)
    return type(link) == "string" and tonumber(link:match("item:(%d+)")) or nil
end

-- The row's name, its price in copper, and whether it costs something else than money.
local function MerchantRow(index)
    if C_MerchantFrame and C_MerchantFrame.GetItemInfo then
        local ok, info = pcall(C_MerchantFrame.GetItemInfo, index)
        if ok and type(info) == "table" then return info.name, info.price, info.hasExtendedCost end
    end
    if GetMerchantItemInfo then
        local name, _, price, _, _, _, _, extended = GetMerchantItemInfo(index)
        return name, price, extended
    end
end

-- One of the things a row costs, as the header of this file writes it; nil while the game has not said.
local function CostOf(index, slot)
    local _, amount, link, name = GetMerchantItemCostItem(index, slot)
    if type(amount) ~= "number" or amount <= 0 then return nil end
    local text = type(link) == "string" and link or ""
    local item, currency = text:match("item:(%d+)"), text:match("currency:(%d+)")
    if item then return ("i%s:%d"):format(item, amount) end
    if currency then return ("c%s:%d"):format(currency, amount) end
    name = Text(name)
    return name and ("n%s:%d"):format((name:gsub(";", " ")), amount) or nil
end

-- The row's item and its line; nil while the game has not said all of it.
local function VendorLine(index)
    local id = MerchantItem(index)
    local name, copper, extended = MerchantRow(index)
    name = Text(name)
    if not id or not name then return nil end
    local count = GetMerchantItemCostInfo and GetMerchantItemCostInfo(index) or 0
    if extended and count == 0 then return nil end
    local costs = {}
    for slot = 1, count do
        costs[slot] = CostOf(index, slot)
        if not costs[slot] then return nil end
    end
    return id, ("%d\t%s\t%d\t%s"):format(id, name, copper or 0, table.concat(costs, ";"))
end

-- The rows kept of a vendor, when they were read in this game.
local function KeptRows(text, game)
    local rows = {}
    if type(text) ~= "string" or text:match("^%d+|([^|]*|[^|]*|[^|]*)|") ~= game then return rows end
    for line in text:gmatch("\n([^\n]+)") do
        rows[tonumber(line:match("^%d+"))] = line
    end
    return rows
end

-- Reads the window and keeps it when something else than money pays for what it shows.
-- { shown = rows read, missing = rows the game has not said yet, kept = rows kept of the vendor, paid = kept or not }
local function ReadVendor(npc)
    local db = EasyBISCaptureDB
    local key, game = "v" .. npc, GameLabel()
    local rows = KeptRows(type(db) == "table" and type(db.vendors) == "table" and db.vendors[key], game)
    local read = { shown = 0, missing = 0, kept = 0, paid = false }
    for index = 1, GetMerchantNumItems() do
        local id, line = VendorLine(index)
        if id then
            rows[id] = line
            read.shown = read.shown + 1
        else
            read.missing = read.missing + 1
        end
    end
    local ids = {}
    for id, line in pairs(rows) do
        ids[#ids + 1] = id
        read.paid = read.paid or line:match("\t[icn][^\t]*$") ~= nil
    end
    read.kept = #ids
    if not read.paid then return read end
    table.sort(ids)
    local name = Text(UnitName and UnitName("npc")) or "?"
    local lines = { ("%d|%s|%s|%s"):format(VENDOR_FORMAT, game, date("%Y-%m-%d %H:%M"), name) }
    for _, id in ipairs(ids) do lines[#lines + 1] = rows[id] end
    if type(db) ~= "table" then db = {} end
    if type(db.vendors) ~= "table" then db.vendors = {} end
    db.vendors[key] = table.concat(lines, "\n")
    EasyBISCaptureDB = db
    read.name = name
    return read
end

-- Whether the window leaves out part of what the vendor sells.
local function Filtered()
    if not GetMerchantFilter or not LE_LOOT_FILTER_ALL then return false end
    local ok, filter = pcall(GetMerchantFilter)
    return ok and filter ~= LE_LOOT_FILTER_ALL
end

local window   -- the vendor's window that is open: { npc, tries, timer, said }

local function ReportVendor(read)
    local filtered = Filtered()
    local said = table.concat({ read.kept, read.missing, tostring(filtered) }, ":")
    if window.said == said then return end
    window.said = said
    Say(("%s: the prices of %d items are kept."):format(read.name, read.kept))
    if read.missing > 0 then
        Say(("%d items of the window did not load: close it and open it again."):format(read.missing))
    end
    if filtered then Say("The window is filtered: choose All in its menu to read all this vendor sells.") end
    Say("Type /reload to save, then run: python -I _build/build.py --import-prices")
end

local function LookAtVendor()
    if not window or window.timer then return end
    local read = ReadVendor(window.npc)
    if (read.missing > 0 or read.shown == 0) and window.tries < VENDOR_TRIES then
        local this = window
        this.tries, this.timer = this.tries + 1, true
        C_Timer.After(VENDOR_WAIT, function()
            this.timer = nil
            if window == this then LookAtVendor() end
        end)
        return
    end
    if read.missing == 0 then window.tries = 0 end
    if read.paid then ReportVendor(read) end
end

local watcher = CreateFrame("Frame")
watcher:RegisterEvent("MERCHANT_SHOW")
watcher:RegisterEvent("MERCHANT_UPDATE")
watcher:RegisterEvent("MERCHANT_CLOSED")
watcher:SetScript("OnEvent", function(_, event)
    if event == "MERCHANT_CLOSED" then
        window = nil
        return
    end
    if event == "MERCHANT_SHOW" then
        local npc = VendorId()
        window = npc and { npc = npc, tries = 0 } or nil
    end
    LookAtVendor()
end)

SLASH_EASYBISCAPTURE1 = "/ebiscapture"
SlashCmdList["EASYBISCAPTURE"] = function(message)
    local command = (message or ""):lower():match("^%s*(%S*)")
    if command == "" then
        Start(false)
    elseif command == "all" then
        Start(true)
    elseif command == "stop" then
        if run then Finish("stopped") else Say("not reading.") end
    elseif command == "status" then
        if run then
            Say(("%d read, %d to go, %d not answered for%s."):format(
                run.read, #run.queue - run.next + 1 + #run.out, #run.later,
                run.quiet > 0 and "; the game is not answering" or ""))
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
