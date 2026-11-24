local _, ns = ...

--[[
Which dungeons to run for a spec's best picks: what the Dungeons tab draws (UI\Dungeons.lua), as plain tables.

  Dungeons.For(state)    state: the window's { class, spec, list }
      {
        runs      = { run, ... }     the runs that hold a piece, the ones with the most left to get first
        sheet     = { cell, ... }    the best pick of every slot, in the order of the game's character sheet
        rows      = { piece, ... }   every piece listed, slot by slot in that order, a slot's alternatives
                                     after its best pick(s): the lines of the grid
        elsewhere = { { category, count }, ... }   where the best picks no dungeon holds come from
        need, got                    best picks left to get in a dungeon, and already the player's
        dungeons                     runs with something left to get
      }
      a run     { key, instance, wing, name, short, color = { r, g, b }, entries, total, need, got, alts, noWing }
                    total     the pieces it holds, best picks and alternatives alike: what its line shows
                    need, got, alts   its best picks left to get, the ones the player has, its alternatives
                    noWing    true for the pieces of a dungeon run wing by wing that the data places in none of
                              its wings (a drop with no boss named): the dungeon's name alone would pass for a wing
      an entry  { piece, drops, percent, quest }   a piece in one run; a run's best picks come before its
                    alternatives
                    drops     the piece's sources in that run (Sources.Runs)
                    percent   the chance that a run gives the piece, from its bosses' rates; nil when a rate
                              is not known, and for a quest's reward
                    quest     the quest's title when the piece is a quest's reward: one run is enough
                    short     a few letters for a narrow place ("UBRS", "DM North")
      a piece   { id, slot, rank, best, owned, moot, source, runs, order, first }
                    best      a best pick; false for an alternative
                    owned     the player has it: worn, in the bags or in the bank (Sources.Owned)
                    moot      an alternative of a slot whose best pick(s) the player has
                    source    where it comes from (Sources.Describe), for the tooltip
                    runs      { [run key] = entry }, nil for a piece of elsewhere
                    order     the keys of runs, the run of the source the addon says for the piece first
                    first     true for the first line of its slot
      a cell    a piece, or { slot, rank, twoHand } for a slot the list leaves empty

A run is a dungeon, or the wing of one that is run on its own. The alternatives come with the option
"listAlts", as in the other tabs; they count in nothing: the numbers are the best picks'. The weapons of
the style that lost (Ladders: other) are omitted. Hand-added and named-list items are tracked goals.

Nothing here says how many runs it takes: a drop rate is a boss's, and who wins the roll is nobody's to say.
]]

local Dungeons = {}
ns.Dungeons = Dungeons

-- Slot order and number of positions on the character sheet.
local SHEET = {
    { "head", 1 }, { "neck", 1 }, { "shoulder", 1 }, { "back", 1 }, { "chest", 1 }, { "wrist", 1 },
    { "hands", 1 }, { "waist", 1 }, { "legs", 1 }, { "feet", 1 },
    { "finger", 2 }, { "trinket", 2 },
    { "main", 1 }, { "off", 1 }, { "ranged", 1 },
}

-- A colour and a short name per run. The wings of one dungeon keep to one family of colours; gold and the
-- colours of the item qualities are left alone.
local RUNS = {
    ["229:u"] = { "UBRS", 0.89, 0.32, 0.24 },
    ["229:l"] = { "LBRS", 0.94, 0.56, 0.18 },
    ["229"] = { "BRS", 0.91, 0.44, 0.23 },
    ["230"] = { "BRD", 0.73, 0.56, 0.32 },
    ["329:l"] = { "Strat Live", 0.90, 0.42, 0.64 },
    ["329:u"] = { "Strat UD", 0.56, 0.49, 0.90 },
    ["329"] = { "Strat", 0.72, 0.45, 0.79 },
    ["289"] = { "Scholo", 0.21, 0.70, 0.67 },
    ["429:e"] = { "DM East", 0.53, 0.77, 0.25 },
    ["429:w"] = { "DM West", 0.18, 0.64, 0.37 },
    ["429:n"] = { "DM North", 0.76, 0.81, 0.23 },
    ["429"] = { "DM", 0.44, 0.72, 0.30 },
    ["349"] = { "Mara", 0.35, 0.66, 0.91 },
    ["2974"] = { "Blackmaw", 0.66, 0.49, 0.36 },
    ["3001"] = { "Shaper's", 0.35, 0.78, 0.84 },
    ["109"] = { "ST", 0.42, 0.62, 0.50 },
    ["209"] = { "ZF", 0.85, 0.75, 0.48 },
    ["2994"] = { "Alcaz", 0.50, 0.58, 0.67 },
    ["70"] = { "Ulda", 0.60, 0.56, 0.50 },
    ["3039"] = { "Krol'dok", 0.66, 0.68, 0.74 },
    ["2970"] = { "Drowned", 0.24, 0.53, 0.80 },
    ["189:g"] = { "SM GY", 0.60, 0.30, 0.30 },
    ["189:l"] = { "SM Lib", 0.75, 0.33, 0.33 },
    ["189:a"] = { "SM Arm", 0.85, 0.38, 0.36 },
    ["189:c"] = { "SM Cath", 0.93, 0.47, 0.44 },
    ["189"] = { "SM", 0.80, 0.36, 0.35 },
    ["129"] = { "RFD", 0.55, 0.62, 0.42 },
    ["47"] = { "RFK", 0.66, 0.60, 0.38 },
    ["90"] = { "Gnomer", 0.45, 0.70, 0.60 },
    ["2959"] = { "Dalaran", 0.62, 0.52, 0.86 },
    ["2998"] = { "Excavation", 0.72, 0.62, 0.44 },
    ["48"] = { "BFD", 0.30, 0.50, 0.72 },
    ["33"] = { "SFK", 0.50, 0.50, 0.66 },
    ["34"] = { "Stockade", 0.58, 0.58, 0.62 },
    ["36"] = { "Deadmines", 0.70, 0.52, 0.40 },
    ["43"] = { "WC", 0.40, 0.68, 0.45 },
    ["2999"] = { "Lordaeron", 0.52, 0.60, 0.52 },
    ["389"] = { "RFC", 0.80, 0.45, 0.30 },
    ["3065"] = { "Thanes", 0.78, 0.66, 0.42 },
}
-- A run this table does not know (a dungeon a later version of the data brings) takes one of these.
local SPARE = { { 0.55, 0.60, 0.70 }, { 0.70, 0.58, 0.50 }, { 0.50, 0.68, 0.62 }, { 0.68, 0.55, 0.68 } }

