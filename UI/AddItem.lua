local _, ns = ...
local L = ns.L
local Widgets = ns.Widgets

--[[
The small dialog that adds an item by hand to the list the window shows
(Custom.lua).

Type an item ID, or a name the game already knows; paste a link; Shift-click
an item (bags, chat, another addon's list) while the box has the focus; or
drop an item on the dialog. The dialog stays open, so several items can be
added in a row, and the line under the box says what happened.

From the second letter typed, a list under the box suggests the worn items
whose name holds the text (Items.Find). Up and Down (or Tab) pick one, Enter
or a click adds it, Escape closes the list.

  AddItem.Open(shown)     shown: the window's state { class, spec, list, slot }, read at each add
  AddItem.Close()
  AddItem.Refresh()       the name of the list it adds to follows the window
  AddItem.Submit(text)    ok, the sentence shown
  AddItem.Suggest(text)   fills the list under the box; returns the ids it shows
  AddItem.dialog          (the tests read it)
]]

local AddItem = {}
ns.AddItem = AddItem

local DIALOG_NAME = "EasyBISAddItem"
local WIDTH, HEIGHT = 400, 136

local dialog
local shown   -- the window's state

local function Say(ok, message)
    dialog.result:SetText(message or "")
    if ok then
        dialog.result:SetTextColor(0.20, 0.82, 0.48)
    else
        dialog.result:SetTextColor(1.00, 0.45, 0.40)
    end
end

---------------------------------------------------------------------------
-- The suggestions under the box
---------------------------------------------------------------------------

local SUGGESTIONS = 8
local ROW_HEIGHT = 20
local GetInfo = (C_Item and C_Item.GetItemInfo) or GetItemInfo
local GetInstant = (C_Item and C_Item.GetItemInfoInstant) or GetItemInfoInstant

local function HideSuggestions()
    if dialog and dialog.suggest then
        dialog.suggest:Hide()
        dialog.suggest.ids = {}
        dialog.suggest.selected = nil
    end
end

local function Select(index)
    local suggest = dialog.suggest
    suggest.selected = index
    for i, row in ipairs(suggest.rows) do row.selected:SetShown(i == index) end
end

-- The name in the item's quality color once the game has the item, and the slot it goes in.
local function FillRow(row, id)
    row.id = id
    -- the quality, not the link's color: newer links write it as |cnIQ4: rather than |cffa335ee
    local name, _, quality = nil, nil, nil
    if GetInfo then name, _, quality = GetInfo(id) end
    if not quality and C_Item and C_Item.GetItemQualityByID then quality = C_Item.GetItemQualityByID(id) end
    local _, _, _, hex = ns.QualityColor(quality)
    row.name:SetText(hex .. (name or ns.Items.Name(id)) .. "|r")
    local _, _, _, equipLoc, icon
    if GetInstant then _, _, _, equipLoc, icon = GetInstant(id) end
    row.icon:SetTexture(icon or 134400)
    row.slot:SetText(equipLoc and _G[equipLoc] or "")
    row:Show()
end

-- Fills the list for the box's text; hides it when nothing matches.
function AddItem.Suggest(text)
    if not dialog then return {} end
    local suggest = dialog.suggest
    local ids, total = ns.Items.Find(text, SUGGESTIONS)
    suggest.ids = ids
    if #ids == 0 then
        HideSuggestions()
        return ids
    end
    for i, row in ipairs(suggest.rows) do
        if ids[i] then FillRow(row, ids[i]) else row:Hide() end
    end
    local more = total - #ids
    suggest.more:SetText(more > 0 and L.ADD_MORE:format(more) or "")
    suggest.more:SetShown(more > 0)
    suggest:SetHeight(#ids * ROW_HEIGHT + (more > 0 and 16 or 0) + 8)
    suggest:Show()
    Select(1)
    return ids
end

-- Moves the choice down (step 1) or up (step -1), round the list.
local function Move(step)
    local suggest = dialog.suggest
    local count = #suggest.ids
    if not suggest:IsShown() or count == 0 then return end
    Select(((suggest.selected or 0) - 1 + step) % count + 1)
end

function AddItem.Submit(text)
    if not dialog or not shown then return false end
    HideSuggestions()
    -- a one-handed weapon goes to the off hand when the window is filtered on that slot
    local ok, message = ns.Custom.Submit(shown.class, shown.spec, shown.list, text, shown.slot)
    Say(ok, message)
    if ok then dialog.box:SetText("") end
    return ok, message
end

-- Enter: the suggestion chosen, or else the text as typed.
local function Enter()
    local suggest = dialog.suggest
    local id = suggest:IsShown() and suggest.selected and suggest.ids[suggest.selected]
    return AddItem.Submit(id and tostring(id) or dialog.box:GetText())
end

local function BuildSuggestions(box)
    local suggest = CreateFrame("Frame", nil, dialog, "BackdropTemplate")
    dialog.suggest = suggest
    suggest:Hide()
    suggest.ids = {}
    suggest:SetPoint("TOPLEFT", box, "BOTTOMLEFT", -6, -2)
    suggest:SetWidth(WIDTH - 28)
    suggest:SetFrameStrata("FULLSCREEN_DIALOG")
    suggest:SetClampedToScreen(true)
    suggest:EnableMouse(true)
    suggest:SetBackdrop(Widgets.FLAT)
    suggest:SetBackdropColor(0.07, 0.07, 0.09, 0.98)
    suggest:SetBackdropBorderColor(1, 1, 1, 0.30)

    suggest.rows = {}
    for i = 1, SUGGESTIONS do
        local row = CreateFrame("Button", nil, suggest)
        row:SetHeight(ROW_HEIGHT)
        row:SetPoint("TOPLEFT", 4, -4 - (i - 1) * ROW_HEIGHT)
        row:SetPoint("RIGHT", suggest, "RIGHT", -4, 0)

        row.selected = row:CreateTexture(nil, "BACKGROUND")
        row.selected:SetAllPoints()
        row.selected:SetColorTexture(1, 1, 1, 0.12)
        row.selected:Hide()

        row.icon = row:CreateTexture(nil, "ARTWORK")
        row.icon:SetSize(16, 16)
        row.icon:SetPoint("LEFT", 2, 0)

        row.slot = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        row.slot:SetPoint("RIGHT", -4, 0)
        row.slot:SetTextColor(Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3])

        row.name = row:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
        row.name:SetPoint("LEFT", row.icon, "RIGHT", 6, 0)
        row.name:SetPoint("RIGHT", row.slot, "LEFT", -6, 0)
        row.name:SetJustifyH("LEFT")
        row.name:SetWordWrap(false)

        row:SetScript("OnEnter", function(self)
            Select(i)
            GameTooltip:SetOwner(suggest, "ANCHOR_NONE")
            GameTooltip:ClearAllPoints()
            GameTooltip:SetPoint("TOPLEFT", suggest, "TOPRIGHT", 4, 0)
            GameTooltip:SetItemByID(self.id)
            ns.Browser.ShowTooltip(suggest)   -- the comparison with the gear worn waits for Shift
        end)
        row:SetScript("OnLeave", function() GameTooltip:Hide() end)
        row:SetScript("OnClick", function(self)
            Widgets.Click()
            GameTooltip:Hide()
            AddItem.Submit(tostring(self.id))
            box:SetFocus()
        end)
        suggest.rows[i] = row
    end

    suggest.more = suggest:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    suggest.more:SetPoint("BOTTOMLEFT", 10, 5)
    suggest.more:SetTextColor(Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3])

    -- names and colors arrive from the server after the first look
    suggest:SetScript("OnShow", function(self) self:RegisterEvent("GET_ITEM_INFO_RECEIVED") end)
    suggest:SetScript("OnHide", function(self) self:UnregisterEvent("GET_ITEM_INFO_RECEIVED") end)
    suggest:SetScript("OnEvent", function(self)
        for i, row in ipairs(self.rows) do
            if self.ids[i] then FillRow(row, self.ids[i]) end
        end
    end)
