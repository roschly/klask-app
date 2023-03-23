import os
import pytz
from typing import List, Optional, Protocol, Set
from uuid import uuid1
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from dateutil.parser import parse
import yaml
import jsons


from .match import Match


# Override jsons datetime serializer to use more
# robust dateutil.parser.parse, that accepts a number
# of different formats


def _load_datetime(obj: str):
    return parse(obj).replace(tzinfo=pytz.utc)


jsons.set_deserializer(lambda obj, cls, **_: _load_datetime(obj), datetime)

MATCH_FOLDER: Path = None
PLAYER_FILE: Path = None
HALL_OF_FAME: Path = None


def list_matches() -> List[Match]:
    """Get a list of all previously played matches in chronological order."""
    matches = []
    for file in MATCH_FOLDER.glob("*.json"):
        content = file.read_text()
        matches.append(jsons.loads(content, Match))
    return list(sorted(matches, key=lambda x: x.date))


def list_players() -> List[str]:
    """List all players from file."""
    content = PLAYER_FILE.read_text()
    players = yaml.load(content, yaml.FullLoader)
    return players


def add_match(match: Match) -> None:
    """Add a new match result."""
    new_file = MATCH_FOLDER / f"{uuid1()}.json"
    new_file.write_text(jsons.dumps(match))


def create_match(winner: str, loser: str, score: str, date: datetime = None) -> None:
    """Submit a new match result."""
    assert winner, "specify a non-empty winner"
    assert loser, "specify a non-empty loser"
    assert winner != loser, "specify different winner/loser"
    new_match = Match(winner, loser, score, None)
    new_file = MATCH_FOLDER / (new_match.to_filename_str() + ".json")
    new_file.write_text(jsons.dumps(new_match))
