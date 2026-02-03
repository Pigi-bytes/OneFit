import os

import click
from config import Config
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

class CustomApi(Api):
    DEFAULT_ERROR_RESPONSE_NAME = None

from flask_cors import CORS



app = Flask(__name__)
CORS(app)  # ← autorise toutes les origines pour tester
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt = JWTManager(app)
api = CustomApi(app)

api.spec.components.security_scheme( # type: ignore
    "bearerAuth",
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Entrez votre token JWT",
    },
)

from app.routes import authBLP, mainBLP  # noqa: E402

api.register_blueprint(mainBLP)
api.register_blueprint(authBLP)


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
