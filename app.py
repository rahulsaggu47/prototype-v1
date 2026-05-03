from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import threading
import urllib.request as _urllib  # stdlib — no extra dependency needed
from groq import Groq
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.db import (
    get_db,
    close_db,
    get_trending_content,
    get_popular_content,
    get_personalized_content,
    get_trending_by_genres,
    get_popular_by_genres,
    add_favorite,
    remove_favorite,
    get_user_favorites,
    save_user_genres,
    get_spotlight_content,
    get_top_rated,
    get_spotlight_map,
    get_admin_picks,
    get_user_by_id
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("app.secret_key")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_API_KEY)

# ================================================================
#  KEEP-ALIVE — pings /ping every 10 minutes so Render never sleeps
#  Set RENDER_EXTERNAL_URL in your Render environment variables,
#  e.g.  https://nextwatch-xxxx.onrender.com
# ================================================================
RENDER_EXTERNAL_URL = os.getenv("https://nextwatch-w3wi.onrender.com", "").rstrip("/")

def _keep_alive():
    import time
    while True:
        time.sleep(10 * 60)   # wait 10 minutes between pings
        if not RENDER_EXTERNAL_URL:
            continue
        try:
            resp = _urllib.urlopen(f"{RENDER_EXTERNAL_URL}/ping", timeout=10)
            print(f"[keep-alive] ping → {resp.status}")
        except Exception as exc:
            print(f"[keep-alive] ping failed: {exc}")

# Only start one thread — not in the Werkzeug reloader child process
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    _ka_thread = threading.Thread(target=_keep_alive, daemon=True)
    _ka_thread.start()

# ================================================================

NEXI_SYSTEM_PROMPT = """You are Nexi, the AI assistant for NextWatch — a personalized anime and movie discovery platform.

Your personality:
- Warm, enthusiastic, and genuinely knowledgeable about anime and movies
- Concise but helpful — no filler, no unnecessary disclaimers
- You feel like a friend who has watched everything, not a corporate chatbot
- Use light emoji occasionally to add energy, but not on every sentence
- Be opinionated when asked — actually recommend things rather than hedging

Your capabilities:
- Recommend anime and movies based on mood, genre, vibe, or specific preferences
- Help users discover hidden gems they would not find on their own
- Explain what a show or movie is about without spoilers unless asked
- Suggest what to watch next after finishing something
- Give honest takes on whether something is worth watching

About NextWatch:
- Users can save favorites, write reviews, and rate content
- The platform covers both anime and movies, filterable by genre, year, and rating
- Users can set preferred genres for personalized recommendations
- There is a Premium plan with mood-based discovery and advanced filters

Rules:
- ONLY discuss anime, movies, and NextWatch features. If asked about anything else, politely redirect.
- Never invent titles. If unsure something exists, say so.
- Keep responses short. 2-4 sentences for simple questions, a short paragraph for recommendations.
- When recommending, give 2-4 specific titles with a one-line reason for each. Do not list 10 things.
- If the user's genre preferences are in context, use them to personalize your response.
"""

def is_admin():
    return session.get("user_id") in [1, 30]

@app.context_processor
def inject_admin_flag():
    return {
        "is_admin": session.get("user_id") in [1, 30]
    }


@app.teardown_appcontext
def teardown_db(exception):
    close_db()

# ── Keep-alive ping endpoint ─────────────────────────────────────
@app.route("/ping")
def ping():
    return "pong", 200

# ── Admin ────────────────────────────────────────────────────────
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or not is_admin():
        return redirect("/login")
    return render_template("admin/dashboard.html")

