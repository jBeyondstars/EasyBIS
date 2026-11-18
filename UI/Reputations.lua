local _, ns = ...
local L = ns.L
local Widgets = ns.Widgets
local Browser = ns.Browser
local Reputation = ns.Reputation

--[[
The Reputations tab of the window: what the spec, the list and the phase ask of each faction.

  left     the factions, most wanted first: the player's own, then the crafters' recipes, which are kept apart
           and counted in nobody's total. Each says where the player stands and how many pieces it opens.
  right    the faction chosen: where the player stands, what each standing unlocks for this spec, who sells
           it, and how to earn it. Each way of earning says how far it can be trusted: Data, To check, Unknown.

Gold is for what the player has earned. Nothing here says how long a standing takes: nothing measures it.

  ReputationView.Create(parent)   the view, hidden
  ReputationView.Update(state)    fills it. state: the window's { class, spec, list, faction, factionArtisan }
  ReputationView.Hide()
  ReputationView.view             (the tests read it: factionData, detailData, buttons, lines, title, you, empty)
]]

local ReputationView = {}
ns.ReputationView = ReputationView

local LIST_WIDTH = 292        -- the factions, their scroll bar included
local BAR_ROOM = 26           -- what a scroll bar takes
local DETAIL_WIDTH = 592      -- the faction's text
local PAD = 8
local GROUP_HEIGHT = 26       -- a group's name over its factions
local FACTION_HEIGHT = 56     -- a faction in the list
local BAR_HEIGHT = 4
local BADGE_WIDTH = 74        -- how far a way of earning can be trusted
local ICON = 20
local HEIGHTS = { section = 30, step = 24, entry = 26, text = 20, way = 20 }
local UNKNOWN_ICON = "Interface\\Icons\\INV_Misc_QuestionMark"

local MUTED = Widgets.MUTED
local GOLD, WHITE, GREY = "|cffffd100", "|cffffffff", "|cffa8a8b0"
local EVIDENCE = { data = "|cff8fd19e", check = "|cffef9a55", unknown = "|cffa8a8b0" }

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

local view

---------------------------------------------------------------------------
-- What the right side says, as plain lines
---------------------------------------------------------------------------

local function EntryName(entry)
    if entry.enchant then
        local info = ns.Enchants.Info(entry.enchant)
        return info and ns.Enchants.Name(info) or entry.enchant
    end
    local name, quality, _
    if GetInfo then name, _, quality = GetInfo(entry.id) end
    local _, _, _, hex = ns.QualityColor(quality)
    return hex .. (name or ns.Items.Name(entry.id)) .. "|r"
end

local function EntryIcon(entry)
    if entry.enchant then
        local info = ns.Enchants.Info(entry.enchant)
        return info and ns.Enchants.Icon(info) or UNKNOWN_ICON
    end
    local texture
    if GetInfo then texture = select(10, GetInfo(entry.id)) end
    return texture or (GetIcon and GetIcon(entry.id)) or UNKNOWN_ICON
end

-- The slot, and what sets this piece apart from the others of the standing.
local function EntryPlace(entry)
    local requirement = entry.requirement
    local place = entry.enchant and ns.Enchants.KeyName(entry.slot) or ns.SlotName(entry.slot)
    if requirement.kind == Reputation.QUEST then return place .. ", " .. L.REP_KIND_QUEST end
    if requirement.profession then return place .. ", " .. ns.ProfessionName(requirement.profession) end
    return place
end

local function StepState(group, standing)
    local status = Reputation.Status({ factionID = group.factionID, standing = standing })
    if status == "met" then return GOLD .. L.REP_MET .. "|r" end
    if status == "unknown" then return WHITE .. L.REP_UNKNOWN .. "|r" end
    return ""
end

