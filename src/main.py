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


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile: an upbeat "pop / happy" listener.
    # Each key is a target the recommender compares songs against.
    user_prefs = {
        "favorite_genre": "pop",      # categorical match bonus
        "favorite_mood": "happy",     # categorical match bonus
        "target_energy": 0.80,        # scored by CLOSENESS, not higher-is-better
        "likes_acoustic": False,      # rewards high-acousticness songs
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # ---- Clean, readable terminal layout ----
    print("\n" + "=" * 56)
    print("  TOP RECOMMENDATIONS")
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


if __name__ == "__main__":
    main()
