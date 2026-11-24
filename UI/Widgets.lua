local _, ns = ...

--[[
The window's controls use the game's panel, menu and achievement artwork.

  Widgets.Dialog(name, parent, width, footer)      a dialog: a bronze header (.icon, .title, .sub, :SetIcon), a
                                                   close button, a darker foot that high; Escape closes it
  Widgets.Well(parent, box)                        a sunken ground for a text box, gold-edged while it has the focus
  Widgets.Button(parent, text, width)              a panel button
  Widgets.MenuButton(parent, text, width)          the filter button used for the options menu
  Widgets.FilterLabel(control, text)               a caption above a filter control
  Widgets.Dropdown(parent, label, width)           a labelled dropdown
                                                   :Set(text, active)   active: the filter narrows the list
  Widgets.Segmented(parent, options, get, set)     two or more buttons, one of them lit
                                                   options: { { value, text }, ... }; :Refresh();
                                                   :Layout(width, padding): every button that wide, or each
                                                   as wide as its text plus the padding (24 when not given)
  Widgets.SideTabs(parent, options, get, set)      the tabs down the window's right side, a picture each, the
                                                   chosen one lit; options: { { value, text, icon }, ... };
                                                   .buttons, :Refresh(). The text is the tab's tooltip
  Widgets.SIDE_ROOM                                the width they take beside the window
  Widgets.Toggle(parent, text, get, set)           a button that stays lit while on; :Refresh()
  Widgets.Check(parent, text, get, set, tip)       a checkbox with a clickable label; :Refresh()
                                                   tip: gives the sentence of its tooltip
  Widgets.MarkNew(button, text)                    a small green badge on its corner
  Widgets.ListHighlight(row, layer, alpha)          a quest-list highlight for an interactive row
  Widgets.Click()                                  the game's click sound
  Widgets.Scroll(parent)                           a scroll frame and the frame it scrolls: scroll, child
  Widgets.Band(texture, orientation, r, g, b, from, to)
                                                   makes a texture a band of one colour that fades from one
                                                   alpha to the other ("HORIZONTAL": to the right)

An active filter has a gold label. The green badge marks a new tab.
]]

local Widgets = {}
ns.Widgets = Widgets

Widgets.FLAT = { bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 }
Widgets.MUTED = { 0.66, 0.66, 0.70 }

local GOLD = { 1, 0.82, 0 }
local CONTROL_HEIGHT, FILTER_LABEL_HEIGHT = 24, 14
local CHECK_SIZE = 22
local SIDE_TAB, SIDE_TAB_GAP, SIDE_TAB_TOP = 32, 17, 36   -- a tab of the window's side, the room under it, the first one's place
Widgets.SIDE_ROOM = SIDE_TAB + 6   -- what the side tabs take on the window's right
local CATEGORY_ART = "Interface\\AchievementFrame\\UI-Achievement-Category-"

function Widgets.Click()
    if PlaySound and SOUNDKIT then PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON) end
end

-- A soft band of colour fading out to the right (or downwards), on any client: the newer gradient takes colours,
-- the older one numbers; without either, an even tint.
function Widgets.Band(texture, orientation, r, g, b, from, to)
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

function Widgets.Scroll(parent)
    local modern = C_XMLUtil ~= nil and C_XMLUtil.GetTemplateInfo ~= nil
        and C_XMLUtil.GetTemplateInfo("ScrollFrameTemplate") ~= nil
    local scroll = CreateFrame("ScrollFrame", nil, parent, modern and "ScrollFrameTemplate" or "UIPanelScrollFrameTemplate")
    local child = CreateFrame("Frame", nil, scroll)
    child:SetSize(1, 1)
    scroll:SetScrollChild(child)
    -- No bar when there is nothing to scroll: the older template reads the field, the newer its bar's setting.
    scroll.scrollBarHideable = true
    if scroll.ScrollBar and scroll.ScrollBar.SetHideIfUnscrollable then scroll.ScrollBar:SetHideIfUnscrollable(true) end
    return scroll, child
end

---------------------------------------------------------------------------
-- The dialogs
---------------------------------------------------------------------------

local DIALOG_BACKDROP = { bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
    edgeSize = 16, insets = { left = 4, right = 4, top = 4, bottom = 4 } }
