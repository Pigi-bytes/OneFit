from datetime import date
from app.Routes.routine import create_routine_for_user,create_routine_Pre

from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app.communRoutes import addAndCommit, checkUserExistsByUsername
from app.models import User
from app.schemas import BaseErrorSchema, LoginSchema, MessageSchema, RegisterSchema, TokenSchema, ValidationErrorSchema
from app.utils.logger import auth_logger

authBLP = Blueprint("auth", __name__, url_prefix="/auth", description="Authentification")


@authBLP.route("/login", methods=["POST"])
@authBLP.arguments(LoginSchema)
@authBLP.response(200, TokenSchema)
@authBLP.alt_response(401, schema=BaseErrorSchema, description="Identifiants invalides")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def login(data):
    """Connexion utilisateur"""
    user = checkUserExistsByUsername(data["username"])

    if not user or not user.checkPassword(data["password"]):
        auth_logger.warning(f"LOGIN FAIL | username={data['username']}")
        abort(401, message="Identifiants invalides")

    auth_logger.info(f"LOGIN SUCCESS | username={data['username']} | user_id={user.id}")
    return {"access_token": create_access_token(identity=str(user.id))}


@authBLP.route("/inscription", methods=["POST"])
@authBLP.arguments(RegisterSchema)
@authBLP.response(201, MessageSchema)
@authBLP.alt_response(409, schema=BaseErrorSchema, description="Nom d'utilisateur déjà pris")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def inscription(data):
    """Inscription d'un nouvel utilisateur"""
    if checkUserExistsByUsername(data["username"]):
        auth_logger.warning(f"REGISTER CONFLICT | Username déjà pris | username={data['username']}")
        abort(409, message="Nom d'utilisateur déjà pris")

    user = User(
        username=data["username"], password=generate_password_hash(data["password"]), date_naissance=date.today(), taille=160
    )  # type: ignore

    addAndCommit(user, "commitInscription")

    auth_logger.info(f"REGISTER SUCCESS | username={data['username']} | user_id={user.id}")

    create_routine_for_user(user,"Nouvelle routine")
    return {"message": "User created successfully!"}
