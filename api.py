import requests
import json
import pandas as pd
from typing import List
from ratelimit import limits, sleep_and_retry
import click
import time

SUPPORTS = ["Full Bloom", "Blessed Aura", "Desperate Salvation"]
BOSSES = {
    "Sonavel": {},
    "Gargadeth": {},
    "Veskal": {},
    "Brelshaza": {"Hard": [1, 2, 3, 4]},
    "Kayangel": {"Hard": [1, 2, 3]},
    "Akkan": {"Normal": [1, 2, 3], "Hard": [1, 2, 3]},
    "Ivory": {"Normal": [1, 2, 3, 4], "Hard": [1, 2, 3, 4]},
    "Thaemine": {"Normal": [1, 2, 3], "Hard": [1, 2, 3, 4]},
}


class Filter:
    """Class for a query filter"""

    def __init__(self, *, boss: str, gate: int = None, difficulty: str = None):
        self.boss = boss
        self.gate = gate
        self.difficulty = difficulty

        self.guardians = ["Caliligos", "Hanumatan", "Sonavel", "Gargadeth", "Veskal"]
        self.raids = {
            "Valtan": [1, 2],
            "Vykas": [1, 2, 3],
            "Kakul Saydon": [1, 2, 3],
            "Brelshaza": [1, 2, 3, 4, 5, 6],
            "Kayangel": [1, 2, 3],
            "Akkan": [1, 2, 3],
            "Ivory": [1, 2, 3, 4],
            "Thaemine": [1, 2, 3, 4],
        }

        # Validate the filter
        if boss not in self.guardians and boss not in self.raids:
            raise ValueError(f"Invalid boss: {boss}")

        # Check guardian
        if boss in self.guardians:
            if gate is not None or difficulty is not None:
                raise ValueError(f"Guardians don't have gates or difficulties")
        else:
            # Check raid
            if gate is None or difficulty is None:
                raise ValueError(f"Raid bosses require a gate and difficulty")

            # Check gate
            if gate not in self.raids[boss]:
                raise ValueError(f"Invalid gate for {boss}")

            # Check difficulty
            if difficulty not in ["Normal", "Hard"]:
                raise ValueError(f"Invalid difficulty: {difficulty}")

    def to_dict(self) -> dict:
        """Convert the filter to a dictionary"""
        if self.boss in self.raids:
            return {
                "raids": {
                    self.boss: {
                        "gates": [self.gate],
                        "difficulties": [self.difficulty],
                    }
                }
            }
        else:
            return {"guardians": [self.boss]}

    def to_name(self) -> str:
        if self.boss in self.guardians:
            return f"{self.boss}"
        else:
            return f"{self.boss.replace(' ', '')}_G{self.gate}_{self.difficulty}"

    def __repr__(self) -> str:
        return (
            f"Filter(boss={self.boss}, gate={self.gate}, difficulty={self.difficulty})"
        )


@sleep_and_retry
@limits(calls=250, period=58)
def _call_logsAPI(
    filter: dict,
    query_strings: dict = {"scope": "arkesia", "order": "recent%20clear"},
) -> requests.Response:
    """Call the logs API with a filter, returns a set of logs"""
    # Turn query_strings dict into a string
    query_string = "&".join([f"{key}={value}" for key, value in query_strings.items()])

    try:
        return requests.post(
            f"https://logs.fau.dev/api/logs?{query_string}", json=filter
        )
    except:
        time.sleep(30)
        return requests.post(
            f"https://logs.fau.dev/api/logs?{query_string}", json=filter
        )


