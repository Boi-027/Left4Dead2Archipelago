"""Static game data shared by the world (generation) and the client (bridge)."""

GAME = "Left 4 Dead 2"
BASE_ID = 1_247_000

# (code, name, maps); the last map of each campaign is its finale.
CAMPAIGNS = [
    ("c1", "Dead Center", ["c1m1_hotel", "c1m2_streets", "c1m3_mall", "c1m4_atrium"]),
    ("c2", "Dark Carnival", ["c2m1_highway", "c2m2_fairgrounds", "c2m3_coaster", "c2m4_barns", "c2m5_concert"]),
    ("c3", "Swamp Fever", ["c3m1_plankcountry", "c3m2_swamp", "c3m3_shantytown", "c3m4_plantation"]),
    ("c4", "Hard Rain", ["c4m1_milltown_a", "c4m2_sugarmill_a", "c4m3_sugarmill_b", "c4m4_milltown_b",
                         "c4m5_milltown_escape"]),
    ("c5", "The Parish", ["c5m1_waterfront", "c5m2_park", "c5m3_cemetery", "c5m4_quarter", "c5m5_bridge"]),
    ("c6", "The Passing", ["c6m1_riverbank", "c6m2_bedlam", "c6m3_port"]),
    ("c7", "The Sacrifice", ["c7m1_docks", "c7m2_barge", "c7m3_port"]),
    ("c8", "No Mercy", ["c8m1_apartment", "c8m2_subway", "c8m3_sewers", "c8m4_interior", "c8m5_rooftop"]),
    ("c9", "Crash Course", ["c9m1_alleys", "c9m2_lots"]),
    ("c10", "Death Toll", ["c10m1_caves", "c10m2_drainage", "c10m3_ranchhouse", "c10m4_mainstreet",
                           "c10m5_houseboat"]),
    ("c11", "Dead Air", ["c11m1_greenhouse", "c11m2_offices", "c11m3_garage", "c11m4_terminal", "c11m5_runway"]),
    ("c12", "Blood Harvest", ["c12m1_hilltop", "c12m2_traintunnel", "c12m3_bridge", "c12m4_barn",
                              "c12m5_cornfield"]),
    ("c13", "Cold Stream", ["c13m1_alpinecreek", "c13m2_southpinestream", "c13m3_memorialbridge",
                            "c13m4_cutthroatcreek"]),
    ("c14", "The Last Stand", ["c14m1_junkyard", "c14m2_lighthouse"]),
]

# Item codes are what the game script understands: "camp:<code>", "give:<classname>", "trap:<kind>".
SUPPLIES = {
    "First Aid Kit": "give:first_aid_kit",
    "Pain Pills": "give:pain_pills",
    "Adrenaline": "give:adrenaline",
    "Defibrillator": "give:defibrillator",
    "Molotov": "give:molotov",
    "Pipe Bomb": "give:pipe_bomb",
    "Bile Bomb": "give:vomitjar",
    "Incendiary Ammo Pack": "give:upgradepack_incendiary",
    "Explosive Ammo Pack": "give:upgradepack_explosive",
    "Full Heal": "give:health",
    "Grenade Launcher": "give:grenade_launcher",
    "M60": "give:rifle_m60",
}
TRAPS = {
    "Tank Trap": "trap:tank",
    "Witch Trap": "trap:witch",
    "Horde Trap": "trap:horde",
}

CAMPAIGN_NAMES = [name for _, name, _ in CAMPAIGNS]

ITEMS: dict[str, tuple[int, str]] = {}  # name -> (id, game code)
for i, (code, name, _) in enumerate(CAMPAIGNS):
    ITEMS[name] = (BASE_ID + i, f"camp:{code}")
for i, (name, code) in enumerate(SUPPLIES.items()):
    ITEMS[name] = (BASE_ID + 100 + i, code)
for i, (name, code) in enumerate(TRAPS.items()):
    ITEMS[name] = (BASE_ID + 200 + i, code)

LOCATIONS: dict[str, tuple[int, str, str]] = {}  # name -> (id, map, campaign name)
FINALE_MAPS: set[str] = set()
for c, (_, name, maps) in enumerate(CAMPAIGNS):
    for m, map_name in enumerate(maps):
        finale = m == len(maps) - 1
        loc = f"{name} Finale" if finale else f"{name} Chapter {m + 1} Safe Room"
        LOCATIONS[loc] = (BASE_ID + c * 10 + m, map_name, name)
        if finale:
            FINALE_MAPS.add(map_name)

MAP_TO_LOCATION_ID = {map_name: loc_id for loc_id, map_name, _ in LOCATIONS.values()}
ITEM_ID_TO_CODE = {item_id: code for item_id, code in ITEMS.values()}
