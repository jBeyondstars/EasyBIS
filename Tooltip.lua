local _, ns = ...
local L = ns.L

--[[
Item tooltips say which classes and specs want the item:

    Easy BIS
    (icon) Shaman Enhancement            BIS
    (icon) Warrior Arms, Fury            BIS PvE · Alt PvP
    (icon) Hunter                        Alt

A line per class and status. The spec names are left out when every spec of
the class is on the line. An AoE/Dung membership names each applicable
list explicitly. Otherwise PvE and PvP are named when the two lists disagree. "Alt" is one of the picks that come after the best, as many
as the "alternatives per slot" option asks for (the second ring or trinket
counts among them), or a weapon of the other style (a one-hander when a
two-hander is best); an
alternative that scores as much as the best pick reads "BIS". "Added" is an
item the player put in that spec's list by hand (Custom.lua), when the data
does not pick it. The lists are the ones of the character's content phase
(ns.Phase). Under those lines, the reputation the item asks for, how far the
character is, where it is sold and for how much (Reputation.TooltipLines).

  Tooltip.BuildLines(id)   { { left, right, r, g, b }, ... }, also used by /easybis item
]]

local Tooltip = {}
ns.Tooltip = Tooltip

-- A delayed leave can arrive after a Blizzard menu has taken the tooltip.
function Tooltip.HideOwned(owner)
    if owner and not (GameTooltip.IsForbidden and GameTooltip:IsForbidden()) and GameTooltip:GetOwner() == owner then
        GameTooltip:Hide()
    end
end

local BIS_COLOR = "|cffffd100"
local ALT_COLOR = "|cffc0c0c0"
local SEPARATOR = " |cff808080·|r "

-- How much a spec wants an item for a list: the highest of its hits counts.
local ADDED, ALT, BIS = 1, 2, 3
local THREAT, MITIGATION = 4, 5

local function RankText(rank)
    if rank == THREAT then return BIS_COLOR .. L.RANK_THREAT .. "|r" end
    if rank == MITIGATION then return BIS_COLOR .. L.RANK_MITIGATION .. "|r" end
    if rank == BIS then return BIS_COLOR .. L.RANK_BIS .. "|r" end
    if rank == ALT then return ALT_COLOR .. L.RANK_ALT .. "|r" end
    return ns.COLOR .. L.RANK_CUSTOM .. "|r"
end

