from datetime import date

import sqlalchemy as sa
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
    ValidationErrorSchema,
)
from app.smart_client import SmartApiClient

authBLP = Blueprint("auth", __name__, url_prefix="/auth", description="Authentification")
userBLP = Blueprint("user", __name__, url_prefix="/user", description="Gestion utilisateur")
userOptionBLP = Blueprint("option", __name__, url_prefix="/user/option", description="Option utilisateur")


def getCurrentUserOrAbort401() -> User:
    """Récupère l'utilisateur courant via le JWT ou abort 401"""
    user_id = get_jwt_identity()
    user = db.session.scalar(sa.select(User).where(User.id == user_id))
    if user is None:
        abort(401, message="Utilisateur non trouvé")
    return user


def userResponse(user: User) -> dict:
    """Construit le dict de réponse standard pour un utilisateur"""
    dernier_poids = user.historique_poids[-1].poids if user.historique_poids else None
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
    user = db.session.scalar(sa.select(User).where(User.username == data["username"]))

    if user is None or not user.checkPassword(data["password"]):
        abort(401, message="Identifiants invalides")

    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token}


@authBLP.route("/inscription", methods=["POST"])
@authBLP.arguments(RegisterSchema)
@authBLP.response(201, MessageSchema)
@authBLP.alt_response(409, schema=BaseErrorSchema, description="Nom d'utilisateur déjà pris")
@authBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def inscription(data):
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
@userBLP.response(200, UserSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def user():
    """Récupère le profil de l'utilisateur connecté"""
    return userResponse(getCurrentUserOrAbort401())


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

    # Cherche si une entrée existe pour cette date
    poids_existant = db.session.scalar(
        sa.select(HistoriquePoids).where(
            HistoriquePoids.user_id == user.id,
            HistoriquePoids.date == poids_date,
        )
    )

    if poids_existant:
        # Modifie l'entrée existante
        poids_existant.poids = data["poids"]
        poids_existant.note = data.get("note")
    else:
        # Crée une nouvelle entrée
        poids_existant = HistoriquePoids(user_id=user.id, poids=data["poids"], date=poids_date, note=data.get("note"))  # type: ignore
        db.session.add(poids_existant)

    db.session.commit()
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
    db.session.delete(user)
    db.session.commit()
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

    if data.get("date_naissance") is not None:
        user.date_naissance = data["date_naissance"]
    if data.get("taille") is not None:
        user.taille = data["taille"]

    db.session.commit()
    db.session.refresh(user)
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

    if not user.checkPassword(data["password"]):
        abort(401, message="Mot de passe actuel invalide")

    user.password = generate_password_hash(data["new_password"])
    db.session.commit()
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

    existing = db.session.scalar(sa.select(User).where(User.username == new_username))
    if existing:
        abort(409, message="Nom d'utilisateur déjà pris")

    user.username = new_username
    db.session.commit()
    return {"message": "Nom d'utilisateur changé avec succès"}

@userOptionBLP.route("/liveness", methods=["GET"])
@userOptionBLP.doc(security=[{"bearerAuth": []}])
@userOptionBLP.response(200)
def liveness():
    "Check si l'api de sport est en ligne"
    headers = {"x-rapidapi-host": Config.X_RAPID_API_HOST, "x-rapidapi-key": Config.X_RAPID_API_KEY}

    client = SmartApiClient()
    response = client.get("https://edb-with-videos-and-images-by-ascendapi.p.rapidapi.com/api/v1/liveness", headers=headers)

    return response
