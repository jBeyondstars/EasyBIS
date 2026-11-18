local _, ns = ...

--[[
The window's own controls, all in one flat dark style:

  Widgets.Button(parent, text, width, withArrow)   a button; with an arrow, it opens a menu
  Widgets.Dropdown(parent, label, width)           a label over a button with an arrow
                                                   :Set(text, active)   active: the filter narrows the list
  Widgets.Segmented(parent, options, get, set)     two or more buttons, one of them lit
                                                   options: { { value, text }, ... }; :Refresh();
                                                   :Layout(width, padding): every button that wide, or each
                                                   as wide as its text plus the padding (24 when not given)
  Widgets.Toggle(parent, text, get, set)           a button that stays lit while on; :Refresh()
  Widgets.Paint(button, look)                      "idle", "lit" (the chosen one, a switch that is on) or
                                                   "active" (gold)
  Widgets.Click()                                  the game's click sound
  Widgets.Scroll(parent)                           a scroll frame and the frame it scrolls: scroll, child

Gold is kept for a filter that hides something, so a glance at the top of
the window tells whether the list is whole.
]]

local Widgets = {}
ns.Widgets = Widgets

Widgets.FLAT = { bgFile = "Interface\\Buttons\\WHITE8x8", edgeFile = "Interface\\Buttons\\WHITE8x8", edgeSize = 1 }
Widgets.MUTED = { 0.66, 0.66, 0.70 }

local LOOKS = {
    idle = { fill = { 0, 0, 0, 0.45 }, edge = { 1, 1, 1, 0.16 }, text = { 0.86, 0.86, 0.88 } },
    lit = { fill = { 1, 1, 1, 0.13 }, edge = { 1, 1, 1, 0.45 }, text = { 1, 1, 1 } },
    active = { fill = { 1, 0.82, 0, 0.14 }, edge = { 1, 0.82, 0, 0.80 }, text = { 1, 0.82, 0 } },
}
local HOVER_EDGE = { 1, 1, 1, 0.60 }

function Widgets.Click()
    if PlaySound and SOUNDKIT then PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON) end
end

function Widgets.Scroll(parent)
    local modern = C_XMLUtil ~= nil and C_XMLUtil.GetTemplateInfo ~= nil
        and C_XMLUtil.GetTemplateInfo("ScrollFrameTemplate") ~= nil
    local scroll = CreateFrame("ScrollFrame", nil, parent, modern and "ScrollFrameTemplate" or "UIPanelScrollFrameTemplate")
    local child = CreateFrame("Frame", nil, scroll)
    child:SetSize(1, 1)
    scroll:SetScrollChild(child)
    return scroll, child
end

function Widgets.Paint(button, look)
    if not LOOKS[look] then look = "idle" end
    button.look = look
    local colors = LOOKS[look]
    local edge = button.hovered and HOVER_EDGE or colors.edge
    button:SetBackdropColor(colors.fill[1], colors.fill[2], colors.fill[3], colors.fill[4])
    button:SetBackdropBorderColor(edge[1], edge[2], edge[3], edge[4])
    button.text:SetTextColor(colors.text[1], colors.text[2], colors.text[3])
    for _, line in ipairs(button.arrow or {}) do
        line:SetColorTexture(colors.text[1], colors.text[2], colors.text[3], 0.9)
    end
end

function Widgets.Button(parent, text, width, withArrow)
    local button = CreateFrame("Button", nil, parent, "BackdropTemplate")
    button:SetBackdrop(Widgets.FLAT)
    button:SetHeight(22)
    button.text = button:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    button.text:SetWordWrap(false)
    button.text:SetText(text or "")
    if withArrow then
        button.text:SetPoint("LEFT", 8, 0)
        button.text:SetPoint("RIGHT", -18, 0)
        button.text:SetJustifyH("LEFT")
        -- a small triangle pointing down, drawn with four lines: no picture to load
        button.arrow = {}
        for index = 0, 3 do
            local line = button:CreateTexture(nil, "OVERLAY")
            line:SetSize(7 - 2 * index, 1)
            line:SetPoint("TOP", button, "RIGHT", -10, 2 - index)
            button.arrow[index + 1] = line
        end
    else
        button.text:SetPoint("CENTER")
    end
    button:SetWidth(width or math.max(60, math.ceil(button.text:GetStringWidth()) + 24))
    button:SetScript("OnEnter", function(self)
        self.hovered = true
        Widgets.Paint(self, self.look)
    end)
    button:SetScript("OnLeave", function(self)
        self.hovered = false
        Widgets.Paint(self, self.look)
    end)
    Widgets.Paint(button, "idle")
    return button
end

function Widgets.Dropdown(parent, label, width)
    local filter = CreateFrame("Frame", nil, parent)
    filter:SetSize(width, 38)
    filter.label = filter:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    filter.label:SetPoint("TOPLEFT", 2, 0)
    filter.label:SetText(label)
    filter.label:SetTextColor(Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3])
    filter.button = Widgets.Button(filter, " ", width, true)
    filter.button:SetPoint("BOTTOMLEFT", 0, 0)

    function filter:Set(text, active)
        self.button.text:SetText(text)
        Widgets.Paint(self.button, active and "active" or "idle")
    end

    return filter
end

function Widgets.Segmented(parent, options, get, set)
    local group = CreateFrame("Frame", nil, parent)
    group:SetHeight(22)
    group.buttons = {}
    for _, option in ipairs(options) do
        local button = Widgets.Button(group, option.text)
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
            Widgets.Paint(button, button.value == current and "lit" or "idle")
        end
    end

    function group:Layout(buttonWidth, padding)
        local x = 0
        for _, button in ipairs(self.buttons) do
            local width = buttonWidth
                or math.max(padding and 44 or 60, math.ceil(button.text:GetStringWidth()) + (padding or 24))
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

function Widgets.Toggle(parent, text, get, set)
    local button = Widgets.Button(parent, text)
    button:SetScript("OnClick", function()
        Widgets.Click()
        set(not get())
    end)

    function button:Refresh()
        Widgets.Paint(self, get() and "lit" or "idle")
    end

    button:Refresh()
    return button
end
