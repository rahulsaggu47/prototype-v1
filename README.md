# NextWatch 🎬

> **Discover your next obsession** — a personalized anime and movie recommendation platform built as a college project.

---

## 👥 Team

| Name | Role |
|------|------|
| **Rahul Saggu** | Co-Developer · UI/UX Design · Backend Architecture |
| **Akriti** | Co-Developer · Content Curation · Database & Research |

---

## 📸 Screenshots

> *(Add screenshots here)*

---

## ✨ Features

### Core Experience
- **Dual World Browsing** — switch between Anime and Movie worlds, each with its own curated experience
- **Personalized Onboarding** — genre selection on signup drives all recommendation logic
- **Cinematic Detail Pages** — full-screen backdrop hero, tabbed info/trailer/reviews layout
- **Spotlight Carousel** — admin-curated featured content with video backgrounds

### Recommendation Engine
- **Genre-Based Recommendations** — matches content to the user's selected genre preferences
- **Because You Liked** — finds similar titles based on favorites and highly-rated content
- **Out of Your Comfort Zone** — intentionally surfaces content outside the user's usual genres
- **More Like This** — genre-scored related content on every detail page
- **Mood-Based Recommender** — 5-question quiz that maps mood/vibe to a personalized pick

### Discovery & Search
- Real-time search with debouncing and keyword highlighting
- Multi-filter system: genre, year range, minimum rating, sort order
- Active filter tags with individual and bulk removal

### Social & User Features
- User reviews with star ratings, edit and delete support
- Rating distribution summary per title (bar chart breakdown)
- Favorites collection with filter and sort
- Custom avatar selection (preset characters + custom upload)
- User profile with review history, top-rated row, and world switching

### Admin Panel
- Spotlight manager — assign up to 3 spotlight items per content type
- Curated Picks manager — Rahul and Akriti each maintain 5 personal picks per type
- Admin picks displayed on the home page with hover-expand design

### NEXI — AI Chatbot
- Floating chat widget available on every page
- Powered by Groq (LLaMA 3.3 70B) for fast, intelligent responses
- Personalized context injection — knows the user's genres, favorites, and ratings
- Session memory — remembers the conversation history within a session
- Quick suggestion chips for common queries
- All conversations logged to database

### Monetization
- Premium membership via Razorpay payment gateway (test mode)
- Monthly (₹49) and yearly (₹399) plans
- Premium features: mood discovery, advanced filters, taste profile insights
- Membership management with two-step cancellation flow

