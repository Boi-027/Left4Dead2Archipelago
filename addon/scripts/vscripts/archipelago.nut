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
	seed = "", ack = 0, dlseen = 0, deaths = 0, checks = {},   // persisted in out.txt
	unlocked = {}, connected = false, warned = false, linkDeath = false, lockTimer = -1, lockTarget = null
}

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
	}
}

::AP_Save <- function() {
	local checks = "";
	foreach (map, _ in ::AP.checks) checks += " " + map;
	StringToFile(::AP_OUT, "seed " + ::AP.seed + "\nack " + ::AP.ack + "\ndlseen " + ::AP.dlseen +
		"\ndeaths " + ::AP.deaths + "\nchecks" + checks + "\nend\n");
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

::AP_Apply <- function(code, msg) {
	local p = split(code, ":");
	local kind = p[0], what = p.len() > 1 ? p[1] : "";
	if (kind == "give") {
		foreach (s in ::AP_Survivors()) s.GiveItem(what);
	} else if (kind == "trap") {
		if (what == "tank") ZSpawn({ type = 8 });
		else if (what == "witch") ZSpawn({ type = 7 });
		else if (what == "horde") ::AP_Panic();
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
		::AP_Save();
	}
	if (!::AP.connected) ::AP_Say("Connected to the Archipelago client.");
	::AP.connected = true;
	::AP.unlocked = unlocked;
	::AP_CheckLock();
	if (::AP.lockTimer >= 0 || ::AP_Survivors().len() == 0) return;

	local changed = false;
	foreach (p in items) {
		local index = p[1].tointeger();
		if (index != ::AP.ack + 1) continue;
		::AP_Apply(p[2], ::AP_Join(p, 3));
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

function OnGameEvent_mission_lost(params) {
	if (!::AP.linkDeath) {
		::AP.deaths++;
		::AP_Save();
	}
	::AP.linkDeath = false;
}
