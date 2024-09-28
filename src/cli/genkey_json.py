import json
import sqlite3
from datetime import datetime
from pathlib import Path

import click

GENKEY_KEYS = ["letters", "bigrams", "trigrams", "skipgrams"]


def create_corpus_json(db_name: str) -> dict:

    con = sqlite3.connect(db_name)
    cur = con.cursor()

    letters = dict(cur.execute("SELECT * FROM unigrams ORDER BY name").fetchall())
    bigrams = dict(cur.execute("SELECT * FROM bigrams ORDER BY name").fetchall())
    trigrams = dict(cur.execute("SELECT * FROM trigrams ORDER BY name").fetchall())
    skipgrams = dict(cur.execute("SELECT * FROM skipgram ORDER BY name").fetchall())
    totalbigrams = len(bigrams)
    total = len(letters)

    con.close()

    data = {
        "letters": letters,
        "bigrams": bigrams,
        "trigrams": trigrams,
        "skipgrams": skipgrams,
        "TotalBigrams": totalbigrams,
        "Total": total,
    }

    return data


def save_to_json(dict) -> None:
    output_dir = Path.cwd() / "data"
    filename = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with open(output_dir / filename, "w") as f:
            f.write(json.dumps(dict))
        click.echo(f"File saved to {output_dir / filename}!")

    except Exception as e:
        raise click.ClickException(f"Error saving to json: {e}")
