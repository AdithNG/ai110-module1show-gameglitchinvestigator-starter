# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable.

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the fixed app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Game purpose:** A number-guessing game where the player tries to identify a hidden number within a limited number of attempts. The difficulty setting controls the range (Easy: 1-20, Normal: 1-100, Hard: 1-200) and the attempt limit.

- [x] **Bugs found:**
  1. **Inverted hints** -"Go HIGHER!" displayed when guess was too high (should be "Go LOWER!"), and vice versa.
  2. **Secret converted to string on even attempts** -`str(st.session_state.secret)` on even-numbered guesses broke numeric comparison and produced wrong hints silently.
  3. **New Game didn't reset game state** -clicking New Game after winning/losing never reset `status`, `history`, or `score`, so the game remained locked.
  4. **Hard difficulty was easier than Normal** - range was 1-50 instead of something harder like 1-200.
  5. **Wrong guesses rewarded points on even attempts** -`update_score` added +5 for a "Too High" guess on even attempt numbers.
  6. **Attempt counter started at 1** -the first real guess was counted as the second attempt.

- [x] **Fixes applied:**
  - Swapped the hint messages in `check_guess` so "Too High" → "Go LOWER!" and "Too Low" → "Go HIGHER!".
  - Removed the `str()` cast; always pass the integer secret to `check_guess`.
  - New Game now resets `status`, `history`, and `score` in addition to `attempts` and `secret`.
  - Changed Hard difficulty range to `(1, 200)`.
  - `update_score` now always subtracts 5 for any wrong guess, regardless of attempt parity.
  - Initialised `attempts` to `0` instead of `1`.
  - Moved all four logic functions into `logic_utils.py` and imported them in `app.py`.

## 📸 Demo

![Winning game screenshot](Success.png)

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
