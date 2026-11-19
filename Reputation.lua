local _, ns = ...
local L = ns.L

--[[
What a reputation asks of the player, for every part of the addon (Data\Reputation.lua, _build/reputations.py).
Nothing here depends on the window: a tab, a tooltip or a later feature reads the same answers.

  Reputation.Requirement(itemId, side)     what the item asks for on that side (the player's when not given),
                                           or nil: { factionID, standing, kind, side, vendor, price, via,
                                           profession, skill, recipe }
                                           for a recipe, vendor sells the recipe and recipe is its item
      standing   3 Neutral, 4 Friendly, 5 Honored, 6 Revered, 7 Exalted
      kind      Reputation.WEAR the wearer's; QUEST a quest that rewards the item asks for it; RECIPE the recipe
                 is sold against it: the crafter's reputation counts, so it stays out of what the player needs
  Reputation.EnchantRequirement(id)        the same for an enchant ("s20025"), with scroll: a scroll does the same
  Reputation.Professions()                 the player's professions, { [English name] = skill }, or nil when the
                                           game does not say
  Reputation.Crafter(requirement)          for a recipe: "crafter" and the player's skill when the profession is
                                           theirs, "other" when it is not, nil when unknown or not a recipe
  Reputation.Crafts(group)                 a group's professions: { { profession, skill (the most its recipes ask),
                                           rank (the player's, or nil), status (as Crafter) }, ... }, and the
                                           group's status: "crafter" when one of them is the player's
  Reputation.Emblem(factionID)             the icon that stands for a faction (an item's: its token, its tabard), or nil
  Reputation.Binding(itemId)               "equip", "pickup", "none" (the game binds it to nobody), or nil when the
                                           game does not say
  Reputation.RecipeName(requirement)       the recipe's name in the game's language, or the data's
  Reputation.Standing(factionID)           what the game says: { factionID, known, met, name, standing, value, span,
                                           total }. known is false when the game has no such faction; met is false
                                           for a faction never met, nil when the reputation pane hides the answer
  Reputation.Status(requirement)           "met", "missing", "unknown" (the game does not say) or "other" (the other
                                           side's faction). A faction never met is missing, even for Neutral: the
                                           game reads it as Neutral 0 without the player having been there
  Reputation.Reachable(requirement)        nothing stands in the player's way: no requirement, a recipe, or it is met
  Reputation.Needs(class, spec, list, phase, side)
                                           { own = { group, ... }, artisan = { group, ... } }, most wanted first;
                                           the recipes of a profession the player has come first
      group      { factionID, artisan, best, alts, other, met, steps = { [standing] = { entry, ... } } }
                 best, alts, other count the pieces; met the best ones the player can already have; a crafter's
                 group also has craftStatus (as Crafts) and crafter (true when it is the player's profession)
      entry      { id, enchant, slot, role = "best"|"alt"|"other", requirement }
  Reputation.Summary(cells)                the sheet's cells (Rows.Character) per faction, recipes left out:
                                           { { factionID, name, met, total, state }, ... }; state "unknown" when
                                           the game does not say, "other" for the other side's faction
  Reputation.Factions()                    the catalogue: { { factionID, name, side, quests, repeatable, once,
                                           vendor, rewards, methods }, ... }
  Reputation.Faction(factionID)            one of them, or nil
  Reputation.Unknown(factionID)            true when no source says how to earn it nor who sells its pieces
  Reputation.UnknownMark(requirement)      " ?" in grey for what such a faction opens, "" otherwise: it follows a name
  Reputation.UnknownRemark(requirement)    the tooltip's line that explains it, or nil
  Reputation.Ways(factionID, class)        how to earn it: { total, listed, repeatable, once, quests = { { quest,
                                           amount, repeats, from, upto }, ... }, checks = { text, ... },
                                           unknowns = { text, ... } }
                                           total: the quests the data has for the faction; quests: the ones of them
                                           the player's side and that class may take, listed counts them; from and
                                           upto: the standings a quest is offered from and up to, when it says;
                                           repeatable: those that repeat and help from Neutral; once: the most the
                                           others give from Neutral to Exalted, of branches that exclude one another
                                           the one that gives the most; checks: what a person wrote down and the
                                           game should confirm; unknowns: what no source says
  Reputation.Sellers(group)                where a group's pieces come from: { { text, map, x, y }, ... }; map, x and
                                           y only for a vendor whose place is known

Where the player stands, counted from the start of Neutral (THRESHOLDS: the standard 3,000 / 6,000 / 12,000 /
21,000 between standings):
  Reputation.Position(factionID)           the reputation from Neutral 0 (below 0 under Neutral), or nil when the
                                           game does not say or the faction was never met
  Reputation.Remaining(factionID, standing)    what is left to reach it: 0 once reached; for a faction never met,
                                           the whole way from Neutral and true; nil when unknown
  Reputation.Watched(factionID), Reputation.CanWatch(factionID), Reputation.Watch(factionID, on)
                                           the faction the game's reputation bar follows

Words, for the frames to show:
  Reputation.StandingName(standing)        Reputation.FactionName(factionID)
  Reputation.ProgressText(factionID, short)     "Honored 4,200 / 12,000", "Exalted", "Not met yet", "Unknown"
  Reputation.Ratio(factionID)              how far along the current standing, from 0 to 1
  Reputation.NeedText(requirement)         "Timbermaw Hold, Honored", with what kind of requirement it is
  Reputation.StateText(requirement)        "Earned" in gold, "You: Honored", "Not met", "Unknown"...
  Reputation.TooltipLines(itemId)          { { text, r, g, b }, ... }

Fires REPUTATION_CHANGED (ns:On) once after a burst of the game's UPDATE_FACTION or SKILL_LINES_CHANGED.

Gold is kept for what is earned. What the data or the game does not say is written as unknown, and no time to
reach a standing is ever said: nothing here measures the player's gains.
]]

local Reputation = {}
ns.Reputation = Reputation

Reputation.WEAR, Reputation.QUEST, Reputation.RECIPE = "w", "q", "r"
Reputation.STANDINGS = { 3, 4, 5, 6, 7 }
Reputation.THRESHOLDS = { [3] = 0, [4] = 3000, [5] = 9000, [6] = 21000, [7] = 42000 }

local WEAR, QUEST, RECIPE = Reputation.WEAR, Reputation.QUEST, Reputation.RECIPE
local NEUTRAL_REACTION = 4        -- the game counts from 1 Hated; the data from 0
local NEUTRAL, EXALTED = 3, 7
local GOLD, GREY, WHITE = "|cffffd100", "|cffa8a8b0", "|cffffffff"
local UNSURE = "|cff808080"        -- the colour of the signs the data wears when it is less than sure
local MUTED = { 0.66, 0.66, 0.70 }
local QUIET_DELAY = 0.25          -- the game sends UPDATE_FACTION in bursts
-- The game's class numbers: a quest's classes are a mask of 2 ^ (number - 1).
local CLASS_NUMBERS = { WARRIOR = 1, PALADIN = 2, HUNTER = 3, ROGUE = 4, PRIEST = 5, SHAMAN = 7, MAGE = 8,
    WARLOCK = 9, DRUID = 11 }

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
                classes = tonumber(f[6]) or 0, from = tonumber(f[7]), upto = tonumber(f[8]), choice = Text(f[9]),
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
            skill = tonumber(f[10]), recipe = tonumber(f[11]),
        })
    end
    for line in (data.enchants or ""):gmatch("[^\n]+") do
        local f = Fields(line)
        catalog.enchants[f[1]] = {
            enchant = f[1], side = "", factionID = tonumber(f[2]), standing = tonumber(f[3]), kind = f[4],
            scroll = f[5] == "1", via = Text(f[6]), vendor = tonumber(f[7]), recipe = tonumber(f[8]),
            profession = Text(f[9]), skill = tonumber(f[10]),
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

-- A faction no source says how to earn, nor who sells what it opens (The Watchers: read only in the game's
-- files). What it opens stays in the lists, its name followed by a grey "?" that the tooltips explain.
function Reputation.Unknown(factionID)
    local faction = Catalog().factions[factionID]
    return faction ~= nil and faction.quests == 0 and faction.methods[1] == nil and faction.vendor == nil
        and not faction.rewards
end

function Reputation.UnknownMark(requirement)
    if requirement and Reputation.Unknown(requirement.factionID) then return " " .. UNSURE .. "?|r" end
    return ""
end

function Reputation.UnknownRemark(requirement)
    if requirement and Reputation.Unknown(requirement.factionID) then return "? " .. L.REP_UNKNOWN_WAY end
    return nil
end

-- A faction's emblem: the icon of an item that stands for it, its token or its tabard, or its side's battle
-- standard. The game's reputation pane has none and no source names one: the choice is Easy BIS's. A faction
-- without one (The Watchers, Powderfuse, the Steamwheedle towns) gets nothing rather than a made-up sign.
local EMBLEMS = {
    [59] = 18945,     -- Thorium Brotherhood: Dark Iron Residue
    [270] = 19858,    -- Zandalar Tribe: Zandalar Honor Token
    [509] = 20132,    -- The League of Arathor: Arathor Battle Tabard
    [510] = 20131,    -- The Defilers: Battle Tabard of the Defilers
    [529] = 12844,    -- Argent Dawn: Argent Dawn Valor Token
    [576] = 21377,    -- Timbermaw Hold: Deadwood Headdress Feather
    [609] = 20802,    -- Cenarion Circle: Cenarion Combat Badge
    [729] = 19031,    -- Frostwolf Clan: Frostwolf Battle Tabard
    [730] = 19032,    -- Stormpike Guard: Stormpike Battle Tabard
    [749] = 17333,    -- Hydraxian Waterlords: Aqual Quintessence
    [910] = 21196,    -- Brood of Nozdormu: Signet Ring of the Bronze Dragonflight
    [2798] = 18607,   -- Darkspear Raiders: Horde Battle Standard
    [2799] = 18606,   -- Theramore Expeditionary Force: Alliance Battle Standard
}
local NO_ICON = 134400   -- the question mark the game gives for an item it does not have

function Reputation.Emblem(factionID)
    local item = EMBLEMS[factionID]
    local Icon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon
    if not item or not Icon then return nil end
    local ok, icon = pcall(Icon, item)
    if not ok or not icon or icon == NO_ICON then return nil end
    return icon
end

---------------------------------------------------------------------------
-- What the game says
---------------------------------------------------------------------------

local standings = {}
local listed, wholeList, indexes

-- The factions the reputation pane lists. Its collapsed headers are left as the player keeps them: a faction
-- under one of them is simply not known to be met or not.
local function ReadList()
    listed, wholeList, indexes = {}, true, {}
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
        if factionID then listed[factionID], indexes[factionID] = true, index end
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
    -- the character's side, not the one the lists show: an Alliance character looking at the Horde's lists earns
    -- none of the Horde's factions
    if faction and faction.side ~= "" and faction.side ~= ns.CharacterSide() then return "other" end
    local standing = Reputation.Standing(requirement.factionID)
    if not standing.known then return "unknown" end
    if standing.met == false then return "missing" end
    if standing.standing < requirement.standing then return "missing" end
    return standing.met and "met" or "unknown"
end

function Reputation.Reachable(requirement)
    return not requirement or requirement.kind == RECIPE or Reputation.Status(requirement) == "met"
end

function Reputation.Position(factionID)
    local standing = Reputation.Standing(factionID)
    if not standing.known or standing.met == false then return nil end
    if standing.standing >= EXALTED then return Reputation.THRESHOLDS[EXALTED] end
    local start = Reputation.THRESHOLDS[standing.standing]
    if start then return start + standing.value end
    return standing.total   -- under Neutral: the game counts down from 0
end

function Reputation.Remaining(factionID, standing)
    local goal = Reputation.THRESHOLDS[standing]
    if not goal then return nil end
    local record = Reputation.Standing(factionID)
    if record.known and record.met == false then return goal, true end
    local position = Reputation.Position(factionID)
    if not position then return nil end
    if record.standing >= standing then return 0 end
    return math.max(0, goal - position)
end

function Reputation.Watched(factionID)
    if C_Reputation and C_Reputation.GetWatchedFactionData then
        local ok, data = pcall(C_Reputation.GetWatchedFactionData)
        return ok and type(data) == "table" and data.factionID == factionID
    end
    if GetWatchedFactionInfo then
        local id = select(6, GetWatchedFactionInfo())
        return id == factionID
    end
    return false
end

-- The game's bar follows a faction of its reputation pane: one never met, or under a header the player keeps
-- collapsed, cannot be chosen.
function Reputation.CanWatch(factionID)
    if Reputation.Standing(factionID).met ~= true then return false end
    if C_Reputation and C_Reputation.SetWatchedFactionByID then return true end
    if not listed then ReadList() end
    return SetWatchedFactionIndex ~= nil and indexes[factionID] ~= nil
end

function Reputation.Watch(factionID, on)
    if C_Reputation and C_Reputation.SetWatchedFactionByID then
        pcall(C_Reputation.SetWatchedFactionByID, on and factionID or 0)
    elseif SetWatchedFactionIndex then
        if not listed then ReadList() end
        local index = indexes[factionID]
        if on and not index then return end
        pcall(SetWatchedFactionIndex, on and index or 0)
    end
end

---------------------------------------------------------------------------
-- The crafter
---------------------------------------------------------------------------

-- The game's skill line of each profession the data names.
local SKILL_LINES = { Alchemy = 171, Blacksmithing = 164, Enchanting = 333, Engineering = 202, Leatherworking = 165,
    Tailoring = 197, Cooking = 185, ["First Aid"] = 129, Fishing = 356, Mining = 186, Herbalism = 182, Skinning = 393 }

local function Profession(name, skillLine)
    for english, line in pairs(SKILL_LINES) do
        if line == skillLine or (name and name == ns.ProfessionName(english)) then return english end
    end
    return nil
end

-- GetProfessions gives the indexes of the player's professions, a hole where one is not learned.
local function ReadProfessions(...)
    local found = {}
    for position = 1, select("#", ...) do
        local index = select(position, ...)
        if index then
            local ok, name, _, rank, _, _, _, skillLine = pcall(GetProfessionInfo, index)
            local english = ok and Profession(name, skillLine)
            if english then found[english] = rank or 0 end
        end
    end
    return found
end

function Reputation.Professions()
    if GetProfessions and GetProfessionInfo then
        local ok, found = pcall(function() return ReadProfessions(GetProfessions()) end)
        return ok and found or nil
    end
    if GetNumSkillLines and GetSkillLineInfo then
        -- the skills are known by their names, which the addon reads in English and French only
        local locale = GetLocale and GetLocale() or "enUS"
        if locale:sub(1, 2) ~= "en" and locale ~= "frFR" then return nil end
        local found = {}
        for index = 1, GetNumSkillLines() or 0 do
            local name, isHeader, isExpanded, rank = GetSkillLineInfo(index)
            if isHeader and not isExpanded then return nil end   -- a folded header hides the skills under it
            local english = not isHeader and Profession(name)
            if english then found[english] = rank or 0 end
        end
        return found
    end
    return nil
end

function Reputation.Crafter(requirement)
    if not requirement or requirement.kind ~= RECIPE or not requirement.profession then return nil end
    local professions = Reputation.Professions()
    if not professions then return nil end
    local rank = professions[requirement.profession]
    if rank then return "crafter", rank end
    return "other"
end

function Reputation.Crafts(group)
    local crafts, byName, status = {}, {}, nil
    local professions = Reputation.Professions()
    for _, standing in ipairs(Reputation.STANDINGS) do
        for _, entry in ipairs(group.steps[standing] or {}) do
            local requirement = entry.requirement
            local name = requirement.kind == RECIPE and requirement.profession
            if name then
                local craft = byName[name]
                if not craft then
                    local rank = professions and professions[name]
                    craft = { profession = name, skill = 0, rank = rank,
                        status = professions and (rank and "crafter" or "other") or nil }
                    byName[name] = craft
                    crafts[#crafts + 1] = craft
                    if craft.status == "crafter" or (craft.status == "other" and status == nil) then
                        status = craft.status
                    end
                end
                craft.skill = math.max(craft.skill, requirement.skill or 0)
            end
        end
    end
    table.sort(crafts, function(a, b) return a.profession < b.profession end)
    return crafts, status
end

local BINDINGS = { [0] = "none", [1] = "pickup", [2] = "equip" }

function Reputation.Binding(itemId)
    local info = (C_Item and C_Item.GetItemInfo) or GetItemInfo
    if not info or not itemId then return nil end
    local ok, name, bind = pcall(function()
        local values = { info(itemId) }
        return values[1], values[14]
    end)
    if not ok or not name then return nil end
    return BINDINGS[bind]
end

function Reputation.RecipeName(requirement)
    local info = (C_Item and C_Item.GetItemInfo) or GetItemInfo
    if requirement.recipe and info then
        local ok, name = pcall(info, requirement.recipe)
        if ok and name then return name end
    end
    return requirement.via
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
    local formulas = {}   -- an enchant the one-handed and two-handed weapons share counts once, at the first
    for _, group in ipairs(ns.Enchants.For(class, spec, phase)) do
        for index, id in ipairs(group.ids) do
            local requirement = not formulas[id] and Reputation.EnchantRequirement(id)
            if requirement then
                formulas[id] = true
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
    for _, group in ipairs(artisan) do
        local _, status = Reputation.Crafts(group)
        group.craftStatus, group.crafter = status, status == "crafter"
    end
    table.sort(artisan, function(a, b)
        if a.crafter ~= b.crafter then return a.crafter end
        return Order(a, b)
    end)
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
            local status = Reputation.Status(requirement)
            if status == "met" then
                line.met = line.met + 1
            elseif status == "unknown" or status == "other" then
                line.state = status
            end
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

local NEED_KEYS = { [WEAR] = "REP_NEED", [QUEST] = "REP_NEED_QUEST" }

-- What a profession calls its recipes: a pattern, plans, a formula...
function Reputation.RecipeWord(requirement)
    local profession = requirement.profession or (requirement.enchant and "Enchanting")
    local key = profession and ("REP_RECIPE_" .. profession:gsub(" ", "_"))
    local word = key and L[key]
    if not word or word == key then return L.REP_RECIPE end
    return word
end

function Reputation.NeedText(requirement)
    local faction, standing = Reputation.FactionName(requirement.factionID), Reputation.StandingName(requirement.standing)
    if requirement.kind == RECIPE then return L.REP_NEED_RECIPE:format(Reputation.RecipeWord(requirement), faction, standing) end
    return L[NEED_KEYS[requirement.kind] or "REP_NEED"]:format(faction, standing)
end

function Reputation.StateText(requirement)
    -- a recipe: the crafter's reputation counts. Only a player of that profession is told theirs.
    if requirement.kind == RECIPE then
        local crafter = Reputation.Crafter(requirement)
        if crafter == "other" then return GREY .. ns.ProfessionName(requirement.profession) .. "|r" end
        if crafter ~= "crafter" then return GREY .. L.REP_FOR_CRAFTER .. "|r" end
    end
    local status = Reputation.Status(requirement)
    if status == "met" then return GOLD .. L.REP_MET .. "|r" end
    if status == "unknown" then return WHITE .. L.REP_UNKNOWN .. "|r" end
    if status == "other" then return GREY .. L.REP_OTHER_SIDE .. "|r" end
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

function Reputation.Sellers(group)
    local sellers, seen, counted, unknown = {}, {}, {}, 0
    local function Add(text, vendor)
        if seen[text] then return end
        seen[text] = true
        sellers[#sellers + 1] = { text = text, map = vendor and vendor.map, x = vendor and vendor.x,
            y = vendor and vendor.y }
    end
    for _, standing in ipairs(Reputation.STANDINGS) do
        for _, entry in ipairs(group.steps[standing] or {}) do
            local requirement = entry.requirement
            if requirement.kind == QUEST then
                Add(L.REP_SELLER_QUEST:format(requirement.via or L.REP_UNKNOWN))
            elseif requirement.kind == RECIPE then
                local name, line = Reputation.RecipeName(requirement) or L.REP_UNKNOWN, VendorLine(requirement.vendor)
                if line then
                    Add(L.REP_SELLER_RECIPE_AT:format(name, line), Catalog().vendors[requirement.vendor])
                else
                    Add(L.REP_SELLER_RECIPE:format(name))
                end
            else
                local line = VendorLine(requirement.vendor)
                if line then
                    Add(line, Catalog().vendors[requirement.vendor])
                elseif requirement.via then
                    Add(L.REP_SELLER_QUEST:format(requirement.via))
                else
                    local piece = entry.id or entry.enchant or entry
                    if not counted[piece] then
                        counted[piece] = true
                        unknown = unknown + 1
                    end
                end
            end
        end
    end
    -- the pieces no source places: said, not dropped
    if not sellers[1] then
        Add(L.REP_UNKNOWN)
    elseif unknown > 0 then
        Add(L.REP_SELLER_REST:format(unknown))
    end
    return sellers
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
        local name = Reputation.RecipeName(requirement) or L.REP_UNKNOWN
        return L.REP_TIP_RECIPE:format(profession and (name .. " (" .. profession .. ")") or name)
    end
    return L.REP_TIP_VENDOR:format(VendorLine(requirement.vendor) or L.REP_UNKNOWN)
end

function Reputation.TooltipLines(itemId)
    local requirement = Reputation.Requirement(itemId)
    if not requirement then return {} end
    -- a recipe of another profession: the player's own standing says nothing of the piece
    local crafter = Reputation.Crafter(requirement)
    local earned = Reputation.Status(requirement) == "met" and crafter ~= "other"
    local lines = { {
        text = L.REP_TIP_NEED:format(Reputation.NeedText(requirement)),
        r = 1, g = earned and 0.82 or 1, b = earned and 0 or 1,
    } }
    local function Quiet(text) lines[#lines + 1] = { text = text, r = MUTED[1], g = MUTED[2], b = MUTED[3] } end
    if crafter == "other" then
        Quiet(L.REP_CRAFT_NOT_YOURS:format(ns.ProfessionName(requirement.profession)))
    else
        Quiet(L.REP_YOU:format(Reputation.ProgressText(requirement.factionID)))
    end
    Quiet(SourceLine(requirement))
    if requirement.kind == WEAR then
        Quiet(L.REP_TIP_PRICE:format(requirement.price and Money(requirement.price) or L.REP_UNKNOWN))
    elseif requirement.kind == RECIPE then
        Quiet(L.REP_TIP_RECIPE_VENDOR:format(VendorLine(requirement.vendor) or L.REP_UNKNOWN))
    end
    local faction = Catalog().factions[requirement.factionID]
    Quiet(faction and faction.quests > 0 and L.REP_TIP_FARM or L.REP_TIP_FARM_UNKNOWN)
    return lines
end

local function TakesClass(classes, class)
    local number = CLASS_NUMBERS[class or ""]
    if classes == 0 or not number then return true end
    return math.floor(classes / 2 ^ (number - 1)) % 2 == 1
end

-- The quest helps on the way from Neutral to Exalted (_build/reputations.py, usable): it is not offered only
-- below Neutral, nor only at Exalted.
local function Usable(method)
    return (method.from or NEUTRAL) < EXALTED and (method.upto == nil or method.upto > NEUTRAL)
end

-- What is known of how to earn a faction. The quests are QuestieDB's; what no source says stays unknown.
function Reputation.Ways(factionID, class)
    local faction = Catalog().factions[factionID]
    local side = ns.PlayerSide()
    local ways = { total = 0, listed = 0, repeatable = 0, once = 0, quests = {}, checks = {}, unknowns = {} }
    local whole, branches = false, {}
    if faction then
        ways.total = faction.quests
        for _, method in ipairs(faction.methods) do
            if (method.side == "" or method.side == side) and TakesClass(method.classes, class) then
                ways.quests[#ways.quests + 1] = { quest = method.quest, amount = method.amount, repeats = method.repeats,
                    from = method.from, upto = method.upto }
                if not Usable(method) then
                    -- listed, counted nowhere
                elseif method.repeats then
                    ways.repeatable = ways.repeatable + 1
                    whole = whole or method.upto == nil or method.upto >= EXALTED
                elseif method.choice then
                    -- of the branches that exclude one another, the one that gives the most counts
                    local set, branch = method.choice:match("^(%d+):(%d+)$")
                    branches[set] = branches[set] or {}
                    branches[set][branch] = (branches[set][branch] or 0) + method.amount
                else
                    ways.once = ways.once + method.amount
                end
            end
        end
        ways.listed = #ways.quests
    end
    for _, totals in pairs(branches) do
        local most = 0
        for _, amount in pairs(totals) do most = math.max(most, amount) end
        ways.once = ways.once + most
    end
    local note = L["REP_NOTE_" .. factionID]
    if note ~= "REP_NOTE_" .. factionID then ways.checks[1] = note end
    if ways.total == 0 then
        ways.unknowns[1] = L.REP_WAY_NONE
    else
        if not whole then ways.unknowns[#ways.unknowns + 1] = L.REP_WAY_ROUTE end
        ways.unknowns[#ways.unknowns + 1] = L.REP_WAY_CREATURES
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
pcall(events.RegisterEvent, events, "SKILL_LINES_CHANGED")   -- a profession learned or a skill gained: the recipes follow
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
