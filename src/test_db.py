import json
from datetime import datetime
from .db import read_match


def test_match_serialization():
    obj = json.dumps({
        "winner": "Caspar",
        "loser": "Robert",
        "date": datetime.utcnow().isoformat(),
        "score": "6-3"
    })
    assert read_match(obj)
