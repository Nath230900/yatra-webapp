import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-this-secret-key"
    # SQLite for easy local development
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "yatra.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
