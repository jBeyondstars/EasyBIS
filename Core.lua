local ADDON, ns = ...

--[[
Easy BIS: best-in-slot gear lists for WoW Forever.
Data from ForeverDB.net (https://foreverdb.net), see NOTICE.txt.

This file holds what every other file needs: messages, internal callbacks,
the saved options and the player's class and faction.
]]

local GetMetadata = (C_AddOns and C_AddOns.GetAddOnMetadata) or GetAddOnMetadata
ns.version = (GetMetadata and GetMetadata(ADDON, "Version")) or "dev"

---------------------------------------------------------------------------
-- Messages
---------------------------------------------------------------------------

ns.COLOR = "|cff33d17a"
local PREFIX = ns.COLOR .. "Easy BIS|r: "

function ns:Print(message)
    DEFAULT_CHAT_FRAME:AddMessage(PREFIX .. message)
end

---------------------------------------------------------------------------
-- Internal callbacks
--   OPTION_CHANGED(key, value)   an option was switched, or the phase ("phase"), the number of
--                                alternatives ("altCount") or the faction of the lists ("side") was changed
--   CUSTOM_CHANGED()             an item was added to a list by hand, or taken out (Custom.lua)
--   LOGIN()                      the character is in the world
--   REPUTATION_CHANGED()         the game says the character's reputations changed (Reputation.lua)
---------------------------------------------------------------------------

local listeners = {}

function ns:On(event, callback)
    listeners[event] = listeners[event] or {}
    table.insert(listeners[event], callback)
end

function ns:Fire(event, ...)
    for _, callback in ipairs(listeners[event] or {}) do
        callback(...)
    end
end

---------------------------------------------------------------------------
-- Saved options (EasyBISDB, shared by every character)
---------------------------------------------------------------------------

local DEFAULTS = {
    tooltip = true,        -- BIS lines in item tooltips
    onlyMyClass = false,   -- tooltips: my class only
    alternatives = true,   -- tooltips: the alternatives too, not only the best picks
    repTooltip = true,     -- tooltips: the reputation an item asks for
    repCompact = true,     -- the window: a reputation's standing without its numbers
    dismissedNotices = {}, -- window notices dismissed for this account, keyed by notice
    unsourced = false,     -- count the items with no known source
    seenOnly = false,      -- count only the items ForeverDB players have seen in Forever
    availableNow = false,  -- the window's checkbox: count only what a player can get today
    pvpRewards = { pve = false, pvp = true }, -- per list: count the PvP rewards (ranks, honor, battlegrounds)
    altCount = 2,          -- picks listed after the best one of a slot, second ring or trinket included
    minimap = true,        -- the button on the minimap
    minimapAngle = 215,    -- where it sits around the minimap, in degrees
    auctionTab = true,     -- the EasyBis tab of the auction house
    lists = { pve = true, pvp = true, aoe = true }, -- tooltip visibility, also keyed by "gearN" for named lists
    compact = true,        -- the window: an item or a consumable on one line instead of two
    listAlts = true,       -- the window: the alternatives too, not only the best picks
    dungeonGrid = false,   -- the Dungeons tab: a line per piece and a column per dungeon, instead of a band per dungeon
    window = {},           -- where the window was left: point, relativePoint, x, y
    windowHeight = 0,      -- its height once resized (0: not resized)
    gearLists = {},        -- named equipment lists, in tab order
    custom = {},           -- the items added by hand (Custom.lua)
}

local function Merge(target, source)
    for key, value in pairs(source) do
        if type(value) == "table" then
            if type(target[key]) ~= "table" then target[key] = {} end
            Merge(target[key], value)
        elseif target[key] == nil then
            target[key] = value
        end
    end
    return target
end

-- Until the saved variables are read, the defaults stand in.
ns.db = Merge({}, DEFAULTS)
-- Per character (EasyBISCharDB): the class, spec and list the window shows, the phase, and the faction the
-- lists are for when it is not the character's.
ns.char = {}

-- Saved lists use stable IDs. Hunter 3 is the archived melee Survival profile.
function ns.ActiveSpec(class, spec)
    if class == "HUNTER" and spec == 3 then return 4 end
    return spec
end

local function InitDB()
    if type(EasyBISDB) ~= "table" then EasyBISDB = {} end
    -- version 1.1.0 kept one answer for both lists: it becomes the PvE list's
    if type(EasyBISDB.pvpRewards) == "boolean" then EasyBISDB.pvpRewards = { pve = EasyBISDB.pvpRewards } end
    -- The old PvE tooltip switch also hid AoE and all existing named lists.
    local lists = EasyBISDB.lists
    local migrateHiddenPvE = type(lists) == "table" and lists.pve == false and lists.aoe == nil
    ns.db = Merge(EasyBISDB, DEFAULTS)
    if migrateHiddenPvE then lists.aoe = false end
    -- Older characters saved "gearN" using the original array position.
    local last = ns.db.lastGearId or 0
    for i, gear in ipairs(ns.db.gearLists) do
        gear.id = gear.id or i
        if migrateHiddenPvE then lists["gear" .. gear.id] = false end
        last = math.max(last, gear.id)
    end
    ns.db.lastGearId = last
    if type(EasyBISCharDB) ~= "table" then EasyBISCharDB = {} end
    ns.char = EasyBISCharDB
    ns.char.spec = ns.ActiveSpec(ns.char.class or ns.PlayerClass(), ns.char.spec)
end

function ns:GetOption(key)
    return self.db[key] == true
end

-- Switches an on/off option.
function ns:SetOption(key, value)
    value = value and true or false
    if type(DEFAULTS[key]) ~= "boolean" or self.db[key] == value then return end
    self.db[key] = value
    self:Fire("OPTION_CHANGED", key, value)
end

function ns:ListShown(list)
    return self.db.lists[list] ~= false
end

function ns:SetListShown(list, shown)
    if self:ListShown(list) == shown then return end
    self.db.lists[list] = shown
    self:Fire("OPTION_CHANGED", "lists", self.db.lists)
end

-- Whether a list ("pve", "pvp") counts the PvP rewards: the PvP list does and the PvE list does not, until
-- the player says otherwise for that list.
function ns:PvPRewards(list)
    return self.db.pvpRewards[list] == true
end

function ns:SetPvPRewards(list, value)
    value = value and true or false
    if DEFAULTS.pvpRewards[list] == nil or self.db.pvpRewards[list] == value then return end
    self.db.pvpRewards[list] = value
    self:Fire("OPTION_CHANGED", "pvpRewards", value)
end

-- How many picks a slot lists after its best one (the second ring or trinket among them): from
-- ns.ALTERNATIVES to what the data files keep of a ladder (Data\Meta.lua).
function ns.MaxAlternatives()
    local kept = ns.data and ns.data.meta and tonumber(ns.data.meta.alternatives)
    return math.max(ns.ALTERNATIVES, kept or ns.ALTERNATIVES)
end

function ns.Alternatives()
    local count = math.floor(tonumber(ns.db.altCount) or ns.ALTERNATIVES)
    return math.max(ns.ALTERNATIVES, math.min(count, ns.MaxAlternatives()))
end

-- A number out of the range is brought back into it.
function ns:SetAlternatives(count)
    count = math.floor(tonumber(count) or ns.ALTERNATIVES)
    count = math.max(ns.ALTERNATIVES, math.min(count, ns.MaxAlternatives()))
    if count == ns.Alternatives() and self.db.altCount == count then return end
    self.db.altCount = count
    self:Fire("OPTION_CHANGED", "altCount", count)
end

---------------------------------------------------------------------------
-- The player
---------------------------------------------------------------------------

function ns.PlayerClass()
    local _, token = UnitClass("player")
    return token
end

-- "a" or "h": the character's faction, as the game says.
function ns.CharacterSide()
    local faction = UnitFactionGroup and UnitFactionGroup("player")
    return faction == "Horde" and "h" or "a"
end

-- "a" or "h": the faction the lists are for, the character's until the player picks the other one. The lists
-- leave out the other faction's items, or show their twin; the tooltips and the reputations follow it too.
function ns.PlayerSide()
    local chosen = ns.char.side
    if chosen == "a" or chosen == "h" then return chosen end
    return ns.CharacterSide()
end

-- "a", "h", or nil for the character's own: picking the character's faction goes back to following it.
function ns:SetSide(side)
    if side ~= "a" and side ~= "h" or side == ns.CharacterSide() then side = nil end
    if side == self.char.side then return end
    local before = ns.PlayerSide()
    self.char.side = side
    if ns.PlayerSide() ~= before then self:Fire("OPTION_CHANGED", "side", ns.PlayerSide()) end
end

-- The content phase the lists stop at: 0 before the raids, 1 and up a phase, 9 everything the data
-- holds. Each character keeps its own; until it picks one, it follows the phase the game is in, as it
-- does whatever it picked while the lists show what is available now.
local function KnownPhase(phase)
    local meta = ns.data and ns.data.meta or {}
    for _, known in ipairs(meta.phases or {}) do
        if known == phase then return true end
    end
    return false
end

function ns.Phase()
    local game = ns.data and ns.data.meta and ns.data.meta.phase or 0
    if ns:GetOption("availableNow") or not KnownPhase(ns.char.phase) then return game end
    return ns.char.phase
end

function ns:SetPhase(phase)
    if not KnownPhase(phase) or phase == ns.Phase() then return end
    self.char.phase = phase
    self:Fire("OPTION_CHANGED", "phase", phase)
end

-- The PvP ranks of a season are capped, and the cap rises at every weekly reset (_build/ranks.py).
local WEEK = 7 * 24 * 60 * 60
local TOP_RANK = 14

-- The week of the season, from 1: how many weekly resets have passed since it began, plus one.
function ns.SeasonWeek()
    local start = ns.data and ns.data.meta and ns.data.meta.seasonStart
    if not start then return 1 end
    local now = GetServerTime()
    local left = C_DateAndTime and C_DateAndTime.GetSecondsUntilWeeklyReset
        and C_DateAndTime.GetSecondsUntilWeeklyReset()
    left = left or (WEEK - (now - start) % WEEK)
    return math.max(1, math.ceil((now + left - start) / WEEK))
end

-- The highest rank a player can have this week.
function ns.RankCap()
    local caps = ns.data and ns.data.meta and ns.data.meta.rankCaps
    if not caps then return TOP_RANK end
    return caps[math.min(ns.SeasonWeek(), #caps)]
end

-- What the lists are filtered on. Two characters with the same key see the same lists. What is available
-- now stops at the week's rank cap and the game's phase (ns.Phase), and leaves out the items of no known
-- source, whatever the options say.
function ns.Filter()
    local availableNow = ns:GetOption("availableNow")
    return {
        side = ns.PlayerSide(),
        unsourced = ns:GetOption("unsourced") and not availableNow,
        seenOnly = ns:GetOption("seenOnly"),
        rankCap = availableNow and ns.RankCap() or nil,
        pvpRewards = { pve = ns:PvPRewards("pve"), pvp = ns:PvPRewards("pvp") },
        phase = ns.Phase(),
        alternatives = ns.Alternatives(),
    }
end

-- The options (and the phase) that change what the lists hold: OPTION_CHANGED keys.
ns.FILTER_OPTIONS = { unsourced = true, seenOnly = true, availableNow = true, pvpRewards = true, phase = true,
    side = true,
    altCount = true }

---------------------------------------------------------------------------
-- Startup
---------------------------------------------------------------------------

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_LOGIN")
events:SetScript("OnEvent", function(self, event, arg1)
    if event == "ADDON_LOADED" and arg1 == ADDON then
        self:UnregisterEvent("ADDON_LOADED")
        InitDB()
    elseif event == "PLAYER_LOGIN" then
        self:UnregisterEvent("PLAYER_LOGIN")
        ns:Fire("LOGIN")
    end
end)
