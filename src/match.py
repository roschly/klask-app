from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Match:
    winner: str
    loser: str
    score: str
    date: Optional[datetime] = None
    video: Optional[str] = None

    def __post_init__(self):
        assert self.winner, "specify a non-empty winner"
        assert self.loser, "specify a non-empty loser"
        assert self.winner != self.loser, "specify different winner/loser"
        self.date = self.date or datetime.utcnow()
