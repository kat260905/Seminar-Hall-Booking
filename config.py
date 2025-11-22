import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        #"sqlite:///app.db"   # ✅ temporary SQLite database
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
