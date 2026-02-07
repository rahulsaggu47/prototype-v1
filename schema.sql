-- CREATE TABLE IF NOT EXISTS users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     username TEXT UNIQUE NOT NULL,
--     password_hash TEXT NOT NULL,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE IF NOT EXISTS content (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     title TEXT NOT NULL,
--     type TEXT CHECK(type IN ('anime', 'movie')) NOT NULL,
--     description TEXT,
--     release_year INTEGER,
--     genres TEXT,
--     poster_url TEXT,
--     background_url TEXT,
--     trailer_url TEXT,
--     rating REAL,
--     views_count INTEGER DEFAULT 0,
--     episodes INTEGER,
--     duration INTEGER
-- );

-- CREATE TABLE IF NOT EXISTS favorites (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER NOT NULL,
--     content_id INTEGER NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
--     FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE,
--     UNIQUE (user_id, content_id)
-- );

-- CREATE TABLE IF NOT EXISTS user_genres (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER NOT NULL,
--     genre TEXT NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
-- );

-- CREATE TABLE IF NOT EXISTS chatbot_logs (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_id INTEGER,
--     user_message TEXT NOT NULL,
--     bot_response TEXT NOT NULL,
--     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
-- );


-- ALTER TABLE users ADD COLUMN preferred_genres TEXT;

-- ALTER TABLE favorites ADD COLUMN created_at DATETIME;

-- DELETE FROM content WHERE type = 'anime';
-- DELETE FROM content WHERE type = 'movie';

-- CREATE TABLE IF NOT EXISTS spotlight (
--     position INTEGER PRIMARY KEY,
--     content_id INTEGER NOT NULL
-- );
