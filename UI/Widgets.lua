local _, ns = ...

--[[
The window's controls use the game's panel, menu and achievement artwork.

  Widgets.Button(parent, text, width)              a panel button
  Widgets.MenuButton(parent, text, width)          the filter button used for the options menu
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
local CONTROL_HEIGHT = 22
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
    texture:SetTexCoord(0, 0.6640625, 0, 1)
    texture:SetPoint("TOPLEFT")
    texture:SetPoint("BOTTOMRIGHT", 0, -7)
    return texture
end

local function ChoiceButton(parent, text)
    local button = CreateFrame("Button", nil, parent)
    button:SetHeight(CONTROL_HEIGHT)
    CategoryTexture(button, "BACKGROUND", "Background")
    local highlight = CategoryTexture(button, "HIGHLIGHT", "Highlight")
    highlight:SetBlendMode("ADD")
    button:SetHighlightTexture(highlight)
    button.Text = button:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    button.Text:SetPoint("CENTER")
    button.Text:SetText(text)
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

-- The badge sits across the corner, not after the button: the credit beside the tabs has no width to spare.
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

function Widgets.Dropdown(parent, label, width)
    local filter = CreateFrame("Frame", nil, parent)
    filter:SetSize(width, 38)
    filter.label = filter:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    filter.label:SetPoint("TOPLEFT", 2, 0)
    filter.label:SetText(label)
    if MenuUtil then
        local button = CreateFrame("DropdownButton", nil, filter, "WowStyle1DropdownTemplate")
        button:SetSize(width, 24)
        button.Text:SetJustifyH("LEFT")
        -- The stock holder extends past the button. Keep it clear of adjacent filters.
        button.Background:ClearAllPoints()
        button.Background:SetPoint("TOPLEFT", -4, 8)
        button.Background:SetPoint("BOTTOMRIGHT", 4, -9)
        filter.button = button
    else
        filter.button = Widgets.Button(filter, " ", width)
    end
    filter.button:SetPoint("BOTTOMLEFT", 0, 0)

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
    for _, option in ipairs(options) do
        local button = ChoiceButton(group, option.text)
        button.value = option.value
        button:SetScript("OnClick", function(self)
            if get() == self.value then return end
            Widgets.Click()
            set(self.value)
        end)
        group.buttons[#group.buttons + 1] = button
    end

    function group:Refresh()
        local current = get()
        for _, button in ipairs(self.buttons) do
            Select(button, button.value == current)
        end
    end

    function group:Layout(buttonWidth, padding)
        local x = 0
        for _, button in ipairs(self.buttons) do
            local width = buttonWidth
                or math.max(padding and 44 or 60, math.ceil(button.Text:GetStringWidth()) + (padding or 24))
            button:SetWidth(width)
            button:ClearAllPoints()
            button:SetPoint("LEFT", self, "LEFT", x, 0)
            x = x + width + 4
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
        button:SetScript("OnLeave", function() GameTooltip:Hide() end)
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
    local button = ChoiceButton(parent, text)
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
    check:SetHeight(CONTROL_HEIGHT)
    -- All of the label is clickable, so pin the template's art to its left.
    for _, texture in ipairs({ check:GetNormalTexture(), check:GetPushedTexture(),
        check:GetHighlightTexture(), check:GetCheckedTexture(), check:GetDisabledCheckedTexture() }) do
        texture:ClearAllPoints()
        texture:SetSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        texture:SetPoint("LEFT")
    end
    check.text = check:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    check.text:SetPoint("LEFT", CONTROL_HEIGHT, 0)
    check.text:SetText(text)
    check:SetWidth(CONTROL_HEIGHT + math.ceil(check.text:GetStringWidth()))

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
        check:SetScript("OnLeave", function() GameTooltip:Hide() end)
    end

    check:Refresh()
    return check
end
