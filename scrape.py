import click
import api
import pandas as pd

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


@click.group()
def cli():
    pass


@click.command()
@click.argument("boss", type=str, required=True)
@click.argument("gate", type=int, required=False)
@click.argument("difficulty", type=str, required=False)
@click.option(
    "--from-latest/--from-oldest",
    default=True,
    help="Start from either the latest or oldest log",
)
@click.option(
    "--from-scratch",
    default=False,
    is_flag=True,
    help="Start from scratch, overwrite cached logs",
)
@click.option(
    "--log-batches",
    default=20,
    help="Number of logs to fetch per batch",
)
@click.option(
    "--max-logs",
    default=100,
    help="Maximum number of logs to fetch before stopping.",
)
@click.option(
    "--patience",
    default=20,
    help="Number of empty calls before stopping.",
)
def boss(
    boss: str,
    gate: int = None,
    difficulty: str = None,
    from_latest: bool = True,
    from_scratch: bool = False,
    log_batches: int = 20,
    max_logs: int = 100,
    patience: int = 20,
):
    """
    Fetch logs for a specific boss, gate, and difficulty.

    BOSS is required, GATE and DIFFICULTY should not be set unless necessary.
    """
    click.echo(f"Fetching logs for {boss} {gate} {difficulty}")
    click.echo(f"Starting from {'latest' if from_latest else 'oldest'}")

    # Make filter
    filter = api.Filter(boss=boss, gate=gate, difficulty=difficulty)

    if from_scratch:
        click.echo("")
        click.echo("=== Starting from scratch ===")
        click.echo("WARNING: THIS OVERWRITES OLD LOGS")
        click.confirm("Are you sure you want to continue?", abort=True)

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
    while newLogsParsed < max_logs:
        logIDs = api.fetch_logIDs(
            filter.to_dict(),
            max_logs=log_batches,
            parsed_logs=oldIDs,
            last_id=lastID,
            last_date=lastDate,
            patience=patience,
        )

        for logID in logIDs:
            click.echo(f"Working on log ID {logID}")
            log = api.fetch_log(logID)

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

        # Save to csv (saves once per batch)
        df.to_csv(f"./data/{filter.to_name()}.csv", index=False)


cli.add_command(boss)

if __name__ == "__main__":
    cli()
