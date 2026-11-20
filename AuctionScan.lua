local _, ns = ...

-- One search per wanted item, by its ID with no level and no suffix: the game answers with every variant
-- on sale, as it does for a piece put up for sale. The house is not browsed. A price is published only
-- from the buyouts read, and never from the player's own auctions.
--
--   Scan.Start(ids, progress, offer, finished)   ids: the items, in the order they are searched
--       progress(index, total)    the item being searched
--       offer(key, price, link)   its lowest buyout, and the key of the variant sold at that price
--       finished(complete)        false: stopped, or an item got no answer
--   Scan.Stop()
local Scan = {}
ns.AuctionScan = Scan

local ANSWER_WAIT = 10   -- seconds left to the game to know an item, then to answer its search
local SEND_WAIT = 90     -- and to let a search through: it allows a hundred of them a minute

local active, frame
local events = {
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
    local lowest, link, variant
    for i = 1, count(arg) do
        local row = get(arg, i)
        if row then
            local price = commodity and row.unitPrice or row.buyoutAmount
            local available = not row.containsOwnerItem and not row.containsAccountItem
            if commodity and row.numOwnerItems and not row.containsAccountItem then
                available = row.quantity > row.numOwnerItems
            end
            if available and row.quantity > 0 and price and price > 0 and (not lowest or price < lowest) then
                lowest, link, variant = price, row.itemLink, row.itemKey
            end
        end
    end
    if lowest then
        variant = variant or key
        ah.GetItemKeyInfo(variant)   -- starts loading what opening this variant's auctions needs
        job.offer(variant, lowest, link)
    end
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
    if not job.waiting then return end
    if (event == "ITEM_SEARCH_RESULTS_UPDATED" or event == "ITEM_SEARCH_RESULTS_ADDED") and SameKey(job.key, arg) then
        ReadBuyouts(job, false)
    elseif (event == "COMMODITY_SEARCH_RESULTS_UPDATED" or event == "COMMODITY_SEARCH_RESULTS_ADDED")
        and arg == job.key.itemID then
        ReadBuyouts(job, true)
    end
end

local function OnUpdate(_, elapsed)
    local job = active
    job.elapsed = job.elapsed + elapsed
    local action, ah = job.pending, C_AuctionHouse
    -- A search waits for the game to know its item: until then the game often ignores it.
    local known = action and ah.GetItemKeyInfo(job.key)
    if job.elapsed >= (known and SEND_WAIT or ANSWER_WAIT) then
        job.incomplete = true
        return NextKey(job)
    end
    if not known or not ah.IsThrottledMessageSystemReady() then return end
    -- Set the expected response first: cached results can arrive during the API call.
    job.pending, job.waiting, job.elapsed = nil, action, 0
    if action == "search" then
        -- the last argument sets the player's own auctions apart
        if known.isCommodity then ah.SendSearchQuery(job.key, {}, true) else ah.SendSellSearchQuery(job.key, {}, true) end
    elseif action == "moreItem" then
        if ah.RequestMoreItemSearchResults(job.key) and active == job and job.waiting == action then ReadBuyouts(job, false) end
    elseif action == "moreCommodity" then
        if ah.RequestMoreCommoditySearchResults(job.key.itemID) and active == job and job.waiting == action then ReadBuyouts(job, true) end
    end
end

function Scan.Start(ids, progress, offer, finished)
    Scan.Stop()
    if not ids[1] then return finished(true) end
    if not frame then
        frame = CreateFrame("Frame")
        frame:SetScript("OnEvent", OnEvent)
    end
    local keys = {}
    for index, id in ipairs(ids) do
        keys[index] = { itemID = id, itemLevel = 0, itemSuffix = 0, battlePetSpeciesID = 0 }
        C_AuctionHouse.GetItemKeyInfo(keys[index])   -- starts loading them all at once
    end
    active = { keys = keys, index = 0, progress = progress, offer = offer, finished = finished }
    for _, event in ipairs(events) do frame:RegisterEvent(event) end
    frame:SetScript("OnUpdate", OnUpdate)
    NextKey(active)
end
