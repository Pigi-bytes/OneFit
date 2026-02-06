from datetime import date

import sqlalchemy as sa
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app import db
from app.models import User
from app.schemas import (
    AuthErrorResponseSchema,
    LoginSchema,
    MessageSchema,
    ProtectedSchema,
    RegisterErrorResponseSchema,
    RegisterSchema,
    TokenSchema,
    UserNotFoundErrorSchema,
    ValidationErrorSchema,
)

authBLP = Blueprint("auth", __name__, url_prefix="/auth", description="Authentification")
userBLP = Blueprint("user", __name__, url_prefix="/user", description="Gestion utilisateur")


@authBLP.route("/login", methods=["POST"])
@authBLP.arguments(LoginSchema)
@authBLP.response(200, TokenSchema)
@authBLP.alt_response(401, schema=AuthErrorResponseSchema, description="Identifiants invalides")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def login(data):
    """Connexion utilisateur"""
    username = data.get("username")
    password = data.get("password")

    user = db.session.scalar(sa.select(User).where(User.username == username))

    if user is None:
        abort(401, message="Identifiants invalides")

    if user.checkPassword(password):
        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token}, 200

    abort(401, message="Identifiants invalides")


@authBLP.route("/inscription", methods=["POST"])
@authBLP.arguments(RegisterSchema)
@authBLP.response(201, MessageSchema)
@authBLP.alt_response(409, schema=RegisterErrorResponseSchema, description="Username existant")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def register(data):
    """Inscription d'un nouvel utilisateur"""
    username = data["username"]
    password = data["password"]
    existing_user = db.session.scalar(sa.select(User).where(User.username == username))
    if existing_user:
        abort(409, message="Nom d'utilisateur déjà pris")

    user = User(username=username, password=generate_password_hash(password), date_naissance=date.today(), taille=160)  # type: ignore # TODO CHANGER LES VALEURS DE BASE PLUS TARD

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully!"}


@userBLP.route("/user", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, ProtectedSchema)
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(401, schema=UserNotFoundErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def user():
    """Route protégée nécessitant un token JWT"""
    id = get_jwt_identity()
    user = db.session.scalar(sa.select(User).where(User.id == id))
    if user is None:
        abort(401, message="User not found")

    dernier_poids = user.historique_poids[-1].poids if user.historique_poids else None
    return {
        "username": user.username,
        "date_naissance": user.date_naissance,
        "taille": user.taille,
        "dernierPoids": dernier_poids,
    }
