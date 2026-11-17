from test.bases import WorldTestBase

from ..data import CAMPAIGN_NAMES, LOCATIONS


class L4D2TestBase(WorldTestBase):
    game = "Left 4 Dead 2"


class TestDefaults(L4D2TestBase):
    def test_pool_matches_locations(self) -> None:
        self.assertEqual(len(LOCATIONS), 57)
        self.assertEqual(len(self.multiworld.itempool), len(LOCATIONS))

    def test_campaign_gates_its_locations(self) -> None:
        world = self.multiworld.worlds[self.player]
        locked = next(name for name in CAMPAIGN_NAMES if name not in world.starting)
        self.assertFalse(self.can_reach_location(f"{locked} Finale"))
        self.collect_by_name(locked)
        self.assertTrue(self.can_reach_location(f"{locked} Finale"))


class TestAllFinales(L4D2TestBase):
    options = {"finales_required": 14, "starting_campaigns": 14, "trap_percentage": 100}

    def test_no_campaigns_in_pool(self) -> None:
        names = {item.name for item in self.multiworld.itempool}
        self.assertFalse(names & set(CAMPAIGN_NAMES))
        self.assertTrue(self.multiworld.state.has_from_list(CAMPAIGN_NAMES, self.player, 14))


class TestBridgeProtocol(L4D2TestBase):
    def test_parse_out(self) -> None:
        from ..client import parse_out
        text = "seed 1-1\nack 3\ndlseen 0\ndeaths 2\nchecks c1m1_hotel c1m4_atrium\nend\n\x00"
        state = parse_out(text)
        self.assertEqual(state["ack"], 3)
        self.assertEqual(state["deaths"], 2)
        self.assertEqual(state["checks"], ["c1m1_hotel", "c1m4_atrium"])
        self.assertIsNone(parse_out("seed 1-1\nack 3\n"))  # half-written file is ignored
