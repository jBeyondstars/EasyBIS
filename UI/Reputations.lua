local _, ns = ...
local L = ns.L
local Widgets = ns.Widgets
local Browser = ns.Browser
local Reputation = ns.Reputation

--[[
The Reputations tab of the window: what the spec, the list and the phase ask of each faction.

  left     the factions, most wanted first: the player's own, then the crafters' recipes, which are kept apart
           and counted in nobody's total. Each shows the pieces it opens, how many are best or alternatives, and
           a bar of the whole way from Neutral to Exalted with a mark where each piece unlocks.
  right    the faction chosen, from top to bottom:
             the track     the way from Neutral to Exalted, each standing as wide as the reputation it asks, the
                           player's place on it and each piece above the standing that unlocks it. A piece's
                           tooltip is the item's; a click opens its slot in the Items tab, Shift-click links it
             the cards     what is left for the next standing a piece needs, what the quests done once give at
                           most, how many quests repeat
             the sections  the pieces, where they come from (a vendor whose place is known has a Map button), the
                           quests kept for the class, and what no source says. A click on a title folds it
           The header has a Watch button: the game's reputation bar follows the faction.

A crafter's recipes show what the faction sells: the recipe, and the piece it makes. When the profession is not
the player's, the reputation is the crafter's: a banner says how to get the pieces instead (the auction house when
they bind when equipped), the player's place and the gold are left out, and the quests are folded. When it is
theirs, the header says their skill against the most the recipes ask.

Gold is for what the player has earned: a reached standing, a piece within reach. The faction chosen is lit in
blue. The rest of the colour is the game's own art: the status bar texture on the ways, the tooltip frame on the
cards, soft bands under the header, the sections and the factions, every other line lighter, an icon per section.
Nothing here says how long a standing takes: nothing measures it.

  ReputationView.Create(parent)   the view, hidden
  ReputationView.Update(state)    fills it. state: the window's { class, spec, list, faction, factionArtisan }
  ReputationView.Hide()
  ReputationView.view             (the tests read it: factionData, detailData, cardData, buttons, lines, pieces,
                                  cards, banner, title, you, watch, empty)
]]

local ReputationView = {}
ns.ReputationView = ReputationView

local LIST_WIDTH = 292        -- the factions, their scroll bar included
local BAR_ROOM = 26           -- what a scroll bar takes
local DETAIL_WIDTH = 592      -- the faction's side
local PAD = 8
local GROUP_HEIGHT = 30       -- a group's name over its factions
local FACTION_HEIGHT = 72     -- a faction in the list
local MINI = 18               -- a piece's icon in the list
local MINI_SHOWN = 4
local LIST_BAR = 5
local TRACK_INSET = 16        -- room for a piece at either end of the track
local TRACK_HEIGHT = 10
local PIECE = 30              -- a piece on the track
local PIECE_GAP = 4
local TRACK_BLOCK = PIECE + 8 + TRACK_HEIGHT + 24
local CARD_HEIGHT = 64
local CARD_GAP = 8
local ICON = 24
local HEIGHTS = { section = 34, entry = 30, seller = 26, quest = 22, note = 22 }
local UNKNOWN_ICON = "Interface\\Icons\\INV_Misc_QuestionMark"
local STATUS_BAR = "Interface\\TargetingFrame\\UI-StatusBar"
local SECTION_ICONS = {
    sources = "Interface\\Icons\\INV_Misc_Bag_08",
    quests = "Interface\\Icons\\INV_Misc_Note_01",
    unknown = UNKNOWN_ICON,
}
local SELLER_ICONS = {
    vendor = "Interface\\GossipFrame\\VendorGossipIcon",
    other = "Interface\\GossipFrame\\GossipGossipIcon",
}

-- The rows' fonts of the other tabs: the game's, two points larger.
local FONTS = Browser.FONTS

local MUTED = Widgets.MUTED
local GOLD, WHITE, GREY = "|cffffd100", "|cffffffff", "|cffa8a8b0"
local GOLD_RGB = { 1, 0.82, 0 }
local GREEN = { 0.12, 0.62, 0.22 }       -- the way travelled, before every piece is earned
local SELECTED = { 0.35, 0.60, 1.00 }    -- the faction chosen: not gold, which is for what is earned
local SLATE = { 0.20, 0.23, 0.30 }       -- the way still to go
local TEAL = { 0.25, 0.70, 0.75 }        -- what the data says
local DOTS = { data = { 0.56, 0.82, 0.62 }, check = { 0.94, 0.60, 0.33 }, unknown = { 0.66, 0.66, 0.70 } }
local THRESHOLDS = Reputation.THRESHOLDS
local WHOLE_WAY = THRESHOLDS[7]

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

local view
local folded = {}             -- [section] = true: the sections the player folded, for the session

local function Number(value)
    if BreakUpLargeNumbers then return BreakUpLargeNumbers(value) end
    return tostring(value)
end

local function HasTemplate(name)
    return C_XMLUtil ~= nil and C_XMLUtil.GetTemplateInfo ~= nil and C_XMLUtil.GetTemplateInfo(name) ~= nil
end

-- A soft band of colour fading out to the right (or downwards), on any client: the newer gradient takes colours,
-- the older one numbers; without either, an even tint.
local function Band(texture, orientation, r, g, b, from, to)
    texture:SetTexture("Interface\\Buttons\\WHITE8x8")
    if texture.SetGradient and CreateColor
        and pcall(texture.SetGradient, texture, orientation, CreateColor(r, g, b, from), CreateColor(r, g, b, to)) then
        return
    end
    if texture.SetGradientAlpha then
        texture:SetGradientAlpha(orientation, r, g, b, from, r, g, b, to)
    else
        texture:SetColorTexture(r, g, b, (from + to) / 2)
    end
end

---------------------------------------------------------------------------
-- The pieces
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

local function EntryQuality(entry)
    if entry.enchant or not GetInfo then return 1, 1, 1 end
    local _, _, quality = GetInfo(entry.id)
    local r, g, b = ns.QualityColor(quality)
    return r, g, b
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

local function EntryPlace(entry)
    local requirement = entry.requirement
    local place = entry.enchant and ns.Enchants.KeyName(entry.slot) or ns.SlotName(entry.slot)
    if requirement.kind == Reputation.QUEST then return place .. ", " .. L.REP_KIND_QUEST end
    if requirement.profession then
        return place .. ", " .. ns.ProfessionName(requirement.profession)
            .. (requirement.skill and (" " .. requirement.skill) or "")
    end
    return place
