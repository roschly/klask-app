from typing import List
from pathlib import Path

import streamlit as st
import pandas as pd

from .. import db
from .nemesis import nemesis_plot
from .versus_stats import versus_stats_widget
from .match_distribution import match_distribution_widget


def extra_stats(matches: List[db.Match]) -> None:
    """Section that adds expandable extra stats"""

    df_matches = pd.DataFrame(matches)
    dot = nemesis_plot(df_matches, matches)

    st.subheader("Extra stats")

    # match distribution
    with st.expander("Match distribution"):
        match_distribution_widget(df_matches)

    with st.expander("Nemesis and domination plot"):
        st.write(
            "A is a nemesis of B (A --> B), if A has the highest winrate over B (and at least > 50%) AND they have played 3 or more matches. More than one nemesis is possible."
        )
        st.write(
            "A is dominating B if A has won at least 3/4 of matches between A and B or, if B has won no matches against A, has won at least 3 matches."
        )
        st.write(
            "Legend: blue dashed == nemesis, red dashed == domination, purple solid == nemesis AND domination."
        )
        st.graphviz_chart(dot.to_string())

    # versus stats
    with st.expander("Versus stats"):
        versus_stats_widget(df_matches)

    # hall of fame
    if db.HALL_OF_FAME.exists():
        with st.expander("Hall of Fame"):
            df = pd.read_csv(db.HALL_OF_FAME)
            df.sort_values(["year", "month"], ascending=[False, False], inplace=True)
            st.table(df)
