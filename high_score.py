"""High-score persistence for the Glitchy Guesser game.

Scores are stored in ``highscore.json`` next to this module.  All I/O
errors are silently ignored so that a missing or corrupt file never
crashes the game.
"""

import json
import os

_HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.json")


def load_high_score() -> int:
    """Load the all-time high score from disk.

    Returns:
        The stored high score as an integer, or ``0`` if no score file
        exists or the file cannot be read.
    """
    if os.path.exists(_HIGHSCORE_FILE):
        try:
            with open(_HIGHSCORE_FILE, "r") as fh:
                data = json.load(fh)
                return int(data.get("high_score", 0))
        except (json.JSONDecodeError, ValueError, OSError):
            return 0
    return 0


def save_high_score(score: int) -> bool:
    """Persist *score* as the new high score if it exceeds the current one.

    Args:
        score: The candidate score to compare against the stored record.

    Returns:
        ``True`` if the file was updated (new record set), ``False``
        otherwise (score did not beat the existing record or a write
        error occurred).
    """
    current = load_high_score()
    if score > current:
        try:
            with open(_HIGHSCORE_FILE, "w") as fh:
                json.dump({"high_score": score}, fh)
            return True
        except OSError:
            return False
    return False
