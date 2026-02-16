import os
from pathlib import Path

from dotenv import load_dotenv

# On charge l'environnement
load_dotenv(Path(__file__).parent / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "c une application super secrete"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{Path(__file__).parent / 'database' / 'app.db'}"

    X_RAPID_API_HOST = os.environ.get("X_RAPID_API_HOST")
    X_RAPID_API_KEY = os.environ.get("X_RAPID_API_KEY")

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

    OPENAPI_SWAGGER_UI_CONFIG = {
        "persistAuthorization": True,
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": -1,
    }

    API_SPEC_OPTIONS = {}
    HTTP_ERROR_RESPONSE_SCHEMAS = {}
    DEFAULT_RESPONSE_SCHEMA = None

    LOG_LEVEL_CONSOLE = os.environ.get("LOG_LEVEL_CONSOLE", "INFO").upper()
    LOG_LEVEL_FILE = os.environ.get("LOG_LEVEL_FILE", "DEBUG").upper()

    LOG_LEVEL_ONEFIT = os.environ.get("LOG_LEVEL_ONEFIT", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_AUTH = os.environ.get("LOG_LEVEL_ONEFIT_AUTH", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_DATABASE = os.environ.get("LOG_LEVEL_ONEFIT_DATABASE", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_APICACHE = os.environ.get("LOG_LEVEL_ONEFIT_APICACHE", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_PERFORMANCE = os.environ.get("LOG_LEVEL_ONEFIT_PERFORMANCE", "DEBUG").upper()
    LOG_LEVEL_ONEFIT_ROUTES = os.environ.get("LOG_LEVEL_ONEFIT_ROUTES", "DEBUG").upper()

    LOG_LEVEL_SQLALCHEMY = os.environ.get("LOG_LEVEL_SQLALCHEMY", "WARNING").upper()
    LOG_LEVEL_WERKZEUG = os.environ.get("LOG_LEVEL_WERKZEUG", "WARNING").upper()
    LOG_LEVEL_URLLIB3 = os.environ.get("LOG_LEVEL_URLLIB3", "WARNING").upper()