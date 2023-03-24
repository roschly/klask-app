import os
from pathlib import Path
import yaml

import streamlit as st

import src.db as db
from src import widgets
from src.bootstrap import bootstrap


def main():
    st.header("Klask")

    # load config
    cfg = yaml.load(Path("config.yaml").read_text(), yaml.FullLoader)

    db.MATCH_FOLDER = Path(cfg["match_folder"])
    db.PLAYER_FILE = Path(cfg["players"])
    db.HALL_OF_FAME = Path(cfg["hall_of_fame"])

    # if no players and no matches: bootstrap
    if not db.PLAYER_FILE.exists() and (
        not db.MATCH_FOLDER.exists() or len(list(db.MATCH_FOLDER.iterdir())) == 0
    ):
        if not db.MATCH_FOLDER.exists():
            db.MATCH_FOLDER.mkdir(parents=True)
        bootstrap()

    # if no players, but matches: error
    elif not db.PLAYER_FILE.exists() and len(list(db.MATCH_FOLDER.iterdir())) > 0:
        st.error(
            f"Found no players file at '{db.PLAYER_FILE}', but found existing matches in '{db.MATCH_FOLDER}'. Either add players.yml matching those in matches or remove matches."
        )
        return

    # if players, but no matches: do nothing
    # if players and matches: do nothing
    if not db.MATCH_FOLDER.exists():
        db.MATCH_FOLDER.mkdir(parents=True)

    widgets.new_match()

    matches = db.list_matches()
    if matches:
        widgets.standings(matches)
        widgets.trueskill_evolution(matches)
        widgets.extra_stats(matches)
        widgets.matches_list(matches)


if __name__ == "__main__":
    main()
