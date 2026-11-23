local _, ns = ...
local L, Widgets = ns.L, ns.Widgets

--[[
The EasyBis tab of the auction house: the gear of a spec's list that is on sale, each piece with its
lowest buyout.

  top    where the game has its search bar: the spec and the list to look for (the window's own filters,
         so both show the same choice), the phase, what the scan is doing, and the scan's button.
  list   the game's own results list (Blizzard_AuctionHouseItemList.xml, the browse layout of
         Blizzard_AuctionHouseTableBuilder.lua) with its sizes, fonts and pictures, over the frame's
         whole width since there are no categories on its left: price, item, rank, slot. A click on a
         line opens the item's auctions in the game's Buy tab.
]]

local TAB = "EasyBis"
local TAB_PADDING, TAB_MIN_WIDTH = 20, 70   -- as LibAHTab sizes a tab
local ROW_HEIGHT, HEADER_HEIGHT = 20, 19
local RANK_WIDTH, SLOT_WIDTH = 100, 146
local PADDING = 10          -- before a column's text
local UNKNOWN_ICON = 134400
local FONT = Number14FontWhite and "Number14FontWhite" or "GameFontHighlight"
local MUTED = Widgets.MUTED
local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetIcon = (C_Item and C_Item.GetItemIconByID) or GetItemIcon

local panel, tab, scanning, priceWidth
local offers, rows = {}, {}

local function HasTemplate(name)
    return C_XMLUtil ~= nil and C_XMLUtil.GetTemplateInfo ~= nil and C_XMLUtil.GetTemplateInfo(name) ~= nil
end

local function Text(parent, font, alignment)
    local text = parent:CreateFontString(nil, "OVERLAY", font)
    text:SetJustifyH(alignment or "LEFT")
    text:SetWordWrap(false)
    return text
end

-- A column's title, as the game draws one that does not sort.
local function Header(parent, title)
    local template = HasTemplate("ColumnDisplayButtonShortTemplate") and "ColumnDisplayButtonShortTemplate" or nil
    local header = CreateFrame("Button", nil, parent, template)
    header:SetHeight(HEADER_HEIGHT)
    header:SetEnabled(false)
    if template then
        header:SetText(title)
    else
        local label = Text(header, "GameFontHighlightSmall")
        label:SetPoint("LEFT", 8, 0)
        label:SetText(title)
    end
    return header
end

-- A price as the game's lists show one, each coin in its own column; in one text where the client
-- lacks the template.
local function Price(row)
    local right = priceWidth - 2 * PADDING
    if HasTemplate("MoneyDisplayFrameTemplate") then
        local money = CreateFrame("Frame", nil, row, "MoneyDisplayFrameTemplate")
        money.useAuctionHouseCopperValue, money.useAuctionHouseIcons = true, true
        money:OnLoad()   -- the template read those two when the frame was made
        money:SetPoint("RIGHT", row, "LEFT", right, 0)
        return money
    end
    local text = Text(row, FONT, "RIGHT")
    text:SetPoint("LEFT")
    text:SetPoint("RIGHT", row, "LEFT", right, 0)
    function text:SetAmount(copper) self:SetText(GetMoneyString(copper, true)) end
    return text
end

