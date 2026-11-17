# Left 4 Dead 2 Setup Guide

## Requirements

- Left 4 Dead 2 (Steam)
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.4 or newer

No SourceMod, Metamod or `-insecure` needed.

## Install

Run **L4D2 Archipelago Installer.exe** and click **Install**. It finds your game and Archipelago, copies
`l4d2.apworld` into `Archipelago/custom_worlds` and `archipelago.vpk` into `left4dead2/addons`, and tells
Archipelago where the game is.

Manual install: copy those two files yourself, then set `l4d2_options: game_folder` in `host.yaml`.

## Play

1. In the installer/launcher, enter your room details and click **Connect**. The client runs hidden in the background.
   Or open the Archipelago Launcher and start **Left 4 Dead 2 Client**.
2. Start Left 4 Dead 2 (the launcher's *Play Archipelago* button just opens it) and play any **Co-op** campaign.
   If it's locked, the mod moves you to one you have.
3. Chat shows `[AP] Connected to the Archipelago client.` when the bridge is working.

In co-op, only the host runs the client. Friends join the host's game normally.
