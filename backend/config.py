import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env situé dans le même dossier
load_dotenv(Path(__file__).parent / ".env")


class Config:
    """Configuration centrale de l'application.

    Contient les clés secrètes, paramètres JWT, configuration de la BDD,
    options OpenAPI et niveaux de logging.
    """

    # Clé secrète Flask (utilisée pour les sessions, CSRF, etc.)
    SECRET_KEY = os.environ.get("SECRET_KEY") or "c une application super secrete"

    # Durée de validité du token d'accès JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # Paramètres de connexion à la base de données
    USER: str = os.getenv("user", "user")
    PASSWORD: str = os.getenv("password", "password")
    HOST: str = os.getenv("host", "host")
    PORT: str = os.getenv("port", "port")
    DBNAME: str = os.getenv("dbname", "dbname")

    # Mode debug pour l'application Flask (True si FLASK_DEBUG vaut 1/true/True)
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")

    # Selon le mode, on utilise une BDD SQLite locale (dev) ou PostgreSQL (prod)
    if FLASK_DEBUG:
        # Base de données locale pour le développement
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent / 'database' / 'app.db'}"
    else:
        # Connexion PostgreSQL en production
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

    # Clés pour accès à des API externes (RapidAPI par exemple)
    X_RAPID_API_HOST = os.environ.get("X_RAPID_API_HOST")
    X_RAPID_API_KEY = os.environ.get("X_RAPID_API_KEY")

    # Clé spécifique à l'API foursquare
    SALLE_KEY = os.environ.get("SALLE_KEY")

    # quotas d'utilisation de l'api
    DAILY_LIMIT = 500
    MONTHLY_LIMIT = 2000

    API_TITLE = "OneFit API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"

    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    OPENAPI_REDOC_PATH = None
    OPENAPI_REDOC_URL = None

    # Configuration d'affichage de Swagger UI
    OPENAPI_SWAGGER_UI_CONFIG = {
        "persistAuthorization": True,  # garder l'authentification entre reloads
        "defaultModelsExpandDepth": -1,  # ne pas afficher les modèles par défaut
        "defaultModelExpandDepth": -1,
    }

    # Options / schémas par défaut pour la génération de l'API
    API_SPEC_OPTIONS = {}
    HTTP_ERROR_RESPONSE_SCHEMAS = {}
    DEFAULT_RESPONSE_SCHEMA = None

    # Niveaux de log
    LOG_LEVEL_CONSOLE = os.environ.get("LOG_LEVEL_CONSOLE", "INFO").upper()
    LOG_LEVEL_FILE = os.environ.get("LOG_LEVEL_FILE", "DEBUG").upper()

    # Niveaux de log pour sous-systèmes OneFit
    LOG_LEVEL_ONEFIT = os.environ.get("LOG_LEVEL_ONEFIT", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_AUTH = os.environ.get("LOG_LEVEL_ONEFIT_AUTH", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_DATABASE = os.environ.get("LOG_LEVEL_ONEFIT_DATABASE", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_APICACHE = os.environ.get("LOG_LEVEL_ONEFIT_APICACHE", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_PERFORMANCE = os.environ.get("LOG_LEVEL_ONEFIT_PERFORMANCE", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_ROUTES = os.environ.get("LOG_LEVEL_ONEFIT_ROUTES", "DEBUG").upper()

    # Niveaux de log pour bibliothèques courantes
    LOG_LEVEL_SQLALCHEMY = os.environ.get("LOG_LEVEL_SQLALCHEMY", "WARNING").upper()
    LOG_LEVEL_WERKZEUG = os.environ.get("LOG_LEVEL_WERKZEUG", "WARNING").upper()
    LOG_LEVEL_URLLIB3 = os.environ.get("LOG_LEVEL_URLLIB3", "WARNING").upper()

    # Mot de passe SMTP 
    ONEFIT_SMTP_PASSWORD = os.environ.get("ONEFIT_SMTP_PASSWORD", "ONEFIT_SMTP_PASSWORD")