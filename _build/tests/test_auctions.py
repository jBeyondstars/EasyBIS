"""Exercise the auction tab with the addon's real lists and an auction house searched item by item."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_addon import Game, lupa


@unittest.skipIf(lupa is None, "lupa is not installed")
class AuctionTest(unittest.TestCase):
    def setUp(self):
        game = Game(locale="frFR", saved="""
            EasyBISCharDB = { class = "SHAMAN", spec = 2, list = "pve" }
            EasyBISDB = { listAlts = false }
        """)
        self.run_lua = game.lua.execute
        g = game.lua.globals()
        g.ns, g.stub = game.ns, game.stub
        self.run_lua("""
            house = CreateFrame("Frame")
            AuctionHouseFrame = house
            AuctionHouseFrameDisplayMode = {Buy = {"BrowseResultsFrame"}}
            house.Tabs = { CreateFrame("Button") }
            function house:SetDisplayMode(mode) self.mode = mode end
            function house:SetTitle(title) self.title = title end
            function house:SelectBrowseResult(result)
                assert(self.mode == AuctionHouseFrameDisplayMode.Buy)
                self.selection = result
                self:SetDisplayMode({"ItemBuyFrame"})
            end
            function PanelTemplates_TabResize() end
            function PanelTemplates_SelectTab(tab) tab.selected = true end
            function PanelTemplates_DeselectTab(tab) tab.selected = false end
            function GetMoneyString(copper) return tostring(copper) end
            local head = ns.Ladders.For("SHAMAN", 2, "pve").head
            best, alt = head.best[1].id, head.alts[1].id
            -- an item's key: without level or suffix for a search, with them for a variant on sale
            function key(id, suffix, level)
                return {itemID=id, itemLevel=level or 0, itemSuffix=suffix or 0, battlePetSpeciesID=0}
            end
            ready, fullItem, fullCommodity = true, true, true
            -- requests: the IDs searched and the pages asked for, in order. unknown, commodities, silent: by ID,
            -- the items the game does not know, those it sells as commodities, those whose search it never answers
            results, requests, unknown, commodities, silent = {}, {}, {}, {}, {}
            C_AuctionHouse = {
                IsThrottledMessageSystemReady = function() return ready end,
                GetItemKeyInfo = function(k)
                    if unknown[k.itemID] then return nil end
                    return {itemName="Item "..k.itemID, iconFileID=123, quality=4, isCommodity=commodities[k.itemID]}
                end,
                SendSellSearchQuery = function(k, _, separate)
                    assert(separate and k.itemLevel == 0 and k.itemSuffix == 0 and not commodities[k.itemID])
                    requests[#requests+1] = k.itemID
                end,
                SendSearchQuery = function(k, _, separate)
                    assert(separate and commodities[k.itemID])
                    requests[#requests+1] = k.itemID
                end,
                HasFullItemSearchResults = function() return fullItem end,
                RequestMoreItemSearchResults = function(k) requests[#requests+1] = "moreItem" end,
                GetNumItemSearchResults = function() return #results end,
                GetItemSearchResultInfo = function(_, i) return results[i] end,
                HasFullCommoditySearchResults = function() return fullCommodity end,
                RequestMoreCommoditySearchResults = function(id) requests[#requests+1] = "moreCommodity" end,
                GetNumCommoditySearchResults = function() return #results end,
                GetCommoditySearchResultInfo = function(_, i) return results[i] end,
            }
            fire = stub.fire
            function click(button) stub.run(button, "OnClick", "LeftButton") end
            function tick(seconds)
                for _, frame in ipairs(stub.frames) do
                    if frame.events.ITEM_SEARCH_RESULTS_UPDATED then stub.run(frame, "OnUpdate", seconds or 0.1) end
                end
            end
            function open()
                fire("AUCTION_HOUSE_SHOW"); stub.runTimers()
                click(EasyBISAuctionTab)
                p = EasyBISAuctionPanel
                assert(EasyBISAuctionTab.text == "EasyBis" and p:IsShown())
                assert(p.spec.button.Text.text:find("Amélioration") and p.list.buttons[1].highlightLocked)
                assert(p.list.buttons[1].Text.text == "JcE" and p.list.label.text == ns.L.FILTER_LIST)
                assert(p.phase.text == ns.PhaseName(ns.Phase()))
                click(p.scan)
            end
            -- the scan's progress, as the tab writes it: the item searched, how many there are
            function progress()
                local index, total = p.status.text:match("(%d+)/(%d+)$")
                return tonumber(index), tonumber(total)
            end
            -- answers the searches with nothing on sale, up to the one for `id`, which is left to the test
            function upto(id)
                for _ = 1, 500 do
                    tick()
                    if requests[#requests] == id then return end
                    results = {}
                    fire("ITEM_SEARCH_RESULTS_UPDATED", key(requests[#requests]))
                end
                error("item " .. id .. " is never searched")
            end
            -- answers every search left: sales[id] = the auctions of an item, nothing for the others
            function finish(sales)
                for _ = 1, 1000 do
                    if p.scan.text == ns.L.AH_SCAN then return end
                    tick()
                    local id = requests[#requests]
                    if id and not silent[id] then
                        results = sales and sales[id] or {}
                        fire("ITEM_SEARCH_RESULTS_UPDATED", key(id))
                    end
                end
                error("the scan does not end")
            end
            function shown()
                local found = {}
                for _, row in ipairs(stub.frames) do
                    if row.data and row.data.key and row:IsShown() then found[#found+1] = row end
                end
                return found
            end
            -- the entry of a menu whose text contains `text`
            function entry(menu, text)
                for _, item in ipairs(menu.items) do
                    if item.text and item.text:find(text, 1, true) then return item end
                end
                error("no menu entry contains " .. text)
            end
        """)

    def test_each_piece_is_searched_once_the_best_picks_first(self):
        self.run_lua("""
            ready = false
            open(); tick()
            local first, total = progress()
            assert(first == 1 and total > 20 and #requests == 0, "the progress is known before the first search")
            ready = true; finish()
            assert(#requests == total and p.status.text == ns.L.AH_EMPTY)

            local wanted, place = {}, {}
            for _, row in ipairs(ns.Rows.Items({class="SHAMAN", spec=2, list="pve"}, true)) do
                if row.kind == "item" then wanted[row.id] = wanted[row.id] or row.bis or row.tie or false end
            end
            local last = 0
            for index, id in ipairs(requests) do
                assert(wanted[id] ~= nil and not place[id], "a piece of the list, searched once")
                place[id] = index
                if wanted[id] then last = index end
            end
            for id, bis in pairs(wanted) do
                assert(place[id], "every piece is searched")
                assert(bis or place[id] > last, "the alternatives come after the best picks")
            end
        """)

    def test_lowest_buyout_among_the_variants_and_pages(self):
        self.run_lua("""
            open(); upto(best)
            -- the answer to another search, and a first page that is not the last
            results = {{quantity=1, buyoutAmount=1}}
            fire("ITEM_SEARCH_RESULTS_UPDATED", key(best, 17, 60)); assert(#shown() == 0)
            fullItem = false
            fire("ITEM_SEARCH_RESULTS_UPDATED", key(best)); tick(); assert(requests[#requests] == "moreItem")
            assert(#shown() == 0)
            fullItem = true
            local plain, variant = key(best, 0, 60), key(best, 17, 60)
            local link = "|cffa335ee|Hitem:" .. best .. "::::::17|h[Helm of the Bear]|h|r"
            -- a bid alone, no buyout, the player's own and the account's: none is a price to pay
            results = {{quantity=1, minBid=10, itemKey=plain}, {quantity=1, buyoutAmount=0, itemKey=plain},
                {quantity=1, buyoutAmount=20, containsOwnerItem=true, itemKey=plain},
                {quantity=1, buyoutAmount=30, containsAccountItem=true, itemKey=plain},
                {quantity=1, buyoutAmount=150, itemKey=plain},
                {quantity=1, buyoutAmount=90, itemKey=variant, itemLink=link}}
            fire("ITEM_SEARCH_RESULTS_ADDED", key(best))
            assert(#shown() == 1 and shown()[1].price.text == "90")
            finish({[alt] = {{quantity=1, buyoutAmount=40, itemKey=key(alt, 0, 58)}}})
            assert(p.status.text == ns.L.AH_COUNT:format(2))

            local found = shown()
            assert(#found == 2 and found[1].data.key == variant and found[1].data.link == link)
            -- the name as the game's list writes it: the auction's own, in its quality's color, no brackets
            assert(found[1].item.text == "|cffa335eeHelm of the Bear|r")
            assert(found[2].item.text == "|cffa335eeItem " .. alt .. "|r" and found[2].icon.texture == 123)
            assert(found[1].rank.text:find("BIS") and found[2].rank.text == "Alternative")
            assert(found[1].slot.text == ns.SlotName("head") and found[2].price.text == "40")
            click(found[1]); assert(house.selection.itemKey == variant and house.selection.minPrice == 90)
            assert(not EasyBISAuctionTab.selected and not p:IsShown())
        """)

    def test_empty_and_bid_only_results(self):
        self.run_lua("""
            open(); finish(); assert(p.status.text == ns.L.AH_EMPTY)
            click(p.scan)
            finish({[best] = {{quantity=1, minBid=2}, {quantity=1, buyoutAmount=3, containsOwnerItem=true}}})
            assert(p.status.text == ns.L.AH_EMPTY and p.scan.text == ns.L.AH_SCAN and #shown() == 0)
        """)

    def test_pieces_bound_when_picked_up_are_not_searched(self):
        self.run_lua("""
            open(); local _, all = progress(); click(p.scan)
            -- the game says how two pieces bind: one cannot be sold, the other can
            stub.itemNames[best], stub.bindings[best] = "Helm", 1
            stub.itemNames[alt], stub.bindings[alt] = "Other helm", 2
            requests = {}
            click(p.scan); local _, total = progress(); assert(total == all - 1)
            finish({[alt] = {{quantity=1, buyoutAmount=15}}})
            local asked = {}
            for _, id in ipairs(requests) do asked[id] = true end
            assert(asked[alt] and not asked[best] and #requests == total)
            assert(#shown() == 1 and p.status.text == ns.L.AH_COUNT:format(1))
        """)

    def test_item_without_answer_is_skipped_and_keeps_the_others(self):
        self.run_lua("""
            -- the game never describes one item, and never answers the search for another
            local other = ns.Ladders.For("SHAMAN", 2, "pve").chest.best[1].id
            unknown[best], silent[other] = true, true
            open(); finish({[alt] = {{quantity=1, buyoutAmount=15}}})
            assert(p.status.text == ns.L.AH_INCOMPLETE and p.scan.text == ns.L.AH_SCAN)
            local asked = 0
            for _, id in ipairs(requests) do
                assert(id ~= best, "no search for an item the game does not know")
                if id == other then asked = asked + 1 end
            end
            assert(asked == 1)
            local found = shown()
            assert(#found == 1 and found[1].data.key.itemID == alt and found[1].price.text == "15")
        """)

    def test_search_held_back_by_the_game_waits_longer(self):
        self.run_lua("""
            ready = false
            open(); tick(60); assert(progress() == 1 and #requests == 0)
            ready = true; tick(); assert(#requests == 1)
            -- once sent, ten seconds for the answer
            tick(9); assert(progress() == 1)
            tick(2); assert(progress() == 2)
            ready = false; tick(91); assert(progress() == 3 and #requests == 1)
            ready = true; finish(); assert(p.status.text == ns.L.AH_INCOMPLETE)
        """)

    def test_stop_another_tab_and_close(self):
        self.run_lua("""
            open(); tick(); assert(p.scan.text == ns.L.AH_STOP)
            click(p.scan); assert(p.status.text == ns.L.AH_INCOMPLETE and p.scan.text == ns.L.AH_SCAN)
            click(p.scan); tick(); house:SetDisplayMode({"Buy"})
            assert(not p:IsShown() and p.scan.text == ns.L.AH_SCAN)
            local before = #requests
            fire("ITEM_SEARCH_RESULTS_UPDATED", key(requests[before])); tick(); assert(#requests == before)
            fire("AUCTION_HOUSE_CLOSED"); assert(p.status.text == ns.L.AH_IDLE)
            open(); tick(); fire("AUCTION_HOUSE_CLOSED")
            assert(p.status.text == ns.L.AH_IDLE and p.scan.text == ns.L.AH_SCAN)
        """)

    def test_commodity_pages_and_list_change(self):
        self.run_lua("""
            commodities[alt] = true
            open(); upto(alt)
            fullCommodity = false
            fire("COMMODITY_SEARCH_RESULTS_UPDATED", alt); tick(); assert(requests[#requests] == "moreCommodity")
            fullCommodity = true
            results = {{quantity=1, numOwnerItems=1, unitPrice=3, containsOwnerItem=true},
                {quantity=2, numOwnerItems=0, unitPrice=10}}
            fire("COMMODITY_SEARCH_RESULTS_ADDED", alt)
            assert(#shown() == 1 and shown()[1].price.text == "10" and shown()[1].data.key.itemID == alt)
            finish(); assert(p.status.text == ns.L.AH_COUNT:format(1))
            click(p.scan); ns:SetAlternatives(3)
            assert(p.scan.text == ns.L.AH_SCAN and p.status.text == ns.L.AH_IDLE and #shown() == 0)
        """)

    def test_spec_and_list_chosen_in_the_tab(self):
        self.run_lua("""
            open(); finish({[best] = {{quantity=1, buyoutAmount=15}}}); assert(#shown() == 1)

            -- the other list: the results of the first one go, the choice is the character's
            click(p.list.buttons[2])
            assert(select(3, ns.Browser.Target()) == "pvp" and EasyBISCharDB.list == "pvp")
            assert(p.list.buttons[2].highlightLocked and not p.list.buttons[1].highlightLocked)
            assert(#shown() == 0 and p.status.text == ns.L.AH_IDLE)

            -- another class: a scan in progress stops, the next one looks for that spec's gear
            click(p.scan); tick(); assert(p.scan.text == ns.L.AH_STOP)
            stub.run(p.spec.button, "OnMouseDown", "LeftButton")
            local fury = entry(stub.menu, "Warrior").items[2]
            assert(not fury.selected()); fury.pick(); assert(fury.selected())
            local class, spec, list = ns.Browser.Target()
            assert(class == "WARRIOR" and spec == 2 and list == "pvp")
            assert(EasyBISCharDB.class == "WARRIOR" and EasyBISCharDB.spec == 2)
            assert(p.spec.button.Text.text:find("Warrior") and p.spec.button.Text.text:find(ns.SpecName("Fury")))
            assert(p.scan.text == ns.L.AH_SCAN and p.status.text == ns.L.AH_IDLE)
            local helm = ns.Ladders.For("WARRIOR", 2, "pvp").head.best[1].id
            assert(helm ~= best)
            requests = {}
            click(p.scan); finish({[best] = {{quantity=1, buyoutAmount=15}}, [helm] = {{quantity=1, buyoutAmount=20}}})
            local asked = {}
            for _, id in ipairs(requests) do asked[id] = true end
            assert(asked[helm] and not asked[best])
            local found = shown()
            assert(#found == 1 and found[1].data.key.itemID == helm and found[1].rank.text:find("BIS"))

            -- one choice for the tab and the window: each follows the other
            ns.Browser.Open()
            local window = ns.Browser.window
            assert(window.spec.button.Text.text:find("Warrior") and window.list.buttons[2].highlightLocked)
            click(window.list.buttons[1])
            assert(p.list.buttons[1].highlightLocked and #shown() == 0 and p.status.text == ns.L.AH_IDLE)
        """)

    def test_lines_drawn_with_the_games_own_parts(self):
        self.run_lua("""
            local known, make = C_XMLUtil.GetTemplateInfo, CreateFrame
            function C_XMLUtil.GetTemplateInfo(name)
                return (name == "MoneyDisplayFrameTemplate" or name == "ColumnDisplayButtonShortTemplate") and {}
                    or known(name)
            end
            function CreateFrame(kind, name, parent, template)
                local frame = make(kind, name, parent, template)
                if template == "MoneyDisplayFrameTemplate" then
                    -- as the game's: what the frame is asked to be is read when it loads
                    function frame:OnLoad() self.auctionCoins = self.useAuctionHouseIcons and self.useAuctionHouseCopperValue end
                    function frame:SetAmount(copper) self.amount = copper end
                    frame:OnLoad()
                end
                return frame
            end
            function C_AuctionHouse.SupportsCopperValues() return true end
            AUCTION_HOUSE_BROWSE_HEADER_NAME = "Nom"

            open(); finish({[best] = {{quantity=1, buyoutAmount=12345}}})
            local row = shown()[1]
            assert(row.price.template == "MoneyDisplayFrameTemplate" and row.price.auctionCoins)
            assert(row.price.amount == 12345 and row.height == 20)
            assert(row.icon.points[1][2] == 178, "the item starts after the price column, wide enough for copper")

            local titles = {}
            for _, frame in ipairs(stub.frames) do
                if frame.template == "ColumnDisplayButtonShortTemplate" then
                    assert(not frame:IsEnabled() and frame.height == 19)
                    titles[#titles+1] = frame.text
                end
            end
            table.sort(titles)
            local expected = {ns.L.AH_BUYOUT, ns.L.FILTER_SLOT, ns.L.AH_RANK, "Nom"}
            table.sort(expected)
            assert(table.concat(titles, "|") == table.concat(expected, "|"))
        """)

    def test_shared_tab_bar_attaches_once_and_last(self):
        self.run_lua("""
            local created, button = 0, CreateFrame("Button")
            LibStub = function(name, optional)
                assert(name == "LibAHTab-1-0" and optional)
                return {CreateTab=function(_, id, panel, text)
                    assert(id == "EasyBIS" and panel == EasyBISAuctionPanel and text == "EasyBis")
                    created = created + 1
                end, GetButton=function(_, id) assert(id == "EasyBIS"); return button end}
            end
            Enum.PlayerInteractionType = {Auctioneer = 21}
            fire("ADDON_LOADED", "Blizzard_AuctionHouseUI")
            fire("PLAYER_INTERACTION_MANAGER_FRAME_SHOW", 21); fire("AUCTION_HOUSE_SHOW")
            -- the addons that add their tabs as the house opens come first
            assert(created == 0)
            stub.runTimers(); assert(created == 1 and not EasyBISAuctionTab)
            fire("AUCTION_HOUSE_SHOW"); stub.runTimers(); assert(created == 1)

            -- switched off: the shared bar's tab hides, and leaves no room behind
            ns:SetOption("auctionTab", false); assert(not button:IsShown() and button.width < 1)
            ns:SetOption("auctionTab", true); assert(button:IsShown())
        """)

    def test_tab_switched_off_in_the_options(self):
        self.run_lua("""
            ns:SetOption("auctionTab", false)
            fire("AUCTION_HOUSE_SHOW"); stub.runTimers()
            assert(not EasyBISAuctionTab and not EasyBISAuctionPanel)

            -- switched on with the house open: no need to open it again
            ns:SetOption("auctionTab", true)
            open(); tick(); assert(p.scan.text == ns.L.AH_STOP)

            -- switched off on the tab itself: the scan stops and the game's Buy tab takes over
            ns:SetOption("auctionTab", false)
            assert(not EasyBISAuctionTab:IsShown() and not p:IsShown())
            assert(house.mode == AuctionHouseFrameDisplayMode.Buy and p.scan.text == ns.L.AH_SCAN)
            assert(EasyBISDB.auctionTab == false)
            ns:SetOption("auctionTab", true); assert(EasyBISAuctionTab:IsShown() and not p:IsShown())
        """)


if __name__ == "__main__":
    unittest.main()
