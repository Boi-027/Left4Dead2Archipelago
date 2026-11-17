<p align="center">
  <img src="docs/images/launcher_connected.png" width="860" alt="The Left 4 Dead 2 Archipelago launcher, connected to a room">
</p>

<h1 align="center">Left 4 Dead 2 Archipelago</h1>

<p align="center">
  <b>A multiworld randomizer for Left 4 Dead 2, with no SourceMod, Metamod or -insecure.</b><br>
  Campaigns unlock as items, every safe room and finale is a check, and a Tank might be a gift from a friend's world.
</p>

<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/status-in%20testing-e8a33d">
  <img alt="Release" src="https://img.shields.io/badge/release-v0.2.2-d4af37">
  <img alt="Archipelago" src="https://img.shields.io/badge/Archipelago-0.6.x-7b4fd8">
  <img alt="Game" src="https://img.shields.io/badge/Left%204%20Dead%202-Steam-b8161b">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows%2010%20%2F%2011-0a63a8">
</p>

<p align="center">
  <a href="https://github.com/Boi-027/Left4Dead2Archipelago/releases"><b>Download</b></a> ·
  <a href="#installation">Install</a> ·
  <a href="#features">Features</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#troubleshooting">Troubleshooting</a>
</p>

> [!IMPORTANT]
> **No game files are included.** The launcher's menu art, fonts, sounds and icon are read from **your own** Left 4 Dead 2
> install each time it starts. Nothing from the game is in this repository or the release.

> [!WARNING]
> **This is in testing.** Generation, the Archipelago tests and the client bridge are tested, but no full playthrough
> has been done yet. Expect bugs.

---

## What it is

