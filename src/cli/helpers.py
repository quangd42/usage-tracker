import click
from tabulate import tabulate

from db.queries import DatabaseQueries


def print_session_list(sessions: list[str]) -> None:
    if len(sessions) > 0:
        click.echo('Existing session/s:')
        click.echo(
            tabulate(
                enumerate(sessions),
                headers=['no', 'session'],
                tablefmt='rounded_outline',
                showindex=False,
            )
        )
    else:
        click.echo('No recorded session.')


def prompt_for_session(db: DatabaseQueries) -> str:
    session_list = db.list_sessions()
    print_session_list(session_list)
    session = click.prompt(
        'Choose session',
        type=click.Choice(session_list, case_sensitive=False),
        show_choices=False,
    )
    return session
