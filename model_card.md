# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeCheck 1.0**

A small music recommender that matches songs to a listener's "vibe."

---

## 2. Intended Use  

**Goal / task.** VibeCheck takes one listener's taste (favorite genre, favorite mood,
target energy, and whether they like acoustic songs) and predicts which songs in the
catalog they will most enjoy. It returns a ranked top-5 list with a reason for each pick.

**Who it is for.** This is a classroom project for learning how recommenders turn data
into predictions. It is not a real product.

**Intended use:**

- Learning and demos: showing how content-based scoring and ranking work.
- Exploring how different user tastes change the recommendations.

**Non-intended use:**

- Not for real listeners or a real music app.
- Not for judging song quality, artists, or making business decisions.
- Not for any high-stakes or fairness-sensitive setting — it is a toy model on a tiny
  hand-made dataset.

---

## 3. How the Model Works  

Think of it as giving each song a score, then sorting by score.

Each song can earn points four ways:

- **+2 points** if the song's genre matches the listener's favorite genre.
- **+1 point** if the song's mood matches the listener's favorite mood.
- **Up to +2 points** for energy: the closer a song's energy is to the listener's target
  energy, the more points it gets. An exact match earns the full 2 points; a big gap earns
  almost none. (We reward being *close*, not just being loud.)
- **+1 point** if the listener likes acoustic music and the song is acoustic.

We add those points up for every song, sort from highest to lowest, and show the top 5.
Each recommendation also lists the reasons for its score, so the listener can see *why*
it was picked. Compared to the starter code (which just returned the first few songs), we
added the real scoring, the energy "closeness" idea, and the plain-English reasons.

---

## 4. Data  

The catalog is a small CSV file, `data/songs.csv`, with **18 songs**.

Each song has these features:

- Text: title, artist, genre, mood, language.
- Numbers (0.0–1.0): energy, valence, danceability, acousticness, instrumentalness.
- Number: tempo in beats per minute.
- Advanced attributes (added as a stretch feature): popularity (0–100), release decade,
  and detailed mood tags (e.g. `nostalgic`, `aggressive`, `euphoric`).

**Genres** include pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop,
classical, country, edm, reggae, metal, r&b, and folk. **Moods** include happy, chill,
intense, relaxed, moody, focused, energetic, melancholy, nostalgic, euphoric, uplifting,
angry, romantic, and dreamy.

**Changes I made.** The starter had 10 songs. I added 8 more to bring in genres and moods
that were missing, so the catalog is more diverse.

**Limits.** The dataset is tiny and hand-made, so it does not represent real listening
habits. It also has a lopsided energy spread (lots of low- and high-energy songs, few in
the middle), and it has no lyrics, language, or popularity data.

---

## 5. Strengths  

- It works well for listeners with a clear taste. The "chill lofi" and "intense rock"
  profiles both got top-5 lists that felt right.
- The energy "closeness" rule works. Low-energy users get calm songs, high-energy users
  get loud songs, and it can even break ties between two very similar songs.
- Every pick comes with reasons, so it is easy to see *why* a song was chosen.
- It handles new songs with no problem, because it only looks at song features, not at
  other people's listening history.

---

## 6. Limitations and Bias 

**Weakness discovered: the energy gap under-serves mid-energy listeners.** The scoring
rule rewards how close a song's energy is to the user's target, but the catalog is
*bimodal* — of 18 songs, 7 sit at low energy (< 0.45) and 8 at high energy (> 0.65),
leaving only 3 in the middle (0.45–0.65). This means a user with a mid-range
`target_energy` around 0.5 has almost no songs that closely match, so their top
recommendations score lower and are effectively more arbitrary than the confident,
high-scoring lists a low-energy ("chill lofi") or high-energy ("intense rock") user
receives. In effect the system quietly favors listeners at the extremes of the energy
scale and treats "moderate energy" as an unsupported taste, even though nothing in the
scoring logic *intends* that bias — it emerges purely from the dataset's shape. A related
filter-bubble risk is that `favorite_genre` and `favorite_mood` are single values with
additive bonuses, so the system reinforces one narrow taste and rarely surprises the user
with a good cross-genre pick. Fixing this would require balancing the catalog's energy
distribution and/or allowing users to express a *range* or *list* of preferences instead
of one value.

