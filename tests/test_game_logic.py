from logic_utils import check_guess, update_score, parse_guess, get_hot_cold_label


# ---------------------------------------------------------------------------
# Original tests (Phase 2)
# ---------------------------------------------------------------------------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result[0] == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, outcome should be "Too High"
    result = check_guess(60, 50)
    assert result[0] == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, outcome should be "Too Low"
    result = check_guess(40, 50)
    assert result[0] == "Too Low"


def test_hint_too_high_says_go_lower():
    # FIX verification: when guess is too high, hint must say go lower
    _, message = check_guess(60, 50)
    assert "LOWER" in message.upper()


def test_hint_too_low_says_go_higher():
    # FIX verification: when guess is too low, hint must say go higher
    _, message = check_guess(40, 50)
    assert "HIGHER" in message.upper()


def test_update_score_wrong_guess_always_subtracts():
    # FIX verification: wrong guesses should always subtract points,
    # never add them (the bug gave +5 on even attempts for "Too High")
    score_after_even = update_score(100, "Too High", 2)
    score_after_odd = update_score(100, "Too High", 3)
    assert score_after_even == 95
    assert score_after_odd == 95


def test_update_score_win():
    # Winning on attempt 1 should give 100 - 10*(1+1) = 80 points
    result = update_score(0, "Win", 1)
    assert result == 80


# ---------------------------------------------------------------------------
# Challenge 1: Edge-case tests
# ---------------------------------------------------------------------------

# --- parse_guess edge cases ---

def test_parse_guess_negative_number():
    """Negative number strings should parse to negative ints successfully."""
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5
    assert err is None


def test_parse_guess_decimal_truncates_not_rounds():
    """Decimal input should truncate toward zero, not round.

    "7.9" becomes 7, not 8, because int(float("7.9")) truncates.
    This is a documented edge-case: players entering decimals get the
    floor value, which may surprise them.
    """
    ok, value, err = parse_guess("7.9")
    assert ok is True
    assert value == 7  # truncated, NOT rounded to 8


def test_parse_guess_negative_decimal_truncates():
    """Negative decimals also truncate toward zero."""
    ok, value, err = parse_guess("-3.7")
    assert ok is True
    assert value == -3  # int(float("-3.7")) == -3


def test_parse_guess_extremely_large_number():
    """Very large integers should parse without error."""
    ok, value, err = parse_guess("999999999999")
    assert ok is True
    assert value == 999999999999


def test_parse_guess_whitespace_only():
    """Whitespace-only input is not a valid guess (no strip in parse_guess)."""
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert value is None


def test_parse_guess_zero():
    """Zero is a valid integer input."""
    ok, value, err = parse_guess("0")
    assert ok is True
    assert value == 0


# --- check_guess edge cases ---

def test_check_guess_negative_guess_is_too_low():
    """A negative guess is always below a positive secret."""
    outcome, _ = check_guess(-1, 50)
    assert outcome == "Too Low"


def test_check_guess_both_values_zero():
    """check_guess handles the zero == zero case correctly."""
    outcome, _ = check_guess(0, 0)
    assert outcome == "Win"


def test_check_guess_extremely_large_guess():
    """A hugely large guess is correctly identified as Too High."""
    outcome, _ = check_guess(999999999, 50)
    assert outcome == "Too High"


def test_check_guess_boundary_one_above():
    """A guess exactly one above the secret returns Too High."""
    outcome, _ = check_guess(51, 50)
    assert outcome == "Too High"


def test_check_guess_boundary_one_below():
    """A guess exactly one below the secret returns Too Low."""
    outcome, _ = check_guess(49, 50)
    assert outcome == "Too Low"


# --- update_score edge cases ---

def test_update_score_can_go_below_zero():
    """Score has no lower floor for wrong guesses - it can go negative."""
    result = update_score(0, "Too High", 1)
    assert result == -5


def test_update_score_win_minimum_points_enforced():
    """Winning very late still awards the minimum of 10 points."""
    result = update_score(0, "Win", 20)
    assert result == 10  # 100 - 10*(21) = -110 → clamped to 10


def test_update_score_win_on_first_attempt():
    """Winning on attempt 1 gives 100 - 10*2 = 80 points."""
    assert update_score(0, "Win", 1) == 80


def test_update_score_unknown_outcome_unchanged():
    """An unrecognised outcome string leaves the score unchanged."""
    assert update_score(42, "Draw", 3) == 42


# --- get_hot_cold_label edge cases ---

def test_hot_cold_burning_hot():
    """Distance < 5 % of range → Burning Hot."""
    label = get_hot_cold_label(4, 100)
    assert "Burning Hot" in label


def test_hot_cold_ice_cold():
    """Distance ≥ 60 % of range → Ice Cold."""
    label = get_hot_cold_label(80, 100)
    assert "Ice Cold" in label


def test_hot_cold_zero_distance():
    """Zero distance means the player guessed correctly - Burning Hot."""
    label = get_hot_cold_label(0, 100)
    assert "Burning Hot" in label


def test_hot_cold_zero_range_does_not_crash():
    """A total_range of zero should not raise ZeroDivisionError."""
    label = get_hot_cold_label(0, 0)
    assert isinstance(label, str)
