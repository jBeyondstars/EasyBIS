local _, ns = ...
local L = ns.L
local Widgets = ns.Widgets
local Browser = ns.Browser

--[[
The Character tab of the window: the best pick of every slot, laid out as the
game's character sheet (UI\Rows.lua, Rows.Character).

  left     head, neck, shoulder, back, chest, wrist
  right    hands, waist, legs, feet, two rings, two trinkets
  bottom   main hand, off hand, ranged
  middle   the spec, the list and the phase; under them the player's own character wearing the set,
           turned by dragging, with the melee weapons in hand (a hunter: the ranged one; a player
           without Dual Wield: the main hand's alone). A client that cannot make the model shows the
           class's icon instead. Under the character, what is left to pay in a currency for the set.

A cell says the item's name in its quality's color, where it comes from in a
few words and, when one goes on the item, the best enchant of the phase. An
item behind a reputation says instead which one it asks for, or that the
player has earned it. Its tooltip is the list's, with the enchant and the
items that tie with it. A click opens the Items tab on that slot; Shift-click
and Ctrl-click do what they do on a row.

Under the character, the reputations the set asks of the player, recipes left
out: how many pieces each one already opens. A click opens the Reputations tab.

The view keeps its width. Extra height goes to the model and to the space
between cells; under the height it needs, the view is drawn smaller.

  Character.Create(parent)        the view, hidden
  Character.Update(state, room)   fills it. state: the window's { class, spec, list }; room: the height it has
  Character.Hide()
  Character.view                  (the tests read it: cells, title, subtitle, cost, model, crest, worn, reputations)
]]

local Character = {}
ns.Character = Character

local WIDTH = 928                     -- the window's width (960) is fixed, so is the view's
local PAD = 10                        -- between the view and what holds it
local ICON, FRAME = 36, 40            -- an item's picture, and the square in its quality's color around it
local GAP = 8                         -- between the picture and the texts
local COLUMN = 264                    -- a cell: the picture, then the texts
local TEXT_WIDTH = COLUMN - FRAME - GAP
local CELLS_HIGH = 8                  -- the right column, the longer one
local MIN_PITCH, MAX_PITCH = 46, 60   -- from a cell's top to the next one's
local WEAPONS = 56                    -- the bottom row, the line over it included
local HEAD = 40                       -- the title and the line under it, over the model
local COST_LINE = 16                  -- what is left to pay, under the model
local MIN_HEIGHT = CELLS_HIGH * MIN_PITCH + WEAPONS
local TURN = 0.012                    -- radians the model turns per pixel dragged
local SUMMARY_LINE = 16               -- a reputation's line under the character
local SUMMARY_WIDTH = 300
local SUMMARY_BOTTOM = WEAPONS + 16    -- over the line that says what the set still costs
local UNKNOWN_ICON = "Interface\\Icons\\INV_Misc_QuestionMark"
local CLASS_ICONS = "Interface\\GLUES\\CHARACTERCREATE\\UI-CharacterCreate-Classes"

local MUTED = Widgets.MUTED
local FAINT = { 0.45, 0.45, 0.48 }
local ENCHANT = { 0.35, 0.85, 0.45 }
local GREY = "|cff808080"
local GOLD = "|cffffd100"

-- What shows on a character: a necklace, a ring or a trinket does not.
local UNSEEN = { neck = true, finger = true, trinket = true }
-- The model holds the weapon tried on last, and a bow, a gun or a wand takes the melee weapons' place
-- in its hands: only a hunter is shown with it. The others hold what they fight with.
local AT_RANGE = { HUNTER = true }
-- The hand a weapon is tried on in, where the game lets us say it.
local HANDS = { main = "MAINHANDSLOT", off = "SECONDARYHANDSLOT" }
-- The weapons are tried on after the armour, in this order. The model is the player's own character:
-- without Dual Wield it keeps one of two one-handers, the one tried on last, so the main hand's comes
-- after the off hand's.
local WEAPON_ORDER = { off = 1, main = 2, ranged = 3 }

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

local view

---------------------------------------------------------------------------
-- Cells
---------------------------------------------------------------------------

local function CellTooltip(cell)
    local data = cell.data
    if not data then return end
    local side = cell.mirrored and "LEFT" or nil   -- the right column's open toward the model
    if data.id then
        Browser.ItemTooltip(cell, data, side)
        if data.enchant then
            GameTooltip:AddLine(L.TIP_ENCHANT:format(ns.Enchants.Name(data.enchant)),
                ENCHANT[1], ENCHANT[2], ENCHANT[3], true)
        end
        if data.ties[1] then
            local names = {}
            for index, id in ipairs(data.ties) do names[index] = ns.Items.Name(id) end
            GameTooltip:AddLine(L.TIP_TIES:format(table.concat(names, ", ")), MUTED[1], MUTED[2], MUTED[3], true)
        end
    else
        Browser.PlaceTooltip(cell, side)
        GameTooltip:SetText(ns.SlotName(data.slot), 1, 1, 1)
        GameTooltip:AddLine(data.twoHand and L.CHAR_TWO_HAND or L.CHAR_EMPTY, MUTED[1], MUTED[2], MUTED[3], true)
    end
    GameTooltip:AddLine(L.TIP_OPEN_SLOT, MUTED[1], MUTED[2], MUTED[3], true)
    Browser.ShowTooltip()
end

local function CellClick(cell)
    local data = cell.data
    if not data then return end
    if data.id and Browser.ModifiedClick(data.id) then return end
    Widgets.Click()
    Browser.ShowSlot(data.slot)
end

local function Text(cell, font)
    local text = cell:CreateFontString(nil, "OVERLAY", font)
    text:SetWidth(TEXT_WIDTH)
    text:SetJustifyH(cell.mirrored and "RIGHT" or "LEFT")
    text:SetWordWrap(false)
    return text
end

-- mirrored: the picture on the right and the texts running up to it, as in the sheet's right column.
local function CreateCell(parent, mirrored)
    local cell = CreateFrame("Button", nil, parent)
    cell:SetSize(COLUMN, FRAME)
    cell.mirrored = mirrored
    Widgets.ListHighlight(cell, "HIGHLIGHT", 0.30)

    local side = mirrored and "RIGHT" or "LEFT"
    cell.border = cell:CreateTexture(nil, "BACKGROUND")
    cell.border:SetSize(FRAME, FRAME)
    cell.border:SetPoint(side, cell, side, 0, 0)
    cell.back = cell:CreateTexture(nil, "BORDER")
    cell.back:SetSize(ICON, ICON)
    cell.back:SetPoint("CENTER", cell.border, "CENTER", 0, 0)
    cell.back:SetColorTexture(0.04, 0.04, 0.05, 1)
    cell.icon = cell:CreateTexture(nil, "ARTWORK")
    cell.icon:SetSize(ICON, ICON)
    cell.icon:SetPoint("CENTER", cell.border, "CENTER", 0, 0)
    cell.icon:SetTexCoord(0.08, 0.92, 0.08, 0.92)

    cell.name = Text(cell, "GameFontNormal")
    cell.where = Text(cell, "GameFontHighlightSmall")
    cell.enchant = Text(cell, "GameFontHighlightSmall")
    cell.enchant:SetTextColor(ENCHANT[1], ENCHANT[2], ENCHANT[3])

    cell:SetScript("OnEnter", CellTooltip)
    cell:SetScript("OnLeave", function() GameTooltip:Hide() end)
    cell:SetScript("OnClick", CellClick)
    return cell
end

-- Three lines fill the picture's height; two sit in its middle.
local LINES = { [true] = { -1, -15, -27 }, [false] = { -6, -21, -21 } }

local function PlaceTexts(cell, three)
    if cell.three == three then return end
    cell.three = three
    for index, text in ipairs({ cell.name, cell.where, cell.enchant }) do
        text:ClearAllPoints()
        if cell.mirrored then
            text:SetPoint("TOPRIGHT", cell.border, "TOPLEFT", -GAP, LINES[three][index])
        else
            text:SetPoint("TOPLEFT", cell.border, "TOPRIGHT", GAP, LINES[three][index])
        end
    end
end

local function FillCell(cell, data)
    cell.data = data
    local enchant = data.id and data.enchant or nil
    PlaceTexts(cell, enchant ~= nil)
    cell.enchant:SetShown(enchant ~= nil)
    cell.icon:SetShown(data.id ~= nil)
    if not data.id then
        cell.border:SetColorTexture(1, 1, 1, 0.12)
        cell.name:SetText(GREY .. ns.SlotName(data.slot) .. "|r")
        cell.where:SetText(data.twoHand and L.CHAR_TWO_HAND or L.CHAR_EMPTY)
        cell.where:SetTextColor(FAINT[1], FAINT[2], FAINT[3])
        return
    end

    local name, quality, texture, _
    if GetInfo then name, _, quality, _, _, _, _, _, _, texture = GetInfo(data.id) end
    local r, g, b, hex = ns.QualityColor(quality)
    cell.border:SetColorTexture(r, g, b, 0.9)
    cell.icon:SetTexture(texture or (GetIcon and GetIcon(data.id)) or UNKNOWN_ICON)
    local ties = data.ties[1] and (" " .. GREY .. "+" .. #data.ties .. "|r") or ""
    cell.name:SetText(hex .. (name or ns.Items.Name(data.id)) .. "|r"
        .. ns.Reputation.UnknownMark(data.reputation) .. ties)

    local source = data.source
    local mark = ns.Sources.OriginMark(source.origin)
    local where = ns.Sources.WithCost(ns.Sources.Short(source), source.cost)
        .. (mark ~= "" and (" " .. GREY .. mark .. "|r") or "")
    local requirement = data.reputation
    local earned = requirement and ns.Reputation.Status(requirement) == "met"
    if earned then where = GOLD .. L.REP_MET .. "|r " .. where end   -- first: a long source is what gets cut
    if requirement and not earned then
        cell.where:SetText(ns.Reputation.NeedText(requirement))
    else
        cell.where:SetText(ns.Sources.IconText(source.category) .. " " .. where)
    end
    cell.where:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    if enchant then cell.enchant:SetText("+ " .. ns.Enchants.ShortName(enchant)) end
end

---------------------------------------------------------------------------
-- The character in the middle
---------------------------------------------------------------------------

-- The player's character, turned by dragging it. nil where the client has no such frame.
local function CreateModel(parent)
    local ok, model = pcall(CreateFrame, "DressUpModel", nil, parent)
    if not ok or not model or not (model.SetUnit and model.TryOn and model.Undress) then return nil end
    model:EnableMouse(true)
    model:SetScript("OnMouseDown", function(self, button)
        if button == "LeftButton" then self.dragX = GetCursorPosition() end
    end)
    model:SetScript("OnMouseUp", function(self) self.dragX = nil end)
    model:SetScript("OnHide", function(self) self.dragX = nil end)
    model:SetScript("OnUpdate", function(self)
        if not self.dragX then return end
        if IsMouseButtonDown and not IsMouseButtonDown("LeftButton") then   -- let go outside the model
            self.dragX = nil
            return
        end
        local x = GetCursorPosition()
        self.facing = (self.facing or 0) + (x - self.dragX) * TURN
        self.dragX = x
        if self.SetFacing then self:SetFacing(self.facing) end
    end)
    return model
end

local function Shown(data, class)
    return data.id ~= nil and not UNSEEN[data.slot] and (data.slot ~= "ranged" or AT_RANGE[class] == true)
end

-- What the character wears, in the order it is put on: the armour in the cells' order, then the weapons.
local function Outfit(cells, class)
    local armour, weapons = {}, {}
    for _, data in ipairs(cells) do
        if Shown(data, class) then
            local list = WEAPON_ORDER[data.slot] and weapons or armour
            list[#list + 1] = data
        end
    end
    table.sort(weapons, function(a, b) return WEAPON_ORDER[a.slot] < WEAPON_ORDER[b.slot] end)
    for _, data in ipairs(weapons) do armour[#armour + 1] = data end
    return armour
end

-- Puts the set on the character. The game only tries on an item it has loaded: the set is put on
-- again once more of it has arrived, and left alone while nothing changed.
local function Dress(cells, class)
    local model = view.model
    if not model then return end
    local outfit = Outfit(cells, class)
    local parts = { class or "" }
    for _, data in ipairs(outfit) do
        parts[#parts + 1] = data.id .. ((GetInfo and GetInfo(data.id)) and "" or "?")
    end
    local set = table.concat(parts, " ")
    if set == view.worn then return end
    view.worn = set
    model:SetUnit("player")
    model:Undress()
    for _, data in ipairs(outfit) do
        local link, hand = "item:" .. data.id, HANDS[data.slot]
        if not (hand and pcall(model.TryOn, model, link, hand)) then pcall(model.TryOn, model, link) end
    end
    if model.facing and model.SetFacing then model:SetFacing(model.facing) end
end

-- Without the model: the icon of the class being looked at.
local function ShowCrest(class)
    local coords = CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS[class]
    view.crest:SetShown(coords ~= nil)
    if coords then view.crest:SetTexCoord(coords[1], coords[2], coords[3], coords[4]) end
end

---------------------------------------------------------------------------
-- The reputations of the set
---------------------------------------------------------------------------

local function SummaryLine(index)
    local line = view.reputations[index]
    if line then return line end
    line = CreateFrame("Button", nil, view)
    view.reputations[index] = line
    line:SetSize(SUMMARY_WIDTH, SUMMARY_LINE)
    line:SetFrameLevel(view:GetFrameLevel() + 5)   -- over the character
    Widgets.ListHighlight(line, "HIGHLIGHT", 0.30)
    line.label = line:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    line.label:SetPoint("LEFT", 6, 0)
    line.label:SetPoint("RIGHT", -64, 0)
    line.label:SetJustifyH("LEFT")
    line.label:SetWordWrap(false)
    line.count = line:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    line.count:SetPoint("RIGHT", -6, 0)
    line:SetScript("OnClick", function(self)
        Widgets.Click()
        Browser.ShowReputation(self.factionID)
    end)
    line:SetScript("OnEnter", function(self)
        Browser.PlaceTooltip(self)
        GameTooltip:SetText(ns.Reputation.FactionName(self.factionID), 1, 1, 1)
        GameTooltip:AddLine(L.REP_YOU:format(ns.Reputation.ProgressText(self.factionID)),
            MUTED[1], MUTED[2], MUTED[3], true)
        GameTooltip:AddLine(L.TIP_OPEN_REPUTATION, MUTED[1], MUTED[2], MUTED[3], true)
        Browser.ShowTooltip()
    end)
    line:SetScript("OnLeave", function() GameTooltip:Hide() end)
    return line
end

local function ShowSummary(cells)
    local summary = ns.Reputation.Summary(cells)
    for index, entry in ipairs(summary) do
        local line = SummaryLine(index)
        line.factionID = entry.factionID
        line:ClearAllPoints()
        line:SetPoint("BOTTOM", view, "BOTTOM", 0, SUMMARY_BOTTOM + (#summary - index) * SUMMARY_LINE)
        line.label:SetText(entry.name)
        local done = entry.met == entry.total
        line.count:SetText((done and GOLD or "|cffffffff") .. entry.met .. " / " .. entry.total .. "|r")
        line:Show()
    end
    for index = #summary + 1, #view.reputations do view.reputations[index]:Hide() end
    view.reputationTitle:SetShown(summary[1] ~= nil)
    view.reputationTitle:ClearAllPoints()
    view.reputationTitle:SetPoint("BOTTOM", view, "BOTTOM", 0, SUMMARY_BOTTOM + #summary * SUMMARY_LINE + 2)
    view.reputationData = summary
end

---------------------------------------------------------------------------
-- The view
---------------------------------------------------------------------------

-- What is left to pay for the set; nothing when it asks for no currency, or all of it is owned.
local function ShowCost(cells)
    local lines = {}
    for index, owed in ipairs(ns.Sources.ToPay(cells)) do lines[index] = ns.Sources.ToPayLine(owed) end
    view.cost:SetText(table.concat(lines, "  "))
    view.cost:SetShown(lines[1] ~= nil)
end

function Character.Create(parent)
    if view then return view end
    view = CreateFrame("Frame", nil, parent)
    Character.view = view
    view.parent = parent
    view:Hide()
    view.cells = {}

    view.title = view:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    view.title:SetPoint("TOP", view, "TOP", 0, -2)
    view.subtitle = view:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    view.subtitle:SetPoint("TOP", view.title, "BOTTOM", 0, -3)
    view.subtitle:SetTextColor(MUTED[1], MUTED[2], MUTED[3])

    view.cost = view:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    view.cost:SetPoint("BOTTOM", view, "BOTTOM", 0, WEAPONS + 1)
    view.cost:SetWidth(WIDTH - 2 * (COLUMN + GAP))
    view.cost:SetWordWrap(false)
    view.cost:SetTextColor(1, 0.82, 0)
    view.cost:Hide()

    view.line = view:CreateTexture(nil, "BACKGROUND")
    view.line:SetColorTexture(1, 1, 1, 0.08)
    view.line:SetHeight(1)
    view.line:SetPoint("BOTTOMLEFT", view, "BOTTOMLEFT", 0, WEAPONS - 8)
    view.line:SetPoint("BOTTOMRIGHT", view, "BOTTOMRIGHT", 0, WEAPONS - 8)

    view.model = CreateModel(view)
    if view.model then
        view.model:SetPoint("TOPLEFT", view, "TOPLEFT", COLUMN + GAP, -HEAD)
        view.model:SetPoint("BOTTOMRIGHT", view, "BOTTOMRIGHT", -(COLUMN + GAP), WEAPONS + COST_LINE)
    else
        view.crest = view:CreateTexture(nil, "ARTWORK")
        view.crest:SetSize(96, 96)
        view.crest:SetPoint("CENTER", view, "CENTER", 0, (WEAPONS - HEAD) / 2)
        view.crest:SetTexture(CLASS_ICONS)
    end
    -- a model that was hidden may have lost what it wore
    view:SetScript("OnHide", function(self) self.worn = nil end)

    view.reputations = {}
    view.reputationTitle = view:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    view.reputationTitle:SetText(L.REP_SHEET_TITLE)
    view.reputationTitle:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    -- what the player buys or loots while the sheet is open; a client without one of these events does without it
    for _, event in ipairs({ "BAG_UPDATE_DELAYED", "CURRENCY_DISPLAY_UPDATE", "PLAYER_EQUIPMENT_CHANGED" }) do
        pcall(view.RegisterEvent, view, event)
    end
    view:SetScript("OnEvent", function(self)
        if self:IsShown() and self.cellData then ShowCost(self.cellData) end
    end)
    return view
end

function Character.Hide()
    if view then view:Hide() end
end

function Character.Update(state, room)
    if not view then return end
    local height, scale = math.max(1, (room or 0) - 2 * PAD), 1
    if height < MIN_HEIGHT then scale, height = height / MIN_HEIGHT, MIN_HEIGHT end
    local pitch = math.min(MAX_PITCH, math.floor((height - WEAPONS) / CELLS_HIGH))
    view:SetScale(scale)
    view:SetSize(WIDTH, height)
    view:ClearAllPoints()
    view:SetPoint("TOP", view.parent, "TOP", 0, -PAD / scale)
    view:Show()

    local r, g, b = ns.ClassColor(state.class)
    view.title:SetText(("|cff%02x%02x%02x%s|r %s"):format(math.floor(r * 255), math.floor(g * 255),
        math.floor(b * 255), ns.ClassName(state.class), ns.SpecName(ns.Index.SpecName(state.class, state.spec) or "")))
    local subtitle = ns.ListLongName(state.list) .. " - " .. ns.PhaseName(ns.Phase())
    if ns:GetOption("availableNow") then subtitle = subtitle .. " - " .. ns.L.RANK_CAP_SHORT:format(ns.RankCap()) end
    view.subtitle:SetText(subtitle)

    local cells = ns.Rows.Character(state)
    local placed = { left = 0, right = 0, bottom = 0 }
    for index, data in ipairs(cells) do
        local cell = view.cells[index]
        if not cell then
            cell = CreateCell(view, data.place == "right")
            view.cells[index] = cell
        end
        local count = placed[data.place]
        placed[data.place] = count + 1
        cell:ClearAllPoints()
        if data.place == "left" then
            cell:SetPoint("TOPLEFT", view, "TOPLEFT", 0, -count * pitch)
        elseif data.place == "right" then
            cell:SetPoint("TOPRIGHT", view, "TOPRIGHT", 0, -count * pitch)
        else
            cell:SetPoint("BOTTOMLEFT", view, "BOTTOMLEFT", count * (WIDTH - COLUMN) / 2, 0)
        end
        FillCell(cell, data)
        cell:Show()
    end
    for index = #cells + 1, #view.cells do view.cells[index]:Hide() end
    view.cellData = cells
    ShowSummary(cells)
    ShowCost(cells)

    if view.model then Dress(cells, state.class) else ShowCrest(state.class) end
end
