from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
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
<<<<<<< HEAD
    get_top_rated
=======
    get_spotlight_map
>>>>>>> baa7bcc0cf4863320b528826635a0195193d3d5f
)


app = Flask(__name__)
app.secret_key = "dev-secret-key"

def is_admin():
    return session.get("user_id") in [1, 25]

@app.context_processor
def inject_admin_flag():
    return {
        "is_admin": session.get("user_id") in [1, 25]
    }


@app.teardown_appcontext
def teardown_db(exception):
    close_db()
    
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
        except Exception:
            return "Username already exists"

        # redirect to login after successful signup
        return redirect(url_for("login"))

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

    # ✅ PRE-FILL SELECTED GENRES (KEY FIX)
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
            return render_template("login.html", error="Invalid credentials")

        if not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid credentials")

        # ✅ LOGIN SUCCESS
        session["user_id"] = user["id"]

        # 🔥 STEP 3 IS EXACTLY THIS CHECK
        if not user["preferred_genres"] or user["preferred_genres"].strip() == "":
            return redirect("/select-genres")


        return redirect("/")

    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

SPOTLIGHT_VIDEO_MAP = {
    202:"/static/videos/frieren.mp4",
    203: "/static/videos/frieren_s2.mp4",
    204: "/static/videos/chainsaw_man.mp4",
    403: "/static/videos/dhurandhar.mp4",
    234: "/static/videos/your_namr.mp4",
    461: "/static/videos/shangchi.mp4",
    265: "/static/videos/jjk_s2.mp4",
    402: "/static/videos/3_idiots.mp4",
}


@app.route("/api/spotlight")
def api_spotlight():
    content_type = request.args.get("type", "anime")

    spotlight_items = get_spotlight_content(content_type)

    result = []
    for row in spotlight_items:
        item = dict(row)

        # 🎬 attach video if available
        item["video_url"] = SPOTLIGHT_VIDEO_MAP.get(item["id"])

        result.append(item)

    return jsonify(result)



@app.route("/api/content")
def api_content():
    content_type = request.args.get("type", "anime")
    genre_param = request.args.get("genres")
    search = request.args.get("q")   # 👈 NEW
    sort = request.args.get("sort", "trending")

    db = get_db()

    query = "SELECT * FROM content WHERE type = ?"
    params = [content_type]

    # 🔍 SEARCH FILTER
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    # 🎭 GENRE FILTER
    if genre_param:
        genres = genre_param.split(",")
        for g in genres:
            query += " AND genres LIKE ?"
            params.append(f"%{g}%")

    # 🔥 SORT
    if sort == "popular":
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
    content_type = request.args.get("type")  # anime / movie / all

    if not user_id:
        return jsonify({"login_required": True}), 401

    favorites = get_user_favorites(user_id, content_type)
    return jsonify([dict(row) for row in favorites])



@app.route("/")
def home():
    content_type = request.args.get("type", "anime")

    trending = get_trending_by_genres(content_type)
    popular = get_popular_by_genres(content_type)
    top_rated = get_top_rated(content_type)


    # 🔔 pop the toast flag (shows once)
    show_toast = session.pop("preferences_saved", None)

    return render_template(
        "home.html",
        trending=trending,
        popular=popular,
        top_rated=top_rated,
        content_type=content_type,
        show_toast=show_toast
    )



@app.route("/content/<int:content_id>")
def content_detail(content_id):
    db = get_db()

    content = db.execute(
        "SELECT * FROM content WHERE id = ?",
        (content_id,)
    ).fetchone()

    if content is None:
        return "Content not found", 404

    return render_template(
        "detail.html",
        content=content
    )
    
    
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





if __name__ == "__main__":
    app.run(debug=True)
