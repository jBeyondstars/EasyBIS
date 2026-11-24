local _, ns = ...
local L = ns.L

--[[
Items the player adds to a list by hand: a piece the data does not have, or a
choice of their own.

They are kept for every character (EasyBISDB.custom), per class, spec and list:
    custom["HUNTER:2:pve"] = { head = { 12345, ... }, ... }
The slot is the one the game gives the item. A one-handed weapon goes to the
main hand, or to the off hand when that is asked for. A hand-added item has no
score: the window lists it after its slot's picks, and its tooltip names the
spec it was added for.

  Custom.Read(text)                               the item id in an ID, a link or a name the game knows; or nil
  Custom.SlotOf(id, preferred)                    the slot the item goes in; nil when it is not worn, and
                                                  nil, true when the game has no such item
  Custom.Add(class, spec, list, id, preferred)    the slot, or nil and why not: "unknown", "notGear",
                                                  "duplicate" (already added) or "listed" (the data has it)
  Custom.Remove(class, spec, list, id)            true when it was there
  Custom.List(class, spec, list, slot)            ids, in the order they were added
  Custom.Each(callback)                           callback(class, spec, list, slot, id) for every added item
  Custom.ListText(class, spec, list)              "Hunter Marksmanship, PvE"
  Custom.Submit(class, spec, list, text, preferred)   Read + Add: ok, the sentence that says what happened
  Custom.Withdraw(class, spec, list, text)            Read + Remove: ok, sentence

CUSTOM_CHANGED is fired after a change.
]]

local Custom = {}
ns.Custom = Custom

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetInstant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant

-- The game's equip slot -> the slots of Easy BIS it can go in, the usual one first.
local SLOTS_OF = {
    INVTYPE_HEAD = { "head" }, INVTYPE_NECK = { "neck" }, INVTYPE_SHOULDER = { "shoulder" },
    INVTYPE_CLOAK = { "back" }, INVTYPE_CHEST = { "chest" }, INVTYPE_ROBE = { "chest" },
    INVTYPE_WRIST = { "wrist" }, INVTYPE_HAND = { "hands" }, INVTYPE_WAIST = { "waist" },
    INVTYPE_LEGS = { "legs" }, INVTYPE_FEET = { "feet" }, INVTYPE_FINGER = { "finger" },
    INVTYPE_TRINKET = { "trinket" },
    INVTYPE_WEAPON = { "main", "off" }, INVTYPE_2HWEAPON = { "main" }, INVTYPE_WEAPONMAINHAND = { "main" },
    INVTYPE_WEAPONOFFHAND = { "off" }, INVTYPE_SHIELD = { "off" }, INVTYPE_HOLDABLE = { "off" },
    INVTYPE_RANGED = { "ranged" }, INVTYPE_RANGEDRIGHT = { "ranged" }, INVTYPE_THROWN = { "ranged" },
    INVTYPE_RELIC = { "ranged" },
}

local function Key(class, spec, list)
    return class .. ":" .. spec .. ":" .. list
end

-- The ids added for a class, spec, list and slot; the table is made when asked for.
local function Ids(class, spec, list, slot, create)
    local custom = ns.db.custom
    local key = Key(class, spec, list)
    local perSlot = custom[key]
    if type(perSlot) ~= "table" then
        if not create then return nil end
        perSlot = {}
        custom[key] = perSlot
    end
    local ids = perSlot[slot]
    if type(ids) ~= "table" then
        if not create then return nil end
        ids = {}
        perSlot[slot] = ids
    end
    return ids
end

function Custom.GearList(class, spec, key)
    local index = type(key) == "string" and key:match("^gear(%d+)$")
    if not index then return end
    local id = tonumber(index)
    for i, gear in ipairs(ns.db.gearLists) do
        if gear.id == id and gear.class == class and gear.spec == spec then return gear, i end
    end
end

local function ListName(class, spec, name, current)
    name = name:match("^%s*(.-)%s*$")
    if name == "" or #name > 80 or name:find("[|%c]") then return nil, L.GEAR_BAD_NAME end
    for _, gear in ipairs(ns.db.gearLists) do
        if gear ~= current and gear.class == class and gear.spec == spec and gear.name:lower() == name:lower() then
            return nil, L.GEAR_DUP_NAME
        end
    end
    return name
end

function Custom.CreateList(class, spec, name)
    local valid, message = ListName(class, spec, name)
    if not valid then return nil, message end
    local id = ns.db.lastGearId + 1
    ns.db.lastGearId = id
    table.insert(ns.db.gearLists, { id = id, class = class, spec = spec, name = valid, slots = {} })
    return "gear" .. id
