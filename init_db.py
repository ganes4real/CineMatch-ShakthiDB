import os
import psycopg2
from werkzeug.security import generate_password_hash

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")

def init_db():
    print(f"Connecting to {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()

    with open('schema.sql', 'r') as f:
        cur.execute(f.read())

    # Users
    password_alice = generate_password_hash("password")
    password_admin = generate_password_hash("admin")
    
    cur.execute("INSERT INTO users (username, password_hash, is_superuser) VALUES (%s, %s, %s)", ('alice', password_alice, False))
    cur.execute("INSERT INTO users (username, password_hash, is_superuser) VALUES (%s, %s, %s)", ('admin', password_admin, True))

    # Movies (title, description, media_type, genre, runtime, release_year, language, actors, production_house, image_url, trailer_url)
    movies = [
        (
            "Inception", 
            "A thief who steals corporate secrets through the use of dream-sharing technology.", 
            "movie", "Sci-Fi, Action", 148, 2010, "English", 
            "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page", "Warner Bros.",
            "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?w=500&q=80",
            "YoHD9XEInc0" # YouTube video ID
        ),
        (
            "The Matrix", 
            "A computer hacker learns from mysterious rebels about the true nature of his reality.", 
            "movie", "Sci-Fi, Action", 136, 1999, "English", 
            "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss", "Warner Bros.",
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80",
            "vKQi3bBA1y8"
        ),
        (
            "Interstellar", 
            "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", 
            "movie", "Sci-Fi, Drama", 169, 2014, "English", 
            "Matthew McConaughey, Anne Hathaway, Jessica Chastain", "Paramount Pictures",
            "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&q=80",
            "zSWdZVtXT7E"
        ),
        (
            "Breaking Bad", 
            "A chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.", 
            "series", "Crime, Drama, Thriller", 47, 2008, "English", 
            "Bryan Cranston, Aaron Paul, Anna Gunn", "Sony Pictures Television",
            "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&q=80",
            "HhesaQXLuRY"
        )
    ]
    
    cur.executemany("""
        INSERT INTO movies 
        (title, description, media_type, genre, runtime, release_year, language, actors, production_house, image_url, trailer_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, movies)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized with mock data successfully.")

if __name__ == '__main__':
    init_db()
