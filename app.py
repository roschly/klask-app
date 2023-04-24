from pathlib import Path
import yaml

import streamlit as st

import src.db as db
from src import widgets
from src.bootstrap import bootstrap
from src.match_history import create_match_history


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
    match_history = create_match_history(matches)

    if matches:
        widgets.standings(match_history.ts_ratings, match_history.win_loss_records)
        widgets.trueskill_evolution(match_history.ts_ratings_history)
        widgets.extra_stats(match_history.head2head, match_history.ts_ratings)
        widgets.matches_list(matches)


if __name__ == "__main__":
    main()
