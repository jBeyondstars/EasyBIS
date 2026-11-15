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

  AddItem.Open(shown)     shown: the window's state { class, spec, list, slot }, read at each add
  AddItem.Close()
  AddItem.Refresh()       the name of the list it adds to follows the window
  AddItem.Submit(text)    ok, the sentence shown
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

function AddItem.Submit(text)
    if not dialog or not shown then return false end
    -- a one-handed weapon goes to the off hand when the window is filtered on that slot
    local ok, message = ns.Custom.Submit(shown.class, shown.spec, shown.list, text, shown.slot)
    Say(ok, message)
    if ok then dialog.box:SetText("") end
    return ok, message
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
    box:SetScript("OnEnterPressed", function(self) AddItem.Submit(self:GetText()) end)
    box:SetScript("OnEscapePressed", function() dialog:Hide() end)
    box:SetScript("OnReceiveDrag", Drop)

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
    dialog:SetScript("OnHide", function() box:ClearFocus() end)

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
