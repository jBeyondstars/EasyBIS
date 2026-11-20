local _, ns = ...
local L, Widgets = ns.L, ns.Widgets
local TAB = "EasyBis"
local panel, scanning
local offers, rows = {}, {}

local function Text(parent, font, alignment)
    local text = parent:CreateFontString(nil, "OVERLAY", font)
    text:SetJustifyH(alignment or "LEFT")
    text:SetWordWrap(false)
    return text
end

local function Columns(line, font, iconWidth)
    line.price = Text(line, font, "RIGHT")
    line.price:SetPoint("RIGHT", -6, 0)
    line.price:SetWidth(152)
    line.slot = Text(line, font)
    line.slot:SetPoint("RIGHT", line.price, "LEFT", -10, 0)
    line.slot:SetWidth(136)
    line.rank = Text(line, font)
    line.rank:SetPoint("RIGHT", line.slot, "LEFT", -10, 0)
    line.rank:SetWidth(90)
    line.item = Text(line, font)
    line.item:SetPoint("LEFT", iconWidth, 0)
    line.item:SetPoint("RIGHT", line.rank, "LEFT", -10, 0)
end

local function NewRow(index)
    local row = CreateFrame("Button", nil, panel.child)
    row:SetPoint("TOPLEFT", 0, -(index - 1) * 28)
    row:SetPoint("TOPRIGHT", 0, -(index - 1) * 28)
    row:SetHeight(28)
    Widgets.ListHighlight(row, "HIGHLIGHT", 0.5)
    row.icon = row:CreateTexture(nil, "ARTWORK")
    row.icon:SetPoint("LEFT", 4, 0)
    row.icon:SetSize(22, 22)
    Columns(row, "GameFontHighlight", 32)
    row:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        if self.data.link then GameTooltip:SetHyperlink(self.data.link)
        else GameTooltip:SetItemByID(self.data.key.itemID) end
        GameTooltip:Show()
    end)
    row:SetScript("OnLeave", function() GameTooltip:Hide() end)
    row:SetScript("OnClick", function(self)
        local data = self.data
        if C_AuctionHouse.GetItemKeyInfo(data.key) then
            AuctionHouseFrame:SetDisplayMode(AuctionHouseFrameDisplayMode.Buy)
            AuctionHouseFrame:SelectBrowseResult({ itemKey = data.key, minPrice = data.price })
        end
    end)
    rows[index] = row
    return row
end

