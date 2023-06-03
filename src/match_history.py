from typing import Any, List, Dict
from dataclasses import dataclass

import pandas as pd
import trueskill as ts

from .widgets.utils import ts_setup
from .widgets.utils.ts_setup import MU
from . import db

ts_setup()

# type alias
Player = str


@dataclass
class MatchHistory:
    ts_ratings: Dict[Player, float] = None
    win_loss_records: Dict[Player, int] = None
    head2head: Dict[Player, Dict[Player, int]] = None
    ts_ratings_history: pd.DataFrame = None

    def __post_init__(self):
        players = db.list_players()
        self.ts_ratings = {player: ts.Rating(MU) for player in players}
        self.win_loss_records = {player: [] for player in players}
        self.head2head = {
            player: {opponent: 0 for opponent in players if opponent != player}
            for player in players
        }


def create_match_history(matches: List[db.Match]) -> Dict[str, Any]:
    """Create the match history based on all played matches, containing:
    - trueskill ratings
    - win_loss_records
    - head2head stats
    - trueskill ratings_history
    """
    mh = MatchHistory()
    ts_ratings_history = []

    for i, m in enumerate(matches):
        winner, loser = m.winner, m.loser

        # update head to head
        mh.head2head[winner][loser] += 1

        # update win loss records of both winner and loser
        mh.win_loss_records[winner].append(1)
        mh.win_loss_records[loser].append(0)

        # calculate new trueskill ratings for winner and loser
        mh.ts_ratings[winner], mh.ts_ratings[loser] = ts.rate_1vs1(
            mh.ts_ratings[winner], mh.ts_ratings[loser]
        )
        # Update rating history
        for name in [winner, loser]:
            ts_ratings_history.append(
                {
                    "game_number": i,
                    "name": name,
                    "rating": mh.ts_ratings[name].mu,
                }
            )

    mh.ts_ratings_history = pd.DataFrame(ts_ratings_history)
    return mh
