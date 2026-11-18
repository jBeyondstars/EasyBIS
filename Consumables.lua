local _, ns = ...
local L = ns.L

--[[
The consumables of a spec, category by category (Data\Consumables.lua).

  Consumables.For(class, spec, list, phase)   { { key = "flask", ranked = { { id, score, twin }, ... }, unranked = { id, ... } }, ... }
                                     in display order: of each category the first PER_CATEGORY of the content phase
                                     (ns.Phase when none is given), what ties with the last of them, then what is
                                     listed without a rank. A twin is the sharp or blunt version of the entry before
                                     it: the weapon decides which is of use, and the two take one place
  Consumables.Has(class, spec, list, key)   whether that list has something in a category
  Consumables.Info(id)               { id, name, effect, where, origin, zoneRule, zone } or nil, plus what the "where" sentence says:
                                     profession, skill, trainer, seller, drop, quest, found, unknownRecipe; or category,
                                     detail, place for what a vendor, a quest or a creature gives
  Consumables.Kind(info)             "Alchemy (300)"; "Vendor"; "Unknown source"
  Consumables.Detail(info)           "Recipe sold by Kania (Silithus)"
  Consumables.Category(info)         the source category whose picture goes with it (Sources.Icon)
  Consumables.Where(info)            the source in a sentence, for a tooltip
  Consumables.ZoneNote(info)         what its zone changes, in a sentence; nil for what works everywhere
  Consumables.Name(info)             the game's name for it, in its language; the data's until the game knows it
  Consumables.Icon(info)             its picture, or nil
  Consumables.KeyName(key)           the category's name

A category is ranked on its own: the lists say nothing of how consumables stack, and do not make a set. The scores
are the generator's (_build/consumable_lists.py): weight x stat, or the amount restored for what heals or gives mana.
The effect and the source sentence are in English, as the generator wrote them; the tooltip is the game's.
]]

local Consumables = {}
ns.Consumables = Consumables

-- Display order.
Consumables.CATEGORIES = {
    "flask", "elixir", "food", "scroll", "weapon", "combat", "healing", "mana", "bandage", "situational",
}

