import unittest
from types import SimpleNamespace

import phases
import raid_sources


class RaidSourceTest(unittest.TestCase):
    def test_the_dungeon_route_and_legacy_range_both_stay_visible(self):
        item = {"name": "Marksman Bands", "groups": frozenset("w"), "sources": [["w", "0", "0", "k"]]}
        raid_sources.apply(SimpleNamespace(items={18296: item}))
        self.assertEqual(item["groups"], frozenset("dw"))
        self.assertEqual(item["sources"][0], ["d", "429", "Wildspawn Satyr", "", "0", "t"])
        self.assertEqual(item["sources"][-1], ["w", "0", "0", "k"])
        self.assertEqual(phases.item_phase(item), phases.PRE_RAID)

    def test_unobserved_world_range_for_the_naxxramas_ring(self):
        ring = {"name": "Ring of the Eternal Flame", "groups": frozenset("w"), "sources": [["w", "60", "63", "k"]]}
        db = SimpleNamespace(items={23237: ring})
        raid_sources.apply(db)
        raid_sources.apply(db)
        self.assertEqual(phases.item_phase(ring), phases.LATER)
        self.assertEqual(phases.shown_sources(ring), [
            ["d", "533", "Dread Creeper", "", "1", "t"],
            ["d", "533", "Carrion Spinner", "", "1", "t"],
        ])

    def test_new_vendor_and_observed_world_drop_remain_pre_raid(self):
        for groups, sources in (
            ("vw", [["w", "60", "63", "k"], ["v", "22668", "Pix Xizzix", "", "s"]]),
            ("w", [["w", "60", "63", "s"]]),
        ):
            ring = {"name": "Ring of the Eternal Flame", "groups": frozenset(groups), "sources": sources}
            raid_sources.apply(SimpleNamespace(items={23237: ring}))
            self.assertEqual(ring["sources"], sources)
            self.assertEqual(phases.item_phase(ring), phases.PRE_RAID)
