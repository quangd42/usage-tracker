import json
import sqlite3
from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

import click


class CorpusDict(Protocol):
    def to_corpora_dict(self) -> dict[str, Any]: ...


@dataclass
class GenkeyOutput:
    letters: dict[str, int]
    bigrams: dict[str, int]
    trigrams: dict[str, int]
    skipgrams: dict[str, float]
    top_trigrams: list = field(init=False)
    total_bigrams: int = field(init=False)
    total: int = field(init=False)

    def __post_init__(self) -> None:
        self.top_trigrams = [{'Ngram': k, 'Count': v} for k, v in self.trigrams.items()]
        self.top_trigrams = sorted(
            self.top_trigrams, key=lambda trigram: trigram['Count'], reverse=True
        )

        self.total_bigrams = len(self.bigrams)
        self.total = len(self.letters)

    @classmethod
    def list_keys(cls) -> list[str]:
        return [field.name for field in fields(cls) if field.init]

    def to_corpora_dict(self) -> dict[str, Any]:
        return {
            'letters': self.letters,
            'bigrams': self.bigrams,
            'trigrams': self.trigrams,
            'skipgrams': self.skipgrams,
            'TopTrigrams': self.top_trigrams,
            'TotalBigrams': self.total_bigrams,
            'Total': self.total,
        }


def create_genkey_json(db_name: str, session_name: str) -> GenkeyOutput:
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    letters = cur.execute(
        'SELECT name, freq FROM letters WHERE session = ? ORDER BY name',
        (session_name,),
    ).fetchall()
    bigrams = cur.execute(
        'SELECT name, freq FROM bigrams WHERE session = ? ORDER BY name',
        (session_name,),
    ).fetchall()
    trigrams = cur.execute(
        'SELECT name, freq FROM trigrams WHERE session = ? ORDER BY name',
        (session_name,),
    ).fetchall()
    skipgrams = cur.execute(
        'SELECT name, weight FROM skipgrams WHERE session = ? ORDER BY name',
        (session_name,),
    ).fetchall()

    con.close()

    return GenkeyOutput(dict(letters), dict(bigrams), dict(trigrams), dict(skipgrams))


def save_to_json(data: CorpusDict) -> None:
    output_dir = Path.cwd() / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f'{datetime.now().strftime('%Y%m%d_%H%M%S')}.json'

    try:
        with open(output_dir / filename, 'w') as f:
            f.write(json.dumps(data.to_corpora_dict()))
        click.echo(f'File saved to {output_dir / filename}!')

    except Exception as e:
        raise click.ClickException(f'Error saving to json: {e}')
