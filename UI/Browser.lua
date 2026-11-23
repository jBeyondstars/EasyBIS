local _, ns = ...
local L = ns.L
local Widgets = ns.Widgets

--[[
The Easy BIS window: the best gear of a spec, slot by slot.

  top      filters: spec, list (PvE, PvP), phase, slot, source, zone, reputation. A filter that narrows
           the list down is gold; the others stay quiet. On the Consumables tab the slot filter is a category
           filter.
  notice   a band under the filters while a known problem awaits its fix (NOTICE), with a cross that puts it
           away until the window is opened again and gives its room to the list; none otherwise, and the
           middle takes its room.
  middle   the rows (UI\Rows.lua). An item or a consumable takes one line: icon, name, score bar and rank,
           type or effect, where it comes from. With the option "compact" off it takes two, as an enchant
           always does. What a reputation stands in front of says so under where it comes from. Over the
           scores of each item slot, a mark says in a tooltip how the list is ranked (Browser.ScoreInfo).
           After the score of a few items, the same mark says a word on a rank that may surprise (Notes.lua).
           The Character tab shows the best pick of every slot as a character sheet instead
           (UI\Character.lua), the Reputations tab what the spec needs of each faction
           (UI\Reputations.lua): both follow the spec, the list and the phase, and have no other filter.
  bottom   Items / Enchants / Character / Consumables / Reputations, "Add an item" (UI\AddItem.lua),
           the alternatives switch and the options menu. The data credit sits below this row. The grip
           in the corner changes the window's height.
  side     two tabs down the right edge, as the game's professions have them: the lists (all of the above),
           and the dungeons, which dungeons hold the spec's best picks (UI\Dungeons.lua). The dungeons take
           the whole middle and follow the spec, the list, the phase and the alternatives switch; the tabs
           of the bottom are the lists' and go while the dungeons show.

The class, spec, list and phase are remembered per character; the other
filters last until the window is rebuilt (a reload). The phase is not the
window's alone: tooltips follow it too (ns.Phase). Changing a filter leaves
the list scrolled where it was. Hover a row for the item's tooltip, which
opens beside the window; Shift-click links the item in chat.

  Browser.Toggle(), Browser.Open(), Browser.Close()
  Browser.Target()                class, spec, list: what the window shows, or will show once opened
  Browser.SpecFilter(parent)      the spec filter and the list filter (with its label, .label), for the
  Browser.ListFilter(parent)      window and for the auction house's tab: both set the same choice;
                                  :Refresh() shows it
  Browser.ShowSlot(slot)          the Items tab, on that slot alone
  Browser.ShowSource(category)    the Items tab, on what comes from that kind of source
  Browser.ShowDungeons()          the dungeons
  Browser.Font(name, base, size)  a font object: one of the game's, at another size
  Browser.ShowReputation(factionID, artisan)   the Reputations tab, on that faction
  Browser.EnchantTooltip(owner, enchant, requirement)   an enchant's tooltip beside the window; the caller shows it
  Browser.PlaceTooltip(owner, side)  the game's tooltip, owned by a part of the window and set beside
                                  it; side "LEFT": against the owner's left edge, inside the window
  Browser.ItemTooltip(owner, data, side)   an item's tooltip there, with where it comes from in full;
                                  data: an item row, or anything with id and source
  Browser.ShowTooltip(owner)      shows it once its lines are set (the caller does): the comparison with
                                  the gear worn waits for Shift; owner: a frame outside the window whose
                                  tooltip follows the same rule (the add dialog's suggestions)
  Browser.ModifiedClick(id)       Shift-click, Ctrl-click on an item: true when a modifier key was held
  Browser.state, Browser.window   (the tests read them)
]]

local Browser = {}
ns.Browser = Browser

local WINDOW_NAME = "EasyBISWindow"
local WIDTH, HEIGHT = 960, 620
local MIN_HEIGHT, MAX_HEIGHT = 380, 1400
-- A notice under the filters while a known problem awaits its fix: the key of its text, nil when there is none.
local NOTICE = "NOTICE_ITEMS"
local NOTICE_HEIGHT, NOTICE_GAP = 24, 4   -- its band, and the room between it and the list
local NOTICE_MARK = "|TInterface\\DialogFrame\\UI-Dialog-Icon-AlertNew:16:16:0:0|t "
local FILTERS, INSET_BOTTOM = 70, 58   -- what the filters and the footer take of the window's height
local FOOTER_BUTTON_BOTTOM = 24   -- room for the credit below and the corner badge above
local NOTICE_CLOSE = "Interface\\Buttons\\UI-StopButton"   -- the cross that puts the notice away
local noticeShown = NOTICE ~= nil   -- false once its cross is clicked, until the window is opened again

-- Where the list starts: under the filters, and under the notice while it shows.
local function InsetTop()
    return FILTERS + (noticeShown and NOTICE_HEIGHT + NOTICE_GAP or 0)
end
local ROW_HEIGHT = 54      -- a row on two lines
local COMPACT_HEIGHT = 36  -- an item or a consumable on one line
local REPUTATION_LINE = 16 -- what a reputation adds to a row on two lines; a row on one keeps its height
local COMPACT_SHIFT = 7    -- on one line: how far where it comes from and the reputation sit from the middle
local HEADER_HEIGHT = 38   -- a slot's name over its rows; the text sits at the bottom, the rest is spacing
local NOTE_HEIGHT = 28     -- a line of plain text between rows
local ICON, COMPACT_ICON = 44, 30   -- the item's picture, on two lines and on one
local SOURCE_ICON = 16     -- the picture of where it comes from
local BAR_WIDTH = 52       -- the score bar
local LINE_ONE = 17        -- on two lines: how far under the row's top the first line's middle is
local TOOLTIP_ROOM = 340 + Widgets.SIDE_ROOM   -- room a tooltip needs on the window's right, past the side tabs;
--                                                without it, it opens on the left
local DUNGEON_ICON = "Interface\\Icons\\INV_Misc_Bone_HumanSkull_01"   -- the side tab of the dungeons
local ALL = "*"            -- the "all" choice of a filter
local UNKNOWN_ICON = "Interface\\Icons\\INV_Misc_QuestionMark"
local INFO_ICON = "Interface\\FriendsFrame\\InformationIcon"   -- over the scores: what a score is

-- Where a row's parts start, from its left edge.
local WIDE = { rank = 392, source = 512 }                -- name and type | where it comes from, on two lines
local COMPACT = { rank = 318, type = 432, source = 622 }  -- name | rank | type | where it comes from

-- The rows' fonts: the game's own, two points larger, so a list reads at a glance. A client without
-- CreateFont keeps the game's.
local function RowFont(name, base, size)
    local model = _G[base]
    if not (CreateFont and model and model.GetFont) then return base end
    local path, _, flags = model:GetFont()
    if not path then return base end
    local font = _G[name] or CreateFont(name)
    font:CopyFontObject(model)
    font:SetFont(path, size, flags or "")
    return name
end
local FONT_NAME = RowFont("EasyBISRowName", "GameFontNormal", 14)            -- the item's name
local FONT_TEXT = RowFont("EasyBISRowText", "GameFontHighlightSmall", 12)    -- its type, rank and source
local FONT_HEADER = RowFont("EasyBISRowHeader", "GameFontNormalLarge", 18)   -- a slot's name

local MUTED = Widgets.MUTED
local GOLD_TEXT, GREY_TEXT = "|cffffd100", "|cffc0c0c0"

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

local window
local state = { tab = "items", page = "lists" }   -- page: the side tab chosen, "lists" or "dungeons"
Browser.state = state
local Refresh

---------------------------------------------------------------------------
-- Small helpers
---------------------------------------------------------------------------

local function HasTemplate(name)
    return C_XMLUtil ~= nil and C_XMLUtil.GetTemplateInfo ~= nil and C_XMLUtil.GetTemplateInfo(name) ~= nil
end

local function QualityHex(quality)
    local _, _, _, hex = ns.QualityColor(quality)
    return hex
end

-- "BIS", "Tied", "-12%", "Added", "Estimated" (placed, no score of its own); an enchant has no score, so its alternatives read "Alt". A consumable is
-- the best of its category and nothing more, so it never reads "BIS".
local function RankText(row)
    if row.option then return GOLD_TEXT .. row.option.label .. "|r" end
    if row.unranked then return GREY_TEXT .. L.RANK_UNRANKED .. "|r" end
    if row.kind == "consumable" and row.bis then return GOLD_TEXT .. L.RANK_BEST .. "|r" end
    if row.custom then return ns.COLOR .. L.RANK_CUSTOM .. "|r" end
    if row.placed then return GREY_TEXT .. L.RANK_PLACED .. "|r" end
    if row.level then return GREY_TEXT .. L.RANK_SITUATIONAL .. "|r" end
    if row.estimated then return "" end   -- its score is no full measure: no figure is shown for it
    if row.bis then return GOLD_TEXT .. L.RANK_BIS .. "|r" end
    if row.tie then return GOLD_TEXT .. L.RANK_TIE .. "|r" end
    if row.gap == nil then return GREY_TEXT .. L.RANK_ALT .. "|r" end
    if row.gap < 0 then return GREY_TEXT .. L.GAP:format(row.gap) .. "|r" end
    return GREY_TEXT .. L.GAP_NONE .. "|r"   -- behind, by less than half a percent
end

-- A picture of Sources.Icon: a square icon loses its border.
local function SetIcon(texture, path, cropped)
    texture:SetTexture(path)
    if cropped then
        texture:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    else
        texture:SetTexCoord(0, 1, 0, 1)
    end
end

---------------------------------------------------------------------------
-- What the window shows: the character's last choice, or its own class
---------------------------------------------------------------------------

local function SavedChoice()
    local saved = ns.char
    local class = saved.class or ns.PlayerClass() or ns.CLASSES[1]
    if ns.Index.SpecCount(class) == 0 then class = ns.CLASSES[1] end
    local spec = saved.spec or 1
    if not ns.Index.SpecName(class, spec) then spec = 1 end
    return class, spec, saved.list == "pvp" and "pvp" or "pve"
end

local function LoadState()
    state.class, state.spec, state.list = SavedChoice()
end

local function SaveState()
    ns.char.class, ns.char.spec, ns.char.list = state.class, state.spec, state.list
    ns:Fire("TARGET_CHANGED")
end

function Browser.Target()
    if state.class then return state.class, state.spec, state.list end
    return SavedChoice()
end

---------------------------------------------------------------------------
-- Menus: a list of choices, some with children. Without the game's menu
-- API, each click moves to the next choice.
---------------------------------------------------------------------------

local function Flatten(choices, into)
    for _, choice in ipairs(choices) do
        if choice.children then Flatten(choice.children, into) else into[#into + 1] = choice end
    end
    return into
end

local function ChoiceEntries(list, current, choose)
    local entries = {}
    for _, choice in ipairs(list) do
        if choice.children then
            entries[#entries + 1] = { text = choice.text, items = ChoiceEntries(choice.children, current, choose) }
        else
            entries[#entries + 1] = { kind = "radio", text = choice.text,
                selected = function() return current() == choice.value end,
                pick = function() choose(choice.value) end }
        end
    end
    return entries
end

local function SetupChoices(button, choices, current, choose)
    if MenuUtil then
        ns.Menu.Attach(button, function() return ChoiceEntries(choices(), current, choose) end)
        return
    end
    button:SetScript("OnClick", function()
        Widgets.Click()
        local flat = Flatten(choices(), {})
        for index, choice in ipairs(flat) do
            if choice.value == current() then
                choose(flat[index % #flat + 1].value)
                return
            end
        end
        if flat[1] then choose(flat[1].value) end
    end)
end

local function SpecKey(class, spec)
    return class .. ":" .. spec
end

local function ClassHex(class)
    local r, g, b = ns.ClassColor(class)
    return ("|cff%02x%02x%02x"):format(math.floor(r * 255), math.floor(g * 255), math.floor(b * 255))
end

local function SpecChoices()
    local choices = {}
    local function AddClass(class)
        local order = ns.Index.SpecOrder(class)
        if not order[1] then return end
        local children = {}
        for _, spec in ipairs(order) do
            children[#children + 1] = {
                text = ns.SpecName(ns.Index.SpecName(class, spec)),
                value = SpecKey(class, spec),
            }
        end
        choices[#choices + 1] = { text = ClassHex(class) .. ns.ClassName(class) .. "|r", children = children }
    end
    local mine = ns.PlayerClass()
    if mine then AddClass(mine) end
    for _, class in ipairs(ns.CLASSES) do
        if class ~= mine then AddClass(class) end
    end
    return choices
end

local function PhaseChoices()
    local choices = {}
    for _, phase in ipairs(ns.data and ns.data.meta and ns.data.meta.phases or {}) do
        choices[#choices + 1] = { text = phase == 9 and L.PHASE_ALL_LONG or ns.PhaseName(phase), value = phase }
    end
    return choices
end

local function SlotChoices()
    local choices = { { text = L.ALL_SLOTS, value = ALL } }
    for _, slot in ipairs(ns.SLOTS) do
        choices[#choices + 1] = { text = ns.SlotName(slot), value = slot }
    end
    return choices
end

local function CategoryChoices()
    local choices = { { text = L.ALL_CATEGORIES, value = ALL } }
    for _, group in ipairs(ns.Consumables.For(state.class, state.spec, state.list)) do
        choices[#choices + 1] = { text = ns.Consumables.KeyName(group.key), value = group.key }
    end
    return choices
end

-- Each category with its picture: the menu is also where the pictures are explained.
local function SourceChoices(facets)
    local choices = { { text = L.ALL_SOURCES, value = ALL } }
    for _, category in ipairs(ns.Sources.CATEGORIES) do
        if facets.sources[category] then
            choices[#choices + 1] = {
                text = ns.Sources.IconText(category) .. " " .. ns.Sources.CategoryName(category),
                value = category,
            }
        end
    end
    return choices
end

local function ZoneChoices(facets)
    local names = {}
    for name in pairs(facets.zones) do names[#names + 1] = name end
    table.sort(names)
    local choices = { { text = L.ALL_ZONES, value = ALL } }
    for _, name in ipairs(names) do
        choices[#choices + 1] = { text = name, value = name }
    end
    return choices
end

local REPUTATION_NAMES = { ok = "REP_FILTER_OK", todo = "REP_FILTER_TODO" }

local function ReputationChoices()
    return {
        { text = L.REP_FILTER_ALL, value = ALL },
        { text = L.REP_FILTER_OK, value = "ok" },
        { text = L.REP_FILTER_TODO, value = "todo" },
    }
end

---------------------------------------------------------------------------
-- The window
---------------------------------------------------------------------------

-- Where the window sits and how tall it is, for the next time.
local function SavePlace(frame)
    local point, _, relativePoint, x, y = frame:GetPoint(1)
    if point then ns.db.window = { point, relativePoint, x, y } end
    local height = frame:GetHeight()
    if height and height >= MIN_HEIGHT then ns.db.windowHeight = math.floor(height + 0.5) end
end

-- The window's title: the addon's name, and the faction of the lists when it is not the character's.
local function ShowTitle(frame)
    local text = L.ADDON_TITLE
    if ns.PlayerSide() ~= ns.CharacterSide() then
        text = L.TITLE_SIDE:format(L.ADDON_TITLE, L["SIDE_" .. ns.PlayerSide()])
    end
    if frame.SetTitle then
        frame:SetTitle(text)
    elseif frame.TitleContainer and frame.TitleContainer.TitleText then
        frame.TitleContainer.TitleText:SetText(text)
    elseif frame.titleText then
        frame.titleText:SetText(text)
    end
    frame.titleShown = text
end

local function CreateWindow()
    local modern = HasTemplate("PortraitFrameTemplate")
    local frame = CreateFrame("Frame", WINDOW_NAME, UIParent, modern and "PortraitFrameTemplate" or "BackdropTemplate")
    frame:Hide()
    local height = ns.db.windowHeight
    if type(height) ~= "number" or height < MIN_HEIGHT then height = HEIGHT end
    frame:SetSize(WIDTH, math.min(height, MAX_HEIGHT))
    frame:SetFrameStrata("HIGH")
    frame:SetToplevel(true)
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:RegisterForDrag("LeftButton")
    if frame.SetDontSavePosition then frame:SetDontSavePosition(true) end
    frame:SetScript("OnDragStart", frame.StartMoving)
    frame:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        SavePlace(self)
    end)
    table.insert(UISpecialFrames, WINDOW_NAME)

    if modern then
        if frame.SetPortraitToAsset then
            frame:SetPortraitToAsset(ns.PORTRAIT)
        elseif frame.SetPortraitTextureRaw then
            frame:SetPortraitTextureRaw(ns.PORTRAIT)
        end
    else
        frame:SetBackdrop(Widgets.FLAT)
        frame:SetBackdropColor(0.05, 0.05, 0.06, 0.97)
        frame:SetBackdropBorderColor(0.3, 0.3, 0.32, 1)
        local close = CreateFrame("Button", nil, frame, "UIPanelCloseButton")
        close:SetPoint("TOPRIGHT", 2, 2)
        frame.titleText = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
        frame.titleText:SetPoint("TOP", 0, -8)
    end
    ShowTitle(frame)

    local saved = ns.db.window
    if type(saved) == "table" and type(saved[1]) == "string" and type(saved[3]) == "number" and type(saved[4]) == "number" then
        frame:SetPoint(saved[1], UIParent, type(saved[2]) == "string" and saved[2] or saved[1], saved[3], saved[4])
    else
        frame:SetPoint("CENTER", UIParent, "CENTER", 0, 20)
    end
    return frame
end

-- The grip in the bottom right corner: the window keeps its width, its height follows the mouse.
local function CreateGrip(frame)
    if not (frame.SetResizable and frame.StartSizing) then return nil end
    frame:SetResizable(true)
    if frame.SetResizeBounds then
        frame:SetResizeBounds(WIDTH, MIN_HEIGHT, WIDTH, MAX_HEIGHT)
    else
        if frame.SetMinResize then frame:SetMinResize(WIDTH, MIN_HEIGHT) end
        if frame.SetMaxResize then frame:SetMaxResize(WIDTH, MAX_HEIGHT) end
    end
    local grip = CreateFrame("Button", nil, frame)
    grip:SetSize(16, 16)
    grip:SetPoint("BOTTOMRIGHT", -8, 26)
    grip:SetNormalTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Up")
    grip:SetHighlightTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Highlight")
    grip:SetPushedTexture("Interface\\ChatFrame\\UI-ChatIM-SizeGrabber-Down")
    grip:SetScript("OnMouseDown", function() frame:StartSizing("BOTTOMRIGHT") end)
    grip:SetScript("OnMouseUp", function()
        frame:StopMovingOrSizing()
        SavePlace(frame)
        Refresh()
    end)
    return grip
end

local function CreateInset(parent)
    if HasTemplate("InsetFrameTemplate") then
        return CreateFrame("Frame", nil, parent, "InsetFrameTemplate")
    end
    local inset = CreateFrame("Frame", nil, parent, "BackdropTemplate")
    inset:SetBackdrop(Widgets.FLAT)
    inset:SetBackdropColor(0, 0, 0, 0.35)
    inset:SetBackdropBorderColor(1, 1, 1, 0.1)
    return inset
end

-- A band across the window: one line of text over amber, after the game's alert mark.
local function CreateNotice(parent, text)
    local notice = CreateFrame("Frame", nil, parent, "BackdropTemplate")
    notice:SetBackdrop(Widgets.FLAT)
    notice:SetBackdropColor(0.32, 0.20, 0.02, 0.92)
    notice:SetBackdropBorderColor(1, 0.72, 0.10, 0.9)
    notice:SetHeight(NOTICE_HEIGHT)
    notice.text = notice:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    notice.text:SetPoint("LEFT", 26, 0)
    notice.text:SetPoint("RIGHT", -26, 0)   -- clear of the cross, and as far from the left edge: the text stays centered
    notice.text:SetJustifyH("CENTER")
    notice.text:SetWordWrap(false)
    notice.text:SetText(NOTICE_MARK .. text)
    notice.close = CreateFrame("Button", nil, notice)
    notice.close:SetSize(14, 14)
    notice.close:SetPoint("RIGHT", -6, 0)
    notice.close:SetNormalTexture(NOTICE_CLOSE)
    notice.close:SetHighlightTexture(NOTICE_CLOSE, "ADD")
    notice.close:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(L.NOTICE_HIDE, 1, 1, 1, 1, true)
        GameTooltip:Show()
    end)
    notice.close:SetScript("OnLeave", ns.Tooltip.HideOwned)
    return notice
end

-- Shows the notice or puts it away, and starts the list under what shows.
local function PlaceNotice()
    if window.notice then window.notice:SetShown(noticeShown) end
    window.inset:ClearAllPoints()
    window.inset:SetPoint("TOPLEFT", 6, -InsetTop())
    window.inset:SetPoint("BOTTOMRIGHT", -6, INSET_BOTTOM)
end

---------------------------------------------------------------------------
-- Rows
---------------------------------------------------------------------------

-- The game can set what the character wears beside an item's tooltip (its option "always compare
-- items"), and it puts that comparison on the side with room: over the window. The window's tooltips
-- show it only while Shift is held, as the game does without that option.
local COMPARISONS = { "ShoppingTooltip1", "ShoppingTooltip2" }
local tipOwner   -- the part of the window the tooltip was last set for
local shiftWatch = CreateFrame("Frame")
shiftWatch:Hide()

local function OursShown()
    return tipOwner ~= nil and not (GameTooltip.IsForbidden and GameTooltip:IsForbidden())
        and GameTooltip:IsShown() and GameTooltip:GetOwner() == tipOwner
end

local function ShiftDown() return IsShiftKeyDown ~= nil and IsShiftKeyDown() == true end

local function IsOurComparison(tip)
    return tip and not (tip.IsForbidden and tip:IsForbidden()) and tip:IsShown() and tip:GetOwner() == GameTooltip
end

local function HideComparison()
    for _, name in ipairs(COMPARISONS) do
        local tip = _G[name]
        if IsOurComparison(tip) then tip:Hide() end
    end
end

local function ComparisonShown()
    local tip = _G[COMPARISONS[1]]
    return IsOurComparison(tip)
end

-- Shift pressed or let go over a tooltip of the window: the comparison follows.
local function FollowShift()
    if not OursShown() then return end
    if not ShiftDown() then
        HideComparison()
    elseif not ComparisonShown() and GameTooltip_ShowCompareItem then
        pcall(GameTooltip_ShowCompareItem, GameTooltip)
    end
end

-- Blizzard can refresh the comparison while the row is hovered. Watch only
-- during that hover, without installing an update script on the shared tooltip.
shiftWatch:SetScript("OnUpdate", function(self)
    if not OursShown() then
        tipOwner = nil
        self:Hide()
    elseif not ShiftDown() then
        HideComparison()
    end
end)
shiftWatch:SetScript("OnShow", function(self) self:RegisterEvent("MODIFIER_STATE_CHANGED") end)
shiftWatch:SetScript("OnHide", function(self) self:UnregisterEvent("MODIFIER_STATE_CHANGED") end)
shiftWatch:SetScript("OnEvent", FollowShift)

-- The tooltip opens beside the window, level with its top, on the side that has room: it stays put
-- from row to row and never climbs off the screen. side "LEFT": against the owner's left edge
-- instead, inside the window (the right column of the character sheet).
local function PlaceTooltip(owner, side)
    tipOwner = owner
    GameTooltip:SetOwner(owner, "ANCHOR_NONE")
    GameTooltip:ClearAllPoints()
    local right, edge = window:GetRight(), UIParent:GetRight()
    if side == "LEFT" then
        GameTooltip:SetPoint("TOPRIGHT", owner, "TOPLEFT", -4, 0)
    elseif right and edge and edge - right < TOOLTIP_ROOM then
        GameTooltip:SetPoint("TOPRIGHT", window, "TOPLEFT", -2, -24)
    else
        GameTooltip:SetPoint("TOPLEFT", window, "TOPRIGHT", Widgets.SIDE_ROOM, -24)   -- clear of the side tabs
    end
end

-- Shows the tooltip once its lines are set, without the comparison unless Shift is held.
local function ShowTooltip(owner)
    if owner then tipOwner = owner end
    GameTooltip:Show()
    if not OursShown() then return end
    shiftWatch:Show()
    if ShiftDown() then FollowShift() else HideComparison() end
end

local function ItemTooltip(owner, data, side)
    PlaceTooltip(owner, side)
    pcall(GameTooltip.SetItemByID, GameTooltip, data.id)
    if GameTooltip:NumLines() == 0 then GameTooltip:SetText(ns.Items.Name(data.id), 1, 1, 1) end
    -- what a row shortens or leaves to a picture, in full
    local source = data.source
    local line = ns.Sources.Line(source)
    local where = ns.Sources.CategoryName(source.category) .. (line ~= "" and (" - " .. line) or "")
    GameTooltip:AddLine(" ")
    GameTooltip:AddLine(L.TIP_SOURCE:format(where), 1, 0.82, 0, true)
    if source.cost then
        GameTooltip:AddLine(ns.Sources.CostLine(source.cost), 1, 0.82, 0, true)
        if source.cost.beta then GameTooltip:AddLine(L.TIP_COST_BETA, MUTED[1], MUTED[2], MUTED[3], true) end
    end
    local remark = ns.Sources.OriginRemark(source.origin)
    if remark then GameTooltip:AddLine(remark, MUTED[1], MUTED[2], MUTED[3], true) end
    local unsure = ns.Reputation.UnknownRemark(data.reputation)
    if unsure then GameTooltip:AddLine(unsure, MUTED[1], MUTED[2], MUTED[3], true) end
    if data.option then
        GameTooltip:AddLine(ns.Ladders.OptionNote(data.option), 1, 0.82, 0, true)
    elseif data.custom then
        GameTooltip:AddLine(L.TIP_CUSTOM, MUTED[1], MUTED[2], MUTED[3], true)
    elseif data.placed then
        GameTooltip:AddLine(L.TIP_PLACED, MUTED[1], MUTED[2], MUTED[3], true)
    elseif data.level then
        GameTooltip:AddLine(L.TIP_LEVEL, MUTED[1], MUTED[2], MUTED[3], true)
    elseif data.ratio and not data.bis and not data.tie then
        local share = math.floor(data.ratio * 100 + 0.5)
        GameTooltip:AddLine((data.other and L.TIP_SCORE_SET or L.TIP_SCORE):format(share),
            MUTED[1], MUTED[2], MUTED[3], true)
    end
end

local function EnchantTooltip(owner, enchant, requirement)
    PlaceTooltip(owner)
    if enchant.kind == "spell" then
        pcall(GameTooltip.SetSpellByID, GameTooltip, enchant.number)
    else
        pcall(GameTooltip.SetItemByID, GameTooltip, enchant.number)
    end
    if GameTooltip:NumLines() == 0 then GameTooltip:SetText(enchant.name, 1, 1, 1) end
    if enchant.effect ~= "" then GameTooltip:AddLine(enchant.effect, 0.1, 1, 0.1, true) end
    if enchant.where ~= "" then GameTooltip:AddLine(ns.Enchants.Where(enchant), 1, 0.82, 0, true) end
    local remark = ns.Sources.OriginRemark(enchant.origin)
    if remark then GameTooltip:AddLine(remark, MUTED[1], MUTED[2], MUTED[3], true) end
    if requirement then
        GameTooltip:AddLine(L.REP_TIP_NEED:format(ns.Reputation.NeedText(requirement)), 1, 1, 1, true)
        GameTooltip:AddLine(ns.Reputation.StateText(requirement), MUTED[1], MUTED[2], MUTED[3], true)
        if requirement.scroll then GameTooltip:AddLine(L.REP_SCROLL, MUTED[1], MUTED[2], MUTED[3], true) end
        local unsure = ns.Reputation.UnknownRemark(requirement)
        if unsure then GameTooltip:AddLine(unsure, MUTED[1], MUTED[2], MUTED[3], true) end
    end
end

-- What a score is in that list, a line each: measured by the simulator for the lists the data says so of
-- (Ladders.Measured), with the fight simulated; the weighted stats for the others.
function Browser.ScoreInfo(class, spec, list)
    if ns.Ladders.Measured(class, spec, list) then
        return { L.SCORE_INFO_SIM, L.SCORE_INFO_FIGHT, L.SCORE_INFO_GAP_SIM }
    end
    return { L.SCORE_INFO_WEIGHTS, L.SCORE_INFO_GAP }
end

local function ScoreTooltip(owner)
    PlaceTooltip(owner)
    GameTooltip:SetText(L.SCORE_INFO_TITLE, 1, 0.82, 0)
    for index, line in ipairs(Browser.ScoreInfo(state.class, state.spec, state.list)) do
        if index > 1 then GameTooltip:AddLine(" ") end
        if index == 1 then
            GameTooltip:AddLine(line, 1, 1, 1, true)
        else
            GameTooltip:AddLine(line, MUTED[1], MUTED[2], MUTED[3], true)
        end
    end
    GameTooltip:Show()
end

-- A word on a rank that may surprise, behind the mark after an item's score.
local function WhyTooltip(mark)
    local data = mark.row.data
    if not data or not data.why then return end
    PlaceTooltip(mark)
    GameTooltip:SetText(L.WHY_TITLE, 1, 0.82, 0)
    GameTooltip:AddLine(data.why, 1, 1, 1, true)
    GameTooltip:Show()
end

local function RowTooltip(row)
    local data = row.data
    if not data or data.kind == "note" or data.kind == "header" then return end
    if data.kind == "item" then
        ItemTooltip(row, data)
    elseif data.kind == "consumable" then
        PlaceTooltip(row)
        local consumable = data.consumable
        pcall(GameTooltip.SetItemByID, GameTooltip, data.id)
        if GameTooltip:NumLines() == 0 then GameTooltip:SetText(consumable.name, 1, 1, 1) end
        if consumable.effect ~= "" then GameTooltip:AddLine(consumable.effect, 0.1, 1, 0.1, true) end
        local zoneNote = ns.Consumables.ZoneNote(consumable)
        if zoneNote then GameTooltip:AddLine(zoneNote, 0.45, 0.78, 1, true) end
        GameTooltip:AddLine(ns.Consumables.Where(consumable), 1, 0.82, 0, true)
        if data.unranked and data.key ~= "situational" then
            GameTooltip:AddLine(L.TIP_CONS_UNRANKED, MUTED[1], MUTED[2], MUTED[3], true)
        elseif data.ratio and not data.bis and not data.tie then
            GameTooltip:AddLine(L.TIP_CONS_SCORE:format(math.floor(data.ratio * 100 + 0.5)),
                MUTED[1], MUTED[2], MUTED[3], true)
        end
    else
        EnchantTooltip(row, data.enchant, data.reputation)
    end
    ShowTooltip()
end

-- Shift-click links the item in chat, Ctrl-click tries it on: the game's own handling. True when a
-- modifier key was held, whether or not the game knows the item yet.
local function ModifiedClick(id)
    if not (IsModifierKeyDown and IsModifierKeyDown()) or not HandleModifiedItemClick then return false end
    if id and GetInfo then
        local _, link = GetInfo(id)
        if link then HandleModifiedItemClick(link) end
    end
    return true
end

local function RowClick(row)
    local data = row.data
    if not data then return end
    ModifiedClick(((data.kind == "item" or data.kind == "consumable") and data.id)
        or (data.kind == "enchant" and data.enchant.kind == "item" and data.enchant.number) or nil)
end

local function Text(row, font)
    local text = row:CreateFontString(nil, "OVERLAY", font)
    text:SetJustifyH("LEFT")
    text:SetWordWrap(false)
    return text
end

local function CreateRow(parent)
    local row = CreateFrame("Button", nil, parent)
    row:SetHeight(ROW_HEIGHT)
    Widgets.ListHighlight(row, "HIGHLIGHT", 0.32)

    -- a consumable tied to a zone: a blue tint over the row and a small map on its picture
    row.zoneBack = row:CreateTexture(nil, "BACKGROUND")
    row.zoneBack:SetAllPoints()
    row.zoneBack:SetColorTexture(0.20, 0.55, 0.85, 0.14)
    row.zoneBack:Hide()

    row.icon = row:CreateTexture(nil, "ARTWORK")
    row.icon:SetPoint("LEFT", 4, 0)
    row.zoneMark = row:CreateTexture(nil, "OVERLAY")
    row.zoneMark:SetSize(14, 14)
    row.zoneMark:SetPoint("BOTTOMRIGHT", row.icon, "BOTTOMRIGHT", 3, -3)
    row.zoneMark:SetTexture("Interface\\Icons\\INV_Misc_Map_01")
    row.zoneMark:SetTexCoord(0.08, 0.92, 0.08, 0.92)
    row.zoneMark:Hide()
    row.name = Text(row, FONT_NAME)
    row.sub = Text(row, FONT_TEXT)
    row.sub:SetTextColor(MUTED[1], MUTED[2], MUTED[3])

    -- the score, as a bar: full and gold for a best pick, shorter and grey for what comes after
    row.barBack = row:CreateTexture(nil, "ARTWORK")
    row.barBack:SetColorTexture(1, 1, 1, 0.10)
    row.barBack:SetSize(BAR_WIDTH, 6)
    row.bar = row:CreateTexture(nil, "OVERLAY")
    row.bar:SetHeight(6)
    row.bar:SetPoint("LEFT", row.barBack, "LEFT", 0, 0)
    row.rank = Text(row, FONT_TEXT)

    -- ... and, after the score of a few items, a mark: a word on a rank that may surprise (Notes.lua)
    row.why = CreateFrame("Button", nil, row)
    row.why.row = row
    row.why:SetSize(14, 14)
    row.why:SetPoint("LEFT", row.rank, "RIGHT", 6, 0)
    row.why.icon = row.why:CreateTexture(nil, "ARTWORK")
    row.why.icon:SetAllPoints()
    row.why.icon:SetTexture(INFO_ICON)
    row.why.icon:SetAlpha(0.75)
    row.why:SetScript("OnEnter", function(self)
        self.icon:SetAlpha(1)
        WhyTooltip(self)
    end)
    row.why:SetScript("OnLeave", function(self)
        self.icon:SetAlpha(0.75)
        ns.Tooltip.HideOwned(self)
    end)
    row.why:Hide()

    -- where it comes from: a picture for the category, then the words
    row.sourceIcon = row:CreateTexture(nil, "ARTWORK")
    row.sourceIcon:SetSize(SOURCE_ICON, SOURCE_ICON)
    row.kind = Text(row, FONT_TEXT)
    row.kind:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    row.detail = Text(row, FONT_TEXT)

    -- what a reputation asks for, and where the player stands
    row.rep = Text(row, FONT_TEXT)
    row.rep:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    row.repState = Text(row, FONT_TEXT)
    row.repState:SetJustifyH("RIGHT")

    -- a header row shows this alone: the slot's name
    row.header = row:CreateFontString(nil, "OVERLAY", FONT_HEADER)
    row.header:SetPoint("BOTTOMLEFT", 6, 5)
    row.header:SetTextColor(1, 0.82, 0)
    row.header:Hide()

    -- ... and, over the scores of an item slot, what a score is: a word and the game's information mark
    row.info = CreateFrame("Button", nil, row)
    row.info:SetHeight(16)
    row.info.text = Text(row.info, FONT_TEXT)
    row.info.text:SetPoint("LEFT", 0, 0)
    row.info.text:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    row.info.text:SetText(L.SCORE_COLUMN)
    row.info.icon = row.info:CreateTexture(nil, "ARTWORK")
    row.info.icon:SetSize(14, 14)
    row.info.icon:SetPoint("LEFT", row.info.text, "RIGHT", 4, 0)
    row.info.icon:SetTexture(INFO_ICON)
    row.info.icon:SetAlpha(0.75)
    row.info:SetScript("OnEnter", function(self)
        self.icon:SetAlpha(1)
        ScoreTooltip(self)
    end)
    row.info:SetScript("OnLeave", function(self)
        self.icon:SetAlpha(0.75)
        ns.Tooltip.HideOwned(self)
    end)
    row.info:Hide()

    -- a note row shows this alone
    row.note = row:CreateFontString(nil, "OVERLAY", FONT_TEXT)
    row.note:SetPoint("BOTTOMLEFT", 8, 4)
    row.note:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    row.note:Hide()

    row.line = row:CreateTexture(nil, "BACKGROUND")
    row.line:SetColorTexture(1, 1, 1, 0.08)
    row.line:SetHeight(1)
    row.line:SetPoint("BOTTOMLEFT", 0, 0)
    row.line:SetPoint("BOTTOMRIGHT", 0, 0)

    -- takes an item added by hand out of the list
    row.remove = CreateFrame("Button", nil, row)
    row.remove.row = row
    row.remove:SetSize(20, 20)
    row.remove:SetPoint("RIGHT", -4, 0)
    row.remove:SetNormalTexture("Interface\\Buttons\\UI-GroupLoot-Pass-Up")
    row.remove:SetHighlightTexture("Interface\\Buttons\\UI-GroupLoot-Pass-Highlight")
    row.remove:SetPushedTexture("Interface\\Buttons\\UI-GroupLoot-Pass-Down")
    row.remove:SetScript("OnClick", function(self)
        local data = self.row.data
        if not data or not data.custom then return end
        Widgets.Click()
        ns.Custom.Remove(state.class, state.spec, state.list, data.id)
    end)
    row.remove:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(L.TIP_REMOVE)
        GameTooltip:Show()
    end)
    row.remove:SetScript("OnLeave", ns.Tooltip.HideOwned)
    row.remove:Hide()

    row:SetScript("OnEnter", RowTooltip)
    row:SetScript("OnLeave", ns.Tooltip.HideOwned)
    row:SetScript("OnClick", RowClick)
    return row
end

-- Puts a row's parts on one line or on two. The rank is placed by PlaceRank, as it depends on the bar.
local function Arrange(row, compact)
    if row.compact == compact then return end
    row.compact = compact
    local icon = compact and COMPACT_ICON or ICON
    row.icon:SetSize(icon, icon)
    for _, part in ipairs({ row.name, row.sub, row.barBack, row.sourceIcon, row.kind }) do
        part:ClearAllPoints()
    end
    -- the right end of the texts leaves room for the button that removes an item added by hand
    if compact then
        row.name:SetPoint("LEFT", row.icon, "RIGHT", 8, 0)
        row.name:SetPoint("RIGHT", row, "LEFT", COMPACT.rank - 8, 0)
        row.barBack:SetPoint("LEFT", row, "LEFT", COMPACT.rank, 0)
        row.sub:SetPoint("LEFT", row, "LEFT", COMPACT.type, 0)
        row.sub:SetPoint("RIGHT", row, "LEFT", COMPACT.source - 8, 0)
        row.sourceIcon:SetPoint("LEFT", row, "LEFT", COMPACT.source, 0)
    else
        row.name:SetPoint("TOPLEFT", row.icon, "TOPRIGHT", 8, -4)
        row.name:SetPoint("RIGHT", row, "LEFT", WIDE.rank - 8, 0)
        row.sub:SetPoint("BOTTOMLEFT", row.icon, "BOTTOMRIGHT", 8, 4)
        row.sub:SetPoint("RIGHT", row, "LEFT", WIDE.source - 10, 0)
        row.barBack:SetPoint("LEFT", row, "TOPLEFT", WIDE.rank, -LINE_ONE)
        row.sourceIcon:SetPoint("LEFT", row, "TOPLEFT", WIDE.source, -LINE_ONE)
        row.kind:SetPoint("LEFT", row.sourceIcon, "RIGHT", 6, 0)
        row.kind:SetPoint("RIGHT", row, "TOPRIGHT", -28, -LINE_ONE)
    end
end

-- Where the row says where it comes from, and the line a reputation adds under it: on one line the two
-- share the row's height, on two the row grows by a line (RowHeight).
local function PlaceReputation(row, compact, gated)
    row.detail:ClearAllPoints()
    row.rep:ClearAllPoints()
    row.repState:ClearAllPoints()
    if compact then
        local shift = gated and COMPACT_SHIFT or 0
        row.detail:SetPoint("LEFT", row.sourceIcon, "RIGHT", 6, shift)
        row.detail:SetPoint("RIGHT", row, "RIGHT", -28, shift)
        row.repState:SetPoint("RIGHT", row, "RIGHT", -28, -COMPACT_SHIFT)
        row.rep:SetPoint("LEFT", row.sourceIcon, "RIGHT", 6, -COMPACT_SHIFT)
    else
        row.detail:SetPoint("BOTTOMLEFT", row, "BOTTOMLEFT", WIDE.source, gated and 9 + REPUTATION_LINE or 9)
        row.detail:SetPoint("RIGHT", row, "RIGHT", -28, 0)
        row.repState:SetPoint("BOTTOMRIGHT", row, "BOTTOMRIGHT", -28, 9)
        row.rep:SetPoint("BOTTOMLEFT", row, "BOTTOMLEFT", WIDE.source, 9)
    end
    row.rep:SetPoint("RIGHT", row.repState, "LEFT", -8, 0)
end

local function ShowReputation(row, data, compact)
    local requirement = data.reputation
    row.rep:SetShown(requirement ~= nil)
    row.repState:SetShown(requirement ~= nil)
    PlaceReputation(row, compact, requirement ~= nil)
    if not requirement then return end
    row.rep:SetText(ns.Reputation.NeedText(requirement))
    row.repState:SetText(ns.Reputation.StateText(requirement))
end

local function PlaceRank(row, hasBar)
    local x = (row.compact and COMPACT or WIDE).rank + (hasBar and BAR_WIDTH + 6 or 0)
    row.rank:ClearAllPoints()
    if row.compact then
        row.rank:SetPoint("LEFT", row, "LEFT", x, 0)
    else
        row.rank:SetPoint("LEFT", row, "TOPLEFT", x, -LINE_ONE)
    end
end

-- The bar and the words after it. An enchant has no score: its best one gets a full bar, the others none.
local function ShowRank(row, data)
    local ratio = data.ratio
    if data.kind == "enchant" then ratio = data.bis and 1 or nil end
    local hasBar = ratio ~= nil
    row.barBack:SetShown(hasBar)
    row.bar:SetShown(hasBar)
    if hasBar then
        row.bar:SetWidth(math.max(2, math.floor(BAR_WIDTH * ratio + 0.5)))
        if data.bis or data.tie then
            row.bar:SetColorTexture(1, 0.82, 0, 0.90)
        else
            row.bar:SetColorTexture(0.78, 0.78, 0.82, 0.85)
        end
    end
    PlaceRank(row, hasBar)
    row.rank:SetText(RankText(data))
end

local HANDED = {
    INVTYPE_2HWEAPON = true, INVTYPE_WEAPON = true, INVTYPE_WEAPONMAINHAND = true, INVTYPE_WEAPONOFFHAND = true,
}
local NO_TYPE = { neck = true, finger = true, trinket = true }

-- An item's type, once the game knows it. The header already names the slot. A weapon also says the
-- hand(s) it takes ("Two-Hand - Staves"), since a slot can list both styles; on one line a two-hander
-- says its type alone, which is enough ("Staves", "Two-Handed Swords"). Necklaces, rings and trinkets
-- have no type worth a word ("Miscellaneous").
local function TypeLine(slot, subType, equipLoc, classID, subclassID, compact)
    local hand = equipLoc and equipLoc ~= "" and _G[equipLoc] or nil
    if type(hand) ~= "string" then hand = nil end
    if equipLoc == "INVTYPE_HOLDABLE" then return hand or "" end
    if NO_TYPE[slot] or (classID == 4 and subclassID == 0) then return "" end
    if not subType or subType == "" then return "" end
    if hand and HANDED[equipLoc] and not (compact and equipLoc == "INVTYPE_2HWEAPON") then
        return hand .. " - " .. subType
    end
    return subType
end

-- The sign a source wears when the data is less than sure of it; the tooltip explains it.
local function Mark(origin)
    local mark = ns.Sources.OriginMark(origin)
    return mark ~= "" and (" |cff808080" .. mark .. "|r") or ""
end

-- Whether a row takes one line.
local function OnOneLine(data)
    return (data.kind == "item" or data.kind == "consumable") and ns:GetOption("compact")
end

local function FillRow(row, data)
    row.data = data
    local header, note = data.kind == "header", data.kind == "note"
    local plain = header or note
    local compact = OnOneLine(data)
    row.header:SetShown(header)
    row.info:SetShown(header and data.scored == true)
    if header and data.scored then   -- over the bars, wherever the option "compact" puts them
        row.info:ClearAllPoints()
        row.info:SetPoint("BOTTOMLEFT", row, "BOTTOMLEFT", (ns:GetOption("compact") and COMPACT or WIDE).rank, 3)
        row.info:SetWidth((row.info.text:GetStringWidth() or 0) + 4 + 14)
    end
    row.note:SetShown(note)
    row.icon:SetShown(not plain)
    row.name:SetShown(not plain)
    row.sub:SetShown(not plain)
    row.rank:SetShown(not plain)
    row.why:SetShown(data.kind == "item" and data.why ~= nil)
    row.sourceIcon:SetShown(not plain)
    row.kind:SetShown(not plain and not compact)
    row.detail:SetShown(not plain)
    row.remove:SetShown(data.custom == true)
    local zoned = data.kind == "consumable" and data.consumable.zone ~= nil
    row.zoneBack:SetShown(zoned)
    row.zoneMark:SetShown(zoned)
    row.line:SetShown(not note)
    row:EnableMouse(not plain)   -- a header or a note neither lights up nor has a tooltip
    if plain then
        row.barBack:Hide()
        row.bar:Hide()
        row.rep:Hide()
        row.repState:Hide()
        if header then
            row.header:SetText(data.text)
            row.line:SetColorTexture(1, 0.82, 0, 0.45)
        else
            row.note:SetText(data.text)
        end
        return
    end
    row.line:SetColorTexture(1, 1, 1, 0.08)
    Arrange(row, compact)
    ShowRank(row, data)
    ShowReputation(row, data, compact)

    if data.kind == "item" then
        local name, _, quality, _, _, _, subType, _, equipLoc, texture, _, classID, subclassID
        if GetInfo then
            name, _, quality, _, _, _, subType, _, equipLoc, texture, _, classID, subclassID = GetInfo(data.id)
        end
        row.icon:SetTexture(texture or (GetIcon and GetIcon(data.id)) or UNKNOWN_ICON)
        row.name:SetText(QualityHex(quality) .. (name or ns.Items.Name(data.id)) .. "|r"
            .. ns.Reputation.UnknownMark(data.reputation))
        row.sub:SetText(TypeLine(data.slot, subType, equipLoc, classID, subclassID, compact))
        local source = data.source
        local category, line, mark = ns.Sources.CategoryName(source.category), ns.Sources.Line(source), Mark(source.origin)
        SetIcon(row.sourceIcon, ns.Sources.Icon(source.category, source.profession))
        row.kind:SetText(category .. mark)
        -- on one line the picture stands for the category, which is spelled out only when nothing else is known
        row.detail:SetText(ns.Sources.WithCost(compact and ((line ~= "" and line or category) .. mark) or line, source.cost))
    elseif data.kind == "consumable" then
        local consumable = data.consumable
        row.icon:SetTexture(ns.Consumables.Icon(consumable) or UNKNOWN_ICON)
        row.name:SetText(ns.Consumables.Name(consumable))
        row.sub:SetText(consumable.effect ~= "" and consumable.effect or ns.Consumables.KeyName(data.key))
        SetIcon(row.sourceIcon, ns.Sources.Icon(ns.Consumables.Category(consumable), consumable.profession))
        local kind, detail = ns.Consumables.Kind(consumable), ns.Consumables.Detail(consumable)
        row.kind:SetText(kind)
        -- on one line the profession and its skill replace what every trainer teaches, or a source with no words
        row.detail:SetText(compact and (consumable.trainer or detail == "") and kind or detail)
    else
        local enchant = data.enchant
        row.icon:SetTexture(ns.Enchants.Icon(enchant) or UNKNOWN_ICON)
        row.name:SetText(ns.Enchants.Name(enchant) .. ns.Reputation.UnknownMark(data.reputation))
        row.sub:SetText(enchant.effect ~= "" and enchant.effect or ns.Enchants.KeyName(data.key))
        SetIcon(row.sourceIcon, ns.Sources.Icon(ns.Enchants.Category(enchant), enchant.profession))
        row.kind:SetText(ns.Enchants.Kind(enchant) .. Mark(enchant.origin))
        row.detail:SetText(ns.Enchants.Detail(enchant))
    end
end

local function RowHeight(data)
    if data.kind == "header" then return HEADER_HEIGHT end
    if data.kind == "note" then return NOTE_HEIGHT end
    if OnOneLine(data) then return COMPACT_HEIGHT end
    return data.reputation and ROW_HEIGHT + REPUTATION_LINE or ROW_HEIGHT
end

local function LayoutRows(rows)
    local width = window.scroll:GetWidth()
    if not width or width < 100 then width = WIDTH - 50 end
    local offset = 0
    for index, data in ipairs(rows) do
        local row = window.rows[index]
        if not row then
            row = CreateRow(window.child)
            window.rows[index] = row
        end
        FillRow(row, data)
        row:SetHeight(RowHeight(data))
        row:ClearAllPoints()
        row:SetPoint("TOPLEFT", window.child, "TOPLEFT", 0, -offset)
        row:SetWidth(width)
        row:Show()
        offset = offset + RowHeight(data)
    end
    for index = #rows + 1, #window.rows do window.rows[index]:Hide() end
    local height = math.max(1, offset)
    window.child:SetSize(width, height)
    if window.scroll.UpdateScrollChildRect then window.scroll:UpdateScrollChildRect() end
    if window.scroll.ScrollBar then
        window.scroll.ScrollBar:SetAlpha(height > window.scroll:GetHeight() + 1 and 1 or 0)
    end
    window.empty:SetShown(#rows == 0)
    window.rowData = rows
end

---------------------------------------------------------------------------
-- Building the window
---------------------------------------------------------------------------

local function Choose(key)
    return function(value)
        state[key] = value ~= ALL and value or nil
        Refresh()
    end
end

-- The on/off options, in three groups: tooltips, what the lists count, the window. After what the lists
-- count come three submenus: the PvP rewards, a box per list (each list counts them or not), the
-- number of alternatives a slot lists, and the faction the lists are for.
local OPTION_GROUPS = {
    { "tooltip", "onlyMyClass", "alternatives", "repTooltip" },
    { "unsourced", "seenOnly" },
    { "compact", "repCompact", "minimap", "auctionTab" },
}

local function OptionEntries()
    local entries = { { kind = "title", text = L.OPTIONS } }
    local function Submenu(text)
        local items = {}
        entries[#entries + 1] = { kind = "button", text = text, items = items }
        return items
    end
    for index, group in ipairs(OPTION_GROUPS) do
        if index > 1 then entries[#entries + 1] = { kind = "divider" } end
        for _, option in ipairs(group) do
            entries[#entries + 1] = { kind = "checkbox", text = L["OPT_" .. option],
                selected = function() return ns:GetOption(option) end,
                pick = function() ns:SetOption(option, not ns:GetOption(option)) end }
        end
        if index == 2 then
            local rewards = Submenu(L.OPT_PVP_REWARDS)
            for _, list in ipairs(ns.LISTS) do
                rewards[#rewards + 1] = { kind = "checkbox", text = L.OPT_PVP_LIST:format(ns.ListName(list)),
                    selected = function() return ns:PvPRewards(list) end,
                    pick = function() ns:SetPvPRewards(list, not ns:PvPRewards(list)) end }
            end
            local counts = Submenu(L.OPT_ALT_COUNT)
            for count = ns.ALTERNATIVES, ns.MaxAlternatives() do
                counts[#counts + 1] = { kind = "radio", text = tostring(count),
                    selected = function() return ns.Alternatives() == count end,
                    pick = function() ns:SetAlternatives(count) end }
            end
            -- the faction the lists are for: the character's, or the other one to see what it would wear
            local sides = Submenu(L.OPT_SIDE)
            for _, side in ipairs({ "a", "h" }) do
                local name = L["SIDE_" .. side]
                sides[#sides + 1] = { kind = "radio", text = side == ns.CharacterSide() and L.OPT_SIDE_OWN:format(name) or name,
                    selected = function() return ns.PlayerSide() == side end,
                    pick = function() ns:SetSide(side) end }
            end
        end
    end
    return entries
end

-- A new spec or list, picked in the window or in the auction house's tab.
local function SetTarget(class, spec, list)
    state.class, state.spec, state.list = class, spec, list
    state.source, state.zone = nil, nil
    SaveState()
    Refresh()
end

function Browser.SpecFilter(parent)
    local filter = Widgets.Dropdown(parent, L.FILTER_SPEC, 176)
    SetupChoices(filter.button, SpecChoices,
        function() return SpecKey(Browser.Target()) end,
        function(value)
            local class, spec = value:match("^(%u+):(%d+)$")
            local _, _, list = Browser.Target()
            SetTarget(class, tonumber(spec), list)
        end)

    function filter:Refresh()
        local class, spec = Browser.Target()
        self:Set(ClassHex(class) .. ns.ClassName(class) .. "|r " .. ns.SpecName(ns.Index.SpecName(class, spec) or ""), false)
    end

    return filter
end

function Browser.ListFilter(parent)
    local filter = Widgets.Segmented(parent,
        { { value = "pve", text = L.LIST_PVE }, { value = "pvp", text = L.LIST_PVP } },
        function() return select(3, Browser.Target()) end,
        function(value)
            local class, spec = Browser.Target()
            SetTarget(class, spec, value)
        end)
    filter:Layout(50)
    filter.label = Widgets.FilterLabel(filter, L.FILTER_LIST)
    return filter
end

local function Build()
    window = CreateWindow()
    Browser.window = window
    window.grip = CreateGrip(window)
    window.facets = { sources = {}, zones = {} }

    -- Filters
    window.spec = Browser.SpecFilter(window)
    window.spec:SetPoint("TOPLEFT", 66, -26)
    window.list = Browser.ListFilter(window)
    window.listLabel = window.list.label

    -- Not the window's own: the phase is the character's, and tooltips follow it too.
    window.phase = Widgets.Dropdown(window, L.FILTER_PHASE, 100)
    SetupChoices(window.phase.button, PhaseChoices, ns.Phase, function(value) ns:SetPhase(value) end)

    window.slot = Widgets.Dropdown(window, L.FILTER_SLOT, 104)
    SetupChoices(window.slot.button,
        function() return state.tab == "consumables" and CategoryChoices() or SlotChoices() end,
        function()
            if state.tab == "consumables" then return state.category or ALL end
            return state.slot or ALL
        end,
        function(value)
            state[state.tab == "consumables" and "category" or "slot"] = value ~= ALL and value or nil
            Refresh()
        end)

    window.source = Widgets.Dropdown(window, L.FILTER_SOURCE, 104)
    SetupChoices(window.source.button, function() return SourceChoices(window.facets) end,
        function() return state.source or ALL end, Choose("source"))

    window.zone = Widgets.Dropdown(window, L.FILTER_ZONE, 112)
    SetupChoices(window.zone.button, function() return ZoneChoices(window.facets) end,
        function() return state.zone or ALL end, Choose("zone"))

    window.reputation = Widgets.Dropdown(window, L.FILTER_REPUTATION, 110)
    SetupChoices(window.reputation.button, ReputationChoices,
        function() return state.reputation or ALL end, Choose("reputation"))
    window.filters = { window.list, window.phase, window.slot, window.source, window.zone, window.reputation }

    -- On every tab: the items, the enchants, the character sheet and the tooltips all follow it. The filters
    -- fill their row, so it sits in the window's title bar.
    window.available = Widgets.Check(window, L.OPT_availableNow,
        function() return ns:GetOption("availableNow") end,
        function(value) ns:SetOption("availableNow", value) end,
        function() return L.TIP_AVAILABLE_NOW:format(ns.RankCap()) end)
    window.available:SetPoint("TOPRIGHT", window, "TOPRIGHT", -34, -1)
    -- The window's border is drawn at frame level 500 and its title at 510, over the window's own children:
    -- below them, the border's title bar hides the box.
    local over = window.TitleContainer or window.NineSlice
    if over then window.available:SetFrameLevel(over:GetFrameLevel() + 1) end

    -- On every tab and on the dungeons, where the list used to start
    if NOTICE then
        window.notice = CreateNotice(window, L[NOTICE])
        window.notice:SetPoint("TOPLEFT", 8, -FILTERS)
        window.notice:SetPoint("TOPRIGHT", -8, -FILTERS)
        window.notice.close:SetScript("OnClick", function(self)
            Widgets.Click()
            noticeShown = false
            ns.Tooltip.HideOwned(self)
            PlaceNotice()
            Refresh()
        end)
    end

    -- Rows
    local inset = CreateInset(window)
    window.inset = inset
    PlaceNotice()
    local template = HasTemplate("ScrollFrameTemplate") and "ScrollFrameTemplate" or "UIPanelScrollFrameTemplate"
    window.scroll = CreateFrame("ScrollFrame", nil, inset, template)
    window.scroll:SetPoint("TOPLEFT", 6, -6)
    window.scroll:SetPoint("BOTTOMRIGHT", -28, 6)
    window.child = CreateFrame("Frame", nil, window.scroll)
    window.child:SetSize(1, 1)
    window.scroll:SetScrollChild(window.child)
    window.rows = {}
    window.empty = inset:CreateFontString(nil, "OVERLAY", "GameFontDisable")
    window.empty:SetPoint("TOP", 0, -40)
    window.empty:SetText(L.NO_ROWS)

    -- Footer tabs and actions share a row, with the data credit underneath.
    window.tabs = Widgets.Segmented(window,
        {
            { value = "items", text = L.TAB_ITEMS },
            { value = "enchants", text = L.TAB_ENCHANTS },
            { value = "character", text = L.TAB_CHARACTER },
            { value = "consumables", text = L.TAB_CONSUMABLES },
            { value = "reputations", text = L.TAB_REPUTATIONS },
        },
        function() return state.tab end,
        function(value)
            state.tab = value
            Refresh()
        end)
    window.tabs:Layout(nil, 10)
    Widgets.MarkNew(window.tabs.buttons[5], L.TAB_NEW)
    window.tabs:SetPoint("BOTTOMLEFT", 10, FOOTER_BUTTON_BOTTOM)

    -- Down the right edge: the lists, and the dungeons
    window.pages = Widgets.SideTabs(window,
        {
            { value = "lists", text = L.PAGE_LISTS, icon = ns.ICON },
            { value = "dungeons", text = L.TAB_DUNGEONS, icon = DUNGEON_ICON },
        },
        function() return state.page end,
        function(value)
            state.page = value
            Refresh()
        end)
    Widgets.MarkNew(window.pages.buttons[2], L.TAB_NEW)
    if window.SetClampRectInsets then window:SetClampRectInsets(0, Widgets.SIDE_ROOM, 0, 0) end   -- they stay on the screen

    window.options = Widgets.MenuButton(window, L.OPTIONS, 88)
    window.options:SetPoint("BOTTOMRIGHT", -28, FOOTER_BUTTON_BOTTOM)
    if MenuUtil then
        ns.Menu.Attach(window.options, OptionEntries, true)
    else
        window.options:Hide()
    end

    window.alts = Widgets.Toggle(window, L.TOGGLE_ALTS,
        function() return ns:GetOption("listAlts") end,
        function(value) ns:SetOption("listAlts", value) end)
    window.alts:SetPoint("RIGHT", window.options, "LEFT", -8, 0)

    window.add = Widgets.Button(window, "+ " .. L.ADD_BUTTON)
    window.add:SetPoint("RIGHT", window.alts, "LEFT", -8, 0)
    window.add:SetScript("OnClick", function()
        Widgets.Click()
        ns.AddItem.Open(state)
    end)

    window.credit = window:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    window.credit:SetPoint("BOTTOM", 0, 9)
    window.credit:SetJustifyH("CENTER")
    window.credit:SetWordWrap(false)
    window.credit:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    window.credit:SetText(L.DATA_VERSION:format(ns.data and ns.data.meta and ns.data.meta.build or "?"))

    -- Names, colors and icons arrive from the server after the first look.
    window:SetScript("OnShow", function(self) self:RegisterEvent("GET_ITEM_INFO_RECEIVED") end)
    window:SetScript("OnHide", function(self)
        self:UnregisterEvent("GET_ITEM_INFO_RECEIVED")
        ns.AddItem.Close()
        if NOTICE and not noticeShown then   -- put away with its cross: back for the next time the window opens
            noticeShown = true
            PlaceNotice()
        end
    end)
    window:SetScript("OnEvent", function(self)
        if self.refreshQueued then return end
        self.refreshQueued = true
        C_Timer.After(0.3, function()
            self.refreshQueued = false
            Refresh()
        end)
    end)
end

Refresh = function()
    if not window or not window:IsShown() then return end
    ShowTitle(window)
    -- the dungeons take the place of the lists: none of the lists' tabs is open then
    local dungeons = state.page == "dungeons"
    local tab = not dungeons and state.tab or nil
    local items, character, consumables = tab == "items", tab == "character", tab == "consumables"
    local enchants, reputations = tab == "enchants", tab == "reputations"
    local rows, facets = {}, { sources = {}, zones = {} }
    if items then
        rows, facets = ns.Rows.Items(state)
        -- a source or a zone the new spec, list or slot does not have: back to "all"
        if (state.source and not facets.sources[state.source]) or (state.zone and not facets.zones[state.zone]) then
            if state.source and not facets.sources[state.source] then state.source = nil end
            if state.zone and not facets.zones[state.zone] then state.zone = nil end
            rows, facets = ns.Rows.Items(state)
        end
    elseif consumables then
        -- a category the new spec or list does not have: back to "all"
        if state.category and not ns.Consumables.Has(state.class, state.spec, state.list, state.category) then
            state.category = nil
        end
        rows = ns.Rows.Consumables(state)
    elseif enchants then
        rows = ns.Rows.Enchants(state)
    end
    window.facets = facets

    window.spec:Refresh()
    window.phase:Set(ns.PhaseName(ns.Phase()), false)
    window.phase.button:SetEnabled(not ns:GetOption("availableNow"))
    window.slot.label:SetText(consumables and L.FILTER_CATEGORY or L.FILTER_SLOT)
    if consumables then
        window.slot:Set(state.category and ns.Consumables.KeyName(state.category) or L.ALL_CATEGORIES, state.category ~= nil)
    else
        window.slot:Set(state.slot and ns.SlotName(state.slot) or L.ALL_SLOTS, state.slot ~= nil)
    end
    window.source:Set(state.source and ns.Sources.CategoryName(state.source) or L.ALL_SOURCES, state.source ~= nil)
    window.zone:Set(state.zone or L.ALL_ZONES, state.zone ~= nil)
    window.reputation:Set(state.reputation and L[REPUTATION_NAMES[state.reputation]] or L.REP_FILTER_ALL,
        state.reputation ~= nil)
    -- The two lists do not apply to enchants. Where an item comes from and adding one by hand belong to
    -- the list of items. The character sheet and the reputations have every slot and no alternative: only
    -- the spec, the list and the phase apply to them. The dungeons have every slot too, and the alternatives
    -- when asked for.
    local listed = items or enchants or consumables
    window.listLabel:SetShown(not enchants)
    window.list:SetShown(not enchants)
    window.slot:SetShown(listed)
    window.source:SetShown(items)
    window.zone:SetShown(items)
    window.reputation:SetShown(items or enchants)
    local previous = window.spec
    for _, filter in ipairs(window.filters) do
        if filter:IsShown() then
            filter:ClearAllPoints()
            filter:SetPoint("BOTTOMLEFT", previous, "BOTTOMRIGHT", 8, 0)
            previous = filter
        end
    end
    window.add:SetShown(items)
    window.alts:SetShown(listed or dungeons)
    window.tabs:SetShown(not dungeons)

    window.list:Refresh()
    window.tabs:Refresh()
    window.pages:Refresh()
    window.alts:Refresh()
    window.available:Refresh()
    ns.AddItem.Refresh()
    window.scroll:SetShown(listed)
    if not listed then window.empty:Hide() end
    if character then
        if not window.character then window.character = ns.Character.Create(window.inset) end
        ns.Character.Update(state, window:GetHeight() - InsetTop() - INSET_BOTTOM)
    else
        ns.Character.Hide()
    end
    if reputations then
        if not window.reputations then window.reputations = ns.ReputationView.Create(window.inset) end
        ns.ReputationView.Update(state)
    else
        ns.ReputationView.Hide()
    end
    if dungeons then
        if not window.dungeons then window.dungeons = ns.DungeonView.Create(window.inset) end
        ns.DungeonView.Update(state)
    else
        ns.DungeonView.Hide()
    end
    if listed then LayoutRows(ns.Rows.Grouped(rows)) end
end

function Browser.ShowSlot(slot)
    -- the filters off: the piece clicked must be in the list
    state.page, state.tab, state.slot, state.source, state.zone, state.reputation = "lists", "items", slot, nil, nil, nil
    Refresh()
end

function Browser.ShowSource(category)
    state.page, state.tab, state.slot, state.source, state.zone, state.reputation = "lists", "items", nil, category, nil, nil
    Refresh()
end

function Browser.ShowReputation(factionID, artisan)
    state.page, state.tab, state.faction, state.factionArtisan = "lists", "reputations", factionID, artisan == true
    Refresh()
end

function Browser.ShowDungeons()
    state.page = "dungeons"
    Refresh()
end

Browser.PlaceTooltip = PlaceTooltip
Browser.FONTS = { name = FONT_NAME, text = FONT_TEXT, header = FONT_HEADER }   -- for the other tabs
Browser.Font = RowFont
Browser.ItemTooltip = ItemTooltip
Browser.EnchantTooltip = EnchantTooltip
Browser.ShowTooltip = ShowTooltip
Browser.ModifiedClick = ModifiedClick

function Browser.Open()
    if not window then
        LoadState()
        Build()
    end
    window:Show()
    if window.Raise then window:Raise() end
    Refresh()
    -- The scroll frame has its size once shown: rows laid out again.
    if C_Timer and C_Timer.After then C_Timer.After(0, Refresh) end
end

function Browser.Close()
    if window then window:Hide() end
end

function Browser.Toggle()
    if window and window:IsShown() then
        Browser.Close()
    else
        Browser.Open()
    end
end

ns:On("OPTION_CHANGED", function() Refresh() end)
ns:On("CUSTOM_CHANGED", function() Refresh() end)
ns:On("REPUTATION_CHANGED", function() Refresh() end)

-- The entry in the game's addon menu (see the toc).
function EasyBIS_OnCompartmentClick()
    -- Let Blizzard finish picking and dismissing the compartment entry first.
    C_Timer.After(0, Browser.Toggle)
end
