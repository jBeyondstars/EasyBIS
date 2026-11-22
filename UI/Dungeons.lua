local _, ns = ...
local L = ns.L
local Widgets = ns.Widgets
local Browser = ns.Browser
local Dungeons = ns.Dungeons

--[[
The dungeons, the second of the tabs down the window's side: which dungeons to run for the spec's best picks
(Dungeons.lua), in the colours of a spreadsheet where each dungeon has its own.

  top      how many best picks are left to farm and in how many dungeons, and the switch between the two
           ways to look at them. The choice is kept (the option "dungeonGrid").
  by dungeon
           the set: the best pick of every slot in the order of the character sheet, each over a bar in
           its dungeon's colour; a piece no dungeon holds is in black and white, a little darker, and
           its bar grey.
           Then a band per run, the one with the most best picks left to get first: on the run's colour,
           how many pieces the band holds, every one it shows; its name; and its pieces, each with its
           boss and its drop rate. A run whose best picks are all the player's turns grey.
           Then, in one line, where the other best picks come from: a click opens them in the Items tab.
  by piece the spreadsheet: a line per piece in the order of the character sheet, a column per run under
           the same count, a cell in the run's colour where the piece drops, with its rate. The last
           column says where a piece of no dungeon comes from; such a line is dimmed.

A run is a dungeon, or a wing that is run on its own. A quest's reward sits with the dungeon its quest is
done in, under the game's quest mark, with the quest's title in place of a boss: one run is enough for it.
What the player has (worn, in the bags or in the bank) is checked and greyed, and leaves the sentence at
the top. The alternatives come with the window's Alternatives button: smaller and tagged;
they count in a band's number, as they are in the band, and in nothing else. They fade once the slot's
best pick is the player's.

Pointing at a run lights its slots in the set; pointing at a piece lights its run. A piece's tooltip is the
item's, with its runs; a click opens its slot in the Items tab, Shift-click links it.

  DungeonView.Create(parent)   the view, hidden
  DungeonView.Update(state)    fills it. state: the window's { class, spec, list }
  DungeonView.Hide()
  DungeonView.view             (the tests read it: model, summary, mode, tiles, lanes, elsewhere, headers, rows,
                               empty)
]]

local DungeonView = {}
ns.DungeonView = DungeonView

local PAD = 8
local BAR_ROOM = 26           -- what a scroll bar takes
local WIDTH = 904             -- what scrolls
local HEAD = 32               -- the summary and the switch
local TILE = 40               -- a slot of the set
local TILE_GAP, TILE_BREAK = 5, 12   -- between two slots; more before the rings and before the weapons
local BAR = 5                 -- the bar of colour under a slot
local STRIP = TILE + 3 + BAR + 12
local LANE_MIN, LANE_GAP = 56, 6
local BLOCK = 56              -- the block of colour that holds a run's count
local WHO = 188               -- the run's name and its squares
local CHIPS_LEFT = BLOCK + WHO
local PER_ROW = 3
local CHIP_GAP = 8
local CHIP_WIDTH = math.floor((WIDTH - CHIPS_LEFT - (PER_ROW - 1) * CHIP_GAP - 4) / PER_ROW)
local CHIP_PITCH = 46
local ICON, ALT_ICON = 38, 30
local ELSEWHERE = 30          -- the line of the pieces no dungeon holds
local GRID_HEAD = 58          -- the columns' names, on two lines where a column is narrow ("Strat" over "Live")
local GRID_NAME = 250         -- the piece's column
local GRID_ROW = 28
local GRID_ICON = 22
local COLUMN_MIN, COLUMN_MAX, COLUMN_GAP = 30, 66, 3
local ELSE_ROOM = 150         -- what the last column keeps at least
local CROWDED = 8             -- runs: past that many, the names and the last column give up some room
local DIM = 0.45              -- a piece the player has, an alternative that has had its day, a line of no dungeon
local ASIDE = 0.7             -- a piece of the set no dungeon holds: black and white, and a little darker
local FADED = 0.22            -- what the mouse is not on, while it is on a run
local UNKNOWN_ICON = "Interface\\Icons\\INV_Misc_QuestionMark"
local CHECK = "Interface\\Buttons\\UI-CheckBox-Check"
local QUEST = "Interface\\GossipFrame\\AvailableQuestIcon"
local QUEST_TEXT = "|T" .. QUEST .. ":14:14|t"

local FONTS = Browser.FONTS
local COUNT_FONT = Browser.Font("EasyBISDungeonCount", "GameFontNormalLarge", 26)   -- a run's count
local MUTED = Widgets.MUTED
local WHITE, GREY, GOLD = "|cffffffff", "|cffa8a8b0", "|cffffd100"
local DONE = { 0.30, 0.30, 0.33 }   -- the block of a run with nothing left to get

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

local view

---------------------------------------------------------------------------
-- A piece: its picture, its tooltip, a click
---------------------------------------------------------------------------

