from typing import List

import pandas as pd
import streamlit as st

from .. import db
from ..elo_system import ELOSystem

pd.options.plotting.backend = "plotly"


def _build_frame(matches: List[db.Match]) -> pd.DataFrame:
    elo_system = ELOSystem([player for player in db.players])
    # p = {player: ts.Rating(25) for player in db.players}
    r = []

    for i, m in enumerate(matches):
        winner, loser = m.winner, m.loser
        elo_system.new_match(winner, loser)
        # p[winner], p[loser] = ts.rate_1vs1(p[winner], p[loser])
        for name in [winner, loser]:
            r.append(
                {
                    "game_number": i,
                    "name": name,
                    "ELO": elo_system.get_elo(name),
                }
            )

    return pd.DataFrame(r)


def elo_evolution(matches: List[db.Match]):
    st.subheader("ELO Evolution")

    frame = _build_frame(matches)
    fig = frame.plot(x="game_number", y="ELO", color="name")
    st.plotly_chart(fig)
