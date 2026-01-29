import os

import click
from config import Config
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt = JWTManager(app)

from app import models, routes  # noqa: E402, F401


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