---

## 7. Evaluation  

I stress-tested the recommender with five profiles defined in `src/main.py`: three
"normal" tastes and two adversarial edge cases. Below is the actual terminal output
from `python -m src.main` for each. I looked for whether the top results were sensible
and whether the scoring could be "tricked."

**1. High-Energy Pop** — expected upbeat pop to win.

```
========================================================
  HIGH-ENERGY POP
  For: pop / happy | target energy 0.90 | acoustic: False
========================================================

1. Sunrise City — Neon Echo        Score: 4.84   (pop / happy)
     • genre match: pop (+2.0); mood match: happy (+1.0); energy 0.82 vs target 0.90 (+1.84)
2. Gym Hero — Max Pulse            Score: 3.94   (pop / intense)
     • genre match: pop (+2.0); energy 0.93 vs target 0.90 (+1.94)
3. Rooftop Lights — Indigo Parade  Score: 2.72   (indie pop / happy)
     • mood match: happy (+1.0); energy 0.76 vs target 0.90 (+1.72)
4. Storm Runner — Voltline         Score: 1.98   (rock / intense)
     • energy 0.91 vs target 0.90 (+1.98)
5. Neon Overdrive — Pulsewave      Score: 1.90   (edm / euphoric)
     • energy 0.95 vs target 0.90 (+1.90)
```

**2. Chill Lofi** — expected calm, acoustic lofi to win.

```
========================================================
  CHILL LOFI
  For: lofi / chill | target energy 0.35 | acoustic: True
========================================================

1. Library Rain — Paper Lanterns   Score: 6.00   (lofi / chill)   [perfect score]
     • genre match: lofi (+2.0); mood match: chill (+1.0); energy 0.35 vs target 0.35 (+2.00); acoustic match: 0.86 (+1.0)
2. Midnight Coding — LoRoom        Score: 5.86   (lofi / chill)
     • genre match: lofi (+2.0); mood match: chill (+1.0); energy 0.42 vs target 0.35 (+1.86); acoustic match: 0.71 (+1.0)
3. Focus Flow — LoRoom             Score: 4.90   (lofi / focused)
     • genre match: lofi (+2.0); energy 0.40 vs target 0.35 (+1.90); acoustic match: 0.78 (+1.0)
4. Spacewalk Thoughts — Orbit Bloom Score: 3.86  (ambient / chill)
     • mood match: chill (+1.0); energy 0.28 vs target 0.35 (+1.86); acoustic match: 0.92 (+1.0)
5. Coffee Shop Stories — Slow Stereo Score: 2.96 (jazz / relaxed)
     • energy 0.37 vs target 0.35 (+1.96); acoustic match: 0.89 (+1.0)
```

**3. Deep Intense Rock** — expected high-energy rock to win.

```
========================================================
  DEEP INTENSE ROCK
  For: rock / intense | target energy 0.95 | acoustic: False
========================================================

1. Storm Runner — Voltline         Score: 4.92   (rock / intense)
     • genre match: rock (+2.0); mood match: intense (+1.0); energy 0.91 vs target 0.95 (+1.92)
2. Gym Hero — Max Pulse            Score: 2.96   (pop / intense)
     • mood match: intense (+1.0); energy 0.93 vs target 0.95 (+1.96)
3. Neon Overdrive — Pulsewave      Score: 2.00   (edm / euphoric)
     • energy 0.95 vs target 0.95 (+2.00)
4. Iron Verdict — Blacktide        Score: 1.94   (metal / angry)
     • energy 0.98 vs target 0.95 (+1.94)
5. Sunrise City — Neon Echo        Score: 1.74   (pop / happy)
     • energy 0.82 vs target 0.95 (+1.74)
```

### Adversarial / edge cases

**4. Conflicting (loud + moody + acoustic)** — asks for high energy (0.95) *and* an
acoustic, moody jazz feel, which almost never co-occur.

