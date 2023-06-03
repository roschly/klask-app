from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional


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
        # Set to danish UTC+1 as default
        self.date = self.date or datetime.now(timezone(timedelta(hours=1)))

    def to_filename_str(self) -> str:
        """Match info as a filename."""
        s = f"{self.date.strftime('%Y-%m-%d %H-%M-%S')} {self.winner} {self.score} {self.loser}".lower()
        return s.replace(" ", "_")