end

-- An item dropped on the dialog, or carried onto it by a click.
local function Drop()
    if not GetCursorInfo then return end
    local kind, id = GetCursorInfo()
    if kind ~= "item" or not id then return end
    if ClearCursor then ClearCursor() end
    AddItem.Submit(tostring(id))
end

-- The game hands a Shift-clicked item's link to the chat box; while this box has the focus, it is
-- meant for it.
local function OnLink(link)
    if dialog and dialog:IsShown() and dialog.box:HasFocus() and type(link) == "string" then
        AddItem.Submit(link)
    end
end

local function Build()
    dialog = CreateFrame("Frame", DIALOG_NAME, UIParent, "BackdropTemplate")
    AddItem.dialog = dialog
    dialog:Hide()
    dialog:SetSize(WIDTH, HEIGHT)
    dialog:SetFrameStrata("DIALOG")
    dialog:SetToplevel(true)
    dialog:SetClampedToScreen(true)
    dialog:EnableMouse(true)
    dialog:SetBackdrop(Widgets.FLAT)
    dialog:SetBackdropColor(0.05, 0.05, 0.06, 0.97)
    dialog:SetBackdropBorderColor(1, 1, 1, 0.35)
    table.insert(UISpecialFrames, DIALOG_NAME)

    dialog.title = dialog:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    dialog.title:SetPoint("TOPLEFT", 14, -12)
    dialog.title:SetText(L.ADD_BUTTON)

    dialog.target = dialog:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dialog.target:SetPoint("TOPLEFT", dialog.title, "BOTTOMLEFT", 0, -4)

    dialog.hint = dialog:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dialog.hint:SetPoint("TOPLEFT", dialog.target, "BOTTOMLEFT", 0, -6)
    dialog.hint:SetWidth(WIDTH - 28)
    dialog.hint:SetJustifyH("LEFT")
    dialog.hint:SetTextColor(Widgets.MUTED[1], Widgets.MUTED[2], Widgets.MUTED[3])
    dialog.hint:SetText(L.ADD_HINT)

    local close = CreateFrame("Button", nil, dialog, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", 2, 2)

    local box = CreateFrame("EditBox", nil, dialog, "InputBoxTemplate")
    dialog.box = box
    box:SetSize(266, 22)
    box:SetPoint("BOTTOMLEFT", 20, 32)
    box:SetAutoFocus(false)
    box:SetMaxLetters(300)
    box:SetScript("OnEnterPressed", Enter)
    box:SetScript("OnEscapePressed", function()
        if dialog.suggest:IsShown() then HideSuggestions() else dialog:Hide() end
    end)
    box:SetScript("OnReceiveDrag", Drop)
    -- only what the player types: the box emptied after an add, or a pasted link, asks for nothing
    box:SetScript("OnTextChanged", function(self, typed)
        if typed then AddItem.Suggest(self:GetText()) else HideSuggestions() end
    end)
    box:SetScript("OnArrowPressed", function(_, key)
        if key == "DOWN" then Move(1) elseif key == "UP" then Move(-1) end
    end)
    box:SetScript("OnTabPressed", function()
        Move(IsShiftKeyDown and IsShiftKeyDown() and -1 or 1)
    end)
    BuildSuggestions(box)

    dialog.add = Widgets.Button(dialog, L.ADD_CONFIRM, 90)
    dialog.add:SetPoint("LEFT", box, "RIGHT", 10, 0)
    dialog.add:SetScript("OnClick", function()
        Widgets.Click()
        AddItem.Submit(box:GetText())
    end)

    dialog.result = dialog:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dialog.result:SetPoint("BOTTOMLEFT", 14, 10)
    dialog.result:SetPoint("RIGHT", -14, 0)
    dialog.result:SetJustifyH("LEFT")
    dialog.result:SetWordWrap(false)

    dialog:SetScript("OnReceiveDrag", Drop)
    dialog:SetScript("OnMouseUp", Drop)
    dialog:SetScript("OnShow", function() box:SetFocus() end)
    dialog:SetScript("OnHide", function()
        box:ClearFocus()
        HideSuggestions()
    end)

    if hooksecurefunc then
        if ChatFrameUtil and ChatFrameUtil.InsertLink then
            hooksecurefunc(ChatFrameUtil, "InsertLink", OnLink)
        elseif ChatEdit_InsertLink then
            hooksecurefunc("ChatEdit_InsertLink", OnLink)
        end
    end
end

function AddItem.Refresh()
    if not dialog or not shown then return end
    dialog.target:SetText(L.ADD_TARGET:format(ns.Custom.ListText(shown.class, shown.spec, shown.list)))
end

function AddItem.Open(state)
    if not dialog then Build() end
    shown = state
    dialog:ClearAllPoints()
    dialog:SetPoint("CENTER", ns.Browser and ns.Browser.window or UIParent, "CENTER", 0, 0)
    AddItem.Refresh()
    dialog.box:SetText("")
    Say(true, "")
    dialog:Show()
    if dialog.Raise then dialog:Raise() end
    dialog.box:SetFocus()
end

function AddItem.Close()
    if dialog then dialog:Hide() end
end
