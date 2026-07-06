import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

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
    # Advanced attributes (Stretch Challenge 1). Defaults keep older callers/tests working.
    popularity: int = 0             # 0-100
    release_decade: int = 0         # e.g. 1980, 2020
    mood_tags: List[str] = field(default_factory=list)  # e.g. ["nostalgic", "moody"]
    instrumentalness: float = 0.0   # 0-1
    language: str = ""              # e.g. "english", "instrumental"

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
    # Advanced preferences (Stretch Challenge 1). All optional — a rule only applies
    # when its preference is set, so older profiles score exactly as before.
    min_popularity: Optional[int] = None       # reward songs at/above this popularity
    favorite_decade: Optional[int] = None      # reward songs from this decade
    preferred_mood_tags: Optional[List[str]] = None  # reward each matching tag
    likes_instrumental: bool = False           # reward instrumental songs
    preferred_language: Optional[str] = None   # reward songs in this language

def _advanced_points(
    reasons: List[str],
    *,
    popularity: int,
    release_decade: int,
    mood_tags: List[str],
    instrumentalness: float,
    language: str,
    min_popularity: Optional[int],
    favorite_decade: Optional[int],
    preferred_mood_tags: Optional[List[str]],
    likes_instrumental: bool,
    preferred_language: Optional[str],
) -> float:
    """
    Scoring for the advanced attributes (Stretch Challenge 1). Shared by both the
    dict-based score_song() and the object-based Recommender._score().

    Each rule only fires when the matching preference is set, so profiles that don't
    use these preferences score exactly as they did before.

      +1.0        popularity >= the user's minimum
      +1.0        release_decade == the user's favorite decade
      +0.5/tag    each preferred mood tag the song carries (capped at +1.5)
      +1.0        user likes instrumental and song is instrumental (>= 0.5)
      +1.0        song language == the user's preferred language
    """
    pts = 0.0

    if min_popularity is not None and popularity >= min_popularity:
        pts += 1.0
        reasons.append(f"popular enough: {popularity} >= {min_popularity} (+1.0)")

    if favorite_decade is not None and release_decade == favorite_decade:
        pts += 1.0
        reasons.append(f"decade match: {release_decade}s (+1.0)")

    if preferred_mood_tags:
        matched = [t for t in preferred_mood_tags if t in mood_tags]
        if matched:
            tag_pts = min(1.5, 0.5 * len(matched))
            pts += tag_pts
            reasons.append(f"mood tags {matched} (+{tag_pts:.1f})")

    if likes_instrumental and instrumentalness >= 0.5:
        pts += 1.0
        reasons.append(f"instrumental: {instrumentalness:.2f} (+1.0)")

    if preferred_language is not None and language == preferred_language:
        pts += 1.0
        reasons.append(f"language match: {language} (+1.0)")

    return pts


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one Song against a UserProfile using the Algorithm Recipe."""
        score = 0.0
        reasons: List[str] = []

        if song.genre == user.favorite_genre:
            score += 2.0
            reasons.append(f"genre match: {song.genre} (+2.0)")

        if song.mood == user.favorite_mood:
            score += 1.0
            reasons.append(f"mood match: {song.mood} (+1.0)")

        energy_points = 2.0 * (1 - abs(song.energy - user.target_energy))
        score += energy_points
        reasons.append(
            f"energy {song.energy:.2f} vs target {user.target_energy:.2f} (+{energy_points:.2f})"
        )

        if user.likes_acoustic and song.acousticness >= 0.6:
            score += 1.0
            reasons.append(f"acoustic match: {song.acousticness:.2f} (+1.0)")

        # Advanced attributes (Stretch Challenge 1).
        score += _advanced_points(
            reasons,
            popularity=song.popularity,
            release_decade=song.release_decade,
            mood_tags=song.mood_tags,
            instrumentalness=song.instrumentalness,
            language=song.language,
            min_popularity=user.min_popularity,
            favorite_decade=user.favorite_decade,
            preferred_mood_tags=user.preferred_mood_tags,
            likes_instrumental=user.likes_instrumental,
            preferred_language=user.preferred_language,
        )

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Rank all songs by score (highest first) and return the top k."""
        ranked = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string of why this song matches the user."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "no matching preferences"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dictionaries.

    Numeric columns are converted so we can do math on them later:
      - id, tempo_bpm, popularity, release_decade -> int
      - energy, valence, danceability, acousticness, instrumentalness -> float
    mood_tags is split on "|" into a list of tags.
    Text columns (title, artist, genre, mood, language) stay as strings.

    Required by src/main.py
    """
    int_fields = {"id", "tempo_bpm", "popularity", "release_decade"}
    float_fields = {"energy", "valence", "danceability", "acousticness", "instrumentalness"}

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
                elif key == "mood_tags":
                    song[key] = value.split("|") if value else []
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

    # Advanced attributes (Stretch Challenge 1). Uses .get() so songs/profiles that
    # predate these columns still work.
    score += _advanced_points(
        reasons,
        popularity=song.get("popularity", 0),
        release_decade=song.get("release_decade", 0),
        mood_tags=song.get("mood_tags", []),
        instrumentalness=song.get("instrumentalness", 0.0),
        language=song.get("language", ""),
        min_popularity=user_prefs.get("min_popularity"),
        favorite_decade=user_prefs.get("favorite_decade"),
        preferred_mood_tags=user_prefs.get("preferred_mood_tags"),
        likes_instrumental=user_prefs.get("likes_instrumental", False),
        preferred_language=user_prefs.get("preferred_language"),
    )

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
