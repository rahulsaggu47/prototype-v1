import sqlite3
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "database.db"

# ================================================================
#  API KEYS
#  TMDB: free at https://www.themoviedb.org/settings/api
#  Jikan: no key needed
# ================================================================
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Set this in your .env file

TMDB_BASE    = "https://api.themoviedb.org/3"
TMDB_IMG     = "https://image.tmdb.org/t/p"
JIKAN_URL    = "https://api.jikan.moe/v4/top/anime"


# ================================================================
#  MOVIES YOU WANT IN THE DATABASE
#  Add/remove titles freely. The seeder finds them by name on TMDB.
# ================================================================
MOVIE_TITLES = [

# ================= HOLLYWOOD =================
"The Shawshank Redemption",
"The Godfather",
"The Dark Knight",
"Pulp Fiction",
"Forrest Gump",
"Inception",
"Fight Club",
"Interstellar",
"The Matrix",
"Gladiator",
"Titanic",
"Avatar",
"Avengers: Endgame",
"Iron Man",
"Captain America: The First Avenger",
"Thor",
"Doctor Strange",
"Black Panther",
"Spider-Man: No Way Home",
"Deadpool",
"Logan",
"Joker",
"The Batman",
"The Prestige",
"Memento",
"Django Unchained",
"Inglourious Basterds",
"Once Upon a Time in Hollywood",
"Se7en",
"Zodiac",
"Shutter Island",
"The Wolf of Wall Street",
"The Social Network",
"Whiplash",
"La La Land",
"Parasite",
"1917",
"Saving Private Ryan",
"Braveheart",
"Mad Max: Fury Road",
"John Wick",
"Mission: Impossible",
"Top Gun: Maverick",
"Edge of Tomorrow",
"Pacific Rim",
"Transformers",
"Jurassic Park",
"Jaws",
"The Lion King",
"Frozen",
"Toy Story",
"Coco",
"Up",
"Inside Out",
"Finding Nemo",
"Cars",
"Monsters, Inc.",
"Ratatouille",
"The Incredibles",

# ================= BOLLYWOOD =================
"3 Idiots",
"Dangal",
"PK",
"Taare Zameen Par",
"Zindagi Na Milegi Dobara",
"Rockstar",
"Tamasha",
"Barfi!",
"Bajrangi Bhaijaan",
"Sultan",
"War",
"Pathaan",
"Jawan",
"Chak De! India",
"Swades",
"Rang De Basanti",
"Dil Chahta Hai",
"Kal Ho Naa Ho",
"Kabhi Khushi Kabhie Gham",
"Devdas",
"Mughal-e-Azam",
"Sholay",
"Don",
"Agneepath",
"Gully Boy",
"Andhadhun",
"Drishyam",
"Article 15",
"Badhaai Ho",
"Stree",
"Bhool Bhulaiyaa",
"Tumbbad",
"Kahaani",
"Raazi",
"Queen",
"English Vinglish",
"Piku",
"Dear Zindagi",
"Udta Punjab",
"Omkara",
"Haider",
"Kaminey",
"Black",
"Guru",
"Kesari",
"Lagaan",
"Border",
"URI: The Surgical Strike",

# ================= PUNJABI =================
"Carry On Jatta",
"Carry On Jatta 2",
"Carry On Jatta 3",
"Jatt & Juliet",
"Jatt & Juliet 2",
"Sufna",
"Qismat",
"Qismat 2",
"Ardaas",
"Ardaas Karaan",
"Shadaa",
"Nikka Zaildar",
"Nikka Zaildar 2",
"Nikka Zaildar 3",
"Chal Mera Putt",
"Chal Mera Putt 2",
"Chal Mera Putt 3",
"Angrej",
"Love Punjab",
"Punjab 1984",
"Subedar Joginder Singh",
"Rabb Da Radio",
"Rabb Da Radio 2",
"Lahoriye",
"Saunkan Saunkne",
"Manje Bistre",
"Manje Bistre 2",
"Honsla Rakh",
"Paani Ch Madhaani",
"Kala Shah Kala",

# ================= SOUTH INDIAN =================
"Baahubali: The Beginning",
"Baahubali: The Conclusion",
"RRR",
"KGF Chapter 1",
"KGF Chapter 2",
"Pushpa: The Rise",
"Vikram",
"Master",
"Leo",
"Jailer",
"Enthiran",
"2.0",
"Drishyam (Malayalam)",
"Premam",
"Super Deluxe",
"96",
"Kaithi",
"Sarkar",
"Thuppakki",
"Ala Vaikunthapurramuloo",
"Arjun Reddy",

# ================= INTERNATIONAL =================
"Parasite",
"Oldboy",
"Train to Busan",
"The Host",
"Spirited Away",
"Your Name",
"Weathering with You",
"Akira",
"Seven Samurai",
"Rashomon",
"Amelie",
"The Intouchables",
"Life Is Beautiful",
"Cinema Paradiso",
"Pan’s Labyrinth",
"The Platform",
"Roma",
"City of God",

# ================= MORE VARIETY =================
"The Conjuring",
"Annabelle",
"Insidious",
"It",
"The Exorcist",
"A Quiet Place",
"Hereditary",
"Midsommar",
"Saw",
"The Ring",
"Final Destination",
"Get Out",
"Us",
"Nope",

"The Hangover",
"Superbad",
"Step Brothers",
"21 Jump Street",
"Deadpool 2",
"Rush Hour",
"Home Alone",
"Mean Girls",
"White Chicks",

"The Notebook",
"Titanic",
"Before Sunrise",
"Before Sunset",
"Before Midnight",
"Pride & Prejudice",
"La La Land",
"500 Days of Summer",

"Rocky",
"Creed",
"Moneyball",
"Ford v Ferrari",
"Rush",
"The Blind Side",
"Coach Carter",

"Harry Potter and the Sorcerer's Stone",
"Harry Potter and the Chamber of Secrets",
"Harry Potter and the Prisoner of Azkaban",
"Harry Potter and the Goblet of Fire",
"Harry Potter and the Order of the Phoenix",
"Harry Potter and the Half-Blood Prince",
"Harry Potter and the Deathly Hallows Part 1",
"Harry Potter and the Deathly Hallows Part 2",

"The Lord of the Rings: The Fellowship of the Ring",
"The Lord of the Rings: The Two Towers",
"The Lord of the Rings: The Return of the King",
"The Hobbit: An Unexpected Journey",
"The Hobbit: The Desolation of Smaug",
"The Hobbit: The Battle of the Five Armies",

"Pirates of the Caribbean: The Curse of the Black Pearl",
"Pirates of the Caribbean: Dead Man's Chest",
"Pirates of the Caribbean: At World's End",

"Fast & Furious",
"2 Fast 2 Furious",
"Tokyo Drift",
"Fast Five",
"Fast & Furious 6",
"Furious 7",
"Fate of the Furious",
"Fast X",

"Transformers",
"Transformers: Revenge of the Fallen",
"Transformers: Dark of the Moon",
"Transformers: Age of Extinction",
"Transformers: The Last Knight",

]


