from dataclasses import dataclass, field, fields
from typing import Any


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
