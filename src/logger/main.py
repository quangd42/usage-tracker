import click

from logger.genkey_json import create_corpus_json, save_to_json
from logger.Logger import DB_NAME, Logger


@click.group()
def cli():
    """CLI tool to log all keypresses for keyboard layout optimization.

    To see help for each command use: key-logger COMMAND --help"""
    pass


@cli.command()
def run():
    """Start the logger. End the logger with by typing `.end` command."""
    logger = Logger()
    logger.start()
    print("Listening to all keystrokes...")
    while True:
        command = input("Command: ")
        if command == ".end":
            logger.stop()
            break


@cli.command()
def view():
    """View the stats of the logged keys."""
    pass


@cli.command()
# @click.option("-f", "--format", default="g", help="Format for consuming analyzers")
def save():
    """Save logged keys to corpus json, default in genkey corput format."""
    # Support genkey only for now so "g" is the only option
    # Use enum for other analyzers later
    data = create_corpus_json(DB_NAME)
    save_to_json(data)


if __name__ == "__main__":
    run()
