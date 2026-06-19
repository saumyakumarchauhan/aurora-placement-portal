import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from datetime import timedelta

# Load environment variables from the .env file
load_dotenv()

# 1. IMPORT EXTENSIONS FIRST
# (Added cache and mail here so they initialize correctly)
from extensions import db, cache, mail
from models.models import User

# 2. INITIALIZE FLASK GLOBALLY 
app = Flask(__name__)


# BASIC CONFIGURATION
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "fallback-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///placement.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-jwt-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)


# MAIL CONFIGURATION
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465               
app.config['MAIL_USE_TLS'] = False          
app.config['MAIL_USE_SSL'] = True           

# Pulling email credentials from .env
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")


# INITIALIZE EXTENSIONS
db.init_app(app)

cache.init_app(app, config={
    'CACHE_TYPE': 'RedisCache', 
    'CACHE_REDIS_URL': os.getenv("CACHE_REDIS_URL", "redis://127.0.0.1:6379/0")
})

# Initialize Mail
mail.init_app(app)

JWTManager(app)
CORS(app)   # Allow Vue frontend requests

from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.student_controller import student_bp
from controllers.company_controller import company_bp

# REGISTER BLUEPRINTS
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)
app.register_blueprint(company_bp)

# ROUTES & DB SETUP
@app.route("/")
def index():
    return redirect(url_for("auth.login"))

# Create tables + Default Admin
with app.app_context():
    db.create_all()

    # Pull admin credentials from .env
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_pass = os.getenv("ADMIN_PASSWORD")

    # Create default admin if not exists
    admin = User.query.filter_by(email=admin_email).first()

    if not admin:
        admin_user = User(
            email=admin_email,
            password_hash=generate_password_hash(admin_pass),
            role="admin",
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin created.")

# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)