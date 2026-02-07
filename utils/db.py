import sqlite3
from flask import g

DATABASE = "database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_trending_content(content_type, limit=10):
    db = get_db()
    query = """
        SELECT * FROM content
        WHERE type = ?
        ORDER BY views_count DESC
        LIMIT ?
    """
    return db.execute(query, (content_type, limit)).fetchall()


def get_popular_content(content_type, limit=10):
    db = get_db()
    query = """
        SELECT * FROM content
        WHERE type = ?
        ORDER BY rating DESC
        LIMIT ?
    """
    return db.execute(query, (content_type, limit)).fetchall()


def get_personalized_content(user_id, content_type, limit=10):
    db = get_db()

    # get user's preferred genres
    genres = db.execute(
        "SELECT genre FROM user_genres WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    if not genres:
        return []

    genre_conditions = " OR ".join(
        ["genres LIKE ?" for _ in genres]
    )
    genre_values = [f"%{g['genre']}%" for g in genres]

    query = f"""
        SELECT * FROM content
        WHERE type = ?
        AND ({genre_conditions})
        ORDER BY rating DESC
        LIMIT ?
    """

    return db.execute(
        query,
        [content_type] + genre_values + [limit]
    ).fetchall()


def get_trending_by_genres(content_type, genres=None, limit=10):
    db = get_db()

    base_query = """
        SELECT * FROM content
        WHERE type = ?
    """
    params = [content_type]

    if genres:
        conditions = " OR ".join(["genres LIKE ?" for _ in genres])
        base_query += f" AND ({conditions})"
        params.extend([f"%{g}%" for g in genres])

    base_query += " ORDER BY views_count DESC LIMIT ?"
    params.append(limit)

    return db.execute(base_query, params).fetchall()


def get_popular_by_genres(content_type, genres=None, limit=10):
    db = get_db()

    base_query = """
        SELECT * FROM content
        WHERE type = ?
    """
    params = [content_type]

    if genres:
        conditions = " OR ".join(["genres LIKE ?" for _ in genres])
        base_query += f" AND ({conditions})"
        params.extend([f"%{g}%" for g in genres])

    base_query += " ORDER BY rating DESC LIMIT ?"
    params.append(limit)

    return db.execute(base_query, params).fetchall()


def add_favorite(user_id, content_id):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO favorites (user_id, content_id) VALUES (?, ?)",
            (user_id, content_id)
        )
        db.commit()
        return True
    except Exception:
        return False


def remove_favorite(user_id, content_id):
    db = get_db()
    db.execute(
        "DELETE FROM favorites WHERE user_id = ? AND content_id = ?",
        (user_id, content_id)
    )
    db.commit()
    return True


def get_user_favorites(user_id, content_type=None):
    db = get_db()

    query = """
        SELECT c.*
        FROM content c
        JOIN favorites f ON c.id = f.content_id
        WHERE f.user_id = ?
    """
    params = [user_id]

    if content_type:
        query += " AND c.type = ?"
        params.append(content_type)

    return db.execute(query, params).fetchall()

def save_user_genres(user_id, genres):
    db = get_db()
    genres_str = ",".join(genres)

    db.execute(
        "UPDATE users SET preferred_genres = ? WHERE id = ?",
        (genres_str, user_id)
    )
    db.commit()

def get_spotlight_content(content_type, limit=3):
    db = get_db()

    # 1️⃣ Try admin-defined spotlight first
    rows = db.execute("""
        SELECT c.id, c.title, c.description, c.poster_url, c.background_url
        FROM spotlight s
        JOIN content c ON c.id = s.content_id
        WHERE c.type = ?
        ORDER BY s.position
        LIMIT ?
    """, (content_type, limit)).fetchall()

    # 2️⃣ Fallback: rating-based spotlight (your old logic)
    if not rows:
        rows = db.execute("""
            SELECT id, title, description, poster_url, background_url
            FROM content
            WHERE type = ?
            ORDER BY rating DESC
            LIMIT ?
        """, (content_type, limit)).fetchall()

    return rows


def get_spotlight_map():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT position, content_id FROM spotlight")
    return {row["position"]: row["content_id"] for row in cur.fetchall()}
