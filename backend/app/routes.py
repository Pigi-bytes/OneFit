from datetime import date

import sqlalchemy as sa
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app import db
from app.models import HistoriquePoids, User
from app.schemas import (
    AuthErrorResponseSchema,
    ChangementMdpInvalideSchema,
    ChangementMdpReussiSchema,
    LoginSchema,
    MessageSchema,
    RegisterErrorResponseSchema,
    RegisterSchema,
    TokenSchema,
    UserAjouterPoidsSchema,
    UserChangementMdp,
    UserConfigurer,
    UserHistoriqueResponse,
    UserNotFoundErrorSchema,
    UserSchema,
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


@userBLP.route("/ajouterOuModifierPoids", methods=["POST"])
@userBLP.arguments(UserAjouterPoidsSchema)
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, UserSchema)
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(401, schema=UserNotFoundErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def ajouterOuModifierPoids(data):
    """Ajoute ou modifie un poids dans l'historique de l'utilisateur connecté"""
    id = get_jwt_identity()
    user = db.session.scalar(sa.select(User).where(User.id == id))
    if user is None:
        abort(401, message="User not found")

    poids_date = data.get("date", date.today())

    # Cherche si une entrée existe pour cette date
    poids_existant = db.session.scalar(
        sa.select(HistoriquePoids).where((HistoriquePoids.user_id == user.id) & (HistoriquePoids.date == poids_date))
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
    dernier_poids = user.historique_poids[-1].poids if user.historique_poids else None
    return {
        "username": user.username,
        "date_naissance": user.date_naissance,
        "taille": user.taille,
        "dernierPoids": dernier_poids,
    }


@userBLP.route("/configurer", methods=["POST"])
@userBLP.arguments(UserConfigurer)
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, UserSchema)
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(401, schema=UserNotFoundErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def configurerUser(data):
    """Configure la date de naissance et la taille de l'utilisateur"""
    id = get_jwt_identity()
    user = db.session.scalar(sa.select(User).where(User.id == id))
    if user is None:
        abort(401, message="User not found")

    if "date_naissance" in data and data.get("date_naissance"):
        user.date_naissance = data.get("date_naissance")
    if "taille" in data and data.get("taille"):
        user.taille = data.get("taille")

    db.session.commit()
    db.session.refresh(user)

    dernier_poids = user.historique_poids[-1].poids if user.historique_poids else None
    return {
        "username": user.username,
        "date_naissance": user.date_naissance,
        "taille": user.taille,
        "dernierPoids": dernier_poids,
    }


@userBLP.route("/modifierMDP", methods=["POST"])
@userBLP.arguments(UserChangementMdp)
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, ChangementMdpReussiSchema)
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(401, schema=UserNotFoundErrorSchema, description="Utilisateur non trouvé")
@userBLP.alt_response(401, schema=ChangementMdpInvalideSchema, description="Mot de passe invalide")
@jwt_required()
def modifierMDP(data):
    "Changer le mot de passe de l'utilisateur"
    id = get_jwt_identity()
    user = db.session.scalar(sa.select(User).where(User.id == id))
    if user is None:
        abort(401, message="User not found")

    password = data.get("password")
    newPassword = data.get("new_password")
    if user.checkPassword(password):
        user.password = generate_password_hash(newPassword)
        db.session.commit()
        db.session.refresh(user)
        return {"message": "Mot de passe changé avec succès"}

    abort(401, message="Mot de passe actuel invalide")


@userBLP.route("/getAllPoids", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, schema=UserHistoriqueResponse)
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(401, schema=UserNotFoundErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def getAllPoids():
    """Récupère tout l'historique des poids de l'utilisateur connecté"""
    id = get_jwt_identity()
    user = db.session.scalar(sa.select(User).where(User.id == id))
    if user is None:
        abort(401, message="User not found")

    df = user.getHistoriquePoidsPanda()
    historique = df.to_dict(orient="records") if not df.empty else []
    return {"historique": historique}
