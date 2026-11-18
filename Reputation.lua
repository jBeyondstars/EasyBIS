local _, ns = ...
local L = ns.L

--[[
What a reputation asks of the player, for every part of the addon (Data\Reputation.lua, _build/reputations.py).
Nothing here depends on the window: a tab, a tooltip or a later feature reads the same answers.

  Reputation.Requirement(itemId, side)     what the item asks for on that side (the player's when not given),
                                           or nil: { factionID, standing, kind, side, vendor, price, via,
                                           profession, skill }
      standing   3 Neutral, 4 Friendly, 5 Honored, 6 Revered, 7 Exalted
      kind      Reputation.WEAR the wearer's; QUEST a quest that rewards the item asks for it; RECIPE the recipe
                 is sold against it: the crafter's reputation counts, so it stays out of what the player needs
  Reputation.EnchantRequirement(id)        the same for an enchant ("s20025"), with scroll: a scroll does the same
  Reputation.Standing(factionID)           what the game says: { factionID, known, met, name, standing, value, span,
                                           total }. known is false when the game has no such faction; met is false
                                           for a faction never met, nil when the reputation pane hides the answer
  Reputation.Status(requirement)           "met", "missing", "unknown" (the game does not say) or "other" (the other
                                           side's faction). A faction never met is missing, even for Neutral: the
                                           game reads it as Neutral 0 without the player having been there
  Reputation.Reachable(requirement)        nothing stands in the player's way: no requirement, a recipe, or it is met
  Reputation.Needs(class, spec, list, phase, side)
                                           { own = { group, ... }, artisan = { group, ... } }, most wanted first
      group      { factionID, artisan, best, alts, other, met, steps = { [standing] = { entry, ... } } }
                 best, alts, other count the pieces; met the best ones the player can already have
      entry      { id, enchant, slot, role = "best"|"alt"|"other", requirement }
  Reputation.Summary(cells)                the sheet's cells (Rows.Character) per faction, recipes left out:
                                           { { factionID, name, met, total }, ... }
  Reputation.Factions()                    the catalogue: { { factionID, name, side, quests, repeatable, once,
                                           vendor, rewards, methods }, ... }
  Reputation.Faction(factionID)            one of them, or nil
  Reputation.Ways(factionID)               how to earn it: { { text, evidence = "data"|"check"|"unknown" }, ... }

Words, for the frames to show:
  Reputation.StandingName(standing)        Reputation.FactionName(factionID)
  Reputation.ProgressText(factionID, short)     "Honored 4,200 / 12,000", "Exalted", "Not met", "Unknown"
  Reputation.Ratio(factionID)              how far along the current standing, from 0 to 1
  Reputation.NeedText(requirement)         "Timbermaw Hold, Honored", with what kind of requirement it is
  Reputation.StateText(requirement)        "Earned" in gold, "You: Honored", "Not met", "Unknown"...
  Reputation.VendorText(factionID)         who sells its pieces, or "Unknown"
  Reputation.TooltipLines(itemId)          { { text, r, g, b }, ... }

Fires REPUTATION_CHANGED (ns:On) once after a burst of the game's UPDATE_FACTION.

Gold is kept for what is earned. What the data or the game does not say is written as unknown, and no time to
reach a standing is ever said: nothing here measures the player's gains.
]]

local Reputation = {}
ns.Reputation = Reputation

Reputation.WEAR, Reputation.QUEST, Reputation.RECIPE = "w", "q", "r"
Reputation.NEUTRAL = 3
Reputation.STANDINGS = { 3, 4, 5, 6, 7 }

local WEAR, QUEST, RECIPE = Reputation.WEAR, Reputation.QUEST, Reputation.RECIPE
local NEUTRAL_REACTION = 4        -- the game counts from 1 Hated; the data from 0
local EXALTED = 7
local GOLD, GREY, WHITE = "|cffffd100", "|cffa8a8b0", "|cffffffff"
local MUTED = { 0.66, 0.66, 0.70 }
local QUIET_DELAY = 0.25          -- the game sends UPDATE_FACTION in bursts

---------------------------------------------------------------------------
-- The data
---------------------------------------------------------------------------

local function Fields(line)
    local fields = {}
    for field in (line .. "|"):gmatch("(.-)|") do fields[#fields + 1] = field end
    return fields
end

local function Text(field)
    return field ~= "" and field or nil
end

local catalog

local function Catalog()
    if catalog then return catalog end
    catalog = { order = {}, factions = {}, vendors = {}, items = {}, enchants = {} }
    local data = ns.data and ns.data.reputation or {}
    for line in (data.factions or ""):gmatch("[^\n]+") do
        local f = Fields(line)
        local faction = {
            factionID = tonumber(f[1]), name = f[2], side = f[3], quests = tonumber(f[4]) or 0,
            repeatable = tonumber(f[5]) or 0, once = { a = tonumber(f[6]) or 0, h = tonumber(f[7]) or 0 },
            vendor = tonumber(f[8]), rewards = f[9] == "1", methods = {},
        }
        catalog.factions[faction.factionID] = faction
        catalog.order[#catalog.order + 1] = faction
    end
    for line in (data.methods or ""):gmatch("[^\n]+") do
        local f = Fields(line)
        local faction = catalog.factions[tonumber(f[1])]
        if faction then
            faction.methods[#faction.methods + 1] = {
                quest = f[2], amount = tonumber(f[3]) or 0, repeats = f[4] == "1", side = f[5],
            }
        end
    end
    for line in (data.vendors or ""):gmatch("[^\n]+") do
        local f = Fields(line)
        catalog.vendors[tonumber(f[1])] = { name = f[2], map = tonumber(f[3]), x = tonumber(f[4]), y = tonumber(f[5]) }
    end
    for line in (data.items or ""):gmatch("[^\n]+") do
        local f = Fields(line)
        local id = tonumber(f[1])
        catalog.items[id] = catalog.items[id] or {}
        table.insert(catalog.items[id], {
            itemId = id, side = f[2], factionID = tonumber(f[3]), standing = tonumber(f[4]), kind = f[5],
            vendor = tonumber(f[6]), price = tonumber(f[7]), via = Text(f[8]), profession = Text(f[9]),
            skill = tonumber(f[10]),
        })
    end
    for line in (data.enchants or ""):gmatch("[^\n]+") do
        local f = Fields(line)
        catalog.enchants[f[1]] = {
            enchant = f[1], side = "", factionID = tonumber(f[2]), standing = tonumber(f[3]), kind = f[4],
            scroll = f[5] == "1", via = Text(f[6]),
        }
    end
    return catalog
end

function Reputation.Requirement(itemId, side)
    local rows = Catalog().items[itemId]
    if not rows then return nil end
    side = side or ns.PlayerSide()
    local shared
    for _, row in ipairs(rows) do
        if row.side == side then return row end
        if row.side == "" then shared = row end
    end
    return shared
end

function Reputation.EnchantRequirement(id)
    return Catalog().enchants[id]
end

function Reputation.Factions()
    return Catalog().order
end

function Reputation.Faction(factionID)
    return Catalog().factions[factionID]
end

---------------------------------------------------------------------------
-- What the game says
---------------------------------------------------------------------------

local standings = {}
local listed, wholeList

-- The factions the reputation pane lists. Its collapsed headers are left as the player keeps them: a faction
-- under one of them is simply not known to be met or not.
local function ReadList()
    listed, wholeList = {}, true
    local api = C_Reputation
    local count = 0
    if api and api.GetNumFactions then
        count = api.GetNumFactions() or 0
    elseif GetNumFactions then
        count = GetNumFactions() or 0
    end
    for index = 1, count do
        local factionID, isHeader, isCollapsed
        if api and api.GetFactionDataByIndex then
            local data = api.GetFactionDataByIndex(index)
            if data then factionID, isHeader, isCollapsed = data.factionID, data.isHeader, data.isCollapsed end
        elseif GetFactionInfo then
            local info = { GetFactionInfo(index) }
            isHeader, isCollapsed, factionID = info[9], info[10], info[14]
        end
        if factionID then listed[factionID] = true end
        if isHeader and isCollapsed then wholeList = false end
    end
end

-- name, reaction (1 Hated to 8 Exalted), the current standing's start and end, the reputation; nil when the
-- game does not know the faction.
local function ReadFaction(factionID)
    if C_Reputation and C_Reputation.GetFactionDataByID then
        local ok, data = pcall(C_Reputation.GetFactionDataByID, factionID)
        if not ok or type(data) ~= "table" or not data.reaction then return nil end
        return data.name, data.reaction, data.currentReactionThreshold or 0, data.nextReactionThreshold or 0,
            data.currentStanding or 0
    end
    if GetFactionInfoByID then
        local ok, name, _, reaction, low, high, value = pcall(GetFactionInfoByID, factionID)
        if ok and reaction then return name, reaction, low or 0, high or 0, value or 0 end
    end
    return nil
end

function Reputation.Standing(factionID)
    local record = standings[factionID]
    if record then return record end
    local faction = Catalog().factions[factionID]
    record = { factionID = factionID, known = false, name = faction and faction.name or ("#" .. tostring(factionID)) }
    local name, reaction, low, high, value = ReadFaction(factionID)
    if reaction then
        if not listed then ReadList() end
        record.known = true
        if name and name ~= "" then record.name = name end
        record.standing = reaction - 1
        record.value = math.max(0, value - low)
        record.span = math.max(0, high - low)
        record.total = value
        -- The game reads a faction never met as Neutral 0, the same as one met and left there.
        if listed[factionID] or value ~= 0 or reaction ~= NEUTRAL_REACTION then
            record.met = true
        elseif wholeList then
            record.met = false
        end
    end
    standings[factionID] = record
    return record
end

function Reputation.Status(requirement)
    local faction = Catalog().factions[requirement.factionID]
    if faction and faction.side ~= "" and faction.side ~= ns.PlayerSide() then return "other" end
    local standing = Reputation.Standing(requirement.factionID)
    if not standing.known then return "unknown" end
    if standing.met == false then return "missing" end
    if standing.standing < requirement.standing then return "missing" end
    return standing.met and "met" or "unknown"
end

function Reputation.Reachable(requirement)
    return not requirement or requirement.kind == RECIPE or Reputation.Status(requirement) == "met"
end

---------------------------------------------------------------------------
-- What a spec needs
---------------------------------------------------------------------------

local function Picks(class, spec, list, phase, side)
    local filter = ns.Filter()
    if (not phase or phase == filter.phase) and (not side or side == filter.side) then
        return ns.Ladders.For(class, spec, list)
    end
    filter.phase, filter.side = phase or filter.phase, side or filter.side
    local data = ns.Ladders.Decode(class)
    return data and ns.Ladders.Compute(data, spec, list, filter) or nil
end

local ROLES = { { "best", "best" }, { "alts", "alt" }, { "other", "other" } }
local COUNTERS = { best = "best", alt = "alts", other = "other" }

function Reputation.Needs(class, spec, list, phase, side)
    local groups, own, artisan = {}, {}, {}
    local function Add(requirement, entry)
        local crafted = requirement.kind == RECIPE
        local key = requirement.factionID .. (crafted and ":r" or ":o")
        local group = groups[key]
        if not group then
            group = { factionID = requirement.factionID, artisan = crafted, best = 0, alts = 0, other = 0, met = 0,
                steps = {} }
            groups[key] = group
            local into = crafted and artisan or own
            into[#into + 1] = group
        end
        entry.requirement = requirement
        group[COUNTERS[entry.role]] = group[COUNTERS[entry.role]] + 1
        if entry.role == "best" and Reputation.Status(requirement) == "met" then group.met = group.met + 1 end
        group.steps[requirement.standing] = group.steps[requirement.standing] or {}
        table.insert(group.steps[requirement.standing], entry)
    end

    local slots = Picks(class, spec, list, phase, side)
    for _, slot in ipairs(slots and ns.SLOTS or {}) do
        for _, role in ipairs(ROLES) do
            for _, pick in ipairs(slots[slot][role[1]]) do
                local requirement = Reputation.Requirement(pick.id, side)
                if requirement then Add(requirement, { id = pick.id, slot = slot, role = role[2] }) end
            end
        end
    end
    for _, group in ipairs(ns.Enchants.For(class, spec, phase)) do
        for index, id in ipairs(group.ids) do
            local requirement = Reputation.EnchantRequirement(id)
            if requirement then
                Add(requirement, { enchant = id, slot = group.key, role = index == 1 and "best" or "alt" })
            end
        end
    end

    local function Order(a, b)
        if a.best ~= b.best then return a.best > b.best end
        if a.alts ~= b.alts then return a.alts > b.alts end
        return a.factionID < b.factionID
    end
    table.sort(own, Order)
    table.sort(artisan, Order)
    return { own = own, artisan = artisan }
end

function Reputation.Summary(cells)
    local byFaction, summary = {}, {}
    for _, cell in ipairs(cells) do
        local requirement = cell.reputation
        if requirement and requirement.kind ~= RECIPE then
            local line = byFaction[requirement.factionID]
            if not line then
                line = { factionID = requirement.factionID, name = Reputation.FactionName(requirement.factionID),
                    met = 0, total = 0 }
                byFaction[requirement.factionID] = line
                summary[#summary + 1] = line
            end
            line.total = line.total + 1
            if Reputation.Status(requirement) == "met" then line.met = line.met + 1 end
        end
    end
    table.sort(summary, function(a, b)
        if a.total ~= b.total then return a.total > b.total end
        return a.factionID < b.factionID
    end)
    return summary
end

---------------------------------------------------------------------------
-- Words
---------------------------------------------------------------------------

local function Number(value)
    if BreakUpLargeNumbers then return BreakUpLargeNumbers(value) end
    return tostring(value)
end

function Reputation.StandingName(standing)
    return _G["FACTION_STANDING_LABEL" .. (standing + 1)] or L["REP_STANDING_" .. standing]
end

function Reputation.FactionName(factionID)
    return Reputation.Standing(factionID).name
end

function Reputation.ProgressText(factionID, short)
    local standing = Reputation.Standing(factionID)
    if not standing.known then return L.REP_UNKNOWN end
    if standing.met == false then return L.REP_NOT_MET end
    local name = Reputation.StandingName(standing.standing)
    if short or standing.standing >= EXALTED or standing.span <= 0 then return name end
    return L.REP_PROGRESS:format(name, Number(standing.value), Number(standing.span))
end

function Reputation.Ratio(factionID)
    local standing = Reputation.Standing(factionID)
    if not standing.known or standing.met == false then return 0 end
    if standing.standing >= EXALTED or standing.span <= 0 then return 1 end
    return math.max(0, math.min(1, standing.value / standing.span))
end

local NEED_KEYS = { [WEAR] = "REP_NEED", [QUEST] = "REP_NEED_QUEST", [RECIPE] = "REP_NEED_RECIPE" }

function Reputation.NeedText(requirement)
    local key = NEED_KEYS[requirement.kind] or "REP_NEED"
    if requirement.enchant and requirement.kind == RECIPE then key = "REP_NEED_FORMULA" end
    return L[key]:format(Reputation.FactionName(requirement.factionID), Reputation.StandingName(requirement.standing))
end

function Reputation.StateText(requirement)
    local status = Reputation.Status(requirement)
    if status == "met" then return GOLD .. L.REP_MET .. "|r" end
    if status == "unknown" then return WHITE .. L.REP_UNKNOWN .. "|r" end
    if status == "other" then return GREY .. L.REP_OTHER_SIDE .. "|r" end
    if requirement.kind == RECIPE then return GREY .. L.REP_FOR_CRAFTER .. "|r" end
    local standing = Reputation.Standing(requirement.factionID)
    if standing.met == false then return GREY .. L.REP_NOT_MET .. "|r" end
    return GREY .. L.REP_YOU:format(Reputation.ProgressText(requirement.factionID, ns:GetOption("repCompact"))) .. "|r"
end

local function MapName(id)
    local info = id and C_Map and C_Map.GetMapInfo and C_Map.GetMapInfo(id)
    return info and info.name or nil
end

local function VendorLine(npc)
    local vendor = npc and Catalog().vendors[npc]
    if not vendor or vendor.name == "" then return nil end
    local zone = MapName(vendor.map)
    if zone and vendor.x and vendor.y then return L.REP_VENDOR_AT:format(vendor.name, zone, vendor.x, vendor.y) end
    return zone and (vendor.name .. ", " .. zone) or vendor.name
end

function Reputation.VendorText(factionID)
    local faction = Catalog().factions[factionID]
    local line = faction and VendorLine(faction.vendor)
    if line then return line end
    return faction and faction.rewards and L.REP_VENDOR_QUESTS or L.REP_UNKNOWN
end

local function Money(copper)
    if GetCoinTextureString then return GetCoinTextureString(copper) end
    local gold, silver, rest = math.floor(copper / 10000), math.floor(copper / 100) % 100, copper % 100
    local parts = {}
    if gold > 0 then parts[#parts + 1] = L.REP_GOLD:format(gold) end
    if silver > 0 then parts[#parts + 1] = L.REP_SILVER:format(silver) end
    if rest > 0 or not parts[1] then parts[#parts + 1] = L.REP_COPPER:format(rest) end
    return table.concat(parts, " ")
end

-- Where the requirement is met, for a tooltip.
local function SourceLine(requirement)
    if requirement.kind == QUEST then return L.REP_TIP_QUEST:format(requirement.via or L.REP_UNKNOWN) end
    if requirement.kind == RECIPE then
        local profession = requirement.profession and ns.ProfessionName(requirement.profession)
        local name = requirement.via or L.REP_UNKNOWN
        return L.REP_TIP_RECIPE:format(profession and (name .. " (" .. profession .. ")") or name)
    end
    return L.REP_TIP_VENDOR:format(VendorLine(requirement.vendor) or L.REP_UNKNOWN)
end

function Reputation.TooltipLines(itemId)
    local requirement = Reputation.Requirement(itemId)
    if not requirement then return {} end
    local earned = Reputation.Status(requirement) == "met"
    local lines = { {
        text = L.REP_TIP_NEED:format(Reputation.NeedText(requirement)),
        r = 1, g = earned and 0.82 or 1, b = earned and 0 or 1,
    } }
    local function Quiet(text) lines[#lines + 1] = { text = text, r = MUTED[1], g = MUTED[2], b = MUTED[3] } end
    Quiet(L.REP_YOU:format(Reputation.ProgressText(requirement.factionID)))
    Quiet(SourceLine(requirement))
    if requirement.kind == WEAR then
        Quiet(L.REP_TIP_PRICE:format(requirement.price and Money(requirement.price) or L.REP_UNKNOWN))
    end
    local faction = Catalog().factions[requirement.factionID]
    Quiet(faction and faction.quests > 0 and L.REP_TIP_FARM or L.REP_TIP_FARM_UNKNOWN)
    return lines
end

-- What is known of how to earn a faction, each line with how far it can be trusted.
function Reputation.Ways(factionID)
    local faction = Catalog().factions[factionID]
    local ways = {}
    local function Add(text, evidence) ways[#ways + 1] = { text = text, evidence = evidence } end
    if not faction or faction.quests == 0 then
        Add(L.REP_WAY_NONE, "unknown")
    else
        local side = ns.PlayerSide()
        Add(L.REP_WAY_QUESTS:format(faction.quests, faction.repeatable), "data")
        for _, method in ipairs(faction.methods) do
            if method.side == "" or method.side == side then
                Add(L[method.repeats and "REP_WAY_REPEATS" or "REP_WAY_ONCE"]:format(method.quest, method.amount), "data")
            end
        end
        if faction.once[side] > 0 then Add(L.REP_WAY_CEILING:format(Number(faction.once[side])), "data") end
    end
    local note = L["REP_NOTE_" .. factionID]
    if note ~= "REP_NOTE_" .. factionID then Add(note, "check") end
    if faction and faction.quests > 0 then
        if faction.repeatable == 0 then Add(L.REP_WAY_ROUTE, "unknown") end
        Add(L.REP_WAY_CREATURES, "unknown")
    end
    return ways
end

---------------------------------------------------------------------------
-- Following the game
---------------------------------------------------------------------------

local queued = false

local function Announce()
    queued = false
    ns:Fire("REPUTATION_CHANGED")
end

local events = CreateFrame("Frame")
events:RegisterEvent("UPDATE_FACTION")
events:SetScript("OnEvent", function()
    standings, listed, wholeList = {}, nil, nil
    if queued then return end
    if C_Timer and C_Timer.After then
        queued = true
        C_Timer.After(QUIET_DELAY, Announce)
    else
        Announce()
    end
end)
