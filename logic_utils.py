"""Core game-logic utilities for the Glitchy Guesser number-guessing game.

All functions here are pure (no I/O, no Streamlit imports) so they can be
imported and tested independently of the UI layer.
"""


def get_range_for_difficulty(difficulty: str):
    """Return the (low, high) inclusive integer range for a given difficulty.

    Args:
        difficulty: Difficulty level string.  Accepted values are ``"Easy"``,
            ``"Normal"``, and ``"Hard"``.  Any unrecognised value falls back
            to the Normal range.

    Returns:
        A 2-tuple ``(low, high)`` of integers representing the inclusive
        lower and upper bounds of the secret number pool.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Normal")
        (1, 100)
        >>> get_range_for_difficulty("Hard")
        (1, 200)
        >>> get_range_for_difficulty("unknown")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        # FIX: was incorrectly set to (1, 50), which is easier than Normal
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Accepts plain integers and decimal strings (decimals are truncated toward
    zero, not rounded).  Rejects empty, ``None``, or non-numeric input.

    Args:
        raw: The raw string entered by the player, e.g. ``"42"`` or
            ``"3.7"``.  Pass ``None`` to represent a missing value.

    Returns:
        A 3-tuple ``(ok, guess_int, error_message)`` where:

        - ``ok`` (``bool``) - ``True`` if parsing succeeded.
        - ``guess_int`` (``int | None``) - The parsed integer when *ok* is
          ``True``; ``None`` otherwise.
        - ``error_message`` (``str | None``) - A human-readable error string
          when *ok* is ``False``; ``None`` otherwise.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("3.7")
        (True, 3, None)
        >>> parse_guess("")
        (False, None, 'Enter a guess.')
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a player's guess to the secret number and return feedback.

    Args:
        guess: The player's integer guess.
        secret: The secret integer the player is trying to find.

    Returns:
        A 2-tuple ``(outcome, message)`` where:

        - ``outcome`` (``str``) - One of ``"Win"``, ``"Too High"``, or
          ``"Too Low"``.
        - ``message`` (``str``) - A human-readable feedback string suitable
          for display in the UI.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(40, 50)
        ('Too Low', '📈 Go HIGHER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: hints were inverted - "Go HIGHER!" was shown when guess was too
    # high, and "Go LOWER!" when guess was too low.  Swapped to correct logic.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Calculate a new score after a guess.

    Winning earlier yields more points (capped at a minimum of 10 so very
    late wins still reward the player).  Wrong guesses always deduct 5 points.

    Args:
        current_score: The player's score before this guess.
        outcome: Result string from :func:`check_guess` - one of ``"Win"``,
            ``"Too High"``, or ``"Too Low"``.
        attempt_number: 1-based attempt index used to scale the win bonus.
            Formula: ``100 - 10 * (attempt_number + 1)``, minimum 10.

    Returns:
        The updated integer score after applying the outcome.

    Examples:
        >>> update_score(0, "Win", 1)
        80
        >>> update_score(100, "Too High", 2)
        95
        >>> update_score(0, "Too Low", 5)
        -5
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: was rewarding +5 points on even attempts for wrong "Too High"
    # guesses.  Wrong guesses should always deduct points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


def get_hot_cold_label(distance: int, total_range: int) -> str:
    """Return a Hot/Cold proximity label based on how close a guess is.

    The label is derived from the ratio of *distance* to *total_range*,
    giving a consistent experience across all difficulty levels regardless
    of the absolute size of the number pool.

    Args:
        distance: Absolute difference between the player's guess and the
            secret number (i.e. ``abs(guess - secret)``).
        total_range: The full span of the game's number pool
            (``high - low``).  Must be a positive integer; if zero or
            negative the function returns the hottest label.

    Returns:
        One of five emoji-labelled strings indicating proximity:

        - ``"🔥 Burning Hot!"`` – within 5 % of the range
        - ``"♨️ Hot"``          – within 20 % of the range
        - ``"😐 Warm"``         – within 40 % of the range
        - ``"❄️ Cold"``         – within 60 % of the range
        - ``"🧊 Ice Cold!"``    – more than 60 % away

    Examples:
        >>> get_hot_cold_label(1, 100)
        '🔥 Burning Hot!'
        >>> get_hot_cold_label(15, 100)
        '♨️ Hot'
        >>> get_hot_cold_label(50, 100)
        '❄️ Cold'
        >>> get_hot_cold_label(80, 100)
        '🧊 Ice Cold!'
    """
    if total_range <= 0:
        return "🔥 Burning Hot!"
    ratio = distance / total_range
    if ratio < 0.05:
        return "🔥 Burning Hot!"
    if ratio < 0.20:
        return "♨️ Hot"
    if ratio < 0.40:
        return "😐 Warm"
    if ratio < 0.60:
        return "❄️ Cold"
    return "🧊 Ice Cold!"
