from flask import request
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app import db
from app.communRoutes import checkUserExistsByUsername, getCurrentUserOrAbort401, userResponse
from app.schemas import (
    BaseErrorSchema,
    MessageSchema,
    UserChangementMdpSchema,
    UserChangementUsernameSchema,
    UserConfigurerSchema,
    UserSchema,
    ValidationErrorSchema,
)
from app.utils.logger import QueryTimer, auth_logger, route_logger

userOptionBLP = Blueprint("option", __name__, url_prefix="/user/option", description="Option utilisateur")


@userOptionBLP.route("/configurer", methods=["POST"])
@userOptionBLP.arguments(UserConfigurerSchema)
@userOptionBLP.doc(security=[{"bearerAuth": []}])
@userOptionBLP.response(200, UserSchema)
@userOptionBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@userOptionBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def configurerUser(data):
    """Configure la date de naissance et la taille de l'utilisateur"""
    user = getCurrentUserOrAbort401()

    changes = []
    if data.get("date_naissance") is not None:
        old_val = user.date_naissance
        user.date_naissance = data["date_naissance"]
        changes.append(f"date_naissance: {old_val} -> {data['date_naissance']}")
    if data.get("taille") is not None:
        old_val = user.taille
        user.taille = data["taille"]
        changes.append(f"taille: {old_val}cm -> {data['taille']}cm")

    if changes:
        route_logger.info(f"USER CONFIGURE | user_id={user.id} | {' | '.join(changes)}")
        with QueryTimer("commitConfigure"):
            db.session.commit()
        db.session.refresh(user)
    else:
        route_logger.debug(f"USER CONFIGURE | user_id={user.id} | Aucune modification")

    return userResponse(user)


@userOptionBLP.route("/modifierMDP", methods=["POST"])
@userOptionBLP.arguments(UserChangementMdpSchema)
@userOptionBLP.doc(security=[{"bearerAuth": []}])
@userOptionBLP.response(200, MessageSchema)
@userOptionBLP.alt_response(401, schema=BaseErrorSchema, description="Non authentifié ou mot de passe invalide")
@userOptionBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modifierMDP(data):
    """Changer le mot de passe de l'utilisateur"""
    user = getCurrentUserOrAbort401()

    auth_logger.info(f"Changement de password ATTEMPT | user_id={user.id} | IP={request.remote_addr}")

    if not user.checkPassword(data["password"]):
        auth_logger.warning(f"PASSWORD CHANGE FAIL | Ancien MDP incorrect | user_id={user.id} | IP={request.remote_addr}")
        abort(401, message="Mot de passe actuel invalide")

    user.password = generate_password_hash(data["new_password"])
    with QueryTimer("commitPasswordChange"):
        db.session.commit()

    auth_logger.info(f"PASSWORD CHANGER | user_id={user.id} | IP={request.remote_addr}")
    return {"message": "Mot de passe changé avec succès"}


@userOptionBLP.route("/modifierUsername", methods=["POST"])
@userOptionBLP.arguments(UserChangementUsernameSchema)
@userOptionBLP.doc(security=[{"bearerAuth": []}])
@userOptionBLP.response(200, MessageSchema)
@userOptionBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@userOptionBLP.alt_response(409, schema=BaseErrorSchema, description="Nom d'utilisateur déjà pris")
@userOptionBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modifierUsername(data):
    """Changer le nom de l'utilisateur"""
    user = getCurrentUserOrAbort401()
    new_username = data["username"]
    old_username = user.username

    route_logger.info(f"USERNAME CHANGE ATTEMPT | user_id={user.id} | {old_username} -> {new_username}")

    if checkUserExistsByUsername(data["username"]):
        route_logger.warning(f"USERNAME CHANGE CONFLICT | user_id={user.id} | {new_username} déjà pris")
        abort(409, message="Nom d'utilisateur déjà pris")

    user.username = new_username
    with QueryTimer("commitUsernameChange"):
        db.session.commit()

    route_logger.info(f"USERNAME CHANGED | user_id={user.id} | {old_username} -> {new_username}")
    return {"message": "Nom d'utilisateur changé avec succès"}
