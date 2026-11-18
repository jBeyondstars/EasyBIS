"""Tests for what the Consumables tab reads: ForeverDB's files, the capture, the tooltips.

    python -P _build/tests/test_consumables.py

The tests of the capture tool need the `lupa` package and are skipped without it.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TESTS = Path(__file__).resolve().parent
BUILD = TESTS.parent
sys.path.insert(0, str(BUILD))
sys.path.insert(0, str(TESTS))

import capture  # noqa: E402
import consumables  # noqa: E402
import fdb  # noqa: E402
import source  # noqa: E402
from test_generator import CAPTURE_STUB, saved_variable, tiny_db  # noqa: E402

try:
    import lupa
except ImportError:  # pragma: no cover
    lupa = None

HEADER = fdb.HEADER_PREFIX + ", build 1.0.0.1. Reuse requires this credit.\nlocal _, ns = ...\n"
MONGOOSE, TITANS, OLD_FLASK, SOUP, LOW_SOUP, BANDAGE, ALE, SCROLL, LEFTOVER, ENCHANT, STONE, OIL, OLD_STONE = (
    13452, 13510, 3000, 13931, 3001, 14529, 3002, 3003, 3004, 3005, 12404, 20749, 211845)

FILES = {
    "Consumables.lua": "ns.consumables = {" + ",".join((
        '{13452,"Elixir of the Mongoose","elixir","Agility",46,25,1,0,0}',
        '{3006,"Weak Agility","elixir","Agility",10,4,1,0,0}',
        '{13510,"Flask of the Titans","flask","Maximum health",50,1200,1,0,0}',
        '{3000,"Old Flask","flask","Maximum mana",30,500,1,0,0}',
        '{3007,"Older Flask","flask","Maximum mana",20,300,1,0,0}',
        '{13931,"Nightfin Soup","food","Well Fed: other",35,874,10,0,0}',
        '{3001,"Low Soup","food","Well Fed: other",1,61,10,0,0}',
        '{14529,"Runecloth Bandage","bandage","Healing",0,1360,11,0,0}',
        '{3002,"Strong Ale","food","Alcohol",0,0,0,1,0}',
        '{3003,"Scroll of \\"Luck\\"","scroll","Other",55,0,0,1,0}',
        '{3004,"Season Elixir","elixir","Agility",60,99,0,0,1}',
        '{3005,"Enchant Boots - Speed","enhance","Enchant scrolls",60,0,0,0,0}',
    )) + "}\n",
    "Recipes.lua": 'ns.recipes = {Blacksmithing={{16641,"Dense Sharpening Stone",230,250,255,260,12404,1,"12365:1","t",0,0,0},'
                   '{430397,"Blackfathom Sharpening Stone",0,0,0,0,211845,1,"","",0,0,0}},'
                   'Enchanting={{25129,"Brilliant Wizard Oil",300,310,315,320,20749,1,"14344:2,8831:3","i20756",0,0,0,1,2}},'
                   '["First Aid"]={{18630,"Runecloth Bandage",260,290,320,350,14529,1,"14047:1","t",0,0,0}}}\n'
                   'ns.names = {[12404]="Dense Sharpening Stone"}\n',
    "Items.lua": 'ns.professions = {"Alchemy","Blacksmithing","Enchanting","Engineering","Leatherworking","Tailoring",'
                 '"Herbalism","Mining","Skinning","Cooking","First Aid","Fishing"}\n'
                 'ns.items = {[13510]="m0~300|u2~0,1",[23122]="qShadows of Doom~1",'
                 '[25]="v1~Brammold Deepmine~Alterac Mountains~1|dChest of \\"Spoils\\"~0~1~1~0"}\n',
    "Coach.lua": 'ns.coachData = {v=1,profiles={}}\n'
                 'ns.coachData.profiles["rogue-combat"] = {class="ROGUE",specName="Combat",role="dps",brackets={'
                 '{levels={50,59},prepull={{kind="consumable",id=1,name="Too Early",value=0.5,src={"sim"}}}},'
                 '{levels={60,60},prepull={{kind="buff",id=2,name="Kings",value=0.1},'
                 '{kind="consumable",id=13452,name="Elixir of the Mongoose",value=0.041,src={"sim"}}}}}}\n'
                 'ns.coachData.profiles["druid-feral"] = {class="DRUID",specName="Feral",role="tank",brackets={{levels={40,49}}}}\n',
}


def write_files(folder: Path, files=FILES) -> None:
    for name, text in files.items():
        (folder / name).write_text(HEADER + text, encoding="utf-8")


def fixture():
    with tempfile.TemporaryDirectory() as folder:
        write_files(Path(folder))
        return fdb.read_consumables(folder)


class FilesTest(unittest.TestCase):
    def test_the_four_files_are_read_as_text(self):
        data = fixture()
        self.assertEqual(data.catalogue[TITANS], {
            "name": "Flask of the Titans", "kind": "flask", "family": "Maximum health", "level": 50, "strength": 1200.0,
            "profession": "Alchemy", "vendor": False, "leftover": False})
        self.assertEqual(data.catalogue[SCROLL]["name"], 'Scroll of "Luck"')
        self.assertTrue(data.catalogue[LEFTOVER]["leftover"])
        self.assertEqual(data.recipes[BANDAGE][0]["profession"], "First Aid", "a profession written with brackets")
        self.assertEqual(data.recipes[OIL][0]["reagents"], {14344: 2, 8831: 3})
        self.assertEqual(data.facts[TITANS]["made"], [("Alchemy", 300)])
        self.assertEqual(data.facts[25]["vendors"], [(1, "Brammold Deepmine", "Alterac Mountains")])
        self.assertEqual(data.facts[25]["drops"], ['Chest of "Spoils"'])
        self.assertEqual(data.facts[23122]["quests"], ["Shadows of Doom"])
        self.assertEqual(data.coach["rogue-combat"]["entries"], [(MONGOOSE, "Elixir of the Mongoose", 0.041)],
                         "the bracket of the level cap only, and its consumables only")
        self.assertNotIn("druid-feral", data.coach)

    def test_a_form_the_reader_does_not_know_is_refused(self):
        for name, broken in (("Consumables.lua", FILES["Consumables.lua"].replace(",46,25,1,0,0}", ",46,25,1,0}")),
                             ("Recipes.lua", FILES["Recipes.lua"].replace('"12365:1","t",0,0,0', '"12365:1","t",0,0'))):
            with tempfile.TemporaryDirectory() as folder, self.subTest(name):
                write_files(Path(folder), {**FILES, name: broken})
                with self.assertRaises(ValueError):
                    fdb.read_consumables(folder)

    def test_without_the_files_the_gear_lists_still_build(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(fdb.read_consumables(folder))
        self.assertIsNone(tiny_db().consumables)
        self.assertEqual(capture.capture_ids(tiny_db())["consumables"], [])

    def test_the_files_are_fetched_with_their_checksum(self):
        payload = b"-- data"
        good = hashlib.sha256(payload).hexdigest()
        names = fdb.DATA_FILES + fdb.CONSUMABLE_FILES
        entries = [{"path": f"Data/{name}", "url": f"downloads/addon-data/{name}?v=1", "sha256": good, "bytes": 7} for name in names]
        entries.append({"path": "Data/Atlas.lua", "url": "downloads/addon-data/Atlas.lua", "sha256": good, "bytes": 7})
        manifest = json.dumps({"data": {"version": "v", "files": entries}}).encode()
        with mock.patch.object(source, "_get", return_value=manifest):
            read = source.read_manifest()
        self.assertEqual(set(read["files"]), set(names), "the files the generator reads, and no other")
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(source, "_get", return_value=payload):
            self.assertEqual(sorted(source.update(Path(folder), read, only=fdb.CONSUMABLE_FILES)), sorted(fdb.CONSUMABLE_FILES))
            self.assertEqual(sorted(path.name for path in Path(folder).iterdir()), sorted(fdb.CONSUMABLE_FILES))
        read["files"]["Coach.lua"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(source, "_get", return_value=payload):
            with self.assertRaisesRegex(ValueError, "Coach.lua"):
                source.update(Path(folder), read, only=("Coach.lua",))
            self.assertEqual(list(Path(folder).iterdir()), [])


class ListTest(unittest.TestCase):
    def test_what_the_capture_reads(self):
        ids = consumables.consumable_ids(fixture())
        for item, why in ((MONGOOSE, "of a level that counts"), (TITANS, "of a level that counts"),
                          (OLD_FLASK, "the highest level of a family with nothing above"),
                          (SOUP, "a well fed food, whatever its level"), (LOW_SOUP, "a well fed food, whatever its level"),
                          (BANDAGE, "no level at all"), (SCROLL, "of a level that counts"),
                          (STONE, "a weapon stone of the recipes"), (OIL, "an oil of the recipes")):
            self.assertIn(item, ids, why)
        for item, why in ((3006, "a lower rank of a family that has a higher one"), (3007, "a lower rank"),
                          (ALE, "alcohol"), (LEFTOVER, "a Season of Discovery leftover"),
                          (ENCHANT, "permanent: the Enchants tab's"), (OLD_STONE, "a recipe of another season")):
            self.assertNotIn(item, ids, why)

    def test_they_are_read_first_and_say_nothing_of_the_gear(self):
        self.assertEqual(capture.ORDER[0], "consumables")
        db = tiny_db()
        db.data_dir = None
        db._consumables = fixture()
        groups = capture.capture_ids(db)
        self.assertIn(STONE, groups["consumables"])
        with tempfile.TemporaryDirectory() as folder:
            target, counts = capture.write_tool(db, folder)
            self.assertEqual(counts["consumables"], len(groups["consumables"]))
            listed = (target / "Ids.lua").read_text(encoding="utf-8").split("[==[\n")[1].split()
            self.assertEqual(int(listed[0]), groups["consumables"][0])
        rows = "\n".join(f'[{item}] = "Piece {item}\\nChest\\tCloth\\n#stats ",' for item in (1, 2, 3, 7, 8, 9))
        text = f'EasyBISCaptureDB = {{\n["meta"] = "1|1.0.0|1|enUS|2026-11-15 12:30",\n["items"] = {{\n{rows}\n}},\n}}\n'
        reading = capture.game_reading(db, capture.parse_saved(text))
        self.assertEqual((reading["listed"], reading["absent"]), (6, []), "a consumable not read is no missing piece of gear")


def read(*use, kind="elixir", family="Other", weapon=False, name="Test Item"):
    return consumables.decode([name, *[f"Use: {line}" for line in use], "Requires Level 50"], (), kind, family, weapon)


class DecodeTest(unittest.TestCase):
    def test_the_stat_ids_are_those_of_the_game(self):
        for stat in (consumables.AGILITY, consumables.STRENGTH, consumables.INTELLECT, consumables.SPIRIT, consumables.STAMINA,
                     consumables.CRIT, consumables.HIT, consumables.HASTE, consumables.DODGE, consumables.PARRY,
                     consumables.ATTACK_POWER, consumables.RANGED_ATTACK_POWER, consumables.HEALING, consumables.SPELL_DAMAGE,
                     consumables.SPELL_POWER, consumables.MANA_REGEN, consumables.HEALTH_REGEN, consumables.BLOCK_VALUE,
                     *consumables.RESISTANCES.values(), *consumables.SCHOOLS.values()):
            self.assertIn(stat, capture.GAME_KEYS.values())

    def test_stats_are_read_whole(self):
        mongoose = read("Increases Agility by 25 and critical strike chance by 2% for 1 hour.")
        self.assertEqual((mongoose.stats, mongoose.duration, mongoose.unread), ({3: 25, 32: 28}, 3600, []))
        self.assertTrue(mongoose.understood)
        self.assertEqual(read("Increases Agility and Intellect by 25 for 1 hr.").stats, {3: 25, 5: 25})
        self.assertEqual(read("Increases spell damage by up to 150 for 2 hrs.", kind="flask").stats, {42: 150})
        self.assertEqual(read("Increases damage done by Fire spells and effects by up to 40 for 30 min.").stats, {85: 40})
        self.assertEqual(read("Increases all resistances by 25 for 2 hrs.").stats, {51: 25, 52: 25, 54: 25, 55: 25, 56: 25})

    def test_percent_uses_the_rate_of_the_games_own_tooltips(self):
        self.assertEqual(read("Improves your chance to hit by 1% for 1 hr.").stats, {31: 10})
        self.assertEqual(read("Increases your chance to dodge by 1% for 1 hr.").stats, {13: 12})
        percent_of_armor = read("Increases Armor by 20% for 1 hr.")
        self.assertEqual((percent_of_armor.stats, percent_of_armor.unread), ({}, ["Increases Armor by N%"]))

    def test_what_is_no_stat_of_the_weights_is_kept_apart(self):
        titans = read("Increases the player's maximum health by 1,200 for 2 hrs. You can only have the effect of one "
                      "flask at a time. This effect persists through death.", kind="flask", family="Maximum health",
                      name="Flask of the Titans")
        self.assertEqual((titans.stats, titans.extras, titans.duration, titans.category, titans.unread),
                         ({}, {"max_health": 1200}, 7200, "flask", []))
        stone = read("Increase sharp weapon damage by 8 for 30 minutes.", kind="", family="", weapon=True)
        self.assertEqual((stone.extras, stone.category, stone.duration), ({"weapon_damage": 8}, "weapon", 1800))

    def test_weapon_oils(self):
        oil = read("While applied to target weapon it increases spell damage by up to 36 and spell critical strike "
                   "chance by 1% for 30 minutes.", kind="", family="", weapon=True)
        self.assertEqual((oil.stats, oil.spell_stats, oil.unread), ({42: 36}, {32: 14}, []),
                         "a critical strike of spells only is not a warrior's")
        mana = read("While applied to target weapon it restores 12 mana to the caster every 5 seconds and increases "
                    "healing done by up to 25 for 30 minutes.", kind="", family="", weapon=True)
        self.assertEqual((mana.stats, mana.unread), ({43: 12, 41: 25}, []))

    def test_food(self):
        soup = read("Restores 874 health over 27 sec. Must remain seated while eating. If you spend at least 10 seconds "
                    "eating you will become well fed and gain 8 Mana every 5 seconds for 15 min.", kind="food", family="Well Fed: other")
        self.assertEqual((soup.stats, soup.restores, soup.duration, soup.category, soup.unread),
                         ({43: 8}, {"health": 874}, 900, "food", []))
        two = read("Restores 1,933 health over 27 sec. If you spend at least 10 seconds eating you will become well fed "
                   "and gain 12 Stamina and Spirit for 15 min.", kind="food", family="Well Fed: Stamina")
        self.assertEqual(two.stats, {7: 12, 6: 12})

    def test_what_restores_and_its_cooldown(self):
        potion = read("Restores 1,050 to 1,750 health. (2 |4Min:Min; Cooldown)", kind="potion", family="Health")
        self.assertEqual((potion.restores, potion.cooldown, potion.category), ({"health": 1400}, 120, "healing"))
        self.assertEqual(read("Restores 1,350 to 2,250 mana. (2 Min Cooldown)", kind="potion", family="Mana").category, "mana")
        bandage = read("Heals 2,000 damage over 8 sec.", kind="bandage", family="Healing")
        self.assertEqual((bandage.restores, bandage.category), ({"health": 2000}, "bandage"))

    def test_a_condition_is_kept_with_what_it_limits(self):
        natural = read("Increases Stamina by 30 for 2 hrs. Improves your chance to hit by 2% while in Hyjal Summit.",
                       kind="flask", family="Stamina")
        self.assertEqual((natural.stats, natural.conditional, natural.condition),
                         ({7: 30}, {31: 20}, {"kind": "zone", "what": "Hyjal Summit"}))
        demons = read("Increases attack power against Demons by 120 for 5 min. (2 |4Min:Min; Cooldown)",
                      kind="potion", family="Attack power")
        self.assertEqual((demons.stats, demons.conditional, demons.condition, demons.category),
                         ({}, {38: 120}, {"kind": "creature", "what": "Demons"}, "combat"))

    def test_the_classes_an_item_is_for(self):
        rage = consumables.decode(["Mighty Rage Potion", "Use: Increases Rage by 45 to 75 and increases Strength by 60 for 20 sec.",
                                   "Classes: Warrior, Druid", "Requires Level 46"], kind="potion", family="Strength")
        self.assertEqual(rage.classes, ["WARRIOR", "DRUID"])
        self.assertEqual(rage.record()["classes"], ["WARRIOR", "DRUID"])
        free = consumables.decode(["Major Frenzy Potion", "Use: Increases Attack Power by 80 for 30 sec."], kind="potion")
        self.assertEqual(free.classes, [])
        self.assertNotIn("classes", free.record())

    def test_a_place_named_below_the_effect(self):
        bandage = consumables.decode(["Alterac Heavy Runecloth Bandage", "Requires First Aid (225)",
                                      "Use: Heals 2000 damage over 8 sec.", '"May only be used in Alterac Valley."'], kind="bandage")
        self.assertEqual((bandage.only, bandage.unread), ("Alterac Valley", []))

    def test_protection_is_situational(self):
        fire = read("Absorbs 1,950 to 3,250 fire damage. Lasts 1 hour. (2 |4Min:Min; Cooldown)", kind="potion", family="Protection: Fire")
        self.assertEqual((fire.category, fire.duration, fire.cooldown, fire.stats, fire.unread), ("situational", 3600, 120, {}, []))
        free = read("Makes you immune to Stun and Movement Impairing effects for the next 30 sec.", kind="potion")
        self.assertEqual((free.category, free.duration, free.unread), ("situational", 30, []))

    def test_what_is_not_understood_is_said_and_never_guessed(self):
        odd = read("Increases Agility by 25 and makes you feel lucky by 3 for 1 hr.")
        self.assertEqual((odd.stats, odd.unread), ({}, ["Increases Agility by N and makes you feel lucky by N"]),
                         "nothing of a sentence half understood")
        self.assertFalse(odd.understood)
        hidden = read("Increases your resistance to poison by 5 for 1 hr.")
        self.assertEqual((hidden.utility, len(hidden.unread)), ([], 1), "a number of something unknown is no utility")
        self.assertEqual(consumables.decode(["Plain Thing", "Requires Level 50"]).unread, ["no use text"])

    def test_the_wordings_the_game_really_uses(self):
        """Tooltips as the capture of 2026-11-18 (game build 1.60.1.70959) read them."""
        for text, kind, family, stats, others in (
                ("Drink to gain 25 Agility and Intellect. Lasts for 30 min.", "elixir", "Other", {3: 25, 5: 25}, {"duration": 1800}),
                ("Drink to increase your Strength and Agility by 18. Lasts for 30 min.", "elixir", "Other", {4: 18, 3: 18}, {}),
                ("Drink to increase your Spirit by 25 and chance to critically hit by 2%. Lasts for 30 min.", "elixir", "Spirit",
                 {6: 25, 32: 28}, {}),
                ("Increases Agility by 25 and chance to get a critical hit by 2%. Lasts for 30 min.", "elixir", "Agility",
                 {3: 25, 32: 28}, {}),
                ("Drink to restore 9 health and 10 mana every 5 sec. Lasts for 30 min.", "elixir", "Other", {46: 9, 43: 10}, {}),
                ("Drink to regenerate 20 mana every 5 sec. Lasts for 30 min.", "elixir", "Mana regeneration", {43: 20}, {}),
                ("Drink to gain 400 Maximum Health and 500 Armor. Lasts for 30 min.", "elixir", "Other", {"armor": 500},
                 {"extras": {"max_health": 400}}),
                ("Increases spell Holy damage by up to 40 for 30 min.", "elixir", "Holy spell damage", {84: 40}, {}),
                ("Drink to increase nature spell damage by up to 40. Lasts for 30 min.", "elixir", "Other", {86: 40}, {}),
                ("Increases your melee attack power by 35 and size for 20 min. (1 Min Cooldown)", "elixir", "Other", {38: 35},
                 {"cooldown": 60}),
                ("Increases Stamina by 15 for 15 min and gets you drunk to boot!", "food", "Other", {7: 15}, {"duration": 900}),
                ("Increases your Intellect by 10 and decreases your Stamina by 5 for 10 min.", "food", "Other", {5: 10, 7: -5}, {}),
                ("Increases Spell Healing by 88 for 30 sec. (2 Min Cooldown)", "potion", "Other", {41: 88}, {"category": "combat"}),
                ("Increases Rage by 45 to 75 and increases Strength by 60 for 20 sec.", "potion", "Other", {4: 60},
                 {"extras": {"rage": 60}, "category": "combat"}),
                ("Restores 1440 to 1760 mana and health.", "potion", "Health and mana", {},
                 {"restores": {"health": 1600, "mana": 1600}, "category": "healing"}),
                ("Restores 980 to 1260 health. This item may only be used in PvP Battlegrounds.", "potion", "Health", {},
                 {"only": "PvP Battlegrounds"}),
                ("Heals 2000 damage over 8 sec. Usable only inside Arathi Basin.", "bandage", "Healing", {}, {"only": "Arathi Basin"}),
                ("Restores 2148 health over 30 sec. Must remain seated while eating. If you spend at least 10 sec eating, you "
                 "will become well fed and gain 2% Critical Strike chance for 15 min. Additionally, experience gained from "
                 "kills is increased by 2%. (1 Sec Cooldown)", "food", "Well Fed: Critical strike", {32: 28}, {"duration": 900}),
                ("Imbue a staff with magic for 1 hour, increasing your chance to critically hit by 1.0%.", "scroll",
                 "Weapon imbues", {32: 14}, {"duration": 3600, "category": "weapon"}),
                ("Imbue a staff with magic for 1 hour, increasing damage done with Fire spells and effects by up to 20.", "scroll",
                 "Weapon imbues", {85: 20}, {}),
                ("Increase the damage of a blunt weapon by 8 for 30 minutes. (1 Sec Cooldown)", "", "", {},
                 {"extras": {"weapon_damage": 8}}),
                ("Increase critical chance on a melee weapon by 2% for 30 minutes. (1 Sec Cooldown)", "", "", {32: 28}, {}),
        ):
            with self.subTest(text):
                reading = read(text, kind=kind, family=family, weapon=not kind)
                self.assertEqual((reading.stats, reading.unread), (stats, []))
                for name, value in others.items():
                    self.assertEqual(getattr(reading, name), value, name)

    def test_an_and_inside_an_effect_is_not_a_cut(self):
        oil = read("While applied to target weapon it increases spell damage and healing by up to 36 and increases Spell "
                   "Critical chance by 1%. Lasts for 30 minutes. (1 Sec Cooldown)", kind="", family="", weapon=True)
        self.assertEqual((oil.stats, oil.spell_stats, oil.duration, oil.unread), ({45: 36}, {32: 14}, 1800, []))

    def test_the_natural_flasks_hold_their_bonus_in_three_zones_only(self):
        where = "While in Mount Hyjal, Hyjal Summit, and the Barrow Deeps, you also gain"
        for bonus, conditional in (("2% Hit Chance", {31: 20}), ("2% Critical Strike Chance", {32: 28}), ("2% Haste", {36: 20}),
                                   ("2% reduced chance to be dodged or parried", {consumables.LESS_DODGED: 2})):
            flask = read(f"Increases your Stamina by 30. {where} {bonus}. Lasts for 2 hour. You can only have the effect of "
                         "one flask at a time. This effect persists through death.", kind="flask", family="Stamina")
            self.assertEqual((flask.stats, flask.conditional, flask.duration, flask.unread), ({7: 30}, conditional, 7200, []))
            self.assertEqual(flask.condition, {"kind": "zone", "what": "Mount Hyjal, Hyjal Summit, and the Barrow Deeps"})

    def test_a_grenade_is_no_weapon_oil(self):
        grenade = read("Inflicts 300 to 500 Holy damage to targets in a 3 yds radius.", kind="explosive", family="Weapon imbues")
        self.assertEqual(grenade.category, "other")

    def test_the_spell_stands_in_for_a_tooltip_without_a_use_line(self):
        reading = consumables.decode(["Odd Elixir"], [(1234, "Odd", "Increases Strength by 8 for 1 hr.")], "elixir", "Strength")
        self.assertEqual(reading.stats, {4: 8})


SAVED = "\n".join([
    'EasyBISCaptureDB = {', '["meta"] = "1|1.60.1|70938|enUS|2026-11-18 09:00",', '["items"] = {',
    r'[13452] = "Elixir of the Mongoose\nUse: Increases Agility by 25 and critical strike chance by 2% for 1 hr.'
    r'\n#use 17538	Mongoose	Increases Agility.\n#stats ",',
    r'[13510] = "Flask of the Titans\nUse: Increases maximum health by 1200 for 2 hrs.\n#stats ",',
    r'[14529] = "Runecloth Bandage\nUse: Heals 900 damage over 8 sec.\n#stats ",',
    r'[12404] = "Dense Sharpening Stone\nUse: Wibbles your weapon by 8 for 30 min.\n#stats ",',
    '},', '}', ''])


class ImportTest(unittest.TestCase):
    def setUp(self):
        self.db = tiny_db()
        self.db._consumables = fixture()
        self.parsed = capture.parse_saved(SAVED)

    def test_the_spell_line_is_no_tooltip_line(self):
        self.assertEqual(self.parsed["uses"], {MONGOOSE: [(17538, "Mongoose", "Increases Agility.")]})
        self.assertEqual(self.parsed["items"][MONGOOSE][0],
                         ["Elixir of the Mongoose", "Use: Increases Agility by 25 and critical strike chance by 2% for 1 hr."])
        self.assertEqual(capture.parse_saved(SAVED.replace("\\n#use 17538\tMongoose\tIncreases Agility.", ""))["uses"], {},
                         "a capture made before the tool asked for the spell is still read")

    def test_a_capture_is_decoded_and_kept(self):
        result = consumables.read_capture(self.db, self.parsed)
        self.assertEqual((result.read, result.understood), (4, 3))
        self.assertEqual(result.unread, {"Wibbles your weapon by N": 1})
        self.assertIn(OIL, result.absent)
        self.assertEqual(result.by_category["weapon"], 1)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "consumables.json"
            consumables.save(result, "2026-11-18", path)
            self.assertNotIn(b"\r", path.read_bytes())
            kept = consumables.load(path)
            self.assertEqual((kept["build"], kept["date"]), ("1.60.1.70938", "2026-11-18"))
            self.assertEqual(kept["items"][MONGOOSE]["stats"], {"3": 25, "32": 28})
            self.assertEqual(kept["items"][STONE]["unread"], ["Wibbles your weapon by N"])
            # another capture replaces what it read again, and leaves the rest
            again = consumables.read_capture(self.db, capture.parse_saved(SAVED.replace("Agility by 25", "Agility by 30")))
            del again.readings[TITANS]
            consumables.save(again, "2026-11-19", path)
            kept = consumables.load(path)
            self.assertEqual(kept["items"][MONGOOSE]["stats"]["3"], 30)
            self.assertIn(TITANS, kept["items"])

    def test_another_language_is_not_guessed_at(self):
        parsed = capture.parse_saved(SAVED.replace("enUS", "frFR"))
        result = consumables.read_capture(self.db, parsed)
        self.assertEqual((result.read, result.readings), (0, {}))

    def test_the_audit_says_where_the_game_differs(self):
        catalogue = {
            1: {"name": "Elixir of the Mongoose", "kind": "elixir", "family": "Agility", "strength": 25.0},
            2: {"name": "Weak Elixir", "kind": "elixir", "family": "Strength", "strength": 20.0},
            3: {"name": "Wrong Elixir", "kind": "elixir", "family": "Spirit", "strength": 10.0},
            4: {"name": "Major Healing Potion", "kind": "potion", "family": "Health", "strength": 1400.0},
            5: {"name": "Thin Potion", "kind": "potion", "family": "Health", "strength": 1000.0},
            6: {"name": "Soup", "kind": "food", "family": "Well Fed: Stamina", "strength": 874.0},
            7: {"name": "Murky Elixir", "kind": "elixir", "family": "Agility", "strength": 5.0},
            8: {"name": "Renamed", "kind": "elixir", "family": "Other", "strength": 0.0},
            10: {"name": "Ranged Potion", "kind": "potion", "family": "Health", "strength": 1750.0},
            11: {"name": "Mender", "kind": "potion", "family": "Healing", "strength": 88.0},
            12: {"name": "Harvest Bread", "kind": "food", "family": "Health", "strength": 2.0},
        }
        items = {
            1: {"name": "Elixir of the Mongoose", "text": "", "stats": {"3": 25, "32": 28}},
            2: {"name": "Weak Elixir", "text": "", "stats": {"4": 30}},
            3: {"name": "Wrong Elixir", "text": "Increases Armor by 5", "stats": {"armor": 5}},
            4: {"name": "Major Healing Potion", "text": "", "restores": {"health": 1400}},
            5: {"name": "Thin Potion", "text": "", "restores": {"health": 700}},
            6: {"name": "Soup", "text": "", "stats": {"7": 12}, "restores": {"health": 874}},
            7: {"name": "Murky Elixir", "text": "", "unread": ["Does N things"]},
            8: {"name": "New Name", "text": "", "utility": ["Makes you glow"]},
            9: {"name": "Dense Sharpening Stone", "text": "", "extras": {"weapon_damage": 8}},
            10: {"name": "Ranged Potion", "text": "", "restores": {"health": 1400}, "ranges": {"health": [1050, 1750]}},
            11: {"name": "Mender", "text": "", "stats": {"41": 88}},
            12: {"name": "Harvest Bread", "text": "", "utility": ["Restores 2% of your health per second"]},
        }
        found = {(entry.item, entry.kind) for entry in consumables.audit(items, catalogue)}
        self.assertEqual(found, {(1, "hidden"), (2, "strength"), (3, "family"), (5, "strength"), (7, "unread"), (8, "name")})
        self.assertEqual(consumables.audit_summary(consumables.audit(items, catalogue)),
                         "1 family, 1 hidden, 1 name, 2 strength, 1 unread")


@unittest.skipIf(lupa is None, "lupa is not installed")
class ToolTest(unittest.TestCase):
    """Capture.lua against stand-ins of the game, with the spell an item casts."""

    def setUp(self):
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.stub = self.lua.execute(CAPTURE_STUB)
        self.lua.execute("""
            spells, descriptions, loads = {}, {}, {}
            C_Item.GetItemSpell = function(id) if spells[id] then return "Potion", spells[id] end end
            C_Spell = {
                GetSpellDescription = function(spell) return descriptions[spell] end,
                RequestLoadSpellData = function(spell) loads[#loads + 1] = spell end,
            }
        """)
        self.source = (BUILD / "capture_addon" / "Capture.lua").read_text(encoding="utf-8")
        self.table = self.lua.table_from

    def add(self, item, *lines):
        self.stub.add(item, True, self.table([self.table([line]) for line in lines]), None)

    def play(self, steps=400, each=None):
        for step in range(steps):
            if self.stub.script is None:
                return
            if each:
                each(step)
            self.stub.script(None, 0.25)
        self.fail("the capture never ended")

    def test_the_spells_description_is_kept_and_waited_for(self):
        globals_ = self.lua.globals()
        self.add(100, "Elixir", "Use: Increases Agility by 25 for 1 hr.")
        self.add(101, "Slow Elixir", "Use: Increases Strength by 8 for 1 hr.")
        self.add(102, "Mute Elixir", "Use: Increases Spirit by 8 for 1 hr.")
        self.add(103, "Plain Thing", "Vendor trash")
        globals_.spells[100], globals_.spells[101], globals_.spells[102] = 9100, 9101, 9102
        globals_.descriptions[9100] = "Increases Agility."
        self.stub.run(self.source, "100 101 102 103")
        globals_.SlashCmdList.EASYBISCAPTURE("")

        def arrive(step):
            if step == 3:
                globals_.descriptions[9101] = "Increases\nStrength."

        self.play(each=arrive)
        saved = globals_.EasyBISCaptureDB["items"]
        self.assertIn("\n#use 9100\tPotion\tIncreases Agility.\n#stats ", saved[100])
        self.assertIn("\n#use 9101\tPotion\tIncreases Strength.\n#stats ", saved[101], "waited for, on one line")
        self.assertIn("\n#use 9102\tPotion\t\n#stats ", saved[102], "the description never came: the tooltip is kept")
        self.assertNotIn("#use", saved[103])
        self.assertIn(9102, list(globals_.loads.values()), "the game was asked for the spell")
        parsed = capture.parse_saved(saved_variable(globals_.EasyBISCaptureDB))
        self.assertEqual(parsed["uses"][100], [(9100, "Potion", "Increases Agility.")])
        self.assertEqual(parsed["uses"][102], [(9102, "Potion", "")])
        self.assertEqual(parsed["items"][102][0], ["Mute Elixir", "Use: Increases Spirit by 8 for 1 hr."])

    def test_a_list_that_grew_does_not_ask_again_for_what_the_game_lacks(self):
        globals_ = self.lua.globals()
        for item in range(1, 9):
            self.add(item, f"Piece {item}", "Chest")
        self.stub.run(self.source, "1 2 3 4 5 6 7 8")
        globals_.SlashCmdList.EASYBISCAPTURE("")
        self.play()
        for item in range(50, 56):
            self.stub.unknown[item] = True   # numbers the game's own table does not list
        self.add(9, "Potion", "Use: Restores 5 health.")
        self.stub.requests = 0
        self.stub.run(self.source, "9 1 2 3 4 5 6 7 8 50 51 52 53 54 55")
        globals_.SlashCmdList.EASYBISCAPTURE("")
        self.play()
        self.assertIn(9, list(globals_.EasyBISCaptureDB["items"].keys()))
        self.assertEqual(globals_.EasyBISCaptureDB.absent, "50 51 52 53 54 55", "six the game lacks are fewer than nine it has")


if __name__ == "__main__":
    unittest.main(verbosity=1)
