from datetime import date

import sqlalchemy as sa
from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app import db
from app.models import User
from app.schemas import BaseErrorSchema, LoginSchema, MessageSchema, RegisterSchema, TokenSchema, ValidationErrorSchema
from app.utils.logger import QueryTimer, auth_logger

authBLP = Blueprint("auth", __name__, url_prefix="/auth", description="Authentification")


@authBLP.route("/login", methods=["POST"])
@authBLP.arguments(LoginSchema)
@authBLP.response(200, TokenSchema)
@authBLP.alt_response(401, schema=BaseErrorSchema, description="Identifiants invalides")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def login(data):
    """Connexion utilisateur"""
    username = data["username"]
    auth_logger.info(f"LOGIN ATTEMPT | username={username}")

    with QueryTimer("Test Login"):
        user = db.session.scalar(sa.select(User).where(User.username == username))

    if user is None:
        auth_logger.warning(f"LOGIN FAIL | Utilisateur inexistant | username={username}")
        abort(401, message="Identifiants invalides")

    if not user.checkPassword(data["password"]):
        auth_logger.warning(f"LOGIN FAIL | Mot de passe incorrect | username={username} | user_id={user.id}")
        abort(401, message="Identifiants invalides")

    access_token = create_access_token(identity=str(user.id))
    auth_logger.info(f"LOGIN SUCCESS | username={username} | user_id={user.id}")
    return {"access_token": access_token}


@authBLP.route("/inscription", methods=["POST"])
@authBLP.arguments(RegisterSchema)
@authBLP.response(201, MessageSchema)
@authBLP.alt_response(409, schema=BaseErrorSchema, description="Nom d'utilisateur déjà pris")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def inscription(data):
    """Inscription d'un nouvel utilisateur"""
    username = data["username"]
    auth_logger.info(f"REGISTER ATTEMPT | username={username}")

    with QueryTimer("checkUsernameExists"):
        existing_user = db.session.scalar(sa.select(User).where(User.username == username))

    if existing_user:
        auth_logger.warning(f"REGISTER CONFLICT | Username déjà pris | username={username}")
        abort(409, message="Nom d'utilisateur déjà pris")

    user = User(username=username, password=generate_password_hash(data["password"]), date_naissance=date.today(), taille=160)  # type: ignore # TODO CHANGER LES VALEURS DE BASE PLUS TARD

    db.session.add(user)
    with QueryTimer("commitInscription"):
        db.session.commit()

    auth_logger.info(f"REGISTER SUCCESS | username={username} | user_id={user.id}")
    return {"message": "User created successfully!"}
