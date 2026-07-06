# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
