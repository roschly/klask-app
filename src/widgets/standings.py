from typing import List, Dict
from itertools import takewhile

import pandas as pd
import trueskill as ts
import streamlit as st
import numpy as np

from .utils import ts_setup
from ..elo_system import ELOSystem
from .. import db

# from .winrate_rating import weighted_average_winrate


ts_setup()


def _get_elo_ratings(matches: List[db.Match]):
    all_winners = {match.winner for match in matches}
    all_losers = {match.loser for match in matches}
    all_players = all_winners | all_losers

    elo_system = ELOSystem(list(all_players))

    for match in matches:
        elo_system.new_match(match.winner, match.loser)

    return elo_system.players


def _championed_player_name(standings: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(db.HALL_OF_FAME)
    df.sort_values(["year", "month"], ascending=[False, False], inplace=True)
    champion = df.iloc[0]["champion"]
    standings.loc[standings["Player"] == champion, "Player"] = champion + " " + "🏆"
    return standings


def _player_streak(streak_len: int, res: str):
    if res is None:
        return "-"
    streak = res + str(streak_len)

    if res == "W":
        streak += " " + "🔥" * (streak_len - 1)

    return streak


def _get_standings_frame(
    players: Dict[str, ts.Rating], player_records: Dict[str, List[int]]
) -> pd.DataFrame:
    standings = {
        player: {
            "Player": player,
            "Rating": players[player].mu,
            "TrueSkill_LC": players[player].mu - players[player].sigma,
        }
        for player in players
    }

    for player, record in player_records.items():
        standings[player]["W"] = record.count(1)
        standings[player]["L"] = record.count(0)

        if len(record) == 0:
            standings[player]["win_rate"] = 0
        else:
            standings[player]["win_rate"] = 100 * record.count(1) / len(record)

        if len(record) >= 10:
            l10 = record[-10:]
        else:
            l10 = record

        l10_wins, l10_losses = l10.count(1), l10.count(0)
        standings[player]["L10"] = f"{l10_wins}-{l10_losses}"

        # Get current win or loss streak for player
        streak_len = sum(1 for _ in takewhile(lambda x: x == record[-1], record[::-1]))
        if len(record) > 0:
            res = "L" if record[-1] == 0 else "W"
        else:
            res = None

        standings[player]["Streak"] = _player_streak(streak_len, res)

    rows = []
    for player, standing in standings.items():
        rows.append(
            {
                "Pos": 0,
                "Player": player,
                "W": standing["W"],
                "L": standing["L"],
                "WR %": round(standing["win_rate"], 2),
                # "WAWR %": round(weighted_average_winrate(player, df_matches) * 100, 2),
                # "ELO": round(players_elo[player]["elo"]),
                "Rating": round(standing["Rating"], 2),
                # "TrueSkillLB": round(standing["TrueSkill_LC"], 2),
                "L10": standing["L10"],
                "Streak": standing["Streak"],
            }
        )
    df = pd.DataFrame(rows)
    df.sort_values("Rating", ascending=False, inplace=True)
    df["Pos"] = np.arange(len(players)) + 1
    df.set_index("Pos", inplace=True)
    return df


def standings(
    players: Dict[str, ts.Rating], player_records: Dict[str, List[int]]
) -> None:
    """Standings dataframe widget"""
    frame = _get_standings_frame(players, player_records)

    # add emoji to champion name, if hall of fame with previous winner exists
    # use copy to avoid mutating cached dataframe
    if db.HALL_OF_FAME.exists():
        frame = _championed_player_name(frame.copy())

    st.subheader("Standings")

    # only show players that have played so far
    frame = frame[frame["W"] + frame["L"] > 0]

    st.table(
        frame.style.format(
            {
                "WR %": "{:.2f}",
                "WAWR %": "{:.2f}",
                "Rating": "{:.2f}",
                "TrueSkillLB": "{:.2f}",
            }
        )
    )