```
========================================================
  CONFLICTING (LOUD + MOODY + ACOUSTIC)
  For: jazz / moody | target energy 0.95 | acoustic: True
========================================================

1. Coffee Shop Stories — Slow Stereo Score: 3.84 (jazz / relaxed)
     • genre match: jazz (+2.0); energy 0.37 vs target 0.95 (+0.84); acoustic match: 0.89 (+1.0)
2. Night Drive Loop — Neon Echo    Score: 2.60   (synthwave / moody)
     • mood match: moody (+1.0); energy 0.75 vs target 0.95 (+1.60)
3. Backroad Memories — Dusty Wheeler Score: 2.20 (country / nostalgic)
     • energy 0.55 vs target 0.95 (+1.20); acoustic match: 0.72 (+1.0)
4. Neon Overdrive — Pulsewave      Score: 2.00   (edm / euphoric)
     • energy 0.95 vs target 0.95 (+2.00)
5. Gym Hero — Max Pulse            Score: 1.96   (pop / intense)
     • energy 0.93 vs target 0.95 (+1.96)
```

> **Observation:** the winner is a *low-energy* (0.37) acoustic jazz track — the genre
> (+2.0) and acoustic (+1.0) bonuses outweighed the large energy miss (only +0.84).
> The system silently resolved the contradiction by favoring the categorical matches
> over the numeric target, which a user who wanted something *loud* would find wrong.

**5. No-Match (polka / ecstatic)** — no song matches the genre or mood, so ranking
falls back to pure energy closeness.

```
========================================================
  NO-MATCH (POLKA / ECSTATIC)
  For: polka / ecstatic | target energy 0.50 | acoustic: False
========================================================

1. Velvet Hours — Mika Rae         Score: 2.00   (r&b / romantic)
     • energy 0.50 vs target 0.50 (+2.00)
2. Backroad Memories — Dusty Wheeler Score: 1.90 (country / nostalgic)
     • energy 0.55 vs target 0.50 (+1.90)
3. Midnight Coding — LoRoom        Score: 1.84   (lofi / chill)
     • energy 0.42 vs target 0.50 (+1.84)
4. Focus Flow — LoRoom             Score: 1.80   (lofi / focused)
     • energy 0.40 vs target 0.50 (+1.80)
5. Island Time — Coral Sound System Score: 1.80  (reggae / uplifting)
     • energy 0.60 vs target 0.50 (+1.80)
```

> **Observation:** with no categorical matches, every score comes from energy alone
> (max 2.0), and the system still returns 5 songs — it never says "no good match."
> This exposes a limitation: the recommender always fills `k` slots even when nothing
> genuinely fits the user's stated genre/mood.

### What surprised me

- The **conflicting profile** revealed that genre/acoustic bonuses can override a big
  energy mismatch, so "loud + acoustic" quietly becomes "quiet + acoustic."
- The **no-match profile** never returns an empty list or a low-confidence warning —
  it confidently recommends songs that match *nothing* the user asked for.
- Ties are common in the numeric-only cases (e.g. two songs at 1.80), and the tie-break
  is just the original CSV order, which is arbitrary.

### Profile-to-profile comparisons

Plain-language comments on how each pair of profiles differs, and why the difference
makes sense:

- **High-Energy Pop vs. Chill Lofi:** these are near opposites and the outputs prove it.
  Pop pulls loud, upbeat, non-acoustic tracks (Sunrise City, Gym Hero); Lofi pulls quiet,
  acoustic, mellow tracks (Library Rain, Midnight Coding). There is *zero* overlap in
  their top 5, which is exactly what we'd want — the two users share no songs because they
  share no genre, mood, or energy target.
- **High-Energy Pop vs. Deep Intense Rock:** these overlap a lot (both want high energy),
  and the lists share Gym Hero, Storm Runner, Neon Overdrive. The difference is *which one
  wins*: Pop crowns Sunrise City (a genre match), Rock crowns Storm Runner (its own genre
  match). So the high-energy cluster is the same pool of songs; the genre bonus just
  reshuffles who sits at #1. This makes sense — energy decides the neighborhood, genre
  decides the winner within it.
