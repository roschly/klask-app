import random
from pathlib import Path
import jsons

from . import db
from .match import Match


def bootstrap():
    """Bootstrap app with players in a players.yml file and matches."""

    print("Bootstrapping app...")
    N = 50  # number of matches to create

    # create players.yml file
    players = [
        "Captain America",
        "Iron Man",
        "Hulk",
        "Thor",
        "Ant-Man",
        "Blade",
        "Spider-Man",
    ]

    with open(db.PLAYER_FILE, "w+", encoding="utf-8") as f:
        for player in players:
            f.write(f"- {player}\n")

    # create matches
    for i in range(N):
        player1 = random.choice(players)
        player2 = random.choice([p for p in players if p != player1])
        loser_score = random.randint(0, 5)
        # db.create_match(winner=player1, loser=player2, score=f"6-{loser_score}")

        new_match = Match(player1, player2, f"6-{loser_score}", None)
        new_file = db.MATCH_FOLDER / (new_match.to_filename_str() + f"_{i}" + ".json")
        new_file.write_text(jsons.dumps(new_match))
