"""Tests for the addon's Lua, run outside the game with stand-ins for the WoW API.

    python -P tests/test_addon.py

Needs the `lupa` package. The addon's files are loaded in the order of
EasyBIS.toc, then the game's startup events are sent. The picks the Lua code
makes are checked against the generator's (ladders.py), which is itself
checked against foreverdb.net.
"""
from __future__ import annotations

import re
import sys
import unittest
from itertools import product
from pathlib import Path

TESTS = Path(__file__).resolve().parent
BUILD = TESTS.parent
ADDON = BUILD.parent
sys.path.insert(0, str(BUILD))

import consumable_lists  # noqa: E402
import fdb  # noqa: E402
import ladders  # noqa: E402
import luaout  # noqa: E402
import phases  # noqa: E402
import reputations  # noqa: E402
import ranks  # noqa: E402
import runs  # noqa: E402

try:
    import lupa
except ImportError:  # pragma: no cover
    lupa = None

CLASSES = ("WARRIOR", "PALADIN", "HUNTER", "ROGUE", "PRIEST", "SHAMAN", "MAGE", "WARLOCK", "DRUID")
EYE_OF_REND = 12587          # the best PvE head for an Alliance Enhancement Shaman
SENTINELS_LEGGINGS = 22748   # Alliance; the Horde wears its twin
OUTRIDERS_LEGGINGS = 22673
ATIESH = 22589               # a Naxxramas quest reward: Classic data only
MAGEBLADE = 23451            # Grand Marshal's Mageblade (Alliance), a rank 14 one-hander: the best main hand of a
#                              Fire Mage before the raids. A PvP-rank reward is ranked in the PvE list on its stats.
VAULTED_SECRETS = 21413      # a one-hander of Ahn'Qiraj: an alternative for a Fire Mage once every raid counts
MARK_OF_FORDRING = 15411     # a neck several classes want in PvE, the Shaman among them
# The saved option of a player who counts the PvP rewards in the PvE lists, which leave them out until
# then: the examples above that are PvP rewards (the leggings, the Mageblade) need it.
WITH_PVP = "EasyBISDB = { pvpRewards = { pve = true } }"
EVERYTHING = phases.LATER


def default_filter(side="a", unsourced=False, seen_only=False, phase=phases.CURRENT, pvp=None) -> tuple:
    """The filter a character has until it changes an option or the phase. pvp: whether the PvP rewards
    count; None is each list's own answer (for_list)."""
    return (side, unsourced, seen_only, phase, pvp)


def for_list(flt: tuple, mode: str) -> tuple:
    """A filter as it applies to one list: until the player says otherwise the PvP list counts the PvP
    rewards and the PvE list leaves them out."""
    return flt if flt[4] is not None else (*flt[:4], ladders.PVP_REWARDS[mode], *flt[5:])


def toc_files() -> list[Path]:
    files = []
    for line in (ADDON / "EasyBIS.toc").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            files.append(ADDON / line.replace("\\", "/"))
    return files


def strip_colors(text: str) -> str:
    return re.sub(r"\|c[0-9a-fA-F]{8}|\|r", "", text)


def no_pictures(text: str) -> str:
    return re.sub(r"\|T[^|]*\|t\s*", "", text)


class Game:
    """The addon, loaded in a fresh Lua state as the game would load it."""

    def __init__(self, locale="enUS", faction="Alliance", cls="SHAMAN", login=True, saved=None):
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.stub = self.lua.execute((TESTS / "wowstub.lua").read_text(encoding="utf-8"))
        self.stub.locale, self.stub.faction, self.stub["class"] = locale, faction, cls
        if saved:
            self.lua.execute(saved)  # the saved variables, as the game restores them before the addon's files
        self.ns = self.lua.table()
        load = self.lua.eval(
            "function(source, name, addon, ns) local chunk = assert(load(source, name)); chunk(addon, ns) end")
        for path in toc_files():
            load(path.read_text(encoding="utf-8"), "@" + path.name, "EasyBIS", self.ns)
        self.stub.fire("ADDON_LOADED", "EasyBIS")
        if login:
            self.stub.fire("PLAYER_LOGIN")

    def slash(self, message: str) -> list[str]:
        self.stub.clearChat()
        self.lua.globals().SlashCmdList.EASYBIS(message)
        return [strip_colors(line) for line in self.stub.chat.values()]

    def tooltip(self, item_id: int) -> list[tuple]:
        lines = self.stub.showItem(item_id).lines
        return [tuple(strip_colors(text) for text in line.values()) for line in lines.values()]

    def lines(self, item_id: int) -> list[tuple[str, str]]:
        return [(strip_colors(line.left), strip_colors(line.right))
                for line in self.ns.Tooltip.BuildLines(item_id).values()]