local DIALOG_EDGE = 4            -- what the border takes
local DIALOG_ICON = 32
local BRONZE = { 0.55, 0.38, 0.16 }      -- the grounds of the Reputations tab
local BRASS = { 0.85, 0.66, 0.36 }       -- the rule under a dialog's header, the border
local WELL_EDGE = { 1, 1, 1, 0.14 }
Widgets.DIALOG_HEADER = 52       -- the header's height, the border included
Widgets.DIALOG_PAD = 16          -- from the dialog's side to what it holds

-- A dialog dressed as the window's tabs are: the game's tooltip border, a bronze band under an icon, a title
-- and a line under it, a darker foot for the buttons and what the dialog has to say.
function Widgets.Dialog(name, parent, width, footer)
    local fonts = ns.Browser and ns.Browser.FONTS or { header = "GameFontNormalLarge", text = "GameFontHighlightSmall" }
    local dialog = CreateFrame("Frame", name, parent, "BackdropTemplate")
    dialog:Hide()
    dialog:SetBackdrop(DIALOG_BACKDROP)
    dialog:SetBackdropColor(0.06, 0.055, 0.05, 1)
    dialog:SetBackdropBorderColor(BRASS[1], BRASS[2], BRASS[3], 1)
    dialog:SetWidth(width)
    dialog:SetFrameStrata("DIALOG")
    dialog:SetToplevel(true)
    dialog:SetClampedToScreen(true)
    dialog:EnableMouse(true)
    table.insert(UISpecialFrames, name)
    dialog.footerHeight = footer

    local band = dialog:CreateTexture(nil, "BACKGROUND", nil, 1)
    band:SetPoint("TOPLEFT", DIALOG_EDGE, -DIALOG_EDGE)
    band:SetPoint("TOPRIGHT", -DIALOG_EDGE, -DIALOG_EDGE)
    band:SetHeight(Widgets.DIALOG_HEADER - DIALOG_EDGE)
    Widgets.Band(band, "HORIZONTAL", BRONZE[1], BRONZE[2], BRONZE[3], 0.50, 0.06)
    local rule = dialog:CreateTexture(nil, "BORDER")
    rule:SetPoint("TOPLEFT", band, "BOTTOMLEFT", 0, 0)
    rule:SetPoint("TOPRIGHT", band, "BOTTOMRIGHT", 0, 0)
    rule:SetHeight(1)
    Widgets.Band(rule, "HORIZONTAL", BRASS[1], BRASS[2], BRASS[3], 0.75, 0.08)

    local top = -(DIALOG_EDGE + (Widgets.DIALOG_HEADER - DIALOG_EDGE - DIALOG_ICON) / 2)
    dialog.iconEdge = dialog:CreateTexture(nil, "BORDER")
    dialog.iconEdge:SetColorTexture(0, 0, 0, 0.85)
    dialog.iconEdge:SetSize(DIALOG_ICON + 2, DIALOG_ICON + 2)
    dialog.iconEdge:SetPoint("TOPLEFT", Widgets.DIALOG_PAD - 3, top + 1)
    dialog.icon = dialog:CreateTexture(nil, "ARTWORK")
    dialog.icon:SetSize(DIALOG_ICON, DIALOG_ICON)
    dialog.icon:SetPoint("TOPLEFT", Widgets.DIALOG_PAD - 2, top)

    local room = width - (Widgets.DIALOG_PAD - 2) - DIALOG_ICON - 10 - 36   -- up to the close button
    dialog.title = dialog:CreateFontString(nil, "OVERLAY", fonts.header)
    dialog.title:SetPoint("TOPLEFT", dialog.icon, "TOPRIGHT", 10, 1)
    dialog.title:SetWidth(room)
    dialog.title:SetJustifyH("LEFT")
    dialog.title:SetWordWrap(false)
    dialog.title:SetTextColor(1, 1, 1)
    dialog.sub = dialog:CreateFontString(nil, "OVERLAY", fonts.text)
    dialog.sub:SetPoint("BOTTOMLEFT", dialog.icon, "BOTTOMRIGHT", 10, -1)
    dialog.sub:SetWidth(room)
    dialog.sub:SetJustifyH("LEFT")
    dialog.sub:SetWordWrap(false)
    dialog.sub:SetTextColor(Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3])

    dialog.close = CreateFrame("Button", nil, dialog, "UIPanelCloseButton")
    dialog.close:SetPoint("TOPRIGHT", -2, -2)

    local foot = dialog:CreateTexture(nil, "BACKGROUND", nil, 1)
    foot:SetPoint("BOTTOMLEFT", DIALOG_EDGE, DIALOG_EDGE)
    foot:SetPoint("BOTTOMRIGHT", -DIALOG_EDGE, DIALOG_EDGE)
    foot:SetHeight(footer - DIALOG_EDGE)
    foot:SetColorTexture(0, 0, 0, 0.42)
    local footRule = dialog:CreateTexture(nil, "BORDER")
    footRule:SetPoint("BOTTOMLEFT", foot, "TOPLEFT", 0, 0)
    footRule:SetPoint("BOTTOMRIGHT", foot, "TOPRIGHT", 0, 0)
    footRule:SetHeight(1)
    footRule:SetColorTexture(1, 1, 1, 0.10)

    -- An item's icon is trimmed of its own border and framed; the game's alert mark is shown as it is.
    function dialog:SetIcon(texture, plain)
        self.icon:SetTexture(texture)
        self.iconEdge:SetShown(not plain)
        if plain then
            self.icon:SetTexCoord(0, 1, 0, 1)
        else
            self.icon:SetTexCoord(0.07, 0.93, 0.07, 0.93)
        end
    end

    return dialog
