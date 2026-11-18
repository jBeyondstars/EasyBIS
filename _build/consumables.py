"""What the consumables do, read in the game.

ForeverDB's catalogue (Consumables.lua) says which consumables exist, with one effect and one number each: too
little to rank them. Elixir of the Mongoose is "Agility 25" there and its critical strike is missing, a food's
number is the health it restores and not the stat it gives. So the tooltips are read in the game with the
developer's capture tool (capture.py, _build/capture_addon) and decoded here:

    decode(lines, uses, ...)    one tooltip -> a Reading: its stats, what it restores, how long it lasts, its
                                cooldown, its category, and the condition its effect depends on
    read_capture(db, parsed)    every consumable of a capture, with what was not understood
    audit(kept, catalogue)      where the game disagrees with the catalogue's family and strength

What was read is kept in corrections/consumables.json. A phrase that is not understood is counted and reported
by its wording, numbers as N. It is never guessed: the item keeps what was understood of it and says what was not.

What is read (consumable_ids): the catalogue's rows, but for the Season of Discovery leftovers, the kind "enhance"
(enchant scrolls, armor kits and spikes are permanent, and the Enchants tab's business) and alcohol; and of each
kind and family of effect the ones of level FROM_LEVEL or more. A family with none of those keeps its highest level.
At any level are kept a row of no level at all (a level of 0 says nothing), a row that the catalogue makes as
strong as the best of its family, and every food and drink that makes you well fed: the catalogue's number for
those is the health restored, so nothing tells a weak buff from a strong one before the game is read. To these
come the weapon stones and oils, which the catalogue lacks: the items that Recipes.lua makes and whose names say so,
and the few potions of ALWAYS_READ.

Effects in percent are written in the rating the game's items use, at the rates of the game's own tooltips and
stat tables (RATING_PER_PERCENT). An effect that holds for spells only is kept apart in "spell_stats". A conditional
effect (one zone, one kind of creature) is kept apart in "conditional", with its condition, and is no part of
"stats". Nothing here says how consumables stack, or which of them go together.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

FILE = Path(__file__).resolve().parent / "corrections" / "consumables.json"
ABOUT = ("What the consumables do, read from their tooltips in the game with the EasyBIS_Capture tool "
         "(_build/capture_addon) and decoded by _build/consumables.py. \"unread\" holds the phrases not understood. "
         "Written by `python build.py --import-capture`: do not edit.")

FROM_LEVEL = 40        # the level from which a catalogue row is read whatever else its family holds
PERMANENT_KIND = "enhance"
NOT_READ_FAMILIES = ("Alcohol",)
_WEAPON_ITEM = re.compile(r"Sharpening Stone|Weightstone|Wizard Oil|Mana Oil")
# Free Action, Swiftness and Restorative potions: of a low level, and what a raid or a battleground asks for at the cap.
ALWAYS_READ = (5634, 2459, 9030)

# Stat ids are ForeverDB's, which are the game's item stats (capture.GAME_KEYS); "armor" is ForeverDB's weight of that name.
AGILITY, STRENGTH, INTELLECT, SPIRIT, STAMINA = 3, 4, 5, 6, 7
DODGE, PARRY, BLOCK, HIT, CRIT, HASTE = 13, 14, 15, 31, 32, 36
ATTACK_POWER, RANGED_ATTACK_POWER, HEALING, SPELL_DAMAGE, MANA_REGEN, SPELL_POWER, HEALTH_REGEN = 38, 39, 41, 42, 43, 45, 46
BLOCK_VALUE = 48
ARMOR = "armor"
RESISTANCES = {"fire": 51, "frost": 52, "shadow": 54, "nature": 55, "arcane": 56}
SCHOOLS = {"holy": 84, "fire": 85, "nature": 86, "frost": 87, "shadow": 88, "arcane": 89}

# Rating for 1%, as the game's tooltips and stat tables show them side by side (the capture of 2026-11-15:
# "critical strike by 1.0%" is 14 of ITEM_MOD_CRIT_RATING_SHORT on 476 items, and so on).
RATING_PER_PERCENT = {CRIT: 14, HIT: 10, DODGE: 12, PARRY: 15, BLOCK: 5, HASTE: 10}

MAX_HEALTH, MAX_MANA, WEAPON_DAMAGE = "max_health", "max_mana", "weapon_damage"   # read, and no stat of the weights
RAGE = "rage"
# In percent, as the game says it: no tooltip read so far shows this one next to its rating, so no rate is assumed.
LESS_DODGED = "less_dodged_or_parried_percent"

_WORDS = {  # what a tooltip calls a stat -> the stat
    "agility": AGILITY, "strength": STRENGTH, "intellect": INTELLECT, "spirit": SPIRIT, "stamina": STAMINA,
    "armor": ARMOR, "attack power": ATTACK_POWER, "melee attack power": ATTACK_POWER,
    "ranged attack power": RANGED_ATTACK_POWER,
    "spell damage": SPELL_DAMAGE, "magical damage": SPELL_DAMAGE,
    "damage done by magical spells and effects": SPELL_DAMAGE, "damage done by spells and effects": SPELL_DAMAGE,
    "healing": HEALING, "healing done": HEALING, "healing power": HEALING, "healing spells": HEALING,
    "healing done by magical spells and effects": HEALING, "healing done by spells and effects": HEALING,
    "spell healing": HEALING, "effect of healing spells": HEALING,
    "spell power": SPELL_POWER, "spell damage and healing": SPELL_POWER, "healing and spell damage": SPELL_POWER,
    "damage and healing done by magical spells and effects": SPELL_POWER,
    "critical strike chance": CRIT, "chance to get a critical strike": CRIT, "critical strike": CRIT,
    "critical strike rating": CRIT, "crit": CRIT, "crit chance": CRIT,
    "critical strike chance of a melee weapon": CRIT, "critical chance on a melee weapon": CRIT,
    "critical chance": CRIT, "chance to critically hit": CRIT, "chance to get a critical hit": CRIT,
    "reduced chance to be dodged or parried": LESS_DODGED,
    "chance to hit": HIT, "hit chance": HIT, "hit": HIT, "hit rating": HIT,
    "chance to dodge": DODGE, "chance to dodge an attack": DODGE, "dodge chance": DODGE, "dodge": DODGE,
    "chance to parry": PARRY, "chance to parry an attack": PARRY, "parry chance": PARRY, "parry": PARRY,
    "chance to block": BLOCK, "chance to block attacks with a shield": BLOCK, "block chance": BLOCK, "block": BLOCK,
    "block value": BLOCK_VALUE, "block value of your shield": BLOCK_VALUE,
    "attack speed and casting speed": HASTE, "haste": HASTE, "haste rating": HASTE,
    "mana regeneration": MANA_REGEN, "mana per 5 sec": MANA_REGEN, "health regeneration": HEALTH_REGEN,
    "health per 5 sec": HEALTH_REGEN,
    "maximum health": MAX_HEALTH, "max health": MAX_HEALTH, "health": MAX_HEALTH,
    "maximum mana": MAX_MANA, "max mana": MAX_MANA, "mana": MAX_MANA,
    "weapon damage": WEAPON_DAMAGE, "sharp weapon damage": WEAPON_DAMAGE, "blunt weapon damage": WEAPON_DAMAGE,
    "damage of a blunt weapon": WEAPON_DAMAGE, "damage of a sharp weapon": WEAPON_DAMAGE,
    "melee damage": WEAPON_DAMAGE,
}
for _school, _stat in RESISTANCES.items():
    _WORDS[f"{_school} resistance"] = _stat
    _WORDS[f"resistance to {_school}"] = _stat
for _school, _stat in SCHOOLS.items():
    _WORDS[f"{_school} spell damage"] = _stat
    _WORDS[f"{_school} damage"] = _stat
    _WORDS[f"spell {_school} damage"] = _stat
    _WORDS[f"damage done by {_school} spells and effects"] = _stat
    _WORDS[f"damage done with {_school} spells and effects"] = _stat
_SPELL_ONLY = {  # effects on spells alone
    "spell critical strike chance": CRIT, "critical strike chance with spells": CRIT,
    "chance to get a critical strike with spells": CRIT, "spell critical strike rating": CRIT,
    "spell crit": CRIT, "spell crit chance": CRIT, "spell critical chance": CRIT,
    "spell hit chance": HIT, "chance to hit with spells": HIT, "spell hit rating": HIT, "spell hit": HIT,
}
_ALL_RESISTANCES = ("all resistances", "resistance to all schools of magic", "all magical resistances", "resistances")
_NOT_A_STAT = (MAX_HEALTH, MAX_MANA, WEAPON_DAMAGE, RAGE, LESS_DODGED)

_CREATURES = "Demons|Undead|Beasts|Elementals|Dragonkin|Humanoids|Giants|Mechanicals"
_SECONDS = {"sec": 1, "second": 1, "min": 60, "minute": 60, "hr": 3600, "hour": 3600, "day": 86400}
_TIME = r"(\d+(?:\.\d+)?) (sec|second|min|minute|hr|hour|day)s?\b"
_COOLDOWN = re.compile(rf"\(\s*{_TIME}\.? Cooldown\s*\)", re.I)
_FOR_TIME = re.compile(rf"[,;]? (?:for|lasts?)(?: the next| up to)? {_TIME}(?= and gets you drunk to boot!?$|\.?$)", re.I)
_LASTS = re.compile(rf"^Lasts?(?: for)?(?: up to)? {_TIME}\.?$", re.I)
_GRAMMAR = re.compile(r"\|4([^:;|]*):([^:;|]*);")
_THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}\b)")
_SENTENCE = re.compile(r"(?<=[.!])\s+")

# Sentences that say how an item is used, not what it does.
_NOTES = re.compile(
    r"^(Must remain seated|You can only have|This effect persists|Only one|Can only be|Cannot be|May only be|"
    r"Requires|Usable|Use on|Counts as|Guardian Elixir|Battle Elixir|Persists through death|Effect persists|"
    r"Only usable|Only active|Item will|Not usable|Does not stack|Doesn't stack|Stacks? with|Does not remove|"
    r"Additionally, experience|Any damage will break|Eat me|Also packs|You should also|The mine has|"
    r"Both you and the target)", re.I)
_ONLY = re.compile(r"^(?:Usable only (?:inside|in)|(?:This item )?may only be used in) (.+)$", re.I)
_CLASSES = re.compile(r"^Classes: (.+)$")
# What protects or helps without a stat: understood, and listed for what it is.
_UTILITY = re.compile(
    r"\b(absorbs?|immune|immunity|invulnerab|invisib|underwater|water breathing|breathe|walk on water|water walking|"
    r"detect|stealth|movement speed|run speed|swim speed|removes?|cures?|dispels?|purges?|resurrect|summons?|"
    r"your level to|protecting you|imbiber heals|shows the location|belch|throw|unleash|suffer|dealing \d|"
    r"% of your|\bskill\b|locked doors|open a lock|firework|"
    r"teleports?|polymorph|sleep|stun|knock|slow fall|levitat|fear|charm|poison|disease|curse|magic effect|"
    r"damage to all|damage to the|deals? \d|inflicts?|causes? \d|hurls?)", re.I)

_RESTORE = re.compile(r"^(?:Instantly )?(?:Restores?|Heals?|Regenerates?)(?: you)?(?: for)? (\d+)(?: to (\d+))? "
                      r"(health|mana|life|damage)(?: (?:over|during) \d+ (?:sec|second)s?)?(?: and (\d+)(?: to (\d+))? "
                      r"(health|mana|life))?(?: (?:over|during) \d+ (?:sec|second)s?)?$", re.I)
_BOTH_RESTORED = re.compile(r"^Restores? (\d+) to (\d+) (?:mana and health|health and mana)$", re.I)
_BOTH_REGEN = re.compile(r"^Restores? (\d+) health and (\d+) mana every 5 (?:sec|second)s?$", re.I)
_RAGE = re.compile(r"^(?:Increases? )?Rage by (\d+) to (\d+)$", re.I)
_REGEN = re.compile(r"^(?:(?:Restores?|Regenerates?|Heals?|Gain)(?: you)?(?: for)? )?(\d+) (health|mana)"
                    r"(?: to the caster)? (?:every|per) 5 (?:sec|second)s?$", re.I)
_WELL_FED = re.compile(r"^If you spend at least \d+ sec(?:ond)?s? (?:eating|drinking|consuming)[^,]*?,? you will become "
                       r"well fed and gain (.+)$|^(?:You )?(?:will )?become well fed and gain (.+)$", re.I)
_ZONE_RULES = (
    re.compile(r"^(?:While|When) (?:you are |you're )?(?:in|inside|within) (?P<zone>.+), (?P<rest>.+)$", re.I),
    re.compile(r"^(?P<rest>.+?),? (?:while|when) (?:you are |you're )?(?:in|inside|within) (?P<zone>.+)$", re.I),
    re.compile(r"^(?P<rest>.+?),? only (?:in|inside|within) (?P<zone>.+)$", re.I),
    re.compile(r"^(?P<rest>.+?) in (?P<zone>(?:the )?Hyjal\b.*)$", re.I),
)
_AGAINST = re.compile(rf"^(?P<rest>.+?) (?:against|versus|vs\.?) (?P<creature>{_CREATURES})\b(?P<tail>.*)$", re.I)
_MOVING = re.compile(r"movement speed|run speed", re.I)
_APPLIED = re.compile(r"^(?:While|When) applied to (?:a |an |the |your |target )*[\w -]*weapon,? (?:it )?", re.I)
_LEAD = re.compile(r"^(?:Also\s+)?(?:you (?:also )?gain|Increases?|Raises?|Improves?|Boosts?|Enhances?|Adds?|Grants?|Gives?|"
                   r"Gain)\s+", re.I)
_LOWER = re.compile(r"^(?:Decreases?|Reduces?)\s+", re.I)
_DRINK = re.compile(r"^Drink to\s+", re.I)
_IMBUE = re.compile(rf"^Imbue a [\w ]+? for {_TIME}, increasing (.+)$", re.I)
_JOINS = re.compile(r",\s*and\s+|\s+and\s+|,\s+")
_ASIDE = re.compile(r" and (?:size|gets you drunk to boot!?)$", re.I)   # what comes with a stat and is none
_TARGET = re.compile(r"^(?:your |the player's |the target's |the wearer's |target's |player's |all |the )+", re.I)
_BY = re.compile(r"^(?P<what>.+?) by (?:up to )?(?P<n>\d+(?:\.\d+)?)(?P<percent>%)?(?: (?:points?|rating))?$", re.I)
_AMOUNT = re.compile(r"^\+?(?P<n>\d+(?:\.\d+)?)(?P<percent>%)? (?P<what>.+)$")


def _number(value: float):
    return int(value) if float(value).is_integer() else round(float(value), 2)


def _seconds(amount: str, unit: str) -> int:
    return int(float(amount) * _SECONDS[unit.lower()])


def clean(text: str) -> str:
    """A tooltip's line without the game's grammar marks, thousands separators and double spaces."""
    text = _GRAMMAR.sub(lambda match: match.group(1), text.replace(" ", " "))
    return re.sub(r"\s+", " ", _THOUSANDS.sub("", text)).strip()


def _template(text: str) -> str:
    return re.sub(r"\d+(?:\.\d+)?", "N", text)


@dataclass
class Reading:
    """What one consumable's tooltip says."""
    name: str = ""
    stats: dict = field(default_factory=dict)        # stat -> value, for everyone and everywhere
    spell_stats: dict = field(default_factory=dict)  # stat -> value, that holds for spells only
    conditional: dict = field(default_factory=dict)  # stat -> value, that holds under `condition` only
    condition: dict | None = None                    # {"kind": "zone" or "creature", "what": the place or the creature}
    only: str = ""                                   # the one place the item can be used in at all
    classes: list = field(default_factory=list)      # the class tokens that can use it, when the tooltip names them
    extras: dict = field(default_factory=dict)       # maximum health or mana, weapon damage: read, and no weighted stat
    restores: dict = field(default_factory=dict)     # "health" or "mana" -> the average amount
    ranges: dict = field(default_factory=dict)       # "health" or "mana" -> [lowest, highest], when the game gives a range
    utility: list = field(default_factory=list)      # the sentences that protect or help without a stat
    duration: int = 0                                # seconds
    cooldown: int = 0                                # seconds
    category: str = "other"
    text: str = ""                                   # the "Use:" text, cleaned
    unread: list = field(default_factory=list)       # what was not understood, numbers as N

    @property
    def understood(self) -> bool:
        return not self.unread and bool(self.stats or self.spell_stats or self.conditional or self.extras
                                        or self.restores or self.utility)

    def record(self) -> dict:
        """The form corrections/consumables.json keeps; what is empty is left out."""
        record = {"name": self.name, "category": self.category, "text": self.text}
        for key in ("stats", "spell_stats", "conditional", "condition", "only", "classes", "extras", "restores", "ranges",
                    "utility", "duration", "cooldown", "unread"):
            value = getattr(self, key)
            if value:
                record[key] = {str(stat): number for stat, number in value.items()} if isinstance(value, dict) \
                    and key != "condition" else value
        return record


