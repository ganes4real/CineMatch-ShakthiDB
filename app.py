import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cinematch_super_secret_key' # Needed for Flask-Login & sessions

# Database configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Models ---
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    media_type = db.Column(db.String(20), default='movie')
    genre = db.Column(db.String(255))
    runtime = db.Column(db.Integer)
    release_year = db.Column(db.Integer)
    language = db.Column(db.String(50))
    actors = db.Column(db.Text)
    production_house = db.Column(db.String(150))
    image_url = db.Column(db.String(255))
    trailer_url = db.Column(db.String(255))
    
class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'))
    rating = db.Column(db.Integer)

# --- Routes ---

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'error')
        else:
            new_user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
            
    return render_template('login.html', register=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# App Routes
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    
    if search_query:
        movies = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).all()
        recommendations = []
    else:
        movies = Movie.query.limit(8).all()
        recommendations = []
        
        if current_user.is_authenticated:
            # Find genres the user likes (rated 4 or 5)
            user_liked_genres = db.session.query(Movie.genre).join(Rating).filter(
                Rating.user_id == current_user.id,
                Rating.rating >= 4
            ).distinct().all()
            
            liked_genres = []
            for g in user_liked_genres:
                # Assuming genre might be a comma-separated string like "Sci-Fi, Action"
                # For a simple recommendation, we just search for exact matching strings 
                # or we can just use the exact strings from DB.
                liked_genres.append(g[0])
            
            if liked_genres:
                rated_movies_subq = db.session.query(Rating.movie_id).filter(Rating.user_id == current_user.id)
                recommendations = Movie.query.filter(
                    Movie.genre.in_(liked_genres),
                    ~Movie.id.in_(rated_movies_subq)
                ).limit(4).all()
                
        if not recommendations:
            recommendations = Movie.query.order_by(func.random()).limit(4).all()

    return render_template('index.html', movies=movies, recommendations=recommendations, search_query=search_query)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    avg_rating_query = db.session.query(func.avg(Rating.rating)).filter(Rating.movie_id == movie_id).scalar()
    avg_rating = round(avg_rating_query, 1) if avg_rating_query else "No ratings yet"
    
    similar_movies = Movie.query.filter(
        Movie.genre == movie.genre,
        Movie.id != movie.id
    ).limit(4).all()
    
    # Extract user rating if logged in
    user_rating = None
    if current_user.is_authenticated:
        r = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
        if r:
            user_rating = r.rating

    return render_template('movie_detail.html', movie=movie, avg_rating=avg_rating, similar_movies=similar_movies, user_rating=user_rating)

@app.route('/rate', methods=['POST'])
@login_required
def rate_movie():
    movie_id = request.form.get('movie_id')
    rating_val = request.form.get('rating')
    
    if movie_id and rating_val:
        existing_rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
        if existing_rating:
            existing_rating.rating = int(rating_val)
        else:
            new_rating = Rating(user_id=current_user.id, movie_id=movie_id, rating=int(rating_val))
            db.session.add(new_rating)
        db.session.commit()
        
    return redirect(url_for('movie_detail', movie_id=movie_id))

# Admin Routes
@app.route('/admin/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if not current_user.is_superuser:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # Extract YouTube ID if full URL is pasted
        trailer_url = request.form.get('trailer_url', '')
        if 'v=' in trailer_url:
            trailer_url = trailer_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in trailer_url:
            trailer_url = trailer_url.split('youtu.be/')[1].split('?')[0]
            
        new_movie = Movie(
            title=request.form.get('title'),
            description=request.form.get('description'),
            media_type=request.form.get('media_type'),
            genre=request.form.get('genre'),
            runtime=request.form.get('runtime', type=int) or None,
            release_year=request.form.get('release_year', type=int) or None,
            language=request.form.get('language'),
            actors=request.form.get('actors'),
            production_house=request.form.get('production_house'),
            image_url=request.form.get('image_url'),
            trailer_url=trailer_url
        )
        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully!', 'success')
        return redirect(url_for('movie_detail', movie_id=new_movie.id))
        
    return render_template('add_movie.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
