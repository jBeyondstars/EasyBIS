local _, ns = ...
local L = ns.L

--[[
The best enchants, armor kits and scopes per spec (Data\Enchants.lua).

  Enchants.For(class, spec, phase)   { { key = "chest", ids = { "i273593", "s20025", ... } }, ... } best first:
                                     the first PER_KEY of each key that the content phase has (ns.Phase when
                                     none is given)
  Enchants.Info(id)                  { id, kind = "spell"|"item", number, name, effect, where, origin } or nil,
                                     plus what the "where" sentence says: profession, skill, recipe, seller,
                                     drop, trainer, scroll; or category, detail, place for an item to apply
                                     that a quest, a boss or a vendor gives
  Enchants.Kind(info)                "Enchanting (300)"; "Quest"; "Enchant" or "Item to apply" when the
                                     sentence names neither a profession nor a source
  Enchants.Detail(info)              "Formula sold by Alynsia (Redridge Mountains), or a scroll";
                                     "Libram of Protection - Dire Maul"
  Enchants.Category(info)            the source category whose picture goes with it (Sources.Icon)
  Enchants.Where(info)               the source in a sentence, for a tooltip
  Enchants.Name(info)                the game's name for it, in its language; the data's until the game knows it
  Enchants.ShortName(info)           what sets it apart, for a small space: "Greater Stats"
  Enchants.Icon(info)                its picture, or nil
  Enchants.SlotOf(key)               the gear slot an enchant key goes with (w2h -> main, shield -> off...)
  Enchants.KeyOf(slot, id, twoHand)  the enchant key of an item worn in a slot, or nil when the game does not
                                     know the item or nothing goes on it (a wand, a relic)

An id is "s<spell id>" for an enchant, "i<item id>" for something applied
from the bags. The name, the effect and the source sentence are ForeverDB's,
in English; the window asks the game for the name in its own language, and
puts the sentence in a few words of its own. The sentence of an item to apply
that ForeverDB's data has no source for is read in QuestieDB by the generator
(_build/questie.py), with the label t.
]]

local Enchants = {}
ns.Enchants = Enchants

-- Display order.
Enchants.KEYS = {
    "head", "neck", "shoulder", "back", "chest", "wrist", "hands", "legs", "feet",
    "w1h", "w2h", "shield", "held", "rng",
}