@unittest.skipIf(lupa is None, "lupa is not installed")
class AddonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.kept = ladders.build_all(cls.db)

    # -- reference: what the generator's rules give ---------------------------------------

    def expected_picks(self, token, spec, mode, flt, count=ladders.ALTERNATIVES, full=False) -> dict:
        """count: the alternatives asked for. full: from the whole ladder, not the part the data files keep."""
        flt = for_list(flt, mode)
        side = flt[0]
        ladder = (lambda slot: ladders.full_ladder(self.db, token, spec, mode, slot)) if full \
            else self.kept[token][spec][mode].__getitem__
        visible = {slot: [e for e in ladder(slot) if e.passes(flt)] for slot, _ in ladders.SLOTS}
        two_hand = bool(visible["main"]) and not ladders.weapon_lists(visible["main"], visible["off"])[1] \
            and ladders.weapon_lists(visible["main"], visible["off"])[0][0].two_hand
        other_main, other_off = ladders.other_weapons(visible["main"], visible["off"])
        visible["main"], visible["off"] = ladders.weapon_lists(visible["main"], visible["off"])
        out = {"twoHand": two_hand, "ties": {}}
        for slot, entries in visible.items():
            best, alternatives = ladders.picks(slot, entries, count)
            out[slot] = ([e.shown(side) for e in best], [e.shown(side) for e in alternatives])
            # an alternative that scores exactly as a best pick is its equal; a placed one has no score of its own
            out["ties"][slot] = {e.shown(side) for e in alternatives
                                 if not e.placed and any(e.stored == b.stored for b in best)}
        shown = 1 + count
        out["other"] = {"main": [e.shown(side) for e in other_main[:shown]],
                        "off": [e.shown(side) for e in other_off[:shown]]}
        return out

    def expected_hits(self, flt) -> dict:
        hits = {}
        for token in CLASSES:
            for spec in self.kept[token]:
                for mode in ladders.MODES:
                    picks = self.expected_picks(token, spec, mode, flt)
                    for slot, _ in ladders.SLOTS:
                        best, alternatives = picks[slot]
                        for item_id in best:
                            hits.setdefault(item_id, set()).add((token, spec, mode, slot, True))
                        for item_id in alternatives:
                            hits.setdefault(item_id, set()).add(
                                (token, spec, mode, slot, item_id in picks["ties"][slot]))
                        for item_id in picks["other"].get(slot, []):
                            hits.setdefault(item_id, set()).add((token, spec, mode, slot, False))
        return hits

    # -- loading ------------------------------------------------------------------------------

    def test_toc_lists_existing_files(self):
        for path in toc_files():
            self.assertTrue(path.is_file(), f"{path.name} is in the toc but not on disk")
        listed = {path.name for path in toc_files()}
        on_disk = {path.name for path in ADDON.rglob("*.lua") if "_build" not in path.parts}
        self.assertEqual(listed, on_disk, "the toc and the Lua files on disk differ")

    def test_textures_the_game_can_read(self):
        # Every picture of the addon's folder named by the toc or the Lua files, and nothing more in Media.
        named = set()
        texts = [(ADDON / "EasyBIS.toc").read_text(encoding="utf-8")]
        texts += [path.read_text(encoding="utf-8") for path in toc_files()]
        for text in texts:
            for found in re.findall(r"Interface\\+AddOns\\+EasyBIS\\+([\w\\]+\.tga)", text):
                named.add(re.sub(r"\\+", "/", found))
        self.assertTrue({"Media/Logo.tga", "Media/Icon.tga", "Media/Portrait.tga"} <= named)
        self.assertEqual(named, {f"Media/{path.name}" for path in (ADDON / "Media").iterdir()})
        for name in named:
            header = (ADDON / name).read_bytes()[:18]
            width, height = int.from_bytes(header[12:14], "little"), int.from_bytes(header[14:16], "little")
            self.assertEqual(header[2], 2, f"{name}: not an uncompressed true-colour TGA")
            self.assertEqual((header[16], header[17] & 0x0F), (32, 8), f"{name}: not 32 bits with alpha")
            for side in (width, height):
                self.assertTrue(side >= 8 and side & (side - 1) == 0, f"{name}: a side is not a power of two")

    def test_saved_options_get_their_defaults(self):
        game = Game()
        saved = game.lua.globals().EasyBISDB
        self.assertTrue(saved.tooltip)
        self.assertFalse(saved.unsourced)
        self.assertTrue(saved.lists.pve and saved.lists.pvp)
        self.assertEqual(game.ns.data.meta.level, 60)

    def test_saved_options_are_kept(self):
        game = Game(saved="EasyBISDB = { tooltip = false, lists = { pvp = false } }")
        self.assertFalse(game.ns.db.tooltip, "a saved choice was overwritten by the default")
        self.assertFalse(game.ns.db.lists.pvp, "a saved choice was overwritten by the default")
        self.assertTrue(game.ns.db.lists.pve, "a missing option did not get its default")
        self.assertTrue(game.ns.db.alternatives, "a missing option did not get its default")
        self.assertEqual(game.tooltip(EYE_OF_REND), [], "tooltips were switched off in the saved options")

    # -- the lists ----------------------------------------------------------------------------

    def test_lua_makes_the_generators_picks(self):
        """Every class, spec, list, slot and filter: same best picks and alternatives as ladders.py."""
        game = Game()
        compute, decode = game.ns.Ladders.Compute, game.ns.Ladders.Decode
        decoded = {token: decode(token) for token in CLASSES}
        checked = 0
        for flt in ladders.FILTERS:
            lua_filter = game.lua.table(side=flt[0], unsourced=flt[1], seenOnly=flt[2], phase=flt[3],
                                        pvpRewards=flt[4], rankCap=flt[5])
            for token in CLASSES:
                for spec in self.kept[token]:
                    for mode in ladders.MODES:
                        expected = self.expected_picks(token, spec, mode, flt)
                        result = compute(decoded[token], spec, mode, lua_filter)
                        self.assertEqual(bool(result.twoHand), expected["twoHand"], f"{token} {spec} {mode} {flt}")
                        for slot, _ in ladders.SLOTS:
                            got = ([pick.id for pick in result[slot].best.values()],
                                   [pick.id for pick in result[slot].alts.values()])
                            self.assertEqual(got, expected[slot], f"{token} {spec} {mode} {slot} {flt}")
                            other = [pick.id for pick in result[slot].other.values()]
                            self.assertEqual(other, expected["other"].get(slot, []),
                                             f"{token} {spec} {mode} {slot} {flt}: the other weapon style")
                            checked += 1
        self.assertEqual(checked, len(ladders.FILTERS) * 27 * 2 * 15)
        self.assertEqual(len(ladders.FILTERS), 2 * 2 * 2 * len(phases.PHASES) * 2 * len(ladders.RANK_CAPS))
        # a filter that does not say counts the PvP rewards, as the lists did before the option
        silent = game.lua.table(side="a", unsourced=False, seenOnly=False, phase=phases.CURRENT)
        head = compute(decoded["WARRIOR"], 3, "pve", silent).head
        self.assertEqual([pick.id for pick in head.best.values()],
                         self.expected_picks("WARRIOR", 3, "pve", default_filter(pvp=True))["head"][0])

    def test_the_rank_cap_rises_at_every_weekly_reset(self):
        """A realm in America resets on Tuesdays, one in Europe on Wednesdays: both count their own resets."""
        game = Game()
        self.assertEqual(game.ns.data.meta.seasonStart, ranks.SEASON_START)
        self.assertEqual(list(game.ns.data.meta.rankCaps.values()), list(ranks.WEEKLY_CAPS))
        week = 7 * 24 * 60 * 60
        launch = ranks.SEASON_START
        for first_reset in (1794322800, 1794369600):  # 2026-11-10 15:00 UTC, 2026-11-11 04:00 UTC
            for now, next_reset, expected_week in (
                    (launch + 60, first_reset, 1),
                    (first_reset - 1, first_reset, 1),
                    (first_reset, first_reset + week, 2),
                    (first_reset + week - 1, first_reset + week, 2),
                    (first_reset + week, first_reset + 2 * week, 3),
                    (first_reset + 8 * week, first_reset + 9 * week, 10),
                    (first_reset + 30 * week, first_reset + 31 * week, 32)):
                game.stub.serverTime, game.stub.untilReset = now, next_reset - now
                self.assertEqual(game.ns.SeasonWeek(), expected_week, f"{now}")
                self.assertEqual(game.ns.RankCap(), ranks.WEEKLY_CAPS[min(expected_week, 10) - 1], f"{now}")
        # a client that does not say when the reset is: the weeks count from the launch
        game.stub.untilReset = None
        for now, expected_week in ((launch, 1), (launch + week - 1, 1), (launch + week, 2)):
            game.stub.serverTime = now
            self.assertEqual(game.ns.SeasonWeek(), expected_week)

    def test_the_rank_cap_option_narrows_the_lists(self):
        game = Game()
        self.assertIsNone(game.ns.Filter().rankCap, "the lists follow the cap only when asked")
        before = game.ns.Ladders.For("PRIEST", 3, "pvp").head.best[1].id
        self.assertEqual(before, 17602, "Field Marshal's Headdress, which no vendor sells")
        self.assertEqual(game.slash("now"), ["Easy BIS: Available now: on."])
        self.assertEqual(game.ns.Filter().rankCap, 6)
        flt = ("a", False, False, phases.CURRENT, True, 6)
        decoded = game.ns.Ladders.Decode("PRIEST")
        for spec in self.kept["PRIEST"]:
            result = game.ns.Ladders.Compute(decoded, spec, "pvp", game.ns.Filter())
            expected = self.expected_picks("PRIEST", spec, "pvp", flt, full=True)
            for slot, _ in ladders.SLOTS:
                picks = [*result[slot].best.values(), *result[slot].alts.values()]
                self.assertEqual([pick.id for pick in picks], expected[slot][0] + expected[slot][1], slot)
                self.assertTrue(all(pick.entry.rank <= 6 for pick in picks), slot)
        head = game.ns.Ladders.For("PRIEST", 3, "pvp").head.best[1]
        self.assertEqual(self.db.items[head.id]["name"], "Premier Satin Cowl", "sold for honor, with no rank")
        self.assertEqual(game.ns.Sources.Describe(head.id).detail, "Honor")
        self.assertEqual(game.slash("now"), ["Easy BIS: Available now: off."])
        self.assertEqual(game.ns.Ladders.For("PRIEST", 3, "pvp").head.best[1].id, before)

    def test_available_now_overrules_the_other_choices(self):
        """The week's rank cap, the game's phase and no unknown source, and the player's own choices come back."""
        game = Game(saved="EasyBISDB = { unsourced = true, availableNow = true }; EasyBISCharDB = { phase = 9 }")
        flt = game.ns.Filter()
        self.assertEqual((flt.rankCap, flt.phase, flt.unsourced), (6, phases.CURRENT, False))
        self.assertEqual(game.ns.Phase(), phases.CURRENT)
        game.ns.SetOption(game.ns, "availableNow", False)
        flt = game.ns.Filter()
        self.assertEqual((flt.rankCap, flt.phase, flt.unsourced), (None, EVERYTHING, True))

    def test_a_slot_lists_as_many_alternatives_as_asked(self):
        """From two to six alternatives: the picks the whole ladder gives, which the kept part must hold."""
        game = Game()
        compute, decode = game.ns.Ladders.Compute, game.ns.Ladders.Decode
        self.assertEqual((game.ns.ALTERNATIVES, game.ns.MaxAlternatives()),
                         (ladders.ALTERNATIVES, ladders.MAX_ALTERNATIVES))
        self.assertEqual(game.ns.data.meta.alternatives, ladders.MAX_ALTERNATIVES)
        longest = 0
        for flt in (default_filter(pvp=False), default_filter("h", True, False, EVERYTHING, True)):
            for count in range(ladders.ALTERNATIVES, ladders.MAX_ALTERNATIVES + 1):
                lua_filter = game.lua.table(side=flt[0], unsourced=flt[1], seenOnly=flt[2], phase=flt[3],
                                            pvpRewards=flt[4], alternatives=count)
                for token in CLASSES:
                    decoded = decode(token)
                    for spec in self.kept[token]:
                        for mode in ladders.MODES:
                            expected = self.expected_picks(token, spec, mode, flt, count, full=True)
                            result = compute(decoded, spec, mode, lua_filter)
                            for slot, _ in ladders.SLOTS:
                                got = ([pick.id for pick in result[slot].best.values()],
                                       [pick.id for pick in result[slot].alts.values()])
                                self.assertEqual(got, expected[slot], f"{token} {spec} {mode} {slot} {flt} {count}")
                                self.assertEqual([pick.id for pick in result[slot].other.values()],
                                                 expected["other"].get(slot, []), f"{token} {spec} {mode} {slot}")
                                longest = max(longest, len(got[1]))
        self.assertEqual(longest, ladders.MAX_ALTERNATIVES)

        # the character's own number: two until it asks for more, kept between two and what the data holds
        self.assertEqual(game.ns.Alternatives(), 2)
        head = lambda: [pick.id for pick in game.ns.Ladders.For("SHAMAN", 2, "pve").head.alts.values()]  # noqa: E731
        self.assertEqual(head(), self.expected_picks("SHAMAN", 2, "pve", default_filter())["head"][1])
        self.assertEqual(game.slash("alternatives 4"), ["Easy BIS: Alternatives per slot: 4."])
        self.assertEqual((game.ns.Alternatives(), game.ns.db.altCount, game.ns.Filter().alternatives), (4, 4, 4))
        self.assertEqual(head(), self.expected_picks("SHAMAN", 2, "pve", default_filter(), 4)["head"][1])
        self.assertEqual(len(head()), 4)
        self.assertEqual(game.slash("alternatives 40"), ["Easy BIS: Alternatives per slot: 6."])
        self.assertEqual(game.slash("alternatives 0"), ["Easy BIS: Alternatives per slot: 2."])
        self.assertEqual(game.slash("alternatives"), ["Easy BIS: Alternatives per slot: 2."])
        self.assertTrue(any("/easybis alternatives" in line for line in game.slash("help")))
        # the tooltips follow: the fourth alternative of a slot is wanted once it is listed
        fourth = self.expected_picks("SHAMAN", 2, "pve", default_filter(), 4)["head"][1][3]
        wanted = lambda: {(hit["class"], hit.spec, hit.list, hit.slot)   # noqa: E731
                          for hit in (game.ns.Index.ForItem(fourth) or game.lua.table()).values()}
        self.assertNotIn(("SHAMAN", 2, "pve", "head"), wanted())
        game.ns.SetAlternatives(game.ns, 4)
        self.assertIn(("SHAMAN", 2, "pve", "head"), wanted())
        # a saved number the data no longer holds, or something that is no number
        game.ns.db.altCount = 12
        self.assertEqual(game.ns.Alternatives(), 6)
        game.ns.db.altCount = "many"
        self.assertEqual(game.ns.Alternatives(), 2)

    def test_specs_are_listed_in_order(self):
        game = Game()
        specs = [(spec.index, spec.name, spec.style) for spec in game.ns.Ladders.Specs("SHAMAN").values()]
        self.assertEqual(specs, [(1, "Elemental", "any"), (2, "Enhancement", "2h"), (3, "Restoration", "any")])

    def test_a_faction_sees_its_own_items(self):
        alliance = Game(faction="Alliance", saved=WITH_PVP).ns.Ladders.For("SHAMAN", 2, "pve")
        horde = Game(faction="Horde", saved=WITH_PVP).ns.Ladders.For("SHAMAN", 2, "pve")
        self.assertEqual(alliance.legs.best[1].id, SENTINELS_LEGGINGS)
        self.assertEqual(horde.legs.best[1].id, OUTRIDERS_LEGGINGS)
        self.assertEqual(alliance.head.best[1].id, EYE_OF_REND)
        self.assertEqual(horde.head.best[1].id, EYE_OF_REND)
        self.assertTrue(alliance.twoHand)
        self.assertEqual(len(alliance.off.best), 0)

    def test_the_player_picks_the_faction_of_the_lists(self):
        """The character's faction until the player picks the other one: the lists, the tooltips and the
        reputations follow; the choice is the character's, and picking its own faction goes back to following it."""
        game = Game(faction="Alliance", saved=WITH_PVP)
        ns = game.ns
        legs = lambda: ns.Ladders.For("SHAMAN", 2, "pve").legs.best[1].id
        self.assertEqual((ns.CharacterSide(), ns.PlayerSide(), legs()), ("a", "a", SENTINELS_LEGGINGS))
        self.assertTrue(game.lines(SENTINELS_LEGGINGS))
        self.assertFalse(game.lines(OUTRIDERS_LEGGINGS), "the Horde's twin is nobody's on the Alliance")
        seen = []
        ns.On(ns, "OPTION_CHANGED", lambda key, value: seen.append((key, value)))
        stormpike = game.lua.table_from({"factionID": 730, "standing": 4})
        self.assertEqual(ns.Reputation.Status(stormpike), "missing")

        ns.SetSide(ns, "h")
        self.assertEqual((ns.CharacterSide(), ns.PlayerSide(), ns.char.side), ("a", "h", "h"))
        self.assertEqual(seen, [("side", "h")])
        self.assertEqual(legs(), OUTRIDERS_LEGGINGS)
        self.assertTrue(game.lines(OUTRIDERS_LEGGINGS))
        self.assertFalse(game.lines(SENTINELS_LEGGINGS))
        self.assertEqual(ns.Reputation.Status(stormpike), "missing", "the character's own faction, whatever lists it reads")
        defilers = game.lua.table_from({"factionID": 510, "standing": 4})
        self.assertEqual(ns.Reputation.Status(defilers), "other", "the Horde's lists: the character earns none of it")
        self.assertEqual(ns.Ladders.For("SHAMAN", 2, "pve").head.best[1].id, EYE_OF_REND, "a piece for both")
        ns.SetSide(ns, "h")
        self.assertEqual(len(seen), 1, "nothing changed: nothing said")

        ns.SetSide(ns, "a")   # the character's own: back to following it
        self.assertIsNone(ns.char.side)
        self.assertEqual(seen[-1], ("side", "a"))
        self.assertEqual(legs(), SENTINELS_LEGGINGS)
        ns.SetSide(ns, "x")
        self.assertEqual((ns.char.side, len(seen)), (None, 2))

        # kept per character
        saved = Game(faction="Alliance", saved=WITH_PVP + " EasyBISCharDB = { side = 'h' }")
        self.assertEqual(saved.ns.PlayerSide(), "h")
        self.assertEqual(saved.ns.Ladders.For("SHAMAN", 2, "pve").legs.best[1].id, OUTRIDERS_LEGGINGS)
        horde = Game(faction="Horde", saved=WITH_PVP)
        horde.ns.SetSide(horde.ns, "a")
        self.assertEqual((horde.ns.CharacterSide(), horde.ns.PlayerSide()), ("h", "a"))
        self.assertEqual(horde.ns.Ladders.For("SHAMAN", 2, "pve").legs.best[1].id, SENTINELS_LEGGINGS)

    def test_faction_command(self):
        game = Game(faction="Alliance")
        self.assertEqual(game.slash("faction"), ["Easy BIS: Lists for: Alliance."])
        self.assertEqual(game.slash("faction horde"),
                         ["Easy BIS: Lists for: Horde. Not your character's faction: /easybis faction auto goes back to it."])
        self.assertEqual(game.ns.PlayerSide(), "h")
        self.assertEqual(game.slash("faction a"), ["Easy BIS: Lists for: Alliance."])
        self.assertIsNone(game.ns.char.side)
        game.slash("faction h")
        self.assertEqual(game.slash("faction auto"), ["Easy BIS: Lists for: Alliance."])
        self.assertEqual(game.slash("faction elves"), ["Easy BIS: Lists for: Alliance."], "an unknown word changes nothing")
        self.assertTrue(any("/easybis faction" in line for line in game.slash("help")))
        french = Game(locale="frFR", faction="Horde")
        self.assertEqual(french.slash("faction alliance"),
                         ["Easy BIS: Listes pour : Alliance. Ce n'est pas la faction de votre personnage : "
                          "/easybis faction auto y revient."])

    def test_options_change_the_lists(self):
        # The best PvP head of an Alliance Enhancement Shaman who counts the PvP rewards has no known source;
        # the next one is crafted.
        game = Game(saved=WITH_PVP)
        before = game.ns.Ladders.For("SHAMAN", 2, "pvp").head.best[1].id
        self.assertEqual(before, self.expected_picks("SHAMAN", 2, "pvp", default_filter(pvp=True))["head"][0][0])
        game.ns.SetOption(game.ns, "unsourced", True)
        after = game.ns.Ladders.For("SHAMAN", 2, "pvp").head.best[1].id
        self.assertNotEqual(before, after, "counting items with no known source did not change the head pick")
        self.assertEqual(after, self.expected_picks("SHAMAN", 2, "pvp",
                                                    default_filter(unsourced=True, pvp=True))["head"][0][0])
        game.ns.SetOption(game.ns, "unsourced", False)
        self.assertEqual(game.ns.Ladders.For("SHAMAN", 2, "pvp").head.best[1].id, before)

    def test_each_list_counts_the_pvp_rewards_or_not(self):
        # The PvP list counts them and the PvE list leaves them out, until the player says otherwise for
        # that list. The example: the best head of an Alliance Protection Warrior is a rank 13 reward in
        # both lists.
        game = Game(cls="WARRIOR")
        self.assertEqual(dict(game.ns.db.pvpRewards), ladders.PVP_REWARDS)
        self.assertEqual(dict(game.ns.Filter().pvpRewards), {"pve": False, "pvp": True})
        self.assertEqual((game.ns.PvPRewards(game.ns, "pve"), game.ns.PvPRewards(game.ns, "pvp")), (False, True))
        lists = game.ns.Ladders.Decode("WARRIOR").lists[3]
        flags = {mode: {entry.id: entry.flags for entries in lists[mode].values() for entry in entries.values()}
                 for mode in ladders.MODES}
        with_them, without = default_filter(pvp=True), default_filter(pvp=False)

        def picks(mode):
            result = game.ns.Ladders.For("WARRIOR", 3, mode)
            return {slot: [pick.id for kind in ("best", "alts", "other") for pick in result[slot][kind].values()]
                    for slot, _ in ladders.SLOTS}

        def check(mode, flt):
            shown, expected = picks(mode), self.expected_picks("WARRIOR", 3, mode, flt)
            for slot, _ in ladders.SLOTS:
                self.assertEqual(shown[slot][:len(expected[slot][0])], expected[slot][0], f"{mode} {slot} {flt}")
                rewards = [item_id for item_id in shown[slot] if "p" in flags[mode][item_id]]
                self.assertEqual(bool(rewards) and not flt[4], False, f"{mode} {slot}: a PvP reward is listed")
            return shown

        wanted = lambda item: {(hit["class"], hit.spec, hit.list)   # noqa: E731
                               for hit in (game.ns.Index.ForItem(item) or game.lua.table()).values()}
        in_pve, in_pvp = check("pve", without), check("pvp", with_them)
        rank_13 = in_pvp["head"][0]
        self.assertIn("p", flags["pvp"][rank_13], "the best PvP head is no PvP reward: this test needs another spec")
        self.assertEqual(wanted(rank_13) & {("WARRIOR", 3, "pve"), ("WARRIOR", 3, "pvp")}, {("WARRIOR", 3, "pvp")})

        # the PvE list counts them: its best head is that helm too; the PvP list has not moved
        game.ns.SetPvPRewards(game.ns, "pve", True)
        self.assertEqual(check("pve", with_them)["head"][0], rank_13)
        self.assertEqual(picks("pvp"), in_pvp)
        self.assertLessEqual({("WARRIOR", 3, "pve"), ("WARRIOR", 3, "pvp")}, wanted(rank_13))
        # the PvP list leaves them out: what is best for PvP without the honor system; the PvE list has not moved
        counted = picks("pve")
        game.ns.SetPvPRewards(game.ns, "pvp", False)
        self.assertNotEqual(check("pvp", without)["head"][0], rank_13)
        self.assertEqual(picks("pve"), counted)
        self.assertEqual(wanted(rank_13) & {("WARRIOR", 3, "pve"), ("WARRIOR", 3, "pvp")}, {("WARRIOR", 3, "pve")})
        self.assertEqual(dict(game.lua.globals().EasyBISDB.pvpRewards), {"pve": True, "pvp": False}, "not saved")
        game.ns.SetPvPRewards(game.ns, "pve", False)
        game.ns.SetPvPRewards(game.ns, "pvp", True)
        self.assertEqual((picks("pve"), picks("pvp")), (in_pve, in_pvp))
        game.ns.SetPvPRewards(game.ns, "raid", True)   # no such list
        self.assertIsNone(game.ns.db.pvpRewards.raid)

        # saved: one list's answer, the other keeps its own; version 1.1.0's single answer was the PvE list's
        saved = Game(saved="EasyBISDB = { pvpRewards = { pvp = false } }")
        self.assertEqual(dict(saved.ns.db.pvpRewards), {"pve": False, "pvp": False})
        old = Game(saved="EasyBISDB = { pvpRewards = true }")
        self.assertEqual(dict(old.ns.db.pvpRewards), {"pve": True, "pvp": True})
        self.assertEqual(dict(Game(saved="EasyBISDB = { pvpRewards = false }").ns.db.pvpRewards), ladders.PVP_REWARDS)

    # -- phases -------------------------------------------------------------------------------

    def test_phase_follows_the_game_until_the_character_picks_one(self):
        game = Game()
        self.assertEqual(list(game.ns.data.meta.phases.values()), list(phases.PHASES))
        self.assertEqual(game.ns.Phase(), phases.CURRENT)
        self.assertEqual(game.ns.Filter().phase, phases.CURRENT)
        self.assertIsNone(game.lua.globals().EasyBISCharDB.phase)

        game.ns.SetPhase(game.ns, EVERYTHING)
        self.assertEqual(game.ns.Phase(), EVERYTHING)
        self.assertEqual(game.lua.globals().EasyBISCharDB.phase, EVERYTHING, "the phase is not saved")
        game.ns.SetPhase(game.ns, 4)   # not a phase of the data
        self.assertEqual(game.ns.Phase(), EVERYTHING)

        self.assertEqual(Game(saved="EasyBISCharDB = { phase = 1 }").ns.Phase(), 1)
        self.assertEqual(Game(saved="EasyBISCharDB = { phase = 4 }").ns.Phase(), phases.CURRENT,
                         "a saved phase the data no longer has should fall back to the game's")

    def test_phase_changes_the_lists_and_the_tooltips(self):
        # The example: a Fire Mage wears a one-hander before the raids, and Atiesh once every raid counts.
        # The generator says whether the data still tells that story; the ids only name it.
        example = "the lists changed: this test needs another example"
        early = self.expected_picks("MAGE", 2, "pve", default_filter(pvp=True))
        late = self.expected_picks("MAGE", 2, "pve", default_filter(phase=EVERYTHING, pvp=True))
        self.assertEqual((early["twoHand"], early["main"][0]), (False, [MAGEBLADE]), example)
        self.assertEqual((late["twoHand"], late["main"][0]), (True, [ATIESH]), example)
        self.assertEqual(set(late["other"]["main"][:2]), {MAGEBLADE, VAULTED_SECRETS}, example)

        game = Game(cls="MAGE", saved=WITH_PVP)
        before = game.ns.Ladders.For("MAGE", 2, "pve")
        self.assertFalse(before.twoHand)
        self.assertEqual(before.main.best[1].id, MAGEBLADE)
        self.assertEqual(game.lines(ATIESH), [], "a Naxxramas reward is wanted before the raids")
        mage = [right for left, right in game.lines(MAGEBLADE) if "Mage" in left]
        self.assertTrue(mage and "BIS" in mage[0])

        game.ns.SetPhase(game.ns, EVERYTHING)
        after = game.ns.Ladders.For("MAGE", 2, "pve")
        self.assertTrue(after.twoHand)
        self.assertEqual(after.main.best[1].id, ATIESH)
        self.assertEqual([pick.id for pick in after.main.other.values()], late["other"]["main"],
                         "the best one-handers are still offered")
        self.assertTrue(after.off.other[1], "and so is an off hand to go with them")
        self.assertEqual(len(after.off.best), 0)
        mage = [right for left, right in game.lines(ATIESH) if "Mage" in left]
        self.assertTrue(mage and "BIS" in mage[0])
        for one_hander in (VAULTED_SECRETS, MAGEBLADE):
            mage = [right for left, right in game.lines(one_hander) if "Mage" in left]
            self.assertTrue(mage and all("Alt" in right and "BIS" not in right for right in mage),
                            "a one-hander behind a two-hander is an alternative")

        game.ns.SetPhase(game.ns, phases.PRE_RAID)
        self.assertEqual(game.ns.Ladders.For("MAGE", 2, "pve").main.best[1].id, MAGEBLADE)
        self.assertEqual(game.lines(ATIESH), [])

    def test_phase_command(self):
        game = Game()
        self.assertEqual(game.slash("phase"), ["Easy BIS: Lists up to: Pre-raid."])
        self.assertEqual(game.slash("phase 1"), ["Easy BIS: Lists up to: Phase 1."])
        self.assertEqual(game.ns.Phase(), 1)
        self.assertEqual(game.slash("phase all"), ["Easy BIS: Lists up to: Everything."])
        self.assertEqual(game.ns.Phase(), EVERYTHING)
        self.assertEqual(game.slash("phase 7"), ["Easy BIS: Lists up to: Everything."])
        self.assertEqual(game.slash("phase 0"), ["Easy BIS: Lists up to: Pre-raid."])
        self.assertTrue(any("/easybis phase" in line for line in game.slash("help")))

    # -- the index and the tooltip ----------------------------------------------------------

    def test_index_knows_who_wants_every_item(self):
        for faction, side in (("Alliance", "a"), ("Horde", "h")):
            for unsourced in (False, True):
                game = Game(faction=faction)
                game.ns.SetOption(game.ns, "unsourced", unsourced)
                expected = self.expected_hits(default_filter(side, unsourced))
                for item_id, wanted in expected.items():
                    hits = game.ns.Index.ForItem(item_id)
                    self.assertIsNotNone(hits, f"{item_id} is in a list but not in the index")
                    got = {(hit["class"], hit.spec, hit.list, hit.slot, bool(hit.bis)) for hit in hits.values()}
                    self.assertEqual(got, wanted, f"item {item_id}, {faction}, unsourced={unsourced}")
                self.assertIsNone(game.ns.Index.ForItem(1), "an item in no list has hits")

    def test_index_warms_up_after_login(self):
        game = Game()
        self.assertGreaterEqual(game.stub.runTimers(), 1, "login did not schedule the warm-up")
        ran = 1
        while game.stub.runTimers():
            ran += 1
        self.assertEqual(ran, len(CLASSES) + 1, "the warm-up should read one class per frame, then stop")
        self.assertIsNotNone(game.ns.Index.ForItem(EYE_OF_REND))

    def test_tooltip_lines(self):
        game = Game()
        lines = game.lines(EYE_OF_REND)
        shaman = [line for line in lines if "Shaman" in line[0]]
        self.assertEqual(shaman, [("<classicon-shaman> Shaman Enhancement", "BIS PvE")])
        # the same answer as the generator, class by class
        wanted = {hit[0] for hit in self.expected_hits(default_filter())[EYE_OF_REND]}
        self.assertEqual({line[0].split()[1] for line in lines}, {token.capitalize() for token in wanted})

    def test_tooltip_gets_the_lines(self):
        game = Game()
        tooltip = game.tooltip(EYE_OF_REND)
        self.assertEqual(tooltip[0], (" ",))
        self.assertEqual(tooltip[1], ("Easy BIS",))
        self.assertIn(("<classicon-shaman> Shaman Enhancement", "BIS PvE"), tooltip[2:])
        self.assertEqual(game.tooltip(1), [], "an item nobody wants got lines")

        game.ns.SetOption(game.ns, "tooltip", False)
        self.assertEqual(game.tooltip(EYE_OF_REND), [])

    def test_tooltip_options(self):
        game = Game(cls="SHAMAN")
        everyone = game.lines(MARK_OF_FORDRING)
        game.ns.SetOption(game.ns, "onlyMyClass", True)
        mine = game.lines(MARK_OF_FORDRING)
        self.assertTrue(all("Shaman" in left for left, _ in mine))
        self.assertLess(len(mine), len(everyone))

        game.ns.SetOption(game.ns, "onlyMyClass", False)
        game.ns.SetOption(game.ns, "alternatives", False)
        for _, right in game.lines(EYE_OF_REND):
            self.assertNotIn("Alt", right)

    def test_whole_class_line_drops_the_spec_names(self):
        """When every spec of a class has the same status, the line names the class alone."""
        game = Game()
        hits = self.expected_hits(default_filter())
        found = None
        for item_id, wanted in hits.items():
            per_class = {}
            for token, spec, mode, _, bis in wanted:
                per_class.setdefault(token, {}).setdefault(spec, {})
                per_class[token][spec][mode] = per_class[token][spec].get(mode, False) or bis
            for token, specs in per_class.items():
                if len(specs) == 3 and len({tuple(sorted(status.items())) for status in specs.values()}) == 1:
                    found = (item_id, token)
                    break
            if found:
                break
        self.assertIsNotNone(found, "no item is wanted the same way by every spec of a class")
        item_id, token = found
        lefts = [left for left, _ in game.lines(item_id) if token.capitalize() in left]
        self.assertEqual(lefts, [f"<classicon-{token.lower()}> {token.capitalize()}"])

    # -- items added by hand ------------------------------------------------------------------

    def test_items_added_by_hand(self):
        crown, blade, dagger, potion = 990001, 990002, 990003, 990004
        game = Game()
        custom, stub = game.ns.Custom, game.stub
        stub.equipLocs[crown], stub.itemNames[crown] = "INVTYPE_HEAD", "Crown of Tests"
        stub.equipLocs[blade], stub.equipLocs[dagger], stub.equipLocs[potion] = "INVTYPE_WEAPON", "INVTYPE_WEAPON", ""
        stub.equipLocs[EYE_OF_REND] = "INVTYPE_HEAD"

        self.assertEqual(custom.Add("SHAMAN", 2, "pve", crown), "head")
        self.assertEqual(list(custom.List("SHAMAN", 2, "pve", "head").values()), [crown])
        self.assertEqual(game.lua.globals().EasyBISDB.custom["SHAMAN:2:pve"].head[1], crown, "it is not saved")
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", crown), (None, "duplicate"))
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", potion), (None, "notGear"))
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", 424242), (None, "unknown"))
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", EYE_OF_REND), (None, "listed"), "the data already picks it")
        self.assertEqual(custom.Add("MAGE", 1, "pve", EYE_OF_REND), "head", "another spec may still add it")
        # a one-handed weapon: the main hand, or the off hand when asked
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", blade), "main")
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", dagger, "off"), "off")
        self.assertEqual(custom.Add("SHAMAN", 2, "pve", crown + 100, "off"), (None, "unknown"))

        # tooltips name the spec; an item the data also picks keeps the data's word
        self.assertEqual(game.lines(crown), [("<classicon-shaman> Shaman Enhancement", "Added PvE")])
        self.assertIn(("<classicon-mage> Mage Arcane", "Added PvE"), game.lines(EYE_OF_REND))
        self.assertIn(("<classicon-shaman> Shaman Enhancement", "BIS PvE"), game.lines(EYE_OF_REND))
        game.ns.SetOption(game.ns, "alternatives", False)
        self.assertEqual(len(game.lines(crown)), 1, "an added item is not an alternative to hide")

        self.assertTrue(custom.Remove("SHAMAN", 2, "pve", crown))
        self.assertFalse(custom.Remove("SHAMAN", 2, "pve", crown))
        self.assertEqual(game.lines(crown), [])
        self.assertEqual(list(custom.List("SHAMAN", 2, "pve", "head").values()), [])

        # reading what the player gives: a link, an ID, a name the game knows
        self.assertEqual(custom.Read("|cffa335ee|Hitem:12587::::::::60|h[Eye of Rend]|h|r"), 12587)
        self.assertEqual(custom.Read(" 456 "), 456)
        self.assertEqual(custom.Read("Crown of Tests"), crown)
        self.assertIsNone(custom.Read("no such thing"))
        self.assertIsNone(custom.Read(""))

    def test_added_items_are_saved_and_survive_bad_data(self):
        game = Game(saved="EasyBISDB = { custom = { ['SHAMAN:2:pvp'] = { head = { 990001, 'x' }, legs = 7 }, "
                          "['DEATHKNIGHT:1:pve'] = { head = { 990001 } }, junk = true } }")
        self.assertEqual(game.lines(990001), [("<classicon-shaman> Shaman Enhancement", "Added PvP")])
        broken = Game(saved="EasyBISDB = { custom = 'oops' }")
        self.assertEqual(broken.lines(990001), [])
        broken.stub.equipLocs[990001] = "INVTYPE_HEAD"
        self.assertEqual(broken.ns.Custom.Add("SHAMAN", 1, "pve", 990001), "head")

    def test_add_and_remove_commands(self):
        blade = 990002
        game = Game()
        game.stub.equipLocs[blade], game.stub.itemNames[blade] = "INVTYPE_WEAPON", "Blade of Tests"
        chat = game.slash(f"add {blade}")
        self.assertEqual(len(chat), 1)
        self.assertIn("[Blade of Tests]", chat[0])
        self.assertIn("added to Shaman Elemental, PvE (Main hand).", chat[0], "the list the window would show")
        self.assertIn("is already in this list", game.slash(f"add {blade}")[0])
        self.assertIn("removed from Shaman Elemental, PvE.", game.slash(f"remove |Hitem:{blade}|h[Blade of Tests]|h")[0])
        self.assertIn("was not added by hand", game.slash(f"remove {blade}")[0])
        self.assertIn("(Off hand)", game.slash(f"add {blade} off")[0])
        self.assertIn("No such item", game.slash("add 424242")[0])
        self.assertIn("/easybis add", game.slash("add")[0])
        self.assertIn("/easybis remove", game.slash("remove")[0])
        # the list the window shows, once it has been opened on another spec
        rogue = Game(saved="EasyBISCharDB = { class = 'ROGUE', spec = 2, list = 'pvp' }")
        rogue.stub.equipLocs[blade] = "INVTYPE_WEAPON"
        self.assertIn("added to Rogue Combat, PvP", rogue.slash(f"add {blade}")[0])
        self.assertTrue(any("/easybis add" in line for line in game.slash("help")))

    def test_ties_exist_and_read_as_best(self):
        """An alternative that scores exactly as a best pick is BIS in the index (the tooltips read it)."""
        ties = [(token, spec, slot, item_id)
                for token in CLASSES for spec in self.kept[token]
                for slot, ids in self.expected_picks(token, spec, "pve", default_filter())["ties"].items()
                for item_id in ids]
        self.assertTrue(ties, "no tie in the PvE lists: the tie rule is not exercised")
        game = Game()
        token, spec, slot, item_id = ties[0]
        hits = [hit for hit in game.ns.Index.ForItem(item_id).values()
                if (hit["class"], hit.spec, hit.list, hit.slot) == (token, spec, "pve", slot)]
        self.assertTrue(hits and all(hit.bis for hit in hits))

    # -- languages ----------------------------------------------------------------------------

    def test_french(self):
        game = Game(locale="frFR")
        self.assertEqual(game.ns.SpecName("Enhancement"), "Amélioration")
        self.assertEqual(game.ns.L.LIST_PVE, "JcE")
        self.assertEqual(game.ns.SlotName("head"), "Tête")
        self.assertIn(("<classicon-shaman> Shaman Amélioration", "BIS JcE"), game.lines(EYE_OF_REND))

    def test_unknown_language_falls_back_to_english(self):
        game = Game(locale="deDE")
        self.assertEqual(game.ns.L.LIST_PVE, "PvE")
        self.assertEqual(game.ns.SpecName("Enhancement"), "Enhancement")

    def test_translations_match_the_english_texts(self):
        game = Game()
        english = dict(game.ns.locales.enUS.items())
        french = dict(game.ns.locales.frFR.items())
        self.assertFalse(set(french) - set(english), "French has keys English lacks")
        untranslated = set(english) - set(french) - {"ADDON_TITLE", "RANK_BIS", "RANK_ALT"}
        self.assertFalse(untranslated, "texts with no French translation")
        for key, text in french.items():
            self.assertEqual(re.findall(r"%[sd]", text), re.findall(r"%[sd]", english[key]), key)

    def test_every_profession_has_a_french_name(self):
        game = Game()
        french = dict(game.ns.localeProfessions.frFR.items())
        used = {source[1] for item in self.db.items.values() for source in item["sources"] if source[0] == "c"}
        self.assertFalse(used - set(french), "professions with no French name")

    def test_every_spec_has_a_french_name(self):
        game = Game()
        french = dict(game.ns.localeSpecs.frFR.items())
        for token, data in self.db.classes.items():
            for spec in data["specs"].values():
                self.assertIn(spec["name"], french, f"{token} {spec['name']}")

    # -- commands -----------------------------------------------------------------------------

    def test_help(self):
        chat = Game().slash("help")
        self.assertIn("Commands", chat[0])
        self.assertTrue(any("ForeverDB.net" in line for line in chat), "the help does not credit the data")

    def test_option_commands(self):
        game = Game()
        self.assertEqual(game.slash("tooltip"), ["Easy BIS: BIS lines in item tooltips: off."])
        self.assertFalse(game.ns.db.tooltip)
        self.assertEqual(game.slash("TOOLTIP"), ["Easy BIS: BIS lines in item tooltips: on."])
        self.assertEqual(game.slash("unsourced"), ["Easy BIS: Items with no known source: on."])
        self.assertTrue(game.ns.db.unsourced)
        # the PvP rewards: the list the window shows (the PvE one here), or the one named
        self.assertEqual(game.slash("pvp"), ["Easy BIS: PvP rewards in the PvE list: on."])
        self.assertEqual(dict(game.ns.db.pvpRewards), {"pve": True, "pvp": True})
        self.assertEqual(game.slash("pvp"), ["Easy BIS: PvP rewards in the PvE list: off."])
        self.assertEqual(game.slash("pvp PVP"), ["Easy BIS: PvP rewards in the PvP list: off."])
        self.assertEqual(dict(game.ns.db.pvpRewards), {"pve": False, "pvp": False})
        self.assertEqual(game.slash("pvp pve"), ["Easy BIS: PvP rewards in the PvE list: on."])
        self.assertTrue(any("/easybis pvp" in line for line in game.slash("help")))
        self.assertEqual(game.slash("minimap"), ["Easy BIS: Minimap button: off."])

    def test_item_command(self):
        game = Game()
        game.stub.itemNames[EYE_OF_REND] = "Eye of Rend"
        chat = game.slash(f"item |cffa335ee|Hitem:{EYE_OF_REND}::::::::60|h[Eye of Rend]|h|r")
        self.assertIn("is wanted by", chat[0])
        self.assertTrue(any("Shaman Enhancement" in line and "BIS PvE" in line for line in chat[1:]))
        self.assertIn("nobody", game.slash("item 1")[0])
        self.assertIn("/easybis item", game.slash("item")[0])

    def test_list_command(self):
        game = Game()
        chat = game.slash("list 2")
        self.assertEqual(chat[0], "Easy BIS: Shaman Enhancement, Level 60 PvE:")
        self.assertEqual(len(chat), 1 + 15)
        self.assertIn("[Eye of Rend]", chat[1])       # the English name, the game has not loaded the item
        self.assertTrue(chat[1].startswith("Easy BIS:   Head: BIS "))
        self.assertIn("two-hander", next(line for line in chat if "Off hand" in line))
        # a Fire Mage has both styles: the two-handers follow the one-handers as alternatives
        mage = Game(cls="MAGE")
        main = next(line for line in mage.slash("list 2") if "Main hand" in line)
        self.assertEqual(main.count("["), 1 + ladders.ALTERNATIVES + 1 + ladders.ALTERNATIVES, main)
        self.assertIn("PvP", game.slash("list 2 pvp")[0])
        self.assertIn("no spec number 7", game.slash("list 7")[0])

    # -- reputations ---------------------------------------------------------------------------

    @staticmethod
    def wearers_pieces(game, phase, side, mode) -> tuple[int, int, int, int]:
        """The best pieces asking for the wearer's reputation: their number over every spec, the specs that have
        some, the most a spec has, and the number of specs."""
        count = game.lua.eval("""function(ns, phase, side, list)
            local total, specs, most, all = 0, 0, 0, 0
            for _, class in ipairs(ns.CLASSES) do
                for spec = 1, ns.Index.SpecCount(class) do
                    all = all + 1
                    local mine = 0
                    for _, group in ipairs(ns.Reputation.Needs(class, spec, list, phase, side).own) do
                        for _, entries in pairs(group.steps) do
                            for _, entry in ipairs(entries) do
                                if entry.id and entry.role == "best" and entry.requirement.kind == "w" then
                                    mine = mine + 1
                                end
                            end
                        end
                    end
                    total, most = total + mine, math.max(most, mine)
                    if mine > 0 then specs = specs + 1 end
                end
            end
            return total, specs, most, all
        end""")
        return count(game.ns, phase, side, mode)

    def test_reputation_counts_follow_the_generators_picks(self):
        """The addon's count of the best pieces asking for the wearer's reputation, against the generator's picks
        and the reading kept in corrections/reputations.json."""
        records = reputations.load()["items"]

        def asks_the_wearer(item_id, side):
            found = records.get(item_id, ())
            own = [record for record in found if record["side"] == side] or [r for r in found if r["side"] == ""]
            return bool(own) and own[0]["kind"] == reputations.WEAR

        game = Game()
        for phase, side, mode in ((0, "a", "pve"), (0, "h", "pve"), (0, "a", "pvp"), (0, "h", "pvp"), (9, "a", "pve")):
            per_spec = []
            for token in CLASSES:
                for spec in self.kept[token]:
                    picks = self.expected_picks(token, spec, mode, default_filter(side=side, phase=phase))
                    per_spec.append(sum(asks_the_wearer(item_id, side) for slot, _ in ladders.SLOTS for item_id in picks[slot][0]))
            self.assertGreater(sum(per_spec), 0)
            self.assertEqual(self.wearers_pieces(game, phase, side, mode),
                             (sum(per_spec), sum(1 for count in per_spec if count), max(per_spec), len(per_spec)),
                             (phase, side, mode))

    def test_reputation_requirements_follow_the_data(self):
        game = Game()
        text = (ADDON / "Data" / "Reputation.lua").read_text(encoding="utf-8")
        block = re.search(r"items = \[==\[\n(.*?)\]==\]", text, re.S).group(1)
        records = [line.split("|") for line in block.splitlines()]
        self.assertTrue(records)
        rep = game.ns.Reputation
        for fields in records:
            item_id, side = int(fields[0]), fields[1]
            found = rep.Requirement(item_id, side or "a")
            self.assertEqual((found.factionID, found.standing, found.kind),
                             (int(fields[2]), int(fields[3]), fields[4]), fields)
        self.assertIsNone(rep.Requirement(EYE_OF_REND, "a"))
        self.assertIsNone(rep.EnchantRequirement("no such enchant"))

    def test_reputation_of_the_other_side(self):
        for faction, status in (("Horde", "other"), ("Alliance", "missing")):
            game = Game(faction=faction)
            stormpike = game.lua.table_from({"factionID": 730, "standing": 4})
            self.assertEqual(game.ns.Reputation.Status(stormpike), status)

    def test_reputation_standing_as_the_game_says(self):
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        need = game.lua.table_from({"factionID": 576, "standing": 5, "kind": "w"})
        def be(reaction, value, low, high):
            stub.factions[576] = game.lua.table_from({"reaction": reaction, "value": value, "low": low, "high": high})
            stub.fire("UPDATE_FACTION")
        # never met: the game reads Neutral 0, the pane does not list it
        self.assertFalse(rep.Standing(576).met)
        self.assertEqual(rep.ProgressText(576), "Not met yet")
        self.assertEqual(rep.Status(need), "missing")
        be(5, 3500, 3000, 9000)        # Friendly, 500 into it
        self.assertEqual(rep.Status(need), "missing")
        self.assertEqual((rep.Standing(576).standing, rep.Standing(576).value, rep.Standing(576).span), (4, 500, 6000))
        self.assertEqual(rep.ProgressText(576), "Friendly 500 / 6000")
        self.assertEqual(rep.ProgressText(576, True), "Friendly")
        self.assertAlmostEqual(rep.Ratio(576), 500 / 6000)
        self.assertEqual(strip_colors(rep.StateText(need)), "You: Friendly")
        self.assertNotIn("|cffffd100", rep.StateText(need))
        be(6, 9000, 9000, 21000)       # Honored: what is asked for
        self.assertEqual(rep.Status(need), "met")
        self.assertTrue(rep.Reachable(need))
        self.assertEqual(rep.StateText(need), "|cffffd100Earned|r")
        be(8, 42000, 42000, 43000)     # Exalted: no numbers left to read
        self.assertEqual(rep.ProgressText(576), "Exalted")
        self.assertEqual(rep.Ratio(576), 1)

    def test_reputation_position_and_what_is_left(self):
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        def be(reaction, value, low, high):
            stub.factions[576] = game.lua.table_from({"reaction": reaction, "value": value, "low": low, "high": high})
            stub.fire("UPDATE_FACTION")
        # never met: nowhere on the way, and the whole way from Neutral is left
        self.assertIsNone(rep.Position(576))
        self.assertEqual(rep.Remaining(576, 6), (21000, True))
        be(5, 3500, 3000, 9000)        # Friendly, 500 into it
        self.assertEqual(rep.Position(576), 3500)
        self.assertEqual(rep.Remaining(576, 4), 0)
        self.assertEqual(rep.Remaining(576, 6), 17500)
        be(3, -2000, -6000, 0)         # Unfriendly: the game counts down from Neutral 0
        self.assertEqual(rep.Position(576), -2000)
        self.assertEqual(rep.Remaining(576, 4), 5000)
        be(8, 42000, 42000, 43000)     # Exalted
        self.assertEqual(rep.Position(576), 42000)
        self.assertEqual(rep.Remaining(576, 7), 0)
        stub.factionsUnknown = True
        stub.fire("UPDATE_FACTION")
        self.assertIsNone(rep.Position(576))
        self.assertEqual(rep.Remaining(576, 6), None, "what the game does not say stays unknown")

    def test_reputation_watched_by_the_game_bar(self):
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        self.assertFalse(rep.CanWatch(576), "a faction never met is not in the reputation pane")
        stub.factions[576] = game.lua.table_from({"reaction": 5, "value": 3500, "low": 3000, "high": 9000})
        stub.fire("UPDATE_FACTION")
        self.assertTrue(rep.CanWatch(576))
        self.assertFalse(rep.Watched(576))
        rep.Watch(576, True)
        self.assertEqual(stub.watched, 576)
        self.assertTrue(rep.Watched(576))
        rep.Watch(576, False)
        self.assertIsNone(stub.watched)

    def test_reputation_watched_on_a_client_without_c_reputation(self):
        game = Game(saved="""C_Reputation = nil
            function GetFactionInfoByID(id) return "Old " .. id, "", 5, 3000, 9000, 3500 end
            function GetNumFactions() return 2 end
            function GetFactionInfo(index)
                if index == 1 then return "Header", "", 0, 0, 0, 0, false, false, true, false, false, false, false, nil end
                return "Old 576", "", 5, 3000, 9000, 3500, false, false, false, false, false, false, false, 576
            end
            watching = 0
            function SetWatchedFactionIndex(index) watching = index end
            function GetWatchedFactionInfo() if watching == 2 then return "Old 576", 5, 3000, 9000, 3500, 576 end end""")
        rep = game.ns.Reputation
        self.assertTrue(rep.CanWatch(576))
        rep.Watch(576, True)
        self.assertEqual(game.lua.globals().watching, 2, "the bar is set by the faction's line in the pane")
        self.assertTrue(rep.Watched(576))
        rep.Watch(576, False)
        self.assertEqual(game.lua.globals().watching, 0)

    def test_reputation_sellers_say_where_each_piece_comes_from(self):
        game = Game()
        rep = game.ns.Reputation
        group = lambda *entries: game.lua.table_from({"steps": game.lua.table_from({
            4: game.lua.table_from([game.lua.table_from({"requirement": game.lua.table_from(e)}) for e in entries])})})
        texts = lambda sellers: [seller.text for seller in sellers.values()]
        quest = rep.Sellers(group({"kind": "q", "via": "Honored Amongst the Guard"}))
        self.assertEqual(texts(quest), ["Quest reward: Honored Amongst the Guard"])
        recipe = rep.Sellers(group({"kind": "r", "via": "Plans: Dark Iron Helm"}))
        self.assertEqual(texts(recipe), ["Plans: Dark Iron Helm: where to get it is unknown"])
        self.assertEqual(texts(rep.Sellers(group({"kind": "w"}))), ["Unknown"])
        # a piece no vendor sells: the quest that rewards it, else said to be unknown, not dropped
        self.assertEqual(texts(rep.Sellers(group({"kind": "w", "via": "The Path of the Protector"}))),
                         ["Quest reward: The Path of the Protector"])
        some = rep.Sellers(group({"kind": "w", "vendor": 263569}, {"kind": "w", "id": 1}, {"kind": "w", "id": 2}))
        self.assertEqual(texts(some)[1:], ["Other pieces: where to get them is unknown (2)"])
        vendor = rep.Sellers(group({"kind": "w", "vendor": 263569}, {"kind": "w", "vendor": 263569}))
        self.assertEqual(len(texts(vendor)), 1, "a vendor is named once")
        self.assertTrue(texts(vendor)[0].startswith("Bryanna Embreeze, "))
        self.assertEqual((vendor[1].map, vendor[1].x, vendor[1].y), (1413, 63.4, 58.7))

    def test_reputation_recipes_follow_the_players_professions(self):
        """A recipe's reputation is the crafter's: the player is told theirs only when the profession is theirs."""
        game = Game(cls="WARRIOR")
        rep, stub, lua = game.ns.Reputation, game.stub, game.lua
        learn = lambda *professions: stub.learn(lua.table_from(
            {index: lua.table_from({1: name, 2: rank, 3: line}) for index, (name, rank, line) in enumerate(professions, 1)}))
        woolies = rep.Requirement(15065)
        self.assertEqual((woolies.kind, woolies.recipe, woolies.vendor, woolies.profession, woolies.skill),
                         ("r", 20254, 11557, "Leatherworking", 260))
        stub.factions[576] = lua.table_from({"reaction": 5, "value": 3500, "low": 3000, "high": 9000, "name": "Timbermaw Hold"})
        stub.fire("UPDATE_FACTION")
        self.assertEqual(rep.NeedText(woolies), "Pattern: Timbermaw Hold, Friendly")
        self.assertEqual(rep.RecipeWord(rep.EnchantRequirement("s23800")), "Formula")
        self.assertEqual(rep.RecipeName(woolies), "Pattern: Warbear Woolies")
        # sold by Meilosh, in Felwood: the recipe's vendor, with its place
        group = lua.table_from({"steps": lua.table_from({4: lua.table_from({1: lua.table_from({"requirement": woolies})})})})
        seller = rep.Sellers(group)[1]
        self.assertEqual(seller.text, "Pattern: Warbear Woolies, sold by Meilosh, Map 1448 65.7, 2.8")
        self.assertEqual((seller.map, seller.x, seller.y), (1448, 65.7, 2.8))

        # a client without the professions' API: nothing is said of the player
        self.assertIsNone(rep.Professions())
        self.assertIsNone(rep.Crafter(woolies))
        self.assertEqual(strip_colors(rep.StateText(woolies)), "For the crafter")
        crafts, status = rep.Crafts(group)
        self.assertEqual((crafts[1].profession, crafts[1].rank, crafts[1].status, status), ("Leatherworking", None, None, None))
        # a leatherworker: their reputation and their skill
        learn(("Leatherworking", 270, 165), ("Skinning", 300, 393))
        self.assertEqual(dict(rep.Professions()), {"Leatherworking": 270, "Skinning": 300})
        self.assertEqual(rep.Crafter(woolies), ("crafter", 270))
        self.assertEqual(rep.StateText(woolies), "|cffffd100Earned|r", "Friendly is what the pattern asks")
        crafts, status = rep.Crafts(group)
        self.assertEqual((crafts[1].profession, crafts[1].skill, crafts[1].rank, crafts[1].status, status),
                         ("Leatherworking", 260, 270, "crafter", "crafter"))
        self.assertIsNone(rep.Crafter(rep.Requirement(EYE_OF_REND)), "a piece that is not a recipe")
        # a profession known by its name alone, in the game's language
        learn(("Leatherworking", 120, None))
        self.assertEqual(rep.Crafter(woolies), ("crafter", 120))
        # a tailor: the reputation is not theirs, and never gold
        learn(("Tailoring", 300, 197))
        self.assertEqual(rep.Crafter(woolies), "other")
        self.assertEqual(strip_colors(rep.StateText(woolies)), "Leatherworking")
        stub.factions[576] = lua.table_from({"reaction": 8, "value": 42000, "low": 42000, "high": 43000, "name": "Timbermaw Hold"})
        stub.fire("UPDATE_FACTION")
        self.assertNotIn("|cffffd100", rep.StateText(woolies))
        lines = list(rep.TooltipLines(15065).values())
        self.assertEqual((lines[0].r, lines[0].g, lines[0].b), (1, 1, 1), "the tailor's own standing is not the piece's")
        self.assertEqual(lines[1].text, "Leatherworking: not one of your professions")
        self.assertIn("Recipe sold by: Meilosh, Map 1448 65.7, 2.8", [line.text for line in lines])
        learn(("Leatherworking", 300, 165))
        first = rep.TooltipLines(15065)[1]
        self.assertEqual((first.r, first.g, first.b), (1, 0.82, 0), "the leatherworker has earned it: gold")
        # no profession at all
        learn()
        self.assertEqual(dict(rep.Professions()), {})
        self.assertEqual(rep.Crafter(woolies), "other")

    def test_reputation_binding_as_the_game_says(self):
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        self.assertIsNone(rep.Binding(15065), "an item the game has not shown yet")
        stub.itemNames[15065] = "Warbear Woolies"
        self.assertIsNone(rep.Binding(15065), "a bind type the game does not give")
        for bind, word in ((0, "none"), (1, "pickup"), (2, "equip")):
            stub.bindings[15065] = bind
            self.assertEqual(rep.Binding(15065), word)
        self.assertIsNone(rep.Binding(None))

    def test_reputation_emblems(self):
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        self.assertIsNone(rep.Emblem(576), "the game gives the question mark: an item it does not have")
        stub.itemIcons[21377] = 236000
        self.assertEqual(rep.Emblem(576), 236000)
        stub.itemIcons[18606], stub.itemIcons[18607] = 132486, 132485
        self.assertEqual((rep.Emblem(2799), rep.Emblem(2798)), (132486, 132485), "Alliance and Horde battle standards")
        stub.itemIcons[19505], stub.itemIcons[19506] = 132482, 132483
        self.assertEqual((rep.Emblem(889), rep.Emblem(890)), (132482, 132483), "Warsong and Silverwing battle tabards")
        for none in (2819, 2827, 21, 999999):
            self.assertIsNone(rep.Emblem(none), none)

    def test_reputation_battlegrounds(self):
        """A battleground's faction says so: the battleground named as the game names it, or only said to be one."""
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        for faction, area in reputations.BATTLEGROUNDS.items():
            self.assertEqual(rep.Battleground(faction), (area, None), faction)
            self.assertEqual(rep.BattlegroundText(faction), "Battleground", faction)
        stub.areaNames[2597] = "Alterac Valley"
        self.assertEqual(rep.Battleground(730), (2597, "Alterac Valley"))
        self.assertEqual(rep.BattlegroundText(729), "Battleground: Alterac Valley")
        for elsewhere in (21, 529, 2819, 999999):
            self.assertIsNone(rep.Battleground(elsewhere), elsewhere)
            self.assertIsNone(rep.BattlegroundText(elsewhere), elsewhere)
        game.lua.execute("C_Map.GetAreaInfo = function() error('not on this client') end")
        self.assertEqual(rep.BattlegroundText(729), "Battleground", "what the game does not say is not made up")
        game.lua.execute("C_Map.GetAreaInfo = nil")
        self.assertEqual(rep.BattlegroundText(729), "Battleground")
        # Warsong Gulch's factions, one to each side
        self.assertEqual((rep.Faction(889).side, rep.Faction(890).side), ("h", "a"))
        self.assertGreater(rep.Faction(890).quests, 0)

    def test_reputation_of_the_quartermasters_pieces(self):
        """What the Alterac and Warsong quartermasters ask, which their pieces' tooltips do not say (AtlasLoot's
        tables): each side its own faction, at its own vendor."""
        rep = Game().ns.Reputation
        for side, faction, vendor in (("a", 730, 13217), ("h", 729, (13218, 13219))):
            found = rep.Requirement(19325, side)   # Don Rodrigo's Band, Don Julio's for the Horde
            self.assertEqual((found.factionID, found.standing, found.kind), (faction, 7, "w"), side)
            self.assertIn(found.vendor, vendor if isinstance(vendor, tuple) else (vendor,), side)
        found = rep.Requirement(19083, "h")       # Frostwolf Legionnaire's Cloak
        self.assertEqual((found.factionID, found.standing), (729, 5))

    def test_reputation_crafters_come_first(self):
        game = Game(cls="PRIEST")
        rep, stub, lua = game.ns.Reputation, game.stub, game.lua
        before = [group.factionID for group in rep.Needs("PRIEST", 1, "pve").artisan.values()]
        self.assertTrue({576, 609} < set(before))
        stub.learn(lua.table_from({1: lua.table_from({1: "Tailoring", 2: 300, 3: 197})}))
        groups = list(rep.Needs("PRIEST", 1, "pve").artisan.values())
        crafters = [group.factionID for group in groups if group.crafter]
        self.assertEqual(set(crafters), {576, 609}, "Timbermaw and Cenarion Circle sell tailoring patterns")
        self.assertEqual([group.factionID for group in groups[:len(crafters)]], crafters, "the tailor's come first")
        self.assertTrue(all(group.craftStatus == "other" for group in groups[len(crafters):]))

    def test_reputation_unknown_faction(self):
        """A faction no source says how to earn, nor who sells its pieces: its pieces wear a grey "?"."""
        game = Game()
        rep = game.ns.Reputation
        self.assertTrue(rep.Unknown(2819), "The Watchers: read only in the game's files")
        for known in (21, 529, 576, 749, 2827):
            self.assertFalse(rep.Unknown(known), known)
        self.assertFalse(rep.Unknown(999999), "a faction the data does not have is not said unknown")
        need = lambda faction: game.lua.table_from({"factionID": faction, "standing": 6, "kind": "w"})
        self.assertEqual(rep.UnknownMark(need(2819)), " |cff808080?|r")
        self.assertEqual(rep.UnknownMark(need(576)), "")
        self.assertEqual(rep.UnknownMark(None), "")
        self.assertEqual(rep.UnknownRemark(need(2819)),
                         "? No source says how to earn this reputation, nor who sells its pieces.")
        self.assertIsNone(rep.UnknownRemark(need(576)))

    def test_reputation_asking_for_neutral(self):
        """The game reads a faction never met as Neutral 0: that is not a Neutral standing earned."""
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        need = game.lua.table_from({"factionID": 910, "standing": 3, "kind": "w"})
        self.assertEqual(rep.Status(need), "missing")
        self.assertFalse(rep.Reachable(need))
        self.assertNotIn("|cffffd100", rep.StateText(need))
        # the reputation pane hides the answer: unknown, and still not gold
        stub.factionList = game.lua.table_from({1: game.lua.table_from({"factionID": 1, "isHeader": True, "isCollapsed": True})})
        stub.fire("UPDATE_FACTION")
        self.assertEqual(rep.Status(need), "unknown")
        self.assertNotIn("|cffffd100", rep.StateText(need))
        # met, and at Neutral: earned
        stub.factionList = game.lua.table_from({1: game.lua.table_from({"factionID": 910, "isHeader": False, "isCollapsed": False})})
        stub.fire("UPDATE_FACTION")
        self.assertEqual(rep.Status(need), "met")

    def test_reputation_never_claims_what_the_game_hides(self):
        game = Game()
        rep, stub = game.ns.Reputation, game.stub
        entry = lambda **fields: game.lua.table_from(fields)
        # a collapsed header may hide the faction: nothing is said of whether it was met
        stub.factionList = game.lua.table_from({1: entry(factionID=1118, isHeader=True, isCollapsed=True)})
        stub.fire("UPDATE_FACTION")
        self.assertIsNone(rep.Standing(576).met)
        self.assertEqual(rep.ProgressText(576), "Neutral 0 / 3000")
        # listed at Neutral 0: met
        stub.factionList = game.lua.table_from({1: entry(factionID=576, isHeader=False, isCollapsed=False)})
        stub.fire("UPDATE_FACTION")
        self.assertTrue(rep.Standing(576).met)
        # a faction the game does not know is written as unknown, and is not "missing"
        stub.factionsUnknown = True
        stub.fire("UPDATE_FACTION")
        need = game.lua.table_from({"factionID": 576, "standing": 5, "kind": "w"})
        self.assertEqual(rep.Status(need), "unknown")
        self.assertEqual(rep.ProgressText(576), "Unknown")
        self.assertEqual(strip_colors(rep.StateText(need)), "Unknown")
        self.assertFalse(rep.Reachable(need))

    def test_reputation_on_a_client_without_c_reputation(self):
        game = Game(saved="""C_Reputation = nil
            function GetFactionInfoByID(id) return "Old " .. id, "", 6, 9000, 21000, 12000 end
            function GetNumFactions() return 0 end""")
        standing = game.ns.Reputation.Standing(576)
        self.assertEqual((standing.name, standing.standing, standing.value, standing.span), ("Old 576", 5, 3000, 12000))

    def test_reputation_changes_are_announced_once(self):
        game = Game()
        seen = game.lua.eval("function(ns) local n = { count = 0 }; ns:On('REPUTATION_CHANGED', function() n.count = n.count + 1 end); return n end")(game.ns)
        for _ in range(5):
            game.stub.fire("UPDATE_FACTION")
        self.assertEqual(seen.count, 0, "the game sends them in bursts")
        game.stub.runTimers()
        self.assertEqual(seen.count, 1)

    def test_reputation_tooltip(self):
        game = Game(cls="WARRIOR")
        rep = game.ns.Reputation
        text = (ADDON / "Data" / "Reputation.lua").read_text(encoding="utf-8")
        block = re.search(r"items = \[==\[\n(.*?)\]==\]", text, re.S).group(1)
        # a piece of a faction the Alliance can earn: one of the Horde's is never earned
        fields = next(fields for fields in map(lambda line: line.split("|"), block.splitlines())
                      if fields[4] == "w" and fields[6] and fields[1] != "h"
                      and reputations.FACTIONS[int(fields[2])][1] != "h")
        item_id, faction = int(fields[0]), int(fields[2])
        lines = list(rep.TooltipLines(item_id).values())
        self.assertTrue(lines[0].text.startswith("Requires "))
        self.assertEqual((lines[0].r, lines[0].g, lines[0].b), (1, 1, 1), "not earned: not gold")
        words = [strip_colors(line.text) for line in lines]
        self.assertTrue(any(word.startswith("You: ") for word in words), words)
        self.assertTrue(any(word.startswith("Vendor: ") for word in words), words)
        self.assertTrue(any(word.startswith("Price: ") for word in words), words)
        game.stub.factions[faction] = game.lua.table_from({"reaction": 8, "value": 42000, "low": 42000, "high": 43000})
        game.stub.fire("UPDATE_FACTION")
        first = rep.TooltipLines(item_id)[1]
        self.assertEqual((first.r, first.g, first.b), (1, 0.82, 0), "earned: gold")
        self.assertEqual(len(rep.TooltipLines(EYE_OF_REND)), 0)
        # the option takes them out of the game's tooltips
        shown = lambda: any(line[0].startswith("Requires ") for line in game.tooltip(item_id))
        if game.lines(item_id):
            self.assertTrue(shown())
            game.ns.SetOption(game.ns, "repTooltip", False)
            self.assertFalse(shown())

    def test_reputation_ways_say_what_is_known(self):
        game = Game()
        rep = game.ns.Reputation
        values = lambda table: list(table.values())
        watchers = rep.Ways(2819)
        self.assertEqual(watchers.listed, 0)
        self.assertFalse(values(watchers.quests))
        self.assertEqual(values(watchers.unknowns), ["No quest, vendor or creature is known for this faction."],
                         "The Watchers: nothing is known")
        powderfuse = rep.Ways(2827)
        self.assertTrue(values(powderfuse.checks), "what a person wrote down is to be checked")
        self.assertEqual(values(powderfuse.unknowns), ["The whole way to Exalted.", "Reputation from creatures."])
        argent = rep.Ways(529, "WARRIOR")
        quests = values(argent.quests)
        usable = lambda quest: (quest["from"] or 3) < 7 and (quest.upto is None or quest.upto > 3)
        self.assertEqual(argent.listed, len(quests), "the cards count the quests listed")
        self.assertEqual(argent.repeatable, sum(1 for quest in quests if quest.repeats and usable(quest)))
        self.assertGreater(argent.total, argent.listed, "the other side's quests and the other classes' are not listed")
        self.assertEqual(values(argent.unknowns), ["Reputation from creatures."])
        names = [quest.quest for quest in quests]
        self.assertGreater(len(names), 100, "every quest a warrior can take, not a handful")
        self.assertLessEqual(len(names), argent.listed)
        self.assertIn("Corruptor's Scourgestones", names)
        # a class's own quest is kept for that class only
        zandalar = lambda cls: {quest.quest for quest in values(rep.Ways(270, cls).quests)}
        self.assertIn("Death's Embrace", zandalar("ROGUE"))
        self.assertNotIn("Death's Embrace", zandalar("MAGE"))
        self.assertIn("Animist's Caress", zandalar("DRUID"))
        self.assertNotIn("Animist's Caress", zandalar("ROGUE"))
        # the other side's quests are left out
        theramore = values(rep.Ways(2799).quests)
        self.assertTrue(theramore)
        horde = Game(faction="Horde").ns.Reputation
        self.assertFalse(values(horde.Ways(2799).quests))
        # no time is ever said: nothing measures the player's gains
        for language, words in game.ns.locales.items():
            for key, value in words.items():
                if str(key).startswith("REP_"):
                    self.assertIsNone(re.search(r"\b(hours?|heures?|minutes?|days?|jours?)\b", str(value), re.I), (language, key))

    def test_reputation_ways_count_what_one_character_can_do(self):
        """The cards count the quests of the list: of branches that exclude one another (the rings of Ahn'Qiraj)
        the one that gives the most, nothing a quest gives only below Neutral or at Exalted; the same sums as the
        generator's, class by class."""
        game = Game()
        rep = game.ns.Reputation
        values = lambda table: list(table.values())
        reading = reputations.load()
        for faction in (21, 59, 270, 529, 609, 730, 910, 2799):
            for cls, number in (("WARRIOR", 1), ("MAGE", 8), ("DRUID", 11)):
                mine = [{"title": m[0], "amount": m[1], "repeats": bool(m[2]), "side": m[3], "classes": m[4],
                         "from": m[5] or None, "until": m[6] or None, "choice": m[7]}
                        for m in reading["factions"][faction]["methods"] if not m[4] or m[4] >> (number - 1) & 1]
                ways = rep.Ways(faction, cls)
                self.assertEqual(ways.once, reputations.once_total(mine, "a"), (faction, cls))
                self.assertEqual(ways.repeatable, sum(1 for quest in mine if quest["repeats"] and quest["side"] in ("", "a")
                                                      and reputations.usable(quest)), (faction, cls))
        # the three paths of the rings: four steps of 100 each, one path counted
        brood = rep.Ways(910, "WARRIOR")
        paths = [quest for quest in values(brood.quests)
                 if quest.quest in ("The Path of the Protector", "The Path of the Conqueror", "The Path of the Invoker")]
        self.assertEqual(len(paths), 12)
        usable = [quest for quest in values(brood.quests)
                  if not quest.repeats and (quest["from"] or 3) < 7 and (quest.upto is None or quest.upto > 3)]
        self.assertEqual(sum(quest.amount for quest in usable) - brood.once, 800)
        # offered between two standings: said, and counted only where it helps
        thorium = {quest.quest: quest for quest in values(rep.Ways(59, "WARRIOR").quests)}
        flux = thorium["Restoring Fiery Flux Supplies via Iron"]
        self.assertEqual((bool(flux.repeats), flux.upto), (True, 4), "repeatable until Friendly")
        booty = rep.Ways(21, "WARRIOR")
        traitor = next(quest for quest in values(booty.quests) if quest.quest == "Traitor to the Bloodsail")
        self.assertEqual(traitor.upto, 3, "only below Neutral")
        self.assertEqual(booty.repeatable, 0)
        self.assertIn("The whole way to Exalted.", values(booty.unknowns))
        # the quests Questie says the game does not have are gone
        self.assertNotIn("DND FLAG The Dread Citadel - Naxxramas", [quest.quest for quest in values(rep.Ways(529).quests)])
        self.assertNotIn("Wanted: ORCS!", [quest.quest for quest in values(rep.Ways(730).quests)])
        self.assertFalse(values(Game(faction="Horde").ns.Reputation.Ways(730).quests), "Stormpike: nothing for the Horde")

    def test_reputation_an_enchant_counts_once(self):
        """An enchant the one-handed and two-handed weapons share is one piece of its faction."""
        game = Game()
        rep, ns = game.ns.Reputation, game.ns
        seen = 0
        for cls in CLASSES:
            for spec in range(1, int(ns.Index.SpecCount(cls)) + 1):
                for mode in ("pve", "pvp"):
                    needs = rep.Needs(cls, spec, mode)
                    for group in list(needs.own.values()) + list(needs.artisan.values()):
                        enchants = [entry.enchant for entries in group.steps.values() for entry in entries.values()
                                    if entry.enchant]
                        self.assertEqual(len(enchants), len(set(enchants)), (cls, spec, mode, group.factionID))
                        seen += len(enchants)
        self.assertGreater(seen, 0)

    def test_reputation_summary_when_the_game_does_not_say(self):
        game = Game()
        rep, lua = game.ns.Reputation, game.lua
        cells = lambda: lua.table_from([lua.table_from({"reputation": lua.table_from(
            {"factionID": 576, "standing": 5, "kind": "w"})})])
        self.assertIsNone(rep.Summary(cells())[1].state)
        game.stub.factionsUnknown = True
        game.stub.fire("UPDATE_FACTION")
        game.stub.runTimers()
        self.assertEqual(rep.Summary(cells())[1].state, "unknown", "not 0 of 1: the game does not say")

    # -- the game runs Lua 5.1 ----------------------------------------------------------------

    def test_no_syntax_newer_than_lua_51(self):
        newer = re.compile(r"\bgoto\b|//|<<|>>|\btable\.unpack\b|\btable\.pack\b|\butf8\.|\bmath\.tointeger\b"
                           r"|\bstring\.pack\b|(?<![~=<>])~(?!=)")
        for path in list(ADDON.glob("*.lua")) + list((ADDON / "UI").glob("*.lua")):
            code = path.read_text(encoding="utf-8")
            code = re.sub(r"--\[\[.*?\]\]", "", code, flags=re.S)
            code = re.sub(r"--[^\n]*", "", code)
            code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
            found = newer.search(code)
            self.assertIsNone(found, f"{path.name}: {found.group(0) if found else ''} is not Lua 5.1")


