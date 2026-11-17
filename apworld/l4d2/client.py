"""Left 4 Dead 2 client: talks to the Archipelago server and to the in-game VScript through two text files
in <L4D2>/left4dead2/ems/archipelago/ (VScript can only read/write files there, it has no networking).

in.txt  (client -> game): seed, unlocked campaigns, pending items, incoming DeathLink id.
out.txt (game -> client): seed, last applied item index (ack), DeathLink id seen, wipe count, checked maps.
"""
import asyncio
import os
import time

import Utils
from CommonClient import CommonContext, get_base_parser, gui_enabled, handle_url_arg, logger, server_loop
from NetUtils import ClientStatus

from .data import (FINALE_MAPS, GAME, ITEM_ID_TO_CODE, MAP_TO_LOCATION_ID, MILESTONE_LOCATION_IDS,
                   PICKUP_TO_LOCATION_ID)

MAX_ITEMS_PER_WRITE = 50  # keep in.txt small; FileToString returns null for files that are "too big"
DEATHLINK_TTL = 30  # seconds an incoming DeathLink waits for the game before it is dropped


def parse_out(text: str) -> dict | None:
    """Parse the game's out.txt. Returns None if it is incomplete (mid-write)."""
    state = {"seed": "", "ack": 0, "dlseen": 0, "deaths": 0, "checks": [], "picks": [], "counts": {}}
    complete = False
    for line in text.replace("\x00", "").splitlines():
        parts = line.split()
        if not parts:
            continue
        key, rest = parts[0], parts[1:]
        if key == "end":
            complete = True
        elif key == "seed":
            state["seed"] = rest[0] if rest else ""
        elif key in ("checks", "picks"):
            state[key] = rest
        elif key == "count" and len(rest) == 2:
            state["counts"][rest[0]] = int(rest[1])
        elif key in ("ack", "dlseen", "deaths") and rest:
            state[key] = int(rest[0])
    return state if complete else None


def location_ids(state: dict) -> set[int]:
    """Every location the game's state has earned: maps reached, weapons picked up, milestones met."""
    ids = {MAP_TO_LOCATION_ID[m] for m in state["checks"] if m in MAP_TO_LOCATION_ID}
    ids |= {PICKUP_TO_LOCATION_ID[w] for w in state["picks"] if w in PICKUP_TO_LOCATION_ID}
    ids |= {loc_id for stat, n, loc_id in MILESTONE_LOCATION_IDS if state["counts"].get(stat, 0) >= n}
    return ids


def clean(text: str) -> str:
    return " ".join(text.split())  # no newlines/tabs can break the line format


