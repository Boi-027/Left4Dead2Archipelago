from dataclasses import dataclass
from typing import ClassVar

import settings
from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from Options import DeathLink, OptionGroup, PerGameCommonOptions, Range
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, Type, components, icon_paths, launch

from .data import CAMPAIGN_NAMES, CAMPAIGNS, GAME, ITEMS, LOCATIONS, SUPPLIES, TRAPS


def run_client(*args: str) -> None:
    from .client import main
    launch(main, name="Left 4 Dead 2 Client", args=args)


components.append(Component("Left 4 Dead 2 Client", func=run_client, game_name=GAME,
                            component_type=Type.CLIENT, supports_uri=True, icon="l4d2"))
icon_paths["l4d2"] = f"ap:{__name__}/icons/l4d2.png"


class L4D2Settings(settings.Group):
    class GameFolder(settings.UserFolderPath):
        """The Left 4 Dead 2 install folder (the one that contains left4dead2.exe)."""
        description = "Left 4 Dead 2 install folder"

    game_folder: GameFolder = GameFolder("C:/Program Files (x86)/Steam/steamapps/common/Left 4 Dead 2")


class FinalesRequired(Range):
    """How many campaign finales you must beat to goal."""
    display_name = "Finales Required"
    range_start = 1
    range_end = len(CAMPAIGNS)
    default = 5


class StartingCampaigns(Range):
    """How many random campaigns are unlocked from the start."""
    display_name = "Starting Campaigns"
    range_start = 1
    range_end = len(CAMPAIGNS)
    default = 1


class TrapPercentage(Range):
    """Percent of filler items that are traps (Tank, Witch, Horde)."""
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 20


@dataclass
class L4D2Options(PerGameCommonOptions):
    finales_required: FinalesRequired
    starting_campaigns: StartingCampaigns
    trap_percentage: TrapPercentage
    death_link: DeathLink


class L4D2Web(WebWorld):
    theme = "stone"
    bug_report_page = "https://github.com/Boi-027/Left4Dead2Archipelago/issues"
    tutorials = [Tutorial("Setup Guide", "How to set up Left 4 Dead 2 for Archipelago.", "English",
                          "setup_en.md", "setup/en", ["Boi-027"])]
    option_groups = [
        OptionGroup("Goal", [FinalesRequired, StartingCampaigns]),
        OptionGroup("Challenge", [TrapPercentage, DeathLink]),
    ]
    options_presets = {
        "Quick Run": {"finales_required": 2, "starting_campaigns": 2, "trap_percentage": 10},
        "Full Apocalypse": {"finales_required": 14, "starting_campaigns": 1, "trap_percentage": 40,
                            "death_link": True},
    }


class L4D2Item(Item):
    game = GAME


class L4D2Location(Location):
    game = GAME


class L4D2World(World):
    """Fight through the zombie apocalypse. Campaigns are locked until someone in the multiworld finds them,
    and every safe room and finale you reach sends out an item."""
    game = GAME
    web = L4D2Web()
    options_dataclass = L4D2Options
    options: L4D2Options
    settings: ClassVar[L4D2Settings]
    settings_key = "l4d2_options"

    item_name_to_id = {name: v[0] for name, v in ITEMS.items()}
    location_name_to_id = {name: v[0] for name, v in LOCATIONS.items()}
    item_name_groups = {"Campaigns": set(CAMPAIGN_NAMES), "Traps": set(TRAPS), "Supplies": set(SUPPLIES)}
    location_name_groups = {
        "Finales": {name for name in LOCATIONS if name.endswith("Finale")},
        "Safe Rooms": {name for name in LOCATIONS if name.endswith("Safe Room")},
        **{campaign: {name for name, v in LOCATIONS.items() if v[2] == campaign} for campaign in CAMPAIGN_NAMES},
    }

    def generate_early(self) -> None:
        self.starting = self.random.sample(CAMPAIGN_NAMES, self.options.starting_campaigns.value)
        for name in self.starting:
            self.multiworld.push_precollected(self.create_item(name))

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        for _, campaign, _ in CAMPAIGNS:
            region = Region(campaign, self.player, self.multiworld)
            region.add_locations({name: v[0] for name, v in LOCATIONS.items() if v[2] == campaign}, L4D2Location)
            self.multiworld.regions.append(region)
            menu.connect(region, f"Play {campaign}", lambda state, c=campaign: state.has(c, self.player))

    def create_items(self) -> None:
        pool = [self.create_item(name) for name in CAMPAIGN_NAMES if name not in self.starting]
        pool += [self.create_filler() for _ in range(len(LOCATIONS) - len(pool))]
        self.multiworld.itempool += pool

    def get_filler_item_name(self) -> str:
        if self.random.randint(1, 100) <= self.options.trap_percentage.value:
            return self.random.choice(list(TRAPS))
        return self.random.choice(list(SUPPLIES))

    def create_item(self, name: str) -> L4D2Item:
        if name in CAMPAIGN_NAMES:
            classification = ItemClassification.progression
        elif name in TRAPS:
            classification = ItemClassification.trap
        else:
            classification = ItemClassification.filler
        return L4D2Item(name, classification, self.item_name_to_id[name], self.player)

    def set_rules(self) -> None:
        # Each unlocked campaign's finale is beatable, so N unlocks == N finales possible.
        needed = self.options.finales_required.value
        self.multiworld.completion_condition[self.player] = \
            lambda state: state.has_from_list(CAMPAIGN_NAMES, self.player, needed)

    def fill_slot_data(self) -> dict:
        return {"finales_required": self.options.finales_required.value,
                "death_link": bool(self.options.death_link.value)}