@unittest.skipIf(lupa is None, "lupa is not installed")
class ConsumablesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.lists = consumable_lists.build(cls.db)
        cls.game = Game()

    def groups(self, token, spec, mode, phase):
        return {group.key: group for group in self.game.ns.Consumables.For(token, spec, mode, phase).values()}

    def test_the_categories_are_the_generators(self):
        self.assertEqual(list(self.game.ns.Consumables.CATEGORIES.values()), list(consumable_lists.CATEGORIES))
        self.assertEqual(self.game.ns.Consumables.PER_CATEGORY, consumable_lists.PER_CATEGORY)

    def test_the_lists_are_the_generators(self):
        for token, spec, mode, phase in product(CLASSES, (1, 2, 3), consumable_lists.MODES, phases.PHASES):
            groups = self.groups(token, spec, mode, phase)
            for category, shelf in self.lists[token][spec][mode].items():
                with self.subTest(token=token, spec=spec, mode=mode, phase=phase, category=category):
                    wanted = [(entry[0], entry[2]) for entry in consumable_lists.shown(shelf.ranked, phase, twins=shelf.twins)]
                    group = groups.get(category)
                    got = [(entry.id, entry.score) for entry in group.ranked.values()] if group else []
                    self.assertEqual(got, wanted)
                    unranked = list(group.unranked.values()) if group else []
                    self.assertEqual(unranked, [item for item, needed in shelf.unranked if needed <= phase])

    def test_a_sharp_and_a_blunt_stone_take_one_place(self):
        ranked = list(self.groups("PALADIN", 3, "pve", phases.PRE_RAID)["weapon"].ranked.values())
        self.assertEqual([entry.id for entry in ranked], [12404, 12643, 7964, 7965, 2871, 3241])
        self.assertEqual([entry.twin for entry in ranked], [None, True, None, True, None, True])

    def test_every_spec_is_listed_in_both_lists(self):
        for token, spec, mode in product(CLASSES, (1, 2, 3), consumable_lists.MODES):
            groups = self.groups(token, spec, mode, phases.CURRENT)
            self.assertLessEqual({"flask", "elixir", "food", "scroll", "combat", "healing", "bandage", "situational"},
                                 set(groups), (token, spec, mode))

    def test_situational_is_what_the_class_can_use(self):
        for token, spec, phase in product(("WARRIOR", "MAGE"), (1, 2), phases.PHASES):
            wanted = [item for item, needed in consumable_lists.situational(self.db, token) if needed <= phase]
            group = self.groups(token, spec, "pve", phase)["situational"]
            self.assertEqual(list(group.unranked.values()), wanted)
            self.assertEqual(len(group.ranked), 0)
        cryoblast = 277499
        self.assertIn(cryoblast, self.groups("MAGE", 2, "pve", phases.LATER)["situational"].unranked.values())
        self.assertNotIn(cryoblast, self.groups("WARRIOR", 2, "pve", phases.LATER)["situational"].unranked.values())

    def test_every_row_says_what_it_does_and_where_it_comes_from(self):
        api = self.game.ns.Consumables
        known = consumable_lists.used_ids(self.lists, consumable_lists.situational(self.db))
        for item in known:
            with self.subTest(item=item):
                record = api.Info(item)
                self.assertIsNotNone(record)
                self.assertTrue(api.Kind(record))
                self.assertTrue(api.Detail(record))
                self.assertTrue(api.Where(record))
                if record.where != consumable_lists.UNKNOWN_WHERE:
                    self.assertNotEqual(api.Category(record), "unknown", record.where)

    def test_a_source_in_a_few_words(self):
        api = self.game.ns.Consumables
        oil = api.Info(20749)
        self.assertEqual((api.Kind(oil), api.Detail(oil)),
                         ("Enchanting (300)", "Recipe sold by Rin'wosho the Trader (Stranglethorn Vale)"))
        bandage = api.Info(14530)
        self.assertEqual(api.Kind(bandage), "First Aid (290)")
        self.assertEqual(api.Detail(api.Info(13510)), "Recipe drops from General Drakkisath")
        self.assertEqual(api.Kind(api.Info(10305)), "Vendor")
        self.assertEqual(api.Detail(api.Info(286152)), "Recipe found in Deadwind Pass")
        self.assertEqual(api.Detail(api.Info(274276)), "Recipe, source unknown")
        scroll = api.Info(277492)
        self.assertEqual((api.Category(scroll), api.Detail(scroll)), ("container", "Bundle of Scrolls"))

    def test_what_a_zone_changes(self):
        api = self.game.ns.Consumables
        flask = api.Info(274276)
        self.assertEqual((flask.zoneRule, flask.zone), ("bonus", "Mount Hyjal, Hyjal Summit, and the Barrow Deeps"))
        self.assertEqual(api.ZoneNote(flask), "Its bonus works only in Mount Hyjal, Hyjal Summit, and the Barrow Deeps.")
        self.assertEqual(api.ZoneNote(api.Info(17348)), "Usable only in PvP Battlegrounds.")
        self.assertIsNone(api.ZoneNote(api.Info(13446)))


