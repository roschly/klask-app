from typing import Any

import pandas as pd
import trueskill as ts

from .widgets.utils import ts_setup
from .widgets.utils.ts_setup import MU
from . import db

ts_setup()


def process_match_data(matches: list[db.Match]) -> dict[str, Any]:
    """Calculate player ratings for all matches and saves match records
    and rating history for each player
    """
    # Players and TrueSkill rating
    players = {player: ts.Rating(MU) for player in db.list_players()}
    # Match results for each player
    player_records = {player: [] for player in players}
    # Player results against every other player
    head2head = {
        player: {
            opponent: 0 for opponent in set(players.keys()).symmetric_difference(player)
        }
        for player in players
    }

    rating_history = []

    for i, m in enumerate(matches):
        winner, loser = m.winner, m.loser

        head2head[winner][loser] += 1

        # Update match records
        player_records[winner].append(1)
        player_records[loser].append(0)

        # Update ratings
        players[winner], players[loser] = ts.rate_1vs1(players[winner], players[loser])

        # Update rating history
        for name in [winner, loser]:
            rating_history.append(
                {
                    "game_number": i,
                    "name": name,
                    "rating": players[name].mu,
                }
            )

    return {
        "players": players,
        "records": player_records,
        "ratings_history": pd.DataFrame(rating_history),
        "h2h": head2head,
    }
