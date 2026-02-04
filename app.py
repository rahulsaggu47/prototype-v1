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
    get_spotlight_content
)


app = Flask(__name__)
app.secret_key = "dev-secret-key"

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

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

    # Check if user already selected genres
    user = db.execute(
        "SELECT preferred_genres FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if user["preferred_genres"] and user["preferred_genres"].strip() != "":
        return redirect("/")


    # ✅ ALWAYS define this (fixes the error)
    selected_genres = []
    error = None

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

@app.route("/api/spotlight")
def api_spotlight():
    content_type = request.args.get("type", "anime")

    spotlight_items = get_spotlight_content(content_type)

    return jsonify([dict(row) for row in spotlight_items])


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


@app.route("/api/favorites/add", methods=["POST"])
def api_add_favorite():
    data = request.json
    user_id = session.get("user_id")
    content_id = data.get("content_id")

    if not user_id or not content_id:
        return jsonify({"error": "Missing user_id or content_id"}), 400

    success = add_favorite(user_id, content_id)

    return jsonify({"success": success})


@app.route("/api/favorites/remove", methods=["POST"])
def api_remove_favorite():
    data = request.json
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    content_id = data.get("content_id")

    if not user_id or not content_id:
        return jsonify({"error": "Missing user_id or content_id"}), 400

    remove_favorite(user_id, content_id)
    return jsonify({"success": True})


@app.route("/api/favorites")
def api_get_favorites():
    user_id = request.args.get("user_id")
    content_type = request.args.get("type")  # optional: anime/movie

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    favorites = get_user_favorites(user_id, content_type)
    return jsonify([dict(row) for row in favorites])



@app.route("/")
def home():
    content_type = request.args.get("type", "anime")

    trending = get_trending_by_genres(content_type)
    popular = get_popular_by_genres(content_type)

    # 🔔 pop the toast flag (shows once)
    show_toast = session.pop("preferences_saved", None)

    return render_template(
        "home.html",
        trending=trending,
        popular=popular,
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


if __name__ == "__main__":
    app.run(debug=True)
