// Archipelago mutation for Left 4 Dead 2.
// VScript has no networking, so the Archipelago client (in the Archipelago Launcher) talks to us through
// two files in left4dead2/ems/archipelago/:  in.txt (client -> game) and out.txt (game -> client).

MutationOptions <- {}

::AP_IN <- "archipelago/in.txt"
::AP_OUT <- "archipelago/out.txt"

::AP_ORDER <- ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14"]
::AP_FIRST_MAP <- {
	c1 = "c1m1_hotel", c2 = "c2m1_highway", c3 = "c3m1_plankcountry", c4 = "c4m1_milltown_a",
	c5 = "c5m1_waterfront", c6 = "c6m1_riverbank", c7 = "c7m1_docks", c8 = "c8m1_apartment",
	c9 = "c9m1_alleys", c10 = "c10m1_caves", c11 = "c11m1_greenhouse", c12 = "c12m1_hilltop",
	c13 = "c13m1_alpinecreek", c14 = "c14m1_junkyard"
}

::AP <- {
	seed = "", ack = 0, dlseen = 0, deaths = 0, checks = {}, counts = {}, picks = {},   // persisted in out.txt
	unlocked = {}, connected = false, warned = false, linkDeath = false, lockTimer = -1, lockTarget = null,
	dirty = false
}

// GetZombieType() -> stat name for kill milestones
::AP_ZOMBIE <- { [1] = "smoker", [2] = "boomer", [3] = "hunter", [4] = "spitter", [5] = "jockey", [6] = "charger",
	[8] = "tank" }
::AP_SPAWN <- { smoker = 1, boomer = 2, hunter = 3, spitter = 4, jockey = 5, charger = 6, witch = 7, tank = 8 }
::AP_MELEE <- { fireaxe = 1, katana = 1, machete = 1, baseball_bat = 1, cricket_bat = 1, crowbar = 1,
	electric_guitar = 1, frying_pan = 1, golfclub = 1, tonfa = 1, pitchfork = 1, shovel = 1, knife = 1 }

::AP_Say <- function(msg) {
	ClientPrint(null, 3, "\x04[AP]\x01 " + msg);
}

::AP_Lines <- function(text) {
	local lines = [];
	foreach (line in split(text, "\n")) {
		line = strip(line);
		if (line.len() > 0) lines.append(split(line, " "));
	}
	return lines;
}

::AP_Join <- function(parts, start) {
	local s = "";
	for (local i = start; i < parts.len(); i++) s += (i > start ? " " : "") + parts[i];
	return s;
}

::AP_Load <- function() {
	local text = FileToString(::AP_OUT);
	if (text == null) return;
	foreach (p in ::AP_Lines(text)) {
		if (p[0] == "seed" && p.len() > 1) ::AP.seed = p[1];
		else if (p[0] == "ack") ::AP.ack = p[1].tointeger();
		else if (p[0] == "dlseen") ::AP.dlseen = p[1].tointeger();
		else if (p[0] == "deaths") ::AP.deaths = p[1].tointeger();
		else if (p[0] == "checks") for (local i = 1; i < p.len(); i++) ::AP.checks[p[i]] <- true;
		else if (p[0] == "picks") for (local i = 1; i < p.len(); i++) ::AP.picks[p[i]] <- true;
		else if (p[0] == "count" && p.len() > 2) ::AP.counts[p[1]] <- p[2].tointeger();
	}
}

::AP_Save <- function() {
	local checks = "", picks = "", counts = "";
	foreach (map, _ in ::AP.checks) checks += " " + map;
	foreach (weapon, _ in ::AP.picks) picks += " " + weapon;
	foreach (stat, n in ::AP.counts) counts += "count " + stat + " " + n + "\n";
	StringToFile(::AP_OUT, "seed " + ::AP.seed + "\nack " + ::AP.ack + "\ndlseen " + ::AP.dlseen +
		"\ndeaths " + ::AP.deaths + "\nchecks" + checks + "\npicks" + picks + "\n" + counts + "end\n");
	::AP.dirty = false;
}

// Milestones are team totals; the client turns them into checks. Saved once a second, not per kill.
::AP_Count <- function(stat) {
	if (!::AP.connected) return;
	::AP.counts[stat] <- (stat in ::AP.counts ? ::AP.counts[stat] : 0) + 1;
	::AP.dirty = true;
}

::AP_IsSurvivor <- function(userid) {
	local p = GetPlayerFromUserID(userid);
	return p != null && p.IsSurvivor();
}

