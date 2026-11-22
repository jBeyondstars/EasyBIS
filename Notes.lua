local _, ns = ...

--[[
A few words on rankings that surprise (Data\Notes.lua): hand-written item notes, simulator limitations,
then paired PvE comparisons for the exact item and slot tested.
The window shows them by a mark after an item's score.

Notes.For(item, class, spec, list, slot)   the text for that item in that slot of that list, in the game's
                                           language; nil without one. Of an item's notes, the first that fits.
]]

local Notes = {}
ns.Notes = Notes

-- The data holds a note once, with its items: item -> its notes, in the data's order, made on first use.
local byItem

local function ByItem()
    byItem = {}
    for _, note in ipairs(ns.data.notes or {}) do
        for _, item in ipairs(note.items) do
            local notes = byItem[item]
            if not notes then
                notes = {}
                byItem[item] = notes
            end
            notes[#notes + 1] = note
        end
    end
    return byItem
end

local function Comparison(item, key, slot)
    local rows = ns.data.comparisons and ns.data.comparisons[key .. "_" .. slot]
    if not rows then return nil end
    local rival, swap, stats, status, limits = rows:match(" " .. item .. ":(%d+):([%d%-]+):([%d%-]+):%d+:(%a)(%a*)")
    if not rival then return nil end
    local name = ns.Items.Name(tonumber(rival))
    local french = ns.locale == "frFR"
    if limits ~= "" then
        if limits == "a" then
            return french and ("La fréquence du proc de " .. name .. " rend ce classement incertain.")
                or ("The uncertain proc rate of " .. name .. " can change this ranking.")
        end
        return french and ("Le simulateur omet un effet de " .. name .. ", ce qui peut changer le classement.")
            or ("The simulator omits an effect on " .. name .. ", which can change this ranking.")
    end
    if status == "n" then
        return french and ("Le test ne départage pas cet objet et " .. name .. ".")
            or ("The test cannot distinguish this item from " .. name .. ".")
    end
    local function dps(cents)
        local number = string.format("%+.1f", tonumber(cents) / 100)
        return french and (number:gsub("%.", ",")) or number
    end
    if status == "r" then
        return french and string.format("Un second essai inverse l’ordre face à %s (%s DPS).", name, dps(swap))
            or string.format("A second test reverses the ranking against %s (%s DPS).", name, dps(swap))
    end
    return french and string.format("Sur la tenue testée, %s DPS face à %s (%s avec les seules stats fixes).", dps(swap), name, dps(stats))
        or string.format("On the reference set, %s DPS versus %s (%s from fixed stats alone).", dps(swap), name, dps(stats))
end

function Notes.For(item, class, spec, list, slot)
    if not item or not class or not spec then return nil end
    local notes = (byItem or ByItem())[item]
    local key = class .. spec
    for i = 1, notes and #notes or 0 do
        local note = notes[i]
        if (not note.specs or note.specs[key])
            and (not note.slot or note.slot == slot)
            and (not note.list or note.list == list)
            and (not note.simulated or ns.Ladders.Measured(class, spec, list)) then
            return note[ns.locale] or note.enUS
        end
    end
    if list == "pve" and slot and ns.Ladders.Measured(class, spec, list) then
        return Comparison(item, key, slot)
    end
    return nil
end
