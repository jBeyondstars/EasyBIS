local _, ns = ...

--[[
What Easy BIS knows about the listed items besides what the game says
(Data\Items.lua): an English name to fall back on, and where each comes from.

  Items.Get(id)    { id, name, groups, flags, sources = { { kind, ..., label = letter }, ... } } or nil
  Items.Name(id)   the game's name, or the English one until the game has loaded the item
  Items.Link(id)   the game's link, or "[name]"
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
    return item and item.name or ("#" .. id)
end

function Items.Link(id)
    local link
    if GetInfo then
        local _
        _, link = GetInfo(id)
    end
    return link or ("[" .. Items.Name(id) .. "]")
end
