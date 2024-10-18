from dataclasses import dataclass, field, fields
from typing import Any

from models.logger import LoggedKey


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

    @classmethod
    def calc_skipgrams(cls, log_1gram: list[LoggedKey]) -> dict[str, float]:
        # Skipgram weight: most recent key is 1/2, next key is 1/4
        # and so on up to the most recent 10 keys
        weight = []
        for i in range(10):
            weight.append(1 / 2 ** (i + 1))

        # List of most recent keypress, most recent as 0 index
        last_chars: list[str] = []

        skipgram: dict[str, float] = {}

        for logged_key in log_1gram:
            # For now, simply skip special keys, and count mistyped key as correct.
            if not logged_key.is_letter:
                continue
            key_name = logged_key.name
            # Go through last_chars, add weight of skipgram
            # `current_key+last_char` to the dict
            for i in range(len(last_chars)):
                try:
                    skipgram[last_chars[i] + key_name] += weight[i]
                except KeyError:
                    skipgram[last_chars[i] + key_name] = weight[i]

            # Add current key to last_chars list, make sure that it's
            # not more than 10
            last_chars.insert(0, key_name)
            if len(last_chars) > 10:
                last_chars = last_chars[:10]

        return skipgram

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
