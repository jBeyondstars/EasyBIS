local _, ns = ...
local L = ns.L

--[[
Where an item comes from, in words (its first source in Data\Items.lua).

  Sources.Describe(id)   { category, detail, zone, percent, origin, profession }
      category   quest, dungeon, raid, crafted, vendor, reputation, pvp, drop, rare, world, chest,
                 container, unknown; manual for an item added by hand that the data does not have
      detail     the quest, the boss, the vendor, the profession...  ("" when there is nothing to say)
      zone       the dungeon or the zone, when the data has one
      percent    the drop chance as text, or ""
      origin     how the data is known: s seen in Forever, c a clue, f the Forever client, k Classic data
      profession the profession's English name, for a crafted item
  Sources.Manual()                    the description of an item only the player knows
  Sources.CategoryName(category)
  Sources.Icon(category, profession)  texture, cropped: a small picture per category (a crafted item gets its
                                      profession's); cropped is true for a square icon whose border should go
  Sources.IconText(category)          the same picture as text, for a menu
  Sources.OriginName(letter)          a short remark, only for c and k: nil otherwise
  Sources.OriginMark(letter)          the sign rows carry for it ("*", "?"), or ""
  Sources.OriginRemark(letter)        the sentence that explains the sign, or nil
  Sources.Line(description)           "detail - zone (17%)"
  Sources.Short(description)          a few words for a small space: the place, else the detail, else the
                                      category's name

The pictures tell the categories apart; the texts next to them keep one quiet
color, so the item names stay the only ones that wear the quality colors.
]]

local Sources = {}
ns.Sources = Sources

-- Display order of the Source filter.
Sources.CATEGORIES = {
    "quest", "dungeon", "raid", "crafted", "vendor", "reputation", "pvp", "drop", "rare", "world", "chest",
    "container", "unknown", "manual",
}

-- texture, and true when it is a square icon with a border to crop
local ICONS = {
    quest = { "Interface\\GossipFrame\\AvailableQuestIcon" },
    dungeon = { "Interface\\TargetingFrame\\UI-RaidTargetingIcon_8" },
    raid = { "Interface\\Icons\\INV_Misc_Head_Dragon_01", true },
    crafted = { "Interface\\Icons\\Trade_BlackSmithing", true },
    vendor = { "Interface\\GossipFrame\\VendorGossipIcon" },
    reputation = { "Interface\\GossipFrame\\TabardGossipIcon" },
    pvp = { "Interface\\GossipFrame\\BattleMasterGossipIcon" },
    drop = { "Interface\\CURSOR\\Attack" },
    rare = { "Interface\\TargetingFrame\\UI-RaidTargetingIcon_1" },
    world = { "Interface\\Icons\\INV_Misc_Map_01", true },
    chest = { "Interface\\Icons\\INV_Box_01", true },
    container = { "Interface\\Icons\\INV_Misc_OrnateBox", true },
    unknown = { "Interface\\Icons\\INV_Misc_QuestionMark", true },
    manual = { "Interface\\Icons\\INV_Misc_Note_01", true },
}

-- By the English name the data gives a profession.
local PROFESSION_ICONS = {
    Alchemy = "Interface\\Icons\\Trade_Alchemy",
    Blacksmithing = "Interface\\Icons\\Trade_BlackSmithing",
    Enchanting = "Interface\\Icons\\Trade_Engraving",
    Engineering = "Interface\\Icons\\Trade_Engineering",
    Leatherworking = "Interface\\Icons\\Trade_LeatherWorking",
    Tailoring = "Interface\\Icons\\Trade_Tailoring",
}

local ORIGIN_MARKS = { k = "*", c = "?" }

local STANDINGS = { "Hated", "Hostile", "Unfriendly", "Neutral", "Friendly", "Honored", "Revered", "Exalted" }

local function MapName(id)
    id = tonumber(id)
    if not id or id <= 0 or not (C_Map and C_Map.GetMapInfo) then return nil end
    local info = C_Map.GetMapInfo(id)
    return info and info.name or nil
end

-- The dungeon's name in the game's language, or the data's English one.
local function InstanceName(id)
    id = tonumber(id)
    if not id then return nil, nil end
    local raw = ns.data and ns.data.instances and ns.data.instances[id]
    local english, kind = nil, nil
    if raw then english, kind = raw:match("^([^%^]*)%^([^%^]*)") end
    local name = GetRealZoneText and GetRealZoneText(id)
    if not name or name == "" then name = english end
    return name, kind
end

local function Percent(text)
    local value = tonumber(text)
    if not value or value <= 0 then return "" end
    local number = value >= 10 and ("%d"):format(math.floor(value + 0.5)) or ("%.1f"):format(value)
    return L.SRC_PERCENT:format(number)
end

local function Standing(text)
    local index = (tonumber(text) or 0) + 1
    return _G["FACTION_STANDING_LABEL" .. index] or STANDINGS[index] or ""
end

-- kind -> function(fields) returning category, detail, zone, percent, origin
local READERS = {
    q = function(f) return "quest", f[3], nil, "", f[6] end,
    v = function(f)
        -- a vendor whose name the data does not have is written "NPC 12345": the zone alone says more
        local name = f[3] or ""
        if name:match("^NPC %d+$") then name = "" end
        return "vendor", name, MapName(f[4]), "", f[9]
    end,
    d = function(f)
        local zone, kind = InstanceName(f[2])
        return (f[5] == "1" or kind == "raid") and "raid" or "dungeon", f[3], zone, Percent(f[4]), f[6]
    end,
    m = function(f) return "drop", f[3], nil, Percent(f[4]), f[5] end,
    R = function(f) return "rare", f[3], nil, Percent(f[4]), f[5] end,
    c = function(f)
        local skill = tonumber(f[3]) or 0
        local profession = ns.ProfessionName(f[2])
        return "crafted", skill > 1 and L.SRC_SKILL:format(profession, skill) or profession, nil, "", f[5]
    end,
    w = function(f)
        local from, to = tonumber(f[2]) or 0, tonumber(f[3]) or 0
        return "world", from > 0 and L.SRC_LEVELS:format(from, math.max(from, to)) or "", nil, "", f[4]
    end,
    o = function(f) return "chest", f[2], nil, Percent(f[3]), f[4] end,
    x = function(f) return "container", f[3], nil, "", f[4] end,
    p = function(f) return "pvp", L.SRC_RANK:format(tonumber(f[2]) or 0), nil, "", f[4] end,
    r = function(f) return "reputation", L.SRC_REPUTATION:format(f[4] or "", Standing(f[3])), nil, "", f[5] end,
}

function Sources.Describe(id)
    local item = ns.Items.Get(id)
    local source = item and item.sources[1]
    local reader = source and READERS[source.kind]
    if not reader then
        return { category = "unknown", detail = "", percent = "", origin = "f" }
    end
    local category, detail, zone, percent, origin = reader(source)
    return {
        category = category, detail = detail or "", zone = zone, percent = percent or "", origin = origin,
        profession = source.kind == "c" and source[2] or nil,
    }
end

function Sources.Manual()
    return { category = "manual", detail = "", percent = "", origin = "" }
end

function Sources.CategoryName(category)
    return L["SRC_" .. category]
end

function Sources.Icon(category, profession)
    if profession and PROFESSION_ICONS[profession] then return PROFESSION_ICONS[profession], true end
    local icon = ICONS[category] or ICONS.unknown
    return icon[1], icon[2] or false
end

function Sources.IconText(category)
    local texture, cropped = Sources.Icon(category)
    if cropped then return ("|T%s:14:14:0:0:64:64:5:59:5:59|t"):format(texture) end
    return ("|T%s:14:14|t"):format(texture)
end

-- Said only when the data is less than sure: "s" (seen in Forever) and "f" (read in Forever's
-- files) need no remark.
function Sources.OriginName(letter)
    if not letter or letter == "" or letter == "s" or letter == "f" then return nil end
    local key = "ORIGIN_" .. letter
    local text = L[key]
    return text ~= key and text or nil
end

function Sources.OriginMark(letter)
    return ORIGIN_MARKS[letter] or ""
end

function Sources.OriginRemark(letter)
    if not ORIGIN_MARKS[letter] then return nil end
    return ORIGIN_MARKS[letter] .. " " .. L["ORIGIN_LONG_" .. letter]
end

function Sources.Line(description)
    local text = description.detail
    if description.zone and description.zone ~= "" then
        text = text ~= "" and (text .. " - " .. description.zone) or description.zone
    end
    if description.percent ~= "" then
        text = text ~= "" and (text .. " (" .. description.percent .. ")") or description.percent
    end
    return text
end

function Sources.Short(description)
    if description.zone and description.zone ~= "" then return description.zone end
    if description.detail ~= "" then return description.detail end
    return Sources.CategoryName(description.category)
end
