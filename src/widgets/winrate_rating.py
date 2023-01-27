import pandas as pd
from statistics import median

import src.db as db


def get_all_players(df: pd.DataFrame, has_played_only: bool = False):
    """Get all registered players or all who has played so far."""

    if has_played_only:
        return set(df.winner.unique()) | set(df.loser.unique())
    else:
        return set(db.list_players())


def calc_winrate(A: str, B: str, df: pd.DataFrame) -> float:
    """A's winrate over B.

    If A and B haven't played any matches, make very conservative assumption:
        A's winrate over B = 0

    NOTE: this encourages players to always play against new opponents,
    since their winrate can only remain the same or improve.
    """
    # A as winner
    a_wins = len(df[(df.winner == A) & (df.loser == B)])

    # B as winner
    b_wins = len(df[(df.winner == B) & (df.loser == A)])

    total_matches = a_wins + b_wins
    if total_matches == 0:
        return 0.5
    return a_wins / total_matches


def median_player_matches(player: str, df: pd.DataFrame) -> int:
    """The median number of matches between player and all opponents."""
    all_players = get_all_players(df, has_played_only=False)
    other_players = all_players.symmetric_difference(set([player]))

    num_matches_per_player = [
        num_matches_between_players(player, p, df) for p in other_players
    ]
    return median(num_matches_per_player)


def num_matches_between_players(A: str, B: str, df: pd.DataFrame) -> int:
    """How many matches have two players played."""
    cond1 = (df.winner == A) & (df.loser == B)
    cond2 = (df.winner == B) & (df.loser == A)
    matches = df[cond1 | cond2]
    return len(matches)


def winrate_certainty(player: str, opponent: str, df: pd.DataFrame) -> float:
    """Don't trust a winrate over an opponent that is based on too few matches.

    If the number of matches between player and opponent is below
    the median of number of matches between opponent and other players,
    assign less certainty to winrate result.
    """
    # cap median at 1, to avoid zero divsion in ratio
    capped_median_player_matches = max(1, median_player_matches(opponent, df))
    median_match_ratio = (
        num_matches_between_players(player, opponent, df) / capped_median_player_matches
    )

    # ensure certainty is at or below 1.0
    # no reward for playing more than median number of matches
    return min(1.0, median_match_ratio)


def weighted_average_winrate(player: str, df: pd.DataFrame) -> float:
    """The weighted average winrate of a player over all other players.

    The winrate over an opponent is weighted by a winrate certainty,
    dependent on the number of matches between player and opponent compared to other players.
    """
    all_players = get_all_players(df, has_played_only=False)
    other_players = all_players.symmetric_difference(set([player]))

    winrates = [
        calc_winrate(player, p, df) * winrate_certainty(player, p, df)
        for p in other_players
    ]

    return sum(winrates) / len(winrates)
