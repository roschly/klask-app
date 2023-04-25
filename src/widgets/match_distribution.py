from typing import Dict
from itertools import combinations

import pandas as pd
import streamlit as st
import plotly.express as px

import src.db as db
from .winrate_rating import num_matches_between_players


def match_distribution_widget(head2head: Dict[str, Dict[str, int]]) -> None:
    """
    A sorted stacked bar chart of player matches.
    I.e. each stack represents the absolute/relative number of matches against a specific player (regardless of outcome).
    Bars are sorted according to total num of matches played.
    """

    all_players = db.list_players()
    # Example:
    # {Jens: {Martin: 5, Robert: 3, ...}, Martin: {...}}
    # match_dist[p1][p1] set to 0
    match_dist = {p: {p: 0} for p in all_players}

    for p1, p2 in combinations(all_players, 2):
        num_matches = num_matches_between_players(A=p1, B=p2, head2head=head2head)
        # num_matches_between_players(p1, p2) = num_matches_between_players(p2, p1)
        match_dist[p1][p2] = num_matches
        match_dist[p2][p1] = num_matches

    # convert to dataframe
    df = pd.DataFrame(match_dist)

    # sort according to total number of matches
    sorted_index = df.sum().sort_values().index

    scale_check = st.checkbox(
        "Distribution view", value=False, help="Scale with total num matches"
    )
    if scale_check:
        num_matches = df.sum(axis=1).clip(lower=1)
        # Scale to get actual distribution
        for p in all_players:
            df.loc[p] = df.loc[p] / num_matches[p]

    fig = px.bar(df.loc[sorted_index])

    # display as widget
    st.plotly_chart(fig)
