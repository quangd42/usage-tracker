import json
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol


class CorpusDict(Protocol):
    def to_corpora_dict(self) -> dict[str, Any]: ...


def save_to_json(data: CorpusDict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f'{datetime.now().strftime('%Y%m%d_%H%M%S')}.json'
    output_file = output_dir / filename

    try:
        with open(output_file, 'w') as f:
            f.write(json.dumps(data.to_corpora_dict()))
        return output_file

    except Exception as e:
        raise Exception(f'Error saving to json: {e}')