end

function Custom.RenameList(class, spec, key, name)
    local gear = Custom.GearList(class, spec, key)
    if not gear then return false end
    local valid, message = ListName(class, spec, name, gear)
    if not valid then return false, message end
    gear.name = valid
    ns:Fire("CUSTOM_CHANGED")
    return true
end

function Custom.DeleteList(class, spec, key)
    local gear, index = Custom.GearList(class, spec, key)
    if not gear then return false end
    table.remove(ns.db.gearLists, index)
    ns.db.lists[key] = nil
    if ns.char.gearList == key then ns.char.gearList = nil end
    ns:Fire("CUSTOM_CHANGED")
    return true
end

function Custom.Neighbor(class, spec, key, step)
    local _, index = Custom.GearList(class, spec, key)
    if not index or (step ~= 1 and step ~= -1) then return end
    local lists = ns.db.gearLists
    for i = index + step, step == 1 and #lists or 1, step do
        if lists[i].class == class and lists[i].spec == spec then return i, index end
    end
end

function Custom.MoveListTo(class, spec, key, target)
    local gear, index = Custom.GearList(class, spec, key)
    local _, destination = Custom.GearList(class, spec, target)
    if not index or not destination or index == destination then return false end
    local step = destination > index and 1 or -1
    local lists = ns.db.gearLists
    for i = index + step, destination, step do
        if lists[i].class == class and lists[i].spec == spec then
            lists[index] = lists[i]
            index = i
        end
    end
    lists[destination] = gear
    ns:Fire("CUSTOM_CHANGED")
    return true
end

function Custom.MoveList(class, spec, key, step)
    local neighbor = Custom.Neighbor(class, spec, key, step)
    if not neighbor then return false end
    return Custom.MoveListTo(class, spec, key, "gear" .. ns.db.gearLists[neighbor].id)
end

local SIM_SLOTS = { "head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist",
    "legs", "feet", "finger", "finger", "trinket", "trinket", "main", "off", "ranged" }

local function ValidNumber(value)
    return type(value) == "number" and value >= 0 and value <= 2147483647 and value == math.floor(value)
end

function Custom.Import(class, spec, key, text)
    local gear = Custom.GearList(class, spec, key)
    if not gear then return nil, L.GEAR_BAD_IMPORT end
    local ok, root = pcall(ns.Json.decode, text)
    local player = ok and type(root) == "table" and root.player
    local equipment = type(player) == "table" and player.equipment
    local items = type(equipment) == "table" and equipment.items
    if getmetatable(items) ~= ns.Json.array or #items > #SIM_SLOTS then return nil, L.GEAR_BAD_IMPORT end
    local slots, count = {}, 0
    for i, item in ipairs(items) do
        if type(item) ~= "table" or getmetatable(item) or item == ns.Json.null
            or (item.id ~= nil and not ValidNumber(item.id))
            or (item.enchant ~= nil and not ValidNumber(item.enchant))
            or (not item.id and next(item) ~= nil) then return nil, L.GEAR_BAD_IMPORT end
        if item.id and item.id > 0 then
            local slot = SIM_SLOTS[i]
            slots[slot] = slots[slot] or {}
            table.insert(slots[slot], { id = item.id, enchant = item.enchant })
            count = count + 1
        end
    end
    if count == 0 then return nil, L.GEAR_NO_ITEMS end
    gear.slots = slots
    ns:Fire("CUSTOM_CHANGED")
    return count
end

function Custom.Read(text)
    if type(text) ~= "string" then return nil end
    local id = text:match("item:(%d+)") or text:match("^%s*(%d+)%s*$")
    if id then return tonumber(id) end
    local name = text:match("^%s*(.-)%s*$")
    if name == "" or not GetInfo then return nil end
    local _, link = GetInfo(name)   -- by name: only an item the game has already met
    id = link and link:match("item:(%d+)")
    return id and tonumber(id) or nil
end

function Custom.SlotOf(id, preferred)
    if not GetInstant then return nil, true end
    local known, _, _, equipLoc = GetInstant(id)
    if not known then return nil, true end
    local slots = SLOTS_OF[equipLoc or ""]
    if not slots then return nil end
    for _, slot in ipairs(slots) do
        if slot == preferred then return slot end
    end
    return slots[1]
end

function Custom.List(class, spec, list, slot)
    local gear = Custom.GearList(class, spec, list)
    if gear then
        local ids = {}
        for i, entry in ipairs(gear.slots[slot] or {}) do ids[i] = entry.id end
        return ids
    end
    return Ids(class, spec, list, slot) or {}