local function NewRow(index)
    local row = CreateFrame("Button", nil, panel.child)
    row:SetPoint("TOPLEFT", 0, -(index - 1) * ROW_HEIGHT)
    row:SetPoint("TOPRIGHT", 0, -(index - 1) * ROW_HEIGHT)
    row:SetHeight(ROW_HEIGHT)
    local highlight = row:CreateTexture(nil, "HIGHLIGHT")
    highlight:SetAllPoints()
    highlight:SetAtlas("auctionhouse-ui-row-highlight")
    highlight:SetBlendMode("ADD")

    row.price = Price(row)
    row.icon = row:CreateTexture(nil, "BACKGROUND", nil, 1)
    row.icon:SetPoint("LEFT", priceWidth + PADDING, 0)
    row.icon:SetSize(14, 14)
    local border = row:CreateTexture(nil, "BACKGROUND", nil, 2)
    border:SetAtlas("auctionhouse-itemicon-small-border")
    border:SetSize(16, 16)
    border:SetPoint("CENTER", row.icon)
    row.item = Text(row, FONT)
    row.item:SetPoint("LEFT", row.icon, "RIGHT", 4, 0)
    row.item:SetPoint("RIGHT", -RANK_WIDTH - SLOT_WIDTH, 0)
    row.rank = Text(row, FONT)
    row.rank:SetPoint("LEFT", row, "RIGHT", PADDING - RANK_WIDTH - SLOT_WIDTH, 0)
    row.rank:SetPoint("RIGHT", -SLOT_WIDTH, 0)
    row.slot = Text(row, FONT)
    row.slot:SetPoint("LEFT", row, "RIGHT", PADDING - SLOT_WIDTH, 0)
    row.slot:SetPoint("RIGHT", -4, 0)

    row:SetScript("OnEnter", function(self)
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        if self.data.link then GameTooltip:SetHyperlink(self.data.link)
        else GameTooltip:SetItemByID(self.data.key.itemID) end
        GameTooltip:Show()
    end)
    row:SetScript("OnLeave", ns.Tooltip.HideOwned)
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

