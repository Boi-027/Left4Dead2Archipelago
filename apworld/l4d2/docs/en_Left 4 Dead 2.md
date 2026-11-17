# Left 4 Dead 2

## Where is the options page?

The [player options page for this game](../player-options) has everything you need to make a YAML file.

## What does randomization do to this game?

All 14 official campaigns start **locked** except your starting campaign(s). Campaign unlocks are scattered across
the multiworld. If you load a locked campaign, the mod tells you so and moves you to one you have.

Everything runs inside the game's own scripting (VScript), so you don't need SourceMod, Metamod or `-insecure`.
The host runs a small client that passes items and checks between Archipelago and the game.

## What is a location check?

Up to **139** checks:

| Checks | How many | Option |
|---|---|---|
| Every chapter's **safe room** and every **finale** | 57 | always on |
| **Kill milestones:** Tanks and Witches (1/5/10), crowning a Witch, each special infected (1/10/25/50), common infected (100 to 5,000) | 38 | `kill_milestones` |
| **Weapon pickups:** the first time your team picks up each gun and melee weapon | 31 | `weapon_pickups` |
| **Teamwork milestones:** reviving, healing and defibbing teammates, rescuing survivors from closets | 13 | `teamwork_milestones` |

Milestones count the whole team's totals across every map you play. Logic expects the bigger milestones and the rarer
weapons only once you have more campaigns open.

Location groups: `Finales`, `Safe Rooms`, `Kill Milestones`, `Teamwork Milestones`, `Weapon Pickups`, and one group
per campaign name.

## What items can I receive?

| Type | Items | What happens |
|---|---|---|
| **Campaigns** (progression) | Dead Center … The Last Stand | Unlocks that campaign |
| **Supplies** | First Aid Kit, Pain Pills, Adrenaline, Defibrillator, Molotov, Pipe Bomb, Bile Bomb, Incendiary / Explosive Ammo Pack, Full Heal | Every living survivor gets one |
| **Weapon drops** | Every gun from the Magnum to the M60, the Chainsaw, and every melee weapon | Dropped in front of a survivor, one for each of you |
| **Traps** | Tank, Witch, Horde, Smoker, Boomer, Hunter, Spitter, Jockey, Charger, Vomit, Fragile, Incap | Happens right away |

Items show up in chat as `[AP] Received …`. Items that arrive while you're in a menu are handed out when the next
round starts.

## What is the goal?

Beat the number of finales set by **Finales Required**.

## Does co-op work?

Yes. Only the host runs the client, and friends join the host's game normally. Supplies go to every survivor.

## DeathLink

When your whole team wipes, everyone on DeathLink dies. When someone else dies, all your survivors die.
