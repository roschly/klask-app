import random
from pathlib import Path

from . import db
from .match import Match


def bootstrap():
    """Bootstrap app with players in a players.yml file and matches."""

    print("Bootstrapping app...")
    N = 50  # number of matches to create

    # create players.yml file
    players = [
        "Asger A",
        "Asger O",
        "Caspar",
        "Jens",
        "Lasse",
        "Mads",
        "Martin",
        "Robert",
        "Soeren",
    ]

    with open(db.PLAYER_FILE, "w+", encoding="utf-8") as f:
        for player in players:
            f.write(f"- {player}\n")

    # create matches
    for _ in range(N):
        player1 = random.choice(players)
        player2 = random.choice([p for p in players if p != player1])
        loser_score = random.randint(0, 5)
        db.add_match(Match(player1, player2, f"6-{loser_score}"))
