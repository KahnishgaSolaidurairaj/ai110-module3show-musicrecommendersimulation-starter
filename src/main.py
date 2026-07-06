"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender. It also demonstrates the
stretch features:
  - multiple scoring modes / strategies (Challenge 2)
  - a diversity penalty (Challenge 3)
  - a formatted summary table with reasons (Challenge 4)
"""

import textwrap

try:
    # When run as a module from the project root: python -m src.main
    from src.recommender import load_songs, recommend_songs, STRATEGIES
except ModuleNotFoundError:
    # When run directly from inside src/: python main.py
    from recommender import load_songs, recommend_songs, STRATEGIES


# Profiles for stress testing. The first three are "normal" tastes; the next two are
# adversarial / edge cases, and the last exercises the advanced attributes.
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
    # Advanced profile (Stretch Challenge 1): exercises the new attributes —
    # popularity, release decade, detailed mood tags, instrumentalness, language.
    "Retro Synthwave Nostalgia": {
        "favorite_genre": "synthwave", "favorite_mood": "moody",
        "target_energy": 0.75, "likes_acoustic": False,
        "favorite_decade": 1980,               # loves 80s tracks
        "preferred_mood_tags": ["nostalgic"],  # wants a nostalgic feel
        "min_popularity": 60,                  # reasonably well-known songs
        "preferred_language": "english",       # with vocals in English
    },
}

# Column layout for the summary table: (header, width).
_COLUMNS = [("#", 2), ("Song", 20), ("Artist", 16), ("Genre / Mood", 16),
            ("Score", 6), ("Why (reasons)", 42)]


def render_table(recommendations: list) -> str:
    """
    Render recommendations as a formatted ASCII table (Stretch Challenge 4).

    The table includes the reasons for each score, wrapped inside the last column so
    every point that contributed to the score is visible.
    """
    border = "+" + "+".join("-" * (w + 2) for _, w in _COLUMNS) + "+"
    head = "|" + "|".join(f" {h:<{w}} " for h, w in _COLUMNS) + "|"
    lines = [border, head, border]

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        raw_cells = [
            str(rank),
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f}",
        ]
        # Wrap each of the first five cells to its column width.
        wrapped = [textwrap.wrap(val, w) or [""] for (_, w), val in zip(_COLUMNS, raw_cells)]
        # The "Why" column: one wrapped block per reason.
        why_width = _COLUMNS[5][1]
        why_lines = []
        for reason in explanation.split("; "):
            why_lines.extend(textwrap.wrap(reason, why_width) or [""])
        wrapped.append(why_lines)

        height = max(len(cell) for cell in wrapped)
        for i in range(height):
            row = []
            for (_, w), cell in zip(_COLUMNS, wrapped):
                text = cell[i] if i < len(cell) else ""
                row.append(f" {text:<{w}} ")
            lines.append("|" + "|".join(row) + "|")
        lines.append(border)

    return "\n".join(lines)


def _header(title: str, subtitle: str = "") -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * 72)


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5,
                          strategy=None, diversity_penalty: float = 0.0) -> None:
    """Run the recommender for one profile and print the results as a table."""
    recs = recommend_songs(user_prefs, songs, k=k,
                           strategy=strategy, diversity_penalty=diversity_penalty)
    subtitle = (f"{user_prefs['favorite_genre']} / {user_prefs['favorite_mood']}"
                f" | target energy {user_prefs['target_energy']:.2f}"
                f" | acoustic: {user_prefs['likes_acoustic']}")
    _header(name.upper(), subtitle)
    print(render_table(recs))


def main() -> None:
    songs = load_songs("data/songs.csv")

    # 1. Every profile, default (balanced) mode, as a table.
    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs)

    # 2. Scoring modes (Challenge 2): same profile, different strategies.
    demo_name = "High-Energy Pop"
    demo_prefs = PROFILES[demo_name]
    for key, strategy in STRATEGIES.items():
        print_recommendations(f"{demo_name}  [mode: {strategy.name}]",
                              demo_prefs, songs, k=4, strategy=strategy)

    # 3. Diversity penalty (Challenge 3): off vs on for a genre-heavy profile.
    print_recommendations("High-Energy Pop  [diversity OFF]",
                          demo_prefs, songs, k=5, diversity_penalty=0.0)
    print_recommendations("High-Energy Pop  [diversity ON, penalty 1.5]",
                          demo_prefs, songs, k=5, diversity_penalty=1.5)


if __name__ == "__main__":
    main()
