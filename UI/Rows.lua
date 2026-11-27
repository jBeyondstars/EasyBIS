local _, ns = ...
local L = ns.L

--[[
What the window lists, as plain tables: the frames only draw them.

  Rows.Items(state, withAlts)      rows, facets. Omit withAlts to follow the browser option.
      state    { class, spec, list, slot, source, zone, reputation }   slot, source, zone and reputation are nil
               for "all"; reputation "ok": what is within the player's reach, "todo": what is still to earn
      a row    { kind = "item", id, slot, bis, tie, gap, ratio, source, other, custom, reputation, why }
                   reputation   what the item asks for (Reputation.Requirement), or nil
                   gap      percent behind the best (0 or less); nil for an item added by hand
                   ratio    its score as a share of the best's (0 to 1), for the score bar; nil likewise
                   tie      true for an alternative that scores exactly as a best pick
                   other    true for a weapon of the style that is not the best one (see below)
                   custom   true for an item the player added by hand (Custom.lua): no score
                   estimated  true for an alternative whose score is no full measure (flag g): it keeps its
                            place, and has no gap and no ratio, so the window shows nothing for its score
                   level    true for an item whose effect the weights cannot count (flag x): no score of its
                            own, so it has no gap, ratio or measured tie
                   placed   true for an item the data placed from a close spec's simulation (flag e): no
                            score of its own, so no gap and no ratio either
               { kind = "note", slot, text }   a line of plain text between rows
      facets   { sources = { [category] = true }, zones = { [name] = true } }: what the Source and
               Zone filters can offer for this spec, list and slot
  Rows.Enchants(state)   rows
      a row    { kind = "enchant", key, bis, enchant, reputation }
  Rows.Consumables(state)   rows: a note, then each category's, ranked ones first
      state    { class, spec, list, category }   category is nil for "all"
      a row    { kind = "consumable", key, id, consumable, bis, twin, tie, gap, ratio, unranked }
                   gap, ratio  as for an item, against the best of the category
                   unranked    true for what is listed without a rank
                   twin        true for the sharp or blunt version of the row before it; of the best, it is the best too
  Rows.Grouped(rows)     the same rows with a { kind = "header", group, text, scored } row before each slot's
                         rows, so the window can set the slots apart
  Rows.Character(state)  cells: the best pick of every slot, in the order of the game's character sheet
      a cell   { place = "left"|"right"|"bottom", slot, rank, id, source, ties, enchant, twoHand, reputation }
                   rank      1, or 2 for the second ring and the second trinket
                   id        nil when the list has nothing for the slot
                   ties      the other items that score exactly as this one: { id, ... }
                   enchant   the best enchant of the phase that goes on the item (Enchants.Info), or nil
                   twoHand   true for the off hand a two-hander leaves empty
               Items added by hand have no score: they stay in the list and are not on the sheet.

With the option "listAlts" off, only the best picks and the hand-added items
are listed.

Weapons: when a two-hander is the best pick, the main hand goes on with the
best one-handers and the off hand lists what goes with them, each under a note;
when a one-hander is, the main hand goes on with the best two-handers. Their
gap compares whole sets: a one-hander with the best off hand, or an off hand
with the best one-hander, against the two-hander; a two-hander against the
best main hand and off hand together.

A gap is a gap in score for that slot, not in damage or healing done.
]]

local Rows = {}
ns.Rows = Rows

local function Gap(score, reference)
    if not reference or reference <= 0 then return 0 end
    return math.floor((score - reference) / reference * 100 + 0.5)
end

local function Ratio(score, reference)
    if not reference or reference <= 0 then return 1 end
    return math.max(0, math.min(1, score / reference))
end

-- A weapon of the other style and what it is weighed against: both as scores, and both in the tenths
-- the data holds (whole numbers, to tell a tie for sure).
local function OtherScores(slots, slot, pick)
    local main, off = slots.main, slots.off
    if slots.twoHand then
        local partner
        if pick.partialSet ~= nil then
            partner = pick.partner
        else
            partner = ns.Ladders.Lead(slot == "main" and off.other or main.other)
        end
        return pick.score + (partner and partner.score or 0), main.best[1].score,
            pick.entry.score10 + (partner and partner.entry.score10 or 0), main.best[1].entry.score10
    end
    local offBest = off.best[1]
    return pick.score, main.best[1].score + (offBest and offBest.score or 0),
        pick.entry.score10, main.best[1].entry.score10 + (offBest and offBest.entry.score10 or 0)
end