def _stat_of(words: str):
    """(stat, holds for spells only) for what a tooltip calls a stat; (None, False) when it is not known."""
    words = _TARGET.sub("", words.strip().rstrip(".")).lower()
    if words in _SPELL_ONLY:
        return _SPELL_ONLY[words], True
    return _WORDS.get(words), False


def _add(target: dict, stat, value) -> None:
    target[stat] = _number(target.get(stat, 0) + value)


class _Decoder:
    """One tooltip's sentences into a Reading."""

    def __init__(self, reading: Reading) -> None:
        self.reading = reading

    def _put(self, stat, spell_only: bool, value: float, percent: bool, condition: dict | None) -> bool:
        """Keeps one effect; False when it is in percent of something that has no rate."""
        reading = self.reading
        if percent and stat != LESS_DODGED:
            if stat not in RATING_PER_PERCENT:
                return False
            value *= RATING_PER_PERCENT[stat]
        if condition:
            reading.condition = condition
            _add(reading.conditional, stat, value)
        elif spell_only:
            _add(reading.spell_stats, stat, value)
        elif stat in _NOT_A_STAT:
            _add(reading.extras, stat, value)
        else:
            _add(reading.stats, stat, value)
        return True

    def _stats_by(self, what: str, amount: str, percent: str | None, condition: dict | None) -> bool:
        """"Agility and Intellect" by the same amount; False when one of the names is not known."""
        value = float(amount)
        words = _TARGET.sub("", what.strip()).lower()
        if words in _ALL_RESISTANCES:
            if percent:
                return False
            for stat in RESISTANCES.values():
                self._put(stat, False, value, False, condition)
            return True
        whole = _stat_of(what)
        if whole[0] is not None:
            return self._put(whole[0], whole[1], value, bool(percent), condition)
        names = [part for part in re.split(r",\s*(?:and\s+)?|\s+and\s+", what) if part.strip()]
        found = [_stat_of(name) for name in names]
        if len(names) < 2 or any(stat is None for stat, _ in found):
            return False
        return all([self._put(stat, spell, value, bool(percent), condition) for stat, spell in found])

    def _clause(self, clause: str, condition: dict | None) -> bool:
        clause = clause.strip().rstrip(".")
        rage = _RAGE.match(clause)
        if rage and not condition:
            _add(self.reading.extras, RAGE, (float(rage[1]) + float(rage[2])) / 2)
            return True
        lower = _LOWER.match(clause)
        if lower:
            by = _BY.match(clause[lower.end():])
            stat, spell = _stat_of(by["what"]) if by and not by["percent"] else (None, False)
            return stat is not None and self._put(stat, spell, -float(by["n"]), False, condition)
        led = _LEAD.sub("", clause)
        by = _BY.match(led)
        if by and self._stats_by(by["what"], by["n"], by["percent"], condition):
            return True
        amount = _AMOUNT.match(led)
        return bool(amount and self._stats_by(amount["what"], amount["n"], amount["percent"], condition))

    def _part(self, part: str, condition: dict | None) -> bool:
        return (not condition and self._restore(part.strip())) or self._clause(part, condition)

    def _effects(self, sentence: str, condition: dict | None) -> bool:
        """All of a sentence's effects, or nothing of it: it is split only where each part is understood."""
        parts = self._parts(sentence, condition)
        return bool(parts) and all([self._part(part, condition) for part in parts])

    def _parts(self, sentence: str, condition: dict | None) -> list | None:
        """The sentence cut into effects. An "and" may also be inside one ("spell damage and healing by up to 36")."""
        if _Decoder(Reading())._part(sentence, condition):
            return [sentence]
        for cut in _JOINS.finditer(sentence):
            left = sentence[:cut.start()]
            if left.strip() and _Decoder(Reading())._part(left, condition):
                rest = self._parts(sentence[cut.end():], condition)
                if rest:
                    return [left, *rest]
        return None

    def _restore(self, sentence: str) -> bool:
        both = _BOTH_RESTORED.match(sentence)
        if both:
            average = _number((float(both[1]) + float(both[2])) / 2)
            self.reading.restores.update(health=average, mana=average)
            self.reading.ranges.update(health=[int(both[1]), int(both[2])], mana=[int(both[1]), int(both[2])])
            return True
        both = _BOTH_REGEN.match(sentence)
        if both:
            return self._put(HEALTH_REGEN, False, float(both[1]), False, None) \
                and self._put(MANA_REGEN, False, float(both[2]), False, None)
        regen = _REGEN.match(sentence)
        if regen:
            return self._put(MANA_REGEN if regen[2].lower() == "mana" else HEALTH_REGEN, False, float(regen[1]), False, None)
        match = _RESTORE.match(sentence)
        if not match:
            return False
        for low, high, what in ((match[1], match[2], match[3]), (match[4], match[5], match[6])):
            if low:
                key = "mana" if what.lower() == "mana" else "health"
                average = (float(low) + float(high or low)) / 2
                self.reading.restores[key] = _number(self.reading.restores.get(key, 0) + average)
                if high:
                    self.reading.ranges[key] = [int(low), int(high)]
        return True

    def sentence(self, sentence: str) -> None:
        reading = self.reading
        sentence = sentence.strip().rstrip(".").strip()
        only = _ONLY.match(sentence)
        if only:
            reading.only = only[1]
            return
        if not sentence or _NOTES.match(sentence):
            return
        sentence = _DRINK.sub("", sentence)
        imbue = _IMBUE.match(sentence)
        if imbue:
            reading.duration = _seconds(imbue[1], imbue[2])
            sentence = imbue[3]
        lasts = _LASTS.match(sentence)
        if lasts:
            reading.duration = _seconds(lasts[1], lasts[2])
            return
        well_fed = _WELL_FED.match(sentence)
        if well_fed:
            sentence = (well_fed[1] or well_fed[2]).strip()
        sentence = _APPLIED.sub("", sentence)
        timed = _FOR_TIME.search(sentence)
        if timed:
            reading.duration = _seconds(timed[1], timed[2])
            sentence = sentence[:timed.start()].strip()
        sentence = _ASIDE.sub("", sentence)

        condition = None
        for rule in _ZONE_RULES:
            zone = rule.match(sentence)
            if zone:
                condition, sentence = {"kind": "zone", "what": zone["zone"].strip()}, zone["rest"].strip()
                break
        against = _AGAINST.match(sentence)
        if against:
            condition = {"kind": "creature", "what": against["creature"].capitalize()}
            sentence = f"{against['rest'].strip()} {against['tail'].strip()}".strip()

        if self._effects(sentence, condition):
            return
        # "Increases <something> by 5" is a stat this file does not know, whatever words it holds
        names_a_stat = _LEAD.match(sentence) and _BY.match(_LEAD.sub("", sentence)) and not _MOVING.search(sentence)
        if _UTILITY.search(sentence) and not names_a_stat:
            reading.utility.append(sentence)
            return
        reading.unread.append(_template(sentence))


