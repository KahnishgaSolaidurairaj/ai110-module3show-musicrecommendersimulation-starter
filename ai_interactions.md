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

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