### Streaming Quick Links
- "Watch Now" modal on detail pages and spotlight
- Platform suggestions per content type (Crunchyroll, Netflix, Prime, Hotstar, JioCinema etc.)
- Search-linked buttons that open the title on each platform

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · Flask |
| Database | SQLite (via Flask `g` context) |
| Frontend | Jinja2 Templates · Vanilla JS · CSS3 |
| AI | Groq API (LLaMA 3.3 70B) |
| Payments | Razorpay (test mode) |
| Anime Data | Jikan API (MyAnimeList) |
| Movie Data | TMDB API |
| Fonts | Google Fonts (Bebas Neue · DM Sans) |

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd nextwatch
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root (see [Environment Variables](#-environment-variables) below):

```bash
cp .env.example .env
# Then fill in your keys
```

### 5. Initialize the database

```bash
python init_db.py
```

### 6. Seed content (optional but recommended)

```bash
python seed_data.py
# Choose option 1 for anime, 2 for movies, or 5 for both
```

### 7. Run the app

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## 🔑 Environment Variables

NextWatch uses environment variables to keep API keys out of the source code. Here is every variable the app needs:

```
SECRET_KEY=your-random-secret-key-here
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxx
TMDB_API_KEY=xxxxxxxxxxxxxxxxxxxx
```

See the [Environment Variables guide](#-how-environment-variables-work) at the bottom of this file for how to set these up.

### Where to get each key

| Variable | Where to get it | Free? |
|----------|----------------|-------|
| `SECRET_KEY` | Generate yourself (any long random string) | ✅ |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | ✅ |
| `RAZORPAY_KEY_ID` | [dashboard.razorpay.com](https://dashboard.razorpay.com) → Settings → API Keys | ✅ test mode |
| `RAZORPAY_KEY_SECRET` | Same as above | ✅ test mode |
| `TMDB_API_KEY` | [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) | ✅ |

---

## 🗄️ Database Schema

```
users           — accounts, preferences, premium status, avatar
content         — anime and movies (title, type, genres, poster, backdrop, trailer, rating)
favorites       — user ↔ content many-to-many
reviews         — star ratings + written reviews per user per title
spotlight       — admin-assigned featured content (up to 3 per type)
admins_picks    — Rahul and Akriti's curated picks (up to 5 per admin per type)
chatbot_logs    — NEXI conversation history (user_id nullable for guests)
```

---

## 📁 Project Structure

```
nextwatch/
├── app.py                  # Flask routes and application logic
├── init_db.py              # Database initializer
├── seed_data.py            # Content seeder (Jikan + TMDB)
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (auto-created)
├── schema.sql              # Database schema
│
├── utils/
│   └── db.py               # Database helpers and query functions
│
├── templates/
│   ├── base.html           # Base layout (splash, NEXI widget, toast)
│   ├── home.html           # Main browse page
│   ├── welcome.html        # Landing page
│   ├── detail.html         # Content detail page
│   ├── profile.html        # User profile
│   ├── favorites.html      # Favorites collection
│   ├── premium.html        # Premium upgrade page
│   ├── login.html          # Login
│   ├── signup.html         # Sign up
│   ├── select_genres.html  # Genre preference selector
│   ├── footer.html         # Footer (included in base)
│   ├── payment.html        # Payment page
│   └── admin/
│       ├── dashboard.html
│       ├── spotlight.html
│       └── picks.html
│
└── static/
    ├── css/                # Stylesheets per page
    ├── js/                 # JavaScript files
    ├── avatars/            # Default avatar images
    ├── videos/             # Spotlight background videos
    ├── sounds/             # Intro sound
    ├── gif/                # No-results animation
    └── uploads/            # User-uploaded avatars
```

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/spotlight` | Spotlight content for home carousel |
| GET | `/api/content` | Browse/search/filter content |
| GET | `/api/recommended` | Personalized recommendations |
| GET | `/api/because-you-liked` | Similarity-based recommendations |
| GET | `/api/out-of-comfort/<type>` | Outside-preference suggestions |
| GET | `/api/related/<id>` | More like this for detail page |
| GET | `/api/admin-picks` | Curated admin picks |
| GET | `/api/favorites` | User's saved favorites |
| POST | `/api/favorites/add` | Save a title to favorites |
| POST | `/api/favorites/remove` | Remove from favorites |
| GET | `/api/favorites/status/<id>` | Check if a title is favorited |
| GET | `/api/reviews/<id>` | Reviews for a title |
| POST | `/add-review` | Submit a review |
| POST | `/edit-review/<id>` | Edit own review |
| POST | `/delete-review/<id>` | Delete own review |
| POST | `/api/nexi` | NEXI AI chatbot |
| GET | `/api/recommend` | Mood-based single recommendation |
| GET | `/create-order/<plan>` | Create Razorpay payment order |

---

## 👤 Admin Access

Admin features (spotlight manager, picks manager) are accessible to user IDs `1` and `30`. Create an account first, then these routes become available:

- `/admin` — dashboard
- `/admin/spotlight` — manage spotlight
- `/admin/picks` — manage curated picks

---

## 📝 Notes

- Payment integration is in **test mode** — use Razorpay test card details, no real money is charged
- The NEXI chatbot requires a Groq API key to function — without it the endpoint returns a fallback message
- SQLite is used for simplicity in a college project context — a production deployment would use PostgreSQL
- All video files for spotlight backgrounds are stored locally in `/static/videos/`

---

## 📄 License

This project was built as a college submission. All third-party content (anime/movie metadata, posters) belongs to their respective owners and is used here purely for educational purposes.
