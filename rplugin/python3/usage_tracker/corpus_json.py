import json
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

import click


class CorpusDict(Protocol):
    def to_corpora_dict(self) -> dict[str, Any]: ...


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