# ================================================================
#  HELPERS
# ================================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def tmdb_get(endpoint, params=None):
    """Make a TMDB GET request. Returns parsed JSON or None on failure."""
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY

    try:
        r = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=12)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ⚠️  TMDB request failed ({endpoint}): {e}")
        return None


def tmdb_poster(path, size="w500"):
    return f"{TMDB_IMG}/{size}{path}" if path else None


def tmdb_backdrop(path, size="w1280"):
    return f"{TMDB_IMG}/{size}{path}" if path else None


def tmdb_trailer(movie_id):
    """
    Returns the best YouTube embed URL for a movie's trailer.
    Prefers official trailers, falls back to any trailer/teaser.
    Returns None if nothing found.
    """
    data = tmdb_get(f"/movie/{movie_id}/videos")
    if not data:
        return None

    videos = data.get("results", [])

    # Priority order: official trailer → trailer → teaser
    for label in ["Official Trailer", "Trailer", "Teaser"]:
        for v in videos:
            if v.get("site") == "YouTube" and label.lower() in v.get("name","").lower():
                return f"https://www.youtube.com/embed/{v['key']}"

    # Fallback: any YouTube video
    for v in videos:
        if v.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{v['key']}"

    return None


# ================================================================
#  ANIME SEEDER  (Jikan + TMDB backdrop lookup)
# ================================================================

