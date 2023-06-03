from typing import Dict
from statistics import median

import pandas as pd

import src.db as db


def get_all_players(df: pd.DataFrame, has_played_only: bool = False):
    """Get all registered players or all who has played so far."""

    if has_played_only:
        return set(df.winner.unique()) | set(df.loser.unique())
    else:
        return set(db.list_players())


def calc_winrate(A: str, B: str, head2head: Dict[str, Dict[str, int]]) -> float:
    """A's winrate over B.

    If A and B haven't played any matches, make very conservative assumption:
        A's winrate over B = 0

    NOTE: this encourages players to always play against new opponents,
    since their winrate can only remain the same or improve.
    """
    total_matches = head2head[A][B] + head2head[B][A]
    if total_matches == 0:
        return 0.5
    return head2head[A][B] / total_matches


def median_player_matches(player: str, head2head: Dict[str, Dict[str, int]]) -> int:
    """The median number of matches between player and all opponents."""
    all_players = db.list_players()
    other_players = all_players.symmetric_difference(set([player]))

    num_matches_per_player = [
        num_matches_between_players(player, p, head2head) for p in other_players
    ]
    return median(num_matches_per_player)


def num_matches_between_players(
    A: str, B: str, head2head: Dict[str, Dict[str, int]]
) -> int:
    """How many matches have two players played."""
    return head2head[A][B] + head2head[B][A]


def winrate_certainty(
    player: str, opponent: str, head2head: Dict[str, Dict[str, int]]
) -> float:
    """Don't trust a winrate over an opponent that is based on too few matches.

    If the number of matches between player and opponent is below
    the median of number of matches between opponent and other players,
    assign less certainty to winrate result.
    """
    # cap median at 1, to avoid zero divsion in ratio
    capped_median_player_matches = max(1, median_player_matches(opponent, head2head))
    median_match_ratio = (
        num_matches_between_players(player, opponent, head2head)
        / capped_median_player_matches
    )

    # ensure certainty is at or below 1.0
    # no reward for playing more than median number of matches
    return min(1.0, median_match_ratio)


def weighted_average_winrate(
    player: str, head2head: Dict[str, Dict[str, int]]
) -> float:
    """The weighted average winrate of a player over all other players.

    The winrate over an opponent is weighted by a winrate certainty,
    dependent on the number of matches between player and opponent compared to other players.
    """
    all_players = db.list_players()
    other_players = all_players.symmetric_difference(set([player]))

    winrates = [
        calc_winrate(player, p, head2head) * winrate_certainty(player, p, head2head)
        for p in other_players
    ]

    return sum(winrates) / len(winrates)
