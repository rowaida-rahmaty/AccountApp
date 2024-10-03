from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize extensions globally
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()  # Initialize CSRFProtect


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    
    # Initialize CSRFProtect before other extensions
    csrf.init_app(app)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Import and register blueprints
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views)
    app.register_blueprint(auth)

    # Set login view and message category
    login_manager.login_view = 'auth.login'  # Adjust route if needed
    login_manager.login_message_category = 'info'
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    try:
        user = User.query.get(int(user_id))
        if user is None:
            print(f"User with ID {user_id} not found")
            return None
        return user
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

def create_db(app):
    with app.app_context():
        db.create_all()  # Create tables in the database

