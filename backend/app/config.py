# /app/config.py
import os
import secrets


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    #the below code is bad practice
    #SECRET_KEY = 'e8be6c76f90f01893eedc58ee07c65fcc1e4339b1a854dc1edc9969402a84bc2'
    SQLALCHEMY_DATABASE_URI = 'mysql://silver:Password_12345@192.168.33.10/quizzle'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'images') 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
    #SECRET_KEY = 'supersecretkey'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    JWT_SECRET_KEY = 'b3f47c8a9f2c03d9c24d2fbc68a3c587d2c03ab11b20f73989227ac63892f1f3'
    GEMINI_API_KEY = 'AIzaSyDQDrSoYWlBDMyVg35e8_BlSrvGuhfy9QI'
    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'marwaasabon@gmail.com'
    MAIL_PASSWORD = 'kcybbulukyxkdxzo' #ge
    MAIL_DEFAULT_SENDER = 'marwasabon@gmail.com'