end

-- A sunken ground for a text box: its edge turns gold while the box has the focus, and a click anywhere in it
-- gives the box the focus.
function Widgets.Well(parent, box)
    local well = CreateFrame("Frame", nil, parent, "BackdropTemplate")
    well:SetBackdrop(Widgets.FLAT)
    well:SetBackdropColor(0, 0, 0, 0.55)
    well:SetBackdropBorderColor(WELL_EDGE[1], WELL_EDGE[2], WELL_EDGE[3], WELL_EDGE[4])
    function well:Hold(held)
        self:EnableMouse(true)
        self:SetScript("OnMouseDown", function() held:SetFocus() end)
        held:HookScript("OnEditFocusGained", function() self:SetBackdropBorderColor(GOLD[1], GOLD[2], GOLD[3], 0.75) end)
        held:HookScript("OnEditFocusLost", function()
            self:SetBackdropBorderColor(WELL_EDGE[1], WELL_EDGE[2], WELL_EDGE[3], WELL_EDGE[4])
        end)
    end
    if box then well:Hold(box) end
    return well
end

function Widgets.Button(parent, text, width)
    local button = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
    button:SetText(text)
    button:SetSize(width or math.max(60, math.ceil(button:GetFontString():GetStringWidth()) + 24), CONTROL_HEIGHT)
    return button
end

function Widgets.MenuButton(parent, text, width)
    if not MenuUtil then return Widgets.Button(parent, text, width) end
    local button = CreateFrame("DropdownButton", nil, parent, "WowStyle1FilterDropdownTemplate")
    button.resizeToText = false
    button:SetText(text)
    button.Text:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
    button:SetSize(width, CONTROL_HEIGHT)
    return button
end

local function CategoryTexture(button, layer, art)
    local texture = button:CreateTexture(nil, layer)
    texture:SetTexture(CATEGORY_ART .. art)
    texture:SetTexCoord(0, 170 / 256, 0, 1)
    return texture
end

function Widgets.ChoiceButton(parent, text, topInset)
    local button = CreateFrame("Button", nil, parent)
    button:SetHeight(CONTROL_HEIGHT)
    local face = CategoryTexture(button, "BACKGROUND", "Background")
    -- The original art has more shadow below the bevel than above it.
    face:SetPoint("TOPLEFT", 0, 5 - (topInset or 0))
    face:SetPoint("BOTTOMRIGHT", 0, -10)
    local highlight = CategoryTexture(button, "HIGHLIGHT", "Highlight")
    highlight:SetBlendMode("ADD")
    button:SetHighlightTexture(highlight)
    highlight:SetAllPoints(face)
    button.Text = button:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    button.Text:SetPoint("CENTER")
    button.Text:SetText(text)
    button.Text:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
    button:SetWidth(math.max(60, math.ceil(button.Text:GetStringWidth()) + 24))
    return button
