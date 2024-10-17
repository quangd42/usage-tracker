import click
from tabulate import tabulate

from cli.corpus_json import save_to_json
from cli.helpers import print_session_list
from db.queries import DatabaseQueries
from logger.logger import Logger
from models.genkey import GenkeyOutput

GENKEY_KEYS = GenkeyOutput.list_keys()
DB_NAME = 'logger.db'


@click.group()
def cli() -> None:
    """CLI tool to log all keypresses for keyboard layout optimization.

    To see help for each command use: klgr COMMAND --help"""
    pass


@cli.command()
@click.option('-n', '--name', help='Start a session with provided name.')
def run(name: str) -> None:
    """Start the logger with the provided session name.

    End the logger with by typing `.end` command."""

    db = DatabaseQueries(DB_NAME)
    if not name:
        session_list = db.list_sessions()
        print_session_list(session_list)
        name = click.prompt(
            'Choose from existing session or type "new" for new session',
            type=click.Choice(session_list + ['new'], case_sensitive=False),
            show_choices=False,
        )
        if name == 'new':
            name = click.prompt('New session name')

    logger = Logger(db, name)
    logger.start()

    click.echo('---')
    click.echo("""Available commands:
    '.pse': Pause logging.
    '.rse': Resume logging.
    '.end': Stop logging and save to db.
    When executed these commands are not logged.
    """)
    click.echo(
        f'Started session {click.style(name, italic=True, bold=True)}. Listening to all keystrokes...'
    )
    while True:
        try:
            command = input('Command: ')
            if command == '.end':
                logger.stop()
                break
            if command == '.pse':
                logger.pause()
            if command == '.rse':
                logger.resume()
        except Exception as e:
            raise click.ClickException(f'Error: {e}')


@cli.command()
@click.argument('session', type=str)
@click.option(
    '--ngrams_name',
    '-n',
    type=click.Choice(GENKEY_KEYS, case_sensitive=False),
    prompt=True,
    help='Ngram name to view',
)
@click.option('--limit', '-l', default=20, help='Number of top ngrams to view.')
@click.option(
    '--sort_by',
    '-s',
    default='value',
    type=click.Choice(['name', 'value']),
    help='Sort results by name or value.',
)
@click.option(
    '--with_mods', '-m', is_flag=True, help='Show modifiers recorded with letters'
)
def view(
    session: str, ngrams_name: str, limit: int, sort_by: str, with_mods: bool
) -> None:
    """View the stats of the logged keys of provided session name.

    Valid stat names are 'letters', 'bigrams', 'trigrams', 'skipgrams'.

    Default limit is 20. Set limit -1 to see all ngrams.
    """

    db = DatabaseQueries(DB_NAME)
    sessions = db.list_sessions()
    if session not in sessions:
        print_session_list(sessions)
        raise click.ClickException('Session does not exist.')

    if with_mods and ngrams_name != 'letters':
        raise click.ClickException('Mods are only recorded with letters.')

    stat = db.get_stats(
        session=session,
        stat_name=ngrams_name,
        limit=limit,
        sort_by=sort_by,
        with_mods=with_mods,
    )
    click.echo(f'Session: {session}')
    click.echo(f'Ngram: {ngrams_name}')
    click.echo(tabulate(stat, headers='firstrow', tablefmt='rounded_outline'))


@cli.command()
def list() -> None:
    """List logged sessions by name."""

    db = DatabaseQueries(DB_NAME)
    session_list = db.list_sessions()
    print_session_list(session_list)


@cli.command()
@click.argument('session')
def delete(session: str) -> None:
    """Delete a logged sessions by name."""

    db = DatabaseQueries(DB_NAME)

    try:
        db.delete_session(session)
        db.conn.commit()
        session_list = db.list_sessions()
        print_session_list(session_list)
    except Exception as e:
        raise click.ClickException(f'{e}')


@cli.command()
@click.argument('session')
# Support genkey only for now so "g" is the only option
# @click.option("-f", "--format", default="g", help="Format for consuming analyzers")
def export(session: str) -> None:
    """Save logged keys to corpus json, default in genkey corput format."""

    db = DatabaseQueries(DB_NAME)

    data = db.get_genkey_stats(session)
    save_to_json(data)


if __name__ == '__main__':
    run()