@app.route("/admin/spotlight", methods=["GET", "POST"])
def admin_spotlight():
    if "user_id" not in session or not is_admin():
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        db.execute("DELETE FROM spotlight")

        for content_type in ["anime", "movie"]:
            for pos in [1, 2, 3]:
                cid = request.form.get(f"{content_type}_spotlight_{pos}")
                if cid:
                    db.execute("""
                        INSERT INTO spotlight (type, position, content_id)
                        VALUES (?, ?, ?)
                    """, (content_type, pos, cid))

        db.commit()
        return redirect("/admin/spotlight")

    content = db.execute("""
        SELECT id, title, type FROM content ORDER BY title
    """).fetchall()

    spotlight_rows = db.execute("""
        SELECT type, position, content_id FROM spotlight
    """).fetchall()

    spotlight_map = {
        (row["type"], row["position"]): row["content_id"]
        for row in spotlight_rows
    }

    return render_template(
        "admin/spotlight.html",
        content=content,
        spotlight_map=spotlight_map
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for("login"))

        except Exception:
            return render_template(
                "signup.html",
                error="Username already exists",
                username=username
            )

    return render_template("signup.html")

@app.route("/select-genres", methods=["GET", "POST"])
def select_genres():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    user = db.execute(
        "SELECT preferred_genres FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    is_editing = request.args.get("edit") == "1"

    if (
        user["preferred_genres"]
        and user["preferred_genres"].strip() != ""
        and not is_editing
    ):
        return redirect("/")

    error = None

    if user["preferred_genres"]:
        selected_genres = [
            g.strip() for g in user["preferred_genres"].split(",")
        ]
    else:
        selected_genres = []

    if request.method == "POST":
        selected_genres = request.form.getlist("genres")

        if len(selected_genres) < 3:
            error = "Please select at least 3 genres"
        else:
            save_user_genres(session["user_id"], selected_genres)
            session["preferences_saved"] = True
            return redirect("/")

    genres = [
        "Action", "Adventure", "Drama",
        "Comedy", "Fantasy", "Romance",
        "Sci-Fi", "Thriller", "Horror"
    ]

    return render_template(
        "select_genres.html",
        genres=genres,
        selected_genres=selected_genres,
        error=error
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if not user:
            return render_template("login.html", error="Invalid Username")

        if not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid Password")

        session["user_id"] = user["id"]

        next_page = session.pop("next", None)
        if next_page:
            return redirect(next_page)

        if not user["preferred_genres"] or user["preferred_genres"].strip() == "":
            return redirect("/select-genres")

        preferred = user["preferred_world"]

        if preferred:
            return redirect(f"/{preferred}")

        return redirect("/welcome")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/welcome")

SPOTLIGHT_VIDEO_MAP = {
    202:"/static/videos/frieren.mp4",
    203: "/static/videos/frieren_s2.mp4",
    204: "/static/videos/chainsaw_man.mp4",
    403: "/static/videos/dhurandhar.mp4",
    234: "/static/videos/your_namr.mp4",
    265: "/static/videos/jjk_s2.mp4",
    292: "/static/videos/jjk_s3.mp4",
    402: "/static/videos/3_idiots.mp4",
    254: "/static/videos/love_is_war_movie.mp4",
    469: "/static/videos/tangled.mp4",
    614: "/static/videos/cmp.mp4",
    1707: "/static/videos/phm.mp4",
    513: "/static/videos/thor.mp4"
}


@app.route("/api/spotlight")
def api_spotlight():
    content_type = request.args.get("type", "anime")
    spotlight_items = get_spotlight_content(content_type)

    result = []
    for row in spotlight_items:
        item = dict(row)
        item["video_url"] = SPOTLIGHT_VIDEO_MAP.get(item["id"])
        result.append(item)

    return jsonify(result)


@app.route("/api/content")
def api_content():
    content_type = request.args.get("type", "anime")
    genre_param = request.args.get("genres")
    search = request.args.get("q")
    year = request.args.get("year")
    rating = request.args.get("rating")
    sort = request.args.get("sort", "rating_desc")

    db = get_db()

    query = "SELECT * FROM content WHERE type = ?"
    params = [content_type]

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    year_start = request.args.get("year_start")
    year_end = request.args.get("year_end")

    if year_start and year_end:
        query += " AND release_year BETWEEN ? AND ?"
        params.append(int(year_start))
        params.append(int(year_end))

    if rating:
        query += " AND rating >= ?"
        params.append(float(rating))

    if genre_param:
        genres = genre_param.split(",")
        for g in genres:
            query += " AND genres LIKE ?"
            params.append(f"%{g}%")

    if sort == "rating_desc":
        query += " ORDER BY rating DESC"
    elif sort == "rating_asc":
        query += " ORDER BY rating ASC"
    elif sort == "popular":
        query += " ORDER BY views_count DESC"
    else:
        query += " ORDER BY rating DESC"

    results = db.execute(query, params).fetchall()
    return jsonify([dict(row) for row in results])

@app.route("/favorites")
def favorites_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("favorites.html")


@app.route("/api/favorites/add", methods=["POST"])
def api_add_favorite():
    user_id = session.get("user_id")
    data = request.json
    content_id = data.get("content_id")

    if not user_id:
        return jsonify({"login_required": True}), 401

    if not content_id:
        return jsonify({"error": "Missing content_id"}), 400

    add_favorite(user_id, content_id)
    return jsonify({"success": True})


@app.route("/api/favorites/remove", methods=["POST"])
def api_remove_favorite():
    user_id = session.get("user_id")
    data = request.json
    content_id = data.get("content_id")

    if not user_id:
        return jsonify({"login_required": True}), 401

    if not content_id:
        return jsonify({"error": "Missing content_id"}), 400

    remove_favorite(user_id, content_id)
    return jsonify({"success": True})


@app.route("/api/favorites/status/<int:content_id>")
def api_favorite_status(content_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"is_favorite": False})

    db = get_db()
    fav = db.execute(
        "SELECT 1 FROM favorites WHERE user_id = ? AND content_id = ?",
        (user_id, content_id)
    ).fetchone()

    return jsonify({"is_favorite": bool(fav)})


@app.route("/api/favorites")
def api_get_favorites():
    user_id = session.get("user_id")
    content_type = request.args.get("type")

    if not user_id:
        return jsonify({"login_required": True}), 401

    favorites = get_user_favorites(user_id, content_type)
    return jsonify([dict(row) for row in favorites])


@app.route("/")
def home():
    if "user_id" not in session and not request.args.get("type"):
        return redirect("/welcome")

    db = get_db()
    content_type = request.args.get("type")

    if "user_id" in session:
        user = db.execute(
            "SELECT preferred_world FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if not content_type:
            content_type = user["preferred_world"] if user and user["preferred_world"] else "anime"
    else:
        if not content_type:
            content_type = "anime"

    trending = get_trending_by_genres(content_type)
    popular = get_popular_by_genres(content_type)
    top_rated = get_top_rated(content_type)

    show_toast = session.pop("preferences_saved", None)

    return render_template(
        "home.html",
        trending=trending,
        popular=popular,
        top_rated=top_rated,
        content_type=content_type,
        show_toast=show_toast
    )

@app.route("/anime")
def anime_home():
    content_type = "anime"
    trending = get_trending_by_genres(content_type)
    popular = get_popular_by_genres(content_type)
    top_rated = get_top_rated(content_type)
    show_toast = session.pop("preferences_saved", None)

    return render_template(
        "home.html",
        trending=trending,
        popular=popular,
        top_rated=top_rated,
        content_type=content_type,
        show_toast=show_toast
    )


@app.route("/movie")
def movie_home():
    content_type = "movie"
    trending = get_trending_by_genres(content_type)
    popular = get_popular_by_genres(content_type)
    top_rated = get_top_rated(content_type)
    show_toast = session.pop("preferences_saved", None)

    return render_template(
        "home.html",
        trending=trending,
        popular=popular,
        top_rated=top_rated,
        content_type=content_type,
        show_toast=show_toast
    )

@app.route("/set-world/<world>")
def set_world(world):
    if "user_id" in session:
        db = get_db()
        db.execute(
            "UPDATE users SET preferred_world = ? WHERE id = ?",
            (world, session["user_id"])
        )
        db.commit()
        session["preferences_saved"] = True

    return redirect(f"/?type={world}")


@app.route("/content/<int:content_id>")
def content_detail(content_id):
    db = get_db()

    content = db.execute(
        "SELECT * FROM content WHERE id = ?",
        (content_id,)
    ).fetchone()

    if content is None:
        return "Content not found", 404

    return render_template("detail.html", content=content)

@app.route("/api/related/<int:content_id>")
def api_related(content_id):
    db = get_db()

    source = db.execute(
        "SELECT type, genres FROM content WHERE id = ?",
        (content_id,)
    ).fetchone()

    if not source or not source["genres"]:
        rows = db.execute("""
            SELECT * FROM content
            WHERE type = (SELECT type FROM content WHERE id = ?)
            AND id != ?
            ORDER BY rating DESC
            LIMIT 12
        """, (content_id, content_id)).fetchall()
        return jsonify([dict(r) for r in rows])

    genres = [g.strip() for g in source["genres"].split(",") if g.strip()]
    content_type = source["type"]

    if not genres:
        return jsonify([])

    score_expr = " + ".join(
        [f"CASE WHEN genres LIKE '%{g}%' THEN 1 ELSE 0 END" for g in genres]
    )

    rows = db.execute(f"""
        SELECT *,
               ({score_expr}) AS match_score
        FROM content
        WHERE type = ?
          AND id != ?
          AND ({score_expr}) > 0
        ORDER BY match_score DESC, rating DESC
        LIMIT 12
    """, (content_type, content_id)).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route("/api/recommend")
def api_recommend():
    genres = request.args.get("genres", "").split(",")
    content_type = request.args.get("type", "anime")

    db = get_db()

    query = """
        SELECT * FROM content
        WHERE genres LIKE ?
    """

    params = [f"%{genres[0]}%"]

    if content_type != "both":
        query += " AND type = ?"
        params.append(content_type)

    query += " ORDER BY RANDOM() LIMIT 1"

    result = db.execute(query, params).fetchall()
    return jsonify([dict(r) for r in result])

@app.route("/api/recommended")
def api_recommended():
    user_id = session.get("user_id")
    content_type = request.args.get("type", "anime")

    if not user_id:
        return jsonify({"items": [], "reason": None, "all_genres": []})

    db = get_db()

    user = db.execute(
        "SELECT preferred_genres FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user or not user["preferred_genres"]:
        return jsonify({"items": [], "reason": None, "all_genres": []})

    preferred_genres = [
        g.strip() for g in user["preferred_genres"].split(",")
    ]

    genre_conditions = " OR ".join(["c.genres LIKE ?"] * len(preferred_genres))
    genre_params = [f"%{g}%" for g in preferred_genres]

    results = db.execute(f"""
        SELECT c.*
        FROM content c
        WHERE c.type = ?
        AND ({genre_conditions})
        AND c.id NOT IN (
            SELECT content_id
            FROM favorites
            WHERE user_id = ?
        )
        ORDER BY RANDOM()
        LIMIT 10
    """, [content_type, *genre_params, user_id]).fetchall()

    reason = "Because you like " + ", ".join(preferred_genres[:3])

    return jsonify({
        "items": [dict(row) for row in results],
        "reason": reason,
        "all_genres": preferred_genres
    })


@app.route("/api/because-you-liked")
def because_you_liked():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"items": []})

    db = get_db()
    content_type = request.args.get("type")

    source = db.execute("""
        SELECT c.id, c.title, c.genres, c.type
        FROM content c
        JOIN favorites f ON c.id = f.content_id
        WHERE f.user_id = ?
        AND c.type = ?
        ORDER BY RANDOM()
        LIMIT 1
    """, (user_id, content_type)).fetchone()

    source_type = "favorite"

    if not source:
        source = db.execute("""
            SELECT c.id, c.title, c.genres, c.type
            FROM content c
            JOIN reviews r ON c.id = r.content_id
            WHERE r.user_id = ?
            AND r.rating >= 4
            AND c.type = ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (user_id, content_type)).fetchone()
        source_type = "review"

    if not source:
        return jsonify({"items": []})

    genres = [g.strip() for g in source["genres"].split(",")]

    query = """
        SELECT *
        FROM content
        WHERE type = ?
        AND id != ?
        AND id NOT IN (
            SELECT content_id FROM favorites WHERE user_id = ?
        )
        AND id NOT IN (
            SELECT content_id FROM reviews WHERE user_id = ?
        )
        AND (
    """

    params = [source["type"], source["id"], user_id, user_id]

    genre_conditions = []
    for g in genres:
        genre_conditions.append("genres LIKE ?")
        params.append(f"%{g}%")

    query += " OR ".join(genre_conditions)
    query += ") ORDER BY RANDOM() LIMIT 10"

    items = db.execute(query, params).fetchall()

    if not items:
        items = db.execute("""
            SELECT *
            FROM content
            WHERE type = ?
            AND id != ?
            ORDER BY RANDOM()
            LIMIT 10
        """, (source["type"], source["id"])).fetchall()

    return jsonify({
        "source_title": source["title"],
        "source_type": source_type,
        "items": [dict(i) for i in items]
    })


@app.route("/api/out-of-comfort/<content_type>")
def out_of_comfort(content_type):
    if "user_id" not in session:
        return jsonify({"items": [], "user_genres": []})

    db = get_db()
    user_id = session["user_id"]

    user = db.execute(
        "SELECT preferred_genres FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user or not user["preferred_genres"]:
        return jsonify({"items": [], "user_genres": []})

    user_genres = [
        g.strip() for g in user["preferred_genres"].split(",")
    ]

    genre_conditions = " AND ".join(["c.genres NOT LIKE ?"] * len(user_genres))
    genre_params = [f"%{g}%" for g in user_genres]

    results = db.execute(f"""
        SELECT c.*
        FROM content c
        WHERE c.type = ?
        AND ({genre_conditions})
        AND c.id NOT IN (
            SELECT content_id FROM favorites WHERE user_id = ?
        )
        AND c.id NOT IN (
            SELECT content_id FROM reviews WHERE user_id = ?
        )
        ORDER BY RANDOM()
        LIMIT 10
    """, [content_type, *genre_params, user_id, user_id]).fetchall()

    return jsonify({
        "items": [dict(row) for row in results],
        "user_genres": user_genres
    })


@app.route("/api/admin-picks")
def api_admin_picks():
    admin_name = request.args.get("admin")
    content_type = request.args.get("type")

    if not admin_name or not content_type:
        return jsonify([])

    items = get_admin_picks(admin_name, content_type)
    return jsonify([dict(row) for row in items])


@app.route("/admin/picks", methods=["GET", "POST"])
def admin_picks():
    if "user_id" not in session or not is_admin():
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        db.execute("DELETE FROM admins_picks")

        for admin_name in ["fate", "akriti"]:
            for content_type in ["anime", "movie"]:
                for pos in range(1, 11):
                    cid = request.form.get(f"{admin_name}_{content_type}_{pos}")
                    if cid:
                        db.execute("""
                            INSERT INTO admins_picks (admin_name, type, position, content_id)
                            VALUES (?, ?, ?, ?)
                        """, (admin_name, content_type, pos, cid))

        db.commit()
        return redirect("/admin/picks")

    content = db.execute("""
        SELECT id, title, type FROM content ORDER BY title
    """).fetchall()

    picks = db.execute("""
        SELECT admin_name, type, position, content_id FROM admins_picks
    """).fetchall()

    picks_map = {
        (row["admin_name"], row["type"], row["position"]): row["content_id"]
        for row in picks
    }

    return render_template(
        "admin/picks.html",
        content=content,
        picks_map=picks_map
    )


@app.route("/api/reviews/<int:content_id>")
def get_reviews(content_id):
    sort = request.args.get("sort", "newest")
    order_clause = "r.created_at DESC"

    if sort == "highest":
        order_clause = "r.rating DESC"
    elif sort == "lowest":
        order_clause = "r.rating ASC"

    db = get_db()

    rows = db.execute(f"""
        SELECT r.*,
               u.username,
               u.avatar_type,
               u.avatar_value
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.content_id = ?
        ORDER BY {order_clause}
    """, (content_id,)).fetchall()

    return jsonify([dict(row) for row in rows])

@app.route("/edit-review/<int:review_id>", methods=["POST"])
def edit_review(review_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    db = get_db()
    review = db.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()

    if not review or review["user_id"] != session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json
    db.execute("""
        UPDATE reviews SET comment = ?, rating = ? WHERE id = ?
    """, (data["comment"], data["rating"], review_id))
    db.commit()

    return jsonify({"success": True})

@app.route("/delete-review/<int:review_id>", methods=["POST"])
def delete_review(review_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    db = get_db()
    review = db.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()

    if not review or review["user_id"] != session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    db.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    db.commit()

    return jsonify({"success": True})

@app.route("/add-review", methods=["POST"])
def add_review():
    if "user_id" not in session:
        return jsonify({"error": "login required"}), 401

    data = request.json
    db = get_db()

    db.execute("""
        INSERT INTO reviews (user_id, content_id, rating, comment)
        VALUES (?, ?, ?, ?)
    """, (
        session["user_id"],
        data["content_id"],
        data["rating"],
        data["comment"]
    ))

    db.commit()
    return jsonify({"success": True})


@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        return dict(user=user)
    return dict(user=None)

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    show_toast = session.pop("preferences_saved", None)

    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    favorites = db.execute("""
        SELECT c.id, c.title, c.poster_url
        FROM favorites f
        JOIN content c ON f.content_id = c.id
        WHERE f.user_id = ?
        ORDER BY f.id DESC
    """, (session["user_id"],)).fetchall()

    reviews = db.execute("""
        SELECT r.*, c.title, c.poster_url, c.type
        FROM reviews r
        JOIN content c ON r.content_id = c.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """, (session["user_id"],)).fetchall()

    top_rated = db.execute("""
        SELECT c.id as content_id, c.title, c.poster_url, r.rating
        FROM reviews r
        JOIN content c ON r.content_id = c.id
        WHERE r.user_id = ?
        ORDER BY r.rating DESC, r.created_at DESC
        LIMIT 6
    """, (session["user_id"],)).fetchall()

    return render_template(
        "profile.html",
        user=user,
        favorites=favorites,
        reviews=reviews,
        top_rated=top_rated,
        show_toast=show_toast
    )

@app.route("/set-avatar", methods=["POST"])
def set_avatar():
    if "user_id" not in session:
        return {"success": False}, 403

    avatar_name = request.json.get("avatar")
    db = get_db()
    db.execute(
        "UPDATE users SET avatar_type = ?, avatar_value = ? WHERE id = ?",
        ("default", avatar_name, session["user_id"])
    )
    db.commit()
    db.close()
    return {"success": True}


UPLOAD_FOLDER = "static/uploads/avatars"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload-avatar", methods=["POST"])
def upload_avatar():
    if "user_id" not in session:
        return {"success": False}, 403

    if "avatar" not in request.files:
        return {"success": False, "error": "No file provided"}

    file = request.files["avatar"]

    if file.filename == "":
        return {"success": False, "error": "Empty filename"}

    if file and allowed_file(file.filename):
        filename = f"user_{session['user_id']}.png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        db = get_db()
        db.execute(
            "UPDATE users SET avatar_type = ?, avatar_value = ? WHERE id = ?",
            ("custom", f"uploads/avatars/{filename}", session["user_id"])
        )
        db.commit()
        db.close()

        return {"success": True}

    return {"success": False, "error": "Invalid file type"}

@app.route("/welcome")
def welcome():
    if request.args.get("type"):
        return redirect(f"/?type={request.args.get('type')}")
    return render_template("welcome.html")


@app.route("/upgrade/<plan>")
def upgrade(plan):
    user_id = session.get("user_id")

    if not user_id:
        session["next"] = request.path
        return redirect("/login")

    if not session.get("payment_done"):
        return redirect(f"/payment?plan={plan}")

    session.pop("payment_done", None)

    db = get_db()
    cursor = db.cursor()

    if plan == "monthly":
        expiry = datetime.now() + timedelta(days=30)
    else:
        expiry = datetime.now() + timedelta(days=365)

    cursor.execute("""
        UPDATE users
        SET is_premium = 1, premium_type = ?, premium_expiry = ?
        WHERE id = ?
    """, (plan, expiry.strftime("%Y-%m-%d %H:%M:%S"), user_id))

    db.commit()
    db.close()

    return redirect("/")


@app.route("/premium")
def premium_page():
    user_id = session.get("user_id")

    if not user_id:
        session["next"] = request.full_path
        return redirect("/login")

    plan = request.args.get("plan", "monthly")
    return render_template("premium.html", selected_plan=plan, razorpay_key_id=os.getenv("RAZORPAY_KEY_ID"))

@app.route("/payment")
def payment():
    user_id = session.get("user_id")

    if not user_id:
        session["next"] = request.full_path
        return redirect("/login")

    plan = request.args.get("plan", "monthly")
    return render_template("payment.html", plan=plan)


import razorpay

client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

@app.route("/create-order/<plan>")
def create_order(plan):
    amount = 4900 if plan == "monthly" else 39900

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return {"order_id": order["id"], "amount": amount}

@app.route("/payment-success/<plan>")
def payment_success(plan):
    session["payment_done"] = True
    return redirect(f"/upgrade/{plan}")

@app.route("/cancel-membership")
def cancel_membership():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    db = get_db()
    db.execute("""
        UPDATE users SET is_premium = 0, premium_type = NULL, premium_expiry = NULL WHERE id = ?
    """, (user_id,))
    db.commit()

    return redirect("/profile")


@app.route("/api/nexi", methods=["POST"])
def nexi_chat():
    data    = request.json or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "Empty message"}), 400

    context_note = ""
    user_id = session.get("user_id")
    if user_id:
        db   = get_db()
        user = db.execute(
            "SELECT username, preferred_genres FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if user:
            if user["preferred_genres"]:
                genres = ", ".join(g.strip() for g in user["preferred_genres"].split(","))
                context_note = (
                    f"\n\n[Context: This user's name is {user['username']}. "
                    f"Their preferred genres on NextWatch are: {genres}. "
                    f"Use this when making recommendations.]"
                )
            else:
                context_note = (
                    f"\n\n[Context: This user's name is {user['username']}. "
                    f"They have not set genre preferences yet.]"
                )

    messages = [
        {"role": "system", "content": NEXI_SYSTEM_PROMPT + context_note},
        *history[-10:],
        {"role": "user", "content": message},
    ]

    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.75,
            max_tokens=400,
            top_p=0.9,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return jsonify({
            "reply": "I am having a bit of trouble connecting right now. Try again in a moment! 🔧"
        })

    try:
        db = get_db()
        db.execute(
            "INSERT INTO chatbot_logs (user_id, user_message, bot_response) VALUES (?, ?, ?)",
            (user_id, message, reply)
        )
        db.commit()
    except Exception as e:
        print(f"Chat log error: {e}")

    return jsonify({"reply": reply})


@app.route("/admin/chat-logs")
def admin_chat_logs():
    if "user_id" not in session or not is_admin():
        return redirect("/login")
    db   = get_db()
    logs = db.execute("""
        SELECT cl.*, u.username
        FROM chatbot_logs cl
        LEFT JOIN users u ON cl.user_id = u.id
        ORDER BY cl.timestamp DESC
        LIMIT 200
    """).fetchall()
    return render_template("admin/chat_logs.html", logs=logs)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
