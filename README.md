# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**My version (VibeCheck 1.0)** is a content-based recommender. It loads an 18-song catalog
from a CSV, then scores each song against a user's taste profile (favorite genre, favorite
mood, target energy, and whether they like acoustic music). Songs earn points for matching
the genre and mood and for being *close* to the target energy, and the top 5 are returned
with plain-English reasons for each pick. I tested it on five different listener profiles
and documented its behavior, biases, and limitations in the model card.

---

## How The System Works

### Concept Summary

Real-world recommenders at companies like Spotify and YouTube work at massive scale by blending **collaborative filtering** (learning from millions of users' likes, skips, and listening patterns) with **content-based filtering** (comparing the measurable attributes of songs), then layering context and deep-learning ranking on top. They turn raw behavior and audio data into a prediction of *"what will this person want to hear next?"*

My version is a small, transparent **content-based** recommender. It has no other users' data, so instead of learning from a crowd it compares each song's attributes to a single user's stated taste. It **prioritizes matching the "vibe"** — how close a song's energy is to what the user wants, plus whether the genre, mood, and acoustic feel line up. Each song gets a numeric **score** based on closeness (not just higher-is-better), and the whole list is **ranked** so the top matches rise to the top. The tradeoff is honesty over surprise: it's easy to explain *why* a song was picked, but it can only recommend "more of the same" and won't discover cross-genre surprises the way a large collaborative system can.

### Features Used

**`Song`** attributes (from `data/songs.csv`):

- `id`, `title`, `artist` — identity / display
- `genre` — categorical match signal (e.g. pop, lofi, rock)
- `mood` — categorical match signal (e.g. chill, intense, happy)
- `energy` — 0–1, primary "vibe" axis (calm ↔ intense)
- `valence` — 0–1, emotional positivity (moody ↔ bright)
- `tempo_bpm` — beats per minute (normalized before scoring)
- `danceability` — 0–1, tiebreaker
- `acousticness` — 0–1, organic ↔ electronic feel

**`UserProfile`** attributes:

- `favorite_genre` — genre the user prefers (match bonus)
- `favorite_mood` — mood the user prefers (match bonus)
- `target_energy` — 0–1, the energy level the user wants (scored by *closeness*)
- `likes_acoustic` — boolean, whether to reward high-acousticness songs

### Algorithm Recipe (Scoring Rule)

Each song's score is the sum of these rules. Higher total = better recommendation.

| Rule | Points | Why this weight |
|---|---|---|
| **Genre match** (`song.genre == favorite_genre`) | **+2.0** | Strongest identity signal; a genre mismatch is often a dealbreaker. |
| **Mood match** (`song.mood == favorite_mood`) | **+1.0** | Weaker signal, and overlaps with energy — kept at half of genre to avoid double-counting. |
| **Energy closeness** | **+2.0 × (1 − \|song.energy − target_energy\|)** | Rewards songs *near* the target, not just high-energy ones. Closeness, not magnitude. |
| **Acoustic match** (`likes_acoustic and song.acousticness ≥ 0.6`) | **+1.0** | Bonus when the user wants acoustic and the song delivers. |

**Ranking rule:** apply the scoring rule to every song, sort by score descending, and return the top `k`.

```python
score = 0.0
if song.genre == user["favorite_genre"]: score += 2.0
if song.mood  == user["favorite_mood"]:  score += 1.0
score += 2.0 * (1 - abs(song.energy - user["target_energy"]))
if user["likes_acoustic"] and song.acousticness >= 0.6: score += 1.0
```

These weights are tunable — see **Experiments You Tried** for what happens when they change.

### Data Flow

How a single song travels from the CSV to a ranked list:

```
INPUT                    PROCESS (the loop)                 OUTPUT
─────                    ──────────────────                 ──────
User Prefs  ─┐
             │      ┌─────────────────────────────┐
songs.csv ───┼────▶ │ for each song in catalog:    │
             │      │   score = scoring rule       │──▶ sort by score  ──▶ Top K
             │      │   (genre + mood + energy +   │    (descending)       recommendations
             │      │    acoustic bonuses)         │
             │      └─────────────────────────────┘
             │            SCORING RULE                    RANKING RULE
```

- **Input:** the `UserProfile` dict + the parsed list of songs from `data/songs.csv`.
- **Process:** loop over every song, apply the scoring rule → one number per song (this is `score_song`).
- **Output:** sort all scored songs high→low, slice the top `k` (this is `recommend_songs`).

### Potential Biases

- **Genre over-prioritization.** With genre weighted at +2.0 (the largest categorical bonus), the system may bury a song that perfectly matches the user's mood and energy simply because its genre differs — ignoring great cross-genre picks a real listener would enjoy.
- **Popularity/catalog bias.** The catalog is tiny (18 songs) and skewed toward certain genres (lofi, pop). Under-represented genres have fewer chances to be recommended regardless of fit.
- **Mainstream-taste bias.** Single-value `favorite_genre`/`favorite_mood` fields assume a user has *one* taste; eclectic listeners are poorly served, and the system reinforces a narrow "filter bubble" of similar songs.
- **Energy/mood double-counting.** Because `mood` correlates with `energy`, the calm-vs-intense signal is effectively counted twice, subtly amplifying that axis over others like danceability or valence.

### Feature Analysis (from `data/songs.csv`)

The catalog exposes these attributes: `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`.

**Which features drive the recommender, and why:**

- **`energy` (Tier 1)** — the best discriminator; spreads cleanly from calm (0.28) to intense (0.93) and is the axis listeners feel most immediately.
- **`valence` (Tier 1)** — emotional positivity (bright vs. moody); separates songs that share energy but feel different (tense Storm Runner vs. upbeat Gym Hero). Energy + valence together form the classic "mood quadrant."
- **`acousticness` (Tier 1)** — cleanly separates organic/acoustic tracks (0.86+) from produced/electronic ones (0.05).
- **`tempo_bpm` (Tier 2)** — meaningful, but **must be normalized** (÷200 or min-max) before mixing with the 0–1 features, or its large scale dominates.
- **`danceability` (Tier 2)** — correlates with energy here, so it's a useful tiebreaker rather than a primary axis.
- **`genre` / `mood` (Tier 3, categorical)** — used as a **match bonus** (points for matching the user's preference), not as numeric distance. `mood` is somewhat redundant with the energy+valence quadrant.

**Does this match how a "vibe" feels?** Mostly yes — energy × valence mirrors how people intuitively sort music (calm↔hyped, happy↔moody), and acousticness captures the "unplugged vs. polished" feel. Where the numbers fall short: a real vibe also depends on lyrics, context, and artist — things these audio stats can't see.

---

## Background Research: How Real Recommenders Work

Platforms like Spotify and YouTube don't use one algorithm — they blend several. The two foundational approaches are **collaborative filtering** and **content-based filtering**, and modern systems combine them into a **hybrid**.

### Collaborative Filtering — "people like you also liked…"

Predicts what *you'll* like based on the behavior of *other users*, without looking at what a song actually sounds like. It builds a giant user × song matrix of interactions and finds hidden patterns (via matrix factorization or neural embeddings), placing users and songs in the same "taste space" where nearness predicts preference.

- **Strength:** discovers surprising, cross-genre picks no attribute analysis would find (Spotify's Discover Weekly relies heavily on this).
- **Weakness — cold start:** can't recommend a brand-new song nobody has played yet, or serve a brand-new user with no history.

### Content-Based Filtering — "more songs like this one"

Recommends songs whose *attributes* resemble songs you already like. Each song becomes a feature vector (genre, tempo, energy, mood…), your taste profile becomes a vector too, and songs are scored by *similarity* (e.g., cosine similarity). **This is what our project's `Recommender` does** — scoring each `Song` against a `UserProfile`.

- **Strength:** no cold start for new songs; easy to explain ("recommended because it's chill indie like your saves").
- **Weakness:** stays in a bubble — keeps recommending more of the same and rarely surprises you.

### Key Difference

| | Collaborative filtering | Content-based filtering |
|---|---|---|
| **Signal** | Other users' behavior | The song's own attributes |
| **Question** | "What did similar people like?" | "What resembles what *you* like?" |
| **Cold start** | Struggles with new songs/users | Handles new songs well |
| **Discovery** | Surprising, cross-genre | Safe, similar-sounding |
| **Needs** | Lots of interaction data | Good feature/metadata data |

In practice Spotify and YouTube use **hybrid** systems — collaborative filtering for discovery, content-based for cold start and coherence, plus context signals and deep-learning ranking on top.

### Main Data Types Involved

- **Behavioral / interaction data** (fuels collaborative filtering): *explicit* signals like likes, thumbs up/down, saves, follows; and *implicit* signals like **skips** (and how soon you skip), play count, completion rate, replays, playlist adds, session length, search queries.
- **Content / attribute data** (fuels content-based filtering): genre, artist, language, and audio features like **tempo (BPM), energy, valence (mood/positivity), danceability, acousticness**, instrumentalness, loudness, key — plus lyrics via NLP.
- **Context data** (used by hybrid rankers): time of day, device, location, current activity.

> **How this maps to our project:** this simulator is a **content-based** recommender. The `Song` attributes are the content features, the `UserProfile` is the taste vector, and the `Recommender`'s scoring rule is the similarity function. Because it has no other users' behavior (no likes/skips), it can only recommend "more of the same" — it will never surprise a user the way Discover Weekly does.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Terminal output from `python -m src.main` for the upbeat "pop / happy" profile
(`favorite_genre=pop`, `favorite_mood=happy`, `target_energy=0.80`, `likes_acoustic=False`):

```
Loaded songs: 18

========================================================
  TOP RECOMMENDATIONS
  For: pop / happy | target energy 0.80 | acoustic: False
========================================================

1. Sunrise City — Neon Echo
   Score: 4.96   (pop / happy)
   Reasons:
     • genre match: pop (+2.0)
     • mood match: happy (+1.0)
     • energy 0.82 vs target 0.80 (+1.96)

2. Gym Hero — Max Pulse
   Score: 3.74   (pop / intense)
   Reasons:
     • genre match: pop (+2.0)
     • energy 0.93 vs target 0.80 (+1.74)

3. Rooftop Lights — Indigo Parade
   Score: 2.92   (indie pop / happy)
   Reasons:
     • mood match: happy (+1.0)
     • energy 0.76 vs target 0.80 (+1.92)

4. Concrete Kingdom — Vell
   Score: 2.00   (hip hop / energetic)
   Reasons:
     • energy 0.80 vs target 0.80 (+2.00)

5. Night Drive Loop — Neon Echo
   Score: 1.90   (synthwave / moody)
   Reasons:
     • energy 0.75 vs target 0.80 (+1.90)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

### Experiment: Weight Shift (energy ×2, genre ÷2)

I doubled the energy weight (`2.0 → 4.0 × closeness`) and halved the genre weight
(`+2.0 → +1.0`) in both scoring paths of `recommender.py`, then re-ran all five profiles.

**What stayed the same:** the three "normal" profiles kept the *same* #1 (Sunrise City,
Library Rain, Storm Runner) — their top picks match genre *and* energy, so shifting the
balance between those two rules didn't change the winner.

**What changed (the interesting part):** the **Conflicting** profile (wants loud + moody +
acoustic). Under the original weights, #1 was *Coffee Shop Stories* — a **quiet 0.37-energy**
acoustic jazz track that won on genre+acoustic bonuses despite ignoring the user's request
for high energy. After the shift, #1 became **Night Drive Loop** (synthwave / **moody**,
energy 0.75), and the quiet jazz track dropped out of the top 5 entirely.

```
CONFLICTING profile — before vs after
  before (genre 2.0, energy 2.0):  1. Coffee Shop Stories (jazz, energy 0.37)  ← quiet
  after  (genre 1.0, energy 4.0):  1. Night Drive Loop   (synthwave/moody, 0.75) ← louder
```

**More accurate or just different?** For most users it was just *different* (same winners),
but for the conflicting user it was genuinely **more accurate** — a listener asking for loud
music should not get a near-silent track at #1. The trade-off is that genre now matters less,
so the system is more willing to cross genres to honor the energy target. Tests still pass.

---

## Limitations and Risks

- **Tiny, hand-made catalog.** Only 18 songs, so results are not representative of real
  listening and under-represented genres rarely get recommended.
- **Energy-gap bias.** The catalog is bimodal (mostly low- or high-energy songs, few in the
  middle), so mid-energy listeners get weaker, more arbitrary matches. *(See model card §6.)*
- **Always returns 5 songs.** Even when nothing matches the user's genre or mood, it still
  fills the list from energy alone instead of saying "no strong match."
- **No lyrics, language, context, or popularity.** It only sees the audio-style attributes
  in the CSV, so it can't capture much of what makes a song feel right.
- **Single-taste filter bubble.** One favorite genre and one favorite mood mean eclectic
  listeners are poorly served and the system keeps recommending "more of the same."

I go deeper on these in the [model card](model_card.md).

---

## Reflection

Read the full reflection in [**model_card.md**](model_card.md) §9.

The biggest thing I learned is that a recommender is really just **scoring and sorting**:
you turn each song and the user's taste into numbers, give points for how well they match,
add them up, and sort. There is no magic — the "smart" feeling comes entirely from choosing
good features and good weights. Watching four simple rules produce lists that genuinely felt
like recommendations (calm songs for the lofi user, loud songs for the rock user) made that
click.

I also saw how easily bias can hide in a system like this. My scoring never *intends* to
favor anyone, yet the shape of the dataset quietly under-serves mid-energy listeners, and my
weights let a "loud + acoustic" request return a quiet song. Real music apps make thousands of
these tiny scoring choices, and each one silently decides what millions of people hear — so
small, invisible design decisions can have very unequal effects on different users.



