from typing import List
import matplotlib.pyplot as plt

import seaborn as sns
import pandas as pd
import streamlit as st
import trueskill as ts

from .utils import ts_setup
import src.db as db

pd.options.plotting.backend = "plotly"
ts_setup()

MU = 25


def _build_frame(matches: List[db.Match]) -> pd.DataFrame:
    p = {player: ts.Rating(MU) for player in db.list_players()}
    r = []

    for i, m in enumerate(matches):
        winner, loser = m.winner, m.loser
        p[winner], p[loser] = ts.rate_1vs1(p[winner], p[loser])
        for name in [winner, loser]:
            r.append(
                {
                    "game_number": i,
                    "name": name,
                    "rating": p[name].mu,
                }
            )

    return pd.DataFrame(r)


def trueskill_evolution(matches: List[db.Match]) -> None:
    st.subheader("Trueskill Evolution")

    frame = _build_frame(matches)
    fig = frame.plot(x="game_number", y="rating", color="name")
    st.plotly_chart(fig)
