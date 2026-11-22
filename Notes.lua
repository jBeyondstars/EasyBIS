local _, ns = ...

--[[
A few words on rankings that surprise (Data\Notes.lua, written by hand in _build/corrections/notes.json):
why Destiny stands before weapons with more damage per second, what Hand of Justice gives in Forever.
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

function Notes.For(item, class, spec, list, slot)
    local notes = (byItem or ByItem())[item]
    if not notes or not class or not spec then return nil end
    local key = class .. spec
    for _, note in ipairs(notes) do
        if (not note.specs or note.specs[key])
            and (not note.slot or note.slot == slot)
            and (not note.list or note.list == list)
            and (not note.simulated or ns.Ladders.Measured(class, spec, list)) then
            return note[ns.locale] or note.enUS
        end
    end
    return nil
end