local function Look(key, instance, name)
    local known = RUNS[key]
    if known then return known[1], { known[2], known[3], known[4] } end
    return name, SPARE[instance % #SPARE + 1]
end

-- The chance that a run gives the piece: one of its bosses at least. nil when a rate is not known.
local function Percent(drops)
    local miss = 1
    for _, drop in ipairs(drops) do
        if not drop.percent then return nil end
        miss = miss * (1 - math.min(100, drop.percent) / 100)
    end
    return (1 - miss) * 100
end

function Dungeons.Lists(state)
    local lists = { { key = "pve", name = ns.L.LIST_RAID } }
    if ns.Rows.AoeList(state.class, state.spec) then
        lists[#lists + 1] = { key = "aoe", name = ns.L.LIST_AOE }
    end
    lists[#lists + 1] = { key = "pvp", name = ns.ListName("pvp") }
    for _, gear in ipairs(ns.db.gearLists) do
        if gear.class == state.class and gear.spec == state.spec then
            lists[#lists + 1] = { key = "gear" .. gear.id, name = gear.name, gear = gear }
        end
    end
    return lists
end

function Dungeons.Selection(state)
    local saved = ns.char.dungeonLists
    return saved and saved[state.class .. ":" .. state.spec] or { [state.list] = true }
end

function Dungeons.ToggleList(state, key)
    local selection = Dungeons.Selection(state)
    selection[key] = not selection[key] or nil
    ns.char.dungeonLists = ns.char.dungeonLists or {}
    ns.char.dungeonLists[state.class .. ":" .. state.spec] = selection
end

-- Combine goals by slot. Preserve two copies requested by one loadout, and promote
-- an alternative to a goal when another selected list calls for that item.
local function TrackedSlots(state, withAlts)
    local slots, count = {}, 0
    for _, slot in ipairs(ns.SLOTS) do slots[slot] = { best = {}, alts = {}, copies = {}, seenAlt = {} } end
    local selection = Dungeons.Selection(state)
    for _, list in ipairs(Dungeons.Lists(state)) do
        if selection[list.key] then
            local ladder, aoe
            if list.key == "aoe" then aoe = ns.Rows.AoeList(state.class, state.spec)
            elseif not list.gear then ladder = ns.Ladders.For(state.class, state.spec, list.key) end
            if ladder or aoe or list.gear then count = count + 1 end
            if count == 1 then slots.twoHand = ladder and ladder.twoHand else slots.twoHand = nil end
            for _, slot in ipairs(ns.SLOTS) do
                local merged, copies = slots[slot], {}
                local function Add(id, best, option)
                    local pick = { id = id, list = list.key, option = option }
                    if best then
                        copies[id] = (copies[id] or 0) + 1
                        if copies[id] > (merged.copies[id] or 0) then
                            pick.copy = copies[id]
                            merged.copies[id] = copies[id]
                            table.insert(merged.best, pick)
                        end
                    elseif not merged.seenAlt[id] then
                        merged.seenAlt[id] = true
                        table.insert(merged.alts, pick)
                    end
                end
                if list.gear then
                    for _, entry in ipairs(list.gear.slots[slot] or {}) do Add(entry.id, true) end
                elseif aoe then
                    for rank, sample in ns.Rows.AoePicks(aoe[slot] or {}, withAlts) do Add(sample[1], rank == 1) end
                elseif ladder then
                    local picks = ladder[slot]
                    for _, pick in ipairs(picks.best) do Add(pick.id, true, pick.option) end
                    for _, id in ipairs(ns.Custom.List(state.class, state.spec, list.key, slot)) do
                        if not copies[id] then Add(id, true) end
                    end
                    if withAlts then
                        for _, pick in ipairs(ns.Ladders.DisplayAlts(picks, true)) do Add(pick.id, false, pick.option) end
                    end
                end
            end
        end
    end
    return slots, count
end

function Dungeons.For(state)
    local model = { runs = {}, sheet = {}, rows = {}, elsewhere = {}, need = 0, got = 0, dungeons = 0 }
    local slots, tracked = TrackedSlots(state, ns:GetOption("listAlts"))
    model.tracked = tracked
    if tracked == 0 then return model end
    local byKey, counts = {}, {}

    local function Place(piece)
        local drops = ns.Sources.Runs(piece.id)
        if not drops then return end
        local perRun, order = {}, {}
        for _, drop in ipairs(drops) do
            if not perRun[drop.run] then
                perRun[drop.run] = {}
                order[#order + 1] = drop.run
            end
            table.insert(perRun[drop.run], drop)
        end
        piece.runs, piece.order = {}, order
        for _, key in ipairs(order) do
            local first = perRun[key][1]
            local run = byKey[key]
            if not run then
                local name = ns.Sources.RunName(first.instance, first.wing)
                local short, color = Look(key, first.instance, name)
                run = { key = key, instance = first.instance, wing = first.wing, name = name, short = short,
                    color = color, entries = {}, need = 0, got = 0, alts = 0,
                    noWing = first.wing == nil and ns.Sources.HasWings(first.instance) or nil }
                byKey[key] = run
                model.runs[#model.runs + 1] = run
            end
            local entry = { piece = piece, drops = perRun[key], quest = first.quest }
            entry.percent = not first.quest and Percent(perRun[key]) or nil
            run.entries[#run.entries + 1] = entry
            piece.runs[key] = entry
            if not piece.best then
                run.alts = run.alts + 1
            elseif piece.owned then
                run.got = run.got + 1
            else
                run.need = run.need + 1
            end
        end
    end

    local function Piece(slot, rank, pick, best)
        return { id = pick.id, slot = slot, rank = rank, best = best, option = pick.option, list = pick.list,
            owned = ns.Sources.Owned(pick.id, pick.copy),
            source = ns.Items.Get(pick.id) and ns.Sources.Describe(pick.id) or ns.Sources.Manual() }
    end

    local function Slot(slot, capacity)
        local picks = slots[slot]
        for rank = 1, math.max(capacity, #picks.best) do
            local pick = picks.best[rank]
            if pick then
                local piece = Piece(slot, rank, pick, true)
                piece.first = rank == 1
                Place(piece)
                model.sheet[#model.sheet + 1] = piece
                model.rows[#model.rows + 1] = piece
                if not piece.runs then
                    local category = piece.source.category
                    local entry = counts[category] or { category = category, count = 0, list = piece.list }
                    entry.count = entry.count + 1
                    counts[category] = entry
                elseif piece.owned then
                    model.got = model.got + 1
                else
                    model.need = model.need + 1
                end
            else
                table.insert(model.sheet, { slot = slot, rank = rank, twoHand = slot == "off" and slots.twoHand or nil })
            end
        end
        local covered = picks.best[1] ~= nil
        for _, best in ipairs(picks.best) do covered = covered and ns.Sources.Owned(best.id, best.copy) end
        local rank = 0
        for _, alt in ipairs(picks.alts) do
            if not picks.copies[alt.id] then
                rank = rank + 1
                local piece = Piece(slot, rank, alt, false)
                piece.moot = covered and not alt.option
                piece.first = not picks.best[1] and rank == 1
                Place(piece)
                table.insert(model.rows, piece)
            end
        end
    end

    for _, place in ipairs(SHEET) do Slot(place[1], place[2]) end

    for _, run in ipairs(model.runs) do
        if run.need > 0 then model.dungeons = model.dungeons + 1 end
        run.total = #run.entries
        -- the best picks before the alternatives, each in the order of the character sheet
        local ordered = {}
        for _, best in ipairs({ true, false }) do
            for _, entry in ipairs(run.entries) do
                if entry.piece.best == best then ordered[#ordered + 1] = entry end
            end
        end
        run.entries = ordered
    end
    table.sort(model.runs, function(a, b)
        if a.need ~= b.need then return a.need > b.need end
        if a.got ~= b.got then return a.got > b.got end
        if a.alts ~= b.alts then return a.alts > b.alts end
        return a.name < b.name
    end)
    for _, category in ipairs(ns.Sources.CATEGORIES) do
        if counts[category] then
            model.elsewhere[#model.elsewhere + 1] = counts[category]
        end
    end
    return model
end
