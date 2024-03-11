import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import click


@dataclass
class GenkeyData:
    letters: dict[str, int]
    bigrams: dict[str, int]
    trigrams: dict[str, int]
    skipgram: dict[str, float]
    TotalBigrams: int  # Capitalized because genkey corpus wants that...
    Total: int


def create_corpus_json(db_name: str) -> dict:

    con = sqlite3.connect(db_name)
    cur = con.cursor()

    letters = dict(cur.execute("SELECT * FROM t1gram ORDER BY name").fetchall())
    bigrams = dict(cur.execute("SELECT * FROM t2gram ORDER BY name").fetchall())
    trigrams = dict(cur.execute("SELECT * FROM t3gram ORDER BY name").fetchall())
    skipgrams = dict(cur.execute("SELECT * FROM skipgram ORDER BY name").fetchall())
    totalbigrams = len(bigrams)
    total = len(letters)

    con.close()

    data = GenkeyData(letters, bigrams, trigrams, skipgrams, totalbigrams, total)

    return asdict(data)


def save_to_json(dict) -> None:
    output_dir = Path.cwd() / "data"
    filename = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with open(output_dir / filename, "w") as f:
            f.write(json.dumps(dict))
        click.echo(f"File saved to {output_dir / filename}!")

    except Exception as e:
        raise click.ClickException(f"Error saving to json: {e}")
