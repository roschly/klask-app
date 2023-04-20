from typing import List

import pandas as pd
import streamlit as st

from ..db import Match


def egg_formatter(score: str):
    if score == "6-0":
        return "🥚"
    return score


def tv_formatter(video: str):
    if video:
        return "📺"
    return ""


def matches_list(matches: List[Match]):
    frame = pd.DataFrame(matches)
    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    frame["score"] = frame["score"].apply(egg_formatter)
    frame["video"] = frame["video"].apply(tv_formatter)
    frame = frame.iloc[::-1]
    st.subheader("Matches")
    st.table(frame)
