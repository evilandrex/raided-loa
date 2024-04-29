import requests
import json
import pandas as pd
from typing import List
from ratelimit import limits, sleep_and_retry


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
@limits(calls=299, period=60)
def _call_logsAPI(
    filter: dict,
    query_strings: dict = {"scope": "arkesia", "order": "recent%20clear"},
) -> requests.Response:
    """Call the logs API with a filter, returns a set of logs"""
    # Turn query_strings dict into a string
    query_string = "&".join([f"{key}={value}" for key, value in query_strings.items()])

    return requests.post(f"https://logs.fau.dev/api/logs?{query_string}", json=filter)


def fetch_logIDs(
    filter: dict,
    max_logs: int = None,
    parsed_logs: List[int] = [],
    last_id: int = None,
    last_date: int = None,
) -> List[int]:
    # Keep fetching logs to get IDs until we can't
    logIDs = []
    fetching = True
    while fetching:
        if last_id is None:
            r = _call_logsAPI(filter)
        else:
            query_strings = {
                "scope": "arkesia",
                "order": "recent%20clear",
                "past_id": last_id,
                "past_field": last_date,
            }
            r = _call_logsAPI(filter, query_strings)

        data = json.loads(r.text)

        # Get IDs
        ids = [log["id"] for log in data["encounters"]]
        last_id = ids[-1]
        last_date = data["encounters"][-1]["date"]

        # Filter ids that we already have
        ids = [id for id in ids if id not in parsed_logs]
        logIDs += ids
        print(f"Found {len(logIDs)} logs")

        # Check if we should keep fetching
        fetching = data["more"] and (max_logs is None or len(logIDs) < max_logs)

    return logIDs


@sleep_and_retry
@limits(calls=99, period=60)
def _call_logAPI(id: int) -> requests.Response:
    """Call the log API with a log ID, returns the log data"""
    return requests.get(f"https://logs.fau.dev/api/log/{id}")


def fetch_log(id: int) -> List[dict]:
    r = _call_logAPI(id)
    data = json.loads(r.text)

    # Get general information
    date = data["date"]
    duration = data["duration"]

    # Get the players
    playerData = data["players"]
    players = playerData.keys()

    playerEntries = []
    for player in players:
        playerClass = playerData[player]["class"]
        gearScore = playerData[player]["gearScore"]
        dps = playerData[player]["dps"]

        playerEntries += [
            {
                "id": id,
                "player": player,
                "class": playerClass,
                "gearScore": gearScore,
                "dps": dps,
                "date": date,
                "duration": duration,
            }
        ]

    return pd.DataFrame(playerEntries)


if __name__ == "__main__":
    filter = Filter(boss="Akkan", gate=3, difficulty="Hard")

    # Load up old data file
    try:
        df = pd.read_csv(f"./data/{filter.to_name()}.csv", index_col=None)
        oldIDs = df["id"].unique()

        # Find the last ID
        lastID = df["id"].min()
        lastDate = df[df["id"] == lastID]["date"].values[0]
    except FileNotFoundError:
        df = pd.DataFrame()
        oldIDs = []
        lastID = None
        lastDate = None

    logIDs = fetch_logIDs(
        filter.to_dict(),
        max_logs=20,
        parsed_logs=oldIDs,
        last_id=lastID,
        last_date=lastDate,
    )

    for logID in logIDs:
        print(f"Working on log ID {logID}")
        log = fetch_log(logID)

        df = pd.concat([df, log])

    df.to_csv(f"./data/{filter.to_name()}.csv", index=False)
    print(df)
