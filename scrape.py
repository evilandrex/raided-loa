import click
import api
import pandas as pd
import time


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
):
    click.echo(f"Fetching logs for {boss} {gate} {difficulty}")
    click.echo(f"Starting from {'latest' if from_latest else 'oldest'}")

    # Start timer
    start = time.time()

    # Make filter
    filter = api.Filter(boss=boss, gate=gate, difficulty=difficulty)

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
        logIDs = api.fetch_logIDs(
            filter.to_dict(),
            max_logs=log_batches,
            parsed_logs=oldIDs,
            last_id=lastID,
            last_date=lastDate,
        )
        if len(logIDs) == 0:
            emptyRounds += 1
            click.echo(f"Empty batch of logs, empty rounds: {emptyRounds}/{patience}.")

            continue
        else:
            emptyRounds = 0

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

    # End timer
    end = time.time()
    click.echo(f"Time elapsed: {end - start:.2f} seconds")


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
    default=100000000,
    help="Maximum number of logs to fetch before stopping.",
)
@click.option(
    "--patience",
    default=100000000,
    help="Number of empty calls before stopping.",
)
def boss(
    boss: str,
    gate: int = None,
    difficulty: str = None,
    from_latest: bool = True,
    from_scratch: bool = False,
    log_batches: int = 20,
    max_logs: int = 100000000,
    patience: int = 100000000,
):
    """
    Fetch logs for a specific boss, gate, and difficulty.

    BOSS is required, GATE and DIFFICULTY should not be set unless necessary.
    """
    # TODO: Scrap until date
    scrape_log(
        boss,
        gate,
        difficulty,
        from_latest,
        from_scratch,
        log_batches,
        max_logs,
        patience,
    )


cli.add_command(boss)


@click.command()
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
    default=100000000,
    help="Maximum number of logs to fetch before stopping",
)
@click.option(
    "--patience",
    default=100000000,
    help="Number of empty calls before stopping",
)
def all(
    from_latest: bool = True,
    from_scratch: bool = False,
    log_batches: int = 20,
    max_logs: int = 100000000,
    patience: int = 100000000,
):
    """Scrape all bosses."""
    # Start timer
    start = time.time()

    # Build a list of filter args
    bossArgs = []
    for bossName, info in api.BOSSES.items():
        # If info is empty, it's probably a guardian
        if info == {}:
            bossArgs += [{"boss": bossName}]
        else:
            # Get the keys for difficulty
            for diff, gates in info.items():
                for gate in gates:
                    bossArgs += [{"boss": bossName, "gate": gate, "difficulty": diff}]

    # Loop through bossArgs
    for kwargs in bossArgs:
        scrape_log(
            **kwargs,
            from_latest=from_latest,
            from_scratch=from_scratch,
            log_batches=log_batches,
            max_logs=max_logs,
            patience=patience,
            force=True,
        )

    # End timer
    end = time.time()
    click.echo(f"Time elapsed: {end - start:.2f} seconds")


cli.add_command(all)

if __name__ == "__main__":
    cli()
