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
--   OPTION_CHANGED(key, value)   an option was switched, or the phase ("phase") was changed
--   CUSTOM_CHANGED()             an item was added to a list by hand, or taken out (Custom.lua)
--   LOGIN()                      the character is in the world
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
    unsourced = false,     -- count the items with no known source
    seenOnly = false,      -- count only the items ForeverDB players have seen in Forever
    minimap = true,        -- the button on the minimap
    minimapAngle = 215,    -- where it sits around the minimap, in degrees
    lists = { pve = true, pvp = true }, -- the lists tooltips read
    compact = true,        -- the window: an item on one line instead of two
    listAlts = true,       -- the window: the alternatives too, not only the best picks
    window = {},           -- where the window was left: point, relativePoint, x, y
    windowHeight = 0,      -- its height once resized (0: not resized)
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
-- Per character (EasyBISCharDB): the class, spec and list the window shows, and the phase.
ns.char = {}

local function InitDB()
    if type(EasyBISDB) ~= "table" then EasyBISDB = {} end
    ns.db = Merge(EasyBISDB, DEFAULTS)
    if type(EasyBISCharDB) ~= "table" then EasyBISCharDB = {} end
    ns.char = EasyBISCharDB
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

---------------------------------------------------------------------------
-- The player
---------------------------------------------------------------------------

function ns.PlayerClass()
    local _, token = UnitClass("player")
    return token
end

-- "a" or "h": the lists leave out the other faction's items.
function ns.PlayerSide()
    local faction = UnitFactionGroup and UnitFactionGroup("player")
    return faction == "Horde" and "h" or "a"
end

-- The content phase the lists stop at: 0 before the raids, 1 and up a phase, 9 everything the data
-- holds. Each character keeps its own; until it picks one, it follows the phase the game is in.
local function KnownPhase(phase)
    local meta = ns.data and ns.data.meta or {}
    for _, known in ipairs(meta.phases or {}) do
        if known == phase then return true end
    end
    return false
end

function ns.Phase()
    if KnownPhase(ns.char.phase) then return ns.char.phase end
    return ns.data and ns.data.meta and ns.data.meta.phase or 0
end

function ns:SetPhase(phase)
    if not KnownPhase(phase) or phase == ns.Phase() then return end
    self.char.phase = phase
    self:Fire("OPTION_CHANGED", "phase", phase)
end

-- What the lists are filtered on. Two characters with the same key see the same lists.
function ns.Filter()
    return {
        side = ns.PlayerSide(),
        unsourced = ns:GetOption("unsourced"),
        seenOnly = ns:GetOption("seenOnly"),
        phase = ns.Phase(),
    }
end

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