-- name in its quality's colour, r, g, b, picture
local function Look(id)
    local name, quality, texture, _
    if GetInfo then name, _, quality, _, _, _, _, _, _, texture = GetInfo(id) end
    local r, g, b, hex = ns.QualityColor(quality)
    return hex .. (name or ns.Items.Name(id)) .. "|r", r, g, b, texture or (GetIcon and GetIcon(id)) or UNKNOWN_ICON
end

-- A picture in a square of its quality's colour, with room for the two marks: the player has it, a quest gives it.
local function CreateIcon(parent, size)
    local icon = {}
    icon.border = parent:CreateTexture(nil, "BACKGROUND")
    icon.back = parent:CreateTexture(nil, "BORDER")
    icon.back:SetPoint("TOPLEFT", icon.border, "TOPLEFT", 1, -1)
    icon.back:SetPoint("BOTTOMRIGHT", icon.border, "BOTTOMRIGHT", -1, 1)
    icon.back:SetColorTexture(0.04, 0.04, 0.05, 1)
    icon.art = parent:CreateTexture(nil, "ARTWORK")
    icon.art:SetPoint("TOPLEFT", icon.border, "TOPLEFT", 1, -1)
    icon.art:SetPoint("BOTTOMRIGHT", icon.border, "BOTTOMRIGHT", -1, 1)
    icon.art:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    icon.check = parent:CreateTexture(nil, "OVERLAY")
    icon.check:SetTexture(CHECK)
    icon.check:SetPoint("CENTER", icon.border, "TOPRIGHT", -2, -2)
    icon.quest = parent:CreateTexture(nil, "OVERLAY")
    icon.quest:SetTexture(QUEST)
    icon.quest:SetPoint("CENTER", icon.border, "BOTTOMRIGHT", -2, 3)
    icon.border:SetSize(size, size)
    icon.check:SetSize(math.max(14, size / 2), math.max(14, size / 2))
    icon.quest:SetSize(math.max(12, size * 0.42), math.max(12, size * 0.42))
    return icon
end

-- piece: nil for a slot the list leaves empty. Returns the name to write next to it.
local function FillIcon(icon, piece, quest)
    local known = piece ~= nil and piece.id ~= nil
    icon.art:SetShown(known)
    icon.check:SetShown(known and piece.owned == true)
    icon.quest:SetShown(known and quest == true)
    if not known then
        icon.border:SetColorTexture(1, 1, 1, 0.12)
        return ""
    end
    local name, r, g, b, texture = Look(piece.id)
    icon.border:SetColorTexture(r, g, b, 0.9)
    icon.art:SetTexture(texture)
    icon.art:SetDesaturated(piece.owned == true)
    return name
end

local function Mark(origin)
    local mark = ns.Sources.OriginMark(origin)
    return mark ~= "" and (" |cff808080" .. mark .. "|r") or ""
end

-- "General Drakkisath 18%", "2 bosses 9.5%", the quest's title under the game's quest mark.
local function EntryText(entry)
    if entry.quest then return QUEST_TEXT .. " " .. entry.quest end
    local first = entry.drops[1]
    local boss = #entry.drops > 1 and L.DUN_BOSSES:format(#entry.drops) or first.boss
    if boss == "" then boss = L.DUN_BOSS_UNKNOWN end
    local percent = ns.Sources.PercentText(entry.percent)
    return boss .. (percent ~= "" and ("  " .. WHITE .. percent .. "|r") or "") .. Mark(first.origin)
end

-- What a cell of the grid says: the rate, the quest mark, or that the rate is not known.
local function CellText(entry)
    if entry.quest then return QUEST_TEXT end
    local percent = ns.Sources.PercentText(entry.percent)
    return percent ~= "" and percent or "?"
end

local function PieceTooltip(owner, piece, side)
    if not piece then return end
    if not piece.id then
        Browser.PlaceTooltip(owner, side)
        GameTooltip:SetText(ns.SlotName(piece.slot), 1, 1, 1)
        GameTooltip:AddLine(piece.twoHand and L.CHAR_TWO_HAND or L.CHAR_EMPTY, MUTED[1], MUTED[2], MUTED[3], true)
        Browser.ShowTooltip()
        return
    end
    Browser.ItemTooltip(owner, piece, side)
    for _, key in ipairs(piece.order or {}) do
        local entry = piece.runs[key]
        local run = view.runsByKey[key]
        local name = run.noWing and (run.name .. " (" .. L.DUN_NO_WING .. ")") or run.name
        if entry.quest then
            GameTooltip:AddLine(L.DUN_TIP_QUEST:format(name, entry.quest), run.color[1], run.color[2], run.color[3], true)
        else
            for _, drop in ipairs(entry.drops) do
                local percent = ns.Sources.PercentText(drop.percent)
                local boss = drop.boss ~= "" and drop.boss or L.DUN_BOSS_UNKNOWN
                GameTooltip:AddLine(L.DUN_TIP_RUN:format(name, boss .. (percent ~= "" and (" (" .. percent .. ")") or "")),
                    run.color[1], run.color[2], run.color[3], true)
            end
        end
    end
    if piece.owned then GameTooltip:AddLine(L.DUN_TIP_OWNED, 0.12, 1, 0, true) end
    GameTooltip:AddLine(L.REP_PIECE_TIP, MUTED[1], MUTED[2], MUTED[3], true)
    Browser.ShowTooltip()