- **Chill Lofi vs. Deep Intense Rock:** total opposites on the energy axis, and again no
  shared songs. Lofi's picks all sit near energy 0.35; Rock's all sit near 0.95. This is
  the clearest demonstration that the energy-closeness term is doing real work.
- **Deep Intense Rock vs. Conflicting (loud + moody):** both target ~0.95 energy, so both
  reach into the loud cluster (Neon Overdrive, Iron Verdict, Gym Hero appear in both). The
  difference is the Conflicting user's acoustic + jazz + moody preferences drag some
  quieter, moodier songs upward, muddying the list — a good illustration of what happens
  when a user's stated preferences contradict each other.
- **Chill Lofi vs. Conflicting:** they briefly overlap on Coffee Shop Stories (quiet
  acoustic jazz), which the Lofi user loves for its calm and the Conflicting user gets
  *by accident* because its genre+acoustic bonuses outweigh its wrong (too-low) energy.
- **No-Match vs. everyone:** with no genre or mood hits, this profile's list is driven
  purely by energy closeness, so it becomes a "medium-energy" sampler (r&b, country, lofi
  all around 0.5). Compared to any focused profile, its top scores are much lower (~2.0
  vs ~5–6), which correctly signals "nothing here is a strong match" — even though the
  system still returns 5 songs.

### Explaining "why does Gym Hero keep showing up for Happy Pop?" (for a non-programmer)

Imagine each song earns points for three things: matching your favorite *style* (genre),
matching your *mood*, and being close to the *energy level* you asked for. The "Happy Pop"
listener asked for pop, a happy mood, and high energy. **Gym Hero** is a pop song with very
high energy — so it scores big on two of the three (pop style + high energy) even though its
mood is "intense," not "happy." It loses the mood point, but the two it wins are enough to
keep it near the top. In short: Gym Hero shows up because it's genuinely a loud pop song, and
this listener explicitly asked for loud pop — the mood mismatch just isn't heavy enough to
push it down the list.

---

## 8. Future Work  

If I kept developing this, I would:

1. **Let users pick more than one favorite.** Right now you get only one genre and one
   mood. Allowing a list would support people with mixed tastes.
2. **Balance the catalog and add more songs.** Adding mid-energy songs would fix the bias
   where medium-energy listeners get weak matches.
3. **Add a "no strong match" message.** Instead of always returning 5 songs, the system
   could say when nothing really fits the user's request.

---

## 9. Personal Reflection  

**Biggest learning moment.** My biggest moment was realizing a recommender is really just
scoring and sorting. There is no magic — you give each song points, add them up, and sort.
The "smart" feeling comes entirely from choosing good rules and good weights. Once I saw
that, the whole idea stopped feeling mysterious.

**How AI tools helped, and when I double-checked.** AI tools sped me up a lot. They helped me
research collaborative vs. content-based filtering, draft the scoring logic, and format the
terminal output cleanly. But I learned not to trust them blindly. Two examples: the AI caught
that the starter's import would break when I ran `python -m src.main`, which saved me time —
but I still had to run the command myself to confirm. And when I described a bias, the AI
checked my dataset and pointed out that a common example ("60% of songs are pop") was actually
false for my data — only 2 of 18 songs are pop. That reminded me to verify claims against the
real numbers instead of accepting a nice-sounding sentence.

**What surprised me about simple algorithms.** I was surprised that four simple rules could
produce lists that genuinely "feel" like recommendations. When the chill-lofi profile returned
calm, acoustic songs and the rock profile returned loud ones, it looked intelligent — even
though it is just arithmetic. The conflicting profile also surprised me: when a user asked for
loud *and* acoustic music, the system quietly picked a quiet song because the genre and
acoustic points outweighed the energy gap. That showed me how weights can hide trade-offs the
user never sees, and made me realize real music apps make thousands of these small scoring
choices that decide what millions of people hear.

**What I would try next.** I would let users pick more than one favorite genre or mood, add
more mid-energy songs to fix the bias I found, and add a "no strong match" message so the
system does not always force five results when nothing really fits.
