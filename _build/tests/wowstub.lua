-- Stand-ins for the parts of the WoW API that Easy BIS uses, for the offline tests
-- (test_addon.py, test_ui.py). Returns a table the tests use to set the scene and
-- look at what the addon did.
--
-- Widgets (frames, font strings, textures) only answer to the methods listed in
-- METHODS: calling anything else fails, as a misspelled method would in the game.

local stub = {
    locale = "enUS",
    class = "SHAMAN",
    faction = "Alliance",
    frames = {},       -- frames made with CreateFrame
    chat = {},         -- lines sent to the chat frame
    timers = {},       -- functions waiting on C_Timer.After
    itemHooks = {},    -- functions registered for item tooltips
    itemNames = {},    -- [id] = name the game "knows"
    itemTypes = {},    -- [id] = { subtype, equip slot, class id, subclass id } for an item that is not a mail helmet
    equipLocs = {},    -- [id] = the equip slot GetItemInfoInstant gives; an id that is not here does not exist
    cursor = nil,      -- { kind, id }: what the mouse carries
    chatLink = nil,    -- the last link handed to the chat box
    spellNames = {},   -- [id] = spell name the game "knows"
    zoneNames = {},    -- [instance id] = name GetRealZoneText gives
    areaNames = {},    -- [area id] = name C_Map.GetAreaInfo gives
    modifier = false,  -- a modifier key is held
    linked = nil,      -- the last link given to HandleModifiedItemClick
    menu = nil,        -- the last context menu opened
    factions = {},     -- [faction id] = { reaction, value, low, high, name }: what the game says of a reputation
    factionList = {},  -- the reputation pane's lines: { factionID, isHeader, isCollapsed }
    itemCounts = {},   -- [id] = how many the player has, the bank included
    equipped = {},     -- [id] = true for what the player wears
    currencies = {},   -- [currency id] = the quantity the game gives; an id that is not here is no currency
    currencyIcon = nil,  -- the picture the game gives for a currency
    bindings = {},     -- [id] = the bind type GetItemInfo gives (0 none, 1 when picked up, 2 when equipped)
    itemIcons = {},    -- [id] = the icon the game gives, in place of the same one for every item
    professions = nil, -- set with stub.learn: until then the client has no GetProfessions
}

---------------------------------------------------------------------------
-- Widgets
---------------------------------------------------------------------------

local METHODS = {}
local widgetMeta = { __index = METHODS }

local function NewWidget(kind, name, template)
    local widget = setmetatable({
        kind = kind, name = name, template = template,
        shown = true, scripts = {}, events = {}, lines = {}, points = {},
    }, widgetMeta)
    if template == "ScrollFrameTemplate" or template == "UIPanelScrollFrameTemplate" then
        widget.ScrollBar = NewWidget("Slider")
    elseif template == "PortraitFrameTemplate" then
        -- As the game's template: the border and the title lie over the frame's own children.
        widget.NineSlice = NewWidget("Frame")
        widget.NineSlice.frameLevel = 500
        widget.TitleContainer = NewWidget("Frame")
        widget.TitleContainer.frameLevel = 510
        widget.TitleContainer.TitleText = NewWidget("FontString")
    elseif template == "UICheckButtonArtTemplate" then
        for _, key in ipairs({ "Normal", "Pushed", "Highlight", "Checked", "DisabledChecked" }) do
            widget[key .. "Texture"] = NewWidget("Texture")
        end
    elseif kind == "DropdownButton" then
        widget.Text = NewWidget("FontString")
        widget.Background = NewWidget("Texture")
        if template == "WowStyle1DropdownTemplate" then widget.Arrow = NewWidget("Texture") end
        widget.scripts.OnMouseDown = function(self, button)
            if button == "LeftButton" then self:OpenMenu() end
        end
    end
    return widget
end

