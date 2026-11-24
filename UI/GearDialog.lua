local _, ns = ...
local L, W = ns.L, ns.Widgets

--[[
The dialog of the player's own lists: a new list, a list's new name, a WoWSims Forever export pasted into a list,
and the question before a list is deleted.

The header names what the dialog does, and under it the list it does it to. A name is typed in a single line; an
export is pasted in a tall box that scrolls. The foot has what went wrong on the left, Cancel and the action on
the right.

  GearDialog.Open(state, mode, selectList)   mode: "create", "rename", "import" or "delete"
                                             selectList(key): shows the list just created
  GearDialog.Check(state, available)         closes it when the window no longer shows its list
  GearDialog.Close()
]]

local GearDialog = {}
ns.GearDialog = GearDialog
local dialog

local WIDTH = 480
local FOOTER = 44
local PAD = W.DIALOG_PAD
local NAME_HEIGHT = 30        -- the box a name is typed in
local PASTE_HEIGHT = 170      -- the box an export is pasted in
local ALERT = "Interface\\DialogFrame\\UI-Dialog-Icon-AlertNew"
local ICONS = {
    create = "Interface\\Icons\\INV_Misc_Note_01",
    rename = "Interface\\Icons\\INV_Misc_Note_01",
    import = "Interface\\Icons\\INV_Misc_Gear_01",
}
local TITLES = { create = L.GEAR_NEW, import = L.GEAR_IMPORT, rename = L.GEAR_RENAME, delete = L.GEAR_DELETE }

local function Submit()
    local text = dialog.box:GetText()
    if dialog.mode == "import" then
        local count, message = ns.Custom.Import(dialog.class, dialog.spec, dialog.key, text)
        if not count then dialog.error:SetText(message); return end
        ns:Print(L.GEAR_DONE:format(count, ns.Custom.GearList(dialog.class, dialog.spec, dialog.key).name))
    elseif dialog.mode == "rename" then
        local ok, message = ns.Custom.RenameList(dialog.class, dialog.spec, dialog.key, text)
        if not ok then dialog.error:SetText(message); return end
    elseif dialog.mode == "delete" then
        ns.Custom.DeleteList(dialog.class, dialog.spec, dialog.key)
    else
        local key, message = ns.Custom.CreateList(dialog.class, dialog.spec, text)
        if not key then dialog.error:SetText(message); return end
        dialog.selectList(key)
    end
    dialog:Hide()
end

local function Close()
    dialog:Hide()
end

local function Build()
    dialog = W.Dialog("EasyBISGearDialog", ns.Browser.window, WIDTH, FOOTER)
    dialog:SetPoint("CENTER")

    -- what to type or paste, or the question asked
    dialog.hint = dialog:CreateFontString(nil, "OVERLAY", ns.Browser.FONTS.text)
    dialog.hint:SetPoint("TOPLEFT", PAD, -(W.DIALOG_HEADER + 12))
    dialog.hint:SetWidth(WIDTH - 2 * PAD)
    dialog.hint:SetJustifyH("LEFT")

    -- a name: one line
    dialog.nameWell = W.Well(dialog)
    local name = CreateFrame("EditBox", nil, dialog.nameWell)
    dialog.nameBox = name
    dialog.nameWell:Hold(name)
    dialog.nameWell:SetPoint("TOPLEFT", dialog.hint, "BOTTOMLEFT", 0, -6)
    dialog.nameWell:SetSize(WIDTH - 2 * PAD, NAME_HEIGHT)
    name:SetPoint("TOPLEFT", dialog.nameWell, "TOPLEFT", 8, 0)
    name:SetPoint("BOTTOMRIGHT", dialog.nameWell, "BOTTOMRIGHT", -8, 0)
    name:SetFontObject("ChatFontNormal")
    name:SetAutoFocus(false)
    name:SetMaxLetters(24)
    name:SetScript("OnEscapePressed", Close)
    name:SetScript("OnEnterPressed", Submit)

    -- an export: as many lines as it has, scrolled
    dialog.pasteWell = W.Well(dialog)
    local scroll = W.Scroll(dialog.pasteWell)
    local paste = CreateFrame("EditBox", nil, scroll)
    dialog.pasteBox, dialog.scroll = paste, scroll
    dialog.pasteWell:Hold(paste)
    dialog.pasteWell:SetPoint("TOPLEFT", dialog.hint, "BOTTOMLEFT", 0, -10)
    dialog.pasteWell:SetSize(WIDTH - 2 * PAD, PASTE_HEIGHT)
    scroll:SetPoint("TOPLEFT", dialog.pasteWell, "TOPLEFT", 8, -6)
    scroll:SetPoint("BOTTOMRIGHT", dialog.pasteWell, "BOTTOMRIGHT", -26, 6)   -- the bar stands right of the frame
    paste:SetSize(WIDTH - 2 * PAD - 34, PASTE_HEIGHT - 12)
    paste:SetFontObject("ChatFontNormal")
    paste:SetAutoFocus(false)
    paste:SetMultiLine(true)
    paste:SetMaxLetters(0)
    paste:SetScript("OnEscapePressed", Close)
    paste:SetScript("OnCursorChanged", function(_, _, y, _, height)
        local offset = scroll:GetVerticalScroll()
        local bottom = -y + height - scroll:GetHeight()
        if -y < offset then scroll:SetVerticalScroll(-y)
        elseif bottom > offset then scroll:SetVerticalScroll(bottom) end
    end)
    scroll:SetScrollChild(paste)

    local middle = 4 + (FOOTER - 4) / 2   -- the foot's, over the border
    dialog.submit = W.Button(dialog, L.GEAR_IMPORT)
    dialog.submit:SetPoint("RIGHT", dialog, "BOTTOMRIGHT", -PAD + 4, middle)
    dialog.submit:SetScript("OnClick", Submit)
    dialog.cancel = W.Button(dialog, L.GEAR_CANCEL)
    dialog.cancel:SetPoint("RIGHT", dialog.submit, "LEFT", -6, 0)
    dialog.cancel:SetScript("OnClick", Close)
    dialog.error = dialog:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    dialog.error:SetPoint("LEFT", dialog, "BOTTOMLEFT", PAD, middle)
    dialog.error:SetJustifyH("LEFT")
    dialog.error:SetTextColor(1.00, 0.45, 0.40)

    dialog:SetScript("OnHide", function()
        name:ClearFocus()
        paste:ClearFocus()
    end)
