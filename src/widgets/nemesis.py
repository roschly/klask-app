from typing import List, Dict, Tuple

import pydot
import matplotlib
from trueskill import Rating

from .winrate_rating import calc_winrate, num_matches_between_players


def _find_dominators(
    player: str,
    winrates: List[Tuple[str, float]],
    head2head: Dict[str, Dict[str, int]],
) -> List[str]:
    """Find the list of players that dominate this player."""
    # only keep valid dominance winrates, i.e. <= 0.25 and at least 3 matches
    dominators = [
        p
        for (p, wr) in winrates
        if wr <= 0.25 and num_matches_between_players(player, p, head2head) >= 3
    ]
    return dominators


def _find_nemeses(
    player: str,
    winrates: List[Tuple[str, float]],
    head2head: Dict[str, Dict[str, int]],
) -> List[str]:
    """Find the list of possible nemeses of the player.
    A nemeses is the one(s) that the player has the lowest winrate against,
    provided it is lower than 50 % and at least 3 matches have been played.
    """
    # only keep valid nemesis winrates, i.e. < 0.5 and at least 3 matches
    wrs = [
        (p, wr)
        for (p, wr) in winrates
        if wr < 0.5 and num_matches_between_players(player, p, head2head) >= 3
    ]
    # if no opponents meet the criteria, return empty list
    if wrs == []:
        return []
    # nemeses are the ones the player has the lowest winrate against
    min_wr = min(wrs, key=lambda x: x[1])[1]
    nemeses = [p for (p, wr) in wrs if wr == min_wr]
    return nemeses


def nemesis_plot(
    head2head: Dict[str, Dict[str, int]], player_ratings: Dict[str, Rating]
) -> pydot.Dot:
    """Graphviz DOT graph of player nemeses."""

    dot = pydot.Dot()

    for player, ts in player_ratings.items():
        rating = ts.mu

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

    players = player_ratings.keys()
    for player in players:
        winrates = [
            (opponent, calc_winrate(player, opponent, head2head))
            for opponent in players
            if opponent != player
        ]

        nemeses = set(_find_nemeses(player, winrates, head2head))
        dominators = set(_find_dominators(player, winrates, head2head))
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
            winrate = calc_winrate(player, p, head2head)
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
