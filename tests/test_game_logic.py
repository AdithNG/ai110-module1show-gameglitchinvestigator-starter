from logic_utils import check_guess, update_score


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