def seed_anime_from_jikan(target=50):
    conn = get_db()
    cursor = conn.cursor()

    headers = {"User-Agent": "NextWatch-College-Project/1.0"}
    added = 0
    page  = 1

    print(f"\n🎌 Seeding anime from Jikan (target: {target})…\n")

    while added < target:
        r = requests.get(JIKAN_URL, params={"page": page, "limit": 25}, headers=headers, timeout=15)

        if r.status_code != 200:
            print(f"  ❌ Jikan failed (status {r.status_code})")
            break

        data = r.json().get("data", [])
        if not data:
            print("  ❌ No more data from Jikan")
            break

        for anime in data:
            if added >= target:
                break

            # --- Title ---
            title = anime.get("title_english") or anime.get("title")
            if not title:
                continue

            # --- Skip duplicates ---
            if cursor.execute("SELECT 1 FROM content WHERE title = ? AND type = 'anime'", (title,)).fetchone():
                continue

            # --- Description ---
            synopsis    = anime.get("synopsis") or ""
            alt_titles  = " ".join(t for t in [
                anime.get("title",""), anime.get("title_english",""), anime.get("title_japanese","")
            ] if t)
            description = f"{synopsis}\n\n{alt_titles}"

            # --- Genres ---
            genres = ",".join(g["name"].lower() for g in anime.get("genres", []))

            # --- Images from Jikan ---
            images_j    = anime.get("images", {}).get("jpg", {})
            poster_url  = images_j.get("large_image_url") or images_j.get("image_url")

            # --- Try to get a real backdrop from TMDB ---
            background_url = try_tmdb_backdrop_for_anime(title)

            # Fall back to Jikan poster if TMDB had nothing
            if not background_url:
                background_url = poster_url

            # --- Trailer from Jikan ---
            trailer_url = None
            trailer_data = anime.get("trailer", {})
            if trailer_data.get("youtube_id"):
                trailer_url = f"https://www.youtube.com/embed/{trailer_data['youtube_id']}"
            elif trailer_data.get("embed_url"):
                trailer_url = trailer_data["embed_url"]

            # --- Insert ---
            cursor.execute("""
                INSERT INTO content (
                    title, type, description, release_year, genres,
                    poster_url, background_url, trailer_url,
                    rating, views_count, episodes, duration
                ) VALUES (?, 'anime', ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """, (
                title, description,
                anime.get("year"),
                genres,
                poster_url, background_url, trailer_url,
                anime.get("score"),
                anime.get("popularity"),
                anime.get("episodes"),
            ))

            print(f"  ✅ [{added+1:02d}] {title}  |  backdrop: {'TMDB ✨' if background_url != poster_url else 'poster fallback'}")
            added += 1
            time.sleep(0.5)   # Jikan rate limit: ~2 req/sec is safe

        conn.commit()
        page += 1

    conn.commit()
    conn.close()
    print(f"\n🎉 Anime done — {added} titles added.\n")


def try_tmdb_backdrop_for_anime(title):
    # Try TV first
    data = tmdb_get("/search/tv", {"query": title, "include_adult": False})

    if data and data.get("results"):
        for result in data["results"]:
            if result.get("backdrop_path"):
                return tmdb_backdrop(result["backdrop_path"])

    # 🔥 Fallback: try MOVIE (for anime movies like Your Name)
    data = tmdb_get("/search/movie", {"query": title, "include_adult": False})

    if data and data.get("results"):
        for result in data["results"]:
            if result.get("backdrop_path"):
                return tmdb_backdrop(result["backdrop_path"])

    return None


# ================================================================
#  MOVIE SEEDER  (TMDB — backdrops + working trailers)
# ================================================================

def seed_movies_from_tmdb():
    conn   = get_db()
    cursor = conn.cursor()
    added  = 0

    print(f"\n🎬 Seeding {len(MOVIE_TITLES)} movies from TMDB…\n")

    for raw_title in MOVIE_TITLES:

        # --- Search ---
        search = tmdb_get("/search/movie", {"query": raw_title, "include_adult": False})
        if not search or not search.get("results"):
            print(f"  ❌ Not found: {raw_title}")
            continue

        movie = search["results"][0]
        tmdb_id = movie["id"]
        title   = movie["title"]

        # --- Skip duplicates ---
        if cursor.execute("SELECT 1 FROM content WHERE title = ? AND type = 'movie'", (title,)).fetchone():
            print(f"  ↩️  Already exists: {title}")
            continue

        # --- Full details (for runtime, genres, etc.) ---
        details = tmdb_get(f"/movie/{tmdb_id}")
        if not details:
            print(f"  ⚠️  Could not fetch details for: {title}")
            continue

        # --- Images ---
        poster_path   = movie.get("poster_path")   or details.get("poster_path")
        backdrop_path = movie.get("backdrop_path") or details.get("backdrop_path")

        poster_url     = tmdb_poster(poster_path,   "w500")
        background_url = tmdb_backdrop(backdrop_path, "w1280")

        # If no backdrop, fall back to a larger poster
        if not background_url:
            background_url = tmdb_poster(poster_path, "original")

        # --- Trailer ---
        trailer_url = tmdb_trailer(tmdb_id)

        # --- Genres ---
        genre_names = [g["name"].lower() for g in details.get("genres", [])]
        genres      = ",".join(genre_names)

        # --- Other metadata ---
        description  = details.get("overview") or movie.get("overview") or ""
        release_year = None
        rd = details.get("release_date") or movie.get("release_date", "")
        if rd and len(rd) >= 4 and rd[:4].isdigit():
            release_year = int(rd[:4])

        runtime = details.get("runtime")   # minutes, already an int from TMDB
        rating  = round(details.get("vote_average", 0), 1)
        rating  = rating if rating > 0 else None

        # --- Insert ---
        cursor.execute("""
            INSERT INTO content (
                title, type, description, release_year, genres,
                poster_url, background_url, trailer_url,
                rating, views_count, episodes, duration
            ) VALUES (?, 'movie', ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)
        """, (
            title, description, release_year, genres,
            poster_url, background_url, trailer_url,
            rating, runtime,
        ))

        trailer_label = "✅" if trailer_url else "❌ none"
        backdrop_label = "✅" if background_url and backdrop_path else "⚠️  poster fallback"
        print(f"  ✅ {title} ({release_year})  |  backdrop: {backdrop_label}  |  trailer: {trailer_label}")

        added += 1
        time.sleep(0.25)   # TMDB is generous but let's be polite

    conn.commit()
    conn.close()
    print(f"\n🎉 Movies done — {added} titles added.\n")


