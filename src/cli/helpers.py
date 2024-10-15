import click
from tabulate import tabulate


def print_session_list(sessions: list[str]) -> None:
    click.echo('Existing session/s:')
    click.echo(
        tabulate(
            enumerate(sessions),
            headers=['no', 'session'],
            tablefmt='rounded_outline',
            showindex=False,
        )
    )
