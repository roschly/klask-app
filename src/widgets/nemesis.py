from typing import List, Tuple

import pandas as pd
import pydot
import streamlit as st
import matplotlib

from ..db import Match
import src.db as db
from .winrate_rating import calc_winrate, num_matches_between_players
from .standings import _get_standings_frame
from .trueskill_evolution import MU


def _find_dominators(
    player: str,
    all_players: List[str],
    matches: pd.DataFrame,
) -> List[str]:
    """Find the list of players that dominate this player."""
    # list of opponents and winrate against them
    wrs = [
        (opponent, calc_winrate(player, opponent, matches))
        for opponent in all_players
        if opponent != player
    ]
    # only keep valid dominance winrates, i.e. <= 0.25 and at least 3 matches
    dominators = [
        p
        for (p, wr) in wrs
        if wr <= 0.25 and num_matches_between_players(player, p, matches) >= 3
    ]
    return dominators


def _find_nemeses(
    player: str,
    all_players: List[str],
    matches: pd.DataFrame,
) -> List[str]:
    """Find the list of possible nemeses of the player.
    A nemeses is the one(s) that the player has the lowest winrate against,
    provided it is lower than 50 % and at least 3 matches have been played.
    """
    # list of opponents and winrate against them
    wrs = [
        (opponent, calc_winrate(player, opponent, matches))
        for opponent in all_players
        if opponent != player
    ]
    # only keep valid nemesis winrates, i.e. < 0.5 and at least 3 matches
    wrs = [
        (p, wr)
        for (p, wr) in wrs
        if wr < 0.5 and num_matches_between_players(player, p, matches) >= 3
    ]
    # if no opponents meet the criteria, return empty list
    if wrs == []:
        return []
    # nemeses are the ones the player has the lowest winrate against
    min_wr = min(wrs, key=lambda x: x[1])[1]
    nemeses = [p for (p, wr) in wrs if wr == min_wr]
    return nemeses


@st.cache
def nemesis_plot(df_matches: pd.DataFrame, matches: List[Match]) -> pydot.Dot:
    """Graphviz DOT graph of player nemeses."""

    dot = pydot.Dot()
    standings = _get_standings_frame(matches)

    all_players = db.list_players()
    for player in all_players:
        if player not in standings["Player"].values:
            rating = MU
        else:
            rating = standings[standings["Player"] == player]["Rating"].values[0]

        # cap rating between Lower and Upper values, e.g. 15 and 35
        # convert to range [0;1] for color map
        L, U = 15, 35  # 15 and 35 ensures 25 (default rating) corresponds to 0.5
        r = min(max(0, rating - L), U - L) / (U - L)
        # use capped and converted rating as color map percentage
        cmap = matplotlib.cm.get_cmap("coolwarm")
        hex_color = matplotlib.colors.rgb2hex(cmap(r))

        dot.add_node(
            pydot.Node(
                name=player,
                style="filled",
                color=hex_color,
            )
        )

    for player in all_players:
        nemeses = set(_find_nemeses(player, all_players, df_matches))
        dominators = set(_find_dominators(player, all_players, df_matches))
        both = nemeses.intersection(dominators)

        for p in nemeses.union(dominators):
            # domination is the default edge style
            color = "red"
            style = "dashed"
            # if opponent p is both a dominator and a nemesis
            if p in both:
                color = "purple"
                style = "solid"
            # if p is only a nemesis
            elif p in nemeses - both:
                color = "blue"
            winrate = calc_winrate(player, p, df_matches)
            edge = pydot.Edge(
                pydot.Node(name=p),
                pydot.Node(name=player),
                style=style,
                # scale width of arrow with winrate
                # min width is set to 0.5 in order to be visible
                penwidth=max(5 * (winrate - 0.5), 0.5),
                tooltip="{:.2f}".format(winrate),
                color=color,
            )
            dot.add_edge(edge)
    return dot