::AP_Campaign <- function(map) {
	local m = map.find("m");
	if (map.len() < 2 || map[0] != 'c' || m == null) return null;
	local c = map.slice(0, m);
	return (c in ::AP_FIRST_MAP) ? c : null;
}

::AP_Survivors <- function() {
	local list = [];
	local p = null;
	while ((p = Entities.FindByClassname(p, "player")) != null)
		if (p.IsSurvivor() && !p.IsDead()) list.append(p);
	return list;
}

::AP_Panic <- function() {
	local d = Entities.FindByClassname(null, "info_director");
	if (d == null) d = SpawnEntityFromTable("info_director", {});
	DoEntFire("!self", "ForcePanicEvent", "", 0, null, d);
}

::AP_Random <- function(list) {
	return list[RandomInt(0, list.len() - 1)];
}

// A weapon spawner (4 uses, one per survivor) in front of a random survivor; hand it out if spawning fails.
::AP_Drop <- function(weapon) {
	local survivors = ::AP_Survivors();
	local who = ::AP_Random(survivors);
	local f = who.GetForwardVector();
	local pos = who.GetOrigin() + Vector(f.x * 48, f.y * 48, 8);
	local ent = (weapon in ::AP_MELEE)
		? SpawnEntityFromTable("weapon_melee_spawn", { origin = pos, melee_weapon = weapon, count = 4 })
		: SpawnEntityFromTable("weapon_" + weapon + "_spawn", { origin = pos, count = 4 });
	if (ent == null) foreach (s in survivors) s.GiveItem(weapon);
}

::AP_Apply <- function(code, msg) {
	local p = split(code, ":");
	local kind = p[0], what = p.len() > 1 ? p[1] : "";
	local survivors = ::AP_Survivors();
	if (kind == "give") {
		foreach (s in survivors) s.GiveItem(what);
	} else if (kind == "drop") {
		::AP_Drop(what);
		msg += " (dropped nearby)";
	} else if (kind == "trap") {
		if (what in ::AP_SPAWN) ZSpawn({ type = ::AP_SPAWN[what] });
		else if (what == "horde") ::AP_Panic();
		else if (what == "vomit") foreach (s in survivors) s.HitWithVomit();
		else if (what == "fragile") {
			foreach (s in survivors) if (!s.IsIncapacitated()) { s.SetHealth(1); s.SetHealthBuffer(0); }
		} else if (what == "incap") {
			local standing = [];
			foreach (s in survivors) if (!s.IsIncapacitated()) standing.append(s);
			if (standing.len()) {
				local s = ::AP_Random(standing);
				s.TakeDamage(s.GetHealth() + s.GetHealthBuffer() + 1, 0, Entities.First());
			}
		}
	}
	::AP_Say("Received \x05" + msg);
}

::AP_KillAll <- function() {
	::AP.linkDeath = true;
	::AP_Say("\x04DeathLink!\x01 Someone else died, so you do too.");
	local world = Entities.First();
	for (local i = 0; i < 3; i++)  // standing -> incapped -> dead
		foreach (s in ::AP_Survivors()) s.TakeDamage(10000.0, 0, world);
}

::AP_Check <- function() {
	local map = Director.GetMapName();
	local c = ::AP_Campaign(map);
	if (!::AP.connected || map in ::AP.checks || (c != null && !(c in ::AP.unlocked))) return;
	::AP.checks[map] <- true;
	::AP_Save();
	::AP_Say("Location checked!");
}

::AP_CheckLock <- function() {
	if (::AP.lockTimer >= 0 || ::AP.unlocked.len() == 0) return;
	local c = ::AP_Campaign(Director.GetMapName());
	if (c == null || c in ::AP.unlocked) return;
	foreach (k in ::AP_ORDER) if (k in ::AP.unlocked) { ::AP.lockTarget = ::AP_FIRST_MAP[k]; break; }
	::AP.lockTimer = 5;
	::AP_Say("This campaign is \x04locked\x01. Find it in the multiworld! Moving you to an unlocked campaign...");
}

