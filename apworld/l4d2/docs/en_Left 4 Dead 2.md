# Left 4 Dead 2

## Where is the options page?

The [player options page for this game](../player-options) has everything you need to make a YAML file.

## What does randomization do to this game?

All 14 official campaigns start **locked** except your starting campaign(s). Campaign unlocks are scattered across
the multiworld. If you load a locked campaign, the mod tells you so and moves you to one you have.

Everything runs inside the game's own scripting (VScript), so you don't need SourceMod, Metamod or `-insecure`.
The host runs a small client that passes items and checks between Archipelago and the game.

## What is a location check?

Every **safe room** you reach and every **finale** you beat, 57 checks in all:

| Campaign | Checks | Campaign | Checks |
|---|---|---|---|
| Dead Center | 4 | No Mercy | 5 |
| Dark Carnival | 5 | Crash Course | 2 |
| Swamp Fever | 4 | Death Toll | 5 |
| Hard Rain | 5 | Dead Air | 5 |
| The Parish | 5 | Blood Harvest | 5 |
| The Passing | 3 | Cold Stream | 4 |
| The Sacrifice | 3 | The Last Stand | 2 |

Location groups: `Finales`, `Safe Rooms`, and one group per campaign name.

## What items can I receive?

| Type | Items | What happens |
|---|---|---|
| **Campaigns** (progression) | Dead Center … The Last Stand | Unlocks that campaign |
| **Supplies** | First Aid Kit, Pain Pills, Adrenaline, Defibrillator, Molotov, Pipe Bomb, Bile Bomb, Incendiary / Explosive Ammo Pack, Full Heal, Grenade Launcher, M60 | Every living survivor gets one |
| **Traps** | Tank Trap, Witch Trap, Horde Trap | Spawns it right away |

Items show up in chat as `[AP] Received …`. Items that arrive while you're in a menu are delivered when the next
round starts.

## What is the goal?

Beat the number of finales set by **Finales Required**.

## Does co-op work?

Yes. Only the host runs the client, and friends join the host's game normally. Supplies go to every survivor.

## DeathLink

When your whole team wipes, everyone on DeathLink dies. When someone else dies, all your survivors die.
