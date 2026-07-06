"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    # When run as a module from the project root: python -m src.main
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:
    # When run directly from inside src/: python main.py
    from recommender import load_songs, recommend_songs


# Profiles for stress testing. The first three are "normal" tastes; the last
# two are adversarial / edge cases designed to try to trick the scoring logic.
PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop", "favorite_mood": "happy",
        "target_energy": 0.90, "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi", "favorite_mood": "chill",
        "target_energy": 0.35, "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock", "favorite_mood": "intense",
        "target_energy": 0.95, "likes_acoustic": False,
    },
    # Edge case: conflicting preferences — wants HIGH energy but a moody/acoustic
    # feel, which almost never co-occur in the catalog.
    "Conflicting (loud + moody + acoustic)": {
        "favorite_genre": "jazz", "favorite_mood": "moody",
        "target_energy": 0.95, "likes_acoustic": True,
    },
    # Edge case: nothing in the catalog matches genre or mood, so ranking must
    # fall back to pure energy closeness.
    "No-Match (polka / ecstatic)": {
        "favorite_genre": "polka", "favorite_mood": "ecstatic",
        "target_energy": 0.50, "likes_acoustic": False,
    },
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Run the recommender for one profile and print a clean ranked list."""
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print("\n" + "=" * 56)
    print(f"  {name.upper()}")
    print(
        f"  For: {user_prefs['favorite_genre']} / {user_prefs['favorite_mood']}"
        f" | target energy {user_prefs['target_energy']:.2f}"
        f" | acoustic: {user_prefs['likes_acoustic']}"
    )
    print("=" * 56 + "\n")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — {song['artist']}")
        print(f"   Score: {score:.2f}   ({song['genre']} / {song['mood']})")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     • {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()
