local _, ns = ...

--[[
Reads the lists (Data\Lists.lua) and turns a slot's ladder into its best
pick(s) and their alternatives, for one faction and the current options.

A ladder is every pick of a slot, best first. What a character sees of it
depends on the filter: the faction, whether items with no known source count,
whether only items seen in Forever count, whether the PvP rewards count in the
list (each list has its own answer), the PvP rank the week's cap allows, the
content phase the list stops at, and how many alternatives a slot lists.

  Ladders.Specs(class)               { { index, name, role, style }, ... }
  Ladders.For(class, spec, list)     { [slot] = { best = {...}, alts = {...}, other = {...} }, twoHand = bool }
      a pick is { id = item for this faction, score = number, entry = its ladder entry }
      other: for the two weapon slots, the weapons of the style that lost (one-handers and their
      off hands when a two-hander is best, two-handers otherwise), offered as alternatives
  Ladders.IsTie(picks, pick)         whether an alternative of a slot scores as much as a best pick

The rules are the generator's (_build/ladders.py: picks, weapon_lists,
other_weapons); the tests check both give the same picks.
]]

local Ladders = {}
ns.Ladders = Ladders

---------------------------------------------------------------------------
-- Decoding
---------------------------------------------------------------------------

-- "id:score*10:flags:twin:limit:rank", the empty fields at the end left out.
local function ParseEntry(text)
    local id, score, flags, twin, limit, rank = text:match("^(%d+):(%d+):?([%a%d]*):?(%d*):?([%a%d]*):?(%d*)$")
    if not id then return nil end
    return {
        id = tonumber(id),
        score10 = tonumber(score),
        flags = flags,
        side = flags:match("^[ah]") or "",
        phase = tonumber(flags:match("%d")) or 0,
        twin = tonumber(twin),
        limit = limit ~= "" and limit or nil,
        rank = tonumber(rank) or 0,
    }
end

-- flags: s seen in Forever, n new in Forever, u no known source, U unique, t two-hander, r random bonus,
-- p a PvP reward, v a Premier piece (sold for honor, even when the data gives it no source); a digit is the
-- content phase the item needs (entry.phase, 0 without one)
function Ladders.HasFlag(entry, letter)
    return entry.flags:find(letter, 1, true) ~= nil
end

