from datetime import date

import sqlalchemy as sa
from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app import Config, db
from app.models import HistoriquePoids, User
from app.schemas import (
    BaseErrorSchema,
    LoginSchema,
    MessageSchema,
    RegisterSchema,
    TokenSchema,
    UserAjouterPoidsSchema,
    UserChangementMdpSchema,
    UserChangementUsernameSchema,
    UserConfigurerSchema,
    UserHistoriqueResponseSchema,
    UserSchema,
    UserSuppPoidSchema,
    ValidationErrorSchema,
)
from app.smart_client import SmartApiClient
from app.utils.logger import QueryTimer, auth_logger, db_logger, route_logger

authBLP = Blueprint("auth", __name__, url_prefix="/auth", description="Authentification")
userBLP = Blueprint("user", __name__, url_prefix="/user", description="Gestion utilisateur")
userOptionBLP = Blueprint("option", __name__, url_prefix="/user/option", description="Option utilisateur")

headers = {"x-rapidapi-host": Config.X_RAPID_API_HOST, "x-rapidapi-key": Config.X_RAPID_API_KEY}

APISPORT = SmartApiClient(
    "https://edb-with-videos-and-images-by-ascendapi.p.rapidapi.com/api/v1/",
    headers=headers,
)


def getCurrentUserOrAbort401() -> User:
    """Récupère l'utilisateur courant via le JWT ou abort 401"""
    user_id = get_jwt_identity()
    route_logger.debug(f"Résolution JWT identity: user_id={user_id}")

    with QueryTimer("getCurrentUser"):
        user = db.session.scalar(sa.select(User).where(User.id == user_id))

    if user is None:
        auth_logger.warning(f"AUTH FAIL | JWT valide mais user introuvable | user_id={user_id}")
        abort(401, message="Utilisateur non trouvé")

    route_logger.debug(f"Utilisateur résolu: id={user.id} username={user.username}")
    return user


def userResponse(user: User) -> dict:
    """Construit le dict de réponse standard pour un utilisateur"""
    dernier_poids = user.historique_poids[-1].poids if user.historique_poids else None
    route_logger.debug(f"Construction réponse user | id={user.id}")
    return {
        "username": user.username,
        "date_naissance": user.date_naissance,
        "taille": user.taille,
        "dernierPoids": dernier_poids,
    }


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


@userBLP.route("/user", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, UserSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def user():
    """Récupère le profil de l'utilisateur connecté"""
    current_user = getCurrentUserOrAbort401()
    route_logger.info(f"GET PROFILE | user_id={current_user.id} | username={current_user.username}")
    return userResponse(current_user)


@userBLP.route("/ajouterOuModifierPoids", methods=["POST"])
@userBLP.arguments(UserAjouterPoidsSchema)
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, MessageSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def ajouterOuModifierPoids(data):
    """Ajoute ou modifie un poids dans l'historique de l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()
    poids_date = data.get("date", date.today())
    poids_val = data["poids"]
    note = data.get("note")

    route_logger.info(f"POIDS EXISTE T'IL ?  | user_id={user.id} | date={poids_date} | poids={poids_val}kg | note={note!r}")

    # Cherche si une entrée existe pour cette date
    with QueryTimer("checkPoidsExistant"):
        poids_existant = db.session.scalar(
            sa.select(HistoriquePoids).where(
                HistoriquePoids.user_id == user.id,
                HistoriquePoids.date == poids_date,
            )
        )

    if poids_existant:
        ancien_poids = poids_existant.poids
        # Modifie l'entrée existante
        poids_existant.poids = poids_val
        poids_existant.note = note
        route_logger.info(f"POIDS MODIFIER | user_id={user.id} | date={poids_date} | {ancien_poids}kg -> {poids_val}kg")
    else:
        # Crée une nouvelle entrée
        poids_existant = HistoriquePoids(user_id=user.id, poids=poids_val, date=poids_date, note=note)  # type: ignore
        db.session.add(poids_existant)
        route_logger.info(f"POIDS AJOUTER | user_id={user.id} | date={poids_date} | {poids_val}kg")

    with QueryTimer("commitPoids"):
        db.session.commit()
    db.session.refresh(user)

    db_logger.debug(f"MODIFICATION, AJOUT SUCCESS | user_id={user.id} | date={poids_date}")
    return {"message": "Poids ajouter ou modifier correctement!"}


@userBLP.route("/suprimerPoid", methods=["DELETE"])
@userBLP.arguments(UserSuppPoidSchema)
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, MessageSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(404, schema=BaseErrorSchema, description="Donnée non présente")
@jwt_required()
def suprimerPoid(data):
    """Ajoute ou modifie un poids dans l'historique de l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()
    date = data.get("date")

    route_logger.info(f"POIDS DELETE | user_id={user.id} | date={date}")

    # Cherche si une entrée existe pour cette date
    with QueryTimer("checkPoidsExistant"):
        poids_existant = db.session.scalar(
            sa.select(HistoriquePoids).where(
                HistoriquePoids.user_id == user.id,
                HistoriquePoids.date == date,
            )
        )

    if poids_existant:
        poids_val = poids_existant.poids
        db.session.delete(poids_existant)
        with QueryTimer("commitDeletePoids"):
            db.session.commit()
        route_logger.info(f"POIDS SUPPRIME | user_id={user.id} | date={date} | poids_supprimé={poids_val}kg")
        return {"message": "Poids supprimé correctement!"}
    else:
        route_logger.warning(f"POIDS NON TROUVE | user_id={user.id} | date={date}")
        abort(404, message="Poid non présent")

    db.session.refresh(user)
    return {"message": "Poids ajouter ou modifier correctement!"}


@userBLP.route("/getAllPoids", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, UserHistoriqueResponseSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def getAllPoids():
    """Récupère tout l'historique des poids de l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()
    route_logger.debug(f"GET ALL POIDS | user_id={user.id}")

    df = user.getHistoriquePoidsPanda()
    historique = df.to_dict(orient="records") if not df.empty else []

    return {"historique": historique}


@userBLP.route("/supprimer", methods=["DELETE"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, MessageSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def supprimer_utilisateur():
    """Supprime l'utilisateur connecté et son historique"""
    user = getCurrentUserOrAbort401()
    user_id = user.id
    username = user.username

    route_logger.warning(f"USER DELETE | Suppression du compte | user_id={user_id} username={username}")

    with QueryTimer("deleteUser"):
        db.session.delete(user)
        db.session.commit()

    route_logger.info(f"USER DELETE | user_id={user_id} username={username}")
    return {"message": "Utilisateur supprimé avec succès"}


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

    with QueryTimer("checkUsernameExists"):
        existing = db.session.scalar(sa.select(User).where(User.username == new_username))

    if existing:
        route_logger.warning(f"USERNAME CHANGE CONFLICT | user_id={user.id} | {new_username} déjà pris")
        abort(409, message="Nom d'utilisateur déjà pris")

    user.username = new_username
    with QueryTimer("commitUsernameChange"):
        db.session.commit()

    route_logger.info(f"USERNAME CHANGED | user_id={user.id} | {old_username} -> {new_username}")
    return {"message": "Nom d'utilisateur changé avec succès"}


@userOptionBLP.route("/liveness", methods=["GET"])
@userOptionBLP.doc(security=[{"bearerAuth": []}])
@userOptionBLP.response(200)
def liveness():
    "Check si l'api de sport est en ligne"
    response = APISPORT.get("/liveness", useCache=False)

    return response
