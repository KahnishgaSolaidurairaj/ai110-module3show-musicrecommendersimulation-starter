# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



