import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dictionaries.

    Numeric columns are converted so we can do math on them later:
      - id, tempo_bpm  -> int
      - energy, valence, danceability, acousticness -> float
    Text columns (title, artist, genre, mood) stay as strings.

    Required by src/main.py
    """
    int_fields = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song: Dict = {}
            for key, value in row.items():
                if key in int_fields:
                    song[key] = int(value)
                elif key in float_fields:
                    song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)

    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (the "Scoring Rule").

    Algorithm Recipe:
      +2.0                              genre match
      +1.0                              mood match
      +2.0 * (1 - |energy - target|)    energy closeness (reward being NEAR the target)
      +1.0                              acoustic match (user likes acoustic and song is acoustic)

    Returns (score, reasons) where reasons explains each point awarded.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    # +2.0 for a genre match
    if song["genre"] == user_prefs.get("favorite_genre"):
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    # +1.0 for a mood match
    if song["mood"] == user_prefs.get("favorite_mood"):
        score += 1.0
        reasons.append(f"mood match: {song['mood']} (+1.0)")

    # Energy closeness: reward songs whose energy is NEAR the target, not just high.
    target_energy = user_prefs.get("target_energy")
    if target_energy is not None:
        closeness = 1 - abs(song["energy"] - target_energy)  # 1.0 = exact, 0.0 = far
        energy_points = 2.0 * closeness
        score += energy_points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{energy_points:.2f})"
        )

    # +1.0 acoustic match
    if user_prefs.get("likes_acoustic") and song["acousticness"] >= 0.6:
        score += 1.0
        reasons.append(f"acoustic match: {song['acousticness']:.2f} (+1.0)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Ranks the whole catalog and returns the top k (the "Ranking Rule").

    Steps:
      1. Judge every song with score_song() -> (song, score, explanation).
      2. Sort all scored songs from highest score to lowest.
      3. Return the top k.

    Expected return format: (song_dict, score, explanation)
    Required by src/main.py
    """
    # 1. Score every song. Build the explanation string from the reasons list.
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no matching preferences"
        scored.append((song, score, explanation))

    # 2. sorted() returns a NEW list (leaves `scored`/`songs` untouched); key picks the
    #    score (index 1); reverse=True puts the highest score first.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    # 3. Slice the top k.
    return ranked[:k]
