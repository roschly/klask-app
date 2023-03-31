from typing import List

import pandas as pd
import streamlit as st

import src.db as db
from .winrate_rating import calc_winrate, num_matches_between_players

STATS = ["Num matches", "WR %", "Most freq result"]


def _most_freq_result(A: str, B: str, df: pd.DataFrame) -> str:
    """Mode of scores"""
    cond1 = (df.winner == A) & (df.loser == B)
    cond2 = (df.winner == B) & (df.loser == A)
    matches = df[cond1 | cond2]
    # TODO: handle more than one mode...?
    if len(matches) == 0:
        return None
    return matches.score.mode()[0]


def _get_individual_stats(player: str, matches: pd.DataFrame) -> pd.DataFrame:
    """stats from a player versus the rest"""
    all_players = db.list_players()
    df = pd.DataFrame(
        columns=STATS,
        index=all_players,
    )
    df["WR %"] = pd.Series(
        {
            opponent: 100 * calc_winrate(player, opponent, matches)
            for opponent in all_players
            if opponent != player
        }
    )

    df["Num matches"] = pd.Series(
        {
            opponent: num_matches_between_players(player, opponent, matches)
            for opponent in all_players
            if opponent != player
        }
    )

    df["Most freq result"] = pd.Series(
        {
            opponent: _most_freq_result(player, opponent, matches)
            for opponent in all_players
            if opponent != player
        }
    )

    return df


def versus_stats_widget(matches: pd.DataFrame) -> None:
    """Versus stats widget"""
    all_players = db.list_players()

    col1, col2, col3 = st.columns([0.5, 0.35, 0.15])
    with col1:
        player = st.selectbox("Player", all_players)
    with col2:
        sort_by = st.selectbox("Sort by", STATS)
    with col3:
        ascending = st.selectbox("Ascending", [False, True])

    stats = _get_individual_stats(player=player, matches=matches)
    st.table(
        stats.sort_values(sort_by, ascending=ascending).style.format(
            {"WR %": "{:.2f}", "Num matches": "{:.0f}"}
        )
    )
