local _, ns = ...

--[[
What Easy BIS knows about the listed items besides what the game says
(Data\Items.lua): an English name to fall back on, and where each comes from.

  Items.Get(id)    { id, name, groups, flags, sources = { { kind, ..., label = letter }, ... } } or nil
  Items.Name(id)   the game's name, or the English one until the game has loaded the item
  Items.Link(id)   the game's link, or "[name]"
  Items.Find(text, limit)
                   the worn items whose name holds text (Data\Names.lua), best matches first:
                   a list of at most limit ids, and how many items match in all
]]

local Items = {}
ns.Items = Items

local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo

local lines   -- [id] = the item's line, split on first use
local cache = {}

local function Index()
    if lines then return lines end
    lines = {}
    for line in (ns.data and ns.data.items or ""):gmatch("[^\n]+") do
        local id = line:match("^(%d+)|")
        if id then lines[tonumber(id)] = line end
    end
    return lines
end

local function Split(text, separator)
    local parts = {}
    for part in (text .. separator):gmatch("(.-)%" .. separator) do
        parts[#parts + 1] = part
    end
    return parts
end

function Items.Get(id)
    if cache[id] ~= nil then return cache[id] or nil end
    local line = Index()[id]
    if not line then
        cache[id] = false
        return nil
    end
    local _, name, groups, flags, sourceText = line:match("^(%d+)|([^|]*)|([^|]*)|([^|]*)|(.*)$")
    local item = { id = id, name = name, groups = groups, flags = flags, sources = {} }
    if sourceText ~= "" then
        for _, text in ipairs(Split(sourceText, "~")) do
            local source = Split(text, "^")
            source.kind = source[1]
            source.label = source[#source]
            item.sources[#item.sources + 1] = source
        end
    end
    cache[id] = item
    return item
end

function Items.Name(id)
    local name = GetInfo and GetInfo(id)
    if name then return name end
    local item = Items.Get(id)
    if item then return item.name end
    return Items.EnglishName(id) or ("#" .. id)
end

function Items.Link(id)
    local link
    if GetInfo then
        local _
        _, link = GetInfo(id)
    end
    return link or ("[" .. Items.Name(id) .. "]")
end

-- The search by name. The data's names are in English; on a game in another language, the game's own
-- name counts too, for the items the game already has.
local names   -- { { id, required level, English name in lower case, the game's name in lower case }, ... }
local ENGLISH = { enUS = true, enGB = true }
local IsCached = C_Item and C_Item.IsItemDataCachedByID

local english   -- [id] = the English name, as written

local function Names()
    if names then return names end
    names, english = {}, {}
    for idText, level, name in (ns.data and ns.data.names or ""):gmatch("(%d+)|(%d*)|([^\n]+)") do
        local id = tonumber(idText)
        names[#names + 1] = { id, tonumber(level) or 0, name:lower(), false }
        english[id] = name
    end
    return names
end

function Items.EnglishName(id)
    Names()
    return english[id]
end

-- 0 the whole name, 1 its start, 2 the start of a word, 3 anywhere else; nil when the name lacks it.
local function Match(name, query)
    local at = name:find(query, 1, true)
    if not at then return nil end
    if at == 1 then return #name == #query and 0 or 1 end
    if name:sub(at - 1, at - 1):find("[%s%-%(']") then return 2 end
    return 3
end

function Items.Find(text, limit)
    local query = type(text) == "string" and text:match("^%s*(.-)%s*$"):lower() or ""
    if #query < 2 or query:find("^%d+$") then return {}, 0 end
    local localized = GetLocale and not ENGLISH[GetLocale() or "enUS"] and IsCached and GetInfo
    local found = {}
    for _, entry in ipairs(Names()) do
        local rank = Match(entry[3], query)
        if localized and not entry[4] and IsCached(entry[1]) then
            local name = GetInfo(entry[1])
            entry[4] = name and name:lower() or false
        end
        local other = entry[4] and Match(entry[4], query)
        if other and (not rank or other < rank) then rank = other end
        if rank then found[#found + 1] = { entry, rank } end
    end
    -- the closest matches first, then the highest required level, then the newest item
    table.sort(found, function(a, b)
        if a[2] ~= b[2] then return a[2] < b[2] end
        if a[1][2] ~= b[1][2] then return a[1][2] > b[1][2] end
        return a[1][1] > b[1][1]
    end)
    local ids = {}
    for i = 1, math.min(limit or 8, #found) do ids[i] = found[i][1][1] end
    return ids, #found
end