def fetch_logIDs(
    filter: dict,
    max_logs: int = None,
    parsed_logs: List[int] = [],
    last_id: int = None,
    last_date: int = None,
    patience: int = 20,
    verbose: bool = False,
) -> List[int]:
    # Keep fetching logs to get IDs until we can't
    logIDs = []
    fetching = True
    emptyRounds = 0

    if verbose:
        click.echo("Looking for logs")
    while fetching:
        if last_id is None:
            query_strings = {}
            r = _call_logsAPI(filter)
        else:
            query_strings = {
                "scope": "arkesia",
                "order": "recent%20clear",
                "past_id": last_id,
                "past_field": last_date,
            }
            r = _call_logsAPI(filter, query_strings)

        if r.status_code == 429:
            click.echo(f"Rate limited, waiting to retry.")
            with click.progressbar(range(int(r.headers["Retry-After"]) + 30)) as bar:
                for _ in bar:
                    time.sleep(1)

            r = _call_logsAPI(filter, query_strings)

        try:
            data = json.loads(r.text)
        except json.JSONDecodeError:
            time.sleep(5)
            r = _call_logsAPI(filter, query_strings)
            data = json.loads(r.text)

        # Get IDs
        ids = [log["id"] for log in data["encounters"]]

        if len(ids) == 0:
            click.echo("No more logs!")
        else:
            last_id = ids[-1]
            last_date = data["encounters"][-1]["date"]

            # Filter ids that we already have
            ids = [id for id in ids if id not in parsed_logs]
            logIDs += ids

            if verbose:
                click.echo(f"Found {len(logIDs)} logs so far\r", nl=False)

            if len(ids) == 0:
                emptyRounds += 1

        # Check if we should keep fetching
        fetching = (
            data["more"]
            and (max_logs is None or len(logIDs) < max_logs)
            and emptyRounds < patience
        )

    if verbose:
        click.echo(f"Found a total of {len(logIDs)} logs")

    return logIDs


@sleep_and_retry
@limits(calls=180, period=58)
def _call_logAPI(id: int) -> requests.Response:
    """Call the log API with a log ID, returns the log data"""
    try:
        return requests.get(f"https://logs.fau.dev/api/log/{id}")
    except:
        time.sleep(30)
        return requests.get(f"https://logs.fau.dev/api/log/{id}")


def fetch_log(id: int) -> List[dict]:
    r = _call_logAPI(id)

    if r.status_code == 429:
        click.echo(f"Rate limited, waiting to retry.")
        with click.progressbar(range(int(r.headers["Retry-After"]) + 30)) as bar:
            for _ in bar:
                time.sleep(1)

        r = _call_logAPI(id)

    try:
        data = json.loads(r.text)
    except json.JSONDecodeError:
        time.sleep(30)
        r = _call_logAPI(id)
        data = json.loads(r.text)

    # Get general information
    date = data["date"]
    duration = data["duration"]

    # Classify specs
    specs = classify_class(data)

    # Classify weird
    weird = classify_weird(data, specs)

    # Get the players
    playerData = data["players"]
    players = playerData.keys()

    playerEntries = []
    for player in players:
        playerEntries += [
            {
                "id": id,
                "player": player,
                "class": specs[player],
                "gearScore": playerData[player]["gearScore"],
                "dps": playerData[player]["dps"],
                "percent": playerData[player]["percent"],
                "date": date,
                "duration": duration,
                "dead": playerData[player]["dead"],
                "weird": weird,
            }
        ]

    return pd.DataFrame(playerEntries)