end

local function Select(button, selected)
    if selected then
        button:LockHighlight()
        button.Text:SetTextColor(1, 1, 1)
    else
        button:UnlockHighlight()
        button.Text:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
    end
end

function Widgets.ListHighlight(row, layer, alpha)
    local texture = row:CreateTexture(nil, layer)
    texture:SetAllPoints()
    texture:SetTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight")
    texture:SetBlendMode("ADD")
    texture:SetAlpha(alpha)
    return texture
end

-- The badge sits across the corner, clear of the tab's caption.
function Widgets.MarkNew(button, text)
    local badge = CreateFrame("Frame", nil, button, "BackdropTemplate")
    badge:SetBackdrop(Widgets.FLAT)
    badge:SetBackdropColor(0.10, 0.45, 0.20, 1)
    badge:SetBackdropBorderColor(0.35, 0.90, 0.50, 0.95)
    badge:SetFrameLevel(button:GetFrameLevel() + 10)   -- over the list, which its top edge may touch
    badge.text = badge:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    badge.text:SetPoint("CENTER")
    badge.text:SetText(text)
    badge:SetSize(math.ceil(badge.text:GetStringWidth()) + 8, 13)
    badge:SetPoint("CENTER", button, "TOPRIGHT", 0, 3)
    button.newBadge = badge
end

function Widgets.FilterLabel(control, text)
    local label = control:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    label:SetPoint("TOPLEFT", 2, FILTER_LABEL_HEIGHT)
    label:SetTextColor(Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3])
    label:SetText(text)
    return label
end

function Widgets.Dropdown(parent, label, width)
    local filter = CreateFrame("Frame", nil, parent)
    filter:SetSize(width, CONTROL_HEIGHT + FILTER_LABEL_HEIGHT)
    if MenuUtil then
        local button = CreateFrame("DropdownButton", nil, filter, "WowStyle1DropdownTemplate")
        button:SetSize(width, CONTROL_HEIGHT)
        button.Text:SetJustifyH("LEFT")
        button.Background:ClearAllPoints()
        button.Background:SetPoint("TOPLEFT", -4, 8)
        button.Background:SetPoint("BOTTOMRIGHT", 4, -9)
        filter.button = button
    else
        filter.button = Widgets.Button(filter, " ", width)
    end
    filter.button:SetPoint("BOTTOMLEFT", 0, 0)
    filter.label = Widgets.FilterLabel(filter.button, label)

    function filter:Set(text, active)
        if self.button.OverrideText then
            self.button:OverrideText(text)
        else
            self.button:SetText(text)
        end
        local color = active and GOLD or Widgets.MUTED
        self.label:SetTextColor(color[1], color[2], color[3])
    end

    return filter
end

