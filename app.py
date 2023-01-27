import os
from pathlib import Path
import yaml

import streamlit as st

import src.db as db
from src import widgets
from src.bootstrap import bootstrap

# load config
cfg = yaml.load(Path("config.yaml").read_text(), yaml.FullLoader)

db.MATCH_FOLDER = Path(cfg["match_folder"])

if not db.MATCH_FOLDER.exists():
    db.MATCH_FOLDER.mkdir(parents=True, exist_ok=True)

# in demo mode, bootstrap app with players and matches
if cfg["bootstrap"]:
    bootstrap()


st.header("Klask")
widgets.new_match()

matches = db.list_matches()
if matches:
    widgets.standings(matches)
    widgets.trueskill_evolution(matches)
    widgets.extra_stats(matches)
    widgets.matches_list(matches)