local function Noop() end
for _, method in ipairs({
    "SetFrameStrata", "SetToplevel", "SetClampedToScreen", "SetMovable", "EnableMouse",
    "RegisterForDrag", "RegisterForClicks", "SetDontSavePosition", "StartMoving", "StopMovingOrSizing",
    "SetPortraitToAsset", "SetPortraitTextureRaw", "SetBackdrop", "SetBackdropColor",
    "SetWordWrap", "SetJustifyH", "SetColorTexture", "SetTexCoord",
    "SetHighlightTexture", "SetScrollChild", "UpdateScrollChildRect", "Raise", "SetAllPoints",
    "SetResizable", "SetResizeBounds", "StartSizing", "SetNormalTexture", "SetPushedTexture", "SetAutoFocus",
    "SetMaxLetters", "SetBlendMode", "SetDisabledTexture", "SetAtlas", "SetJustifyV",
}) do
    METHODS[method] = Noop
end

function METHODS:SetScale(scale) self.scale = scale end
function METHODS:SetBackdropBorderColor(r, g, b, a) self.borderColor = { r, g, b, a } end
function METHODS:SetVertexColor(r, g, b, a) self.vertexColor = { r, g, b, a } end
function METHODS:SetDesaturated(desaturated) self.desaturated = desaturated and true or false end
function METHODS:SetFontObject(font) self.fontObject = font end

-- Model methods (a DressUpModel): what it was asked to show.
function METHODS:SetUnit(unit) self.unit = unit end
function METHODS:Undress()
    self.undressed = (self.undressed or 0) + 1
    self.tried = {}
