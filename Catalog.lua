local _, ns = ...

--[[
Fixed lists: the classes, the slots and the two gear lists, in display order,
with their names, colors and icons, and the names of the content phases.
]]

-- The addon's own pictures, made from its logo by _build/art/make_textures.py.
ns.ICON = "Interface\\AddOns\\EasyBIS\\Media\\Icon.tga"          -- the minimap button
ns.PORTRAIT = "Interface\\AddOns\\EasyBIS\\Media\\Portrait.tga"  -- the window's portrait

ns.CLASSES = { "WARRIOR", "PALADIN", "HUNTER", "ROGUE", "PRIEST", "SHAMAN", "MAGE", "WARLOCK", "DRUID" }

-- Rings and trinkets fill two slots from one list.
ns.SLOTS = {
    "head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet",
    "finger", "trinket", "main", "off", "ranged",
}
ns.PAIRED = { finger = true, trinket = true }

ns.LISTS = { "pve", "pvp" }

-- Picks shown after the best pick of a slot (the second ring or trinket among them), until the player asks
-- for more (ns.Alternatives, Core.lua).
ns.ALTERNATIVES = 2

local CLASS_NAMES = {
    WARRIOR = "Warrior", PALADIN = "Paladin", HUNTER = "Hunter", ROGUE = "Rogue", PRIEST = "Priest",
    SHAMAN = "Shaman", MAGE = "Mage", WARLOCK = "Warlock", DRUID = "Druid",
}

function ns.ClassName(token)
    return (LOCALIZED_CLASS_NAMES_MALE and LOCALIZED_CLASS_NAMES_MALE[token]) or CLASS_NAMES[token] or token
end

function ns.ClassColor(token)
    local color = (C_ClassColor and C_ClassColor.GetClassColor and C_ClassColor.GetClassColor(token))
        or (RAID_CLASS_COLORS and RAID_CLASS_COLORS[token])
    if color then return color.r, color.g, color.b end
    return 1, 1, 1
end

-- An item quality's color: r, g, b and "|cffrrggbb". White for a quality the game has not told yet.
function ns.QualityColor(quality)
    local color = quality and ITEM_QUALITY_COLORS and ITEM_QUALITY_COLORS[quality]
    if not color then return 1, 1, 1, "|cffffffff" end
    local hex = color.hex
        or ("|cff%02x%02x%02x"):format(math.floor(color.r * 255), math.floor(color.g * 255), math.floor(color.b * 255))
    return color.r, color.g, color.b, hex
end

-- The class icon as text, to put in front of a name.
function ns.ClassIcon(token, size)
    size = size or 14
    if CreateAtlasMarkup then
        return CreateAtlasMarkup("classicon-" .. token:lower(), size, size)
    end
    local coords = CLASS_ICON_TCOORDS and CLASS_ICON_TCOORDS[token]
    if not coords then return "" end
    return ("|TInterface\\GLUES\\CHARACTERCREATE\\UI-CharacterCreate-Classes:%d:%d:0:0:256:256:%d:%d:%d:%d|t"):format(
        size, size, coords[1] * 256, coords[2] * 256, coords[3] * 256, coords[4] * 256)
end

function ns.SlotName(slot)
    return ns.L["SLOT_" .. slot]
end

-- 0 "Pre-raid", 9 "Everything", the others "Phase 1"...
function ns.PhaseName(phase)
    if phase == 0 then return ns.L.PHASE_PRERAID end
    if phase == 9 then return ns.L.PHASE_ALL end
    return ns.L.PHASE_N:format(phase)
end

function ns.ListName(list)
    if list == "weave" then return ns.L.LIST_WEAVE end
    return list == "pvp" and ns.L.LIST_PVP or ns.L.LIST_PVE
end

function ns.ListLongName(list)
    local level = ns.data and ns.data.meta and ns.data.meta.level or 60
    return (list == "pvp" and ns.L.LIST_PVP_LONG or ns.L.LIST_PVE_LONG):format(level)
end
