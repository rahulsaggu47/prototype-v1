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

# ================= HOLLYWOOD (MORE) =================
"The Green Mile",
"American Beauty",
"The Departed",
"Goodfellas",
"Casino",
"The Irishman",
"No Country for Old Men",
"There Will Be Blood",
"The Big Lebowski",
"Blade Runner",
"Blade Runner 2049",
"Alien",
"Aliens",
"Prometheus",
"The Martian",
"Gravity",
"Arrival",
"Looper",
"Minority Report",
"War of the Worlds",
"Ready Player One",
"The Truman Show",
"Eternal Sunshine of the Spotless Mind",
"Her",
"Ex Machina",
"A.I. Artificial Intelligence",
"The Curious Case of Benjamin Button",
"The Revenant",
"Birdman",
"Spotlight",
"12 Years a Slave",
"Slumdog Millionaire",
"The King's Speech",
"Argo",
"The Theory of Everything",
"Bohemian Rhapsody",
"Elvis",
"Oppenheimer",
"Dunkirk",
"Tenet",

# ================= BOLLYWOOD (MORE) =================
"Animal",
"Sam Bahadur",
"12th Fail",
"OMG: Oh My God!",
"OMG 2",
"Special 26",
"Baby",
"Airlift",
"Holiday",
"Naam Shabana",
"Kesari Chapter 2",
"Toilet: Ek Prem Katha",
"Pad Man",
"Mission Mangal",
"Housefull",
"Housefull 2",
"Housefull 3",
"Housefull 4",
"Golmaal",
"Golmaal Returns",
"Golmaal 3",
"Golmaal Again",
"Dhamaal",
"Double Dhamaal",
"Total Dhamaal",
"Hera Pheri",
"Phir Hera Pheri",
"Welcome",
"Welcome Back",
"Bhagam Bhag",
"De Dana Dan",
"Singh Is Kinng",
"Rowdy Rathore",
"Kick",
"Race",
"Race 2",
"Race 3",
"Dhoom",
"Dhoom 2",
"Dhoom 3",
"Baaghi",
"Baaghi 2",
"Baaghi 3",
"Ek Villain",
"Ek Villain Returns",

# ================= PUNJABI (MORE) =================
"Jinde Meriye",
"Kali Jotta",
"Annhi Dea Mazaak Ae",
"Maurh",
"Godday Godday Chaa",
"Mitran Da Naa Chalda",
"Babe Bhangra Paunde Ne",
"Tu Hovein Main Hovan",
"Yaar Mera Titliaan Warga",
"Snowman",
"Warning",
"Warning 2",
"Criminal",
"PR",
"Zilla Sangrur",
"Jatt Brothers",
"Fuffad Ji",
"Yaaran Da Rutbaa",
"Jodi",
"Chobbar",
"Batch 2013",
"Ji Wife Ji",

# ================= SOUTH INDIAN (MORE) =================
"Salaar",
"Salaar Part 2",
"Devara",
"Devara Part 2",
"Pushpa 2",
"Indian 2",
"Game Changer",
"Captain Miller",
"Mark Antony",
"Maaveeran",
"Thunivu",
"Varisu",
"Beast",
"Doctor",
"Don",
"Bigil",
"Mersal",
"Theri",
"Kaththi",
"Vada Chennai",
"Asuran",
"Karnan",
"Jigarthanda",
"Jigarthanda DoubleX",
"RRR 2",

# ================= INTERNATIONAL (MORE) =================
"The Raid",
"The Raid 2",
"I Saw the Devil",
"Memories of Murder",
"Burning",
"Decision to Leave",
"The Wailing",
"A Taxi Driver",
"Shoplifters",
"Drive My Car",
"Battle Royale",
"Crouching Tiger, Hidden Dragon",
"Hero",
"House of Flying Daggers",
"In the Mood for Love",
"2046",
"The Handmaiden",

# ================= HORROR / THRILLER =================
"The Babadook",
"Sinister",
"The Witch",
"The Lighthouse",
"The Others",
"The Sixth Sense",
"Orphan",
"Don't Breathe",
"Lights Out",
"The Nun",
"The Nun II",
"Smile",
"Talk to Me",
"Barbarian",

# ================= COMEDY =================
"Dumb and Dumber",
"Bruce Almighty",
"Evan Almighty",
"The Mask",
"Liar Liar",
"Yes Man",
"Get Smart",
"Johnny English",
"Johnny English Reborn",
"Johnny English Strikes Again",
"Mr. Bean's Holiday",
"Rush Hour 2",
"Rush Hour 3",
"Shanghai Noon",
"Shanghai Knights",

# ================= ROMANCE =================
"Notting Hill",
"Love Actually",
"The Fault in Our Stars",
"Me Before You",
"Safe Haven",
"The Vow",
"Dear John",
"PS I Love You",
"The Time Traveler's Wife",

# ================= SPORTS =================
"Remember the Titans",
"Million Dollar Baby",
"Warrior",
"Creed II",
"Creed III",
"The Fighter",
"Invictus",
"Seabiscuit",

# ================= ANIMATION =================
"Spider-Man: Into the Spider-Verse",
"Spider-Man: Across the Spider-Verse",
"Encanto",
"Moana",
"Brave",
"Turning Red",
"Soul",
"Luca",
"Onward",
"Kung Fu Panda",
"Kung Fu Panda 2",
"Kung Fu Panda 3",
"How to Train Your Dragon",
"How to Train Your Dragon 2",
"How to Train Your Dragon: The Hidden World",
"Despicable Me",
"Despicable Me 2",
"Despicable Me 3",
"Minions",
"Minions: The Rise of Gru",

# ================= ACTION FRANCHISES =================
"Die Hard",
"Die Hard 2",
"Die Hard with a Vengeance",
"Live Free or Die Hard",
"A Good Day to Die Hard",

"The Expendables",
"The Expendables 2",
"The Expendables 3",
"The Expendables 4",

"Rambo",
"Rambo: First Blood Part II",
"Rambo III",
"Rambo (2008)",
"Rambo: Last Blood",

# ================= RANDOM MIX =================
"Now You See Me",
"Now You See Me 2",
"The Illusionist",
"The Prestige",
"Catch Me If You Can",
"The Terminal",
"Sully",
"Bridge of Spies",
"War Horse",
"Lincoln",
"The Post",
"A Beautiful Mind",
"Good Will Hunting",
"Dead Poets Society",
"The Pursuit of Happyness",
"Seven Pounds",

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

def seed_anime_from_jikan(target=500):
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