def category_of(kind: str, family: str, reading: Reading, weapon: bool = False) -> str:
    """Where a consumable belongs: flask, elixir, food, scroll, weapon, combat, healing, mana, bandage,
    situational, or other (what the tab does not list)."""
    powers = bool(reading.stats or reading.spell_stats or reading.conditional or reading.extras)
    if weapon or (kind == "scroll" and family == "Weapon imbues"):
        return "weapon"
    if kind == "bandage":
        return "bandage"
    if kind == "potion":
        if reading.restores.get("health"):
            return "healing"
        if reading.restores.get("mana"):
            return "mana"
        return "combat" if powers and not reading.utility else "situational"
    if kind in ("flask", "elixir", "scroll"):
        if family in ("Familiars", "Teleports"):
            return "other"
        return kind if powers or not reading.utility else "situational"
    if kind in ("food", "drink"):
        return "food"
    return "other"


def _read_restrictions(lines: list, reading: Reading) -> None:
    """Who can use an item, and where when the game says so outside its "Use:" text, in the quoted line below it."""
    for line in lines:
        text = clean(line.split("\t", 1)[0])
        classes = _CLASSES.match(text)
        if classes:
            reading.classes = [name.strip().upper().replace(" ", "") for name in classes[1].split(",")]
        elif not text.startswith("Use: "):
            only = _ONLY.match(text.strip('"').rstrip("."))
            if only:
                reading.only = only[1]


