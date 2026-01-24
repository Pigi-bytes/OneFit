import os
from pathlib import Path

from dotenv import load_dotenv

# On charge l'environnement
load_dotenv(Path(__file__).parent / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "c une application super secrete"
