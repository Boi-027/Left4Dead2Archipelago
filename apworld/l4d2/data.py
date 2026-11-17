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

# Item codes are what the game script understands: "camp:<code>", "give:<classname>", "drop:<weapon>", "trap:<kind>".
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
}

# name -> (weapon script name, how many campaigns logic wants before you're expected to have found one)
GUNS = {
    "Magnum Pistol": ("pistol_magnum", 1),
    "SMG": ("smg", 1),
    "Silenced SMG": ("smg_silenced", 1),
    "MP5": ("smg_mp5", 3),
    "Pump Shotgun": ("pumpshotgun", 1),
    "Chrome Shotgun": ("shotgun_chrome", 1),
    "Auto Shotgun": ("autoshotgun", 1),
    "Combat Shotgun": ("shotgun_spas", 1),
    "Assault Rifle": ("rifle", 1),
    "AK-47": ("rifle_ak47", 1),
    "Combat Rifle": ("rifle_desert", 1),
    "SG552": ("rifle_sg552", 3),
    "Hunting Rifle": ("hunting_rifle", 1),
    "Military Sniper Rifle": ("sniper_military", 1),
    "AWP": ("sniper_awp", 3),
    "Scout": ("sniper_scout", 3),
    "Grenade Launcher": ("grenade_launcher", 3),
    "M60": ("rifle_m60", 3),
    "Chainsaw": ("chainsaw", 2),
}
MELEE = {
    "Fire Axe": ("fireaxe", 2),
    "Katana": ("katana", 2),
    "Machete": ("machete", 2),
    "Baseball Bat": ("baseball_bat", 2),
    "Cricket Bat": ("cricket_bat", 2),
    "Crowbar": ("crowbar", 2),
    "Electric Guitar": ("electric_guitar", 2),
    "Frying Pan": ("frying_pan", 2),
    "Golf Club": ("golfclub", 2),
    "Nightstick": ("tonfa", 2),
    "Pitchfork": ("pitchfork", 2),
    "Shovel": ("shovel", 2),
    "Knife": ("knife", 0),  # 0: drop item only, too region-dependent to be a pickup check
}
WEAPONS = {**GUNS, **MELEE}

TRAPS = {
    "Tank Trap": "trap:tank",
    "Witch Trap": "trap:witch",
    "Horde Trap": "trap:horde",
    "Smoker Trap": "trap:smoker",
    "Boomer Trap": "trap:boomer",
    "Hunter Trap": "trap:hunter",
    "Spitter Trap": "trap:spitter",
    "Jockey Trap": "trap:jockey",
    "Charger Trap": "trap:charger",
    "Vomit Trap": "trap:vomit",
    "Fragile Trap": "trap:fragile",
    "Incap Trap": "trap:incap",
}

# Milestones are team totals the game counts: (stat, option group, thresholds, name for 1, name for many)
MILESTONES = [
    ("tank", "kills", [1, 5, 10], "Kill a Tank", "Kill {} Tanks"),
    ("witch", "kills", [1, 5, 10], "Kill a Witch", "Kill {} Witches"),
    ("crown", "kills", [1], "Crown a Witch", ""),
    ("smoker", "kills", [1, 10, 25, 50], "Kill a Smoker", "Kill {} Smokers"),
    ("boomer", "kills", [1, 10, 25, 50], "Kill a Boomer", "Kill {} Boomers"),
    ("hunter", "kills", [1, 10, 25, 50], "Kill a Hunter", "Kill {} Hunters"),
    ("spitter", "kills", [1, 10, 25, 50], "Kill a Spitter", "Kill {} Spitters"),
    ("jockey", "kills", [1, 10, 25, 50], "Kill a Jockey", "Kill {} Jockeys"),
    ("charger", "kills", [1, 10, 25, 50], "Kill a Charger", "Kill {} Chargers"),
    ("common", "kills", [100, 250, 500, 1000, 2000, 3000, 5000], "", "Kill {} Common Infected"),
    ("revive", "teamwork", [1, 5, 10, 25], "Revive a Teammate", "Revive {} Teammates"),
    ("heal", "teamwork", [1, 5, 10], "Heal a Teammate", "Heal {} Teammates"),
    ("defib", "teamwork", [1, 3, 5], "Defib a Teammate", "Defib {} Teammates"),
    ("rescue", "teamwork", [1, 3, 5], "Rescue a Survivor from a Closet", "Rescue {} Survivors from Closets"),
]

CAMPAIGN_NAMES = [name for _, name, _ in CAMPAIGNS]

ITEMS: dict[str, tuple[int, str]] = {}  # name -> (id, game code)
for i, (code, name, _) in enumerate(CAMPAIGNS):
    ITEMS[name] = (BASE_ID + i, f"camp:{code}")
for i, (name, code) in enumerate(SUPPLIES.items()):
    ITEMS[name] = (BASE_ID + 100 + i, code)
for i, (name, code) in enumerate(TRAPS.items()):
    ITEMS[name] = (BASE_ID + 200 + i, code)
for i, (name, (weapon, _)) in enumerate(WEAPONS.items()):
    ITEMS[name] = (BASE_ID + 300 + i, f"drop:{weapon}")

# name -> (id, game code, kind, campaign name or campaigns needed)
#   kind "map": code is a map name; "pick": a weapon script name; "count": "<stat>:<threshold>"
LOCATIONS: dict[str, tuple[int, str, str, str | int]] = {}
FINALE_MAPS: set[str] = set()
for c, (_, name, maps) in enumerate(CAMPAIGNS):
    for m, map_name in enumerate(maps):
        finale = m == len(maps) - 1
        loc = f"{name} Finale" if finale else f"{name} Chapter {m + 1} Safe Room"
        LOCATIONS[loc] = (BASE_ID + c * 10 + m, map_name, "map", name)
        if finale:
            FINALE_MAPS.add(map_name)

MILESTONE_GROUPS: dict[str, list[str]] = {"kills": [], "teamwork": []}
milestone_id = BASE_ID + 500
for stat, group, thresholds, one, many in MILESTONES:
    for tier, n in enumerate(thresholds):
        loc = one if n == 1 else many.format(n)
        # bigger milestones take more play, so logic wants more campaigns open before expecting them (1..7)
        needed = 1 + (tier * 6 // (len(thresholds) - 1) if len(thresholds) > 1 else 0)
        LOCATIONS[loc] = (milestone_id, f"{stat}:{n}", "count", needed)
        MILESTONE_GROUPS[group].append(loc)
        milestone_id += 1

PICKUP_LOCATIONS: list[str] = []
for i, (name, (weapon, needed)) in enumerate(WEAPONS.items()):
    if needed:
        loc = f"Pick Up {name}"
        LOCATIONS[loc] = (BASE_ID + 700 + i, weapon, "pick", needed)
        PICKUP_LOCATIONS.append(loc)

MAP_TO_LOCATION_ID = {v[1]: v[0] for v in LOCATIONS.values() if v[2] == "map"}
PICKUP_TO_LOCATION_ID = {v[1]: v[0] for v in LOCATIONS.values() if v[2] == "pick"}
MILESTONE_LOCATION_IDS = [(v[1].split(":")[0], int(v[1].split(":")[1]), v[0])
                          for v in LOCATIONS.values() if v[2] == "count"]
ITEM_ID_TO_CODE = {item_id: code for item_id, code in ITEMS.values()}