def decode(lines: list, uses=(), kind: str = "", family: str = "", weapon: bool = False) -> Reading:
    """One tooltip. `lines` are its lines, `uses` the (spell, name, description) the game gives for its use, which
    stand in when the tooltip itself has no "Use:" line."""
    reading = Reading(name=lines[0] if lines else "")
    texts = [clean(line.split("\t", 1)[0])[len("Use: "):] for line in lines[1:] if line.startswith("Use: ")]
    if not texts:
        texts = [clean(description) for _, _, description in uses if description]
    reading.text = " ".join(texts)
    decoder = _Decoder(reading)
    for text in texts:
        cooldown = _COOLDOWN.search(text)
        if cooldown:
            reading.cooldown = max(reading.cooldown, _seconds(cooldown[1], cooldown[2]))
            text = _COOLDOWN.sub("", text).strip()
        for sentence in _SENTENCE.split(text):
            decoder.sentence(sentence)
    if not texts:
        reading.unread.append("no use text")
    _read_restrictions(lines[1:], reading)
    reading.category = category_of(kind, family, reading, weapon)
    return reading


# -- what the capture reads -------------------------------------------------------------------------------

def weapon_items(data) -> dict:
    """{item: name} of the weapon stones and oils the recipes make; the leftovers of other seasons have no skill."""
    found = {}
    for item, recipes in data.recipes.items():
        for recipe in recipes:
            if _WEAPON_ITEM.search(recipe["name"]) and recipe["skill"] > 0 and recipe["learned"]:
                found[item] = recipe["name"]
    return found


