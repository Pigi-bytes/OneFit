import logging
import os
import time

import click
from config import Config
from flask import Flask, g, request
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

from .utils.logger import logger


class CustomApi(Api):
    DEFAULT_ERROR_RESPONSE_NAME = None


from flask_cors import CORS  # noqa: E402

app = Flask(__name__)
logger.info("Application Flask initialisée !")
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt = JWTManager(app)
api = CustomApi(app)

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
api.register_blueprint(userBLP)
api.register_blueprint(userOptionBLP)


@app.errorhandler(422)
def handle_marshmallow_error(err):
    messages = err.data.get("messages", ["Invalid request"])
    logger.error(f"Erreur de validation Marshmallow : {messages}")

    return {"errors": messages}, 422


@app.before_request
def start_timer():
    g.start = time.perf_counter()


@app.after_request
def log_request(response):
    if request.path == "/favicon.ico":  # On ignore le favicon
        return response

    now = time.perf_counter()
    duration = now - g.start

    if duration > 0.5:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    logger.log(log_level, f"REQ {request.method} {request.path} | Status: {response.status_code} | Time: {duration:.4f}s")
    return response


@app.cli.command("init-db")
def init_db_command():
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "", 1)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    db.create_all()
    click.echo("bd initialisée.")


@app.cli.command("reset-db")
@click.option("--yes", is_flag=True, help="Confirmer la suppression")
def reset_db_command(yes):
    if not yes:
        click.confirm("Voulez-vous vraiment supprimer la bd", abort=True)

    db.drop_all()
    db.create_all()
    click.echo("bd supprimé")


@app.cli.command("drop-requestlog")
def drop_requestlog():
    from app.models import RequestLog

    RequestLog.__table__.drop(db.engine)  # type: ignore
    click.echo("Table RequestLog supprimée.")