@unittest.skipIf(lupa is None, "lupa is not installed")
class CostTest(unittest.TestCase):
    """What a vendor asks in a currency, and what the player has of it."""
    REAL, REAL_CURRENCY, CLOAK = 226404, 3469, 272411   # the Arcanoweave Cloak is sold for 75 Reals

    def setUp(self):
        self.game = Game()
        self.sources = self.game.ns.Sources

    def test_the_source_says_the_price(self):
        cost = self.sources.Describe(self.CLOAK).cost
        self.assertEqual((cost.item, cost.amount), (self.REAL, 75))
        self.assertEqual(no_pictures(self.sources.CostText(cost)), "75 Reals")
        self.assertEqual(no_pictures(self.sources.WithCost("Pix Xizzix", cost)), "75 Reals · Pix Xizzix")
        self.assertIsNone(self.sources.Describe(EYE_OF_REND).cost, "a drop costs nothing")
        self.assertEqual(self.sources.WithCost("Blackrock Spire", None), "Blackrock Spire")

    def test_a_price_read_at_the_vendor_is_not_called_the_betas(self):
        source = self.game.ns.Items.Get(self.CLOAK).sources[1]
        for field, beta in ((f"{self.REAL}:75", False), (f"{self.REAL}:75:b", True)):
            source[7] = field
            cost = self.sources.Describe(self.CLOAK).cost
            self.assertEqual((cost.item, cost.amount, cost.beta), (self.REAL, 75, beta), field)

    def test_the_balance_is_read_as_a_currency_or_as_an_item(self):
        self.assertEqual(self.sources.Held(self.REAL), 0)
        self.game.stub.currencies[self.REAL_CURRENCY] = 38
        self.assertEqual(self.sources.Held(self.REAL), 38)
        self.game.stub.itemCounts[self.REAL] = 50
        self.assertEqual(self.sources.Held(self.REAL), 50, "the larger of the two, never their sum")

    def test_the_line_says_what_is_missing(self):
        cost = self.sources.Describe(self.CLOAK).cost
        self.assertEqual(no_pictures(self.sources.CostLine(cost)), "Cost: 75 Reals (you have 0, 75 missing)")
        self.game.stub.itemCounts[self.REAL] = 38
        self.assertEqual(no_pictures(self.sources.CostLine(cost)), "Cost: 75 Reals (you have 38, 37 missing)")
        self.game.stub.itemCounts[self.REAL] = 80
        self.assertEqual(no_pictures(self.sources.CostLine(cost)), "Cost: 75 Reals (you have 80)")

    def test_a_client_that_cannot_say_shows_the_price_alone(self):
        self.game.lua.globals().C_CurrencyInfo = None
        self.game.lua.globals().GetItemCount = None
        self.assertIsNone(self.sources.Held(self.REAL))
        self.assertEqual(no_pictures(self.sources.CostLine(self.sources.Describe(self.CLOAK).cost)), "Cost: 75 Reals")

    def test_in_french(self):
        game = Game(locale="frFR")
        game.stub.itemCounts[self.REAL] = 38
        cost = game.ns.Sources.Describe(self.CLOAK).cost
        self.assertEqual(no_pictures(game.ns.Sources.CostLine(cost)), "Coût : 75 Reals (vous en avez 38, il en manque 37)")

    def test_the_price_wears_the_items_picture(self):
        cost = self.sources.Describe(self.CLOAK).cost
        self.assertEqual(self.sources.CostText(cost), "75 |T134400:14:14:0:0:64:64:5:59:5:59|t Reals")

    def test_the_currencys_own_picture_comes_first(self):
        self.game.stub.currencies[self.REAL_CURRENCY] = 0
        self.game.stub.currencyIcon = 463446
        cost = self.sources.Describe(self.CLOAK).cost
        self.assertEqual(self.sources.CostText(cost), "75 |T463446:14:14:0:0:64:64:5:59:5:59|t Reals")

    def test_a_game_without_a_picture_shows_the_words(self):
        self.game.lua.globals().C_CurrencyInfo = None
        self.game.lua.globals().GetItemIcon = None
        self.assertEqual(self.sources.CostText(self.sources.Describe(self.CLOAK).cost), "75 Reals")

    def test_both_factions_are_offered_the_vendors_items(self):
        for faction in ("Alliance", "Horde"):
            game = Game(faction=faction, cls="DRUID")
            self.assertEqual(game.ns.Ladders.For("DRUID", 1, "pve").back.best[1].id, self.CLOAK, faction)


