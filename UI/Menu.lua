local _, ns = ...
local W = ns.Widgets

-- Blizzard_Menu pools buttons for the LFG category picker. Easy BIS keeps
-- its filter and options rows in separate panels and reuses them on each open.
local Menu = {}
ns.Menu = Menu
local panels = {}
local ROW, PAD = 22, 5

local function CloseFrom(level)
    for i = #panels, level, -1 do
        local panel = panels[i]
        panel:Hide()
        for _, row in ipairs(panel.rows) do row.entry = nil end
        panel:ClearAllPoints()
        panel.anchor, panel.entries = nil, nil
    end
end

local function RefreshMarks()
    for _, panel in ipairs(panels) do
        for i, entry in ipairs(panel.entries or {}) do
            panel.rows[i].mark:SetShown(entry.selected and entry.selected() or false)
        end
    end
end

local ShowLevel

local function Enter(row)
    local level = row.panel.level + 1
    if row.entry.items then
        ShowLevel(level, row, row.entry.items)
    else
        CloseFrom(level)
    end
end

local function Pick(row)
    if row.entry.items then
        Enter(row)
    elseif row.entry.pick then
        local pick = row.entry.pick
        if not panels[1].keepOpen then CloseFrom(1) end
        W.Click()
        pick()
        RefreshMarks()
    end
end

local function MakeRow(panel)
    local row = CreateFrame("Button", nil, panel.child)
    row.panel = panel
    row:SetHeight(ROW)
    W.ListHighlight(row, "HIGHLIGHT", 0.5)
    row.label = row:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    row.label:SetPoint("LEFT", 20, 0)
    row.mark = row:CreateTexture(nil, "ARTWORK")
    row.mark:SetSize(16, 16)
    row.mark:SetPoint("LEFT", 1, 0)
    row.arrow = row:CreateTexture(nil, "ARTWORK")
    row.arrow:SetSize(14, 14)
    row.arrow:SetPoint("RIGHT", -2, 0)
    row.arrow:SetTexture("Interface\\ChatFrame\\ChatFrameExpandArrow")
    row:SetScript("OnEnter", Enter)
    row:SetScript("OnClick", Pick)
    return row
end

local function MakePanel(level)
    local panel = CreateFrame("Frame", nil, UIParent, "BackdropTemplate")
    panel.rows, panel.level = {}, level
    panel:SetFrameStrata("FULLSCREEN_DIALOG")
    panel:SetFrameLevel(100 + level * 10)
    panel:SetClampedToScreen(true)
    panel:EnableMouse(true)
    panel:SetBackdrop(W.FLAT)
    panel:SetBackdropColor(0.06, 0.06, 0.07, 0.98)
    panel:SetBackdropBorderColor(0.44, 0.40, 0.32, 1)
    panel.scroll, panel.child = W.Scroll(panel)
    panel.scroll:SetPoint("TOPLEFT", PAD, -PAD)
    if level == 1 then
        panel:SetScript("OnShow", function(self) self:RegisterEvent("GLOBAL_MOUSE_DOWN") end)
        panel:SetScript("OnHide", function(self) self:UnregisterEvent("GLOBAL_MOUSE_DOWN") end)
        panel:SetScript("OnEvent", function(self)
            if self.anchor and self.anchor:IsMouseOver() then return end
            for _, open in ipairs(panels) do
                if open:IsShown() and open:IsMouseOver() then return end
            end
            CloseFrom(1)
        end)
    end
    panel:Hide()
    panels[level] = panel
    return panel
end

ShowLevel = function(level, anchor, entries)
    local panel = panels[level] or MakePanel(level)
    if panel:IsShown() and panel.anchor == anchor and panel.entries == entries then return end
    CloseFrom(level + 1)
    panel.anchor, panel.entries = anchor, entries
    local width, height = anchor:GetWidth(), 0
    for i, entry in ipairs(entries) do
        local row = panel.rows[i] or MakeRow(panel)
        panel.rows[i], row.entry = row, entry
        row.label:SetText(entry.text or "")
        row.label:SetFontObject(entry.kind == "title" and "GameFontNormal" or "GameFontHighlight")
        row.arrow:SetShown(entry.items ~= nil)
        row:SetEnabled(entry.pick ~= nil or entry.items ~= nil)
        row:ClearAllPoints()
        row:SetPoint("TOPLEFT", 0, -height)
        row:SetPoint("TOPRIGHT", panel.child, "TOPRIGHT", 0, -height)
        if entry.kind == "radio" then
            row.mark:SetAtlas("common-dropdown-icon-radialtick-yellow-classic")
        else
            row.mark:SetTexture("Interface\\Buttons\\UI-CheckBox-Check")
        end
        row:SetHeight(entry.kind == "divider" and 6 or ROW)
        width = math.max(width, row.label:GetStringWidth() + 42)
        height = height + row:GetHeight()
        row:Show()
    end
    for i = #entries + 1, #panel.rows do
        panel.rows[i].entry = nil
        panel.rows[i]:Hide()
    end
    local visible = math.min(420, height)
    panel.child:SetSize(width, height)
    panel.scroll:SetSize(width, visible)
    panel.scroll:SetVerticalScroll(0)
    width = width + 2 * PAD + (visible < height and 20 or 0)
    panel:SetSize(width, visible + 2 * PAD)
    panel:ClearAllPoints()
    if level == 1 then
        if (anchor:GetBottom() or 0) < panel:GetHeight() then
            panel:SetPoint("BOTTOMLEFT", anchor, "TOPLEFT")
        else
            panel:SetPoint("TOPLEFT", anchor, "BOTTOMLEFT")
        end
    elseif (anchor:GetRight() or 0) + width > UIParent:GetWidth() then
        panel:SetPoint("TOPRIGHT", anchor, "TOPLEFT")
    else
        panel:SetPoint("TOPLEFT", anchor, "TOPRIGHT")
    end
    RefreshMarks()
    panel:Show()
end

function Menu.Attach(button, entries, keepOpen)
    button:SetScript("OnClick", function()
        local root = panels[1]
        if root and root:IsShown() and root.anchor == button then
            CloseFrom(1)
            return
        end
        W.Click()
        ShowLevel(1, button, entries())
        panels[1].keepOpen = keepOpen
    end)
    button:HookScript("OnHide", function()
        if panels[1] and panels[1].anchor == button then CloseFrom(1) end
    end)
end