-- { kind = "section"|"step"|"entry"|"text"|"way", text, right, entry, evidence }, top to bottom
local function DetailLines(group)
    local lines = {}
    local function Add(line) lines[#lines + 1] = line end
    if group.artisan then Add({ kind = "text", text = GREY .. L.REP_ARTISAN_NOTE .. "|r" }) end

    Add({ kind = "section", text = L.REP_LADDER })
    for _, standing in ipairs(Reputation.STANDINGS) do
        local entries = group.steps[standing]
        if entries or standing > Reputation.NEUTRAL then   -- Neutral has a line only when a piece asks for it
            Add({ kind = "step", text = Reputation.StandingName(standing), right = StepState(group, standing) })
            for _, entry in ipairs(entries or {}) do
                local rank = entry.role == "best" and (WHITE .. L.RANK_BIS) or (GREY .. L.RANK_ALT)
                Add({ kind = "entry", text = EntryName(entry), place = EntryPlace(entry), right = rank .. "|r", entry = entry })
            end
            if not entries then Add({ kind = "text", text = GREY .. L.REP_LADDER_NONE .. "|r" }) end
        end
    end

    Add({ kind = "section", text = L.REP_VENDOR })
    Add({ kind = "text", text = Reputation.VendorText(group.factionID) })

    Add({ kind = "section", text = L.REP_WAYS })
    for _, way in ipairs(Reputation.Ways(group.factionID)) do
        Add({ kind = "way", text = way.text, evidence = way.evidence })
    end
    return lines
end

---------------------------------------------------------------------------
-- The factions on the left
---------------------------------------------------------------------------

local function Choose(button)
    Widgets.Click()
    Browser.ShowReputation(button.group.factionID, button.group.artisan)
end

local function CreateGroupTitle(parent)
    local title = parent:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    title:SetJustifyH("LEFT")
    title:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    return title
end

local function CreateFaction(parent)
    local button = CreateFrame("Button", nil, parent)
    button:SetSize(LIST_WIDTH - BAR_ROOM, FACTION_HEIGHT - 2)
    Widgets.ListHighlight(button, "HIGHLIGHT", 0.32)
    button.selected = Widgets.ListHighlight(button, "BACKGROUND", 0.48)

    button.name = button:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    button.name:SetPoint("TOPLEFT", 8, -6)
    button.name:SetPoint("RIGHT", -8, 0)
    button.name:SetJustifyH("LEFT")
    button.name:SetWordWrap(false)
    button.name:SetTextColor(1, 1, 1)

    button.state = button:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    button.state:SetPoint("TOPLEFT", 8, -24)
    button.state:SetJustifyH("LEFT")
    button.state:SetWordWrap(false)

    button.count = button:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    button.count:SetPoint("TOPRIGHT", -8, -24)
    button.count:SetJustifyH("RIGHT")
    button.count:SetWordWrap(false)
    button.count:SetTextColor(MUTED[1], MUTED[2], MUTED[3])

    button.barBack = button:CreateTexture(nil, "ARTWORK")
    button.barBack:SetColorTexture(1, 1, 1, 0.10)
    button.barBack:SetHeight(BAR_HEIGHT)
    button.barBack:SetPoint("BOTTOMLEFT", 8, 7)
    button.barBack:SetPoint("BOTTOMRIGHT", -8, 7)
    button.bar = button:CreateTexture(nil, "OVERLAY")
    button.bar:SetHeight(BAR_HEIGHT)
    button.bar:SetPoint("LEFT", button.barBack, "LEFT", 0, 0)

    button:SetScript("OnClick", Choose)
    return button
end

local function CountText(group)
    local parts = {}
    if group.best > 0 then parts[#parts + 1] = L.REP_COUNT_BEST:format(group.best) end
    local alternatives = group.alts + group.other
    if alternatives > 0 then
        parts[#parts + 1] = (alternatives == 1 and L.REP_COUNT_ALT or L.REP_COUNT_ALTS):format(alternatives)
    end
    return table.concat(parts, ", ")
end

-- Earned: every standing this spec has a use for.
local function Earned(group)
    local top = 0
    for standing in pairs(group.steps) do top = math.max(top, standing) end
    return Reputation.Status({ factionID = group.factionID, standing = top }) == "met"
end

local function FillFaction(button, group, chosen)
    button.group = group
    button.selected:SetShown(chosen)
    button.name:SetText(Reputation.FactionName(group.factionID))
    local earned = Earned(group)
    local progress = Reputation.ProgressText(group.factionID, ns:GetOption("repCompact"))
    button.state:SetText((earned and GOLD or GREY) .. progress .. "|r")
    button.count:SetText(CountText(group))
    local width = LIST_WIDTH - BAR_ROOM - 16
    button.bar:SetWidth(math.max(1, math.floor(width * Reputation.Ratio(group.factionID) + 0.5)))
    if earned then
        button.bar:SetColorTexture(1, 0.82, 0, 0.90)
    else
        button.bar:SetColorTexture(0.78, 0.78, 0.82, 0.85)
    end
end

-- Lays the groups and their factions out; the chosen one, or the first, is returned.
local function LayoutFactions(needs, state)
    local titles, buttons = view.titles, view.buttons
    local chosen
    for _, list in ipairs({ needs.own, needs.artisan }) do
        for _, group in ipairs(list) do
            if group.factionID == state.faction and group.artisan == (state.factionArtisan == true) then
                chosen = group
            end
        end
    end
    chosen = chosen or needs.own[1] or needs.artisan[1]

    local offset, used = 0, 0
    for index, part in ipairs({ { L.REP_GROUP_OWN, needs.own }, { L.REP_GROUP_ARTISAN, needs.artisan } }) do
        titles[index]:SetShown(part[2][1] ~= nil)
        if part[2][1] then
            titles[index]:SetText(part[1])
            titles[index]:ClearAllPoints()
            titles[index]:SetPoint("BOTTOMLEFT", view.listChild, "TOPLEFT", 8, -(offset + GROUP_HEIGHT - 6))
            offset = offset + GROUP_HEIGHT
            for _, group in ipairs(part[2]) do
                used = used + 1
                local button = buttons[used]
                if not button then
                    button = CreateFaction(view.listChild)
                    buttons[used] = button
                end
                FillFaction(button, group, group == chosen)
                button:ClearAllPoints()
                button:SetPoint("TOPLEFT", view.listChild, "TOPLEFT", 0, -offset)
                button:Show()
                offset = offset + FACTION_HEIGHT
            end
        end
    end
    for index = used + 1, #buttons do buttons[index]:Hide() end
    view.listChild:SetSize(LIST_WIDTH - BAR_ROOM, math.max(1, offset))
    if view.list.UpdateScrollChildRect then view.list:UpdateScrollChildRect() end
    return chosen
end

---------------------------------------------------------------------------
-- The faction on the right
---------------------------------------------------------------------------

local function EntryTooltip(line)
    local entry = line.data and line.data.entry
    if not entry then return end
    if entry.enchant then
        local info = ns.Enchants.Info(entry.enchant)
        if not info then return end
        Browser.EnchantTooltip(line, info, entry.requirement)
    else
        Browser.ItemTooltip(line, { id = entry.id, source = ns.Sources.Describe(entry.id) })
    end
    Browser.ShowTooltip()
end

local function EntryClick(line)
    local entry = line.data and line.data.entry
    if entry and entry.id then Browser.ModifiedClick(entry.id) end
end

local function CreateLine(parent)
    local line = CreateFrame("Button", nil, parent)
    line:SetWidth(DETAIL_WIDTH)
    line.back = Widgets.ListHighlight(line, "HIGHLIGHT", 0.32)
    line.rule = line:CreateTexture(nil, "BACKGROUND")
    line.rule:SetColorTexture(1, 1, 1, 0.14)
    line.rule:SetHeight(1)
    line.rule:SetPoint("BOTTOMLEFT", 0, 2)
    line.rule:SetPoint("BOTTOMRIGHT", 0, 2)
    line.icon = line:CreateTexture(nil, "ARTWORK")
    line.icon:SetSize(ICON, ICON)
    line.icon:SetPoint("LEFT", 14, 0)
    line.badge = line:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    line.badge:SetPoint("TOPLEFT", 4, -3)
    line.badge:SetWidth(BADGE_WIDTH)
    line.badge:SetJustifyH("LEFT")
    line.text = line:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    line.text:SetJustifyH("LEFT")
    line.place = line:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    line.place:SetPoint("RIGHT", -64, 0)
    line.place:SetJustifyH("RIGHT")
    line.place:SetWordWrap(false)
    line.place:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    line.right = line:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    line.right:SetPoint("RIGHT", -6, 0)
    line.right:SetJustifyH("RIGHT")
    line:SetScript("OnEnter", EntryTooltip)
    line:SetScript("OnLeave", function() GameTooltip:Hide() end)
    line:SetScript("OnClick", EntryClick)
    return line
end

local function FillLine(line, data)
    line.data = data
    local kind = data.kind
    local entry, way = kind == "entry", kind == "way"
    line:EnableMouse(entry)
    line.back:SetShown(entry)
    line.rule:SetShown(kind == "section")
    line.icon:SetShown(entry)
    line.badge:SetShown(way)
    line.place:SetShown(entry)
    line.right:SetShown(data.right ~= nil)
    line.right:SetText(data.right or "")

    line.text:ClearAllPoints()
    line.text:SetWidth(0)   -- a line is used again for another kind of line
    line.text:SetText(data.text)
    line.text:SetTextColor(1, 1, 1)
    line.text:SetWordWrap(way or kind == "text")
    local height = HEIGHTS[kind]
    if kind == "section" then
        line.text:SetPoint("BOTTOMLEFT", 0, 6)
        line.text:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    elseif kind == "step" then
        line.text:SetPoint("LEFT", 4, 0)
    elseif entry then
        line.icon:SetTexture(EntryIcon(data.entry))
        line.place:SetText(data.place)
        line.text:SetPoint("LEFT", line.icon, "RIGHT", 6, 0)
        line.text:SetPoint("RIGHT", line.place, "LEFT", -8, 0)
    elseif way then
        line.badge:SetText(EVIDENCE[data.evidence] .. L["REP_EVIDENCE_" .. data.evidence] .. "|r")
        line.text:SetPoint("TOPLEFT", BADGE_WIDTH + 8, -3)
        line.text:SetWidth(DETAIL_WIDTH - BADGE_WIDTH - 12)
        height = math.max(height, math.ceil(line.text:GetStringHeight()) + 6)
    else
        line.text:SetPoint("TOPLEFT", 4, -3)
        line.text:SetWidth(DETAIL_WIDTH - 8)
        height = math.max(height, math.ceil(line.text:GetStringHeight()) + 6)
    end
    line:SetHeight(height)
    return height
end

local function ShowDetail(group)
    view.title:SetText(Reputation.FactionName(group.factionID))
    local earned = Earned(group)
    view.you:SetText((earned and GOLD or GREY) .. L.REP_YOU:format(Reputation.ProgressText(group.factionID)) .. "|r")

    local data = DetailLines(group)
    local offset = 0
    for index, lineData in ipairs(data) do
        local line = view.lines[index]
        if not line then
            line = CreateLine(view.detailChild)
            view.lines[index] = line
        end
        local height = FillLine(line, lineData)
        line:ClearAllPoints()
        line:SetPoint("TOPLEFT", view.detailChild, "TOPLEFT", 0, -offset)
        line:Show()
        offset = offset + height
    end
    for index = #data + 1, #view.lines do view.lines[index]:Hide() end
    view.detailChild:SetSize(DETAIL_WIDTH, math.max(1, offset))
    if view.detail.UpdateScrollChildRect then view.detail:UpdateScrollChildRect() end
    view.detailData = data
end

---------------------------------------------------------------------------
-- The view
---------------------------------------------------------------------------

function ReputationView.Create(parent)
    if view then return view end
    view = CreateFrame("Frame", nil, parent)
    ReputationView.view = view
    view:SetPoint("TOPLEFT", parent, "TOPLEFT", PAD, -PAD)
    view:SetPoint("BOTTOMRIGHT", parent, "BOTTOMRIGHT", -PAD, PAD)
    view:Hide()
    view.buttons, view.lines = {}, {}

    view.list, view.listChild = Widgets.Scroll(view)
    view.list:SetPoint("TOPLEFT", 0, 0)
    view.list:SetPoint("BOTTOMLEFT", 0, 0)
    view.list:SetWidth(LIST_WIDTH - BAR_ROOM)
    view.titles = { CreateGroupTitle(view.listChild), CreateGroupTitle(view.listChild) }

    view.divider = view:CreateTexture(nil, "BACKGROUND")
    view.divider:SetColorTexture(1, 1, 1, 0.08)
    view.divider:SetWidth(1)
    view.divider:SetPoint("TOPLEFT", LIST_WIDTH + 2, 0)
    view.divider:SetPoint("BOTTOMLEFT", LIST_WIDTH + 2, 0)

    view.title = view:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    view.title:SetPoint("TOPLEFT", LIST_WIDTH + 14, -2)
    view.title:SetTextColor(1, 1, 1)
    view.you = view:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    view.you:SetPoint("TOPLEFT", view.title, "BOTTOMLEFT", 0, -4)

    view.detail, view.detailChild = Widgets.Scroll(view)
    view.detail:SetPoint("TOPLEFT", LIST_WIDTH + 14, -44)
    view.detail:SetPoint("BOTTOMRIGHT", -BAR_ROOM, 0)

    view.empty = view:CreateFontString(nil, "OVERLAY", "GameFontDisable")
    view.empty:SetPoint("TOP", 0, -40)
    view.empty:SetText(L.REP_NONE)
    return view
end

function ReputationView.Hide()
    if view then view:Hide() end
end

function ReputationView.Update(state)
    if not view then return end
    view:Show()
    local needs = Reputation.Needs(state.class, state.spec, state.list)
    view.factionData = needs
    local chosen = LayoutFactions(needs, state)
    local any = chosen ~= nil
    view.empty:SetShown(not any)
    view.list:SetShown(any)
    view.detail:SetShown(any)
    view.divider:SetShown(any)
    view.title:SetShown(any)
    view.you:SetShown(any)
    view.chosen = chosen
    if chosen then
        ShowDetail(chosen)
    else
        view.detailData = {}
    end
end
