import os

class Config:
    SECRET_KEY = 'your-secret-key'  # Change this to a secure key in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cocktails.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False