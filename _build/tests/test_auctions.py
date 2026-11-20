"""Exercise the auction tab with the addon's real lists and a paginated auction house."""
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
            function key(id, suffix) return {itemID=id, itemLevel=60, itemSuffix=suffix or 0, battlePetSpeciesID=0} end
            best = key(head.best[1].id)
            alt = key(head.alts[1].id)
            function browse(k) return {itemKey=k, totalQuantity=1, minPrice=1} end
            ready, fullBrowse, fullItem, fullCommodity = true, true, true, true
            listings, results, requests = {}, {}, {}
            C_AuctionHouse = {
                IsThrottledMessageSystemReady = function() return ready end,
                SendBrowseQuery = function(query) requests[#requests+1] = query end,
                GetBrowseResults = function() return listings end,
                HasFullBrowseResults = function() return fullBrowse end,
                RequestMoreBrowseResults = function() requests[#requests+1] = "moreBrowse" end,
                GetItemKeyInfo = function(k) return {itemName="Item "..k.itemID, iconFileID=123} end,
                SendSearchQuery = function(k, _, separate) assert(separate); requests[#requests+1] = k end,
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
                fire("AUCTION_HOUSE_SHOW")
                click(EasyBISAuctionTab)
                p = EasyBISAuctionPanel
                assert(EasyBISAuctionTab.text == "EasyBis" and p:IsShown())
                assert(p.target.text:find("Amélioration") and p.target.text:find("JcE"))
                click(p.scan)
            end
        """)

    def test_buyouts_from_all_pages_and_variants(self):
        self.run_lua("""
            fullBrowse, ready = false, false
            open(); tick(); assert(#requests == 0)
            ready = true; tick(); assert(requests[1].searchString == "")
            listings = {browse(key(1)), browse(best)}
            fire("AUCTION_HOUSE_BROWSE_RESULTS_UPDATED"); tick(); assert(requests[2] == "moreBrowse")
            fullBrowse = true
            local variant = key(best.itemID, 17)
            listings[3], listings[4] = browse(alt), browse(variant)
            fire("AUCTION_HOUSE_BROWSE_RESULTS_ADDED", {listings[3], listings[4]}); tick()
            assert(requests[3] == best)
            fire("ITEM_SEARCH_RESULTS_UPDATED", variant); tick(); assert(#requests == 3)
            fullItem = false
            fire("ITEM_SEARCH_RESULTS_UPDATED", best); tick(); assert(requests[4] == "moreItem")
            fullItem = true
            results = {{quantity=1, minBid=10}, {quantity=1, buyoutAmount=0},
                {quantity=1, buyoutAmount=20, containsOwnerItem=true},
                {quantity=1, buyoutAmount=30, containsAccountItem=true}, {quantity=1, buyoutAmount=150}}
            fire("ITEM_SEARCH_RESULTS_ADDED", best); tick(); assert(requests[5] == alt)
            results = {{quantity=1, buyoutAmount=40}}
            fire("ITEM_SEARCH_RESULTS_UPDATED", alt); tick(); assert(requests[6] == variant)
            results = {{quantity=1, buyoutAmount=90, itemLink="variant link"}}
            fire("ITEM_SEARCH_RESULTS_UPDATED", variant); assert(p.status.text == ns.L.AH_COUNT:format(2))
            local found = {}
            for _, row in ipairs(stub.frames) do
                if row.data and row.data.key and row:IsShown() then found[#found+1] = row end
            end
            assert(#found == 2 and found[1].price.text == "90" and found[1].item.text == "variant link")
            assert(found[1].rank.text:find("BIS") and found[2].rank.text == "Alternative")
            assert(found[2].price.text == "40")
            click(found[1]); assert(house.selection.itemKey == variant and house.selection.minPrice == 90)
            assert(not EasyBISAuctionTab.selected and not p:IsShown())
        """)

    def test_empty_and_bid_only_results(self):
        self.run_lua("""
            open(); tick(); fire("AUCTION_HOUSE_BROWSE_RESULTS_UPDATED")
            assert(p.status.text == ns.L.AH_EMPTY)
            click(p.scan); tick()
            listings = {browse(best)}
            fire("AUCTION_HOUSE_BROWSE_RESULTS_UPDATED"); tick()
            results = {{quantity=1, minBid=2}, {quantity=1, buyoutAmount=3, containsOwnerItem=true}}
            fire("ITEM_SEARCH_RESULTS_UPDATED", best)
            assert(p.status.text == ns.L.AH_EMPTY and p.scan.text == ns.L.AH_SCAN)
        """)

    def test_one_unanswered_item_keeps_other_verified_offers(self):
        self.run_lua("""
            open(); tick(); listings = {browse(best), browse(alt)}
            fire("AUCTION_HOUSE_BROWSE_RESULTS_UPDATED"); tick()
            tick(31); tick(); assert(requests[#requests] == alt)
            results = {{quantity=1, buyoutAmount=15}}
            fire("ITEM_SEARCH_RESULTS_UPDATED", best)
            fire("ITEM_SEARCH_RESULTS_UPDATED", alt)
            assert(p.status.text == ns.L.AH_INCOMPLETE and p.scan.text == ns.L.AH_SCAN)
            for _, row in ipairs(stub.frames) do
                if row.data and row.data.key == alt then assert(row.price.text == "15"); return end
            end
            error("missing verified offer")
        """)

    def test_interruption_retry_and_close(self):
        self.run_lua("""
            open(); tick()
            C_AuctionHouse.SendBrowseQuery({searchString="someone else's query"})
            assert(p.status.text == ns.L.AH_INCOMPLETE)
            click(p.scan); tick(); fire("AUCTION_HOUSE_BROWSE_FAILURE")
            assert(p.status.text == ns.L.AH_INCOMPLETE)
            click(p.scan); tick(); tick(31)
            assert(p.status.text == ns.L.AH_INCOMPLETE and p.scan.text == ns.L.AH_SCAN)
            click(p.scan); tick(); click(p.scan); assert(p.status.text == ns.L.AH_INCOMPLETE)
            click(p.scan); tick(); house:SetDisplayMode({"Buy"})
            local before = #requests
            fire("AUCTION_HOUSE_BROWSE_RESULTS_UPDATED"); tick(); assert(#requests == before)
            fire("AUCTION_HOUSE_CLOSED"); assert(p.status.text == ns.L.AH_IDLE)
            open(); tick(); fire("AUCTION_HOUSE_CLOSED")
            assert(p.status.text == ns.L.AH_IDLE and p.scan.text == ns.L.AH_SCAN)
        """)

    def test_commodity_pages_and_list_change(self):
        self.run_lua("""
            open(); tick(); listings = {browse(alt)}
            fire("AUCTION_HOUSE_BROWSE_RESULTS_UPDATED"); tick()
            fullCommodity = false
            fire("COMMODITY_SEARCH_RESULTS_UPDATED", alt.itemID); tick(); assert(requests[3] == "moreCommodity")
            fullCommodity = true
            results = {{quantity=1, numOwnerItems=1, unitPrice=3, containsOwnerItem=true},
                {quantity=2, numOwnerItems=0, unitPrice=10}}
            fire("COMMODITY_SEARCH_RESULTS_ADDED", alt.itemID)
            assert(p.status.text == ns.L.AH_COUNT:format(1))
            click(p.scan); ns:SetAlternatives(3)
            assert(p.scan.text == ns.L.AH_SCAN and p.status.text == ns.L.AH_IDLE)
        """)

    def test_shared_tab_bar_attaches_once(self):
        self.run_lua("""
            local created = 0
            LibStub = function(name, optional)
                assert(name == "LibAHTab-1-0" and optional)
                return {CreateTab=function(_, id, panel, text)
                    assert(id == "EasyBIS" and panel == EasyBISAuctionPanel and text == "EasyBis")
                    created = created + 1
                end}
            end
            fire("ADDON_LOADED", "Blizzard_AuctionHouseUI"); fire("AUCTION_HOUSE_SHOW")
            assert(created == 1 and not EasyBISAuctionTab)
        """)


if __name__ == "__main__":
    unittest.main()