function Widgets.Segmented(parent, options, get, set)
    local group = CreateFrame("Frame", nil, parent)
    group:SetHeight(CONTROL_HEIGHT)
    group.buttons = {}
    function group:AddOption(option)
        local button = Widgets.ChoiceButton(group, option.text)
        button.value = option.value
        button:SetScript("OnClick", function(self)
            if get() == self.value then return end
            Widgets.Click()
            set(self.value)
        end)
        group.buttons[#group.buttons + 1] = button
        return button
    end

    for _, option in ipairs(options) do group:AddOption(option) end

    function group:Refresh()
        local current = get()
        for _, button in ipairs(self.buttons) do
            Select(button, button.value == current)
        end
    end

    function group:Layout(buttonWidth, padding)
        local x = 0
        for _, button in ipairs(self.buttons) do
            if button:IsShown() then
                local width = buttonWidth
                    or math.max(padding and 44 or 60, math.ceil(button.Text:GetStringWidth()) + (padding or 24))
                button:SetWidth(width)
                button:ClearAllPoints()
                button:SetPoint("LEFT", self, "LEFT", x, 0)
                x = x + width + 4
            end
        end
        self:SetWidth(math.max(1, x - 4))
    end

    group:Layout()
    group:Refresh()
    return group
end

-- The tabs down the right side of the window, as the game's spellbook and professions have them: a picture
-- each, the chosen one lit. The game's own art, laid out as its SpellBookSkillLineTabTemplate does.
function Widgets.SideTabs(parent, options, get, set)
    local group = { buttons = {} }
    for index, option in ipairs(options) do
        local button = CreateFrame("Button", nil, parent)
        button:SetSize(SIDE_TAB, SIDE_TAB)
        button:SetPoint("TOPLEFT", parent, "TOPRIGHT", 0, -SIDE_TAB_TOP - (index - 1) * (SIDE_TAB + SIDE_TAB_GAP))
        button.value, button.text = option.value, option.text
        button.back = button:CreateTexture(nil, "BACKGROUND")
        button.back:SetTexture("Interface\\SpellBook\\SpellBook-SkillLineTab")
        button.back:SetSize(64, 64)
        button.back:SetPoint("TOPLEFT", -3, 11)
        button.icon = button:CreateTexture(nil, "ARTWORK")
        button.icon:SetAllPoints()
        button.icon:SetTexture(option.icon)
        local highlight = button:CreateTexture(nil, "HIGHLIGHT")
        highlight:SetTexture("Interface\\Buttons\\ButtonHilight-Square")
        highlight:SetBlendMode("ADD")
        highlight:SetAllPoints()
        button.checked = button:CreateTexture(nil, "OVERLAY")
        button.checked:SetTexture("Interface\\Buttons\\CheckButtonHilight")
        button.checked:SetBlendMode("ADD")
        button.checked:SetAllPoints()
        button:SetScript("OnClick", function(self)
            if get() == self.value then return end
            Widgets.Click()
            set(self.value)
        end)
        button:SetScript("OnEnter", function(self)
            GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
            GameTooltip:SetText(self.text, 1, 1, 1)
            GameTooltip:Show()
        end)
        button:SetScript("OnLeave", ns.Tooltip.HideOwned)
        group.buttons[index] = button
    end

    function group:Refresh()
        local current = get()
        for _, button in ipairs(self.buttons) do
            button.checked:SetShown(button.value == current)
        end
    end

    group:Refresh()
    return group
end

function Widgets.Toggle(parent, text, get, set)
    local button = Widgets.ChoiceButton(parent, text, 1)   -- align the top bevel with the adjacent footer actions
    button:SetScript("OnClick", function()
        Widgets.Click()
        set(not get())
    end)

    function button:Refresh()
        Select(self, get())
    end

    button:Refresh()
    return button
end

function Widgets.Check(parent, text, get, set, tip)
    local check = CreateFrame("CheckButton", nil, parent, "UICheckButtonArtTemplate")
    check:SetHeight(CHECK_SIZE)
    -- All of the label is clickable, so pin the template's art to its left.
    for _, texture in ipairs({ check:GetNormalTexture(), check:GetPushedTexture(),
        check:GetHighlightTexture(), check:GetCheckedTexture(), check:GetDisabledCheckedTexture() }) do
        texture:ClearAllPoints()
        texture:SetSize(CHECK_SIZE, CHECK_SIZE)
        texture:SetPoint("LEFT")
    end
    check.text = check:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    check.text:SetPoint("LEFT", CHECK_SIZE, 0)
    check.text:SetText(text)
    check:SetWidth(CHECK_SIZE + math.ceil(check.text:GetStringWidth()))

    function check:Refresh()
        local on = get()
        self:SetChecked(on)
        if on then
            self.text:SetTextColor(GOLD[1], GOLD[2], GOLD[3])
        else
            self.text:SetTextColor(1, 1, 1)
        end
    end

    check:SetScript("OnClick", function()
        Widgets.Click()
        set(not get())
    end)
    if tip then
        check:SetScript("OnEnter", function(self)
            GameTooltip:SetOwner(self, "ANCHOR_BOTTOMRIGHT")
            GameTooltip:SetText(text, 1, 1, 1)
            GameTooltip:AddLine(tip(), Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3], true)
            GameTooltip:Show()
        end)
        check:SetScript("OnLeave", ns.Tooltip.HideOwned)
    end

    check:Refresh()
    return check
end