@unittest.skipIf(lupa is None, "lupa is not installed")
class DungeonsTest(unittest.TestCase):
    """Which dungeons hold a spec's picks (Dungeons.lua), against the generator's data."""
    DESTRUCTION = ("WARLOCK", 3)

    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.kept = ladders.build_all(cls.db)
        cls.by_name = {item["name"]: item_id for item_id, item in cls.db.items.items()}

    def item(self, name: str) -> int:
        return self.by_name[name]

    @staticmethod
    def model(game, token, spec, mode="pve"):
        return game.ns.Dungeons.For(game.lua.table_from({"class": token, "spec": spec, "list": mode}))

    # -- reference: what the generator's data says ----------------------------------------------

    def expected_runs(self, item_id: int, side="a") -> list[str] | None:
        """The keys of the runs the addon should place an item in, in order; None for an item of elsewhere."""
        item = self.db.items.get(item_id)
        if item is None:
            return None
        sources = phases.shown_sources(item)[:luaout.SOURCES_PER_ITEM]

        def meant_for(source) -> str:
            """The faction a source read in QuestieDB is for: the addon passes over the other side's."""
            index = {"q": 4, "v": 7}.get(source[0]) if source[-1] == "t" else None
            return source[index] if index is not None and len(source) > index else ""

        own = next((source for source in sources if meant_for(source) in ("", side)), sources[0] if sources else None)
        if own is None:
            return None

        def dungeon(number: int) -> bool:
            return (self.db.instances[number] + ["", ""])[1] != "raid"

        if own[0] == "q":
            place = self.db.quest_places.get(int(own[1]))
            return [f"{place[0]}:{place[1]}" if place[1] else str(place[0])] if place and dungeon(place[0]) else None
        if own[0] != "d" or own[4] == "1" or not dungeon(int(own[1])):
            return None
        keys = []
        for source in sources:
            if source[0] == "d" and source[4] != "1" and dungeon(int(source[1])):
                wing = runs.wing_of(self.db.boss_wings, int(source[1]), source[2])
                key = f"{source[1]}:{wing}" if wing else source[1]
                if key not in keys:
                    keys.append(key)
        return keys or None

    # -- an item's runs ---------------------------------------------------------------------

    def test_an_item_says_its_runs(self):
        game = Game()
        runs_of = lambda name: [dict(drop.items()) for drop in (game.ns.Sources.Runs(self.item(name)) or game.lua.table()).values()]
        turban = runs_of("Spellweaver's Turban")
        self.assertEqual([(drop["run"], drop["instance"], drop["wing"], drop["boss"]) for drop in turban],
                         [("229:u", 229, "u", "General Drakkisath")])
        self.assertGreater(turban[0]["percent"], 5)
        self.assertEqual(turban[0]["origin"], "w")
        self.assertNotIn("quest", turban[0])
        # two bosses of one wing; a dungeon without wings; a dungeon ForeverDB's table lacks
        self.assertEqual([drop["run"] for drop in runs_of("Sublime Wristguards")], ["429:n", "429:n"])
        self.assertEqual([(drop["run"], drop.get("wing")) for drop in runs_of("Bonecreeper Stylus")], [("289", None)])
        self.assertEqual([drop["run"] for drop in runs_of("Behemoth Bones")], ["2974"])
        # a quest done in a dungeon: its title, and no boss
        girdle = runs_of("Omokk's Girth Restrainer")
        self.assertEqual([(drop["run"], drop["boss"]) for drop in girdle], [("229:l", "")])
        self.assertIn(girdle[0]["quest"], ("Warlord's Command", "Maxwell's Mission"))
        self.assertNotIn("percent", girdle[0])
        # what no dungeon holds: crafted, a quest of the open world, an item the data does not have
        for name in ("Lionheart Helm", "Mark of Fordring"):
            self.assertIsNone(game.ns.Sources.Runs(self.item(name)), name)
        self.assertIsNone(game.ns.Sources.Runs(1))
        self.assertTrue(game.ns.Sources.Owned is not None and not game.ns.Sources.Owned(self.item("Lionheart Helm")))

    def test_a_raid_is_no_run(self):
        game = Game()
        raids = [item_id for item_id in luaout.shown_ids(self.kept)
                 if item_id in self.db.items and self.db.items[item_id]["sources"]
                 and phases.shown_sources(self.db.items[item_id])[0][0] == "d"
                 and phases.shown_sources(self.db.items[item_id])[0][4] == "1"]
        self.assertTrue(raids)
        for item_id in raids:
            self.assertIsNone(game.ns.Sources.Runs(item_id), item_id)

    def test_every_listed_item_has_the_generators_runs(self):
        for faction, side in (("Alliance", "a"), ("Horde", "h")):
            game = Game(faction=faction)
            for item_id in sorted(luaout.shown_ids(self.kept)):
                found = game.ns.Sources.Runs(item_id)
                keys = None
                if found:
                    keys = []
                    for drop in found.values():
                        if drop.run not in keys:
                            keys.append(drop.run)
                self.assertEqual(keys, self.expected_runs(item_id, side), (item_id, faction))

    def test_runs_are_named(self):
        game = Game()
        name = game.ns.Sources.RunName
        self.assertEqual((name(229, "u"), name(429, "n"), name(329, "l")),
                         ("Upper Blackrock Spire", "Dire Maul: North", "Stratholme: Living"))
        self.assertEqual(name(289), "Scholomance", "the data's name until the game gives its own")
        self.assertEqual(name(2974), "Blackmaw Hold")
        game.stub.zoneNames[289] = "Scholomance (the game's)"
        self.assertEqual(name(289), "Scholomance (the game's)")
        self.assertEqual(name(229, "x"), "Blackrock Spire", "a wing nothing knows is the dungeon")
        french = Game(locale="frFR")
        self.assertEqual(french.ns.Sources.RunName(229, "u"), "Sommet du pic Blackrock")
        self.assertEqual(french.ns.Sources.RunName(429, "e"), "Hache-tripes : Est")
        # every wing the data names has its name in both languages
        for instance, text in game.ns.data.wings.items():
            for wing in text.split("|"):
                key = f"WING_{instance}_{wing.split('^')[0]}"
                self.assertEqual(game.ns.L[key], wing.split("^")[1], key)
                self.assertNotEqual(french.ns.L[key], key)

    # -- the runs of a spec -------------------------------------------------------------------

    def test_the_runs_of_every_spec(self):
        game = Game()
        game.ns.SetOption(game.ns, "listAlts", False)
        flt = default_filter()
        for token in CLASSES:
            for spec in self.kept[token]:
                for mode in ladders.MODES:
                    picks = AddonTest.expected_picks(self, token, spec, mode, flt)
                    model = self.model(game, token, spec, mode)
                    where = (token, spec, mode)
                    # the set: the best pick of every slot, in the order of the character sheet
                    sheet = [(cell.slot, cell.rank, cell.id) for cell in model.sheet.values()]
                    self.assertEqual(len(sheet), 17, where)
                    for slot, rank, item_id in sheet:
                        best = picks[slot][0]
                        self.assertEqual(item_id, best[rank - 1] if len(best) >= rank else None, (where, slot))
                    # each piece in the runs the generator's data gives it
                    need, per_run, elsewhere = 0, {}, 0
                    for cell in model.sheet.values():
                        if cell.id is None:
                            continue
                        expected = self.expected_runs(cell.id)
                        self.assertEqual(list(cell.order.values()) if cell.order else None, expected, (where, cell.id))
                        need += expected is not None
                        elsewhere += expected is None
                        for key in expected or ():
                            per_run[key] = per_run.get(key, 0) + 1
                    self.assertEqual((model.need, model.got), (need, 0), where)
                    self.assertEqual({run.key: run.need for run in model.runs.values()}, per_run, where)
                    self.assertEqual(model.dungeons, len(per_run), where)
                    self.assertEqual(sum(entry.count for entry in model.elsewhere.values()), elsewhere, where)
                    # the run with the most to get first
                    counts = [run.need for run in model.runs.values()]
                    self.assertEqual(counts, sorted(counts, reverse=True), where)
                    self.assertEqual(len(model.rows), sum(1 for cell in model.sheet.values() if cell.id), where)

    def test_a_run_knows_its_pieces(self):
        game = Game()
        game.ns.SetOption(game.ns, "listAlts", False)
        model = self.model(game, *self.DESTRUCTION)
        turban = self.item("Spellweaver's Turban")
        upper = next(run for run in model.runs.values() if run.key == "229:u")
        self.assertEqual((upper.instance, upper.wing, upper.name, upper.short), (229, "u", "Upper Blackrock Spire", "UBRS"))
        self.assertEqual(len(list(upper.color.values())), 3)
        self.assertEqual([entry.piece.id for entry in upper.entries.values()][0], turban)
        self.assertEqual((upper.need, upper.got, upper.alts), (len(upper.entries), 0, 0))
        order = [slot for slot, _ in ladders.SLOTS]
        for run in model.runs.values():
            slots = [order.index(entry.piece.slot) for entry in run.entries.values()]
            self.assertEqual(slots, sorted(slots), f"{run.key}: in the order of the character sheet")
        entry = upper.entries[1]
        self.assertEqual((entry.piece.slot, entry.piece.best, entry.piece.owned, entry.piece.first), ("head", True, False, True))
        self.assertAlmostEqual(entry.percent, entry.drops[1].percent)
        self.assertEqual(entry.piece.source.category, "dungeon")
        # a piece two bosses of a run drop: the chance that one of them does
        wrist = next(entry for run in model.runs.values() for entry in run.entries.values()
                     if entry.piece.id == self.item("Sublime Wristguards"))
        first, second = (drop.percent for drop in wrist.drops.values())
        self.assertAlmostEqual(wrist.percent, 100 * (1 - (1 - first / 100) * (1 - second / 100)))
        # no two runs share a colour here, and every run has a short name of its own
        runs_shown = list(model.runs.values())
        self.assertEqual(len({tuple(run.color.values()) for run in runs_shown}), len(runs_shown))
        self.assertEqual(len({run.short for run in runs_shown}), len(runs_shown))

    def test_what_the_player_has_leaves_the_counts(self):
        game = Game()
        game.ns.SetOption(game.ns, "listAlts", False)
        before = self.model(game, *self.DESTRUCTION)
        busy = next(run for run in before.runs.values() if run.need == 2)   # a run that holds two best picks
        key = busy.key
        first, second = (entry.piece.id for entry in busy.entries.values())
        game.stub.itemCounts[first] = 1    # in the bags or in the bank
        model = self.model(game, *self.DESTRUCTION)
        run = next(run for run in model.runs.values() if run.key == key)
        self.assertEqual((model.need, model.got), (before.need - 1, 1))
        self.assertEqual((run.need, run.got), (1, 1))
        self.assertTrue(run.entries[1].piece.owned)
        self.assertFalse(run.entries[2].piece.owned)
        self.assertEqual(model.dungeons, before.dungeons)
        game.stub.equipped[second] = True     # worn
        model = self.model(game, *self.DESTRUCTION)
        run = next(run for run in model.runs.values() if run.key == key)
        self.assertEqual((run.need, run.got, model.dungeons), (0, 2, before.dungeons - 1))
        self.assertEqual(list(model.runs.values())[-1].key, key, "a run with nothing left comes last")

    def test_alternatives_come_with_the_option(self):
        game = Game()
        model = self.model(game, *self.DESTRUCTION)     # the alternatives are listed until the player says otherwise
        picks = AddonTest.expected_picks(self, *self.DESTRUCTION, "pve", default_filter())
        rows = [(piece.slot, piece.id, bool(piece.best)) for piece in model.rows.values()]
        expected = []
        for slot, _ in ladders.SLOTS:
            best, alternatives = picks[slot]
            expected += [(slot, item_id, True) for item_id in best] + [(slot, item_id, False) for item_id in alternatives]
        order = [slot for slot in ("head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet",
                                   "finger", "trinket", "main", "off", "ranged")]
        self.assertEqual(rows, sorted(expected, key=lambda row: order.index(row[0])))
        firsts = [piece.slot for piece in model.rows.values() if piece.first]
        self.assertEqual(firsts, [slot for slot in order if picks[slot][0] or picks[slot][1]], "one first line per slot")
        # an alternative counts in nothing, and sits after the run's best picks
        alone = Game()
        alone.ns.SetOption(alone.ns, "listAlts", False)
        without = self.model(alone, *self.DESTRUCTION)
        self.assertEqual((model.need, model.dungeons), (without.need, without.dungeons))
        self.assertGreater(len(list(model.runs.values())), len(list(without.runs.values())))
        for run in model.runs.values():
            ranks = [bool(entry.piece.best) for entry in run.entries.values()]
            self.assertEqual(ranks, sorted(ranks, reverse=True), run.key)
            self.assertEqual((run.need + run.got, run.alts), (ranks.count(True), ranks.count(False)), run.key)
        # once the slot's best pick is the player's, its alternatives have had their day
        turban = self.item("Spellweaver's Turban")
        heads = lambda found: [piece for piece in found.rows.values() if piece.slot == "head" and not piece.best]
        self.assertTrue(heads(model))
        self.assertFalse(any(piece.moot for piece in heads(model)))
        game.stub.itemCounts[turban] = 1
        self.assertTrue(all(piece.moot for piece in heads(self.model(game, *self.DESTRUCTION))))

    def test_a_spec_with_no_dungeon(self):
        game = Game()
        game.ns.SetOption(game.ns, "listAlts", False)
        feral = next(spec for spec, modes in self.kept["DRUID"].items() if self.db.classes["DRUID"]["specs"][spec]["name"] == "Feral Combat")
        model = self.model(game, "DRUID", feral)
        if any(self.expected_runs(cell.id) for cell in model.sheet.values() if cell.id):
            self.skipTest("the data gives the Feral Druid a dungeon piece by now")
        self.assertEqual((len(list(model.runs.values())), model.need, model.dungeons), (0, 0, 0))
        self.assertTrue(list(model.elsewhere.values()))
        # a class the data does not have: nothing, and no error
        empty = self.model(game, "DEATHKNIGHT", 1)
        self.assertEqual((len(list(empty.runs.values())), len(list(empty.sheet.values()))), (0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=1)
