local _, ns = ...
local L = ns.L

--[[
Where an item comes from, in words (its first source in Data\Items.lua).

  Sources.Describe(id)   { category, detail, zone, percent, origin, profession, cost }
      category   quest, dungeon, raid, crafted, vendor, reputation, pvp, drop, rare, world, chest,
                 container, unknown; manual for an item added by hand that the data does not have
      detail     the quest, the boss, the vendor, the profession...  ("" when there is nothing to say)
      zone       the dungeon or the zone, when the data has one
      percent    the drop chance as text, or ""
      origin     how the data is known: s seen in Forever, c a clue, f the Forever client, k Classic data,
                 t read in QuestieDB, w counted in Forever (Wowhead Forever's loot counts)
      The source said is the item's first one. Among the sources read in QuestieDB (t), a quest or a
      vendor of the other faction is passed over when the item has another: a set sold in Ironforge
      and in Orgrimmar names the vendor of the player's side.
      profession the profession's English name, for a crafted item
      cost       what the vendor asks in a currency: { item = the currency's item id, amount, beta = true when
                 the price is the beta's and was not read in the game }; nil for anything else
  Sources.Manual()                    the description of an item only the player knows
  Sources.CategoryName(category)
  Sources.Icon(category, profession)  texture, cropped: a small picture per category (a crafted item gets its
                                      profession's); cropped is true for a square icon whose border should go
  Sources.IconText(category)          the same picture as text, for a menu
  Sources.OriginName(letter)          a short remark, only for c, k and t: nil otherwise
  Sources.OriginMark(letter)          the sign rows carry for it ("*", "?"), or ""
  Sources.OriginRemark(letter)        the sentence that explains the sign, or nil
  Sources.Line(description)           "detail - zone (17%)"
  Sources.Short(description)          a few words for a small space: the place, else the detail, else the
                                      category's name
  Sources.CostText(cost)              "75 Reals", the currency's picture before its name when the game has one
  Sources.WithCost(text, cost)        "75 Reals · text": the price first, so a narrow row cuts the place and not it
  Sources.Held(item)                  how much of a currency the player has, bank included; nil when the game
                                      cannot say. The game may keep it as a currency or as an item: the larger
                                      of the two counts
  Sources.CostLine(cost)              the tooltip's line: the price, what the player has and what is missing
  Sources.ToPay(cells)                what is left to pay for cells ({ id, source }, ...), per currency:
                                      { { item, amount, held }, ... }. What the player owns is paid for
  Sources.ToPayLine(owed)             the character sheet's line for one of those
  Sources.Owned(id)                   whether the player has the item, worn, in the bags or in the bank
  Sources.Runs(id)                    the dungeon runs an item is farmed in, or nil for an item of elsewhere:
                                      { { run, instance, wing, boss, percent, origin, quest }, ... }
      An item is a dungeon's when the source the addon says for it (the first, see Describe) is a boss of a
      dungeon, and then every boss of a dungeon among its sources counts; or when that source is a quest done
      in a dungeon (ns.data.questRuns), and then quest holds its title and there is no boss. A raid is no run.
      run        what tells one run from another: "<instance>", or "<instance>:<wing>" for a boss of an
                 instance that is run wing by wing (ns.data.wings) when the data places the boss in one
      percent    the drop chance as a number, nil when the data has none
  Sources.RunName(instance, wing)     the run's name: the wing's, in the game's language where Easy BIS has
                                      it, else the instance's
  Sources.HasWings(instance)          whether the instance is run wing by wing
  Sources.PercentText(value)          "17%", "4.2%"; "" for nothing

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

-- Classic's data and QuestieDB's wear the same sign: known from elsewhere, not confirmed in Forever.
local ORIGIN_MARKS = { k = "*", c = "?", t = "*" }

-- Where a source says which faction it is for: a quest, a vendor. Only QuestieDB's sources are chosen
-- on it: ForeverDB's data marks vendors of Alliance towns as Horde ones (Theramore Pauldrons).
local SIDE_FIELD = { q = 5, v = 8 }
local SIDED_ORIGIN = "t"

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
    p = function(f)
        local rank = tonumber(f[2]) or 0
        return "pvp", rank > 0 and L.SRC_RANK:format(rank) or L.SRC_HONOR, nil, "", f[4]
    end,
    r = function(f) return "reputation", L.SRC_REPUTATION:format(f[4] or "", Standing(f[3])), nil, "", f[5] end,
}

-- id of the game's currency and its English name.
local function Currency(item)
    local raw = ns.data and ns.data.currencies and ns.data.currencies[item]
    if not raw then return nil end
    local currency, name = raw:match("^([^%^]*)%^([^%^]*)$")
    return { id = tonumber(currency), name = name }
end

-- A vendor's price field: copper, or "<the currency's item id>:<amount>", then ":b" while the price is the beta's.
local function Cost(source)
    if source.kind ~= "v" then return nil end
    local item, amount, flag = (source[7] or ""):match("^(%d+):(%d+):?(%a?)$")
    if not item then return nil end
    return { item = tonumber(item), amount = tonumber(amount), beta = flag == "b" }
end

local function OwnSource(item)
    local side = ns.PlayerSide and ns.PlayerSide()
    for _, source in ipairs(item.sources) do
        local wanted = source.label == SIDED_ORIGIN and source[SIDE_FIELD[source.kind] or 0]
        if not wanted or wanted == "" or wanted == side then return source end
    end
    return item.sources[1]
end

function Sources.Describe(id)
    local item = ns.Items.Get(id)
    local source = item and OwnSource(item)
    local reader = source and READERS[source.kind]
    if not reader then
        return { category = "unknown", detail = "", percent = "", origin = "f" }
    end
    local category, detail, zone, percent, origin = reader(source)
    return {
        category = category, detail = detail or "", zone = zone, percent = percent or "", origin = origin,
        profession = source.kind == "c" and source[2] or nil,
        cost = Cost(source),
    }
end

function Sources.Manual()
    return { category = "manual", detail = "", percent = "", origin = "" }
end

function Sources.PercentText(value)
    return Percent(value)
end

---------------------------------------------------------------------------
-- The runs of a dungeon
---------------------------------------------------------------------------

local wings   -- [instance] = { names = { [key] = English name }, bosses = { [boss] = key } }, split on first use

local function Wings(instance)
    if not wings then
        wings = {}
        for number, text in pairs(ns.data and ns.data.wings or {}) do
            local entry = { names = {}, bosses = {} }
            for part in text:gmatch("[^|]+") do
                local key
                for field in part:gmatch("[^%^]+") do
                    if not key then
                        key = field
                    elseif not entry.names[key] then
                        entry.names[key] = field
                    else
                        entry.bosses[field] = key
                    end
                end
            end
            wings[number] = entry
        end
    end
    return wings[instance]
end

local function Run(instance, wing)
    return wing and (instance .. ":" .. wing) or tostring(instance)
end

function Sources.HasWings(instance)
    return Wings(instance) ~= nil
end

function Sources.RunName(instance, wing)
    local known = wing and Wings(instance)
    if known and known.names[wing] then
        local key = "WING_" .. instance .. "_" .. wing
        local text = L[key]
        return text ~= key and text or known.names[wing]
    end
    return (InstanceName(instance)) or tostring(instance)
end

function Sources.Runs(id)
    local item = ns.Items.Get(id)
    local own = item and OwnSource(item)
    if not own then return nil end
    if own.kind == "q" then
        local instance, wing = ((ns.data and ns.data.questRuns or {})[tonumber(own[2]) or 0] or ""):match("^(%d+):?(%a*)$")
        instance = tonumber(instance)
        if not instance or select(2, InstanceName(instance)) == "raid" then return nil end
        if wing == "" then wing = nil end
        return { { run = Run(instance, wing), instance = instance, wing = wing, boss = "", quest = own[3] or "",
            origin = own[6] } }
    end
    local function Dungeon(source)
        local instance = source.kind == "d" and tonumber(source[2])
        return instance and source[5] ~= "1" and select(2, InstanceName(instance)) ~= "raid" and instance or nil
    end
    if not Dungeon(own) then return nil end
    local runs = {}
    for _, source in ipairs(item.sources) do
        local instance = Dungeon(source)
        if instance then
            local known = Wings(instance)
            local wing = known and known.bosses[source[3] or ""] or nil
            local percent = tonumber(source[4])
            runs[#runs + 1] = { run = Run(instance, wing), instance = instance, wing = wing, boss = source[3] or "",
                percent = percent and percent > 0 and percent or nil, origin = source[6] }
        end
    end
    return runs[1] and runs or nil
end

function Sources.CategoryName(category)
    return L["SRC_" .. category]
end

function Sources.Icon(category, profession)
    if profession and PROFESSION_ICONS[profession] then return PROFESSION_ICONS[profession], true end
    local icon = ICONS[category] or ICONS.unknown
    return icon[1], icon[2] or false
end

-- A square icon as text, without its border.
local CROPPED_ICON = "|T%s:14:14:0:0:64:64:5:59:5:59|t"

function Sources.IconText(category)
    local texture, cropped = Sources.Icon(category)
    if cropped then return CROPPED_ICON:format(texture) end
    return ("|T%s:14:14|t"):format(texture)
end

-- Said only when the data is less than sure: "s" (seen in Forever), "f" (read in Forever's files)
-- and "w" (counted in Forever) need no remark.
function Sources.OriginName(letter)
    if not letter or letter == "" or letter == "s" or letter == "f" or letter == "w" then return nil end
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

---------------------------------------------------------------------------
-- What a vendor asks in a currency
---------------------------------------------------------------------------

local function CurrencyName(item)
    local key = "CURRENCY_" .. item
    local text = L[key]
    if text ~= key then return text end
    local currency = Currency(item)
    return currency and currency.name or ns.Items.Name(item)
end

local currencyIcons = {}   -- [the currency's item id] = its picture, once the game has given it

-- The game's own picture: the currency's when it keeps one, else the item's.
local function CurrencyIcon(item)
    if currencyIcons[item] then return currencyIcons[item] end
    local icon
    local currency = Currency(item)
    if currency and currency.id and C_CurrencyInfo and C_CurrencyInfo.GetCurrencyInfo then
        local ok, info = pcall(C_CurrencyInfo.GetCurrencyInfo, currency.id)
        if ok and type(info) == "table" then icon = info.iconFileID end
    end
    local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon
    if not icon and GetIcon then
        local ok, texture = pcall(GetIcon, item)
        if ok then icon = texture end
    end
    if type(icon) ~= "number" and type(icon) ~= "string" then return nil end
    currencyIcons[item] = icon
    return icon
end

-- The currency's name, with its picture before it when the game has one.
local function CurrencyLabel(item)
    local icon = CurrencyIcon(item)
    local name = CurrencyName(item)
    return icon and (CROPPED_ICON:format(icon) .. " " .. name) or name
end

function Sources.CostText(cost)
    return L.COST_AMOUNT:format(cost.amount, CurrencyLabel(cost.item))
end

function Sources.WithCost(text, cost)
    if not cost then return text end
    local price = Sources.CostText(cost)
    return text ~= "" and (price .. " · " .. text) or price
end

-- A number the game hands out; restricted content may hide it.
local function Count(value)
    if issecretvalue and issecretvalue(value) then return nil end
    return type(value) == "number" and value or nil
end

function Sources.Held(item)
    local held
    local currency = Currency(item)
    if currency and currency.id and C_CurrencyInfo and C_CurrencyInfo.GetCurrencyInfo then
        local ok, info = pcall(C_CurrencyInfo.GetCurrencyInfo, currency.id)
        if ok and type(info) == "table" then held = Count(info.quantity) end
    end
    local GetCount = (C_Item and C_Item.GetItemCount) or GetItemCount
    if GetCount then
        local ok, count = pcall(GetCount, item, true)
        count = ok and Count(count) or nil
        if count and (not held or count > held) then held = count end
    end
    return held
end

function Sources.CostLine(cost)
    local price = Sources.CostText(cost)
    local held = Sources.Held(cost.item)
    if not held then return L.TIP_COST:format(price) end
    if held >= cost.amount then return L.TIP_COST_HAVE:format(price, held) end
    return L.TIP_COST_SHORT:format(price, held, cost.amount - held)
end

-- Whether the player has the item, worn, in the bags or in the bank.
local function Owned(id)
    local IsWorn = (C_Item and C_Item.IsEquippedItem) or IsEquippedItem
    if IsWorn then
        local ok, worn = pcall(IsWorn, id)
        if ok and worn == true then return true end
    end
    local GetCount = (C_Item and C_Item.GetItemCount) or GetItemCount
    if not GetCount then return false end
    local ok, count = pcall(GetCount, id, true)
    count = ok and Count(count) or nil
    return count ~= nil and count > 0
end

Sources.Owned = Owned

function Sources.ToPay(cells)
    local owed, byItem = {}, {}
    for _, cell in ipairs(cells) do
        local cost = cell.id and cell.source and cell.source.cost
        if cost and not Owned(cell.id) then
            local entry = byItem[cost.item]
            if not entry then
                entry = { item = cost.item, amount = 0, held = Sources.Held(cost.item) }
                byItem[cost.item] = entry
                owed[#owed + 1] = entry
            end
            entry.amount = entry.amount + cost.amount
        end
    end
    return owed
end

function Sources.ToPayLine(owed)
    local name = CurrencyLabel(owed.item)
    if not owed.held then return L.CHAR_COST_UNKNOWN:format(name, owed.amount) end
    return L.CHAR_COST:format(name, owed.amount, owed.held)
end