-- Shown per category, ties with the last one apart (the generator's PER_CATEGORY).
Consumables.PER_CATEGORY = 3

local SITUATIONAL = "situational"
local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

function Consumables.KeyName(key)
    return L["CONS_" .. key]
end

---------------------------------------------------------------------------
-- The lists
---------------------------------------------------------------------------

local decoded = {}   -- [class] = { [spec] = { [list] = { [key] = { ranked = { ... }, unranked = { ... } } } } }

local function Listed(text)
    local entries = {}
    for token in (text or ""):gmatch("%S+") do
        local id, phase = token:match("^(%d+):?(%d*)$")
        if id then entries[#entries + 1] = { id = tonumber(id), phase = tonumber(phase) or 0 } end
    end
    return entries
end

local function Decode(class)
    if decoded[class] then return decoded[class] end
    local perSpec = {}
    local text = ns.data and ns.data.consumables and ns.data.consumables[class] or ""
    for line in text:gmatch("[^\n]+") do
        local what, spec, list, key, tokens = line:match("^([CU])\t(%d+)\t(%a+)\t(%a+)\t(.*)$")
        if what then
            spec = tonumber(spec)
            perSpec[spec] = perSpec[spec] or {}
            perSpec[spec][list] = perSpec[spec][list] or {}
            local shelf = perSpec[spec][list][key] or { ranked = {}, unranked = {} }
            perSpec[spec][list][key] = shelf
            if what == "U" then
                shelf.unranked = Listed(tokens)
            else
                for token in tokens:gmatch("%S+") do
                    -- id:phase:score*10, no phase before the raids, :t for a twin
                    local id, phase, score, twin = token:match("^(%d+):(%d*):(%d+):?(%a?)$")
                    if id then
                        shelf.ranked[#shelf.ranked + 1] = {
                            id = tonumber(id), phase = tonumber(phase) or 0, score = tonumber(score),
                            twin = twin == "t" or nil,
                        }
                    end
                end
            end
        end
    end
    decoded[class] = perSpec
    return perSpec
end

local situational = {}   -- [class] = entries

local function Situational(class)
    local perClass = ns.data and ns.data.consumableSituational
    situational[class] = situational[class] or Listed(perClass and perClass[class])
    return situational[class]
end

-- The generator's shown(): the best of the phase, and what ties with the last of them. A twin takes no place.
local function Ranked(entries, phase)
    local kept, places = {}, 0
    for _, entry in ipairs(entries) do
        if entry.phase <= phase then
            if not entry.twin then
                if places >= Consumables.PER_CATEGORY and entry.score ~= kept[#kept].score then break end
                places = places + 1
            end
            kept[#kept + 1] = { id = entry.id, score = entry.score, twin = entry.twin }
        end
    end
    return kept
end

local function Ids(entries, phase)
    local ids = {}
    for _, entry in ipairs(entries) do
        if entry.phase <= phase then ids[#ids + 1] = entry.id end
    end
    return ids
end

function Consumables.For(class, spec, list, phase)
    phase = phase or ns.Phase()
    local shelves = (Decode(class)[spec] or {})[list] or {}
    local groups = {}
    for _, key in ipairs(Consumables.CATEGORIES) do
        local shelf = shelves[key]
        local ranked = shelf and Ranked(shelf.ranked, phase) or {}
        local unranked = {}
        if key == SITUATIONAL then
            unranked = Ids(Situational(class), phase)
        elseif shelf then
            unranked = Ids(shelf.unranked, phase)
        end
        if ranked[1] or unranked[1] then
            groups[#groups + 1] = { key = key, ranked = ranked, unranked = unranked }
        end
    end
    return groups
end

function Consumables.Has(class, spec, list, key)
    for _, group in ipairs(Consumables.For(class, spec, list)) do
        if group.key == key then return true end
    end
    return false
end

---------------------------------------------------------------------------
-- One consumable
---------------------------------------------------------------------------

-- The generator says where a consumable comes from in a sentence:
--   <Profession> <skill>: from a trainer
--   <Profession> <skill>: recipe sold by <who> (<zone>)
--   <Profession> <skill>: recipe drops from <who>
--   <Profession> <skill>: recipe from the quest <title>
--   <Profession> <skill>: recipe found in <zone>
--   <Profession> <skill>: recipe, source unknown
--   Vendor: <who> (<zone>)      Quest: <title>      Drop: <who>      Container: <what holds it>
-- or: where it comes from isn't known yet
local PLACED = { ["Vendor"] = "vendor", ["Quest"] = "quest", ["Drop"] = "drop", ["Container"] = "container" }

local function ReadWhere(record)
    local profession, skill, rest = record.where:match("^(%a[%a ]-) (%d+): (.*)$")
    if not profession then
        local what, said = record.where:match("^(%a+): (.+)$")
        if PLACED[what or ""] then
            local name, place = said:match("^(.+) %(([^()]+)%)$")
            record.category, record.detail, record.place = PLACED[what], name or said, place
        end
        return
    end
    record.profession, record.skill = profession, tonumber(skill)
    if rest == "from a trainer" then
        record.trainer = true
    elseif rest:match("^recipe sold by ") then
        record.seller = rest:match("^recipe sold by (.+)$")
    elseif rest:match("^recipe drops from ") then
        record.drop = rest:match("^recipe drops from (.+)$")
    elseif rest:match("^recipe from the quest ") then
        record.quest = rest:match("^recipe from the quest (.+)$")
    elseif rest:match("^recipe found in ") then
        record.found = rest:match("^recipe found in (.+)$")
    else
        record.unknownRecipe = true
    end
end

local info   -- [id] = line, split on first use

function Consumables.Info(id)
    if not info then
        info = {}
        for line in (ns.data and ns.data.consumableInfo or ""):gmatch("[^\n]+") do
            local key = line:match("^(%d+)|")
            if key then info[tonumber(key)] = line end
        end
    end
    local line = info[id]
    if type(line) == "table" then return line end
    if not line then return nil end
    local _, name, effect, where, origin, zone = line:match("^([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)$")
    local record = { id = id, name = name or tostring(id), effect = effect or "", where = where or "", origin = origin }
    record.zoneRule, record.zone = (zone or ""):match("^(%a+):(.+)$")
    ReadWhere(record)
    info[id] = record
    return record
end

function Consumables.ZoneNote(record)
    if record.zoneRule == "only" then return L.CONS_ZONE_ONLY:format(record.zone) end
    if record.zoneRule == "bonus" then return L.CONS_ZONE_BONUS:format(record.zone) end
end

function Consumables.Name(record)
    return GetInfo and GetInfo(record.id) or record.name
end

function Consumables.Icon(record)
    return GetIcon and GetIcon(record.id) or nil
end

function Consumables.Kind(record)
    if record.profession then
        return L.SRC_SKILL:format(ns.ProfessionName(record.profession), record.skill or 0)
    end
    if record.category then return ns.Sources.CategoryName(record.category) end
    return L.SRC_unknown
end

function Consumables.Category(record)
    return record.category or (record.profession and "crafted") or "unknown"
end

function Consumables.Detail(record)
    if record.category then
        return ns.Sources.Line({ detail = record.detail, zone = record.place, percent = "" })
    elseif record.trainer then
        return L.ENCH_TRAINER
    elseif record.seller then
        return L.CONS_RECIPE_SOLD:format(record.seller)
    elseif record.drop then
        return L.CONS_RECIPE_DROP:format(record.drop)
    elseif record.quest then
        return L.CONS_RECIPE_QUEST:format(record.quest)
    elseif record.found then
        return L.CONS_RECIPE_FOUND:format(record.found)
    elseif record.unknownRecipe then
        return L.CONS_RECIPE_UNKNOWN
    end
    return L.SRC_unknown
end

function Consumables.Where(record)
    local detail = Consumables.Detail(record)
    local kind = Consumables.Kind(record)
    return L.TIP_SOURCE:format(detail ~= kind and (kind .. " - " .. detail) or kind)
end