-- Enchants shown per key (the generator's ENCHANTS_PER_SLOT).
Enchants.PER_KEY = 3

local SLOT_OF = { w1h = "main", w2h = "main", shield = "off", held = "off", rng = "ranged" }
local UNKNOWN_WHERE = "where it comes from isn't known yet"

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon
local GetInstant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant

-- What is held in the off hand -> its enchant key.
local OFF_HAND = {
    INVTYPE_SHIELD = "shield", INVTYPE_HOLDABLE = "held", INVTYPE_WEAPON = "w1h", INVTYPE_WEAPONOFFHAND = "w1h",
}
local WEAPON_CLASS, WAND_SUBCLASS = 2, 19

function Enchants.SlotOf(key)
    return SLOT_OF[key] or key
end

-- The generator's rule (_build/luaout.py, _ENCHANT_GOES_ON), from what the game says of the item: armor
-- takes its slot's enchants, a weapon those of what it is. Bows, guns and crossbows take a scope; wands,
-- thrown weapons and relics take nothing.
function Enchants.KeyOf(slot, id, twoHand)
    if slot == "main" then return twoHand and "w2h" or "w1h" end
    if slot ~= "off" and slot ~= "ranged" then return slot end
    if not GetInstant then return nil end
    local _, _, _, equipLoc, _, classID, subclassID = GetInstant(id)
    if slot == "off" then return OFF_HAND[equipLoc or ""] end
    if equipLoc == "INVTYPE_RANGED" then return "rng" end
    if equipLoc == "INVTYPE_RANGEDRIGHT" and not (classID == WEAPON_CLASS and subclassID == WAND_SUBCLASS) then
        return "rng"
    end
    return nil
end

function Enchants.KeyName(key)
    local name = L["ENCH_" .. key]
    if name ~= "ENCH_" .. key then return name end
    return ns.SlotName(key)
end

---------------------------------------------------------------------------
-- The lists
---------------------------------------------------------------------------

local decoded = {}   -- [class] = { [spec] = { [key] = { { id, phase }, ... } } }

local function Decode(class)
    if decoded[class] then return decoded[class] end
    local perSpec = {}
    local text = ns.data and ns.data.enchants and ns.data.enchants[class] or ""
    for line in text:gmatch("[^\n]+") do
        local spec, key, list = line:match("^E\t(%d+)\t(%w+)\t(.*)$")
        if spec then
            spec = tonumber(spec)
            perSpec[spec] = perSpec[spec] or {}
            local entries = {}
            for token in list:gmatch("%S+") do
                -- "s20025", or "s20025:1" when it needs a raid of that phase
                local id, phase = token:match("^([si]%d+):?(%d*)$")
                if id then entries[#entries + 1] = { id = id, phase = tonumber(phase) or 0 } end
            end
            perSpec[spec][key] = entries
        end
    end
    decoded[class] = perSpec
    return perSpec
end

function Enchants.For(class, spec, phase)
    phase = phase or ns.Phase()
    local perKey = Decode(class)[spec] or {}
    local list = {}
    for _, key in ipairs(Enchants.KEYS) do
        local ids = {}
        for _, entry in ipairs(perKey[key] or {}) do
            if #ids >= Enchants.PER_KEY then break end
            if entry.phase <= phase then ids[#ids + 1] = entry.id end
        end
        if ids[1] then list[#list + 1] = { key = key, ids = ids } end
    end
    return list
end

---------------------------------------------------------------------------
-- One enchant
---------------------------------------------------------------------------

-- ForeverDB says where an enchant comes from in a sentence:
--   <Profession> <skill>: recipe <Formula|Pattern|...>: <name>[, sold by <who>][, drops in <where>]
--   <Profession> <skill>: from a trainer
-- with "; or Forever's scroll <name>" after it when a scroll does the same, or
--   where it comes from isn't known yet
-- The generator writes the sources it reads in QuestieDB (_build/questie.py) as
--   <what>: <name>            Quest: Libram of Voracity
--   <what>: <name> (<place>)  Quest: Libram of Protection (Dire Maul)
local PLACED = {
    ["Quest"] = "quest", ["Raid drop"] = "raid", ["Dungeon drop"] = "dungeon", ["Drop"] = "drop",
    ["Rare drop"] = "rare", ["Vendor"] = "vendor", ["Chest"] = "chest", ["Container"] = "container",
}

local function ReadWhere(record)
    local profession, skill, rest = record.where:match("^(%a+) (%d+): (.*)$")
    if not profession then
        local what, said = record.where:match("^(%a[%a ]*): (.+)$")
        if PLACED[what or ""] then
            local name, place = said:match("^(.+) %(([^()]+)%)$")
            record.category, record.detail, record.place = PLACED[what], name or said, place
        end
        return
    end
    record.profession, record.skill = profession, tonumber(skill)
    local alone = rest:match("^(.-); or Forever's scroll .*$")
    if alone then
        rest = alone
        record.scroll = true
    end
    if rest == "from a trainer" then
        record.trainer = true
        return
    end
    local recipe, tail = rest:match("^recipe (%a+): (.*)$")
    if not recipe then return end
    record.recipe = recipe
    record.seller = tail:match(", sold by (.+)$")
    record.drop = tail:match(", drops in (.+)$")
end

local info   -- [id] = line, split on first use

function Enchants.Info(id)
    if not info then
        info = {}
        for line in (ns.data and ns.data.enchantInfo or ""):gmatch("[^\n]+") do
            local key = line:match("^([^|]+)|")
            if key then info[key] = line end
        end
    end
    local line = info[id]
    if type(line) == "table" then return line end
    if not line then return nil end
    local _, name, effect, where, origin = line:match("^([^|]*)|([^|]*)|([^|]*)|([^|]*)|([^|]*)$")
    local kind, number = id:match("^([si])(%d+)$")
    local record = {
        id = id,
        kind = kind == "s" and "spell" or "item",
        number = tonumber(number),
        name = name or id,
        effect = effect or "",
        where = where or "",
        origin = origin,
    }
    ReadWhere(record)
    info[id] = record
    return record
end

function Enchants.Name(record)
    if record.kind == "spell" then
        if C_Spell and C_Spell.GetSpellName then
            local ok, name = pcall(C_Spell.GetSpellName, record.number)
            if ok and name then return name end
        end
        if GetSpellInfo then
            local ok, name = pcall(GetSpellInfo, record.number)
            if ok and type(name) == "string" then return name end
        end
    elseif GetInfo then
        local name = GetInfo(record.number)
        if name then return name end
    end
    return record.name
end

-- "Enchant Chest - Greater Stats" -> "Greater Stats"; in French the game writes "Enchantement de plastron
-- (Caractéristiques supérieures)" -> "Caractéristiques supérieures". A name built another way stays whole.
function Enchants.ShortName(record)
    local name = Enchants.Name(record)
    return name:match("^.- %- (.+)$") or name:match("%(([^()]+)%)%s*$") or name
end

function Enchants.Icon(record)
    if record.kind == "spell" then
        local get = (C_Spell and C_Spell.GetSpellTexture) or GetSpellTexture
        if get then
            local ok, icon = pcall(get, record.number)
            if ok and icon then return icon end
        end
        return nil
    end
    return GetIcon and GetIcon(record.number) or nil
end

function Enchants.Kind(record)
    if record.profession then
        return L.SRC_SKILL:format(ns.ProfessionName(record.profession), record.skill or 0)
    end
    if record.category then return ns.Sources.CategoryName(record.category) end
    return L["ENCH_" .. record.kind]
end

function Enchants.Category(record)
    return record.category or (record.profession and "crafted") or "unknown"
end

function Enchants.Detail(record)
    local text
    if record.category then
        return ns.Sources.Line({ detail = record.detail, zone = record.place, percent = "" })
    elseif record.trainer then
        text = L.ENCH_TRAINER
    elseif record.recipe then
        local recipe = L["RECIPE_" .. record.recipe]
        if recipe == "RECIPE_" .. record.recipe then recipe = record.recipe end
        if record.seller then
            text = L.ENCH_SOLD:format(recipe, record.seller)
        elseif record.drop then
            text = L.ENCH_DROPS:format(recipe, record.drop)
        else
            text = L.ENCH_RECIPE:format(recipe)
        end
    elseif record.where == "" or record.where == UNKNOWN_WHERE then
        return L.SRC_unknown
    else
        return record.where   -- a sentence this file does not know: as ForeverDB wrote it
    end
    if record.scroll then text = text .. L.ENCH_OR_SCROLL end
    return text
end

-- A quest, a boss or a vendor is said as an item's source is; a profession's sentence stays ForeverDB's.
function Enchants.Where(record)
    if not record.category then return record.where end
    return L.TIP_SOURCE:format(Enchants.Kind(record) .. " - " .. Enchants.Detail(record))
end