-- status[list] = BIS, ALT, ADDED or nil (not wanted) -> "BIS", "Alt PvE", "BIS PvE · Alt PvP"...
local function StatusText(status, lists)
    if not status.aoe then
        local first, second = lists[1], lists[2]
        if not second or status[first] == status[second] then
            return status[first] and RankText(status[first]) or nil
        end
    end
    local parts = {}
    for _, list in ipairs(lists) do
        if status[list] ~= nil then
            local label = status.aoe and list == "pve" and L.LIST_RAID or ns.ListName(list)
            parts[#parts + 1] = RankText(status[list]) .. " " .. label
        end
    end
    if status.aoe then parts[#parts + 1] = RankText(status.aoe) .. " AoE/Dung" end
    return parts[1] and table.concat(parts, SEPARATOR) or nil
end

function Tooltip.BuildLines(id)
    local hits = ns.Index.ForItem(id)
    local aoeHits = ns:ListShown("pve") and ns.Index.AoeForItem(id)
    if not hits and not aoeHits then return {} end

    local lists = {}
    for _, list in ipairs(ns.LISTS) do
        if ns:ListShown(list) then lists[#lists + 1] = list end
    end
    if not lists[1] then return {} end

    local onlyClass = ns:GetOption("onlyMyClass") and ns.PlayerClass() or nil
    local withAlternatives = ns:GetOption("alternatives")

    -- perSpec[class][spec][list] = BIS, ALT or ADDED: the best of the item's slots wins
    local perSpec, memberships = {}, {}
    for _, hit in ipairs(hits or {}) do
        local rank = hit.custom and ADDED or (hit.bis and BIS or ALT)
        if hit.option then rank = hit.option.sign == 1 and THREAT or MITIGATION end
        local showClass = not onlyClass or hit.class == onlyClass
        if hit.listName and showClass and ns:ListShown("pve") then
            local r, g, b = ns.ClassColor(hit.class)
            local icon = ns.ClassIcon(hit.class)
            local classSpec = ns.ClassName(hit.class) .. " " .. ns.SpecName(ns.Index.SpecName(hit.class, hit.spec))
            memberships[#memberships + 1] = {
                left = (icon ~= "" and icon .. " " or "") .. classSpec,
                right = L.GEAR_MEMBERSHIP:format(hit.listName), r = r, g = g, b = b,
            }
        elseif not hit.listName and showClass and (rank ~= ALT or withAlternatives) and ns:ListShown(hit.list) then
            perSpec[hit.class] = perSpec[hit.class] or {}
            local status = perSpec[hit.class][hit.spec] or {}
            perSpec[hit.class][hit.spec] = status
            status[hit.list] = math.max(status[hit.list] or 0, rank)
        end
    end

    for _, hit in ipairs(aoeHits or {}) do
        if (not onlyClass or hit.class == onlyClass) and (hit.bis or withAlternatives) then
            perSpec[hit.class] = perSpec[hit.class] or {}
            local status = perSpec[hit.class][hit.spec] or {}
            perSpec[hit.class][hit.spec] = status
            status.aoe = math.max(status.aoe or 0, hit.bis and BIS or ALT)
        end
    end

    local lines = {}
    for _, class in ipairs(ns.CLASSES) do
        local specs = perSpec[class]
        if specs then
            -- specs with the same status share a line, in the order the specs are shown
            local groups, byText = {}, {}
            for _, spec in ipairs(ns.Index.SpecOrder(class)) do
                local text = specs[spec] and StatusText(specs[spec], lists)
                if text then
                    local group = byText[text]
                    if not group then
                        group = { text = text, names = {} }
                        byText[text] = group
                        groups[#groups + 1] = group
                    end
                    group.names[#group.names + 1] = ns.SpecName(ns.Index.SpecName(class, spec))
                end
            end
            local r, g, b = ns.ClassColor(class)
            local icon = ns.ClassIcon(class)
            for _, group in ipairs(groups) do
                local left = (icon ~= "" and icon .. " " or "") .. ns.ClassName(class)
                if #group.names < ns.Index.SpecCount(class) then
                    left = left .. " " .. table.concat(group.names, ", ")
                end
                lines[#lines + 1] = { left = left, right = group.text, r = r, g = g, b = b }
            end
        end
    end
    for _, line in ipairs(memberships) do lines[#lines + 1] = line end
    return lines
end

local function Decorate(tooltip, id)
    if type(id) ~= "number" or not ns:GetOption("tooltip") then return end
    -- Restricted content hands out secret values, which must not be used as table keys.
    if issecretvalue and issecretvalue(id) then return end
    if tooltip.IsForbidden and tooltip:IsForbidden() then return end

    local lines = Tooltip.BuildLines(id)
    if not lines[1] then return end
    tooltip:AddLine(" ")
    tooltip:AddLine(ns.COLOR .. L.ADDON_TITLE .. "|r")
    for _, line in ipairs(lines) do
        tooltip:AddDoubleLine(line.left, line.right, line.r, line.g, line.b, 1, 1, 1)
    end
    if ns:GetOption("repTooltip") then
        for _, line in ipairs(ns.Reputation.TooltipLines(id)) do
            tooltip:AddLine(line.text, line.r, line.g, line.b, true)
        end
    end
end

local errorReported = false

-- A tooltip must never break because of Easy BIS: report the first error, then stay quiet.
local function SafeDecorate(tooltip, id)
    local ok, message = pcall(Decorate, tooltip, id)
    if ok or errorReported then return end
    errorReported = true
    ns:Print(tostring(message))
end

local function Install()
    if TooltipDataProcessor and TooltipDataProcessor.AddTooltipPostCall and Enum and Enum.TooltipDataType
        and Enum.TooltipDataType.Item then
        TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, function(tooltip, data)
            SafeDecorate(tooltip, data and data.id)
        end)
        return
    end
    -- Older tooltip API
    for _, name in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2" }) do
        local tooltip = _G[name]
        if tooltip and tooltip.HookScript then
            tooltip:HookScript("OnTooltipSetItem", function(self)
                local _, link = self:GetItem()
                SafeDecorate(self, link and tonumber(link:match("item:(%d+)")))
            end)
        end
    end
end

Install()
