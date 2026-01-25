import click
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import models, routes  # noqa: E402, F401


@app.cli.command("init-db")
def init_db_command():
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