An [Archipelago](https://archipelago.gg) world for **Left 4 Dead 2**. All 14 official campaigns start locked except your
starting one(s). Safe rooms, finales, kill and teamwork milestones and weapon pickups send checks (up to **139**).
Campaign unlocks, supplies, weapon drops and traps come from the multiworld.

- **Pure VScript.** The mod is a small script add-on, so there's no SourceMod, no Metamod and no `-insecure`. You
  stay on a normal, secure game, in regular Co-op. With the client closed, the game plays completely normally.
- **One-click install.** The launcher installs the mod and the APWorld, and finds the game and Archipelago by itself.
- **Connects in the background.** Enter your room in the launcher and press **CONNECT**. The Archipelago client runs
  hidden, with no client window.
- **Co-op.** Only the host runs the client. Friends join the host's game as usual, and supplies go to every survivor.

---

## Screenshots

<table>
  <tr>
    <td width="50%"><img src="docs/images/launcher.png" alt="The launcher"><br><sub>The launcher, in the game's own menu art, fonts and sounds</sub></td>
    <td width="50%"><img src="docs/images/launcher_connected.png" alt="The launcher, connected"><br><sub>Server, slot and password, then <b>CONNECT</b>. The client runs hidden.</sub></td>
  </tr>
</table>

---

## Features

### The launcher

<p align="center"><img src="docs/images/launcher.png" width="760" alt="The Left 4 Dead 2 Archipelago launcher"></p>

- **One-click install:** press **INSTALL**. It copies `l4d2.apworld` into Archipelago's `custom_worlds` folder and
  `archipelago.vpk` into the game's `addons` folder, and tells Archipelago where the game is. **REINSTALL / UPDATE**
  refreshes both.
- **Connection:** server, slot and password, then **CONNECT**. The Archipelago client runs hidden in the background, and
  the launcher shows its status (*CONNECTED AS …*) and the latest message. Server and slot are remembered; the password
  is not saved.
- **Play:** **PLAY ARCHIPELAGO** starts Left 4 Dead 2. Then start any Co-op campaign.
- **Looks like the game:** the main menu art, the menu font (Trade Gothic), the logo font (Future Rot), the menu
  sounds and the game icon, all read from your own install.

### In the game
- **Regular Co-op:** play **Campaign** (or Realism) as usual. The mod switches on while the AP client is connected
  and stays out of the way otherwise. Versus, Survival and Scavenge are left alone.
- **Chat messages:** `[AP] Connected to the Archipelago client.`, `[AP] Received Pain Pills from …`, and so on.
- **Campaign locking:** if you load a locked campaign, the mod tells you and moves you to one you have.
- **Supplies for everyone:** every living survivor gets the item, bots included.
- **Weapon drops:** a received gun or melee weapon is dropped in front of a survivor, with one for each of you.
- **Counting as you play:** kills, revives, heals, defibs, closet rescues and weapon pickups count for the whole team.
- **Items wait for you:** anything that arrives in a menu or a loading screen is handed out when the next round starts.

### Locations and items

| Checks (up to 139) | Items |
|---|---|
| Every chapter's safe room and every finale, across all 14 official campaigns (57) | **Campaign unlocks** (14, progression) |
| *Kill milestones (38):* Tanks and Witches (1/5/10), crowning a Witch, each special infected (1/10/25/50), common infected (100 up to 5,000) | **Supplies:** First Aid Kit, Pain Pills, Adrenaline, Defibrillator, Molotov, Pipe Bomb, Bile Bomb, Incendiary / Explosive Ammo Pack, Full Heal |
| *Weapon pickups (31):* the first time your team picks up each gun and melee weapon | **Weapon drops (32):** every gun from the Magnum to the M60, the Chainsaw, and every melee weapon |
| *Teamwork milestones (13):* reviving, healing and defibbing teammates, and rescuing survivors from closets | **Traps (12)** |

The three groups in italics are options, all on by default. Bigger milestones are expected later: logic wants more
campaigns open before it counts on 5,000 kills or a rare weapon.

Location groups for hints: `Finales`, `Safe Rooms`, `Kill Milestones`, `Teamwork Milestones`, `Weapon Pickups`, and
one per campaign name.

### Goals
| Goal | What finishes it |
|---|---|
| **Finales Required** | Beat that many campaign finales (1–14) |

### Options
| Option | Default | |
|---|---|---|
| `finales_required` | 5 | Finales to beat to goal (1–14) |
| `starting_campaigns` | 1 | Campaigns unlocked at the start (1–14) |
| `kill_milestones` | on | Kill milestone checks (38) |
| `weapon_pickups` | on | Weapon pickup checks (31) |
| `teamwork_milestones` | on | Teamwork milestone checks (13) |
| `weapon_percentage` | 40 | How much of the non-trap filler is weapon drops (the rest is supplies) |
| `trap_percentage` | 20 | How much of the filler becomes traps |
| `death_link` | off | Share deaths with the multiworld |

Presets: **Quick Run** (2 finales, 2 starting campaigns, no kill or teamwork milestones) and **Full Apocalypse** (all 14
finales, 40% traps, Death Link).

### Links
- **Death Link:** when your whole team wipes, everyone on Death Link dies. When someone else dies, all your survivors die.

<details>
<summary><b>Traps (12)</b>: junk checks can bite back</summary>

| Trap | Effect |
|---|---|
| **Tank Trap** | A Tank spawns |
| **Witch Trap** | A Witch spawns |
| **Horde Trap** | A panic event: here comes the horde |
| **Smoker / Boomer / Hunter / Spitter / Jockey / Charger Trap** | That special infected spawns |
| **Vomit Trap** | Everyone gets covered in bile |
| **Fragile Trap** | Every standing survivor drops to 1 HP |
| **Incap Trap** | One random survivor goes down |

`trap_percentage` sets how much of the filler becomes traps.
</details>

<details>
<summary><b>How it talks to the game</b></summary>

Left 4 Dead 2's scripting (VScript) can't open network connections, but it can read and write files in
`left4dead2/ems/`. The client handles the Archipelago server and swaps two small files with the game:

| File | Direction | Contents |
|---|---|---|
| `ems/archipelago/in.txt` | client → game | seed, unlocked campaigns, pending items, incoming Death Link |
| `ems/archipelago/out.txt` | game → client | seed, last item applied, wipe count, checked maps |

The client writes `in.txt` atomically, and both files end with an `end` line, so a half-written file is ignored.
</details>

---

## Requirements

- **Left 4 Dead 2** on Steam (PC).
- **Windows 10 or 11.**
- An **Archipelago** install (**0.6.4** or newer) to generate, and a server to play on.

That's it: no SourceMod, Metamod, `-insecure` or Python.

---

## Installation

1. Download **`L4D2.Archipelago.Installer.exe`** from the
   [Releases](https://github.com/Boi-027/Left4Dead2Archipelago/releases) page.
2. Start it, and check that both dots at the bottom are green (Left 4 Dead 2 and Archipelago). If one is red, use
   **SET GAME FOLDER** or **SET ARCHIPELAGO FOLDER**.
3. Press **INSTALL**.
4. Restart the Archipelago Launcher if it was open.

To update, download the new release and press **REINSTALL / UPDATE**.

<details>
<summary><b>Manual install</b></summary>

1. Put `l4d2.apworld` in Archipelago's `custom_worlds` folder.
2. Put `archipelago.vpk` in `Left 4 Dead 2/left4dead2/addons/`.
3. In Archipelago's `host.yaml`, set:
   ```yaml
   l4d2_options:
     game_folder: "C:/Program Files (x86)/Steam/steamapps/common/Left 4 Dead 2"
   ```
</details>

<details>
<summary><b>From the source instead</b></summary>

```bash
pip install vpk pyinstaller pillow
python tools/build.py
```

That builds `dist/l4d2.apworld`, `dist/archipelago.vpk` and `dist/L4D2 Archipelago Installer.exe` (the other two are
packed inside). For the tests, copy `apworld/l4d2` into an Archipelago source checkout's `worlds/` folder and run
`python -m pytest worlds/l4d2`.

| Path | What |
|---|---|
| [`apworld/l4d2/`](apworld/l4d2) | The APWorld: items, locations, options, rules, client, tests, docs |
| [`addon/`](addon) | The contents of `archipelago.vpk`: the VScript add-on |
| [`installer/`](installer) | The launcher, and the reader for the game's textures, fonts and sounds |
| [`tools/build.py`](tools/build.py) | The build |
</details>

## APWorld setup

1. The launcher installs `l4d2.apworld` for you. If you only generate or host, take it from the
   [Releases](https://github.com/Boi-027/Left4Dead2Archipelago/releases) page and put it in Archipelago's
   `custom_worlds` folder.
2. Make your YAML from [`examples/Left 4 Dead 2.yaml`](examples/Left%204%20Dead%202.yaml), or use *Generate Template
   Options* in the Archipelago Launcher.
3. Generate your multiworld as usual.

> [!NOTE]
> **After updating, regenerate your seed.** Location IDs can change between versions.

## Playing

1. In the launcher, enter **SERVER**, **SLOT NAME** and **PASSWORD**, then press **CONNECT**. Wait for
   *CONNECTED AS …*.
2. Press **PLAY ARCHIPELAGO**. Keep the launcher open while you play (minimizing is fine).
3. Chat shows `[AP] Connected to the Archipelago client.` Play through campaigns: every safe room and finale sends a
   check, and items show up in chat.

Prefer the standard client? Open the Archipelago Launcher → **Left 4 Dead 2 Client** instead of pressing CONNECT.

<details>
<summary><b>Co-op setup</b></summary>

1. The host installs, connects in the launcher and starts the game.
2. Friends join the host's game normally (Steam invite or the lobby). They don't need the mod's client.
3. Supplies go to every survivor. Traps and Death Link hit the whole team.
</details>

---

## Roadmap

<details>
<summary><b>Done</b></summary>

- The APWorld: up to 139 locations (safe rooms, finales, kill and teamwork milestones, weapon pickups), campaign
  unlocks, supplies, weapon drops, 12 traps, the finales goal, presets, location groups
- The VScript add-on: checks, items, traps, campaign locking, Death Link, tested loading in the real game
- The file bridge between the client and the game
- The launcher: install, update, hidden background connection, play, the game's own look
</details>

**In progress:** the first in-game playthrough

**To do:** weapon unlocks as items · an uninstall button · a Steam Workshop release

**Not planned:** SourceMod plugins (the mod stays VScript-only, so it works on a normal, secure game)

---

## Troubleshooting

- **No `[AP]` messages in chat:** connect in the launcher first (*CONNECTED AS …*), play a **Co-op** campaign, and
  check the add-on is enabled in the game's **Add-ons** menu. The game console shows `[AP] Archipelago add-on loaded`
  when the add-on is running. If it still stays quiet, press **REINSTALL / UPDATE** so Archipelago knows where the
  game is.
- **CONNECT stays on CONNECTING...:** check that the server includes the port (`archipelago.gg:12345`) and that the
  slot name is exact. The line under the status shows the server's message.
- **The launcher looks plain:** it couldn't find the game. Use **SET GAME FOLDER**.
- **Locations don't match after an update:** your seed was made with another `.apworld` version. Regenerate it.
- **Something else, or an idea?** [Open an issue](https://github.com/Boi-027/Left4Dead2Archipelago/issues), with
  what chat showed and what's in `left4dead2/ems/archipelago/`.

---

## Credits

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago).
- The font decoding follows [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat).
- Inspired by the earlier [SourceMod-based Left 4 Dead 2 Archipelago](https://github.com/Syoshiii/Left4Dead2-Archipelago).
- Project direction by **Boi**.

## License

MIT, in [LICENSE](LICENSE).

Left 4 Dead 2 is a trademark of Valve Corporation. This is an unofficial fan project, not affiliated with Valve. The
launcher screenshots show art read from my own copy of the game.

## AI Usage Disclosure

- This project was made with heavy use of AI.
- The code (the APWorld and client, the VScript add-on and the launcher) and this documentation were written by
  Claude (Anthropic) through Claude Code.
- I directed the work: I chose the features and made the design decisions.
