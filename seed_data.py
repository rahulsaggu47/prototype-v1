import sqlite3
import requests
import time

DB_NAME = "database.db"
JIKAN_URL = "https://api.jikan.moe/v4/top/anime"
LIMIT = 25

OMDB_API_KEY = "39b4d97c"
OMDB_URL = "http://www.omdbapi.com/"


MOVIE_TITLES = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "The Godfather Part II",
    "12 Angry Men",
    "Schindler's List",
    "The Lord of the Rings: The Return of the King",
    "Pulp Fiction",
    "The Lord of the Rings: The Fellowship of the Ring",
    "Fight Club",
    "Forrest Gump",
    "Inception",
    "The Lord of the Rings: The Two Towers",
    "The Matrix",
    "Goodfellas",
    "Se7en",
    "Interstellar",
    "The Silence of the Lambs",
    "Saving Private Ryan",
    "The Green Mile",
    "Gladiator",
    "The Prestige",
    "The Departed",
    "Whiplash",
    "The Lion King",
    "The Pianist",
    "Parasite",
    "Joker",
    "Avengers: Endgame",
    "Iron Man",
    "Django Unchained",
    "The Wolf of Wall Street",
    "Batman Begins",
    "The Dark Knight Rises",
    "Doctor Strange",
    "Spider-Man: No Way Home",
    "Titanic",
    "Avatar",
    "Dune",
    "Oppenheimer",
    "Blade Runner 2049",
    "Mad Max: Fury Road",
    "Logan",
    "John Wick",
    "The Social Network",
    "Shutter Island",
    "La La Land",
    "No Country for Old Men",
    "The Grand Budapest Hotel"
]


def seed_anime_from_jikan():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    headers = {
        "User-Agent": "Nextwatch-Student-Project/1.0"
    }

    print("🎌 Fetching top anime from Jikan...")

    added = 0
    page = 1
    PER_PAGE = 25

    while added < 50:
        response = requests.get(
            JIKAN_URL,
            params={"page": page, "limit": PER_PAGE},
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print("❌ Jikan request failed")
            print(response.json())
            break

        data = response.json().get("data", [])
        if not data:
            print("❌ No data returned")
            break

        for anime in data:
            if added >= 50:
                break

            title = anime.get("title")
            if not title:
                continue

            cursor.execute(
                "SELECT id FROM content WHERE title = ? AND type = 'anime'",
                (title,)
            )
            if cursor.fetchone():
                continue

            genres = ",".join(
                [g["name"].lower() for g in anime.get("genres", [])]
            )

            poster_url = (
                anime.get("images", {})
                .get("jpg", {})
                .get("large_image_url")
            )

            trailer_url = None
            if anime.get("trailer") and anime["trailer"].get("embed_url"):
                trailer_url = anime["trailer"]["embed_url"]

            cursor.execute("""
                INSERT INTO content (
                    title, type, description, release_year, genres,
                    poster_url, background_url, trailer_url,
                    rating, views_count, episodes, duration
                )
                VALUES (?, 'anime', ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """, (
                title,
                anime.get("synopsis"),
                anime.get("year"),
                genres,
                poster_url,
                poster_url,
                trailer_url,
                anime.get("score"),
                anime.get("popularity"),
                anime.get("episodes")
            ))

            print(f"✅ Added anime: {title}")
            added += 1
            time.sleep(0.6)  # respect rate limits

        page += 1

    conn.commit()
    conn.close()
    print(f"🎉 Anime seeding completed ({added} anime added).")



def seed_movies_from_omdb():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("🎬 Fetching movies from OMDb...")

    added = 0

    for title in MOVIE_TITLES:
        response = requests.get(
            OMDB_URL,
            params={
                "apikey": OMDB_API_KEY,
                "t": title,
                "plot": "full"
            },
            timeout=15
        )

        data = response.json()

        if data.get("Response") != "True":
            print(f"❌ Skipped: {title}")
            continue

        cursor.execute(
            "SELECT id FROM content WHERE title = ? AND type = 'movie'",
            (data["Title"],)
        )
        if cursor.fetchone():
            continue

        poster_url = None
        if data.get("Poster") and data["Poster"] != "N/A":
            poster_url = data["Poster"]

        cursor.execute("""
            INSERT INTO content (
                title, type, description, release_year, genres,
                poster_url, background_url, trailer_url,
                rating, views_count, episodes, duration
            )
            VALUES (?, 'movie', ?, ?, ?, ?, ?, NULL, ?, ?, NULL, ?)
        """, (
            data["Title"],
            data.get("Plot"),
            int(data["Year"]) if data.get("Year") else None,
            data.get("Genre", "").lower(),
            poster_url,
            poster_url,
            float(data["imdbRating"]) if data.get("imdbRating") != "N/A" else None,
            None,
            int(data["Runtime"].replace(" min", "")) if data.get("Runtime") != "N/A" else None
        ))

        print(f"✅ Added movie: {data['Title']}")
        added += 1
        time.sleep(0.5)

    conn.commit()
    conn.close()
    print(f"🎉 Movie seeding completed ({added} movies added).")


if __name__ == "__main__":
    seed_anime_from_jikan()
    # seed_movies_from_omdb()
