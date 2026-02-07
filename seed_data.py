import sqlite3
from openai import images
import requests
import time

DB_NAME = "database.db"
JIKAN_URL = "https://api.jikan.moe/v4/top/anime"
LIMIT = 25

OMDB_API_KEY = "39b4d97c"
OMDB_URL = "http://www.omdbapi.com/"


MOVIE_TITLES = [
    "Oppenheimer",
    "Barbie",
    "shang-chi and the legend of the ten rings"
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

            title = (
            anime.get("title_english")
             or anime.get("title")
            )

            synopsis = anime.get("synopsis") or ""

            alt_titles = [
            anime.get("title", ""),
            anime.get("title_english", ""),
            anime.get("title_japanese", "")
            ]

            search_blob = " ".join(t for t in alt_titles if t)
    
            full_description = f"{synopsis}\n\n{search_blob}"


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

            images = anime.get("images", {}).get("jpg", {})

            poster_url = images.get("large_image_url") or images.get("image_url")
            background_url = images.get("image_url") or poster_url

            # poster_url = (
            #     anime.get("images", {})
            #     .get("jpg", {})
            #     .get("large_image_url")
            # )

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
                full_description,
                anime.get("year"),
                genres,
                poster_url,
                background_url,
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
            print(f"❌ Skipped (not found): {title}")
            continue

        # 🔒 Skip non-movies (OMDb sometimes returns series)
        if data.get("Type") != "movie":
            print(f"⚠️ Skipped (not a movie): {data.get('Title')}")
            continue

        # 🔁 Prevent duplicates
        cursor.execute(
            "SELECT id, trailer_url, background_url FROM content WHERE title = ? AND type = 'movie'",
            (data["Title"],)
        )
        existing = cursor.fetchone()


        # 🖼️ Poster & background
        poster_url = None
        if data.get("Poster") and data["Poster"] != "N/A":
            poster_url = data["Poster"]

        background_url = poster_url  # safe fallback for now

        # 📅 Release year (robust)
        year_raw = data.get("Year", "")
        release_year = None
        if year_raw and year_raw[:4].isdigit():
            release_year = int(year_raw[:4])

        # ⏱️ Runtime
        runtime = None
        if data.get("Runtime") and data["Runtime"] != "N/A":
            runtime = int(data["Runtime"].replace(" min", ""))

        # ⭐ Rating
        rating = None
        if data.get("imdbRating") and data["imdbRating"] != "N/A":
            rating = float(data["imdbRating"])

        # 🎭 Genres
        genres = data.get("Genre", "").lower()

        # 📝 Plot
        description = data.get("Plot")
        
        # ▶️ Trailer (YouTube search embed)
        title_for_trailer = data["Title"].replace(" ", "+")
        trailer_url = f"https://www.youtube.com/embed?listType=search&list={title_for_trailer}+official+trailer"

        if existing:
            content_id, existing_trailer, existing_bg = existing

            # Only update if missing
            if not existing_trailer or not existing_bg:
                cursor.execute("""
                    UPDATE content
                    SET
                        trailer_url = COALESCE(trailer_url, ?),
                        background_url = COALESCE(background_url, ?)
                    WHERE id = ?
                """, (
                    trailer_url,
                    background_url,
                    content_id
                ))

                print(f"🔄 Updated movie: {data['Title']}")
            else:
                print(f"↩️ No update needed: {data['Title']}")

            continue    


        cursor.execute("""
            INSERT INTO content (
            title, type, description, release_year, genres,
            poster_url, background_url, trailer_url,
            rating, views_count, episodes, duration
            )
            VALUES (?, 'movie', ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
            """, (
            data["Title"],
            description,
            release_year,
            genres,
            poster_url,
            background_url,
            trailer_url,
            rating,
            None,
            runtime
            ))


        print(f"✅ Added movie: {data['Title']}")
        added += 1
        time.sleep(0.5)  # respect OMDb limits

    conn.commit()
    conn.close()
    print(f"🎉 Movie seeding completed ({added} movies added).")



if __name__ == "__main__":
    # seed_anime_from_jikan()
    seed_movies_from_omdb()