def consumable_ids(data) -> list:
    """The items the capture reads; the rule is in this file's first lines."""
    if data is None:
        return []
    families = {}
    for item, row in data.catalogue.items():
        if not row["leftover"] and row["kind"] != PERMANENT_KIND and row["family"] not in NOT_READ_FAMILIES:
            families.setdefault((row["kind"], row["family"]), []).append(item)
    kept = set(weapon_items(data)) | {item for item in ALWAYS_READ if item in data.catalogue}
    for items in families.values():
        rows = {item: data.catalogue[item] for item in items}
        high = [item for item, row in rows.items() if row["level"] >= FROM_LEVEL]
        top = max(row["level"] for row in rows.values())
        best = max((rows[item]["strength"] for item in high), default=None)
        for item, row in rows.items():
            if (row["level"] >= FROM_LEVEL or row["level"] == 0 or (not high and row["level"] == top)
                    or (best is not None and row["strength"] >= best > 0) or row["family"].startswith("Well Fed")):
                kept.add(item)
    return sorted(kept)


# -- a capture --------------------------------------------------------------------------------------------

@dataclass
class Imported:
    """What a capture held of the consumables."""
    game: str = ""
    locale: str = ""
    listed: int = 0                                  # items of the capture's list
    read: int = 0                                    # of which the capture holds
    understood: int = 0                              # of which every phrase was understood
    absent: list = field(default_factory=list)       # items of the list the game did not show
    unread: Counter = field(default_factory=Counter)  # phrase -> items of the tab's categories it was not understood on
    other_unread: int = 0                            # items outside those categories (bombs, keys...) with such a phrase
    by_category: Counter = field(default_factory=Counter)
    readings: dict = field(default_factory=dict)     # item -> Reading