def classify_class(log: dict) -> dict:
    """Classify each player's spec based on the log"""

    def _check_skillSelfBuff(buffName: str) -> bool:
        pSelfBuffs = [
            buffCatalog[buff["buffs"][0]]["name"] for buff in pDetail["skillSelfBuffs"]
        ]
        return len([buff for buff in pSelfBuffs if buffName in buff]) > 0

    def _check_set(setName: str) -> bool:
        return f"set_{setName}" in pDetail["selfBuff"].keys()

    # Grab relevant data
    buffCatalog = log["data"]["buffCatalog"]
    skillCatalog = log["data"]["skillCatalog"]

    playerSpecs = {}
    for name, data in log["players"].items():
        # Figure out class
        pClass = data["class"]
        # Get player details
        pDetail = log["data"]["players"][name]

        if pClass == "Berserker":
            # Check if you have the Mayhem self skill buff
            playerSpecs[name] = (
                "Mayhem" if _check_skillSelfBuff("Mayhem") else "Berserker's Technique"
            )
        elif pClass == "Destroyer":
            # Look for skill "18030" special "Basic 3 Chain Hits" and does high damage split
            playerSpecs[name] = (
                "Gravity Training"
                if "18030" in pDetail["skillDamage"].keys()
                and float(pDetail["skillDamage"]["18030"]["percent"]) > 30
                else "Rage Hammer"
            )
        elif pClass == "Gunlancer":
            # First check if they're Princess Maker
            if float(log["players"][name]["percent"]) < 5:
                playerSpecs[name] = "Princess Maker"
            else:
                # Looking for set
                playerSpecs[name] = (
                    "Combat Readiness"
                    if _check_set("Hallucination") or _check_set("Nightmare")
                    else "Lone Knight"
                )
        elif pClass == "Paladin":
            # Checking if this person does okay damage
            playerSpecs[name] = (
                "Judgment"
                if float(log["players"][name]["percent"]) > 10
                else "Blessed Aura"
            )
        elif pClass == "Slayer":
            # Looking for the "Predator" skill self buff
            playerSpecs[name] = (
                "Predator" if _check_skillSelfBuff("Predator") else "Punisher"
            )
        elif pClass == "Arcanist":
            # Uses the "Emperor" skill to decide spec
            playerSpecs[name] = (
                "Order of the Emperor"
                if "19282" in pDetail["skillDamage"].keys()
                else "Empress's Grace"
            )
        elif pClass == "Summoner":
            # Check if "20290" Kelsion, is in skills
            playerSpecs[name] = (
                "Communication Overflow"
                if "20290" in pDetail["skillDamage"].keys()
                else "Master Summoner"
            )
        elif pClass == "Bard":
            # Check if they're doing okay damage
            playerSpecs[name] = (
                "True Courage"
                if float(log["players"][name]["percent"]) > 10
                else "Desperate Salvation"
            )
        elif pClass == "Sorceress":
            # Looking for "Igniter" self buff
            playerSpecs[name] = (
                "Igniter" if _check_skillSelfBuff("Igniter") else "Reflux"
            )
        elif pClass == "Wardancer":
            # Looking for esoteric skill names
            playerSpecs[name] = (
                "Esoteric Skill Enhancement"
                if any(
                    [
                        "Esoteric Skill: " in skillCatalog[id]["name"]
                        for id in pDetail["skillDamage"].keys()
                    ]
                )
                else "First Intention"
            )
        elif pClass == "Scrapper":
            # This one is weird where the Shock Training buff is ID "500224" but it doesn't have a name
            playerSpecs[name] = (
                "Shock Training"
                if len(
                    [
                        buff
                        for buff in pDetail["skillSelfBuffs"]
                        if buff["buffs"][0] == "500224"
                    ]
                )
                > 0
                else "Ultimate Skill: Taijutsu"
            )
        elif pClass == "Soulfist":
            # A weird one where the RS Hype is ID "240250" but it doesn't have a name
            playerSpecs[name] = (
                "Robust Spirit"
                if len(
                    [
                        buff
                        for buff in pDetail["skillSelfBuffs"]
                        if buff["buffs"][0] == "240250"
                    ]
                )
                > 0
                else "Energy Overflow"
            )
        elif pClass == "Glaivier":
            # Look for the "Pinnacle" skill self buff
            playerSpecs[name] = (
                "Pinnacle" if _check_skillSelfBuff("Pinnacle") else "Control"
            )
        elif pClass == "Striker":
            # Looking for the skill ID "39110", Call of the Wind God
            playerSpecs[name] = (
                "Esoteric Flurry"
                if "39110" in pDetail["skillDamage"].keys()
                else "Deathblow"
            )
        elif pClass == "Breaker":
            # Looking for the skill "47020" Asura Destruction Basic Attack
            playerSpecs[name] = (
                "Asura's Path"
                if "47020" in pDetail["skillDamage"].keys()
                else "Brawl King Storm"
            )
        elif pClass == "Deathblade":
            # Check if "25402" RE Death Trance exists and does damage
            playerSpecs[name] = (
                "Remaining Energy"
                if "25402" in pDetail["skillDamage"].keys()
                and float(pDetail["skillDamage"]["25402"]["percent"]) > 10
                else "Surge"
            )
        elif pClass == "Shadowhunter":
            # Looking for Demonic Impulse self buff
            playerSpecs[name] = (
                "Demonic Impulse"
                if _check_skillSelfBuff("Demonic Impulse")
                else "Perfect Suppression"
            )
        elif pClass == "Reaper":
            # Checking for the "Lunar Voice" self buff
            playerSpecs[name] = (
                "Lunar Voice" if _check_skillSelfBuff("Lunar Voice") else "Hunger"
            )
        elif pClass == "Souleater":
            # Checking for "Soul Snatch" self buff
            playerSpecs[name] = (
                "Night's Edge"
                if _check_skillSelfBuff("Soul Snatch")
                else "Full Moon Harvester"
            )
        elif pClass == "Sharpshooter":
            # Look for Loyal Companion skill self buff
            playerSpecs[name] = (
                "Loyal Companion"
                if _check_skillSelfBuff("Loyal Companion")
                else "Death Strike"
            )
        elif pClass == "Deadeye":
            # Look for the "Enhanced Weapon" self skill buff
            playerSpecs[name] = (
                "Enhanced Weapon"
                if _check_skillSelfBuff("Enhanced Weapon")
                else "Pistoleer"
            )
        elif pClass == "Artillerist":
            # Looking for "30260" Barrage: Focus Fire and doing more than 10% damage
            playerSpecs[name] = (
                "Barrage Enhancement"
                if "30260" in pDetail["skillDamage"].keys()
                and float(pDetail["skillDamage"]["30260"]["percent"]) > 10
                else "Firepower Enhancement"
            )
        elif pClass == "Machinist":
            # Look for Evolutionary Legacy skill self buff
            playerSpecs[name] = (
                "Evolutionary Legacy"
                if _check_skillSelfBuff("Evolutionary Legacy")
                else "Arthetinean Skill"
            )
        elif pClass == "Gunslinger":
            # Looking for Sharpshooter skill
            playerSpecs[name] = (
                "Peacemaker" if "38110" in pDetail["skillDamage"] else "Time to Hunt"
            )
        elif pClass == "Artist":
            # Checks if they're doing okay damage
            playerSpecs[name] = (
                "Recurrence"
                if float(log["players"][name]["percent"]) > 10
                else "Full Bloom"
            )
        elif pClass == "Aeromancer":
            # Check for the synergy buff "320405" sunshower on the sunshower skill "32041"
            playerSpecs[name] = (
                "Wind Fury"
                if "32041" in pDetail["skillSynergy"].keys()
                and "603_320405" in pDetail["skillSynergy"]["32041"].keys()
                else "Drizzle"
            )
        else:
            playerSpecs[name] = "Unknown"

    return playerSpecs


