local _, ns = ...

-- Browse first to discover the exact keys on sale (including level and random suffix).
-- A browse price can be a bid. Only publish a price after reading the actual buyouts.
local Scan = {}
ns.AuctionScan = Scan

local active, frame
local events = {
    "AUCTION_HOUSE_BROWSE_RESULTS_UPDATED", "AUCTION_HOUSE_BROWSE_RESULTS_ADDED", "AUCTION_HOUSE_BROWSE_FAILURE",
    "ITEM_SEARCH_RESULTS_UPDATED", "ITEM_SEARCH_RESULTS_ADDED",
    "COMMODITY_SEARCH_RESULTS_UPDATED", "COMMODITY_SEARCH_RESULTS_ADDED", "AUCTION_HOUSE_CLOSED",
}

local function Finish(complete)
    if not active then return end
    local job = active
    active = nil
    frame:SetScript("OnUpdate", nil)
    for _, event in ipairs(events) do frame:UnregisterEvent(event) end
    job.finished(complete)
end

function Scan.Stop()
    Finish(false)
end

local function Schedule(job, action)
    job.pending, job.waiting, job.elapsed = action, nil, 0
end

local function NextKey(job)
    job.index = job.index + 1
    job.key = job.keys[job.index]
    if not job.key then return Finish(not job.incomplete) end
    Schedule(job, "search")
    job.progress(job.index, #job.keys)
end

local function ReadBrowse(job)
    local ah = C_AuctionHouse
    if not ah.HasFullBrowseResults() then
        Schedule(job, "moreBrowse")
        return
    end
    -- GetBrowseResults contains all the pages accumulated for this query.
    for _, result in ipairs(ah.GetBrowseResults()) do
        local key = result.itemKey
        if key and job.wanted[key.itemID] and result.totalQuantity > 0 then
            job.keys[#job.keys + 1] = key
            ah.GetItemKeyInfo(key) -- start loading metadata for the subsequent searches
        end
    end
    NextKey(job)
end

local function ReadBuyouts(job, commodity)
    local ah, key = C_AuctionHouse, job.key
    local arg = commodity and key.itemID or key
    local full = commodity and ah.HasFullCommoditySearchResults or ah.HasFullItemSearchResults
    if not full(arg) then
        Schedule(job, commodity and "moreCommodity" or "moreItem")
        return
    end

    local count = commodity and ah.GetNumCommoditySearchResults or ah.GetNumItemSearchResults
    local get = commodity and ah.GetCommoditySearchResultInfo or ah.GetItemSearchResultInfo
    local lowest, link
    for i = 1, count(arg) do
        local row = get(arg, i)
        if row then
            local price = commodity and row.unitPrice or row.buyoutAmount
            local available = not row.containsOwnerItem and not row.containsAccountItem
            if commodity and row.numOwnerItems and not row.containsAccountItem then
                available = row.quantity > row.numOwnerItems
            end
            if available and row.quantity > 0 and price and price > 0 and (not lowest or price < lowest) then
                lowest, link = price, row.itemLink
            end
        end
    end
    if lowest then job.offer(key, lowest, link) end
    NextKey(job)
end

local function SameKey(a, b)
    return a and b and a.itemID == b.itemID and a.itemLevel == b.itemLevel and a.itemSuffix == b.itemSuffix
        and a.battlePetSpeciesID == b.battlePetSpeciesID
end

local function OnEvent(_, event, arg)
    local job = active
    if not job then return end
    if event == "AUCTION_HOUSE_CLOSED" then return Finish(false) end
    local waiting = job.waiting
    if waiting == "browse" or waiting == "moreBrowse" then
        if event == "AUCTION_HOUSE_BROWSE_FAILURE" then return Finish(false) end
        if event == "AUCTION_HOUSE_BROWSE_RESULTS_UPDATED"
            or (waiting == "moreBrowse" and event == "AUCTION_HOUSE_BROWSE_RESULTS_ADDED") then
            ReadBrowse(job)
        end
    elseif waiting == "search" or waiting == "moreItem" or waiting == "moreCommodity" then
        if (event == "ITEM_SEARCH_RESULTS_UPDATED" or event == "ITEM_SEARCH_RESULTS_ADDED") and SameKey(job.key, arg) then
            ReadBuyouts(job, false)
        elseif (event == "COMMODITY_SEARCH_RESULTS_UPDATED" or event == "COMMODITY_SEARCH_RESULTS_ADDED")
            and arg == job.key.itemID then
            ReadBuyouts(job, true)
        end
    end
end

local function OnUpdate(_, elapsed)
    local job = active
    job.elapsed = job.elapsed + elapsed
    if job.elapsed >= 30 then
        if not job.key then return Finish(false) end
        job.incomplete = true
        return NextKey(job)
    end
    local action, ah = job.pending, C_AuctionHouse
    if not action or not ah.IsThrottledMessageSystemReady() then return end
    if action == "search" and not ah.GetItemKeyInfo(job.key) then return end
    -- Set the expected response first: cached results can arrive during the API call.
    job.pending, job.waiting, job.elapsed = nil, action, 0
    if action == "browse" then
        ah.SendBrowseQuery(job.query)
    elseif action == "search" then
        ah.SendSearchQuery(job.key, {}, true) -- separate the player's own auctions
    elseif action == "moreBrowse" then
        if ah.HasFullBrowseResults() then ReadBrowse(job) else ah.RequestMoreBrowseResults() end
    elseif action == "moreItem" then
        if ah.RequestMoreItemSearchResults(job.key) and active == job and job.waiting == action then ReadBuyouts(job, false) end
    elseif action == "moreCommodity" then
        if ah.RequestMoreCommoditySearchResults(job.key.itemID) and active == job and job.waiting == action then ReadBuyouts(job, true) end
    end
end

-- The browse cache is shared with Blizzard and other addons. A new browse query replaces it.
local function OtherBrowse(query)
    if active and not active.key and (active.waiting or active.pending == "moreBrowse")
        and query ~= active.query then Finish(false) end
end

local function BrowseQuery(wanted)
    local query = { searchString = "", sorts = {}, filters = {}, itemClassFilters = {} }
    local classes = {}
    local getInstant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant
    for id in pairs(wanted) do
        local _, _, _, _, _, class = getInstant(id)
        if not class then return query end -- unknown class: include the whole market
        classes[class] = true
    end
    for class in pairs(classes) do
        query.itemClassFilters[#query.itemClassFilters + 1] = { classID = class }
    end
    return query
end

function Scan.Start(wanted, progress, offer, finished)
    Scan.Stop()
    if not next(wanted) then return finished(true) end
    if not frame then
        frame = CreateFrame("Frame")
        frame:SetScript("OnEvent", OnEvent)
        for _, name in ipairs({ "SendBrowseQuery", "SearchForFavorites", "SearchForItemKeys" }) do
            if C_AuctionHouse[name] then hooksecurefunc(C_AuctionHouse, name, OtherBrowse) end
        end
    end
    active = { wanted = wanted, query = BrowseQuery(wanted), keys = {}, index = 0,
        progress = progress, offer = offer, finished = finished }
    Schedule(active, "browse")
    for _, event in ipairs(events) do frame:RegisterEvent(event) end
    frame:SetScript("OnUpdate", OnUpdate)
end