local function Draw()
    local sorted = {}
    for _, data in pairs(offers) do sorted[#sorted + 1] = data end
    table.sort(sorted, function(a, b)
        if a.bis ~= b.bis then return a.bis end
        if a.price ~= b.price then return a.price < b.price end
        return a.key.itemID < b.key.itemID
    end)
    for i, data in ipairs(sorted) do
        local row = rows[i] or NewRow(i)
        local info = C_AuctionHouse.GetItemKeyInfo(data.key)
        row.data = data
        row.item:SetText(data.link or (info and info.itemName) or ns.Items.Name(data.key.itemID))
        row.icon:SetTexture(info and info.iconFileID or 134400)
        row.rank:SetText(data.bis and ("|cffffd100" .. L.RANK_BIS .. "|r") or data.label)
        row.slot:SetText(ns.SlotName(data.slot))
        row.price:SetText(GetMoneyString(data.price))
        row:Show()
    end
    for i = #sorted + 1, #rows do rows[i]:Hide() end
    panel.child:SetHeight(math.max(1, #sorted * 28))
    return #sorted
end

local function TargetText()
    local class, spec, list = ns.Browser.Target()
    return ns.Custom.ListText(class, spec, list) .. "  ·  " .. ns.PhaseName(ns.Phase())
end

local function Reset()
    if not panel then return end
    ns.AuctionScan.Stop()
    offers = {}
    Draw()
    panel.scroll:SetVerticalScroll(0)
    panel.target:SetText(TargetText())
    panel.status:SetText(L.AH_IDLE)
end

local function Start()
    local class, spec, list = ns.Browser.Target()
    local wanted = {}
    for _, row in ipairs(ns.Rows.Items({ class = class, spec = spec, list = list }, true)) do
        if row.kind == "item" then
            local bis = row.bis or row.tie or false
            local old = wanted[row.id]
            if not old or (bis and not old.bis) or (old.custom and not row.custom) then
                wanted[row.id] = { bis = bis, slot = row.slot, custom = row.custom }
            end
        end
    end
    Reset()
    scanning = true
    panel.scan:SetText(L.AH_STOP)
    panel.status:SetText(L.AH_BROWSE)
    ns.AuctionScan.Start(wanted, function(index, total)
        panel.status:SetText(L.AH_CHECK:format(index, total))
    end, function(key, price, link)
        local old = offers[key.itemID]
        if old and old.price <= price then return end
        local pick = wanted[key.itemID]
        offers[key.itemID] = { key = key, price = price, link = link, bis = pick.bis, slot = pick.slot,
            label = pick.custom and L.RANK_CUSTOM or L.AH_ALTERNATIVE }
        Draw()
    end, function(complete)
        scanning = false
        panel.scan:SetText(L.AH_SCAN)
        local count = Draw()
        panel.status:SetText(complete and (count == 0 and L.AH_EMPTY or L.AH_COUNT:format(count)) or L.AH_INCOMPLETE)
    end)
end

local function Attach()
    local house = AuctionHouseFrame
    if panel or not house or not house.Tabs or not C_AuctionHouse then return end
    panel = CreateFrame("Frame", "EasyBISAuctionPanel", house)
    panel:Hide()
    panel:SetPoint("TOPLEFT", 16, -42)
    panel:SetPoint("BOTTOMRIGHT", -16, 16)
    panel.scan = Widgets.Button(panel, L.AH_SCAN, 134)
    panel.scan:SetPoint("TOPRIGHT")
    panel.scan:SetScript("OnClick", function()
        if scanning then ns.AuctionScan.Stop() else Start() end
    end)
    panel.target = Text(panel, "GameFontNormalLarge")
    panel.target:SetPoint("TOPLEFT", 0, -3)
    panel.target:SetPoint("TOPRIGHT", panel.scan, "TOPLEFT", -10, -3)
    panel.status = Text(panel, "GameFontHighlight")
    panel.status:SetPoint("TOPLEFT", 0, -30)
    panel.status:SetText(L.AH_IDLE)
    local header = CreateFrame("Frame", nil, panel)
    header:SetPoint("TOPLEFT", 0, -58)
    header:SetPoint("TOPRIGHT", -24, -58)
    header:SetHeight(24)
    Columns(header, "GameFontNormalSmall", 4)
    header.item:SetText(L.TAB_ITEMS)
    header.rank:SetText(L.AH_RANK)
    header.slot:SetText(L.FILTER_SLOT)
    header.price:SetText(L.AH_BUYOUT)
    panel.scroll, panel.child = Widgets.Scroll(panel)
    panel.scroll:SetPoint("TOPLEFT", header, "BOTTOMLEFT")
    panel.scroll:SetPoint("BOTTOMRIGHT", -24, 0)
    panel.scroll:HookScript("OnSizeChanged", function(_, width) panel.child:SetWidth(math.max(1, width)) end)
    panel:SetScript("OnShow", function()
        panel.target:SetText(TargetText())
        panel.child:SetWidth(math.max(1, panel.scroll:GetWidth()))
    end)
    panel:SetScript("OnHide", ns.AuctionScan.Stop)

    local tabs = LibStub and LibStub("LibAHTab-1-0", true)
    if tabs then
        tabs:CreateTab("EasyBIS", panel, TAB)
    else
        local tab = CreateFrame("Button", "EasyBISAuctionTab", house, "AuctionHouseFrameDisplayModeTabTemplate")
        tab:SetText(TAB)
        tab:SetPoint("TOPLEFT", house.Tabs[#house.Tabs], "TOPRIGHT", 3, 0)
        PanelTemplates_TabResize(tab, 20, nil, 70)
        PanelTemplates_DeselectTab(tab)
        tab:SetScript("OnClick", function()
            house:SetDisplayMode({})
            for _, other in ipairs(house.Tabs) do PanelTemplates_DeselectTab(other) end
            PanelTemplates_SelectTab(tab)
            house:SetTitle(TAB)
            panel:Show()
        end)
        hooksecurefunc(house, "SetDisplayMode", function(_, mode)
            if mode and #mode > 0 then
                panel:Hide()
                PanelTemplates_DeselectTab(tab)
            end
        end)
    end
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("AUCTION_HOUSE_SHOW")
events:RegisterEvent("PLAYER_INTERACTION_MANAGER_FRAME_SHOW")
events:RegisterEvent("AUCTION_HOUSE_CLOSED")
events:SetScript("OnEvent", function(_, event, arg)
    if event == "AUCTION_HOUSE_CLOSED" then
        Reset()
    elseif event == "AUCTION_HOUSE_SHOW" or (event == "ADDON_LOADED" and arg == "Blizzard_AuctionHouseUI")
        or (event == "PLAYER_INTERACTION_MANAGER_FRAME_SHOW" and arg == Enum.PlayerInteractionType.Auctioneer) then
        Attach()
    end
end)

ns:On("TARGET_CHANGED", Reset)
ns:On("CUSTOM_CHANGED", Reset)
ns:On("OPTION_CHANGED", function(key) if ns.FILTER_OPTIONS[key] then Reset() end end)
