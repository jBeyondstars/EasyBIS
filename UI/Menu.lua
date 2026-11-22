local _, ns = ...
local W = ns.Widgets

-- Blizzard_Menu pools buttons for the LFG category picker. Easy BIS keeps
-- its filter and options rows in separate panels and reuses them on each open.
local Menu = {}
ns.Menu = Menu
local panels = {}
local ROW = 20
local FILTER = { atlas = "common-dropdown-classic-bg", padX = 16, padY = 10, top = 3 }
local OPTIONS = { atlas = "common-dropdown-classic-b-bg", padX = 14, padY = 14, top = 1 }
local function HasAtlas(name)
    return C_Texture and C_Texture.GetAtlasInfo and C_Texture.GetAtlasInfo(name) ~= nil
end

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
            local mark = panel.rows[i].mark
            local selected = entry.selected and entry.selected()
            if entry.kind == "radio" then
                local atlas = selected and "common-dropdown-icon-radialtick-yellow-classic" or "common-dropdown-tickradial-classic"
                if HasAtlas(atlas) then
                    mark:SetAtlas(atlas, true)
                else
                    mark:SetTexture("Interface\\Buttons\\UI-RadioButton")
                    local left = selected and 0.25 or 0
                    mark:SetTexCoord(left, left + 0.25, 0, 1)
                    mark:SetSize(16, 16)
                end
            elseif entry.kind == "checkbox" then
                mark:SetTexture("Interface\\Buttons\\UI-CheckBox-Check")
                mark:SetTexCoord(0, 1, 0, 1)
                mark:SetSize(20, 20)
            end
            mark:SetShown(entry.kind == "radio" or selected or false)
        end
    end
end

local ShowLevel

local function Enter(row)
    local level = row.panel.level + 1
    if row.entry.items then
        ShowLevel(level, row, row.entry.items, row.panel.style)
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
    W.ListHighlight(row, "HIGHLIGHT", 1)
    row.label = row:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    row.mark = row:CreateTexture(nil, "ARTWORK")
    row.mark:SetPoint("LEFT")
    row.divider = row:CreateTexture(nil, "ARTWORK")
    row.divider:SetTexture("Interface\\Common\\UI-TooltipDivider-Transparent")
    row.divider:SetPoint("LEFT")
    row.divider:SetPoint("RIGHT")
    row.divider:SetHeight(13)
    row.arrow = row:CreateTexture(nil, "ARTWORK")
    row.arrow:SetSize(16, 16)
    row.arrow:SetPoint("RIGHT")
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
    local fill = panel:CreateTexture(nil, "BACKGROUND")
    fill:SetColorTexture(0, 0, 0, 0.8)
    fill:SetPoint("TOPLEFT", 3, -3)
    fill:SetPoint("BOTTOMRIGHT", -3, 3)
    panel.border = panel:CreateTexture(nil, "BORDER")
    panel.scroll, panel.child = W.Scroll(panel)
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

ShowLevel = function(level, anchor, entries, style)
    local panel = panels[level] or MakePanel(level)
    if panel:IsShown() and panel.anchor == anchor and panel.entries == entries then return end
    CloseFrom(level + 1)
    panel.anchor, panel.entries, panel.style = anchor, entries, style
    local native = HasAtlas(style.atlas)
    if native then
        panel:SetBackdrop(nil)
        panel.border:SetAtlas(style.atlas)
    else
        panel:SetBackdrop({ edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border", edgeSize = 14 })
    end
    panel.border:SetShown(native and true or false)
    panel.border:ClearAllPoints()
    panel.border:SetPoint("TOPLEFT", -3, style.top)
    panel.border:SetPoint("BOTTOMRIGHT", 3, -4)
    panel.scroll:ClearAllPoints()
    panel.scroll:SetPoint("TOPLEFT", style.padX, -style.padY)
    local width, height = anchor:GetWidth(), 0
    for i, entry in ipairs(entries) do
        local row = panel.rows[i] or MakeRow(panel)
        panel.rows[i], row.entry = row, entry
        row.label:SetText(entry.text or "")
        row.label:SetFontObject(entry.kind == "title" and "GameFontNormal" or "GameFontHighlight")
        row.label:ClearAllPoints()
        if entry.selected then
            row.label:SetPoint("LEFT", row.mark, "RIGHT", 2, 0)
        else
            row.label:SetPoint("LEFT")
        end
        row.divider:SetShown(entry.kind == "divider")
        row.arrow:SetShown(entry.items ~= nil)
        row:SetEnabled(entry.pick ~= nil or entry.items ~= nil)
        row:ClearAllPoints()
        row:SetPoint("TOPLEFT", 0, -height)
        row:SetPoint("TOPRIGHT", panel.child, "TOPRIGHT", 0, -height)
        row:SetHeight(entry.kind == "divider" and 13 or ROW)
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
    width = width + 2 * style.padX + (visible < height and 20 or 0)
    panel:SetSize(width, visible + 2 * style.padY)
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
    -- The native control paints the pressed state. Only our private panel supplies menu rows.
    button:HookScript("OnMouseDown", function(self, mouseButton)
        if mouseButton ~= "LeftButton" or not self:IsEnabled() then return end
        local root = panels[1]
        if root and root:IsShown() and root.anchor == button then
            CloseFrom(1)
            return
        end
        W.Click()
        ShowLevel(1, button, entries(), keepOpen and OPTIONS or FILTER)
        panels[1].keepOpen = keepOpen
    end)
    button:HookScript("OnHide", function()
        if panels[1] and panels[1].anchor == button then CloseFrom(1) end
    end)
end