::AP_Poll <- function() {
	if (::AP.lockTimer > 0 && --::AP.lockTimer == 0 && ::AP.lockTarget != null)
		SendToServerConsole("changelevel " + ::AP.lockTarget);

	local text = FileToString(::AP_IN);
	if (text == null) {
		if (!::AP.warned) ::AP_Say("Waiting for the Archipelago client (Archipelago Launcher > Left 4 Dead 2 Client)...");
		::AP.warned = true;
		return;
	}
	local seed = null, dl = 0, unlocked = {}, items = [], complete = false;
	foreach (p in ::AP_Lines(text)) {
		if (p[0] == "seed" && p.len() > 1) seed = p[1];
		else if (p[0] == "unlocked") for (local i = 1; i < p.len(); i++) unlocked[p[i]] <- true;
		else if (p[0] == "dl") dl = p[1].tointeger();
		else if (p[0] == "item" && p.len() > 2) items.append(p);
		else if (p[0] == "end") complete = true;
	}
	if (!complete || seed == null) return;  // client is mid-write; try again next tick

	if (seed != ::AP.seed) {
		::AP.seed = seed; ::AP.ack = 0; ::AP.dlseen = 0; ::AP.deaths = 0; ::AP.checks = {};
		::AP.counts = {}; ::AP.picks = {};
		::AP_Save();
	}
	if (!::AP.connected) ::AP_Say("Connected to the Archipelago client.");
	::AP.connected = true;
	::AP.unlocked = unlocked;
	::AP_CheckLock();
	if (::AP.lockTimer >= 0 || ::AP_Survivors().len() == 0) return;

	local changed = ::AP.dirty;
	foreach (p in items) {
		local index = p[1].tointeger();
		if (index != ::AP.ack + 1) continue;
		try {
			::AP_Apply(p[2], ::AP_Join(p, 3));
		} catch (e) {
			printl("[AP] Could not apply item " + p[2] + ": " + e);  // skip it rather than block the queue
		}
		::AP.ack = index;
		changed = true;
	}
	if (dl > ::AP.dlseen) {
		::AP.dlseen = dl;
		::AP_KillAll();
		changed = true;
	}
	if (changed) ::AP_Save();
}

function OnGameplayStart() {
	::AP_Load();
	::AP.linkDeath = false;
	if (Entities.FindByName(null, "ap_think") == null) {
		local ent = SpawnEntityFromTable("info_target", { targetname = "ap_think" });
		ent.ValidateScriptScope();
		ent.GetScriptScope().Think <- function() { ::AP_Poll(); return 1.0; };
		AddThinkToEnt(ent, "Think");
	}
}

function OnGameEvent_map_transition(params) { ::AP_Check(); }
function OnGameEvent_finale_win(params) { ::AP_Check(); }

// --- milestones and pickups ----------------------------------------------------------------------------------------
function OnGameEvent_player_death(params) {
	if (!("userid" in params) || !("attacker" in params) || !::AP_IsSurvivor(params.attacker)) return;
	local victim = GetPlayerFromUserID(params.userid);
	if (victim == null || victim.IsSurvivor()) return;
	local type = victim.GetZombieType();
	if (type in ::AP_ZOMBIE) ::AP_Count(::AP_ZOMBIE[type]);
}

function OnGameEvent_infected_death(params) {
	if ("attacker" in params && ::AP_IsSurvivor(params.attacker)) ::AP_Count("common");
}

function OnGameEvent_witch_killed(params) {
	if (!("userid" in params) || !::AP_IsSurvivor(params.userid)) return;
	::AP_Count("witch");
	if ("oneshot" in params && params.oneshot) ::AP_Count("crown");
}

function OnGameEvent_revive_success(params) { ::AP_Count("revive"); }
function OnGameEvent_defibrillator_used(params) { ::AP_Count("defib"); }
function OnGameEvent_survivor_rescued(params) { ::AP_Count("rescue"); }

function OnGameEvent_heal_success(params) {
	if ("subject" in params && params.subject != params.userid) ::AP_Count("heal");  // teammates only
}

function OnGameEvent_item_pickup(params) {
	if (!::AP.connected || !("item" in params)) return;
	local weapon = params.item;
	if (weapon == "melee") {  // the event only says "melee"; the script name is on the weapon itself
		try {
			local player = GetPlayerFromUserID(params.userid), inv = {};
			GetInvTable(player, inv);
			weapon = NetProps.GetPropString(inv.slot1, "m_strMapSetScriptName");
		} catch (e) {
			return;
		}
	}
	if (weapon in ::AP.picks) return;
	::AP.picks[weapon] <- true;
	::AP.dirty = true;
}

function OnGameEvent_mission_lost(params) {
	if (!::AP.linkDeath) {
		::AP.deaths++;
		::AP_Save();
	}
	::AP.linkDeath = false;
}