end
function METHODS:TryOn(link, hand)
    self.tried = self.tried or {}
    self.tried[#self.tried + 1] = { link, hand }
end
function METHODS:SetFacing(facing) self.facing = facing end

function METHODS:Show()
    if self.shown then return end
    self.shown = true
    if self.scripts.OnShow then self.scripts.OnShow(self) end
end
function METHODS:Hide()
    if not self.shown then return end
    self.shown = false
    if self.scripts.OnHide then self.scripts.OnHide(self) end
end
function METHODS:SetShown(shown) if shown then self:Show() else self:Hide() end end
function METHODS:IsShown() return self.shown end

function METHODS:SetSize(width, height) self.width, self.height = width, height end
function METHODS:SetWidth(width) self.width = width end
function METHODS:SetVerticalScroll(offset) self.verticalScroll = offset end
function METHODS:SetHeight(height) self.height = height end
function METHODS:GetWidth() return self.width or 0 end
function METHODS:GetHeight() return self.height or 0 end
function METHODS:SetPoint(...) self.points[#self.points + 1] = { ... } end
function METHODS:ClearAllPoints() self.points = {} end
function METHODS:GetPoint(index)
    local point = self.points[index or 1]
    if point then return point[1], point[2], point[3], point[4], point[5] end
end
function METHODS:GetCenter() return 0, 0 end
function METHODS:GetRight() return self.right end   -- nil until a test places the frame
function METHODS:GetBottom() return self.bottom end
function METHODS:SetFocus() self.focused = true end
function METHODS:ClearFocus() self.focused = false end
function METHODS:HasFocus() return self.focused == true end
function METHODS:GetEffectiveScale() return 1 end
function METHODS:SetFrameLevel(level) self.frameLevel = level end
function METHODS:GetFrameLevel() return self.frameLevel or 1 end
function METHODS:IsMouseOver() return false end
function METHODS:IsForbidden() return false end
function METHODS:SetAlpha(alpha) self.alpha = alpha end
function METHODS:SetEnabled(enabled) self.enabled = enabled end
function METHODS:IsEnabled() return self.enabled ~= false end
function METHODS:LockHighlight() self.highlightLocked = true end
function METHODS:UnlockHighlight() self.highlightLocked = false end
for _, key in ipairs({ "Normal", "Pushed", "Highlight", "Checked", "DisabledChecked" }) do
    local field = key .. "Texture"
    METHODS["Get" .. field] = function(self) return self[field] end
end

function METHODS:SetScript(name, handler) self.scripts[name] = handler end
function METHODS:GetScript(name) return self.scripts[name] end
function METHODS:HookScript(name, handler)
    local previous = self.scripts[name]
    self.scripts[name] = previous and function(...) previous(...); handler(...) end or handler
end
function METHODS:RegisterEvent(event) self.events[event] = true end
function METHODS:UnregisterEvent(event) self.events[event] = nil end
function METHODS:UnregisterAllEvents() self.events = {} end

function METHODS:CreateFontString(_, _, fontObject)
    local text = NewWidget("FontString")
    text.fontObject = fontObject   -- the font object's name, which the tests read
    return text
end
function METHODS:CreateTexture() return NewWidget("Texture") end
function METHODS:GetFontString()
    if not self.fontString then
        self.fontString = NewWidget("FontString")
        self.fontString:SetText(self.text)
    end
    return self.fontString
end
function METHODS:SetText(text)
    self.text = text
    if self.kind == "DropdownButton" then self.Text:SetText(text) end
    if self.fontString then self.fontString:SetText(text) end
end
function METHODS:GetText() return self.text end
function METHODS:SetTitle(text) self.title = text end
function METHODS:SetTextColor(r, g, b) self.color = { r, g, b } end
function METHODS:GetStringWidth() return #(self.text or "") * 6 end
function METHODS:GetStringHeight() return 14 end
function METHODS:SetTexture(texture) self.texture = texture end
function METHODS:SetChecked(checked) self.checked = checked and true or false end
function METHODS:GetChecked() return self.checked end

-- Font objects (CreateFont and the game's own)
function METHODS:SetFont(file, size, flags) self.fontFile, self.fontSize, self.fontFlags = file, size, flags end
function METHODS:GetFont() return self.fontFile, self.fontSize, self.fontFlags end
function METHODS:CopyFontObject(other)
    if type(other) == "string" then other = _G[other] end
    self.fontFile, self.fontSize, self.fontFlags = other:GetFont()
end

-- Tooltip methods (GameTooltip and the tooltips stub.showItem makes)
function METHODS:SetOwner(owner, anchor)
    self.owner, self.anchor, self.lines, self.item, self.spell = owner, anchor, {}, nil, nil
end
function METHODS:SetItemByID(id)
    self.item = id
    self.lines[#self.lines + 1] = { stub.itemNames[id] or ("item " .. id) }
end
function METHODS:SetSpellByID(id)
    self.spell = id
    self.lines[#self.lines + 1] = { stub.spellNames[id] or ("spell " .. id) }
end
function METHODS:AddLine(text) self.lines[#self.lines + 1] = { text } end
function METHODS:AddDoubleLine(left, right) self.lines[#self.lines + 1] = { left, right } end
function METHODS:NumLines() return #self.lines end
function METHODS:IsOwned(owner) return self.owner == owner end
function METHODS:GetOwner() return self.owner end

function CreateFrame(kind, name, _, template)
    local frame = NewWidget(kind, name, template)
    if kind == "DropdownButton" then
        frame.SetupMenu = stub.setupMenu
        frame.OpenMenu = stub.openMenu
        if template == "WowStyle1DropdownTemplate" then frame.OverrideText = METHODS.SetText end
    end
    stub.frames[#stub.frames + 1] = frame
    if name then _G[name] = frame end
    return frame
end

UIParent = NewWidget("Frame", "UIParent")
Minimap = NewWidget("Frame", "Minimap")
Minimap.width, Minimap.height = 140, 140
GameTooltip = NewWidget("GameTooltip", "GameTooltip")
GameTooltip.shown = false
-- The comparison with the gear worn: the game sets it as soon as an item's tooltip is shown (its
-- option "always compare items" on), and again for GameTooltip_ShowCompareItem.
ShoppingTooltip1 = NewWidget("GameTooltip", "ShoppingTooltip1")
ShoppingTooltip2 = NewWidget("GameTooltip", "ShoppingTooltip2")
ShoppingTooltip1.shown, ShoppingTooltip2.shown = false, false
local function Compare(tooltip)
    if tooltip.item then
        for _, tip in ipairs({ ShoppingTooltip1, ShoppingTooltip2 }) do
            tip:SetOwner(tooltip, "ANCHOR_NONE")
            tip:Show()
        end
    end
end
GameTooltip.scripts.OnShow = Compare
function GameTooltip_ShowCompareItem(tooltip) Compare(tooltip) end
UISpecialFrames = {}

function CreateFont(name)
    local font = NewWidget("Font", name)
    if name then _G[name] = font end
    return font
end
-- The game's fonts the addon builds on, at their sizes in the game.
for name, size in pairs({ GameFontNormal = 12, GameFontNormalLarge = 16, GameFontHighlightSmall = 10 }) do
    CreateFont(name):SetFont("Fonts\\FRIZQT__.TTF", size, "")
end

---------------------------------------------------------------------------
-- The rest of the API
---------------------------------------------------------------------------

function GetLocale() return stub.locale end
function UnitClass() return stub.class, stub.class end
function UnitFactionGroup() return stub.faction end

DEFAULT_CHAT_FRAME = {}
function DEFAULT_CHAT_FRAME:AddMessage(text) stub.chat[#stub.chat + 1] = text end

SlashCmdList = {}

RAID_CLASS_COLORS = {
    WARRIOR = { r = 0.78, g = 0.61, b = 0.43 }, PALADIN = { r = 0.96, g = 0.55, b = 0.73 },
    HUNTER = { r = 0.67, g = 0.83, b = 0.45 }, ROGUE = { r = 1.00, g = 0.96, b = 0.41 },
    PRIEST = { r = 1.00, g = 1.00, b = 1.00 }, SHAMAN = { r = 0.00, g = 0.44, b = 0.87 },
    MAGE = { r = 0.25, g = 0.78, b = 0.92 }, WARLOCK = { r = 0.53, g = 0.53, b = 0.93 },
    DRUID = { r = 1.00, g = 0.49, b = 0.04 },
}
ITEM_QUALITY_COLORS = {
    [2] = { r = 0.12, g = 1.00, b = 0.00, hex = "|cff1eff00" },
    [3] = { r = 0.00, g = 0.44, b = 0.87, hex = "|cff0070dd" },
    [4] = { r = 0.64, g = 0.21, b = 0.93, hex = "|cffa335ee" },
}

C_Timer = {}
function C_Timer.After(_, callback) stub.timers[#stub.timers + 1] = callback end

Enum = { TooltipDataType = { Item = 0 } }
TooltipDataProcessor = {}
function TooltipDataProcessor.AddTooltipPostCall(_, callback) stub.itemHooks[#stub.itemHooks + 1] = callback end

function CreateAtlasMarkup(atlas) return "<" .. atlas .. ">" end

-- name, link, quality, item level, required level, type, subtype, stack, equip slot, icon, price, class id,
-- subclass id, bind type. By name: only an item the game "knows".
function GetItemInfo(id)
    if type(id) == "string" then
        local wanted = id
        id = nil
        for known, name in pairs(stub.itemNames) do
            if name == wanted then id = known end
        end
    end
    local name = stub.itemNames[id]
    if name then
        local kind = stub.itemTypes[id] or { "Mail", "INVTYPE_HEAD" }
        return name, "|Hitem:" .. id .. "|h[" .. name .. "]|h", 4, 60, 60, "Armor", kind[1], 1, kind[2],
            stub.itemIcons[id] or 132767, 0,
            kind[3] or 4, kind[4] or 3, stub.bindings[id]
    end
end
-- id, type, subtype, equip slot, icon, class id, subclass id: at once, for any item that exists
function GetItemInfoInstant(id)
    local equipLoc = stub.equipLocs[id]
    local kind = stub.itemTypes[id] or {}
    if equipLoc then return id, "Armor", kind[1] or "Mail", equipLoc, 132767, kind[3] or 4, kind[4] or 3 end
end
INVTYPE_HEAD, INVTYPE_2HWEAPON, INVTYPE_WEAPON, INVTYPE_HOLDABLE = "Head", "Two-Hand", "One-Hand", "Held In Off-hand"
function GetItemIcon(id) return stub.itemIcons[id] or 134400 end
function GetItemCount(id) return stub.itemCounts[id] or 0 end
function IsEquippedItem(id) return stub.equipped[id] == true end
C_CurrencyInfo = {}
function C_CurrencyInfo.GetCurrencyInfo(id)
    local quantity = stub.currencies[id]
    return quantity and { quantity = quantity, iconFileID = stub.currencyIcon } or nil
end

function GetCursorInfo()
    if stub.cursor then return stub.cursor[1], stub.cursor[2] end
end
function ClearCursor() stub.cursor = nil end

-- A Shift-click on an item hands its link to the chat box.
function ChatEdit_InsertLink(link)
    stub.chatLink = link
    return false
end

-- Runs `hook` after a global function, or after a function of a table.
function hooksecurefunc(owner, name, hook)
    if type(owner) == "string" then owner, name, hook = _G, owner, name end
    local original = owner[name]
    owner[name] = function(...)
        local result = original(...)
        hook(...)
        return result
    end
end

C_Spell = {}
function C_Spell.GetSpellName(id) return stub.spellNames[id] end
function C_Spell.GetSpellTexture() return 136243 end

-- A faction the test did not set reads as the game reads one never met: Neutral 0.
C_Reputation = {}
function C_Reputation.GetFactionDataByID(id)
    if stub.factionsUnknown then return nil end
    local faction = stub.factions[id] or { reaction = 4, value = 0, low = 0, high = 3000 }
    return {
        factionID = id, name = faction.name or ("Faction " .. id), reaction = faction.reaction,
        currentStanding = faction.value, currentReactionThreshold = faction.low,
        nextReactionThreshold = faction.high,
    }
end
function C_Reputation.GetNumFactions() return #stub.factionList end
function C_Reputation.GetFactionDataByIndex(index) return stub.factionList[index] end
-- stub.watched: the faction the reputation bar follows
function C_Reputation.GetWatchedFactionData() return stub.watched and { factionID = stub.watched } or nil end
function C_Reputation.SetWatchedFactionByID(id) stub.watched = id ~= 0 and id or nil end

-- stub.waypoint: the pin last set on the map; stub.openedMap: the map last opened
C_Map = {}
function C_Map.GetMapInfo(id) return { name = "Map " .. id } end
function C_Map.SetUserWaypoint(point) stub.waypoint = point end
function C_Map.GetAreaInfo(id) return stub.areaNames[id] end
UiMapPoint = {}
function UiMapPoint.CreateFromCoordinates(map, x, y) return { uiMapID = map, x = x, y = y } end
function OpenWorldMap(map) stub.openedMap = map end
function GetRealZoneText(id) return stub.zoneNames[id] end

-- 2026-11-18 11:00 UTC, the third week of the first PvP season, six days before the next weekly reset
stub.serverTime, stub.untilReset = 1795000000, 6 * 24 * 60 * 60
function GetServerTime() return stub.serverTime end
C_DateAndTime = {}
function C_DateAndTime.GetSecondsUntilWeeklyReset() return stub.untilReset end

local TEMPLATES = {
    PortraitFrameTemplate = true, InsetFrameTemplate = true, ScrollFrameTemplate = true,
    MinimalCheckboxTemplate = true,
}
C_XMLUtil = {}
function C_XMLUtil.GetTemplateInfo(name) return TEMPLATES[name] and {} or nil end

SOUNDKIT = setmetatable({}, { __index = function() return 1 end })
function PlaySound() end
function IsModifierKeyDown() return stub.modifier end
function IsShiftKeyDown() return stub.shift == true end
function HandleModifiedItemClick(link) stub.linked = link end
function GetCursorPosition() return stub.cursorX or 0, 0 end
function IsMouseButtonDown() return stub.mouseDown ~= false end
-- left, right, top, bottom of each class in the picture that holds them all
CLASS_ICON_TCOORDS = {}
for index, class in ipairs({ "WARRIOR", "MAGE", "ROGUE", "DRUID", "HUNTER", "SHAMAN", "PRIEST", "WARLOCK", "PALADIN" }) do
    local column, line = (index - 1) % 4, math.floor((index - 1) / 4)
    CLASS_ICON_TCOORDS[class] = { column * 0.25, column * 0.25 + 0.25, line * 0.25, line * 0.25 + 0.25 }
end
math.atan2 = math.atan2 or function(y, x) return math.atan(y, x) end   -- the game's Lua 5.1 has it

-- Context menus: the generator fills a tree the tests can read and click.
--   item = { kind = "title"|"button"|"radio"|"checkbox"|"divider", text, items (a button's submenu),
--            selected(), pick() }
local function NewMenu()
    local menu = { items = {} }
    local function Add(item)
        menu.items[#menu.items + 1] = item
        return item
    end
    function menu:SetScrollMode() end
    function menu:CreateTitle(text) return Add({ kind = "title", text = text }) end
    function menu:CreateDivider() return Add({ kind = "divider" }) end
    function menu:CreateButton(text, callback)
        local submenu = NewMenu()
        submenu.kind, submenu.text, submenu.pick = "button", text, callback
        return Add(submenu)
    end
    function menu:CreateRadio(text, selected, pick)
        return Add({ kind = "radio", text = text, selected = selected, pick = pick })
    end
    function menu:CreateCheckbox(text, selected, pick)
        return Add({ kind = "checkbox", text = text, selected = selected, pick = pick })
    end
    return menu
end

MenuResponse = { Close = 1, Refresh = 2 }
MenuUtil = {}
function MenuUtil.CreateContextMenu(owner, generator)
    local root = NewMenu()
    root.owner = owner
    generator(owner, root)
    stub.menu = root
    return root
end

function stub.setupMenu(button, generator)
    button.menuGenerator = generator
    if button:IsShown() then generator(button, NewMenu()) end
end

function stub.openMenu(button)
    if button.menuGenerator then return MenuUtil.CreateContextMenu(button, button.menuGenerator) end
end

---------------------------------------------------------------------------
-- What the tests drive
---------------------------------------------------------------------------

-- Sends a game event to every frame that registered for it.
function stub.fire(event, ...)
    for _, frame in ipairs(stub.frames) do
        if frame.events[event] and frame.scripts.OnEvent then frame.scripts.OnEvent(frame, event, ...) end
    end
end

-- Runs the timers that are due; returns how many ran.
function stub.runTimers()
    local due = stub.timers
    stub.timers = {}
    for _, callback in ipairs(due) do callback() end
    return #due
end

-- A tooltip that records what is added to it: lines[i] = { left, right }.
-- The player's professions, { { name, rank, skill line }, ... } in the game's order: the client then answers
-- GetProfessions and GetProfessionInfo, as the Forever client does.
function stub.learn(professions)
    stub.professions = professions
    local function At(index) return professions[index] and index or nil end
    function GetProfessions() return At(1), At(2), At(3), At(4), At(5), At(6) end
    function GetProfessionInfo(index)
        local profession = professions[index]
        if not profession then error("no profession at " .. tostring(index)) end
        return profession[1], 136240, profession[2], 300, 0, 0, profession[3]
    end
end

function stub.newTooltip()
    return NewWidget("GameTooltip")
end

-- Shows an item in a tooltip the way the game does, through the registered hooks.
function stub.showItem(id)
    local tooltip = stub.newTooltip()
    for _, hook in ipairs(stub.itemHooks) do hook(tooltip, { id = id }) end
    return tooltip
end

-- Runs a widget's script, as a click or the mouse would.
function stub.run(widget, script, ...)
    if (script == "OnClick" or script == "OnMouseDown") and not widget:IsEnabled() then return end
    local handler = widget.scripts[script]
    assert(handler, "the widget has no " .. script .. " script")
    return handler(widget, ...)
end

function stub.update()
    for _, frame in ipairs(stub.frames) do
        if frame:IsShown() and frame.scripts.OnUpdate then frame.scripts.OnUpdate(frame, 0.016) end
    end
end

function stub.menuPanel(level)
    for _, frame in ipairs(stub.frames) do
        if frame:IsShown() and frame.entries and frame.level == level then return frame end
    end
end

function stub.openFilter(button)
    local panel = stub.menuPanel(1)
    local script = button.kind == "DropdownButton" and "OnMouseDown" or "OnClick"
    if panel and panel.anchor == button then stub.run(button, script, "LeftButton") end
    stub.run(button, script, "LeftButton")
    panel = stub.menuPanel(1)
    stub.menu = panel and { items = panel.entries, panel = panel } or nil
end

function stub.clearChat() stub.chat = {} end

return stub
