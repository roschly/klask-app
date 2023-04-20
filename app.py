from pathlib import Path
import yaml

import streamlit as st

import src.db as db
from src import widgets
from src.bootstrap import bootstrap
from src.process_match_data import process_match_data


def main():
    st.header("Klask")

    # load config
    cfg = yaml.load(Path("config.yaml").read_text(), yaml.FullLoader)

    db.MATCH_FOLDER = Path(cfg["match_folder"])
    db.PLAYER_FILE = Path(cfg["players"])
    db.HALL_OF_FAME = Path(cfg["hall_of_fame"])

    do_bootstrap = False
    # if no player file and no matches folder exist, bootstrap
    if not db.PLAYER_FILE.exists() and not db.MATCH_FOLDER.exists():
        do_bootstrap = True

    # create player file and matches folder if they dont exist
    if not db.PLAYER_FILE.exists():
        db.PLAYER_FILE.parent.mkdir(parents=True, exist_ok=True)
        db.PLAYER_FILE.touch()
    if not db.MATCH_FOLDER.exists():
        db.MATCH_FOLDER.mkdir(parents=True)

    # perfom the actual bootstrapping after folder and file creation
    if do_bootstrap:
        bootstrap()

    widgets.new_match()

    matches = db.list_matches()
    history = process_match_data(matches)

    if matches:
        widgets.standings(history["players"], history["records"])
        widgets.trueskill_evolution(matches)
        widgets.extra_stats(matches)
        widgets.matches_list(matches)


if __name__ == "__main__":
    main()
