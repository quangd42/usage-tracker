import click
from click.exceptions import Abort
from tabulate import tabulate

from cli.helpers import get_session_list, get_stat_from_db
from cli.corpora_json import GenkeyOutput, create_genkey_json, save_to_json
from logger.logger import DB_NAME, Logger

GENKEY_KEYS = GenkeyOutput.list_keys()


# TODO: add better type annotation
@click.group()
def cli():
    """CLI tool to log all keypresses for keyboard layout optimization.

    To see help for each command use: klgr COMMAND --help"""
    pass


@cli.command()
# TODO: default option to use the last session
@click.option("-n", "--new", help="Start a new session with provided name.")
@click.option(
    "-s",
    "--session",
    help="Continue logging into session with provided name.",
)
def run(new: str, session: str):
    """Start the logger with the provided session name.

    End the logger with by typing `.end` command."""

    if new:
        session = new
    elif not session:
        try:
            session_list = get_session_list(DB_NAME)
            session = click.prompt(
                f"Existing session/s: {session_list}\nChoose session or 'new' to start new",
                type=click.Choice(session_list + ["new"], case_sensitive=False),
                show_choices=False,
            )
            if session == "new":
                raise Exception
        except Abort:
            raise click.Abort()
        except Exception:
            session = click.prompt("Session name")

    logger = Logger(session)
    logger.start()

    click.echo("---")
    click.echo(
        f"Started session {click.style(session, italic=True, bold=True)}. Listening to all keystrokes..."
    )
    while True:
        try:
            command = input("Command: ")
            if command == ".end":
                logger.stop()
                break
            if command == ".pse":
                logger.pause()
            if command == ".rse":
                logger.resume()
        except Exception as e:
            raise click.ClickException(f"error: {e}")


@cli.command()
@click.argument("session", type=str)
@click.option(
    "--ngrams_name",
    "-n",
    type=click.Choice(GENKEY_KEYS, case_sensitive=False),
    prompt=True,
    help="Ngram name to view",
)
@click.option("--limit", "-l", default=20, help="Number of top ngrams to view.")
@click.option(
    "--sort_by",
    "-s",
    default="value",
    type=click.Choice(["name", "value"]),
    help="Sort results by name or value.",
)
def view(session: str, ngrams_name: str, limit: int, sort_by: str):
    """View the stats of the logged keys of provided session name.

    Valid stat names are 'letters', 'bigrams', 'trigrams', 'skipgrams'."""

    sessions = get_session_list(DB_NAME)
    if session not in sessions:
        raise click.ClickException("Session does not exist.")
    stat = get_stat_from_db(
        session=session,
        stat_name=ngrams_name,
        limit=limit,
        sort_by=sort_by,
        db_name=DB_NAME,
    )
    click.echo(f"Session: {session}")
    click.echo(f"Ngram: {ngrams_name}")
    click.echo(tabulate(stat, headers="firstrow", tablefmt="rounded_outline"))


@cli.command()
# Support genkey only for now so "g" is the only option
# @click.option("-f", "--format", default="g", help="Format for consuming analyzers")
def save() -> None:
    """Save logged keys to corpus json, default in genkey corput format."""

    session_list = get_session_list(DB_NAME)
    session = click.prompt(
        'Choose session',
        type=click.Choice(session_list, case_sensitive=False),
        show_choices=False,
    )

    data = create_genkey_json(DB_NAME, session)
    save_to_json(data)


@cli.command()
def list():
    """List logged sessions by name."""
    sessions = get_session_list(DB_NAME)
    click.echo(
        tabulate(
            enumerate(sessions),
            headers=["no", "session"],
            tablefmt="rounded_outline",
        )
    )


if __name__ == "__main__":
    run()