def read_capture(db, parsed: dict) -> Imported:
    """The consumables of a capture (capture.parse_saved), decoded."""
    data = db.consumables
    listed = consumable_ids(data)
    result = Imported(game=parsed["game"], locale=parsed["locale"], listed=len(listed))
    if not parsed["locale"].startswith("en"):
        return result   # the phrases are understood in English only
    weapons = weapon_items(data) if data else {}
    for item in listed:
        if item not in parsed["items"]:
            result.absent.append(item)
            continue
        row = data.catalogue.get(item, {})
        reading = decode(parsed["items"][item][0], parsed.get("uses", {}).get(item, ()), row.get("kind", ""),
                         row.get("family", ""), item in weapons)
        result.read += 1
        result.understood += reading.understood
        if reading.category == "other":
            result.other_unread += bool(reading.unread)
        else:
            result.unread.update(set(reading.unread))
        result.by_category[reading.category] += 1
        result.readings[item] = reading
    return result


def load(path=FILE) -> dict:
    """{"build", "date", "items": {item: record}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["items"] = {int(item): record for item, record in data.get("items", {}).items()}
    return data


def save(result: Imported, date: str, path=FILE) -> None:
    """One item per line, in id order, so another capture reads as a short difference. An item this capture did
    not hold keeps what was read of it before."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    items = dict(load(path).get("items", {}))
    items.update({item: reading.record() for item, reading in result.readings.items()})
    rows = [f'    "{item}": {json.dumps(items[item], ensure_ascii=False, sort_keys=True)}' for item in sorted(items)]
    text = ("{\n" + f'  "about": {json.dumps(ABOUT)},\n  "build": {json.dumps(result.game)},\n'
            f'  "date": {json.dumps(date)},\n  "items": {{\n' + ",\n".join(rows) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


# -- the game against ForeverDB's catalogue ----------------------------------------------------------------

_FAMILY_STATS = {
    "Agility": AGILITY, "Strength": STRENGTH, "Intellect": INTELLECT, "Spirit": SPIRIT, "Stamina": STAMINA,
    "Armor": ARMOR, "Attack power": ATTACK_POWER, "Spell damage": (SPELL_DAMAGE, SPELL_POWER), "Healing": (HEALING, SPELL_POWER),
    "Mana regeneration": MANA_REGEN,
    "Health regeneration": HEALTH_REGEN, "Critical strike": CRIT, "Maximum health": MAX_HEALTH, "Maximum mana": MAX_MANA,
    "Fire spell damage": SCHOOLS["fire"], "Frost spell damage": SCHOOLS["frost"], "Holy spell damage": SCHOOLS["holy"],
    "Nature spell damage": SCHOOLS["nature"], "Shadow spell damage": SCHOOLS["shadow"],
    "Arcane spell damage": SCHOOLS["arcane"],
}
_RESTORED = {"Health": "health", "Healing": "health", "Mana": "mana"}
TOLERANCE = 0.05   # a share of the catalogue's number, which rounds; of a range it writes the highest amount


@dataclass
class Disagreement:
    """One place where the game and the catalogue differ."""
    item: int
    name: str
    kind: str     # "family": the game shows no such effect; "strength": another number; "hidden": effects the
    #               catalogue does not name; "name": another name; "unread": not understood, so not compared
    detail: str

    def line(self) -> str:
        return f"{self.kind:9s} {self.item} {self.name}: {self.detail}"


def _value_of(record: dict, stat) -> float:
    """What a kept reading gives of a stat, however it holds it."""
    key = str(stat)
    return next((block[key] for block in (record.get("stats", {}), record.get("spell_stats", {}),
                                          record.get("extras", {}), record.get("conditional", {})) if key in block), 0)


def audit(items: dict, catalogue: dict) -> list:
    """Where the game disagrees with the catalogue, for the kept readings `items` ({item: record})."""
    found = []
    for item in sorted(items):
        record, row = items[item], catalogue.get(item)
        if row is None:
            continue   # a weapon stone or an oil: the catalogue does not have them
        note = lambda kind, detail: found.append(Disagreement(item, row["name"], kind, detail))
        if record["name"] and record["name"] != row["name"]:
            note("name", f"{record['name']} in the game")
        if record.get("unread"):
            note("unread", "; ".join(record["unread"]))
            continue
        family = row["family"].replace("Well Fed: ", "")
        restored = _RESTORED.get(family) if row["kind"] != "elixir" and not row["family"].startswith("Well Fed") else None
        stats = _FAMILY_STATS.get(family)
        if restored and record.get("restores", {}).get(restored):
            shown = record["restores"][restored]
            low, high = record.get("ranges", {}).get(restored, (shown, shown))
            if row["strength"] and not low * (1 - TOLERANCE) <= row["strength"] <= high * (1 + TOLERANCE):
                note("strength", f"{restored} {_number(shown)} in the game, {_number(row['strength'])} in the catalogue")
            continue
        if restored and (not row["strength"] or any("% of your" in line for line in record.get("utility", ()))):
            continue   # a share of the health per second, or no number to compare
        if restored and stats is None:
            note("family", f"the catalogue says {family} {_number(row['strength'])}, the game restores no {restored}")
            continue
        if stats is None:
            continue   # a family that names no stat ("Other", "Cures", resistances of several schools...)
        wanted = stats if isinstance(stats, tuple) else (stats,)
        shown = max((_value_of(record, stat) for stat in wanted), default=0)
        if not shown:
            note("family", f"the catalogue says {family}, the game shows {record['text'] or 'nothing'}")
            continue
        # for food the catalogue's number is the health restored, so only the effect is compared
        if row["kind"] not in ("food", "drink") and row["strength"] \
                and abs(shown - row["strength"]) > TOLERANCE * row["strength"]:
            note("strength", f"{family} {_number(shown)} in the game, {_number(row['strength'])} in the catalogue")
        others = [str(stat) for stat in record.get("stats", {}) if stat not in {str(one) for one in wanted}]
        if others:
            note("hidden", f"the catalogue names {family} only, the game also gives stat(s) {', '.join(others)}")
    return found


def audit_summary(found: list) -> str:
    counts = Counter(entry.kind for entry in found)
    return ", ".join(f"{count} {kind}" for kind, count in sorted(counts.items())) or "nothing to report"
