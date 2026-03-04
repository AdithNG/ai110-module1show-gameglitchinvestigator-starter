# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, the hints were completely backwards: guessing a number higher than the secret showed "Go HIGHER!" and guessing lower showed "Go LOWER!", making it impossible to close in on the answer. On top of that, every even-numbered attempt secretly converted the hidden number to a string before comparing it, so comparisons like `60 > "50"` fell into the `except TypeError` path and did string ordering instead of numeric ordering - producing wrong results silently. A third major bug was the "New Game" button: it reset the attempt counter and picked a new secret but never reset `status`, so after winning or losing the game immediately blocked further play even after clicking New Game.

I also noticed:
- **Hard difficulty** had a range of 1-50, which is actually *easier* than Normal (1-100).
- **Wrong guesses rewarded points**: on even-numbered attempts, a "Too High" guess *added* 5 points to the score instead of subtracting.
- **Attempts started at 1**, so the very first guess already consumed one of the allowed attempts before the player even typed anything.

---

## 2. How did you use AI as a teammate?

I used Claude (the AI assistant integrated into my editor) throughout this project to help analyze the code, plan the refactor, and generate tests.

**Correct AI suggestion:** When I described the inverted hints bug, the AI correctly identified that `check_guess` had its return strings swapped - `"📈 Go HIGHER!"` was attached to the `guess > secret` branch (too high) instead of the `guess < secret` branch. It suggested swapping the messages and verified the logic with a concrete example (`60 > 50` → guess is too high → player should go lower). I confirmed this was right by running the game and entering a number I knew was above the secret.

**Incorrect/misleading AI suggestion:** Early on, when I asked why the game sometimes gave wrong results on specific attempts, the AI initially suggested the issue was floating-point rounding in `parse_guess`. That was wrong - `parse_guess` was actually fine. The real bug was in `app.py` where the secret was deliberately cast to a string on even attempts. I found the real cause by carefully reading the submit block line-by-line and noticing the `str(st.session_state.secret)` call, which the AI had overlooked.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed when both the automated pytest suite passed *and* I could reproduce the correct behavior in the live Streamlit app. For the hints bug I ran `pytest tests/test_game_logic.py -v` and confirmed `test_guess_too_high` and `test_hint_too_high_says_go_lower` both went green. I then opened the app, used the "Developer Debug Info" expander to read the secret, and deliberately guessed above it - the hint correctly showed "Go LOWER!" for the first time.

I added `test_update_score_wrong_guess_always_subtracts` to specifically catch the score bug: it calls `update_score(100, "Too High", 2)` (even attempt) and asserts the result is `95`, not `105`. Before the fix, this test failed and showed the +5 behavior clearly. The AI helped me phrase the test so it checked both even and odd attempt numbers, making it a stronger regression guard.

---

## 4. What did you learn about Streamlit and state?

In the original app, the secret number kept changing because Streamlit re-runs the entire script from top to bottom on every user interaction (button click, text input, etc.). Each re-run hit `random.randint(low, high)` again and stored a new value, unless the key was already in `session_state`. The fix was to guard the initialization with `if "secret" not in st.session_state`, so the random call only happens the very first time.

Streamlit "reruns" are like refreshing a web page: every click triggers a fresh execution of `app.py`. Without `session_state`, nothing survives between those refreshes. `st.session_state` is a dictionary that persists across reruns within the same browser session, like a locker that keeps your belongings between class periods. The stable secret came from initializing it in `session_state` exactly once and never overwriting it unless the player explicitly starts a new game.

---

## 5. Looking ahead: your developer habits

One habit I want to carry forward is writing a failing test *before* I fix a bug - the "Too High rewards points" bug was invisible until I had a test that quantified the expected score. Having a concrete assertion (`assert result == 95`) made the problem undeniable and the fix verifiable. In future projects I'll write the test first so I know precisely when the bug is gone.

Next time I work with AI on a coding task I would share the full file context earlier, not just a description of the symptom. The AI's misleading floating-point suggestion happened because I described the symptom verbally without showing the actual code; once I pasted the submit block, the AI immediately spotted the `str()` cast. This project reinforced that AI-generated code needs the same careful human review as any other code - it can contain subtle, intentional-looking bugs that only reveal themselves under specific conditions.

---

## 6. Challenge 5 - AI Model Comparison

**Bug used:** The inverted hints bug in `check_guess` - `"Go HIGHER!"` was returned when the guess was *above* the secret, and `"Go LOWER!"` when it was *below*.

### Claude (Anthropic Claude Sonnet 4.6)

**Prompt given:** "In my `check_guess` function, the hints are inverted - when my guess is higher than the secret it says 'Go HIGHER!' and when it's lower it says 'Go LOWER!'. Here is the function: [pasted full function]"

**Fix provided:**

```python
if guess > secret:
    return "Too High", "📉 Go LOWER!"
else:
    return "Too Low", "📈 Go HIGHER!"
```

**Explanation quality:** Claude immediately identified the root cause - the return values for the two branches were swapped. It walked through a concrete example (`guess=60, secret=50` → `60 > 50` is True → player is too high → tell them to go lower), confirmed the corrected logic step by step, and suggested adding a pytest case to prevent regression:

```python
def test_hint_too_high_says_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message.upper()
```

It also noted that the emoji choice (`📉` for too high, `📈` for too low) reinforces the direction visually, which the original bug had also reversed.

---

### ChatGPT (GPT-5.2)

**Same prompt and function pasted.**

**Fix provided:**

```python
if guess > secret:
    return "Too High", "Go LOWER!"
else:
    return "Too Low", "Go HIGHER!"
```

**Explanation quality:** ChatGPT correctly swapped the strings and explained: *"The condition `guess > secret` means the player guessed too high, so you should tell them to go lower."* The fix was accurate and concise. However, it did not suggest a test, did not mention the emoji mismatch, and did not walk through a numeric example.

---

### Comparison

| | Claude Sonnet 4.6 | ChatGPT GPT-5.2 |
|---|---|---|
| **Correct fix?** | ✅ Yes | ✅ Yes |
| **Explained the "why"?** | ✅ Step-by-step with example | Partial - one sentence |
| **Suggested a test?** | ✅ Yes | ❌ No |
| **Caught emoji mismatch?** | ✅ Yes | ❌ No |
| **Readability of fix** | Clean, added inline comment | Clean, no comment |

**Which gave a more readable fix?**
Both were readable. Claude added a brief comment explaining the logic; ChatGPT left the code uncommented. For a future reader the comment is helpful.

**Which explained the "why" more clearly?**
Claude - it used a numeric walk-through (`60 > 50 is True → too high → go lower`) that made the corrected logic impossible to misread. ChatGPT's single-sentence explanation was correct but could still leave a beginner unsure. Providing a test alongside the fix is also a meaningful advantage: it turns the explanation into something verifiable.

**Takeaway:** Both models identified the bug immediately when shown the full function. The practical difference was in the *depth* of guidance: Claude treated the fix as an opportunity to reinforce the reasoning and harden the codebase, while ChatGPT solved the immediate problem efficiently. Depending on the situation (quick fix vs. learning context) either approach could be more appropriate.
