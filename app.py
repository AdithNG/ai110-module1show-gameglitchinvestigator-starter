import random
import streamlit as st

# FIX: logic moved out of app.py and into logic_utils.py (Refactor)
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    get_hot_cold_label,  # Challenge 4: Hot/Cold proximity labels
)
# Challenge 2: persistent high-score tracker
from high_score import load_high_score, save_high_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

# ---------------------------------------------------------------------------
# Sidebar - settings + scoreboard
# ---------------------------------------------------------------------------
st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# Challenge 2: show high score in sidebar
st.sidebar.divider()
st.sidebar.subheader("🏆 Scoreboard")
st.sidebar.metric("All-Time High Score", load_high_score())
st.sidebar.metric("Current Score", st.session_state.get("score", 0))

# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: attempts counter was initialised to 1, wasting the first attempt
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Challenge 4: richer per-guess records for the history table
if "guess_details" not in st.session_state:
    st.session_state.guess_details = []

# ---------------------------------------------------------------------------
# Main game area
# ---------------------------------------------------------------------------
st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX: New Game now resets status, history, and score in addition to
# attempts and secret, so the player can actually play a new game
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.score = 0
    st.session_state.guess_details = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX: secret was deliberately converted to a string on even attempts,
        # which broke comparisons. Always pass the integer secret.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        # Challenge 4: compute proximity for Hot/Cold label
        distance = abs(guess_int - st.session_state.secret)
        total_range = high - low
        hot_cold = get_hot_cold_label(distance, total_range)

        # Store richer record for the session-history table
        st.session_state.guess_details.append({
            "attempt": st.session_state.attempts,
            "guess": guess_int,
            "outcome": outcome,
            "distance": distance,
            "hot_cold": hot_cold,
        })

        # Challenge 4: color-coded, emoji-enhanced hint display
        if show_hint:
            if outcome == "Win":
                st.success(message)
            elif outcome == "Too High":
                # Red = danger / go down
                st.error(f"{message}  •  {hot_cold}")
            else:
                # Blue = informational / go up
                st.info(f"{message}  •  {hot_cold}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            # Challenge 2: update high score if this run beats the record
            new_record = save_high_score(st.session_state.score)
            if new_record:
                st.success(
                    f"🏆 NEW HIGH SCORE: {st.session_state.score}!  "
                    f"The secret was {st.session_state.secret}."
                )
            else:
                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# ---------------------------------------------------------------------------
# Challenge 4: Session history table
# ---------------------------------------------------------------------------
if st.session_state.guess_details:
    st.divider()
    st.subheader("📊 Guess History")

    outcome_icon = {"Win": "🎉", "Too High": "📉", "Too Low": "📈"}

    rows = [
        {
            "#": d["attempt"],
            "Guess": d["guess"],
            "Result": f"{outcome_icon.get(d['outcome'], '')} {d['outcome']}",
            "Distance": d["distance"],
            "Proximity": d["hot_cold"],
        }
        for d in st.session_state.guess_details
    ]

    st.dataframe(rows, hide_index=True, use_container_width=True)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
