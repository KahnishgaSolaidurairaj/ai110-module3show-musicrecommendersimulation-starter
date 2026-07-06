# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Stretch Challenge 1: add 5+ advanced song attributes to the dataset and make the scoring
logic account for them, then document the workflow. This required coordinated edits across
several files (dataset, dataclasses, CSV loader, both scoring paths, and a demo profile),
which is a good fit for an agent making multi-step changes.

**Prompts used:**

- "Add 5 or more complex attributes to `data/songs.csv` that aren't in the baseline data —
  Song Popularity (0-100), Release Decade, detailed Mood Tags (e.g. nostalgic, aggressive,
  euphoric), instrumentalness, and language. Fill in sensible values for all 18 songs."
- "Update the scoring logic in `src/recommender.py` so it accounts for the new attributes.
  Keep it **backward compatible**: the new rules should only apply when a profile opts into
  them, so my existing profiles and the documented outputs don't change and the tests still
  pass. Verify the math stays valid."
- "Add one demo profile that uses the new preferences so I can see the attributes actually
  affecting the ranking, then run it."

**What did the agent generate or change?**

- **`data/songs.csv`** — added 5 columns (`popularity`, `release_decade`, `mood_tags`,
  `instrumentalness`, `language`) with values for all 18 songs. `mood_tags` is a
  pipe-separated list (e.g. `nostalgic|moody`) to avoid clashing with CSV commas.
- **`src/recommender.py`** —
  - `Song` dataclass: 5 new fields, each with a **default** so existing constructors/tests
    still work (`mood_tags` uses `field(default_factory=list)`).
  - `UserProfile`: 5 new **optional** preference fields (default `None`/`False`).
  - `load_songs()`: parses `popularity`/`release_decade` as ints, `instrumentalness` as a
    float, and splits `mood_tags` on `|` into a list.
  - New shared helper `_advanced_points()` used by both `score_song()` (dict path) and
    `Recommender._score()` (object path), so the two stay in sync. Rules: `+1.0` popularity
    threshold, `+1.0` decade match, `+0.5` per mood tag (capped at `+1.5`), `+1.0`
    instrumental, `+1.0` language match. Every rule is guarded so it only fires when the
    preference is set.
- **`src/main.py`** — added a "Retro Synthwave Nostalgia" profile that sets the new
  preferences (decade 1980, tag `nostalgic`, min popularity 60, English).

**What did I verify or fix manually?**

- **Ran the tests:** `pytest` → still 2 passed. The default values on the new dataclass
  fields were what kept the old tests (which build `Song`/`UserProfile` without the new
  args) from breaking — I confirmed this was intentional, not luck.
- **Checked backward compatibility myself:** re-ran the old pop/happy profile and confirmed
  its #1 is still `Sunrise City` at **4.96** with no new-attribute points added — proving the
  old outputs in the README/model card are still accurate.
- **Confirmed the new attributes actually change ranking:** ran the new profile and saw
  `Night Drive Loop` jump to the top at **8.50**, with the reasons list showing the decade,
  popularity, mood-tag, and language points. Output:

```
1. Night Drive Loop — Neon Echo   Score: 8.50   (synthwave / moody)
     • genre match: synthwave (+2.0)
     • mood match: moody (+1.0)
     • energy 0.75 vs target 0.75 (+2.00)
     • popular enough: 66 >= 60 (+1.0)
     • decade match: 1980s (+1.0)
     • mood tags ['nostalgic'] (+0.5)
     • language match: english (+1.0)
```

- **Sanity-checked the math:** max possible score rose from 6.0 to 11.5, and I verified
  Night Drive Loop's reasons add up to exactly 8.5. I also made sure `mood_tags` loaded as a
  real list (not a raw string) so the tag-matching `in` check works.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy pattern**. I needed multiple scoring "modes" (Stretch Challenge 2) —
Genre-First, Mood-First, Energy-Focused, and a Balanced default — that a user can switch
between in `main.py`. The Strategy pattern lets me swap the *weighting behavior* without
duplicating or editing the scoring algorithm.

**How did AI help you brainstorm or implement it?**

I asked the AI: *"I want two or more ranking strategies (genre-first, mood-first,
energy-focused) that I can switch between in main.py. Suggest a simple design pattern that
keeps recommender.py modular instead of me writing an if/elif for every mode."* The AI
walked through a few options:

- A big `if mode == "genre-first": ... elif ...` block — rejected, because it hard-codes
  every mode and gets messy fast.
- Subclassing the recommender per mode — rejected as overkill for what is really just a
  change of weights.
- A **Strategy** object that holds the weights and is passed into the scoring function —
  chosen, because each mode becomes a small data object and the scoring code never changes.

The AI also pointed out that if I made "Balanced" reproduce the original weights (2/1/2/1)
and passed the strategy as an *optional* argument, all my existing profiles, documented
outputs, and tests would keep working unchanged. I verified that — `pytest` still passes and
the balanced pop/happy profile still scores 4.96.

**How does the pattern appear in your final code?**

- `ScoringStrategy` (a dataclass in `src/recommender.py`) is the strategy object: it just
  holds `genre_weight`, `mood_weight`, `energy_weight`, and `acoustic_weight`.
- `STRATEGIES` is a registry of ready-made modes (`balanced`, `genre-first`, `mood-first`,
  `energy-focused`).
- `score_song()`, `Recommender._score()`, and `recommend_songs()` all take an optional
  `strategy` argument and read the weights from it (defaulting to `balanced`).
- `main.py` loops over `STRATEGIES` to show the same profile ranked under each mode.

Running the demo confirms the modes really differ: under **Genre-First** both pop songs
(Sunrise City, Gym Hero) sit at the top, while under **Mood-First** the happy-mood Rooftop
Lights jumps up — same songs, different priorities, no change to the scoring algorithm.

---

## Additional Stretch Features

### Diversity & Fairness (Challenge 3)

**Prompt used:** *"Add a diversity penalty to `recommend_songs`. After scoring, pick songs
greedily for the top-k list, and subtract a fixed penalty from a candidate's score for every
song already in the list that shares its artist or genre. Keep it off by default so existing
behavior doesn't change, and show the penalty in the explanation."*

**Result:** `recommend_songs(..., diversity_penalty=1.5)` now selects greedily and applies the
penalty. In the demo, the second pop song (Gym Hero) drops from #2 to #3 with a visible
`diversity penalty (-1.5)` because it shares the genre `pop` with #1 (Sunrise City), letting a
different-genre song (indie-pop Rooftop Lights) move up. With `diversity_penalty=0` (default),
the ranking is identical to before.

### Visual Summary Table (Challenge 4)

**Prompt used:** *"Format the terminal recommendations as a table using simple ASCII (no extra
dependency like tabulate, since it isn't installed). The table must include a column with the
`reasons` for each score, wrapped so all the reasons are readable."*

**Result:** `render_table()` in `main.py` builds a bordered ASCII grid with columns for rank,
song, artist, genre/mood, score, and a wrapped **Why (reasons)** column, so every point that
contributed to a score is visible in the table itself. I chose ASCII over `tabulate` so the
app still runs with only the packages already in `requirements.txt`.