local function OtherNote(slots, slot)
    if slot == "off" then return L.LIST_WITH_ONE_HAND end
    return slots.twoHand and L.LIST_OR_ONE_HAND or L.LIST_OR_TWO_HAND
end

-- Whether a row passes the Reputation filter.
local function PassesReputation(row, wanted)
    if not wanted then return true end
    return ns.Reputation.Reachable(row.reputation) == (wanted == "ok")
end

local function AddItem(all, facets, slot, id, row)
    local source = ns.Sources.Describe(id)
    if row.custom and not source.cost and not ns.Items.Get(id) then source = ns.Sources.Manual() end
    facets.sources[source.category] = true
    if source.zone then facets.zones[source.zone] = true end
    row.kind, row.id, row.slot, row.source = "item", id, slot, source
    row.reputation = ns.Reputation.Requirement(id)
    all[#all + 1] = row
end

local function FilterItems(all, facets, state)
    if not state.source and not state.zone and not state.reputation then return all, facets end
    local rows = {}
    for _, row in ipairs(all) do
        if row.kind == "item"
            and (not state.source or row.source.category == state.source)
            and (not state.zone or row.source.zone == state.zone)
            and PassesReputation(row, state.reputation) then
            rows[#rows + 1] = row
        end
    end
    return rows, facets
end

function Rows.AoeList(class, spec)
    return ns.data.aoe.lists[class .. ":" .. spec .. ":" .. ns.PlayerSide()]
end

-- Each slot is ranked after applying the source-evidence preference.
function Rows.AoePicks(tested, withAlternatives)
    local limit = 1 + (withAlternatives and ns.Alternatives() or 0)
    local seenOnly = ns:GetOption("seenOnly")
    local index, shown = 0, 0
    return function()
        while shown < limit and index < #tested do
            index = index + 1
            local sample = tested[index]
            if not seenOnly or ns.Items.Get(sample[1]).flags:find("s", 1, true) then
                shown = shown + 1
                return shown, sample
            end
        end
    end
end

function Rows.Aoe(state)
    local all, facets = {}, { sources = {}, zones = {} }
    local slots = Rows.AoeList(state.class, state.spec) or {}
    local withAlternatives = ns:GetOption("listAlts")
    for _, slot in ipairs(ns.SLOTS) do
        local tested = slots[slot]
        if tested and (not state.slot or state.slot == slot) then
            for rank, sample in Rows.AoePicks(tested, withAlternatives) do
                AddItem(all, facets, slot, sample[1], {
                    bis = rank == 1,
                    why = ns.Notes.For(sample[1], state.class, state.spec, "aoe", slot),
                    gain = sample[2], se = sample[3], weaponPartner = sample.partner,
                    weaponPriority = sample.weaponPriority, weaponBasePoints = sample.weaponBasePoints,
                    weaponBonusPoints = sample.weaponBonusPoints, weaponRotationPoints = sample.weaponRotationPoints,
                    pointStat = tested.pointStat,
                    shortGain = sample.shortGain, routeGain = sample.routeGain,
                    shortAverageGain = sample.shortAverageGain, routeAverageGain = sample.routeAverageGain,
                    cooldownSeconds = sample.cooldownSeconds,
                    shortRank = sample.shortRank, routeRank = sample.routeRank,
                    shortBaseline = tested.shortBaseline, routeBaseline = tested.routeBaseline,
                    routePackDamage = sample.routePackDamage, routeBaselinePackDamage = tested.routeBaselinePackDamage,
                    schools = sample.shortSchools, petPct = sample.shortPetPct,
                    passiveGain = sample.shortPassiveGain, activeGain = sample.shortActiveGain,
                    useAfter = sample.shortUseAfter, routeActivated = sample.routeActivated,
                    routeUsePack = sample.routeUsePack, routeUseAfter = sample.routeUseAfter,
                    pairedItem = tested.pairedItem, comparisonItem = tested.comparisonItem,
                    referenceWeapons = tested.referenceWeapons, activatedWeapons = sample.shortActivated,
                })
            end
        end
    end
    return FilterItems(all, facets, state)
end

function Rows.Gear(state)
    local all, facets = {}, { sources = {}, zones = {} }
    local gear = ns.Custom.GearList(state.class, state.spec, state.itemList)
    for _, slot in ipairs(ns.SLOTS) do
        if not state.slot or state.slot == slot then
            for index, entry in ipairs(gear.slots[slot] or {}) do
                AddItem(all, facets, slot, entry.id, { custom = true, gearIndex = index, enchantId = entry.enchant })
            end
        end
    end
    return FilterItems(all, facets, state)
end

function Rows.Items(state, withAlts)
    local all, facets = {}, { sources = {}, zones = {} }
    local slots = ns.Ladders.For(state.class, state.spec, state.list)
    if not slots then return all, facets end
    if withAlts == nil then withAlts = ns:GetOption("listAlts") end

    local function Add(slot, id, row)
        row.why = ns.Notes.For(id, state.class, state.spec, state.list, slot)
        AddItem(all, facets, slot, id, row)
    end

    for _, slot in ipairs(ns.SLOTS) do
        if not state.slot or state.slot == slot then
            local picks = slots[slot]
            local top = picks.best[1]
            local listed = {}
            for _, pick in ipairs(ns.Ladders.DisplayPicks(picks, withAlts)) do
                listed[pick.id] = true
                local bis = pick == top or pick == picks.best[2]
                if pick.option then
                    Add(slot, pick.id, { bis = bis, option = pick.option })
                elseif bis then
                    if ns.Ladders.HasFlag(pick.entry, "c") then
                        Add(slot, pick.id, { bis = true, recommended = true })
                    else
                        Add(slot, pick.id, { bis = true, gap = 0, ratio = 1 })
                    end
                elseif ns.Ladders.HasFlag(pick.entry, "x") then
                    Add(slot, pick.id, { bis = false, level = true })
                elseif ns.Ladders.HasFlag(pick.entry, "e") then
                    Add(slot, pick.id, { bis = false, placed = true })
                elseif ns.Ladders.HasFlag(pick.entry, "g") then
                    Add(slot, pick.id, { bis = false, estimated = true })
                elseif ns.Ladders.HasFlag(pick.entry, "c") or (top and ns.Ladders.HasFlag(top.entry, "c")) then
                    Add(slot, pick.id, { bis = false })
                else
                    local reference = pick.pairedWith and picks.best[2] or top
                    Add(slot, pick.id, {
                        bis = false, tie = ns.Ladders.IsTie(picks, pick) or nil,
                        gap = Gap(pick.score, reference.score), ratio = Ratio(pick.score, reference.score),
                    })
                end
            end
            if withAlts and picks.other[1] then
                all[#all + 1] = { kind = "note", slot = slot, text = OtherNote(slots, slot) }
                for _, pick in ipairs(picks.other) do
                    listed[pick.id] = true
                    if ns.Ladders.HasFlag(pick.entry, "x") then
                        Add(slot, pick.id, { bis = false, other = true, level = true })
                    elseif ns.Ladders.HasFlag(pick.entry, "e") then
                        Add(slot, pick.id, { bis = false, other = true, placed = true })
                    elseif ns.Ladders.HasFlag(pick.entry, "g") or pick.partialSet then
                        Add(slot, pick.id, { bis = false, other = true, estimated = true })
                    elseif slots.measuredWeaponSet then
                        -- The full enchanted sets decided the style. Individual slot scores use a different baseline.
                        Add(slot, pick.id, { bis = false, other = true })
                    else
                        local score, reference, score10, reference10 = OtherScores(slots, slot, pick)
                        Add(slot, pick.id, {
                            bis = false, other = true, tie = score10 == reference10 or nil,
                            gap = Gap(score, reference), ratio = Ratio(score, reference),
                        })
                    end
                end
            elseif slot == "off" and slots.twoHand then
                all[#all + 1] = { kind = "note", slot = slot, text = L.LIST_TWO_HAND }
            end
            for _, id in ipairs(ns.Custom.List(state.class, state.spec, state.list, slot)) do
                if not listed[id] then   -- the data may list it by now, under another phase or option
                    listed[id] = true
                    Add(slot, id, { bis = false, custom = true })
                end
            end
        end
    end

    return FilterItems(all, facets, state)
end

function Rows.Grouped(rows)
    local grouped, last = {}, nil
    for _, row in ipairs(rows) do
        local enchant, consumable = row.kind == "enchant", row.kind == "consumable"
        local group = (enchant or consumable) and row.key or row.slot
        if group ~= last then
            last = group
            grouped[#grouped + 1] = {
                kind = "header", group = group, scored = not (enchant or consumable or row.gearIndex or row.gain) or nil,
                text = (consumable and ns.Consumables.KeyName(group))
                    or (enchant and ns.Enchants.KeyName(group)) or ns.SlotName(group),
            }
        end
        grouped[#grouped + 1] = row
    end
    return grouped
end

---------------------------------------------------------------------------
-- The character sheet
---------------------------------------------------------------------------

-- The game's character sheet without the shirt and the tabard: place, slot, rank.
local SHEET = {
    { "left", "head" }, { "left", "neck" }, { "left", "shoulder" }, { "left", "back" }, { "left", "chest" },
    { "left", "wrist" },
    { "right", "hands" }, { "right", "waist" }, { "right", "legs" }, { "right", "feet" },
    { "right", "finger", 1 }, { "right", "finger", 2 }, { "right", "trinket", 1 }, { "right", "trinket", 2 },
    { "bottom", "main" }, { "bottom", "off" }, { "bottom", "ranged" },
}

-- The alternatives that score exactly as a best pick. When two rings or two trinkets score the same,
-- the second one carries them, so they are not counted twice.
local function Ties(picks, rank)
    local pick, ties = picks.best[rank], {}
    local second = picks.best[2]
    if rank == 1 and second and ns.Ladders.IsTie({ best = { pick } }, second) then return ties end
    for _, alt in ipairs(picks.alts) do
        if ns.Ladders.IsTie({ best = { pick } }, alt) then ties[#ties + 1] = alt.id end
    end
    return ties
end

function Rows.Character(state)
    local cells = {}
    local slots = ns.Ladders.For(state.class, state.spec, state.list)
    if not slots then return cells end
    local enchants = {}
    for _, group in ipairs(ns.Enchants.For(state.class, state.spec)) do
        enchants[group.key] = ns.Enchants.Info(group.ids[1])
    end
    for _, place in ipairs(SHEET) do
        local slot, rank = place[2], place[3] or 1
        local picks = slots[slot]
        local pick = picks.best[rank]
        local cell = { kind = "cell", place = place[1], slot = slot, rank = rank, ties = {} }
        if pick then
            cell.id = pick.id
            cell.option = pick.option
            if pick.option or (rank == 1 and not (picks.best[2] and picks.best[2].option)) then
                cell.tankOptions = picks.options
            end
            cell.source = ns.Sources.Describe(pick.id)
            cell.reputation = ns.Reputation.Requirement(pick.id)
            cell.ties = Ties(picks, rank)
            local key = ns.Enchants.KeyOf(slot, pick.id, ns.Ladders.HasFlag(pick.entry, "t"))
            cell.enchant = key and enchants[key] or nil
        elseif slot == "off" and slots.twoHand then
            cell.twoHand = true
        end
        cells[#cells + 1] = cell
    end
    return cells
end

function Rows.Consumables(state)
    local rows = {}
    local withAlts = ns:GetOption("listAlts")
    for _, group in ipairs(ns.Consumables.For(state.class, state.spec, state.list)) do
        if not state.category or state.category == group.key then
            local top = group.ranked[1]
            for index, entry in ipairs(group.ranked) do
                local consumable = ns.Consumables.Info(entry.id)
                local best = index == 1 or (index == 2 and entry.twin == true)
                if consumable and (best or withAlts) then
                    rows[#rows + 1] = {
                        kind = "consumable", key = group.key, id = entry.id, consumable = consumable,
                        bis = best, twin = entry.twin, tie = not best and entry.score == top.score or nil,
                        gap = Gap(entry.score, top.score), ratio = Ratio(entry.score, top.score),
                    }
                end
            end
            for _, id in ipairs(group.unranked) do
                local consumable = ns.Consumables.Info(id)
                if consumable then
                    rows[#rows + 1] = {
                        kind = "consumable", key = group.key, id = id, consumable = consumable, unranked = true,
                    }
                end
            end
        end
    end
    if rows[1] then table.insert(rows, 1, { kind = "note", text = L.CONS_NOTE }) end
    return rows
end

function Rows.Enchants(state)
    local rows = {}
    local withAlts = ns:GetOption("listAlts")
    local function Allowed(id)
        return PassesReputation({ reputation = ns.Reputation.EnchantRequirement(id) }, state.reputation)
    end
    local function Add(id, key, best, unranked)
        local enchant = ns.Enchants.Info(id)
        if enchant then
            rows[#rows + 1] = { kind = "enchant", key = key, bis = best, unranked = unranked, enchant = enchant,
                reputation = ns.Reputation.EnchantRequirement(id) }
        end
    end
    for _, group in ipairs(ns.Enchants.For(state.class, state.spec, nil, state.reputation and Allowed)) do
        if not state.slot or ns.Enchants.SlotOf(group.key) == state.slot then
            for index, id in ipairs(group.ids) do
                if index > 1 and not withAlts then break end
                Add(id, group.key, index == 1)
            end
            for _, id in ipairs(group.unranked) do Add(id, group.key, false, true) end
        end
    end
    return rows
end