end

-- Whether the data already lists the item in that slot, as the lists stand now.
local function Listed(class, spec, list, slot, id)
    local slots = ns.Ladders.For(class, spec, list)
    local picks = slots and slots[slot]
    if not picks then return false end
    for _, group in ipairs({ picks.best, ns.Ladders.DisplayAlts(picks, true), picks.other }) do
        for _, pick in ipairs(group) do
            if pick.id == id then return true end
        end
    end
    return false
end

function Custom.Add(class, spec, list, id, preferred)
    local slot, unknown = Custom.SlotOf(id, preferred)
    if not slot then return nil, unknown and "unknown" or "notGear" end
    local gear = Custom.GearList(class, spec, list)
    if gear then
        local entries = gear.slots[slot] or {}
        for _, entry in ipairs(entries) do
            if entry.id == id then return nil, "duplicate" end
        end
        entries[#entries + 1] = { id = id }
        gear.slots[slot] = entries
        ns:Fire("CUSTOM_CHANGED")
        return slot
    end
    for _, known in ipairs(Custom.List(class, spec, list, slot)) do
        if known == id then return nil, "duplicate" end
    end
    if Listed(class, spec, list, slot, id) then return nil, "listed" end
    local ids = Ids(class, spec, list, slot, true)
    ids[#ids + 1] = id
    ns:Fire("CUSTOM_CHANGED")
    return slot
end

function Custom.Remove(class, spec, list, id, slot, index)
    local gear = Custom.GearList(class, spec, list)
    if gear then
        if not slot then
            for _, candidate in ipairs(ns.SLOTS) do
                for i, entry in ipairs(gear.slots[candidate] or {}) do
                    if entry.id == id then return Custom.Remove(class, spec, list, id, candidate, i) end
                end
            end
            return false
        end
        local entries = gear.slots[slot]
        if not entries or not entries[index] or entries[index].id ~= id then return false end
        table.remove(entries, index)
        if #entries == 0 then gear.slots[slot] = nil end
        ns:Fire("CUSTOM_CHANGED")
        return true
    end
    local perSlot = ns.db.custom[Key(class, spec, list)]
    if type(perSlot) ~= "table" then return false end
    local removed = false
    for _, ids in pairs(perSlot) do
        if type(ids) == "table" then
            for index = #ids, 1, -1 do
                if ids[index] == id then
                    table.remove(ids, index)
                    removed = true
                end
            end
        end
    end
    if removed then ns:Fire("CUSTOM_CHANGED") end
    return removed
end

function Custom.Each(callback)
    for key, perSlot in pairs(ns.db.custom) do
        local class, spec, list = tostring(key):match("^(%u+):(%d+):(%a+)$")
        if class and type(perSlot) == "table" then
            for slot, ids in pairs(perSlot) do
                if type(ids) == "table" then
                    for _, id in ipairs(ids) do
                        if type(id) == "number" then callback(class, tonumber(spec), list, slot, id) end
                    end
                end
            end
        end
    end
end

---------------------------------------------------------------------------
-- In words, for the dialog and the commands
---------------------------------------------------------------------------

function Custom.ListText(class, spec, list)
    local gear = Custom.GearList(class, spec, list)
    return ("%s %s, %s"):format(ns.ClassName(class), ns.SpecName(ns.Index.SpecName(class, spec) or ""),
        gear and gear.name or ns.ListName(list))
end

function Custom.Submit(class, spec, list, text, preferred)
    local id = Custom.Read(text)
    if not id then return false, L.ADD_NOT_FOUND end
    local slot, why = Custom.Add(class, spec, list, id, preferred)
    if slot then
        return true, L.ADD_DONE:format(ns.Items.Link(id), Custom.ListText(class, spec, list), ns.SlotName(slot))
    end
    if why == "unknown" then return false, L.ADD_NOT_FOUND end
    if why == "notGear" then return false, L.ADD_NOT_GEAR:format(ns.Items.Link(id)) end
    return false, L.ADD_ALREADY:format(ns.Items.Link(id))
end

function Custom.Withdraw(class, spec, list, text)
    local id = Custom.Read(text)
    if not id then return false, L.ADD_NOT_FOUND end
    if Custom.Remove(class, spec, list, id) then
        return true, L.REMOVE_DONE:format(ns.Items.Link(id), Custom.ListText(class, spec, list))
    end
    return false, L.REMOVE_NOT_THERE:format(ns.Items.Link(id), Custom.ListText(class, spec, list))
end
