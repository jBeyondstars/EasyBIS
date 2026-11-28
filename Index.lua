local _, ns = ...

--[[
Which specs want an item: what item tooltips need.

  Index.ForItem(id)   { { class, spec, list, slot, bis, position, beyondAltLimit, custom }, ... } or nil
                      bis: a best pick, or an alternative that scores as much as one
                      position: row in the slot's ranking, including best picks
                      beyondAltLimit: the window can show extra rows past the tooltip's limit
                      custom: added to that list by hand (Custom.lua), not a pick of the data
  Index.AoeForItem(id)   AoE picks indexed for the active faction and alternative limit
  Index.SpecName(class, spec), Index.SpecCount(class)
  Index.SpecOrder(class)   the class's spec numbers in the order to show them (the data's)

Built once, class by class, from the lists as the player's faction and the
options show them. The first classes are read a few seconds after login, one
per frame; a tooltip that comes earlier reads what is left at once. Only the
result is kept: the decoded lists are dropped.
]]

local Index = {}
ns.Index = Index

local WARM_UP_DELAY = 3   -- seconds after login before the first class is read

local byItem = {}     -- [item id] = hits
local aoeByItem = {}     -- AoE tooltip memberships are separate from Raid and PvP lookups
local specNames = {}  -- [class] = { [spec] = English name }
local specOrder = {}  -- [class] = { spec, ... } as the data lists them
local done = {}       -- [class] = true once read
local generation = 0  -- bumped by Reset, so a warm-up in progress stops
local indexedRankCap  -- the weekly cap used to build the current index
local added           -- [item id] = hits for the items added by hand; nil until asked for, and after a change

local function Add(into, id, hit)
    local hits = into[id]
    if not hits then
        hits = {}
        into[id] = hits
    end
    hits[#hits + 1] = hit
end

local function ReadClass(class, filter)
    if done[class] then return end
    done[class] = true
    local data = ns.Ladders.Decode(class)
    if not data then return end
    specNames[class] = {}
    specOrder[class] = data.order
    for spec, def in pairs(data.specs) do
        specNames[class][spec] = def.name
        for slot, samples in pairs(ns.Rows.AoeList(class, spec) or {}) do
            for rank, sample in ns.Rows.AoePicks(samples, true) do
                Add(aoeByItem, sample[1], { class = class, spec = spec, slot = slot, bis = rank == 1, position = rank })
            end
        end
        local modes = data.lists[spec]
        local lists = modes and modes.weave and { "pve", "pvp", "weave" } or ns.LISTS
        for _, list in ipairs(lists) do
            local slots = ns.Ladders.Compute(data, spec, list, filter)
            for _, slot in ipairs(ns.SLOTS) do
                local picks = slots[slot]
                local displayed = ns.Ladders.DisplayPicks(picks, true)
                local lastAltPosition = filter.alternatives + (picks.best[1] and 1 or 0)
                for position, pick in ipairs(displayed) do
                    local best = pick == picks.best[1] or pick == picks.best[2]
                    Add(byItem, pick.id, { class = class, spec = spec, list = list, slot = slot, position = position,
                        beyondAltLimit = position > lastAltPosition or nil,
                        bis = best or ns.Ladders.IsTie(picks, pick), option = pick.option,
                        recommended = best and list ~= "weave" and ns.Ladders.HasFlag(pick.entry, "c") or nil })
                end
                -- the weapons of the other style (a one-hander when a two-hander is best) are alternatives too
                for index, pick in ipairs(picks.other) do
                    local position = #displayed + index
                    Add(byItem, pick.id, { class = class, spec = spec, list = list, slot = slot,
                        bis = false, position = position, beyondAltLimit = position > lastAltPosition or nil })
                end
            end
        end
    end
end

local function CurrentFilter()
    local filter = ns.Filter()
    if indexedRankCap ~= filter.rankCap then
        Index.Reset()
        indexedRankCap = filter.rankCap
    end
    return filter
end

local function ReadAll()
    local filter = CurrentFilter()
    for _, class in ipairs(ns.CLASSES) do ReadClass(class, filter) end
end

-- The items added by hand, for the specs the data knows.
local function Added()
    if added then return added end
    added = {}
    ns.Custom.Each(function(class, spec, list, slot, id)
        if specNames[class] and specNames[class][spec] then
            Add(added, id, { class = class, spec = spec, list = list, slot = slot, bis = false, custom = true })
        end
    end)
    for _, gear in ipairs(ns.db.gearLists) do
        if specNames[gear.class] and specNames[gear.class][gear.spec] then
            local seen = {}
            for slot, entries in pairs(gear.slots) do
                for _, entry in ipairs(entries) do
                    if not seen[entry.id] then
                        seen[entry.id] = true
                        Add(added, entry.id, { class = gear.class, spec = gear.spec, list = "gear" .. gear.id,
                            slot = slot, custom = true, listName = gear.name })
                    end
                end
            end
        end
    end
    return added
end

function Index.ForItem(id)
    ReadAll()
    local hits, extra = byItem[id], Added()[id]
    if not extra then return hits end
    if not hits then return extra end
    local all = {}
    for _, hit in ipairs(hits) do all[#all + 1] = hit end
    for _, hit in ipairs(extra) do all[#all + 1] = hit end
    return all
end

function Index.AoeForItem(id)
    ReadAll()
    return aoeByItem[id]
end

function Index.SpecName(class, spec)
    ReadAll()
    return specNames[class] and specNames[class][spec]
end

function Index.SpecCount(class)
    ReadAll()
    local count = 0
    for _ in pairs(specNames[class] or {}) do count = count + 1 end
    return count
end

-- The class's spec numbers in the order to show them: the data's, which puts the Druid's two Feral specs together.
function Index.SpecOrder(class)
    ReadAll()
    return specOrder[class] or {}
end

function Index.Reset()
    byItem, specNames, specOrder, done, added = {}, {}, {}, {}, nil
    aoeByItem = {}
    generation = generation + 1
end

-- Reads one class per frame, so the first tooltip does not pay for all nine.
function Index.WarmUp()
    if not (C_Timer and C_Timer.After) then return end
    local filter = CurrentFilter()
    local started = generation
    local position = 0
    local function Step()
        if started ~= generation then return end
        position = position + 1
        local class = ns.CLASSES[position]
        if not class then return end
        ReadClass(class, filter)
        C_Timer.After(0, Step)
    end
    C_Timer.After(WARM_UP_DELAY, Step)
end

ns:On("OPTION_CHANGED", function(key)
    if ns.FILTER_OPTIONS[key] then
        Index.Reset()
        Index.WarmUp()
    end
end)

ns:On("CUSTOM_CHANGED", function() added = nil end)

ns:On("LOGIN", Index.WarmUp)
