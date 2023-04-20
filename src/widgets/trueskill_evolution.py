import pandas as pd
import streamlit as st

pd.options.plotting.backend = "plotly"


def trueskill_evolution(ratings_history: pd.DataFrame) -> None:
    st.subheader("Trueskill Evolution")

    fig = ratings_history.plot(x="game_number", y="rating", color="name")
    st.plotly_chart(fig)