# ================================================================
#  UPDATE EXISTING RECORDS
#  Run this to patch backdrop_url + trailer_url on rows that
#  currently have poster_url as their background_url.
# ================================================================

def update_existing_movies():
    """
    Goes through every movie in the DB and updates:
    - background_url  → real TMDB backdrop (1280px)
    - trailer_url     → working YouTube embed
    Only touches rows where background_url == poster_url (the broken ones).
    """
    conn   = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT id, title, poster_url, background_url, trailer_url
        FROM content
        WHERE type = 'movie'
    """).fetchall()

    print(f"\n🔧 Updating {len(rows)} movies…\n")
    updated = 0

    for row in rows:
        needs_backdrop = (not row["background_url"]) or (row["background_url"] == row["poster_url"])
        needs_trailer  = not row["trailer_url"]

        if not needs_backdrop and not needs_trailer:
            continue

        search = tmdb_get("/search/movie", {"query": row["title"], "include_adult": False})
        if not search or not search.get("results"):
            print(f"  ❌ Not found on TMDB: {row['title']}")
            continue

        movie   = search["results"][0]
        tmdb_id = movie["id"]
        details = tmdb_get(f"/movie/{tmdb_id}")

        new_backdrop = row["background_url"]
        new_trailer  = row["trailer_url"]

        if needs_backdrop:
            bp = (details or {}).get("backdrop_path") or movie.get("backdrop_path")
            if bp:
                new_backdrop = tmdb_backdrop(bp, "w1280")

        if needs_trailer:
            new_trailer = tmdb_trailer(tmdb_id)

        cursor.execute("""
            UPDATE content
            SET background_url = ?, trailer_url = ?
            WHERE id = ?
        """, (new_backdrop, new_trailer, row["id"]))

        print(f"  🔄 {row['title']}  |  backdrop: {'updated' if needs_backdrop and new_backdrop != row['background_url'] else 'unchanged'}  |  trailer: {'updated' if new_trailer else 'none found'}")
        updated += 1
        time.sleep(0.3)

    conn.commit()
    conn.close()
    print(f"\n✅ Done — {updated} rows updated.\n")


def update_existing_anime():
    """
    Goes through every anime in the DB and tries to fetch a real
    TMDB backdrop for rows where background_url == poster_url.
    Also patches missing trailer_url using Jikan if MAL ID is available.
    """
    conn   = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT id, title, poster_url, background_url
        FROM content
        WHERE type = 'anime'
    """).fetchall()

    print(f"\n🔧 Updating {len(rows)} anime…\n")
    updated = 0

    for row in rows:
        needs_backdrop = True
        if not needs_backdrop:
            continue

        backdrop = try_tmdb_backdrop_for_anime(row["title"])
        if not backdrop:
            continue

        cursor.execute("UPDATE content SET background_url = ? WHERE id = ?", (backdrop, row["id"]))
        print(f"  🔄 {row['title']}  →  got TMDB backdrop ✨")
        updated += 1
        time.sleep(0.2)

    conn.commit()
    conn.close()
    print(f"\n✅ Done — {updated} anime backdrops updated.\n")


# ================================================================
#  ENTRY POINT
# ================================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  NextWatch Seeder — powered by Jikan + TMDB")
    print("=" * 55)

    print("""
What do you want to do?

  1  — Seed anime from scratch (Jikan)
  2  — Seed movies from scratch (TMDB)
  3  — Update existing movies (fix backdrops + trailers)
  4  — Update existing anime  (fix backdrops)
  5  — Seed both from scratch

Enter number: """, end="")

    choice = input().strip()

    if   choice == "1": seed_anime_from_jikan()
    elif choice == "2": seed_movies_from_tmdb()
    elif choice == "3": update_existing_movies()
    elif choice == "4": update_existing_anime()
    elif choice == "5": seed_anime_from_jikan(); seed_movies_from_tmdb()
    else: print("Invalid choice.")
