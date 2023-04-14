from typing import List

import pandas as pd
import trueskill as ts
import streamlit as st
import numpy as np

from .utils import ts_setup
from ..elo_system import ELOSystem
from .. import db
from .winrate_rating import weighted_average_winrate


ts_setup()


def _get_elo_ratings(matches: List[db.Match]):
    all_winners = {match.winner for match in matches}
    all_losers = {match.loser for match in matches}
    all_players = all_winners | all_losers

    elo_system = ELOSystem(list(all_players))

    for match in matches:
        elo_system.new_match(match.winner, match.loser)

    return elo_system.players


def _get_ratings(matches: List[db.Match], default_rating: float = 25):
    all_winners = {match.winner for match in matches}
    all_losers = {match.loser for match in matches}
    all_players = all_winners | all_losers
    ratings = {player: ts.Rating(default_rating) for player in all_players}

    for match in matches:
        rating1 = ratings[match.winner]
        rating2 = ratings[match.loser]
        new1, new2 = ts.rate_1vs1(rating1, rating2)
        ratings[match.winner] = new1
        ratings[match.loser] = new2

    return ratings


def _championed_player_name(standings: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(db.HALL_OF_FAME)
    df.sort_values(["year", "month"], ascending=[False, False], inplace=True)
    champion = df.iloc[0]["champion"]
    standings.loc[standings["Player"] == champion, "Player"] = champion + " " + "🏆"
    return standings


def _player_streak(streak: str):
    count = int(streak[1:])

    if (streak[0] == "W") & (count > 1):
        return streak + " " + "🔥" * (count - 1)
    return streak


def _get_standings_frame(matches: List[db.Match]) -> pd.DataFrame:
    players = _get_ratings(matches)
    players_elo = _get_elo_ratings(matches)

    player_records = {player: [] for player in players}
    for match in matches:
        player_records[match.winner].append(1)
        player_records[match.loser].append(0)

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
        standings[player]["win_rate"] = 100 * record.count(1) / len(record)

        if len(record) >= 10:
            l10 = record[-10:]
        else:
            l10 = record

        l10w, l10l = l10.count(1), l10.count(0)
        standings[player]["L10"] = f"{l10w}-{l10l}"

        last = record[-1]
        count = 0
        for res in record[::-1]:
            if res == last:
                count += 1
            else:
                break

        if last == 0:
            streak = f"L{count}"
        else:
            streak = f"W{count}"

        standings[player]["Streak"] = streak

    df_matches = pd.DataFrame(matches)
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
                "Streak": _player_streak(standing["Streak"]),
            }
        )
    df = pd.DataFrame(rows)
    df.sort_values("Rating", ascending=False, inplace=True)
    df["Pos"] = np.arange(len(players)) + 1
    df.set_index("Pos", inplace=True)

    return df


def standings(matches: List[db.Match]) -> None:
    """Standings dataframe widget"""
    frame = _get_standings_frame(matches)
    st.subheader("Standings")

    # add emoji to champion name, if hall of fame with previous winner exists
    # use copy to avoid mutating cached dataframe
    if db.HALL_OF_FAME.exists():
        frame = _championed_player_name(frame.copy())

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
