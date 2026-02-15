import logging
import os
import time

import click
from config import Config
from flask import Flask, g, request
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

from .utils.logger import auth_logger, db_logger, logger


class CustomApi(Api):
    DEFAULT_ERROR_RESPONSE_NAME = None


from flask_cors import CORS  # noqa: E402

app = Flask(__name__)
logger.info("Application Flask initialisée \n")

CORS(app)
logger.debug("CORS activé")
app.config.from_object(Config)
logger.debug("Configuration chargée depuis Config")

db = SQLAlchemy(app)
db_logger.info("SQLAlchemy initialisé")
jwt = JWTManager(app)
auth_logger.info("JWTManager initialisé")
api = CustomApi(app)
logger.info("API Smorest initialisée")

api.spec.components.security_scheme(  # type: ignore
    "bearerAuth",
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Entrez votre token JWT",
    },
)

from app.routes import authBLP, userBLP, userOptionBLP  # noqa: E402

api.register_blueprint(authBLP)
logger.debug("Blueprint enregistré (/auth)")
api.register_blueprint(userBLP)
logger.debug("Blueprint enregistré (/user)")
api.register_blueprint(userOptionBLP)
logger.debug("Blueprint enregistré (/user/option)")


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def log_request(response):
    # Ignore les requêtes OPTIONS et favicon
    if request.method == "OPTIONS" or request.path == "/favicon.ico":
        return response

    duration = time.perf_counter() - g.start
    status = response.status_code

    if status >= 500:
        log_level = logging.ERROR
    elif status >= 400:
        log_level = logging.WARNING
    elif duration > 0.7:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    logger.log(log_level, f"HTTP {request.method} {request.path} | {status} | {(duration * 1000):.1f}ms")
    return response


@app.cli.command("init-db")
def init_db_command():
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    db_logger.info("INIT DB | Initialisation de la base de données")

    if db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "", 1)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            db_logger.info(f"INIT DB | Répertoire créé: {db_dir}")

    db.create_all()
    db_logger.info("INIT DB | Tables créées avec succès")
    click.echo("bd initialisée.")


@app.cli.command("reset-db")
@click.option("--yes", is_flag=True, help="Confirmer la suppression")
def reset_db_command(yes):
    if not yes:
        click.confirm("Voulez-vous vraiment supprimer la bd", abort=True)

    db_logger.warning("RESET DB | Suppression et recréation de toutes les tables")
    db.drop_all()
    db_logger.info("RESET DB | Tables supprimées")
    db.create_all()
    db_logger.info("RESET DB | Tables recréées")
    click.echo("bd supprimé")


@app.cli.command("drop-requestlog")
def drop_requestlog():
    from app.models import RequestLog

    db_logger.warning("DROP TABLE | Suppression de la table RequestLog")
    RequestLog.__table__.drop(db.engine)  # type: ignore
    db_logger.info("DROP TABLE | Table RequestLog supprimée")
    click.echo("Table RequestLog supprimée.")


@app.errorhandler(422)
def handle_marshmallow_error(err):
    messages = err.data.get("messages", ["Invalid request"])
    logger.warning(f"VALIDATION ERROR| 422 | {messages}")
    return {"errors": messages}, 422


@jwt.expired_token_loader
def expiredTokenCallback(jwt_header, jwt_payload):
    auth_logger.warning(f"JWT EXPIRE | sub={jwt_payload.get('sub')}")
    return {"message": "Token expiré", "error": "token_expired"}, 401


@jwt.invalid_token_loader
def invalidTokenLoader(error):
    auth_logger.warning(f"JWT INVALIDE | error={error}")
    return {"message": "Token invalide", "error": "invalid_token"}, 401


@jwt.unauthorized_loader
def missingTokenLoader(error):
    auth_logger.warning("JWT MANQUANT | Requête sans token ")
    return {"message": "Token manquant", "error": "authorization_required"}, 401
