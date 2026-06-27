import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)

# Database configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    
class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'))
    rating = db.Column(db.Integer)

# --- Routes ---
@app.route('/')
def index():
    # Mock logged-in user (id=1, "guest")
    current_user_id = 1 
    
    # Get search query if any
    search_query = request.args.get('search', '')
    
    if search_query:
        movies = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).all()
        recommendations = [] # Don't show recommendations on search results
    else:
        # Trending / All movies
        movies = Movie.query.limit(8).all()
        
        # Simple Recommendation Algorithm:
        # 1. Find genres the user likes (rated 4 or 5)
        # 2. Get top rated movies in those genres that the user hasn't rated yet
        user_liked_genres = db.session.query(Movie.genre).join(Rating).filter(
            Rating.user_id == current_user_id,
            Rating.rating >= 4
        ).distinct().all()
        
        liked_genres = [g[0] for g in user_liked_genres]
        
        recommendations = []
        if liked_genres:
            # Subquery for movies the user already rated
            rated_movies_subq = db.session.query(Rating.movie_id).filter(Rating.user_id == current_user_id)
            
            # Find movies in liked genres not yet rated
            recommendations = Movie.query.filter(
                Movie.genre.in_(liked_genres),
                ~Movie.id.in_(rated_movies_subq)
            ).limit(4).all()
            
        # Fallback if no recommendations
        if not recommendations:
            recommendations = Movie.query.order_by(func.random()).limit(4).all()

    return render_template('index.html', movies=movies, recommendations=recommendations, search_query=search_query)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Calculate average rating
    avg_rating_query = db.session.query(func.avg(Rating.rating)).filter(Rating.movie_id == movie_id).scalar()
    avg_rating = round(avg_rating_query, 1) if avg_rating_query else "No ratings yet"
    
    # Recommendations based on similar genre
    similar_movies = Movie.query.filter(
        Movie.genre == movie.genre,
        Movie.id != movie.id
    ).limit(4).all()
    
    return render_template('movie_detail.html', movie=movie, avg_rating=avg_rating, similar_movies=similar_movies)

@app.route('/rate', methods=['POST'])
def rate_movie():
    # Mock logged-in user (id=1, "guest")
    current_user_id = 1 
    
    movie_id = request.form.get('movie_id')
    rating_val = request.form.get('rating')
    
    if movie_id and rating_val:
        # Check if already rated
        existing_rating = Rating.query.filter_by(user_id=current_user_id, movie_id=movie_id).first()
        if existing_rating:
            existing_rating.rating = int(rating_val)
        else:
            new_rating = Rating(user_id=current_user_id, movie_id=movie_id, rating=int(rating_val))
            db.session.add(new_rating)
        db.session.commit()
        
    return redirect(url_for('movie_detail', movie_id=movie_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
