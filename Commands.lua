local _, ns = ...
local L = ns.L

--[[
/easybis (or /ebis):
  (nothing)                              open or close the window
  help                                   list the commands
  tooltip, class, alt, unsourced, seen, pvp, minimap   switch an option
  alternatives [2-6]                     how many alternatives a slot lists
  phase [0, 1 or all]                    the content phase the lists stop at
  item [link or ID]                      say who wants an item
  list [1-3] [pvp]                       print the list of one of the player's specs
  add [link or ID] [off]                 add an item by hand to the list the window shows (Custom.lua)
  remove [link or ID]                    take it out again
]]

local OPTIONS = {
    tooltip = "tooltip",
    class = "onlyMyClass",
    alt = "alternatives",
    unsourced = "unsourced",
    seen = "seenOnly",
    pvp = "pvpRewards",
    minimap = "minimap",
}

local function Toggle(option)
    ns:SetOption(option, not ns:GetOption(option))
    ns:Print(L.OPT_STATE:format(L["OPT_" .. option], ns:GetOption(option) and L.ON or L.OFF))
end

local function Help()
    ns:Print(L.HELP_HEADER:format(ns.version))
    for _, key in ipairs({ "HELP_WINDOW", "HELP_TOOLTIP", "HELP_CLASS", "HELP_ALT", "HELP_UNSOURCED", "HELP_SEEN",
        "HELP_PVP", "HELP_ALT_COUNT", "HELP_MINIMAP", "HELP_PHASE", "HELP_ITEM", "HELP_LIST", "HELP_ADD", "HELP_REMOVE" }) do
        ns:Print(L[key])
    end
    ns:Print(L.CREDIT)
end

-- "0", "1"... or "all"; anything else only says where the lists stop now.
local function PhaseCommand(rest)
    local wanted = rest:lower() == "all" and 9 or tonumber(rest)
    if wanted then ns:SetPhase(wanted) end
    ns:Print(L.PHASE_STATE:format(ns.PhaseName(ns.Phase())))
end

-- A number sets how many alternatives a slot lists; anything else only says how many it lists now.
local function AlternativesCommand(rest)
    if tonumber(rest) then ns:SetAlternatives(tonumber(rest)) end
    ns:Print(L.ALT_COUNT_STATE:format(ns.Alternatives()))
end

local function ItemCommand(rest)
    local id = tonumber(rest:match("item:(%d+)") or rest:match("^(%d+)$"))
    if not id then
        ns:Print(L.ITEM_USAGE)
        return
    end
    local lines = ns.Tooltip.BuildLines(id)
    if not lines[1] then
        ns:Print(L.ITEM_NOBODY:format(ns.Items.Link(id)))
        return
    end
    ns:Print(L.ITEM_HEADER:format(ns.Items.Link(id)))
    for _, line in ipairs(lines) do
        local color = ("|cff%02x%02x%02x"):format(math.floor(line.r * 255), math.floor(line.g * 255), math.floor(line.b * 255))
        ns:Print(("  %s%s|r  %s"):format(color, line.left, line.right))
    end
end

local function Links(picks)
    local links = {}
    for _, pick in ipairs(picks) do links[#links + 1] = ns.Items.Link(pick.id) end
    return table.concat(links, " ")
end

local function ListCommand(rest)
    local class = ns.PlayerClass()
    local specs = ns.Ladders.Specs(class)
    if not specs[1] then
        ns:Print(L.NO_DATA)
        return
    end
    local wanted = tonumber(rest:match("%d+")) or 1
    local list = rest:lower():find("pvp", 1, true) and "pvp" or "pve"
    local spec
    for _, candidate in ipairs(specs) do
        if candidate.index == wanted then spec = candidate end
    end
    if not spec then
        ns:Print(L.LIST_NO_SPEC:format(tostring(wanted)))
        return
    end

    local slots = ns.Ladders.For(class, spec.index, list)
    ns:Print(L.LIST_HEADER:format(ns.ClassName(class), ns.SpecName(spec.name), ns.ListLongName(list)))
    for _, slot in ipairs(ns.SLOTS) do
        local picks = slots[slot]
        local text
        if picks.best[1] then
            text = "|cffffd100" .. L.RANK_BIS .. "|r " .. Links(picks.best)
        elseif slot == "off" and slots.twoHand then
            text = L.LIST_TWO_HAND
        else
            text = L.LIST_EMPTY
        end
        -- the alternatives, then the weapons of the other style
        local alternatives = Links(picks.alts)
        if picks.other[1] then
            alternatives = (alternatives ~= "" and alternatives .. " " or "") .. Links(picks.other)
        end
        if alternatives ~= "" then
            text = text .. "  |cffc0c0c0" .. L.RANK_ALT .. "|r " .. alternatives
        end
        ns:Print(("  %s: %s"):format(ns.SlotName(slot), text))
    end
end

-- "add [link] off" puts a one-handed weapon in the off hand's list.
local function AddCommand(rest)
    if rest == "" then
        ns:Print(L.HELP_ADD)
        return
    end
    local text = rest:match("^(.-)%s+[oO][fF][fF]$")
    local class, spec, list = ns.Browser.Target()
    local _, message = ns.Custom.Submit(class, spec, list, text or rest, text and "off" or nil)
    ns:Print(message)
end

local function RemoveCommand(rest)
    if rest == "" then
        ns:Print(L.HELP_REMOVE)
        return
    end
    local class, spec, list = ns.Browser.Target()
    local _, message = ns.Custom.Withdraw(class, spec, list, rest)
    ns:Print(message)
end

SLASH_EASYBIS1 = "/easybis"
SLASH_EASYBIS2 = "/ebis"
SlashCmdList.EASYBIS = function(message)
    local command, rest = (message or ""):match("^%s*(%S*)%s*(.-)%s*$")
    command = command:lower()
    if OPTIONS[command] then
        Toggle(OPTIONS[command])
    elseif command == "phase" then
        PhaseCommand(rest)
    elseif command == "alternatives" then
        AlternativesCommand(rest)
    elseif command == "item" then
        ItemCommand(rest)
    elseif command == "list" then
        ListCommand(rest)
    elseif command == "add" and ns.Browser then
        AddCommand(rest)
    elseif command == "remove" and ns.Browser then
        RemoveCommand(rest)
    elseif command == "" and ns.Browser then
        ns.Browser.Toggle()
    else
        Help()
    end
end