-- { specs = { [index] = spec }, lists = { [index] = { [list] = { [slot] = { entries } } } } }, or nil
function Ladders.Decode(class)
    local text = ns.data and ns.data.lists and ns.data.lists[class]
    if not text then return nil end
    local data = { specs = {}, lists = {} }
    for line in text:gmatch("[^\n]+") do
        local kind, index, first, second, rest = line:match("^(%a)\t(%d+)\t([^\t]*)\t([^\t]*)\t?(.*)$")
        index = tonumber(index)
        if kind == "S" then
            data.specs[index] = { index = index, name = first, role = second, style = rest }
        elseif kind == "L" then
            local entries = {}
            for token in rest:gmatch("%S+") do
                entries[#entries + 1] = ParseEntry(token)
            end
            data.lists[index] = data.lists[index] or {}
            data.lists[index][first] = data.lists[index][first] or {}
            data.lists[index][first][second] = entries
        end
    end
    return data
end

---------------------------------------------------------------------------
-- From a ladder to picks
---------------------------------------------------------------------------

-- The item a character of that faction wears for an entry, or nil.
local function Shown(entry, side)
    if entry.side == "" or entry.side == side then return entry.id end
    return entry.twin
end

-- filter.pvpRewards: whether the PvP rewards count, as { pve = bool, pvp = bool } or one answer for both
-- lists; they count when the filter does not say. filter.rankCap: the rank the week's cap allows, nil when
-- the list does not follow it. A list that follows it counts the Premier pieces it allows, source known or not.
local function Visible(entries, filter, list)
    local rewards = filter.pvpRewards
    if type(rewards) == "table" then rewards = rewards[list] end
    local cap = filter.rankCap
    local visible = {}
    for _, entry in ipairs(entries or {}) do
        local id = Shown(entry, filter.side)
        if id
            and entry.phase <= (filter.phase or 9)
            and (not cap or entry.rank <= cap)
            and (filter.unsourced or not Ladders.HasFlag(entry, "u") or (cap and Ladders.HasFlag(entry, "v")))
            and (rewards ~= false or not Ladders.HasFlag(entry, "p"))
            and (not filter.seenOnly or Ladders.HasFlag(entry, "s")) then
            visible[#visible + 1] = { id = id, score = entry.score10 / 10, entry = entry }
        end
    end
    return visible
end

-- Weighs the two weapon slots against each other. When the best two-hander
-- beats the best main hand plus the best off hand, the main hand lists
-- two-handers only and the off hand is empty (third value true). Otherwise the
-- main hand lists one-handers and the off hand leaves out the main hand's pick.
-- The fourth and fifth values are the style that lost, main hand and off hand:
-- the one-handers and the off hands that go with them, or the two-handers.
local function WeaponLists(main, off)
    local two, one = {}, {}
    for _, pick in ipairs(main) do
        local list = Ladders.HasFlag(pick.entry, "t") and two or one
        list[#list + 1] = pick
    end
    local others = {}
    if one[1] then
        for _, pick in ipairs(off) do
            if pick.entry.id ~= one[1].entry.id then others[#others + 1] = pick end
        end
    end
    if two[1] and (not one[1]
        or two[1].entry.score10 >= one[1].entry.score10 + (off[1] and off[1].entry.score10 or 0)) then
        return two, {}, true, one, others
    end
    if not one[1] then return main, off, false, {}, {} end
    return one, others, false, two, {}
end

local function First(picks, count)
    local first = {}
    for index = 1, math.min(count, #picks) do first[index] = picks[index] end
    return first
end

-- best, alternatives. Rings and trinkets have two best picks: the second is the
-- next one that can be worn with the first. That second pick is one of the count
-- asked for: a slot lists the best pick and at most count items after it.
local function Picks(slot, visible, count)
    local best, alts = {}, {}
    local first = visible[1]
    if not first then return best, alts end
    best[1] = first
    if ns.PAIRED[slot] then
        for index = 2, #visible do
            local pick = visible[index]
            if not (first.entry.limit and pick.entry.limit == first.entry.limit) then
                best[2] = pick
                break
            end
        end
    end
    count = count - (#best - 1)
    for _, pick in ipairs(visible) do
        if #alts >= count then break end
        if pick ~= best[1] and pick ~= best[2] then alts[#alts + 1] = pick end
    end
    return best, alts
end

-- The picks of every slot for a spec and a list, from decoded data.
function Ladders.Compute(data, spec, list, filter)
    local ladders = data.lists[spec] and data.lists[spec][list] or {}
    local visible = {}
    for _, slot in ipairs(ns.SLOTS) do
        visible[slot] = Visible(ladders[slot], filter, list)
    end
    local twoHand, otherMain, otherOff
    visible.main, visible.off, twoHand, otherMain, otherOff = WeaponLists(visible.main, visible.off)

    local count = filter.alternatives or ns.ALTERNATIVES
    local result = { twoHand = twoHand }
    for _, slot in ipairs(ns.SLOTS) do
        local best, alts = Picks(slot, visible[slot], count)
        result[slot] = { best = best, alts = alts, other = {} }
    end
    result.main.other = First(otherMain, 1 + count)
    result.off.other = First(otherOff, 1 + count)
    return result
end

-- An alternative that scores exactly as one of the best picks is its equal, not a second choice.
-- picks: a slot of Compute's result.
function Ladders.IsTie(picks, pick)
    for _, best in ipairs(picks.best) do
        if pick.entry.score10 == best.entry.score10 then return true end
    end
    return false
end

---------------------------------------------------------------------------
-- One class at a time (the one being looked at)
---------------------------------------------------------------------------

local current = { class = nil, data = nil, results = {} }

local function Load(class)
    if current.class ~= class then
        current = { class = class, data = Ladders.Decode(class), results = {} }
    end
    return current.data
end

function Ladders.Specs(class)
    local data = Load(class)
    local specs = {}
    for _, spec in pairs(data and data.specs or {}) do specs[#specs + 1] = spec end
    table.sort(specs, function(a, b) return a.index < b.index end)
    return specs
end

function Ladders.For(class, spec, list)
    local data = Load(class)
    if not data then return nil end
    local key = spec .. ":" .. list
    if not current.results[key] then
        current.results[key] = Ladders.Compute(data, spec, list, ns.Filter())
    end
    return current.results[key]
end

ns:On("OPTION_CHANGED", function(key)
    if ns.FILTER_OPTIONS[key] then current.results = {} end
end)
