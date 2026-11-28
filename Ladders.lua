local _, ns = ...

--[[
Reads the lists (Data\Lists.lua) and turns a slot's ladder into its best
pick(s) and their alternatives, for one faction and the current options.

A ladder is every pick of a slot, best first. What a character sees of it
depends on the filter: the faction, whether items with no known source count,
whether only items seen in Forever count, whether the PvP rewards count in the
list (each list has its own answer), the PvP rank the week's cap allows, the
content phase the list stops at, and how many alternatives a slot lists.

  Ladders.Specs(class)               { { index, name, role, style }, ... } in the order the data lists them,
                                     which is the order to show them in: the Druid's Feral (Cat), spec 4,
                                     stands before Feral (Bear), spec 2
  Ladders.For(class, spec, list)     { [slot] = { best = {...}, alts = {...}, other = {...} }, twoHand = bool }
      a pick is { id = item for this faction, score = number, entry = its ladder entry }
      other: for the two weapon slots, the weapons of the style that lost (one-handers and their
      off hands when a two-hander is best, two-handers otherwise), offered as alternatives
  Ladders.IsTie(picks, pick)         whether an alternative of a slot scores as much as a best pick
  Ladders.Lead(picks)                the first pick that can be a best pick (not a placed one, flag e, nor one
                                     whose effect the weights cannot count, flag x)
  Ladders.Unscored(entry)            whether an entry lacks a comparable score (e, x, g, b, c)

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
-- p a PvP reward, v a Premier piece (sold for honor, even when the data gives it no source), e placed from a
-- close spec's simulation; x situational effect beyond the stat weights; g estimated simulation score;
-- b incomplete faction-specific measurement, j situational option outside the alternatives limit, f show that option fourth,
-- k situational only in pre-raid, q its rank depends on a condition or an explicit recommendation.
-- A digit gives the content phase the item needs (entry.phase, 0 without one).
function Ladders.HasFlag(entry, letter)
    return entry.flags:find(letter, 1, true) ~= nil
end

-- { specs = { [index] = spec }, order = { index, ... }, lists = { [index] = { [list] = { [slot] = { entries } } } },
--   measured = { [index] = { [list] = "2026-11-21" } } }, or nil. order: the specs as the data lists them, which is
-- how they are shown. measured: the lists ranked by simulation, with the day they were measured; a list that is
-- not there is ranked on the stat weights.
function Ladders.Decode(class)
    local text = ns.data and ns.data.lists and ns.data.lists[class]
    if not text then return nil end
    local data = { specs = {}, order = {}, lists = {}, measured = {}, contexts = {}, weaponSets = {},
        rangedPairs = {}, tankDuels = {} }
    for line in text:gmatch("[^\n]+") do
        local kind, index, first, second, rest = line:match("^(%a)\t(%d+)\t([^\t]*)\t([^\t]*)\t?(.*)$")
        index = tonumber(index)
        if kind == "S" and index == ns.ActiveSpec(class, index) then
            if not data.specs[index] then data.order[#data.order + 1] = index end
            data.specs[index] = { index = index, name = first, role = second, style = rest }
        elseif kind == "T" and first == "pve" then
            local values = {}
            for value in rest:gmatch("%S+") do values[#values + 1] = tonumber(value) end
            if #values == 8 then
                data.tankDuels[index] = data.tankDuels[index] or {}
                data.tankDuels[index][second] = { threat = values[1], mitigation = values[2],
                    a = { values[3], values[4], values[5] }, h = { values[6], values[7], values[8] } }
            end
        elseif kind == "M" then
            data.measured[index] = data.measured[index] or {}
            data.measured[index][first] = second
        elseif kind == "W" then
            data.weaponSets[index] = data.weaponSets[index] or {}
            data.weaponSets[index][first] = data.weaponSets[index][first] or {}
            data.weaponSets[index][first][second] = true
        elseif kind == "R" then
            local pairs = {}
            for main, ranged in rest:gmatch("(%d+):(%d+)") do
                pairs[#pairs + 1] = { main = tonumber(main), ranged = tonumber(ranged) }
            end
            data.rangedPairs[index] = data.rangedPairs[index] or {}
            data.rangedPairs[index][first] = data.rangedPairs[index][first] or {}
            data.rangedPairs[index][first][second] = pairs
        elseif kind == "L" or kind == "F" then
            local context
            if kind == "F" then context, rest = rest:match("^([^\t]+)\t(.*)$") end
            local entries = {}
            for token in rest:gmatch("%S+") do
                entries[#entries + 1] = ParseEntry(token)
            end
            local target = context and data.contexts or data.lists
            target[index] = target[index] or {}
            target[index][first] = target[index][first] or {}
            if context then
                local slots = target[index][first]
                slots[second] = slots[second] or {}
                slots[second][context] = entries
                if second == "off" and context ~= "situational" then
                    slots[second].hasWeaponContexts = true
                end
            else
                target[index][first][second] = entries
            end
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
local function Visible(entries, filter, list, extras)
    local rewards = filter.pvpRewards
    if type(rewards) == "table" then rewards = rewards[list == "weave" and "pve" or list] end
    local cap = filter.rankCap
    local visible, options, conditional, placed = {}, nil, {}, {}
    if filter.phase == 0 and extras then
        options = Visible(extras, filter, list)
        for _, pick in ipairs(options) do conditional[pick.id] = true end
    end
    for _, entry in ipairs(entries or {}) do
        local id = Shown(entry, filter.side)
        if id
            and entry.phase <= (filter.phase or 9)
            and (not cap or entry.rank <= cap)
            and (filter.unsourced or not Ladders.HasFlag(entry, "u") or (cap and Ladders.HasFlag(entry, "v")))
            and (rewards ~= false or not Ladders.HasFlag(entry, "p"))
            and (not filter.seenOnly or Ladders.HasFlag(entry, "s")) then
            local pick = { id = id, score = entry.score10 / 10, entry = entry }
            if filter.phase == 0 and (conditional[id] or Ladders.HasFlag(entry, "k")) then
                if entry.score10 > 0 and not Ladders.Unscored(entry) and not Ladders.HasFlag(entry, "q") then
                    pick.baseEntry = entry
                end
                pick.entry = setmetatable({ flags = entry.flags .. "xj" }, { __index = entry })
                placed[id] = true
            end
            visible[#visible + 1] = pick
        end
    end
    if options then
        for _, pick in ipairs(options) do
            if not placed[pick.id] then visible[#visible + 1] = pick end
        end
    end
    return visible
end

local function Context(slot, filter, companion)
    if not slot then return nil end
    local key = companion and (filter.side .. ":" .. companion) or filter.side
    if filter.phase == 0 then
        if slot["pre:" .. filter.side] then return slot["pre:" .. key] end
        if not companion and slot.pre then return slot.pre end
    end
    return slot[key]
end

-- Whether an entry's score is a stand-in that keeps the ladder in order, not its own: placed from a close spec's
-- simulation (e), a situational effect (x), an incomplete simulation score (g or b), or an unscored recommendation (c).
function Ladders.Unscored(entry)
    return entry.flags:find("[exgbc]") ~= nil
end

local function CanBeBest(pick)
    return pick.baseEntry ~= nil or not Ladders.Unscored(pick.entry)
end

-- The first pick that can be a best pick: one with no score of its own never is, unless the list has nothing else.
function Ladders.Lead(picks)
    local first
    for _, pick in ipairs(picks) do
        if CanBeBest(pick) then return pick end
        if not first and not Ladders.HasFlag(pick.entry, "j") then first = pick end
    end
    if first and not first.entry.flags:find("[gb]") then return first end
end

-- Weighs the two weapon slots against each other. When the best two-hander
-- beats the best main hand plus the best off hand, the main hand lists
-- two-handers only and the off hand is empty (third value true). Otherwise the
-- main hand lists one-handers and the off hand leaves out the main hand's pick.
-- The fourth and fifth values are the style that lost, main hand and off hand:
-- the one-handers and the off hands that go with them, or the two-handers.
local function WeaponLists(main, off, side, measuredSets)
    local two, one = {}, {}
    for _, pick in ipairs(main) do
        local list = Ladders.HasFlag(pick.entry, "t") and two or one
        list[#list + 1] = pick
    end
    local twoBest, oneBest = Ladders.Lead(two), Ladders.Lead(one)
    local others = {}
    if oneBest then
        for _, pick in ipairs(off) do
            if pick.entry.id ~= oneBest.entry.id then others[#others + 1] = pick end
        end
    end
    local offBest = Ladders.Lead(others)
    local measured = measuredSets and twoBest and oneBest and offBest
        and measuredSets[side .. ":" .. twoBest.id .. ":" .. oneBest.id .. ":" .. offBest.id]
    if twoBest and (not oneBest or measured
        or twoBest.entry.score10 >= oneBest.entry.score10 + (offBest and offBest.entry.score10 or 0)) then
        return two, {}, true, one, others, measured
    end
    if not oneBest then return main, off, false, {}, {} end
    return one, others, false, two, {}
end

local function First(picks, count)
    local first = {}
    for _, pick in ipairs(picks) do
        if Ladders.HasFlag(pick.entry, "j") then
            first[#first + 1] = pick
        elseif count > 0 then
            first[#first + 1] = pick
            count = count - 1
        end
    end
    return first
end

-- Keep each weapon at its first appearance in the ranked pairs that pass the filters.
local function RangedPairs(visible, pairs)
    local melee, ranged = {}, {}
    for _, pick in ipairs(visible.main) do melee[pick.id] = pick end
    for _, pick in ipairs(visible.ranged) do ranged[pick.id] = pick end
    visible.main, visible.ranged = {}, {}
    local seen = {}
    local function Add(slot, pick)
        if seen[pick.id] then return end
        seen[pick.id] = true
        local picks = visible[slot]
        picks[#picks + 1] = pick
    end
    for _, pair in ipairs(pairs or {}) do
        local main, shot = melee[pair.main], ranged[pair.ranged]
        if main and shot then
            Add("main", main)
            Add("ranged", shot)
        end
    end
end

-- best, alternatives. Rings and trinkets have two best picks: the second is the
-- next one that can be worn with the first. That second pick is one of the count
-- asked for: a slot lists the best pick and at most count items after it. A placed
-- item (flag e) is never a best pick.
local function Picks(slot, visible, count, recommendations)
    local best, alts = {}, {}
    local first = Ladders.Lead(visible)
    best[1] = first
    if first and ns.PAIRED[slot] then
        for _, pick in ipairs(visible) do
            if pick ~= first and (CanBeBest(pick) or recommendations and Ladders.HasFlag(pick.entry, "c"))
                and not (first.entry.limit and pick.entry.limit == first.entry.limit) then
                best[2] = pick
                break
            end
        end
    end
    for _, pick in ipairs(best) do pick.entry = pick.baseEntry or pick.entry end
    count = count - math.max(0, #best - 1)
    local fourth
    for position, pick in ipairs(visible) do
        pick.position = position
        if Ladders.HasFlag(pick.entry, "f") then
            fourth = pick
        elseif Ladders.HasFlag(pick.entry, "j") then
            alts[#alts + 1] = pick
        elseif count > 0 and pick ~= best[1] and pick ~= best[2] then
            alts[#alts + 1] = pick
            count = count - 1
        end
    end
    if fourth then table.insert(alts, math.min(#alts + 1, 4 - #best), fourth) end
    return best, alts
end

-- Only describe a duel when both actual item IDs survive the filters and weapon style.
local function TankOptions(picks, visible, duel, side)
    local threat, mitigation
    for _, pick in ipairs(visible) do
        if pick.id == duel.threat then threat = pick end
        if pick.id == duel.mitigation then mitigation = pick end
    end
    if not threat or not mitigation or not duel[side] then return end
    threat.option = { label = ns.L.RANK_THREAT, rival = mitigation.id, delta = duel[side], sign = 1 }
    mitigation.option = { label = ns.L.RANK_MITIGATION, rival = threat.id, delta = duel[side], sign = -1 }
    if threat.entry.limit and threat.entry.limit == mitigation.entry.limit then
        threat.option.exclusive, mitigation.option.exclusive = true, true
    end
    picks.options = {}
    for _, pick in ipairs({ threat, mitigation }) do
        if pick ~= picks.best[1] and pick ~= picks.best[2] then
            picks.options[#picks.options + 1] = pick
        end
    end
end

-- A measured option outside the ordinary best picks stays visible at any alternative count.
-- Keep the scored ladders intact for gear sets, ties and comparisons against the first pick.
local EMPTY = {}
function Ladders.DisplayAlts(picks, withAlts)
    if not picks.options then return withAlts and picks.alts or EMPTY end
    if not withAlts then return picks.options end
    local out = {}
    for _, pick in ipairs(picks.options) do out[#out + 1] = pick end
    for _, pick in ipairs(picks.alts) do
        if not pick.option then
            -- The bear's situational trinket keeps its fourth slot when a duel adds an alternative.
            local position = #out + 1
            if Ladders.HasFlag(pick.entry, "f") then position = math.min(position, 4 - #picks.best) end
            table.insert(out, position, pick)
        end
    end
    return out
end

-- Preserve the order of the ordinary picks, inserting situational picks at their
-- positions among the displayed rows, even when this places them above a BiS pick.
function Ladders.DisplayPicks(picks, withAlts)
    local ordinary, situational, fourth = {}, {}, nil
    for _, pick in ipairs(picks.best) do ordinary[#ordinary + 1] = pick end
    for _, pick in ipairs(Ladders.DisplayAlts(picks, withAlts)) do
        if Ladders.HasFlag(pick.entry, "f") then
            fourth = pick
        elseif Ladders.HasFlag(pick.entry, "j") then
            situational[#situational + 1] = pick
        else
            ordinary[#ordinary + 1] = pick
        end
    end
    local displayed = {}
    for _, pick in ipairs(ordinary) do displayed[#displayed + 1] = pick end
    for index, pick in ipairs(situational) do
        local position = index
        for _, other in ipairs(ordinary) do
            if other.position < pick.position then position = position + 1 end
        end
        table.insert(displayed, position, pick)
    end
    if fourth then table.insert(displayed, math.min(#displayed + 1, 4), fourth) end
    return displayed
end

function Ladders.OptionNote(option)
    local delta, sign = option.delta, option.sign
    local function Signed(value)
        local text = ("%+.1f"):format(sign * value)
        if ns.locale == "frFR" then text = text:gsub("%.", ",") end
        return text
    end
    local note = ns.L.TANK_DUEL:format(ns.Items.Name(option.rival),
        Signed(delta[2]), Signed(delta[3]), Signed(delta[1]))
    return option.exclusive and (note .. " " .. ns.L.TANK_EXCLUSIVE) or note
end

-- The picks of every slot for a spec and a list, from decoded data.
function Ladders.Compute(data, spec, list, filter)
    local ladders = data.lists[spec] and data.lists[spec][list] or {}
    local specContexts = data.contexts and data.contexts[spec]
    local contexts = specContexts and specContexts[list] or {}
    local visible = {}
    for _, slot in ipairs(ns.SLOTS) do
        local context = contexts[slot]
        local entries = Context(context, filter)
        -- A contextual off-hand needs a matching main hand. The base rows use a different reference.
        if not entries and not (context and context.hasWeaponContexts) then entries = ladders[slot] end
        local extras = context and context.situational
        visible[slot] = Visible(entries, filter, list, extras)
        if context and ns.PAIRED[slot] then
            local first = Ladders.Lead(visible[slot])
            local paired = first and Context(context, filter, first.id)
            if paired then
                local companions = Visible(paired, filter, list, extras)
                for _, pick in ipairs(companions) do pick.pairedWith = first.id end
                table.insert(companions, 1, first)
                visible[slot] = companions
            end
        end
    end
    local offSets = contexts.off
    if offSets and offSets.hasWeaponContexts then
        -- An off-hand gain depends on the hit and stats of this actual main hand.
        local one = {}
        for _, pick in ipairs(visible.main) do
            if not Ladders.HasFlag(pick.entry, "t") then one[#one + 1] = pick end
        end
        local first = Ladders.Lead(one)
        if first then
            local selected = Context(offSets, filter, first.id) or Context(offSets, filter)
            if selected then visible.off = Visible(selected, filter, list, offSets.situational) end
        end
    end
    local rangedSets = data.rangedPairs and data.rangedPairs[spec]
    local pairsBySide = rangedSets and rangedSets[list]
    if pairsBySide then RangedPairs(visible, pairsBySide[filter.side]) end
    local twoHand, otherMain, otherOff, measuredWeaponSet
    local measuredSets = filter.phase == 0 and data.weaponSets and data.weaponSets[spec]
    visible.main, visible.off, twoHand, otherMain, otherOff, measuredWeaponSet =
        WeaponLists(visible.main, visible.off, filter.side, measuredSets and measuredSets[list])

    local count = filter.alternatives or ns.ALTERNATIVES
    local result = { twoHand = twoHand, measuredWeaponSet = measuredWeaponSet }
    local duels = list == "pve" and filter.phase == 0 and data.tankDuels and data.tankDuels[spec]
    for _, slot in ipairs(ns.SLOTS) do
        local best, alts = Picks(slot, visible[slot], count, pairsBySide ~= nil)
        result[slot] = { best = best, alts = alts, other = {} }
        if duels and duels[slot] then TankOptions(result[slot], visible[slot], duels[slot], filter.side) end
    end
    result.main.other = First(otherMain, 1 + count)
    result.off.other = First(otherOff, 1 + count)
    if offSets and offSets.hasWeaponContexts and twoHand then
        for _, pick in ipairs(result.main.other) do
            local context = Context(offSets, filter, pick.id) or Context(offSets, filter)
            pick.partialSet = context == nil
            if context then pick.partner = Ladders.Lead(Visible(context, filter, list)) end
        end
    end
    return result
end

-- An alternative that scores exactly as one of the best picks is its equal, not a second choice.
-- picks: a slot of Compute's result. A placed item has no score of its own: it is nobody's equal. One whose effect
-- the weights cannot count (flag x) has no measured score either.
local function HasComparableScore(entry)
    return not Ladders.Unscored(entry) and not Ladders.HasFlag(entry, "g")
end

function Ladders.IsTie(picks, pick)
    if not HasComparableScore(pick.entry) then return false end
    for _, best in ipairs(picks.best) do
        if pick.pairedWith == best.pairedWith and HasComparableScore(best.entry)
            and pick.entry.score10 == best.entry.score10 then return true end
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
    for _, index in ipairs(data and data.order or {}) do specs[#specs + 1] = data.specs[index] end
    return specs
end

-- The day the simulator measured that list ("2026-11-21"), nil for a list ranked on the stat weights.
function Ladders.Measured(class, spec, list)
    local data = Load(class)
    local lists = data and data.measured[spec]
    return lists and lists[list] or nil
end

function Ladders.HasList(class, spec, list)
    local data = Load(class)
    local modes = data and data.lists[spec]
    return modes ~= nil and modes[list] ~= nil
end

function Ladders.For(class, spec, list)
    local data = Load(class)
    if not data then return nil end
    local filter = ns.Filter()
    if current.rankCap ~= filter.rankCap then
        current.rankCap, current.results = filter.rankCap, {}
    end
    local key = spec .. ":" .. list
    if not current.results[key] then
        current.results[key] = Ladders.Compute(data, spec, list, filter)
    end
    return current.results[key]
end

ns:On("OPTION_CHANGED", function(key)
    if ns.FILTER_OPTIONS[key] then current.results = {} end
end)
