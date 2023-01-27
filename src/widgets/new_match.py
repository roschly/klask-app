import streamlit as st

from src.match import Match
import src.db as db


def new_match():
    list_with_empty = [""] + db.list_players()
    with st.form("add-match-result"):
        st.subheader("Create new match")
        c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.2, 0.2])
        with c1:
            winner = st.selectbox("Winner", list_with_empty)
        with c2:
            loser = st.selectbox("Loser", list_with_empty)
        with c3:
            winner_score = st.selectbox("winner score", [6], disabled=True)
        with c4:
            loser_score = st.text_input("loser score", value="")
        submit = st.form_submit_button("Submit")
        if submit:
            if winner == "" or loser == "":
                st.error("Please select players.")
                return
            if winner == loser:
                st.error("Winner and loser cannot be the same.")
                return
            if loser_score not in [str(i) for i in range(0, 6)]:
                st.error(
                    f"'{loser_score}' is not a valid loser score... it must be in range: 0-5"
                )
                return
            score = f"{winner_score}-{loser_score}"
            db.create_match(winner, loser, score)
            st.success("Match was created")