end

-- Shift-click links the item; a click opens its slot among the items.
local function PieceClick(piece)
    if not piece then return end
    if piece.id and Browser.ModifiedClick(piece.id) then return end
    Widgets.Click()
    Browser.ShowSlot(piece.slot)
end

---------------------------------------------------------------------------
-- What the mouse is on: a run lights its slots, a piece lights its run
---------------------------------------------------------------------------

local function Light(key, slot)
    for _, tile in ipairs(view.tiles) do
        local piece = tile.piece
        local mine = key ~= nil and piece ~= nil and piece.runs ~= nil and piece.runs[key] ~= nil
            and (slot == nil or piece.slot == slot)
        tile:SetAlpha(key == nil and tile.rest or (mine and 1 or FADED))
        tile.glow:SetShown(mine)
        if mine then
            local color = view.runsByKey[key].color
            tile.glow:SetColorTexture(color[1], color[2], color[3], 1)
        end
    end
    for _, lane in ipairs(view.lanes) do
        if lane:IsShown() then lane:SetAlpha((key == nil or lane.run.key == key) and 1 or 0.35) end
    end
end

---------------------------------------------------------------------------
-- By dungeon: the set
---------------------------------------------------------------------------

local function CreateTile(parent)
    local tile = CreateFrame("Button", nil, parent)
    tile:SetSize(TILE, TILE + 3 + BAR)
    tile.glow = tile:CreateTexture(nil, "BACKGROUND", nil, -1)
    tile.glow:SetPoint("TOPLEFT", -2, 2)
    tile.glow:SetSize(TILE + 4, TILE + 4)
    tile.glow:Hide()
    tile.icon = CreateIcon(tile, TILE)
    tile.icon.border:SetPoint("TOPLEFT", 0, 0)
    tile.bar = tile:CreateTexture(nil, "ARTWORK")
    tile.bar:SetSize(TILE, BAR)
    tile.bar:SetPoint("TOPLEFT", 0, -(TILE + 3))
    local highlight = tile:CreateTexture(nil, "HIGHLIGHT")
    highlight:SetTexture("Interface\\Buttons\\ButtonHilight-Square")
    highlight:SetBlendMode("ADD")
    highlight:SetPoint("TOPLEFT", 0, 0)
    highlight:SetSize(TILE, TILE)
    tile:SetScript("OnEnter", function(self)
        local piece = self.piece
        if piece and piece.order then Light(piece.order[1], piece.slot) end
        PieceTooltip(self, piece)
    end)
    tile:SetScript("OnLeave", function(self)
        Light(nil)
        ns.Tooltip.HideOwned(self)
    end)
    tile:SetScript("OnClick", function(self) PieceClick(self.piece) end)
    return tile
end

local function LayoutStrip(model)
    local x = 2
    for index, cell in ipairs(model.sheet) do
        local tile = view.tiles[index]
        if not tile then
            tile = CreateTile(view.runsPane)
            view.tiles[index] = tile
        end
        if index > 1 then
            x = x + TILE + ((cell.rank == 1 and (cell.slot == "finger" or cell.slot == "main")) and TILE_BREAK or TILE_GAP)
        end
        tile.piece = cell
        FillIcon(tile.icon, cell)
        local key = cell.order and cell.order[1]
        if key then
            local color = view.runsByKey[key].color
            tile.bar:SetColorTexture(color[1], color[2], color[3], 1)
        else
            tile.bar:SetColorTexture(1, 1, 1, 0.12)
        end
        -- a piece no dungeon holds is in black and white, its frame grey, and steps back a little: the colour
        -- is the dungeons'
        tile.grey = cell.id ~= nil and key == nil
        if tile.grey then
            tile.icon.art:SetDesaturated(true)
            tile.icon.border:SetColorTexture(0.45, 0.45, 0.47, 0.9)
        end
        tile.rest = tile.grey and ASIDE or 1
        tile:SetAlpha(tile.rest)
        tile.glow:Hide()
        tile:ClearAllPoints()
        tile:SetPoint("TOPLEFT", view.runsPane, "TOPLEFT", x, -4)
        tile:Show()
    end
    for index = #model.sheet + 1, #view.tiles do view.tiles[index]:Hide() end
end

---------------------------------------------------------------------------
-- By dungeon: a band per run
---------------------------------------------------------------------------

local function CreateChip(lane)
    local chip = CreateFrame("Button", nil, lane)
    chip:SetSize(CHIP_WIDTH, CHIP_PITCH - 4)
    Widgets.ListHighlight(chip, "HIGHLIGHT", 0.30)
    chip.icon = CreateIcon(chip, ICON)
    chip.name = chip:CreateFontString(nil, "OVERLAY", FONTS.name)
    chip.name:SetJustifyH("LEFT")
    chip.name:SetWordWrap(false)
    chip.tag = chip:CreateFontString(nil, "OVERLAY", FONTS.text)
    chip.tag:SetPoint("TOPRIGHT", -4, -5)
    chip.tag:SetText(L.RANK_ALT)
    chip.tag:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    chip.sub = chip:CreateFontString(nil, "OVERLAY", FONTS.text)
    chip.sub:SetJustifyH("LEFT")
    chip.sub:SetWordWrap(false)
    chip.sub:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    chip:SetScript("OnEnter", function(self)
        Light(self.run.key, self.entry.piece.slot)
        PieceTooltip(self, self.entry.piece)
    end)
    chip:SetScript("OnLeave", function(self)
        Light(nil)
        ns.Tooltip.HideOwned(self)
    end)
    chip:SetScript("OnClick", function(self) PieceClick(self.entry.piece) end)
    return chip
