import os
from pathlib import Path

from dotenv import load_dotenv

# On charge l'environnement
load_dotenv(Path(__file__).parent / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "c une application super secrete"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{Path(__file__).parent / 'database' / 'app.db'}"
    )
