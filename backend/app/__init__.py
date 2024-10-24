from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from .models.db_storage import DBStorage,db 
from .models.user import User
from flask_migrate import Migrate
from flask_login import LoginManager ,UserMixin
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.routes import main as main_blueprint;
import os
from app.config import Config  # Import the Config class
import google.generativeai as genai

mail = Mail()
def create_app():


 
# Configure the Gemini API using the loaded key
    app = Flask(__name__)
    app.config.from_object(Config)  # Apply configuration from Config class
    genai.configure(api_key=app.config['GEMINI_API_KEY'])

    db.init_app(app)  # Initialize the global db instance with the app
    storage = DBStorage(db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Set the login view for Flask-Login
    mail.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

  
    jwt = JWTManager(app)
    CORS(app)
    app.register_blueprint(main_blueprint)

    migrate = Migrate(app, db)
    return app