end

local function FillChip(chip, run, entry)
    local piece = entry.piece
    chip.run, chip.entry = run, entry
    local size = piece.best and ICON or ALT_ICON
    local inset = (ICON - size) / 2
    chip.icon.border:SetSize(size, size)
    chip.icon.border:ClearAllPoints()
    chip.icon.border:SetPoint("LEFT", chip, "LEFT", 2 + inset, 0)
    chip.name:SetText(FillIcon(chip.icon, piece, entry.quest ~= nil))
    chip.tag:SetShown(not piece.best)
    chip.name:ClearAllPoints()
    chip.name:SetPoint("TOPLEFT", chip, "TOPLEFT", ICON + 10, -3)
    if piece.best then
        chip.name:SetPoint("RIGHT", chip, "RIGHT", -4, 0)
    else
        chip.name:SetPoint("RIGHT", chip.tag, "LEFT", -6, 0)
    end
    chip.sub:ClearAllPoints()
    chip.sub:SetPoint("BOTTOMLEFT", chip, "BOTTOMLEFT", ICON + 10, 4)
    chip.sub:SetPoint("RIGHT", chip, "RIGHT", -4, 0)
    chip.sub:SetText(EntryText(entry))
    -- what the player has, and an alternative of a slot that is done, step back
    local faded = piece.owned or piece.moot
    chip.name:SetAlpha(faded and DIM or 1)
    chip.sub:SetAlpha(faded and DIM or 1)
    chip.tag:SetAlpha(faded and DIM or 1)
    chip.icon.art:SetAlpha((piece.moot and not piece.owned) and DIM or 1)
end

local function CreateLane(parent)
    local lane = CreateFrame("Frame", nil, parent)
    lane:SetWidth(WIDTH)
    lane:EnableMouse(true)
    lane.band = lane:CreateTexture(nil, "BACKGROUND")
    lane.band:SetPoint("TOPLEFT", BLOCK, 0)
    lane.band:SetPoint("BOTTOMRIGHT", 0, 0)
    lane.block = lane:CreateTexture(nil, "BORDER")
    lane.block:SetPoint("TOPLEFT", 0, 0)
    lane.block:SetPoint("BOTTOMLEFT", 0, 0)
    lane.block:SetWidth(BLOCK)
    lane.shade = lane:CreateTexture(nil, "ARTWORK")   -- the block darker towards its foot
    lane.shade:SetAllPoints(lane.block)
    Widgets.Band(lane.shade, "VERTICAL", 0, 0, 0, 0.38, 0)
    lane.rule = lane:CreateTexture(nil, "BACKGROUND")
    lane.rule:SetColorTexture(1, 1, 1, 0.08)
    lane.rule:SetHeight(1)
    lane.rule:SetPoint("BOTTOMLEFT", 0, -1)
    lane.rule:SetPoint("BOTTOMRIGHT", 0, -1)
    lane.count = lane:CreateFontString(nil, "OVERLAY", COUNT_FONT)
    lane.count:SetPoint("CENTER", lane.block, "CENTER", 0, 0)
    lane.count:SetTextColor(1, 1, 1)
    lane.name = lane:CreateFontString(nil, "OVERLAY", FONTS.name)
    lane.name:SetWidth(WHO - 18)
    lane.name:SetJustifyH("LEFT")
    lane.name:SetWordWrap(false)
    lane.name:SetTextColor(1, 1, 1)
    lane.note = lane:CreateFontString(nil, "OVERLAY", FONTS.text)   -- a dungeon with wings, and no wing named
    lane.note:SetPoint("LEFT", lane, "LEFT", BLOCK + 12, -9)
    lane.note:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    lane.note:SetText(L.DUN_NO_WING)
    lane.chips = {}
    lane:SetScript("OnEnter", function(self) Light(self.run.key) end)
    lane:SetScript("OnLeave", function() Light(nil) end)
    return lane
end