end

function GearDialog.Open(state, mode, selectList)
    if not dialog then Build() end
    ns.AddItem.Close()
    dialog.class, dialog.spec, dialog.key = state.class, state.spec, state.itemList
    dialog.mode, dialog.selectList = mode, selectList
    local import, deleting = mode == "import", mode == "delete"
    local gear = ns.Custom.GearList(state.class, state.spec, state.itemList)

    -- a new list has no name yet: the header says whose it will be
    dialog.title:SetText(TITLES[mode])
    dialog.sub:SetText(mode == "create" and ns.Custom.ListText(state.class, state.spec, state.list) or gear.name)
    dialog:SetIcon(ICONS[mode] or ALERT, deleting)

    dialog.hint:SetText(deleting and L.GEAR_DELETE_CONFIRM:format(gear.name) or import and L.GEAR_PASTE or L.GEAR_NAME)
    if deleting then
        dialog.hint:SetTextColor(1, 1, 1)
    else
        dialog.hint:SetTextColor(W.MUTED[1], W.MUTED[2], W.MUTED[3])
    end
    dialog.nameWell:SetShown(not import and not deleting)
    dialog.pasteWell:SetShown(import)
    dialog.box = import and dialog.pasteBox or dialog.nameBox
    dialog.box:SetText(mode == "rename" and gear.name or "")
    dialog.scroll:SetVerticalScroll(0)

    -- the action is as wide as its name; what went wrong has the room left of the buttons
    dialog.submit:SetText(TITLES[mode])
    dialog.submit:SetWidth(math.max(90, math.ceil(dialog.submit:GetFontString():GetStringWidth()) + 28))
    dialog.error:SetText("")
    dialog.error:SetWidth(WIDTH - 2 * PAD - dialog.submit:GetWidth() - dialog.cancel:GetWidth() - 14)

    dialog:Show()   -- shown, the hint knows how many lines it takes
    local body = math.ceil(dialog.hint:GetStringHeight())
    if import then
        body = body + 10 + PASTE_HEIGHT
    elseif not deleting then
        body = body + 6 + NAME_HEIGHT
    end
    dialog:SetHeight(W.DIALOG_HEADER + 12 + body + 14 + FOOTER)
    if not deleting then dialog.box:SetFocus() end
end

function GearDialog.Check(state, available)
    if dialog and dialog:IsShown() and (not available or dialog.class ~= state.class
        or dialog.spec ~= state.spec or dialog.key ~= state.itemList) then dialog:Hide() end
end

function GearDialog.Close()
    if dialog then dialog:Hide() end
end
