import click
import api
import time
from typing import List


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
@click.option(
    "--verbose",
    "-v",
    default=False,
    is_flag=True,
    help="Print extra information",
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
    verbose: bool = False,
):
    """
    Fetch logs for a specific boss, gate, and difficulty.

    BOSS is required, GATE and DIFFICULTY should not be set unless necessary.
    """
    # TODO: Scrap until date

    # Start timer
    start = time.time()

    # Build a list of filter args
    bossArgs = []
    if boss == "all":
        for bossName, info in api.BOSSES.items():
            # If info is empty, it's probably a guardian
            if info == {}:
                bossArgs += [{"boss": bossName}]
            else:
                # Get the keys for difficulty
                for diff, gates in info.items():
                    for gate in gates:
                        bossArgs += [
                            {"boss": bossName, "gate": gate, "difficulty": diff}
                        ]
    else:
        bossArgs += [{"boss": boss, "gate": gate, "difficulty": difficulty}]

    for kwargs in bossArgs:
        api.scrape_log(
            **kwargs,
            from_latest=from_latest,
            from_scratch=from_scratch,
            log_batches=log_batches,
            max_logs=max_logs,
            patience=patience,
            force=boss == "all",
            verbose=verbose,
        )

    # End timer
    end = time.time()
    click.echo(f"Time elapsed: {end - start:.2f} seconds")


cli.add_command(boss)


@click.command()
@click.argument("boss", type=str, required=True)
@click.argument("gate", type=int, required=False)
@click.argument("difficulty", type=str, required=False)
@click.option(
    "--id",
    default=[],
    help="Update specific log IDs",
    multiple=True,
)
@click.option(
    "--build",
    default=[],
    help="Update specific builds",
    multiple=True,
)
@click.option(
    "--verbose",
    "-v",
    default=False,
    is_flag=True,
    help="Print extra information",
)
def update(
    boss: str = None,
    gate: int = None,
    difficulty: str = None,
    *,
    id: List[int] = [],
    build: List[str] = [],
    verbose: bool = False,
):
    """
    Update the log IDs or builds for the BOSS, GATE, and DIFFICULTY.

    BOSS is required, GATE and DIFFICULTY should not be set unless necessary.
    """
    if len(id) == 0 and len(build) == 0:
        raise ValueError("Either ID or build must be set.")

    # Start timer
    start = time.time()

    # Build a list of filter args
    bossArgs = []
    if boss == "all":
        for bossName, info in api.BOSSES.items():
            # If info is empty, it's probably a guardian
            if info == {}:
                bossArgs += [{"boss": bossName}]
            else:
                # Get the keys for difficulty
                for diff, gates in info.items():
                    for gate in gates:
                        bossArgs += [
                            {"boss": bossName, "gate": gate, "difficulty": diff}
                        ]
    else:
        bossArgs += [{"boss": boss, "gate": gate, "difficulty": difficulty}]

    # Loop through bossArgs
    for kwargs in bossArgs:
        api.update_logs(
            **kwargs,
            ids=id,
            builds=build,
            verbose=verbose,
        )

    # End timer
    end = time.time()
    click.echo(f"Time elapsed: {end - start:.2f} seconds")


cli.add_command(update)

if __name__ == "__main__":
    cli()