-- The name of the auction itself, which says the random enchantment the item key leaves out.
local function Name(data, info)
    return (data.link and data.link:match("%[(.-)%]")) or (info and info.itemName) or ns.Items.Name(data.key.itemID)
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
        local id = data.key.itemID
        -- the variant's own details may still be loading: the item's quality and picture are the same
        local info = C_AuctionHouse.GetItemKeyInfo(data.key)
        local _, _, _, hex = ns.QualityColor(info and info.quality or (GetInfo and select(3, GetInfo(id))))
        row.data = data
        row.item:SetText(hex .. Name(data, info) .. "|r")
        row.icon:SetTexture(info and info.iconFileID or (GetIcon and GetIcon(id)) or UNKNOWN_ICON)
        row.rank:SetText(data.option and data.option.label or (data.bis and ("|cffffd100" .. L.RANK_BIS .. "|r") or data.label))
        row.slot:SetText(ns.SlotName(data.slot))
        row.price:SetAmount(data.price)
        row:Show()
    end
    for i = #sorted + 1, #rows do rows[i]:Hide() end
    panel.child:SetHeight(math.max(1, #sorted * ROW_HEIGHT))
    return #sorted
end

local function ShowTarget()
    panel.spec:Refresh()
    panel.list:Refresh()
    panel.phase:SetText(ns.PhaseName(ns.Phase()))
end

local function Reset()
    if not panel then return end
    ns.AuctionScan.Stop()
    offers = {}
    Draw()
    panel.scroll:SetVerticalScroll(0)
    ShowTarget()
    panel.status:SetText(L.AH_IDLE)
end

local function Start()
    local class, spec, list = ns.Browser.Target()
    local wanted, ids, order = {}, {}, {}
    for _, row in ipairs(ns.Rows.Items({ class = class, spec = spec, list = list }, true)) do
        -- what binds when picked up is never on sale; what the game has not described yet is searched
        if row.kind == "item" and ns.Reputation.Binding(row.id) ~= "pickup" then
            local bis = row.bis or row.tie or false
            local old = wanted[row.id]
            if not old then
                ids[#ids + 1] = row.id
                order[row.id] = #ids
            end
            if not old or (bis and not old.bis) or (old.custom and not row.custom) then
                wanted[row.id] = { bis = bis, slot = row.slot, custom = row.custom, option = row.option }
            end
        end
    end
    -- the best picks first: theirs are the prices to see first
    table.sort(ids, function(a, b)
        if wanted[a].bis ~= wanted[b].bis then return wanted[a].bis end
        return order[a] < order[b]
    end)
    Reset()
    scanning = true
    panel.scan:SetText(L.AH_STOP)
    ns.AuctionScan.Start(ids, function(index, total)
        panel.status:SetText(L.AH_CHECK:format(index, total))
    end, function(key, price, link)
        local old = offers[key.itemID]
        if old and old.price <= price then return end
        local pick = wanted[key.itemID]
        offers[key.itemID] = { key = key, price = price, link = link, bis = pick.bis, slot = pick.slot, option = pick.option,
            label = pick.custom and L.RANK_CUSTOM or L.AH_ALTERNATIVE }
        Draw()
    end, function(complete)
        scanning = false
        panel.scan:SetText(L.AH_SCAN)
        local count = Draw()
        panel.status:SetText(complete and (count == 0 and L.AH_EMPTY or L.AH_COUNT:format(count)) or L.AH_INCOMPLETE)
    end)
end

-- The spec and the list, the phase and what the scan is doing, the scan's button. The game's search
-- bar lies between 29 and 69 under the frame's top, right of the portrait.
local function BuildBar()
    panel.spec = ns.Browser.SpecFilter(panel)
    panel.spec:SetPoint("TOPLEFT", 70, -28)
    panel.list = ns.Browser.ListFilter(panel)
    panel.list:SetPoint("BOTTOMLEFT", panel.spec, "BOTTOMRIGHT", 8, 0)
    panel.scan = Widgets.Button(panel, L.AH_SCAN, 134)
    panel.scan:SetPoint("BOTTOMRIGHT", panel, "TOPRIGHT", -12, -66)
    panel.scan:SetScript("OnClick", function()
        if scanning then ns.AuctionScan.Stop() else Start() end
    end)
    -- two lines at most between the list and the button, level with them
    panel.status = Text(panel, "GameFontHighlightSmall")
    panel.status:SetWordWrap(true)
    panel.status:SetJustifyV("MIDDLE")
    panel.status:SetHeight(panel.scan:GetHeight())
    panel.status:SetPoint("LEFT", panel.list, "RIGHT", 12, 0)
    panel.status:SetPoint("RIGHT", panel.scan, "LEFT", -10, 0)
    panel.status:SetText(L.AH_IDLE)
    panel.phase = Text(panel, "GameFontHighlightSmall")
    panel.phase:SetTextColor(MUTED[1], MUTED[2], MUTED[3])
    panel.phase:SetPoint("BOTTOMLEFT", panel.status, "TOPLEFT", 0, 2)
end

-- The list sits where the game's categories and results do, 73 under the frame's top and 27 over its
-- bottom. As in the game, the titles stand over the border, and the scroll bar on its right.
local function BuildList()
    local list = CreateFrame("Frame", nil, panel)
    list:SetPoint("TOPLEFT", 4, -74)
    list:SetPoint("BOTTOMRIGHT", -5, 27)
    local border = CreateFrame("Frame", nil, list, "InsetFrameTemplate")
    border:SetPoint("TOPLEFT", 0, -HEADER_HEIGHT)
    border:SetPoint("BOTTOMRIGHT", -22, 0)
    local back = border:CreateTexture(nil, "BACKGROUND", nil, 1)   -- over the template's own
    back:SetAtlas("auctionhouse-background-index")
    back:SetPoint("TOPLEFT", 3, -3)
    back:SetPoint("BOTTOMRIGHT", -3, 3)

    local headers = CreateFrame("Frame", nil, list)
    headers:SetPoint("TOPLEFT", 4, -1)
    headers:SetPoint("TOPRIGHT", -26, -1)
    headers:SetHeight(HEADER_HEIGHT)
    -- each title runs two points under the next, as the game's
    local price = Header(headers, L.AH_BUYOUT)
    price:SetPoint("TOPLEFT")
    price:SetWidth(priceWidth + 2)
    local slot = Header(headers, L.FILTER_SLOT)
    slot:SetPoint("TOPRIGHT")
    slot:SetWidth(SLOT_WIDTH)
    local rank = Header(headers, L.AH_RANK)
    rank:SetPoint("TOPRIGHT", slot, "TOPLEFT", 2, 0)
    rank:SetWidth(RANK_WIDTH + 2)
    local item = Header(headers, AUCTION_HOUSE_BROWSE_HEADER_NAME or L.TAB_ITEMS)
    item:SetPoint("TOPLEFT", price, "TOPRIGHT", -2, 0)
    item:SetPoint("TOPRIGHT", rank, "TOPLEFT", 2, 0)

    -- in the border's frame: over its background
    panel.scroll, panel.child = Widgets.Scroll(border)
    panel.scroll:SetPoint("TOPLEFT", headers, "BOTTOMLEFT", 0, -6)
    panel.scroll:SetPoint("BOTTOMRIGHT", list, "BOTTOMRIGHT", -26, 3)
    panel.scroll:HookScript("OnSizeChanged", function(_, width) panel.child:SetWidth(math.max(1, width)) end)
end

local function Attach()
    local house = AuctionHouseFrame
    if panel or not ns:GetOption("auctionTab") or not house or not house.Tabs or not C_AuctionHouse then return end
    -- the game's price column, wider where the auction house counts copper
    priceWidth = C_AuctionHouse.SupportsCopperValues and C_AuctionHouse.SupportsCopperValues() and 168 or 146
    panel = CreateFrame("Frame", "EasyBISAuctionPanel", house)
    panel:Hide()
    panel:SetAllPoints()
    BuildBar()
    BuildList()
    panel:SetScript("OnShow", function()
        ShowTarget()
        panel.child:SetWidth(math.max(1, panel.scroll:GetWidth()))
    end)
    panel:SetScript("OnHide", ns.AuctionScan.Stop)

    local tabs = LibStub and LibStub("LibAHTab-1-0", true)
    if tabs then
        tabs:CreateTab("EasyBIS", panel, TAB)
        tab = tabs:GetButton("EasyBIS")
    else
        tab = CreateFrame("Button", "EasyBISAuctionTab", house, "AuctionHouseFrameDisplayModeTabTemplate")
        tab:SetText(TAB)
        tab:SetPoint("TOPLEFT", house.Tabs[#house.Tabs], "TOPRIGHT", 3, 0)
        PanelTemplates_TabResize(tab, TAB_PADDING, nil, TAB_MIN_WIDTH)
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

-- The option that shows the tab. Switched off, the tab leaves the bar, gives its room back to the tabs
-- after it, and the game's Buy tab takes over when ours was open.
local function ShowTab()
    local on = ns:GetOption("auctionTab")
    if not panel then
        if on then Attach() end
        return
    end
    if not on and panel:IsShown() then AuctionHouseFrame:SetDisplayMode(AuctionHouseFrameDisplayMode.Buy) end
    tab:SetShown(on)
    if on then PanelTemplates_TabResize(tab, TAB_PADDING, nil, TAB_MIN_WIDTH) else tab:SetWidth(0.01) end
end

local events = CreateFrame("Frame")
events:RegisterEvent("AUCTION_HOUSE_SHOW")
events:RegisterEvent("PLAYER_INTERACTION_MANAGER_FRAME_SHOW")
events:RegisterEvent("AUCTION_HOUSE_CLOSED")
events:SetScript("OnEvent", function(_, event, arg)
    if event == "AUCTION_HOUSE_CLOSED" then
        Reset()
    elseif event == "AUCTION_HOUSE_SHOW"
        or (event == "PLAYER_INTERACTION_MANAGER_FRAME_SHOW" and arg == Enum.PlayerInteractionType.Auctioneer) then
        -- A frame later: the tab comes last, after those other addons (Auctionator) add as the house opens.
        C_Timer.After(0, Attach)
    end
end)

ns:On("TARGET_CHANGED", Reset)
ns:On("CUSTOM_CHANGED", Reset)
ns:On("OPTION_CHANGED", function(key)
    if key == "auctionTab" then ShowTab() elseif ns.FILTER_OPTIONS[key] then Reset() end
end)
