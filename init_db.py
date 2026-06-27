import os
import psycopg2

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

    # Read and execute schema.sql
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())

    # Insert mock users
    cur.execute("INSERT INTO users (username) VALUES ('guest'), ('alice'), ('bob')")

    # Insert mock movies with rich image placeholders (using unsplash)
    movies = [
        ("Inception", "A thief who steals corporate secrets through the use of dream-sharing technology.", "Sci-Fi", 2010, "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?w=500&q=80"),
        ("The Matrix", "A computer hacker learns from mysterious rebels about the true nature of his reality.", "Sci-Fi", 1999, "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80"),
        ("Interstellar", "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", "Sci-Fi", 2014, "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&q=80"),
        ("The Dark Knight", "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham.", "Action", 2008, "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&q=80"),
        ("Avengers: Endgame", "After the devastating events of Infinity War, the universe is in ruins.", "Action", 2019, "https://images.unsplash.com/photo-1561149877-84d25736c58a?w=500&q=80"),
        ("Spirited Away", "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits.", "Animation", 2001, "https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=500&q=80"),
        ("Parasite", "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.", "Thriller", 2019, "https://images.unsplash.com/photo-1601004124991-0329064c5df0?w=500&q=80"),
        ("La La Land", "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.", "Romance", 2016, "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500&q=80"),
        ("Gladiator", "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.", "Action", 2000, "https://images.unsplash.com/photo-1533514114760-4389f572ae26?w=500&q=80"),
        ("Dune", "Feature adaptation of Frank Herbert's science fiction novel, about the son of a noble family entrusted with the protection of the most valuable asset and most vital element in the galaxy.", "Sci-Fi", 2021, "https://images.unsplash.com/photo-1541873676-a18131494184?w=500&q=80")
    ]
    
    cur.executemany("INSERT INTO movies (title, description, genre, release_year, image_url) VALUES (%s, %s, %s, %s, %s)", movies)

    # Insert mock ratings
    ratings = [
        (1, 1, 5), (1, 2, 4), (1, 3, 5), # guest likes Sci-Fi
        (2, 4, 5), (2, 5, 4), (2, 9, 5), # alice likes Action
        (3, 6, 5), (3, 7, 4), (3, 8, 5)  # bob likes variety
    ]
    cur.executemany("INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)", ratings)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized with mock data successfully.")

if __name__ == '__main__':
    init_db()
