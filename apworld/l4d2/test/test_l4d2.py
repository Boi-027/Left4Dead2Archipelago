from test.bases import WorldTestBase

from ..data import CAMPAIGN_NAMES, LOCATIONS, MILESTONE_GROUPS, PICKUP_LOCATIONS, TRAPS, WEAPONS


class L4D2TestBase(WorldTestBase):
    game = "Left 4 Dead 2"


class TestDefaults(L4D2TestBase):
    def test_check_counts(self) -> None:
        self.assertEqual(len(MILESTONE_GROUPS["kills"]), 38)
        self.assertEqual(len(MILESTONE_GROUPS["teamwork"]), 13)
        self.assertEqual(len(PICKUP_LOCATIONS), 31)
        self.assertEqual(len(self.multiworld.get_locations(self.player)), 57 + 38 + 13 + 31)
        self.assertEqual(len(self.multiworld.itempool), len(self.multiworld.get_locations(self.player)))

    def test_campaign_gates_its_locations(self) -> None:
        world = self.multiworld.worlds[self.player]
        locked = next(name for name in CAMPAIGN_NAMES if name not in world.starting)
        self.assertFalse(self.can_reach_location(f"{locked} Finale"))
        self.collect_by_name(locked)
        self.assertTrue(self.can_reach_location(f"{locked} Finale"))

    def test_big_milestones_wait_for_more_campaigns(self) -> None:
        world = self.multiworld.worlds[self.player]
        self.assertTrue(self.can_reach_location("Kill 100 Common Infected"))
        self.assertTrue(self.can_reach_location("Pick Up AK-47"))
        self.assertFalse(self.can_reach_location("Kill 5000 Common Infected"))
        self.collect_by_name([name for name in CAMPAIGN_NAMES if name not in world.starting][:6])
        self.assertTrue(self.can_reach_location("Kill 5000 Common Infected"))


class TestOnlyCampaignChecks(L4D2TestBase):
    options = {"kill_milestones": False, "weapon_pickups": False, "teamwork_milestones": False}

    def test_only_maps(self) -> None:
        self.assertEqual(len(self.multiworld.get_locations(self.player)), 57)


class TestAllFinales(L4D2TestBase):
    options = {"finales_required": 14, "starting_campaigns": 14, "trap_percentage": 100}

    def test_no_campaigns_in_pool(self) -> None:
        names = {item.name for item in self.multiworld.itempool}
        self.assertFalse(names & set(CAMPAIGN_NAMES))
        self.assertTrue(names <= set(TRAPS))
        self.assertTrue(self.multiworld.state.has_from_list(CAMPAIGN_NAMES, self.player, 14))


class TestWeaponFiller(L4D2TestBase):
    options = {"trap_percentage": 0, "weapon_percentage": 100}

    def test_filler_is_weapons(self) -> None:
        names = {item.name for item in self.multiworld.itempool} - set(CAMPAIGN_NAMES)
        self.assertTrue(names and names <= set(WEAPONS))


class TestBridgeProtocol(L4D2TestBase):
    def test_parse_out(self) -> None:
        from ..client import location_ids, parse_out
        text = ("seed 1-1\nack 3\ndlseen 0\ndeaths 2\nchecks c1m1_hotel c1m4_atrium\npicks rifle_ak47 katana\n"
                "count tank 5\ncount common 120\nmsgseen 1700000000 4\nend\n\x00")
        state = parse_out(text)
        self.assertEqual(state["ack"], 3)
        self.assertEqual(state["deaths"], 2)
        self.assertEqual(state["checks"], ["c1m1_hotel", "c1m4_atrium"])
        self.assertEqual(state["counts"], {"tank": 5, "common": 120})
        self.assertEqual(state["msgseen"], (1700000000, 4))
        expected = {LOCATIONS[name][0] for name in (
            "Dead Center Chapter 1 Safe Room", "Dead Center Finale", "Pick Up AK-47", "Pick Up Katana",
            "Kill a Tank", "Kill 5 Tanks", "Kill 100 Common Infected")}
        self.assertEqual(location_ids(state), expected)
        self.assertIsNone(parse_out("seed 1-1\nack 3\n"))  # half-written file is ignored
