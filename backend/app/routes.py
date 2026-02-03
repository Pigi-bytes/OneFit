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
    ValidationErrorSchema,
)

mainBLP = Blueprint("main", __name__, description="Main")
authBLP = Blueprint("auth", __name__, url_prefix="/auth", description="Authentification")

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
        access_token = create_access_token(identity=username)
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

    user = User(username=username, password=generate_password_hash(password))  # type: ignore

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully!"}


@authBLP.route("/user", methods=["GET"])
@authBLP.doc(security=[{"bearerAuth": []}])
@authBLP.response(200, ProtectedSchema)
@jwt_required()
def user(data):
    """Route protégée nécessitant un token JWT"""
    identity = get_jwt_identity()
    return {"logged_in_as": identity}
