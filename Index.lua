local _, ns = ...

--[[
Which specs want an item: what item tooltips need.

  Index.ForItem(id)   { { class, spec, list, slot, bis = true|false, custom = true|nil }, ... } or nil
                      bis: a best pick, or an alternative that scores as much as one
                      custom: added to that list by hand (Custom.lua), not a pick of the data
  Index.SpecName(class, spec), Index.SpecCount(class)

Built once, class by class, from the lists as the player's faction and the
options show them. The first classes are read a few seconds after login, one
per frame; a tooltip that comes earlier reads what is left at once. Only the
result is kept: the decoded lists are dropped.
]]

local Index = {}
ns.Index = Index

local WARM_UP_DELAY = 3   -- seconds after login before the first class is read

local byItem = {}     -- [item id] = hits
local specNames = {}  -- [class] = { [spec] = English name }
local done = {}       -- [class] = true once read
local generation = 0  -- bumped by Reset, so a warm-up in progress stops
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
    for spec, def in pairs(data.specs) do
        specNames[class][spec] = def.name
        for _, list in ipairs(ns.LISTS) do
            local slots = ns.Ladders.Compute(data, spec, list, filter)
            for _, slot in ipairs(ns.SLOTS) do
                local picks = slots[slot]
                for _, pick in ipairs(picks.best) do
                    Add(byItem, pick.id, { class = class, spec = spec, list = list, slot = slot, bis = true })
                end
                for _, pick in ipairs(picks.alts) do
                    Add(byItem, pick.id, { class = class, spec = spec, list = list, slot = slot,
                        bis = ns.Ladders.IsTie(picks, pick) })
                end
                -- the weapons of the other style (a one-hander when a two-hander is best) are alternatives too
                for _, pick in ipairs(picks.other) do
                    Add(byItem, pick.id, { class = class, spec = spec, list = list, slot = slot, bis = false })
                end
            end
        end
    end
end

local function ReadAll()
    local filter = ns.Filter()
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

function Index.Reset()
    byItem, specNames, done, added = {}, {}, {}, nil
    generation = generation + 1
end

-- Reads one class per frame, so the first tooltip does not pay for all nine.
function Index.WarmUp()
    if not (C_Timer and C_Timer.After) then return end
    local started = generation
    local position = 0
    local function Step()
        if started ~= generation then return end
        position = position + 1
        local class = ns.CLASSES[position]
        if not class then return end
        ReadClass(class, ns.Filter())
        C_Timer.After(0, Step)
    end
    C_Timer.After(WARM_UP_DELAY, Step)
end

ns:On("OPTION_CHANGED", function(key)
    if key == "unsourced" or key == "seenOnly" or key == "phase" then
        Index.Reset()
        Index.WarmUp()
    end
end)

ns:On("CUSTOM_CHANGED", function() added = nil end)

ns:On("LOGIN", Index.WarmUp)