def classify_weird(log: dict, specs: dict) -> bool:
    # Doesn't have 4 or 8 players
    nPlayers = len(log["players"])
    if nPlayers not in [4, 8]:
        return True

    # Has Princess GL
    if "Princess Maker" in specs.values():
        return True

    # Does not have the expected number of supports
    nSupports = len([spec for spec in specs.values() if spec in SUPPORTS])
    if (nPlayers == 4 and not nSupports == 1) or (nPlayers == 8 and not nSupports == 2):
        return True

    # Player without a class
    if "Unknown" in specs.values():
        return True

    return False


def scrape_log(
    boss: str,
    gate: int = None,
    difficulty: str = None,
    from_latest: bool = True,
    from_scratch: bool = False,
    log_batches: int = 20,
    max_logs: int = 100000000,
    patience: int = 100000000,
    force: bool = False,
    verbose: bool = False,
) -> None:
    click.echo(f"Fetching logs for {boss} {gate} {difficulty}")
    click.echo(f"Starting from {'latest' if from_latest else 'oldest'}")

    # Start timer
    start = time.time()

    # Make filter
    filter = Filter(boss=boss, gate=gate, difficulty=difficulty)

    if from_scratch:
        click.echo("")
        click.echo("=== Starting from scratch ===")
        click.echo("WARNING: THIS OVERWRITES OLD LOGS")
        if not force:
            click.confirm("Are you sure you want to continue?", abort=True)
        else:
            click.echo("Continuing without confirmation in three seconds.")
            time.sleep(3)

        df = pd.DataFrame()
        oldIDs = []
        lastID = None
        lastDate = None
    else:
        # Try to load old data file
        try:
            df = pd.read_csv(f"./data/{filter.to_name()}.csv", index_col=None)
            oldIDs = df["id"].unique()

            if not from_latest:
                lastID = df["id"].min()
                lastDate = df[df["id"] == lastID]["date"].values[0]
            else:
                lastID = None
                lastDate = None

        except FileNotFoundError:
            df = pd.DataFrame()
            oldIDs = []
            lastID = None
            lastDate = None

    # Fetch logs until we hit max
    newLogsParsed = 0
    emptyRounds = 0
    while newLogsParsed < max_logs and emptyRounds < patience:
        logIDs = fetch_logIDs(
            filter.to_dict(),
            max_logs=log_batches,
            parsed_logs=oldIDs,
            last_id=lastID,
            last_date=lastDate,
            verbose=verbose,
        )
        if len(logIDs) == 0:
            emptyRounds += 1
            if verbose:
                click.echo(
                    f"Empty batch of logs, empty rounds: {emptyRounds}/{patience}."
                )

            continue
        else:
            emptyRounds = 0

        if verbose:
            click.echo("Scraping for log info")
        for logID in logIDs:
            if verbose:
                click.echo(f"Working on log ID {logID}\r", nl=False)
            log = fetch_log(logID)

            df = pd.concat([df, log])
            newLogsParsed += 1

            # Update lastID and lastDate
            lastID = logID
            lastDate = log["date"].values[0]

        oldIDs = df["id"].unique()

        # If no logs have been found, quit
        if len(logIDs) == 0:
            click.echo("No more logs found.")
            break

        if verbose:
            click.echo("Batch complete, saving logs.")
        # Save to csv (saves once per batch)
        df.to_csv(f"./data/{filter.to_name()}.csv", index=False)

    # End timer
    end = time.time()
    click.echo(f"Time elapsed: {end - start:.2f} seconds")
    click.echo(f"Logs scraped: {newLogsParsed}")
    click.echo("==========")


def update_logs(
    boss: str,
    gate: int = None,
    difficulty: str = None,
    *,
    ids: List[int] = [],
    builds: List[str] = [],
    verbose: bool = False,
) -> None:
    """
    Update the logs for a specific boss, gate, difficulty based on an ID or build
    """
    # Only one of IDs or builds should be set
    if len(ids) > 0 and len(builds) > 0:
        raise ValueError("Either ID or build must be set.")

    # Load the data for the encounter
    filter = Filter(boss=boss, gate=gate, difficulty=difficulty)
    data = pd.read_csv(f"./data/{filter.to_name()}.csv")

    # Get IDs to update
    toUpdate = list(ids)
    if len(builds) > 0:
        toUpdate += list(data.loc[data['class'].isin(builds)]["id"].unique())

    # Remove the to be updated IDs from data
    data = data[~data["id"].isin(toUpdate)]

    # Fetch the logs
    for id in toUpdate:
        if verbose:
            click.echo(f"Updating log ID {id}")
        log = fetch_log(id)

        data = pd.concat([data, log])

    # Save the data
    data.to_csv(f"./data/{filter.to_name()}.csv", index=False)