end

-- What a crafter's faction sells: the recipe, in its quality's colour.
local function RecipeName(entry)
    local requirement = entry.requirement
    local name, quality, _
    if requirement.recipe and GetInfo then name, _, quality = GetInfo(requirement.recipe) end
    local _, _, _, hex = ns.QualityColor(quality)
    return hex .. (name or Reputation.RecipeName(requirement) or L.REP_UNKNOWN) .. "|r"
end

local function RecipeIcon(entry)
    local recipe = entry.requirement.recipe
    local texture
    if recipe and GetInfo then texture = select(10, GetInfo(recipe)) end
    return texture or (recipe and GetIcon and GetIcon(recipe)) or EntryIcon(entry)
end

-- The professions a group's recipes ask, in the game's language.
local function CraftNames(group)
    local names = {}
    for _, craft in ipairs((Reputation.Crafts(group))) do names[#names + 1] = ns.ProfessionName(craft.profession) end
    return table.concat(names, ", ")
end

-- The player's skill in each of the group's professions that is theirs, against the most its recipes ask: gold
-- once reached.
local function CraftSkills(group)
    local parts = {}
    for _, craft in ipairs((Reputation.Crafts(group))) do
        if craft.status == "crafter" then
            parts[#parts + 1] = ((craft.rank or 0) >= craft.skill and GOLD or WHITE)
                .. L.REP_CRAFT_SKILL:format(ns.ProfessionName(craft.profession), craft.rank or 0, craft.skill) .. "|r"
        end
    end
    return table.concat(parts, GREY .. ", " .. "|r")
end

-- What makes the pieces when the reputation is the crafter's: one word for a single profession.
local function CrafterNoun(group)
    local single
    for _, craft in ipairs((Reputation.Crafts(group))) do
        if craft.profession ~= "Enchanting" then
            if single then return L.REP_CRAFTER end
            single = craft.profession
        end
    end
    local key = single and ("REP_CRAFTER_" .. single)
    local noun = key and L[key]
    return (noun and noun ~= key) and noun or L.REP_CRAFTER
end

-- A crafter's recipes of a profession the player does not have: the reputation is the crafter's, not theirs.
local function ForOthers(group)
    return group.artisan == true and group.craftStatus == "other"
end

-- Reached, for the player: never for a reputation that is the crafter's.
local function Met(group, standing)
    if ForOthers(group) then return false end
    return Reputation.Status({ factionID = group.factionID, standing = standing }) == "met"
end

-- The standings this spec has a use for, lowest first.
local function Targets(group)
    local targets = {}
    for _, standing in ipairs(Reputation.STANDINGS) do
        if group.steps[standing] then targets[#targets + 1] = standing end
    end
    return targets
end

-- Every piece in standing order, the best first within a standing.
local function Entries(group)
    local entries = {}
    for _, standing in ipairs(Targets(group)) do
        local step = {}
        for _, entry in ipairs(group.steps[standing]) do step[#step + 1] = entry end
        table.sort(step, function(a, b) return (a.role == "best") and b.role ~= "best" end)
        for _, entry in ipairs(step) do entries[#entries + 1] = entry end
    end
    return entries
end

local function Earned(group)
    local targets = Targets(group)
    return targets[1] ~= nil and Met(group, targets[#targets])
end

local function PieceTooltip(owner, entry)
    if not entry then return end
    if entry.enchant then
        local info = ns.Enchants.Info(entry.enchant)
        if not info then return end
        Browser.EnchantTooltip(owner, info, entry.requirement)
    else
        Browser.ItemTooltip(owner, { id = entry.id, source = ns.Sources.Describe(entry.id),
            reputation = entry.requirement })
        GameTooltip:AddLine(L.REP_PIECE_TIP, MUTED[1], MUTED[2], MUTED[3], true)
    end
    Browser.ShowTooltip()
end

-- A recipe's own tooltip, then what it makes and what it asks.
local function RecipeTooltip(owner, entry)
    local requirement = entry.requirement
    if not requirement.recipe then return PieceTooltip(owner, entry) end
    Browser.PlaceTooltip(owner)
    pcall(GameTooltip.SetItemByID, GameTooltip, requirement.recipe)
    if GameTooltip:NumLines() == 0 then GameTooltip:SetText(Reputation.RecipeName(requirement) or "", 1, 1, 1) end
    GameTooltip:AddLine(L.REP_TIP_MAKES:format(EntryName(entry)), 1, 1, 1, true)
    GameTooltip:AddLine(L.REP_TIP_NEED:format(Reputation.NeedText(requirement)), 1, 1, 1, true)
    local state = Reputation.Crafter(requirement) == "other"
        and L.REP_CRAFT_NOT_YOURS:format(ns.ProfessionName(requirement.profession)) or Reputation.StateText(requirement)
    GameTooltip:AddLine(state, MUTED[1], MUTED[2], MUTED[3], true)
    if entry.id then GameTooltip:AddLine(L.REP_PIECE_TIP, MUTED[1], MUTED[2], MUTED[3], true) end
    Browser.ShowTooltip()
end

-- Shift-click links the item; a click opens its slot among the items.
local function PieceClick(entry)
    if not entry or Browser.ModifiedClick(entry.id) then return end
    if entry.id then
        Widgets.Click()
        Browser.ShowSlot(entry.slot)
    end
end

---------------------------------------------------------------------------
-- The way from Neutral to Exalted
---------------------------------------------------------------------------

local function At(width, value)
    return math.floor(width * math.max(0, math.min(WHOLE_WAY, value)) / WHOLE_WAY + 0.5)
end

-- Four segments, one per standing to reach, each as wide as the reputation it asks.
local function CreateWay(parent, width, height)
    local way = { width = width, segments = {}, marks = {} }
    for index = 1, 4 do
        local from, to = THRESHOLDS[index + 2], THRESHOLDS[index + 3]
        local segment = parent:CreateTexture(nil, "BORDER")
        segment:SetTexture(STATUS_BAR)
        segment:SetVertexColor(SLATE[1], SLATE[2], SLATE[3], 1)
        segment:SetHeight(height)
        local left = At(width, from) + (index > 1 and 1 or 0)
        segment:SetWidth(math.max(1, At(width, to) - left - (index < 4 and 1 or 0)))
        way.segments[index] = segment
        segment.left = left
    end
    way.fill = parent:CreateTexture(nil, "ARTWORK")
    way.fill:SetTexture(STATUS_BAR)
    way.fill:SetHeight(height)
    return way
end

local function PlaceWay(way, anchor, x, y)
    for _, segment in ipairs(way.segments) do
        segment:ClearAllPoints()
        segment:SetPoint("TOPLEFT", anchor, "TOPLEFT", x + segment.left, y)
    end
    way.fill:ClearAllPoints()
    way.fill:SetPoint("TOPLEFT", anchor, "TOPLEFT", x, y)
end

-- The player's place on the way: green on the way, gold once every piece is earned.
local function FillWay(way, group)
    local position = not ForOthers(group) and Reputation.Position(group.factionID) or nil
    local width = position and At(way.width, position) or 0
    way.fill:SetShown(width > 0)
    way.fill:SetWidth(math.max(1, width))
    local color = Earned(group) and GOLD_RGB or GREEN
    way.fill:SetVertexColor(color[1], color[2], color[3], 1)
    way.position = position
end

-- A mark on the way where a standing this spec needs begins: gold once reached.
local function Mark(way, parent, index, x, y, height)
    local mark = way.marks[index]
    if not mark then
        mark = parent:CreateTexture(nil, "OVERLAY")
        way.marks[index] = mark
    end
    mark:ClearAllPoints()
    mark:SetSize(2, height)
    mark:SetPoint("TOPLEFT", parent, "TOPLEFT", x - 1, y)
    mark:Show()
    return mark
end

local function MarkColor(mark, reached)
    if reached then
        mark:SetColorTexture(GOLD_RGB[1], GOLD_RGB[2], GOLD_RGB[3], 1)
    else
        mark:SetColorTexture(1, 1, 1, 0.75)
    end
end

---------------------------------------------------------------------------
-- The factions on the left
---------------------------------------------------------------------------

local function Choose(button)
    Widgets.Click()
    Browser.ShowReputation(button.group.factionID, button.group.artisan)
end

local function CreateGroupTitle(parent)
    local title = parent:CreateFontString(nil, "OVERLAY", FONTS.text)
    title:SetJustifyH("LEFT")
    title:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    return title
end

local function CreateChip(parent, r, g, b)
    local chip = parent:CreateTexture(nil, "ARTWORK")
    chip:SetColorTexture(r, g, b, 0.18)
    chip.text = parent:CreateFontString(nil, "OVERLAY", FONTS.text)
    chip.text:SetPoint("CENTER", chip, "CENTER", 0, 0)
    chip.text:SetTextColor(r, g, b)
    return chip
end

local function SetChip(chip, text)
    chip:SetShown(text ~= nil)
    chip.text:SetShown(text ~= nil)
    if not text then return 0 end
    chip.text:SetText(text)
    local width = math.ceil(chip.text:GetStringWidth()) + 10
    chip:SetSize(width, 17)
    return width
end

local function CreateFaction(parent)
    local width = LIST_WIDTH - BAR_ROOM
    local button = CreateFrame("Button", nil, parent)
    button:SetSize(width, FACTION_HEIGHT - 2)
    button.band = button:CreateTexture(nil, "BACKGROUND", nil, -1)
    button.band:SetAllPoints()
    Band(button.band, "HORIZONTAL", 1, 1, 1, 0.07, 0)
    button.rule = button:CreateTexture(nil, "BACKGROUND")
    button.rule:SetColorTexture(1, 1, 1, 0.06)
    button.rule:SetHeight(1)
    button.rule:SetPoint("BOTTOMLEFT", 0, -1)
    button.rule:SetPoint("BOTTOMRIGHT", 0, -1)
    Widgets.ListHighlight(button, "HIGHLIGHT", 0.32)
    button.selected = Widgets.ListHighlight(button, "BACKGROUND", 0.55)
    button.selected:SetDesaturated(true)   -- grey first: blue over the highlight's yellow turns green
    button.selected:SetVertexColor(SELECTED[1], SELECTED[2], SELECTED[3])

    button.name = button:CreateFontString(nil, "OVERLAY", FONTS.name)
    button.name:SetJustifyH("LEFT")
    button.name:SetWordWrap(false)
    button.name:SetTextColor(1, 1, 1)

    button.icons = {}
    for index = 1, MINI_SHOWN do
        local icon = button:CreateTexture(nil, "ARTWORK")
        icon:SetSize(MINI, MINI)
        icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
        icon:SetPoint("TOPRIGHT", -8 - (index - 1) * (MINI + 2), -6)
        button.icons[index] = icon
    end

    button.state = button:CreateFontString(nil, "OVERLAY", FONTS.text)
    button.state:SetPoint("TOPLEFT", 8, -32)
    button.state:SetJustifyH("LEFT")
    button.state:SetWordWrap(false)

    button.altChip = CreateChip(button, MUTED[1], MUTED[2], MUTED[3])
    button.bestChip = CreateChip(button, 1, 1, 1)

    button.way = CreateWay(button, width - 16, LIST_BAR)
    PlaceWay(button.way, button, 8, -(FACTION_HEIGHT - 2 - 13))

    button:SetScript("OnClick", Choose)
    return button
end

local function FillFaction(button, group, chosen)
    button.group = group
    button.selected:SetShown(chosen)

    local entries = Entries(group)
    local shown = math.min(MINI_SHOWN, #entries)
    for index, icon in ipairs(button.icons) do
        local entry = entries[index]
        icon:SetShown(index <= shown)
        if index <= shown then icon:SetTexture(EntryIcon(entry)) end
    end
    button.name:ClearAllPoints()
    button.name:SetPoint("TOPLEFT", 8, -8)
    button.name:SetPoint("RIGHT", button, "RIGHT", -12 - shown * (MINI + 2), 0)
    button.name:SetText(Reputation.FactionName(group.factionID) .. Reputation.UnknownMark(group))

    local earned = Earned(group)
    if ForOthers(group) then
        button.state:SetText(GREY .. CraftNames(group) .. "|r")   -- whose reputation counts
    else
        button.state:SetText((earned and GOLD or GREY) .. Reputation.ProgressText(group.factionID, true) .. "|r")
    end

    local alternatives = group.alts + group.other
    local altWidth = SetChip(button.altChip, alternatives > 0 and (alternatives .. " " .. L.RANK_ALT:lower()) or nil)
    local bestWidth = SetChip(button.bestChip, group.best > 0 and (group.best .. " " .. L.RANK_BIS) or nil)
    local chips = altWidth + bestWidth + ((altWidth > 0 and bestWidth > 0) and 4 or 0)
    button.state:SetWidth(math.max(40, LIST_WIDTH - BAR_ROOM - 24 - chips))
    button.altChip:ClearAllPoints()
    button.altChip:SetPoint("TOPRIGHT", -8, -30)
    button.bestChip:ClearAllPoints()
    button.bestChip:SetPoint("TOPRIGHT", -8 - (altWidth > 0 and (altWidth + 4) or 0), -30)

    local way = button.way
    FillWay(way, group)
    local used = 0
    for _, standing in ipairs(Targets(group)) do
        if standing > Reputation.NEUTRAL then
            used = used + 1
            local mark = Mark(way, button, used, 8 + At(way.width, THRESHOLDS[standing]), -(FACTION_HEIGHT - 2 - 15),
                LIST_BAR + 4)
            MarkColor(mark, Met(group, standing))
        end
    end
    for index = used + 1, #way.marks do way.marks[index]:Hide() end
end

-- The scroll bar shows only when there is something to scroll, once the frame has its size.
local function Fit(scroll, child, width, height)
    child:SetSize(width, math.max(1, height))
    if scroll.UpdateScrollChildRect then scroll:UpdateScrollChildRect() end
    local bar, room = scroll.ScrollBar, scroll:GetHeight()
    if bar and room and room > 0 then
        local needed = height > room + 1
        bar:SetShown(needed)
        if not needed and scroll.SetVerticalScroll then scroll:SetVerticalScroll(0) end
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
    Fit(view.list, view.listChild, LIST_WIDTH - BAR_ROOM, offset)
    return chosen
end

---------------------------------------------------------------------------
-- The track: the way, the player on it, the pieces above it
---------------------------------------------------------------------------

local function CreatePiece(parent)
    local piece = CreateFrame("Button", nil, parent, "BackdropTemplate")
    piece:SetSize(PIECE, PIECE)
    piece:SetBackdrop(Widgets.FLAT)
    piece:SetBackdropColor(0, 0, 0, 0.6)
    piece.icon = piece:CreateTexture(nil, "ARTWORK")
    piece.icon:SetPoint("TOPLEFT", 2, -2)
    piece.icon:SetPoint("BOTTOMRIGHT", -2, 2)
    piece.icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
    local highlight = piece:CreateTexture(nil, "HIGHLIGHT")
    highlight:SetTexture("Interface\\Buttons\\ButtonHilight-Square")
    highlight:SetBlendMode("ADD")
    highlight:SetAllPoints()
    -- a recipe's piece wears its profession in a corner
    piece.craft = piece:CreateTexture(nil, "OVERLAY", nil, 1)
    piece.craft:SetSize(14, 14)
    piece.craft:SetPoint("BOTTOMRIGHT", 3, -3)
    piece.craft:SetTexCoord(0.07, 0.93, 0.07, 0.93)
    piece.check = piece:CreateTexture(nil, "OVERLAY")
    piece.check:SetTexture("Interface\\Buttons\\UI-CheckBox-Check")
    piece.check:SetSize(18, 18)
    piece.check:SetPoint("TOPRIGHT", 7, 7)
    piece:SetScript("OnEnter", function(self) PieceTooltip(self, self.entry) end)
    piece:SetScript("OnLeave", function() GameTooltip:Hide() end)
    piece:SetScript("OnClick", function(self) PieceClick(self.entry) end)
    return piece
end

local function CreateTrack(parent)
    local track = CreateFrame("Frame", nil, parent)
    track:SetSize(DETAIL_WIDTH, TRACK_BLOCK)
    track.way = CreateWay(track, DETAIL_WIDTH - 2 * TRACK_INSET, TRACK_HEIGHT)
    PlaceWay(track.way, track, TRACK_INSET, -(PIECE + 8))
    track.labels = {}
    for standing = 4, 7 do
        local label = track:CreateFontString(nil, "OVERLAY", FONTS.text)
        local x = TRACK_INSET + At(track.way.width, THRESHOLDS[standing])
        if standing == 7 then
            label:SetPoint("TOPRIGHT", track, "TOPLEFT", x, -(PIECE + 8 + TRACK_HEIGHT + 4))
        else
            label:SetPoint("TOP", track, "TOPLEFT", x, -(PIECE + 8 + TRACK_HEIGHT + 4))
        end
        track.labels[standing] = label
    end
    track.pieces = {}
    -- where the player stands: a white post, outlined so it shows on the green and on the slate
    track.youBack = track:CreateTexture(nil, "OVERLAY", nil, 1)
    track.youBack:SetColorTexture(0, 0, 0, 0.9)
    track.youBack:SetSize(5, TRACK_HEIGHT + 8)
    track.you = track:CreateTexture(nil, "OVERLAY", nil, 2)
    track.you:SetColorTexture(1, 1, 1, 1)
    track.you:SetSize(3, TRACK_HEIGHT + 6)
    return track
end

-- Each standing's pieces side by side above where it begins, pushed right when they would cover the
-- previous standing's.
local function FillTrack(group)
    local track = view.track
    local way = track.way
    FillWay(way, group)
    track.you:SetShown(way.position ~= nil)
    track.youBack:SetShown(way.position ~= nil)
    if way.position then
        local x = TRACK_INSET + At(way.width, way.position)
        for _, post in ipairs({ track.youBack, track.you }) do
            post:ClearAllPoints()
            post:SetPoint("CENTER", track, "TOPLEFT", x, -(PIECE + 8 + TRACK_HEIGHT / 2))
        end
    end
    for standing, label in pairs(track.labels) do
        label:SetText(Reputation.StandingName(standing))
        local color = Met(group, standing) and GOLD_RGB or MUTED
        label:SetTextColor(color[1], color[2], color[3])
    end

    local used, marks, right = 0, 0, -TRACK_INSET - PIECE_GAP
    view.pieces = {}
    for _, standing in ipairs(Targets(group)) do
        local entries = {}
        for _, entry in ipairs(Entries(group)) do
            if entry.requirement.standing == standing then entries[#entries + 1] = entry end
        end
        local reached = Met(group, standing)
        local x = At(way.width, THRESHOLDS[standing])
        local span = #entries * PIECE + (#entries - 1) * PIECE_GAP
        local left = math.max(-TRACK_INSET, math.min(way.width + TRACK_INSET - span, x - span / 2))
        left = math.max(left, right + PIECE_GAP)
        for index, entry in ipairs(entries) do
            used = used + 1
            local piece = track.pieces[used]
            if not piece then
                piece = CreatePiece(track)
                track.pieces[used] = piece
            end
            piece.entry = entry
            piece.icon:SetTexture(EntryIcon(entry))
            local r, g, b = EntryQuality(entry)
            piece:SetBackdropBorderColor(r, g, b, 1)
            piece.check:SetShown(reached)
            local profession = entry.requirement.kind == Reputation.RECIPE and entry.requirement.profession
            piece.craft:SetShown(profession and true or false)
            if profession then piece.craft:SetTexture((ns.Sources.Icon("crafted", profession))) end
            piece:ClearAllPoints()
            piece:SetPoint("TOPLEFT", track, "TOPLEFT", TRACK_INSET + left + (index - 1) * (PIECE + PIECE_GAP), 0)
            piece:Show()
            view.pieces[used] = piece
        end
        right = left + span
        marks = marks + 1
        local mark = Mark(way, track, marks, TRACK_INSET + x, -(PIECE + 2), TRACK_HEIGHT + 10)
        MarkColor(mark, reached)
    end
    for index = used + 1, #track.pieces do track.pieces[index]:Hide() end
    for index = marks + 1, #way.marks do way.marks[index]:Hide() end
end

---------------------------------------------------------------------------
-- The cards: three numbers, each said only when a source gives it
---------------------------------------------------------------------------

-- The game's tooltip frame where the client has it; the accent says what the number is: green the way, teal the
-- data's quests.
local function CreateCard(parent, accent)
    local card
    if HasTemplate("TooltipBackdropTemplate") then
        card = CreateFrame("Frame", nil, parent, "TooltipBackdropTemplate")
    else
        card = CreateFrame("Frame", nil, parent, "BackdropTemplate")
        card:SetBackdrop(Widgets.FLAT)
        card:SetBackdropColor(0.05, 0.06, 0.09, 0.85)
        card:SetBackdropBorderColor(1, 1, 1, 0.14)
    end
    card.accent = card:CreateTexture(nil, "ARTWORK")
    card.accent:SetHeight(2)
    card.accent:SetPoint("TOPLEFT", 4, -4)
    card.accent:SetPoint("TOPRIGHT", -4, -4)
    card.accent:SetColorTexture(accent[1], accent[2], accent[3], 0.9)
    card.glow = card:CreateTexture(nil, "BACKGROUND", nil, 1)
    card.glow:SetPoint("TOPLEFT", 4, -6)
    card.glow:SetPoint("TOPRIGHT", -4, -6)
    card.glow:SetHeight(CARD_HEIGHT / 2)
    Band(card.glow, "VERTICAL", accent[1], accent[2], accent[3], 0, 0.10)
    card.label = card:CreateFontString(nil, "OVERLAY", FONTS.text)
    card.label:SetPoint("TOPLEFT", 10, -10)
    card.label:SetPoint("RIGHT", -10, 0)
    card.label:SetJustifyH("LEFT")
    card.label:SetWordWrap(false)
    card.label:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    card.value = card:CreateFontString(nil, "OVERLAY", FONTS.header)
    card.value:SetPoint("TOPLEFT", card.label, "BOTTOMLEFT", 0, -4)
    card.note = card:CreateFontString(nil, "OVERLAY", FONTS.text)
    card.note:SetPoint("BOTTOMLEFT", 10, 8)
    card.note:SetPoint("RIGHT", -10, 0)
    card.note:SetJustifyH("LEFT")
    card.note:SetWordWrap(false)
    card.note:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    return card
end

-- { { label, value, note }, ... }: what is left, the quests done once, the repeatable ones.
local function CardData(group, ways)
    local targets = Targets(group)
    local top = targets[#targets]
    local left = { label = L.REP_LEFT:format(Reputation.StandingName(top)), value = WHITE .. L.REP_UNKNOWN .. "|r" }
    local known = true
    for _, standing in ipairs(targets) do
        local amount, fromNeutral = Reputation.Remaining(group.factionID, standing)
        if amount == nil then
            known = false
            break
        end
        if amount > 0 then
            left.label = L.REP_LEFT:format(Reputation.StandingName(standing))
            left.value = WHITE .. Number(amount) .. "|r"
            left.note = fromNeutral and L.REP_LEFT_FROM_NEUTRAL or nil
            break
        end
    end
    if known and Earned(group) then left.value = GOLD .. L.REP_LEFT_DONE .. "|r" end

    local once = { label = L.REP_CARD_ONCE, value = WHITE .. L.REP_UNKNOWN .. "|r" }
    local repeats = { label = L.REP_CARD_REPEAT, value = WHITE .. L.REP_UNKNOWN .. "|r" }
    if ways.listed > 0 then
        once.value = WHITE .. Number(ways.once) .. "|r"
        once.note = L.REP_CARD_ONCE_NOTE:format(Number(THRESHOLDS[top]), Reputation.StandingName(top))
        repeats.value = WHITE .. Number(ways.repeatable) .. "|r"
        repeats.note = L.REP_CARD_REPEAT_NOTE:format(ways.listed)
    end
    return { left, once, repeats }
end

-- In place of the cards when the reputation is the crafter's: how to get the pieces.
local function CreateBanner(parent)
    local banner = CreateCard(parent, MUTED)
    banner.value:Hide()
    banner.note:Hide()
    banner.text = banner:CreateFontString(nil, "OVERLAY", FONTS.text)
    banner.text:SetPoint("TOPLEFT", banner.label, "BOTTOMLEFT", 0, -6)
    banner.text:SetWidth(DETAIL_WIDTH - 20)
    banner.text:SetJustifyH("LEFT")
    banner.text:SetWordWrap(true)
    banner.text:SetTextColor(1, 1, 1)
    return banner
end

local BANNERS = { equip = "REP_BANNER_EQUIP", none = "REP_BANNER_EQUIP", pickup = "REP_BANNER_PICKUP",
    mixed = "REP_BANNER_MIXED" }

-- What the banner says: how the pieces bind, as the game tells it, and the enchants an enchanter puts on.
local function BannerText(group)
    local bindings, enchants, scroll = {}, false, false
    for _, entry in ipairs(Entries(group)) do
        if entry.enchant then
            enchants, scroll = true, scroll or entry.requirement.scroll == true
        else
            local binding = Reputation.Binding(entry.id) or "unknown"
            if binding == "none" then binding = "equip" end
            bindings[#bindings + 1] = binding
        end
    end
    local sentences = {}
    if bindings[1] then
        local kind = bindings[1]
        for _, binding in ipairs(bindings) do
            if binding ~= kind then
                kind = (kind == "unknown" or binding == "unknown") and "unknown" or "mixed"
                if kind == "unknown" then break end
            end
        end
        sentences[#sentences + 1] = L[BANNERS[kind] or "REP_BANNER_UNKNOWN"]:format(CrafterNoun(group))
    end
    if enchants then sentences[#sentences + 1] = scroll and L.REP_BANNER_ENCHANT_SCROLL or L.REP_BANNER_ENCHANT end
    return table.concat(sentences, " ")
end

-- The cards, or the banner; returns the height they take.
local function FillCards(group, ways)
    local others = ForOthers(group)
    view.banner:SetShown(others)
    for _, card in ipairs(view.cards) do card:SetShown(not others) end
    if others then
        local banner, text = view.banner, BannerText(group)
        banner.label:SetText(L.REP_BANNER_TITLE)
        banner.text:SetText(text)
        local height = math.max(CARD_HEIGHT, 10 + 14 + 6 + math.ceil(banner.text:GetStringHeight()) + 12)
        banner:SetSize(DETAIL_WIDTH, height)
        view.cardData = { { label = L.REP_BANNER_TITLE, value = text } }
        return height
    end
    local data = CardData(group, ways)
    local width = math.floor((DETAIL_WIDTH - 2 * CARD_GAP) / 3)
    for index, card in ipairs(view.cards) do
        local info = data[index]
        card:SetSize(width, CARD_HEIGHT)
        card.label:SetText(info.label)
        card.value:SetText(info.value)
        card.note:SetText(info.note or "")
    end
    view.cardData = data
    return CARD_HEIGHT
end

---------------------------------------------------------------------------
-- The sections
---------------------------------------------------------------------------

-- { kind = "section"|"entry"|"seller"|"quest"|"note", text, ... }, top to bottom
local function DetailLines(group, ways)
    local lines = {}
    local function Add(line) lines[#lines + 1] = line end
    -- foldedFirst: folded until the player opens it
    local function Section(key, text, icon, foldedFirst)
        local isFolded = folded[key]
        if isFolded == nil then isFolded = foldedFirst == true end
        Add({ kind = "section", key = key, text = text, folded = isFolded, icon = icon or SECTION_ICONS[key] })
        return not isFolded
    end

    -- a crafter's faction sells recipes: they are what the lines name
    local recipes, others = group.artisan == true, ForOthers(group)
    local first = Entries(group)[1]
    local title = recipes and L.REP_SECTION_RECIPES or L.REP_SECTION_PIECES
    if Section("pieces", title, first and (recipes and RecipeIcon(first) or EntryIcon(first))) then
        for _, entry in ipairs(Entries(group)) do
            local standing = entry.requirement.standing
            local rank = entry.role == "best" and (WHITE .. L.RANK_BIS) or (GREY .. L.RANK_ALT)
            Add({ kind = "entry", text = recipes and RecipeName(entry) or EntryName(entry), entry = entry,
                recipe = recipes, icon = recipes and RecipeIcon(entry) or nil, place = EntryPlace(entry),
                standing = (Met(group, standing) and GOLD or WHITE) .. Reputation.StandingName(standing) .. "|r",
                right = rank .. "|r" })
        end
    end

    if Section("sources", L.REP_SECTION_SOURCES) then
        for _, seller in ipairs(Reputation.Sellers(group)) do
            Add({ kind = "seller", text = seller.text, map = seller.map, x = seller.x, y = seller.y })
        end
    end

    -- the crafter's reputation: the quests are for a player who would learn the recipes, folded until asked for
    local questKey = others and "questsSelf" or "quests"
    local questTitle = (others and L.REP_SECTION_QUESTS_SELF or L.REP_SECTION_QUESTS):format(ways.listed, ways.repeatable)
    if ways.listed > 0 and Section(questKey, questTitle, SECTION_ICONS.quests, others) then
        for _, quest in ipairs(ways.quests) do
            Add({ kind = "quest", text = quest.quest, evidence = "data", right = "+" .. quest.amount,
                chip = quest.repeats and L.REP_QUEST_REPEATS or L.REP_QUEST_ONCE })
        end
        if not ways.quests[1] then Add({ kind = "note", text = L.REP_QUESTS_NONE, evidence = "unknown" }) end
    end

    if Section(others and "unknownSelf" or "unknown", L.REP_SECTION_UNKNOWN, SECTION_ICONS.unknown, others) then
        for _, text in ipairs(ways.checks) do Add({ kind = "note", text = text, evidence = "check" }) end
        for _, text in ipairs(ways.unknowns) do Add({ kind = "note", text = text, evidence = "unknown" }) end
    end
    return lines
end

local CanMap = function()
    return (C_Map and C_Map.SetUserWaypoint and UiMapPoint and UiMapPoint.CreateFromCoordinates)
        or OpenWorldMap or (WorldMapFrame and WorldMapFrame.SetMapID)
end

-- A pin where the vendor stands, when the game has them, and the map opened on its zone.
local function ShowOnMap(map, x, y)
    if C_Map and C_Map.SetUserWaypoint and UiMapPoint and UiMapPoint.CreateFromCoordinates
        and (not C_Map.CanSetUserWaypointOnMap or C_Map.CanSetUserWaypointOnMap(map)) then
        local made, point = pcall(UiMapPoint.CreateFromCoordinates, map, x / 100, y / 100)
        if made and point and pcall(C_Map.SetUserWaypoint, point)
            and C_SuperTrack and C_SuperTrack.SetSuperTrackedUserWaypoint then
            pcall(C_SuperTrack.SetSuperTrackedUserWaypoint, true)
        end
    end
    if OpenWorldMap then
        pcall(OpenWorldMap, map)
    elseif WorldMapFrame and WorldMapFrame.SetMapID then
        WorldMapFrame:Show()
        pcall(WorldMapFrame.SetMapID, WorldMapFrame, map)
    end
end

local function LineEnter(line)
    local data = line.data
    if data and data.kind == "entry" then
        if data.recipe then RecipeTooltip(line, data.entry) else PieceTooltip(line, data.entry) end
    end
end

local function LineClick(line)
    local data = line.data
    if not data then return end
    if data.kind == "entry" then
        PieceClick(data.entry)
    elseif data.kind == "section" then
        Widgets.Click()
        folded[data.key] = not data.folded
        ReputationView.Update(view.state)
    end
end

local function CreateLine(parent)
    local line = CreateFrame("Button", nil, parent)
    line:SetWidth(DETAIL_WIDTH)
    line.back = Widgets.ListHighlight(line, "HIGHLIGHT", 0.28)
    line.band = line:CreateTexture(nil, "BACKGROUND", nil, -1)
    line.band:SetPoint("TOPLEFT", 0, -4)
    line.band:SetPoint("BOTTOMRIGHT", 0, 2)
    Band(line.band, "HORIZONTAL", 1, 1, 1, 0.10, 0)
    line.stripe = line:CreateTexture(nil, "BACKGROUND", nil, -1)
    line.stripe:SetAllPoints()
    line.stripe:SetColorTexture(1, 1, 1, 0.035)
    line.badge = line:CreateTexture(nil, "ARTWORK")
    line.badge:SetSize(18, 18)
    line.badge:SetPoint("BOTTOMLEFT", 20, 6)
    line.badge:SetTexCoord(0.07, 0.93, 0.07, 0.93)
    line.rule = line:CreateTexture(nil, "BACKGROUND")
    line.rule:SetColorTexture(1, 1, 1, 0.14)
    line.rule:SetHeight(1)
    line.rule:SetPoint("BOTTOMLEFT", 0, 2)
    line.rule:SetPoint("BOTTOMRIGHT", 0, 2)
    line.fold = line:CreateTexture(nil, "ARTWORK")
    line.fold:SetSize(16, 16)
    line.fold:SetPoint("BOTTOMLEFT", 0, 7)
    line.icon = line:CreateTexture(nil, "ARTWORK")
    line.dot = line:CreateTexture(nil, "ARTWORK")
    line.dot:SetSize(7, 7)
    line.text = line:CreateFontString(nil, "OVERLAY", FONTS.text)
    line.text:SetJustifyH("LEFT")
    line.standing = line:CreateFontString(nil, "OVERLAY", FONTS.text)
    line.standing:SetPoint("LEFT", DETAIL_WIDTH - 300, 0)
    line.standing:SetWidth(96)
    line.standing:SetJustifyH("LEFT")
    line.place = line:CreateFontString(nil, "OVERLAY", FONTS.text)
    line.place:SetPoint("RIGHT", -52, 0)
    line.place:SetWidth(148)
    line.place:SetJustifyH("RIGHT")
    line.place:SetWordWrap(false)
    line.place:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    line.chip = line:CreateFontString(nil, "OVERLAY", FONTS.text)
    line.chip:SetPoint("RIGHT", -64, 0)
    line.chip:SetJustifyH("RIGHT")
    line.chip:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    line.right = line:CreateFontString(nil, "OVERLAY", FONTS.text)
    line.right:SetPoint("RIGHT", -6, 0)
    line.right:SetJustifyH("RIGHT")
    line.map = Widgets.Button(line, L.REP_MAP)
    line.map:SetHeight(20)
    line.map:SetPoint("RIGHT", -4, 0)
    line.map.line = line
    line.map:SetScript("OnClick", function(self)
        local data = self.line.data
        if data and data.map then
            Widgets.Click()
            ShowOnMap(data.map, data.x, data.y)
        end
    end)
    line.map:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(L.REP_MAP_TIP, 1, 1, 1, 1, true)
        GameTooltip:Show()
    end)
    line.map:SetScript("OnLeave", function() GameTooltip:Hide() end)
    line:SetScript("OnEnter", LineEnter)
    line:SetScript("OnLeave", function() GameTooltip:Hide() end)
    line:SetScript("OnClick", LineClick)
    return line
end

local function FillLine(line, data, striped)
    line.data = data
    line.band:SetShown(data.kind == "section")
    line.badge:SetShown(data.kind == "section" and data.icon ~= nil)
    line.stripe:SetShown(striped == true)
    local kind = data.kind
    local entry, section, seller = kind == "entry", kind == "section", kind == "seller"
    local dotted = kind == "quest" or kind == "note"
    line:EnableMouse(entry or section)
    line.back:SetShown(entry or section)
    line.rule:SetShown(section)
    line.fold:SetShown(section)
    line.icon:SetShown(entry or seller)
    line.dot:SetShown(dotted)
    line.standing:SetShown(entry)
    line.place:SetShown(entry)
    line.chip:SetShown(kind == "quest")
    line.right:SetShown(data.right ~= nil)
    line.right:SetText(data.right or "")
    local mapped = (seller and data.map ~= nil and data.x ~= nil and CanMap()) and true or false
    line.map:SetShown(mapped)

    line.text:ClearAllPoints()
    line.text:SetWidth(0)   -- a line is used again for another kind of line
    line.text:SetFontObject((entry or section) and FONTS.name or FONTS.text)
    line.text:SetText(data.text)
    line.text:SetTextColor(1, 1, 1)
    line.text:SetWordWrap(kind == "note")
    line.icon:ClearAllPoints()
    line.dot:ClearAllPoints()
    local height = HEIGHTS[kind]
    if section then
        line.fold:SetTexture(data.folded and "Interface\\Buttons\\UI-PlusButton-Up" or "Interface\\Buttons\\UI-MinusButton-Up")
        line.badge:SetTexture(data.icon)
        line.text:SetPoint("BOTTOMLEFT", data.icon and 44 or 22, 8)
    elseif entry then
        line.icon:SetSize(ICON, ICON)
        line.icon:SetPoint("LEFT", 6, 0)
        line.icon:SetTexture(data.icon or EntryIcon(data.entry))
        line.standing:SetText(data.standing)
        line.place:SetText(data.place)
        line.text:SetPoint("LEFT", line.icon, "RIGHT", 6, 0)
        line.text:SetPoint("RIGHT", line.standing, "LEFT", -8, 0)
        line.text:SetWordWrap(false)
    elseif seller then
        line.icon:SetSize(18, 18)
        line.icon:SetPoint("LEFT", 8, 0)
        line.icon:SetTexture(data.map and SELLER_ICONS.vendor or SELLER_ICONS.other)
        line.text:SetPoint("LEFT", 34, 0)
        line.text:SetPoint("RIGHT", -72, 0)
        line.text:SetWordWrap(false)
    elseif kind == "quest" then
        local color = DOTS[data.evidence]
        line.dot:SetColorTexture(color[1], color[2], color[3], 1)
        line.dot:SetPoint("LEFT", 10, 0)
        line.chip:SetText(data.chip)
        line.text:SetPoint("LEFT", 26, 0)
        line.text:SetPoint("RIGHT", -160, 0)
        line.text:SetWordWrap(false)
    else
        local color = DOTS[data.evidence]
        line.dot:SetColorTexture(color[1], color[2], color[3], 1)
        line.dot:SetPoint("TOPLEFT", 10, -8)
        line.text:SetPoint("TOPLEFT", 26, -4)
        line.text:SetWidth(DETAIL_WIDTH - 32)
        if data.evidence == "unknown" then line.text:SetTextColor(MUTED[1], MUTED[2], MUTED[3]) end
        height = math.max(height, math.ceil(line.text:GetStringHeight()) + 8)
    end
    line:SetHeight(height)
    return height
end

---------------------------------------------------------------------------
-- The faction on the right
---------------------------------------------------------------------------

local function FillWatch(group)
    local watch = view.watch
    local can = Reputation.CanWatch(group.factionID)
    watch:SetShown(can)
    if can then
        watch:SetText(Reputation.Watched(group.factionID) and L.REP_UNWATCH or L.REP_WATCH)
    end
end

local function ShowDetail(group)
    view.title:SetText(Reputation.FactionName(group.factionID) .. Reputation.UnknownMark(group))
    local you = (Earned(group) and GOLD or GREY) .. L.REP_YOU:format(Reputation.ProgressText(group.factionID)) .. "|r"
    local separator = GREY .. "  ·  |r"
    if ForOthers(group) then
        you = GREY .. L.REP_CRAFT_NOT_YOURS:format(CraftNames(group)) .. "|r"
    elseif group.artisan and group.craftStatus == "crafter" then
        you = you .. separator .. CraftSkills(group)
    elseif group.artisan then
        you = you .. separator .. GREY .. L.REP_ARTISAN_NOTE .. "|r"   -- the game does not say the professions
    end
    local unsure = Reputation.UnknownRemark(group)
    view.you:SetText(you .. (unsure and (separator .. GREY .. unsure .. "|r") or ""))
    FillWatch(group)

    local ways = Reputation.Ways(group.factionID, view.state and view.state.class)
    FillTrack(group)
    view.track:ClearAllPoints()
    view.track:SetPoint("TOPLEFT", view.detailChild, "TOPLEFT", 0, 0)
    local offset = TRACK_BLOCK + 4

    local cardsHeight = FillCards(group, ways)
    for index, card in ipairs(view.cards) do
        card:ClearAllPoints()
        card:SetPoint("TOPLEFT", view.detailChild, "TOPLEFT", (index - 1) * (card:GetWidth() + CARD_GAP), -offset)
    end
    view.banner:ClearAllPoints()
    view.banner:SetPoint("TOPLEFT", view.detailChild, "TOPLEFT", 0, -offset)
    offset = offset + cardsHeight + 6

    local data = DetailLines(group, ways)
    local count = 0   -- the lines under a section: every other one lighter
    for index, lineData in ipairs(data) do
        local line = view.lines[index]
        if not line then
            line = CreateLine(view.detailChild)
            view.lines[index] = line
        end
        count = lineData.kind == "section" and 0 or count + 1
        local height = FillLine(line, lineData, count > 0 and count % 2 == 0)
        line:ClearAllPoints()
        line:SetPoint("TOPLEFT", view.detailChild, "TOPLEFT", 0, -offset)
        line:Show()
        offset = offset + height
    end
    for index = #data + 1, #view.lines do view.lines[index]:Hide() end
    Fit(view.detail, view.detailChild, DETAIL_WIDTH, offset)
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

    -- the factions on a darker ground than the faction's side, and a band under the faction's name
    view.listBack = view:CreateTexture(nil, "BACKGROUND")
    view.listBack:SetColorTexture(0, 0, 0, 0.28)
    view.listBack:SetPoint("TOPLEFT", -2, 2)
    view.listBack:SetPoint("BOTTOMLEFT", -2, -2)
    view.listBack:SetWidth(LIST_WIDTH + 4)
    view.headerBand = view:CreateTexture(nil, "BACKGROUND")
    view.headerBand:SetPoint("TOPLEFT", LIST_WIDTH + 3, 2)
    view.headerBand:SetPoint("TOPRIGHT", 0, 2)
    view.headerBand:SetHeight(52)
    Band(view.headerBand, "HORIZONTAL", 1, 1, 1, 0.09, 0)

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

    view.title = view:CreateFontString(nil, "OVERLAY", FONTS.header)
    view.title:SetPoint("TOPLEFT", LIST_WIDTH + 14, -2)
    view.title:SetTextColor(1, 1, 1)
    view.you = view:CreateFontString(nil, "OVERLAY", FONTS.text)
    view.you:SetPoint("TOPLEFT", view.title, "BOTTOMLEFT", 0, -4)

    view.watch = Widgets.Button(view, L.REP_UNWATCH)
    view.watch:SetPoint("TOPRIGHT", -BAR_ROOM, -2)
    view.watch:SetScript("OnClick", function()
        local group = view.chosen
        if not group then return end
        Widgets.Click()
        Reputation.Watch(group.factionID, not Reputation.Watched(group.factionID))
        FillWatch(group)
    end)
    view.watch:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_BOTTOMRIGHT")
        GameTooltip:SetText(L.REP_WATCH_TIP, 1, 1, 1, 1, true)
        GameTooltip:Show()
    end)
    view.watch:SetScript("OnLeave", function() GameTooltip:Hide() end)

    view.detail, view.detailChild = Widgets.Scroll(view)
    view.detail:SetPoint("TOPLEFT", LIST_WIDTH + 14, -54)
    view.detail:SetPoint("BOTTOMRIGHT", -BAR_ROOM, 0)
    view.track = CreateTrack(view.detailChild)
    view.cards = { CreateCard(view.detailChild, GREEN), CreateCard(view.detailChild, TEAL),
        CreateCard(view.detailChild, TEAL) }
    view.banner = CreateBanner(view.detailChild)
    view.banner:Hide()
    view.pieces = {}

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
    view.state = state
    local needs = Reputation.Needs(state.class, state.spec, state.list)
    view.factionData = needs
    local chosen = LayoutFactions(needs, state)
    local any = chosen ~= nil
    view.empty:SetShown(not any)
    view.listBack:SetShown(any)
    view.headerBand:SetShown(any)
    view.list:SetShown(any)
    view.detail:SetShown(any)
    view.divider:SetShown(any)
    view.title:SetShown(any)
    view.you:SetShown(any)
    view.chosen = chosen
    if chosen then
        ShowDetail(chosen)
    else
        view.watch:Hide()
        view.detailData, view.cardData = {}, {}
    end
end