local function FillLane(lane, run)
    lane.run = run
    local color = run.color
    local finished = run.need == 0 and run.got > 0
    local block = finished and DONE or color
    lane.block:SetColorTexture(block[1], block[2], block[3], 1)
    lane.band:SetShown(not finished)
    Widgets.Band(lane.band, "HORIZONTAL", color[1], color[2], color[3], 0.24, 0.03)
    lane.count:SetText(tostring(run.total))   -- every piece of the line, as the eye counts them
    lane.name:SetText(run.name)
    -- "Stratholme" next to "Stratholme: Undead" would pass for the other wing: it says it is neither, under its name
    lane.note:SetShown(run.noWing == true)
    lane.name:ClearAllPoints()
    lane.name:SetPoint("LEFT", lane, "LEFT", BLOCK + 12, run.noWing and 8 or 0)

    local rows = math.max(1, math.ceil(#run.entries / PER_ROW))
    local height = math.max(LANE_MIN, 10 + rows * CHIP_PITCH)
    local top = (height - rows * CHIP_PITCH + 4) / 2
    for index, entry in ipairs(run.entries) do
        local chip = lane.chips[index]
        if not chip then
            chip = CreateChip(lane)
            lane.chips[index] = chip
        end
        FillChip(chip, run, entry)
        local column, line = (index - 1) % PER_ROW, math.floor((index - 1) / PER_ROW)
        chip:ClearAllPoints()
        chip:SetPoint("TOPLEFT", lane, "TOPLEFT", CHIPS_LEFT + column * (CHIP_WIDTH + CHIP_GAP), -(top + line * CHIP_PITCH))
        chip:Show()
    end
    for index = #run.entries + 1, #lane.chips do lane.chips[index]:Hide() end
    lane:SetHeight(height)
    lane:SetAlpha(1)
    return height
end

---------------------------------------------------------------------------
-- By dungeon: the best picks of elsewhere, in one line
---------------------------------------------------------------------------

local function CreateElsewhere(parent)
    local button = CreateFrame("Button", nil, parent)
    button:SetHeight(20)
    Widgets.ListHighlight(button, "HIGHLIGHT", 0.30)
    button.text = button:CreateFontString(nil, "OVERLAY", FONTS.text)
    button.text:SetPoint("LEFT", 4, 0)
    button:SetScript("OnClick", function(self)
        Widgets.Click()
        Browser.ShowSource(self.category)
    end)
    button:SetScript("OnEnter", function(self)
        Browser.PlaceTooltip(self)
        GameTooltip:SetText(ns.Sources.CategoryName(self.category), 1, 1, 1)
        GameTooltip:AddLine(L.DUN_TIP_ELSEWHERE, MUTED[1], MUTED[2], MUTED[3], true)
        Browser.ShowTooltip()
    end)
    button:SetScript("OnLeave", ns.Tooltip.HideOwned)
    return button
end

-- Returns the height the line takes: nothing when every best pick is a dungeon's.
local function LayoutElsewhere(model, offset)
    local total = 0
    for _, entry in ipairs(model.elsewhere) do total = total + entry.count end
    view.elsewhereLabel:SetShown(total > 0)
    local x = 6
    if total > 0 then
        view.elsewhereLabel:SetText(total == 1 and L.DUN_ELSEWHERE_ONE or L.DUN_ELSEWHERE:format(total))
        view.elsewhereLabel:ClearAllPoints()
        view.elsewhereLabel:SetPoint("LEFT", view.runsPane, "TOPLEFT", x, -(offset + ELSEWHERE / 2))
        x = x + math.ceil(view.elsewhereLabel:GetStringWidth()) + 10
    end
    for index, entry in ipairs(model.elsewhere) do
        local button = view.elsewhere[index]
        if not button then
            button = CreateElsewhere(view.runsPane)
            view.elsewhere[index] = button
        end
        button.category = entry.category
        button.text:SetText(ns.Sources.IconText(entry.category) .. " " .. WHITE .. entry.count .. "|r "
            .. GREY .. ns.Sources.CategoryName(entry.category) .. "|r")
        local width = math.ceil(button.text:GetStringWidth()) + 10
        button:SetWidth(width)
        button:ClearAllPoints()
        button:SetPoint("LEFT", view.runsPane, "TOPLEFT", x, -(offset + ELSEWHERE / 2))
        button:Show()
        x = x + width + 6
    end
    for index = #model.elsewhere + 1, #view.elsewhere do view.elsewhere[index]:Hide() end
    return total > 0 and ELSEWHERE or 0
end

-- The set, the runs, the rest. Returns the height of it all.
local function LayoutRuns(model)
    LayoutStrip(model)
    local offset = STRIP
    for index, run in ipairs(model.runs) do
        local lane = view.lanes[index]
        if not lane then
            lane = CreateLane(view.runsPane)
            view.lanes[index] = lane
        end
        local height = FillLane(lane, run)
        lane:ClearAllPoints()
        lane:SetPoint("TOPLEFT", view.runsPane, "TOPLEFT", 0, -offset)
        lane:Show()
        offset = offset + height + LANE_GAP
    end
    for index = #model.runs + 1, #view.lanes do view.lanes[index]:Hide() end
    -- no run at all: the sentence that says so takes the room of two
    local none = model.runs[1] == nil
    view.empty:SetShown(none)
    if none then
        view.empty:ClearAllPoints()
        view.empty:SetPoint("TOP", view.runsPane, "TOP", 0, -(offset + 34))
        view.empty:SetText(WHITE .. L.DUN_NONE .. "|r"
            .. (ns:GetOption("listAlts") and "" or ("\n\n" .. L.DUN_NONE_HINT)))
        offset = offset + 110
    end
    return offset + LayoutElsewhere(model, offset) + 4
end

---------------------------------------------------------------------------
-- By piece: the spreadsheet
---------------------------------------------------------------------------

-- The width of a run's column, and of the piece's: many runs (a spec with every alternative listed) take
-- room from the names and from the last column.
local function Columns(count)
    local name, rest = GRID_NAME, ELSE_ROOM
    if count > CROWDED then name, rest = GRID_NAME - 40, ELSE_ROOM - 30 end
    local width = math.floor((WIDTH - name - rest) / math.max(1, count)) - COLUMN_GAP
    return math.max(COLUMN_MIN, math.min(COLUMN_MAX, width)), name
end

local function ColumnLeft(index, width, name)
    return name + COLUMN_GAP + (index - 1) * (width + COLUMN_GAP)
end

local function CreateHeader(parent)
    local header = CreateFrame("Frame", nil, parent)
    header:SetHeight(GRID_HEAD - 4)
    header:EnableMouse(true)
    header.block = header:CreateTexture(nil, "BORDER")
    header.block:SetAllPoints()
    header.shade = header:CreateTexture(nil, "ARTWORK")
    header.shade:SetAllPoints()
    Widgets.Band(header.shade, "VERTICAL", 0, 0, 0, 0.38, 0)
    header.count = header:CreateFontString(nil, "OVERLAY", FONTS.header)
    header.count:SetPoint("TOP", 0, -3)
    header.count:SetTextColor(1, 1, 1)
    -- the short name wraps at its space rather than lose its end: "Strat Live" must not read like "Strat UD"
    header.short = header:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    header.short:SetPoint("BOTTOM", 0, 5)
    header.short:SetWordWrap(true)
    if header.short.SetMaxLines then header.short:SetMaxLines(2) end
    header.short:SetTextColor(1, 1, 1)
    header:SetScript("OnEnter", function(self)
        Browser.PlaceTooltip(self)
        GameTooltip:SetText(self.run.name, self.run.color[1], self.run.color[2], self.run.color[3])
        if self.run.noWing then GameTooltip:AddLine(L.DUN_NO_WING, MUTED[1], MUTED[2], MUTED[3], true) end
        Browser.ShowTooltip()
    end)
    header:SetScript("OnLeave", ns.Tooltip.HideOwned)
    return header
end

local function CreateCell(row)
    local cell = {}
    cell.back = row:CreateTexture(nil, "BORDER")
    cell.back:SetHeight(GRID_ROW - 2)
    cell.text = row:CreateFontString(nil, "OVERLAY", FONTS.text)
    cell.text:SetPoint("CENTER", cell.back, "CENTER", 0, 0)
    cell.text:SetTextColor(1, 1, 1)
    cell.check = row:CreateTexture(nil, "OVERLAY")
    cell.check:SetTexture(CHECK)
    cell.check:SetSize(16, 16)
    cell.check:SetPoint("CENTER", cell.back, "CENTER", 0, 0)
    return cell
end

local function CreateRow(parent)
    local row = CreateFrame("Button", nil, parent)
    row:SetSize(WIDTH, GRID_ROW)
    Widgets.ListHighlight(row, "HIGHLIGHT", 0.28)
    row.rule = row:CreateTexture(nil, "BACKGROUND")
    row.rule:SetHeight(1)
    row.rule:SetPoint("TOPLEFT", 0, 0)
    row.rule:SetPoint("TOPRIGHT", 0, 0)
    row.icon = CreateIcon(row, GRID_ICON)
    row.name = row:CreateFontString(nil, "OVERLAY", FONTS.name)
    row.name:SetJustifyH("LEFT")
    row.name:SetWordWrap(false)
    row.where = row:CreateFontString(nil, "OVERLAY", FONTS.text)
    row.where:SetJustifyH("LEFT")
    row.where:SetWordWrap(false)
    row.where:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    row.cells = {}
    row:SetScript("OnEnter", function(self) PieceTooltip(self, self.piece) end)
    row:SetScript("OnLeave", ns.Tooltip.HideOwned)
    row:SetScript("OnClick", function(self) PieceClick(self.piece) end)
    return row
end

-- What the last column says of a piece no dungeon holds: a picture for the kind of source, and a few words.
local function WhereText(piece)
    local source = piece.source
    return ns.Sources.IconText(source.category) .. " " .. ns.Sources.Short(source) .. Mark(source.origin)
end

local function FillRow(row, piece, model, width, name)
    row.piece = piece
    local indent = piece.best and 0 or 16
    row.icon.border:ClearAllPoints()
    row.icon.border:SetPoint("LEFT", row, "LEFT", 3 + indent, 0)
    local quest = false
    for _, key in ipairs(piece.order or {}) do quest = quest or piece.runs[key].quest ~= nil end
    row.name:SetText(FillIcon(row.icon, piece, quest))
    row.name:ClearAllPoints()
    row.name:SetPoint("LEFT", row, "LEFT", 3 + indent + GRID_ICON + 7, 0)
    row.name:SetPoint("RIGHT", row, "LEFT", name - 4, 0)
    -- the first line of a slot under a brighter rule, so the slots stand apart
    row.rule:SetColorTexture(1, 1, 1, piece.first and 0.16 or 0.05)

    -- a piece no dungeon holds steps back, as does what the player has and an alternative of a slot that is done
    local alpha = (not piece.runs or piece.owned or piece.moot) and DIM or (piece.best and 1 or 0.85)
    row.name:SetAlpha(alpha)
    row.icon.art:SetAlpha((not piece.runs or piece.moot) and DIM or 1)
    row.icon.border:SetAlpha(not piece.runs and DIM or 1)

    local used = 0
    for index, run in ipairs(model.runs) do
        local entry = piece.runs and piece.runs[run.key]
        if entry then
            used = used + 1
            local cell = row.cells[used]
            if not cell then
                cell = CreateCell(row)
                row.cells[used] = cell
            end
            cell.back:ClearAllPoints()
            cell.back:SetPoint("LEFT", row, "LEFT", ColumnLeft(index, width, name), 0)
            cell.back:SetWidth(width)
            -- a best pick fills its cell; an alternative, and what is done, tints it
            local strong = piece.best and not piece.owned
            cell.back:SetColorTexture(run.color[1], run.color[2], run.color[3], strong and 0.88 or 0.30)
            cell.back:Show()
            cell.check:SetShown(piece.owned == true)
            cell.text:SetShown(not piece.owned)
            cell.text:SetText(CellText(entry))
            cell.run = run
        end
    end
    for index = used + 1, #row.cells do
        row.cells[index].back:Hide()
        row.cells[index].text:Hide()
        row.cells[index].check:Hide()
    end
    row.used = used

    row.where:SetShown(not piece.runs)
    if not piece.runs then
        row.where:ClearAllPoints()
        row.where:SetPoint("LEFT", row, "LEFT", ColumnLeft(#model.runs + 1, width, name) + 6, 0)
        row.where:SetPoint("RIGHT", row, "RIGHT", -4, 0)
        row.where:SetText(WhereText(piece))
    end
end

-- The columns' names over the lines, then a line per piece. Returns the height of the lines.
local function LayoutGrid(model)
    local width, name = Columns(#model.runs)
    for index, run in ipairs(model.runs) do
        local header = view.headers[index]
        if not header then
            header = CreateHeader(view.gridHead)
            view.headers[index] = header
        end
        header.run = run
        local finished = run.need == 0 and run.got > 0
        local block = finished and DONE or run.color
        header.block:SetColorTexture(block[1], block[2], block[3], 1)
        header.count:SetText(tostring(run.total))
        header.short:SetText(run.short)
        header.short:SetWidth(width + 2)
        header:SetWidth(width)
        header:ClearAllPoints()
        header:SetPoint("TOPLEFT", view.gridHead, "TOPLEFT", ColumnLeft(index, width, name), 0)
        header:Show()

        -- a faint stripe down each column, so a cell is found under its name
        local stripe = view.stripes[index]
        if not stripe then
            stripe = view.gridPane:CreateTexture(nil, "BACKGROUND")
            stripe:SetColorTexture(1, 1, 1, 0.03)
            view.stripes[index] = stripe
        end
        stripe:ClearAllPoints()
        stripe:SetPoint("TOPLEFT", view.gridPane, "TOPLEFT", ColumnLeft(index, width, name), 0)
        stripe:SetSize(width, math.max(1, #model.rows * GRID_ROW))
        stripe:Show()
    end
    for index = #model.runs + 1, #view.headers do
        view.headers[index]:Hide()
        view.stripes[index]:Hide()
    end
    view.gridElse:ClearAllPoints()
    view.gridElse:SetPoint("BOTTOMLEFT", view.gridHead, "BOTTOMLEFT", ColumnLeft(#model.runs + 1, width, name) + 6, 8)

    for index, piece in ipairs(model.rows) do
        local row = view.rows[index]
        if not row then
            row = CreateRow(view.gridPane)
            view.rows[index] = row
        end
        FillRow(row, piece, model, width, name)
        row:ClearAllPoints()
        row:SetPoint("TOPLEFT", view.gridPane, "TOPLEFT", 0, -(index - 1) * GRID_ROW)
        row:Show()
    end
    for index = #model.rows + 1, #view.rows do view.rows[index]:Hide() end
    return #model.rows * GRID_ROW + 4
end

---------------------------------------------------------------------------
-- The view
---------------------------------------------------------------------------

-- "8 best picks to farm  ·  6 dungeons  ·  2 already yours"
local function Summary(model)
    if model.need == 0 and model.got == 0 then return "" end
    local separator = GREY .. "  ·  |r"
    local got = model.got > 0 and (GREY .. L.DUN_GOT:format(model.got) .. "|r") or nil
    if model.need == 0 then return GOLD .. L.DUN_ALL_GOT .. "|r" end
    local text = WHITE .. (model.need == 1 and L.DUN_NEED_ONE or L.DUN_NEED:format(model.need)) .. "|r" .. separator
        .. WHITE .. (model.dungeons == 1 and L.DUN_RUNS_ONE or L.DUN_RUNS:format(model.dungeons)) .. "|r"
    return got and (text .. separator .. got) or text
end

-- The scroll bar shows only when there is something to scroll, once the frame has its size.
local function Fit(height)
    view.child:SetSize(WIDTH, math.max(1, height))
    if view.scroll.UpdateScrollChildRect then view.scroll:UpdateScrollChildRect() end
    local bar, room = view.scroll.ScrollBar, view.scroll:GetHeight()
    if bar and room and room > 0 then
        local needed = height > room + 1
        bar:SetShown(needed)
        if not needed and view.scroll.SetVerticalScroll then view.scroll:SetVerticalScroll(0) end
    end
end

function DungeonView.Create(parent)
    if view then return view end
    view = CreateFrame("Frame", nil, parent)
    DungeonView.view = view
    view:SetPoint("TOPLEFT", parent, "TOPLEFT", PAD, -PAD)
    view:SetPoint("BOTTOMRIGHT", parent, "BOTTOMRIGHT", -PAD, PAD)
    view:Hide()
    view.tiles, view.lanes, view.elsewhere, view.headers, view.stripes, view.rows = {}, {}, {}, {}, {}, {}
    view.runsByKey = {}

    view.summary = view:CreateFontString(nil, "OVERLAY", FONTS.name)
    view.summary:SetPoint("LEFT", view, "TOPLEFT", 6, -HEAD / 2 + 2)
    view.mode = Widgets.Segmented(view,
        { { value = "runs", text = L.DUN_VIEW_RUNS }, { value = "grid", text = L.DUN_VIEW_GRID } },
        function() return ns:GetOption("dungeonGrid") and "grid" or "runs" end,
        function(value) ns:SetOption("dungeonGrid", value == "grid") end)
    view.mode:SetPoint("RIGHT", view, "TOPRIGHT", -2, -HEAD / 2 + 2)

    -- the columns' names stay in place while the lines scroll
    view.gridHead = CreateFrame("Frame", nil, view)
    view.gridHead:SetPoint("TOPLEFT", view, "TOPLEFT", 0, -HEAD)
    view.gridHead:SetSize(WIDTH, GRID_HEAD)
    view.gridElse = view.gridHead:CreateFontString(nil, "OVERLAY", FONTS.text)
    view.gridElse:SetText(L.DUN_ELSEWHERE_COLUMN)
    view.gridElse:SetTextColor(MUTED[1], MUTED[2], MUTED[3])

    view.scroll, view.child = Widgets.Scroll(view)
    view.runsPane = CreateFrame("Frame", nil, view.child)
    view.runsPane:SetPoint("TOPLEFT", 0, 0)
    view.gridPane = CreateFrame("Frame", nil, view.child)
    view.gridPane:SetPoint("TOPLEFT", 0, 0)
    view.strip = view.runsPane:CreateTexture(nil, "BACKGROUND")   -- a line under the set
    view.strip:SetColorTexture(1, 1, 1, 0.08)
    view.strip:SetHeight(1)
    view.strip:SetPoint("TOPLEFT", 0, -(STRIP - 6))
    view.strip:SetPoint("TOPRIGHT", 0, -(STRIP - 6))
    view.elsewhereLabel = view.runsPane:CreateFontString(nil, "OVERLAY", FONTS.text)
    view.elsewhereLabel:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    view.empty = view.runsPane:CreateFontString(nil, "OVERLAY", FONTS.name)
    view.empty:SetWidth(WIDTH - 80)
    view.empty:SetTextColor(MUTED[1], MUTED[2], MUTED[3])

    -- what the player loots or puts on while the tab is open; a client without one of these events does without it
    for _, event in ipairs({ "BAG_UPDATE_DELAYED", "PLAYER_EQUIPMENT_CHANGED" }) do
        pcall(view.RegisterEvent, view, event)
    end
    view:SetScript("OnEvent", function(self)
        if self:IsShown() and self.state then DungeonView.Update(self.state) end
    end)
    return view
end

function DungeonView.Hide()
    if view then view:Hide() end
end

function DungeonView.Update(state)
    if not view then return end
    view:Show()
    view.state = state
    local model = Dungeons.For(state)
    view.model = model
    view.runsByKey = {}
    for _, run in ipairs(model.runs) do view.runsByKey[run.key] = run end

    local grid = ns:GetOption("dungeonGrid")
    view.grid = grid
    view.summary:SetText(Summary(model))
    view.mode:Refresh()
    view.gridHead:SetShown(grid)
    view.runsPane:SetShown(not grid)
    view.gridPane:SetShown(grid)
    view.scroll:ClearAllPoints()
    view.scroll:SetPoint("TOPLEFT", view, "TOPLEFT", 0, -(HEAD + (grid and GRID_HEAD or 0)))
    view.scroll:SetPoint("BOTTOMRIGHT", view, "BOTTOMRIGHT", -BAR_ROOM, 0)

    local height = grid and LayoutGrid(model) or LayoutRuns(model)
    view.runsPane:SetSize(WIDTH, math.max(1, height))
    view.gridPane:SetSize(WIDTH, math.max(1, height))
    Fit(height)
end