class L4D2Context(CommonContext):
    game = GAME
    items_handling = 0b111  # we receive everything, including our own items and starting inventory

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.bridge_dir = ""
        self.finales_required = 0
        self.deathlink_id = 0
        self.deathlink_time = 0.0
        self.last_deaths: int | None = None
        self.last_sent: set[int] = set()
        self.last_written = ""

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            slot_data = args.get("slot_data", {})
            self.finales_required = slot_data.get("finales_required", 0)
            self.last_sent = set()
            Utils.async_start(self.update_death_link(bool(slot_data.get("death_link"))))

    def on_deathlink(self, data: dict):
        super().on_deathlink(data)
        self.deathlink_id = max(int(time.time()), self.deathlink_id + 1)
        self.deathlink_time = time.time()

    @property
    def room_seed(self) -> str | None:
        return getattr(self, "server_seed_name", None) or self.seed_name  # server_seed_name is 0.6.8+

    @property
    def seed_key(self) -> str:
        return clean(f"{self.room_seed}-{self.slot}").replace(" ", "_")

    def build_in(self, ack: int) -> str:
        lines = [f"seed {self.seed_key}"]
        unlocked = [ITEM_ID_TO_CODE[i.item][5:] for i in self.items_received
                    if ITEM_ID_TO_CODE.get(i.item, "").startswith("camp:")]
        lines.append("unlocked " + " ".join(unlocked))
        if "DeathLink" in self.tags and time.time() - self.deathlink_time < DEATHLINK_TTL:
            lines.append(f"dl {self.deathlink_id}")
        for index in range(ack, min(len(self.items_received), ack + MAX_ITEMS_PER_WRITE)):
            item = self.items_received[index]
            name = self.item_names.lookup_in_game(item.item)
            if item.player == 0:
                sender = " (starting item)"
            elif item.player == self.slot:
                sender = ""
            else:
                sender = f" from {self.player_names.get(item.player, '?')}"
            lines.append(f"item {index + 1} {ITEM_ID_TO_CODE.get(item.item, 'none')} {clean(name + sender)}")
        lines.append("end")
        return "\n".join(lines) + "\n"

    async def sync_game(self, state: dict | None) -> None:
        if state and state["seed"] == self.seed_key:
            checks = location_ids(state) & self.server_locations  # options may have left some checks out
            new = checks - self.checked_locations
            if new and checks != self.last_sent:
                self.last_sent = checks
                self.locations_checked |= checks
                await self.send_msgs([{"cmd": "LocationChecks", "locations": list(new)}])

            finales = sum(1 for m in state["checks"] if m in FINALE_MAPS)
            if not self.finished_game and self.finales_required and finales >= self.finales_required:
                await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                self.finished_game = True
                logger.info("Goal complete!")

            if self.last_deaths is not None and state["deaths"] > self.last_deaths and "DeathLink" in self.tags:
                await self.send_death(f"{self.player_names[self.slot]}'s team was wiped out in Left 4 Dead 2.")
            self.last_deaths = state["deaths"]

        content = self.build_in(state["ack"] if state and state["seed"] == self.seed_key else 0)
        if content != self.last_written:
            tmp = os.path.join(self.bridge_dir, "in.tmp")
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            os.replace(tmp, os.path.join(self.bridge_dir, "in.txt"))  # atomic, game never reads half a file
            self.last_written = content

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago Left 4 Dead 2 Client"
        return ui


def find_bridge_dir() -> str | None:
    from . import L4D2World
    folder = L4D2World.settings.game_folder
    game_dir = os.path.join(folder, "left4dead2")
    if not os.path.isdir(game_dir):
        logger.error(f"Left 4 Dead 2 not found at '{folder}'. Set l4d2_options.game_folder in host.yaml.")
        return None
    path = os.path.join(game_dir, "ems", "archipelago")
    os.makedirs(path, exist_ok=True)
    return path


async def game_loop(ctx: L4D2Context) -> None:
    ctx.bridge_dir = find_bridge_dir()
    if not ctx.bridge_dir:
        return
    logger.info(f"Bridging with the game through {ctx.bridge_dir}")
    out_path = os.path.join(ctx.bridge_dir, "out.txt")
    while not ctx.exit_event.is_set():
        await asyncio.sleep(0.5)
        if not ctx.slot or not ctx.room_seed:
            continue
        state = None
        try:
            with open(out_path, encoding="utf-8", errors="replace") as f:
                state = parse_out(f.read())
        except FileNotFoundError:
            pass
        try:
            await ctx.sync_game(state)
        except OSError as e:
            logger.warning(f"Could not write to the game folder: {e}")
        except Exception:
            logger.exception("Game bridge error")  # keep bridging; a dead loop would stall the game silently


def main(*args: str) -> None:
    import colorama

    Utils.init_logging("L4D2Client", exception_logger="Client")
    parser = get_base_parser(description="Left 4 Dead 2 Archipelago Client")
    parser.add_argument("--name", default=None, help="Slot name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    parsed = handle_url_arg(parser.parse_args(args), parser=parser)

    async def run():
        ctx = L4D2Context(parsed.connect, parsed.password)
        ctx.auth = parsed.name
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        bridge = asyncio.create_task(game_loop(ctx), name="L4D2 bridge")
        await ctx.exit_event.wait()
        bridge.cancel()
        await ctx.shutdown()

    colorama.just_fix_windows_console()
    asyncio.run(run())
