-- schema.sql
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE
);

CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    media_type VARCHAR(20) DEFAULT 'movie',
    genre VARCHAR(255),
    runtime INTEGER,
    release_year INTEGER,
    language VARCHAR(50),
    actors TEXT,
    production_house VARCHAR(150),
    image_url VARCHAR(255),
    trailer_url VARCHAR(255)
);

CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    UNIQUE(user_id, movie_id)
);
