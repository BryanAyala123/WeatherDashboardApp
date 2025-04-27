-- DROP TABLE IF EXISTS songs;
-- CREATE TABLE songs (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     artist TEXT NOT NULL,
--     title TEXT NOT NULL,
--     year INTEGER NOT NULL CHECK(year >= 1900),
--     genre TEXT NOT NULL,
--     duration INTEGER NOT NULL CHECK(duration > 0),
--     play_count INTEGER DEFAULT 0,
--     UNIQUE(artist, title, year)
-- );

-- CREATE INDEX idx_songs_artist_title ON songs(artist, title);
-- CREATE INDEX idx_songs_year ON songs(year);
-- CREATE INDEX idx_songs_play_count ON songs(play_count);

CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,       -- from user input / coord.lat
    longitude REAL NOT NULL,      -- from user input /coord.lon
    city_name TEXT NOT NULL,      -- from user input / city.name / name
    time DATETIME NOT NULL,       -- dt_txt <- datetime = YYYY-MM-DD HH:MI:SS / dt <- Unix time UTC     
    temp REAL,                    -- main.temp
    feels_like REAL,              -- main.feels_like
    pressure INTEGER,             -- main.pressure
    humidity INTEGER,             -- main.humidity
    weather_main TEXT,            -- weather[0].main
    weather_description TEXT     -- weather[0].description
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    city_name TEXT NOT NULL
);

--might want units parameter assume Imperial for F
