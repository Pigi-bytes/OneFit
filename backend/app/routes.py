from datetime import date

import sqlalchemy as sa
from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from werkzeug.security import generate_password_hash

from app import Config, db
from app.models import DayOfWeek, Exercise, HistoriquePoids, Routine, Seance, User
from app.schemas import (
    BaseErrorSchema,
    CreateRoutineSchema,
    ExerciceRequestSchema,
    ExerciceResponseSchema,
    LoginSchema,
    MessageSchema,
    RegisterSchema,
    RoutinesResponseSchema,
    SalleSchema,
    SalleSchemaByLoc,
    SeancesResponseSchema,
    SearchExoRequestSchema,
    SearchExoResponseSchema,
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
externeBLP = Blueprint("externe", __name__, url_prefix="/externe", description="Call a l'autre api")
sportBLP = Blueprint("sport", __name__, url_prefix="/sport", description="Pour gerer tout ce qui est lié a la séance/routine/exo")

APISPORT = SmartApiClient(
    "https://edb-with-videos-and-images-by-ascendapi.p.rapidapi.com/api/v1/",
    headers={"x-rapidapi-host": Config.X_RAPID_API_HOST, "x-rapidapi-key": Config.X_RAPID_API_KEY},
)

APISALLE = SmartApiClient(
    "https://places-api.foursquare.com/places/",
    headers={"X-Places-Api-Version": "2025-06-17", "accept": "application/json", "Authorization": f"Bearer {Config.SALLE_KEY}"},
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


@externeBLP.route("/salle", methods=["POST"])
@externeBLP.arguments(SalleSchema)
@externeBLP.response(200)
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def getSalle(data):
    "trouve les salles en fonction d'un nom de ville"

    route_logger.info(f"SALLE SEARCH | ville={data['ville']}")

    params = {"near": data["ville"], "limit": 50, "query": "gym"}
    response = APISALLE.get("search", params=params, useCache=True)

    return response


@externeBLP.route("/salleByLoc", methods=["POST"])
@externeBLP.arguments(SalleSchemaByLoc)
@externeBLP.response(200)
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def getSalleLoc(data):
    "trouve les salles en fonction d'un nom de ville"

    route_logger.info(f"SALLE LOC SEARCH | lat={data['lat']} | lng={data['lng']}")

    params = {"ll": f"{data['lat']},{data['lng']}", "limit": 50, "query": "gym"}
    response = APISALLE.get("search", params=params, useCache=True)

    return response


@externeBLP.route("/getExo", methods=["POST"])
@externeBLP.arguments(ExerciceRequestSchema)
@externeBLP.doc(security=[{"bearerAuth": []}])
@externeBLP.response(200, ExerciceResponseSchema)
@externeBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération de l'exercice")
@externeBLP.alt_response(404, schema=BaseErrorSchema, description="Exercice non trouvé sur l'API externe")
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getExo(data):
    """Récupère un exercice depuis la BDD si existant, sinon depuis l'API externe puis le sauvegarde"""

    idExo = data["exoId"]
    if not idExo:
        abort(400, message="exerciseId manquant")

    route_logger.info(f"EXO FETCH ATTEMPT | user_id={get_jwt_identity()} | exoId={idExo}")

    exo = db.session.scalar(sa.select(Exercise).where(Exercise.id_api == idExo))
    if exo:
        route_logger.warning(f"EXO FETCH FAIL | user_id={get_jwt_identity()} | exoId={idExo}")
        return {
            "idExo": exo.id_api,
            "name": exo.name,
            "img_url": exo.img_url,
            "video_url": exo.video_url,
            "overview": exo.overview,
            "instructions": exo.instructions,
            "body_part": exo.body_part,
        }

    exo = APISPORT.get(f"exercises/{idExo}")
    if not exo:
        abort(404, message="Erreur lors de la récupération de l'exercice externe")

    exercise = Exercise(
        id_api=exo["exerciseId"],
        name=exo["name"],
        img_url=exo["imageUrl"],
        video_url=exo["videoUrl"],
        overview=exo["overview"],
        instructions="\n".join(exo["instructions"]) if isinstance(exo["instructions"], list) else exo["instructions"],
        body_part=", ".join(exo["bodyParts"]) if isinstance(exo["bodyParts"], list) else exo["bodyParts"],
    )

    db.session.add(exercise)
    db.session.commit()
    route_logger.info(f"EXO CREATED | user_id={get_jwt_identity()} | exoId={exercise.id_api}")

    return {
        "idExo": exercise.id_api,
        "name": exercise.name,
        "img_url": exercise.img_url,
        "video_url": exercise.video_url,
        "overview": exercise.overview,
        "instructions": exercise.instructions,
        "body_part": exercise.body_part,
    }


@externeBLP.route("/searchExo", methods=["POST"])
@externeBLP.arguments(SearchExoRequestSchema)
@externeBLP.doc(security=[{"bearerAuth": []}])
@externeBLP.response(200, SearchExoResponseSchema)
@externeBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération des exercices")
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def searchExo(data):
    """Recherche des exercices par nom (fuzzy matching) et retourne les n plus proches."""

    recherche = data["recherche"]
    n = int(data["limit"])

    route_logger.info(f"EXO SEARCH | recherche={recherche} | limit={n}")
    params = {"search": recherche, "limit": n}
    response = APISPORT.get("exercises/search", params=params)

    if not response:
        route_logger.warning(f"EXO SEARCH FAIL | recherche={recherche}")
        abort(400, message="Erreur")

    resultat = [(exo["name"], exo["exerciseId"], exo["imageUrl"]) for exo in response]
    return {"resultats": resultat}


@sportBLP.route("/getRoutine", methods=["GET"])
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, RoutinesResponseSchema)
@sportBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération des routines")
@sportBLP.alt_response(400, schema=BaseErrorSchema, description="Aucune routine trouvée")
@jwt_required()
def getRoutines():
    """Renvoie toutes les routines de l'utilisateur, avec indication de la routine active"""
    user = getCurrentUserOrAbort401()
    route_logger.info(f"GET ROUTINES | user_id={user.id}")

    routines = [{"id": r.id, "name": r.name, "is_active": r.is_active} for r in user.routines]

    if not routines:
        route_logger.warning(f"Aucune routine trouvé | user_id={user.id}")

        abort(404, message="Aucune routine trouvée pour cet utilisateur.")

    return {"routines": routines}


@sportBLP.route("/getSeancesPrevu", methods=["GET"])
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, SeancesResponseSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune routine active ou aucune séance trouvée")
@jwt_required()
def getSeancesPrevu():
    """
    Renvoie les séances de la routine active de l'utilisateur avec la liste des exercices prévus (par jour)
    """
    user = getCurrentUserOrAbort401()

    routine = user.activeRoutine()
    route_logger.info(f"GET SEANCES | user_id={user.id} | routine={routine.id}")
    if not routine:
        route_logger.warning(f"Aucune routine trouvé | user_id={user.id}")
        abort(404, message="Aucune routine active trouvée pour cet utilisateur")

    seances = []
    for s in routine.seances:
        seances.append(
            {
                "id": s.id,
                "routine_id": s.routine_id,
                "day": s.day.value,
                "title": s.title,
                "is_rest_day": s.is_rest_day,
                "exercises": [
                    {
                        "id": plan.id,
                        "exercise_id": plan.exercise_id,
                        "name": plan.exercise.name,
                        "ordre": plan.ordre,
                        "planned_sets": plan.planned_sets,
                        "planned_reps": plan.planned_reps,
                        "planned_weight": plan.planned_weight,
                        "img_url": plan.exercise.img_url,
                    }
                    for plan in sorted(s.exercises_plan, key=lambda x: x.ordre)
                ],
            }
        )

    if not seances:
        abort(404, message="Aucune séance trouvée pour la routine active.")

    return {"seances": seances}


@sportBLP.route("/createRoutine", methods=["POST"])
@sportBLP.arguments(CreateRoutineSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(201, MessageSchema)
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def createRoutine(data):
    """Crée une nouvelle routine et initialise 7 jours de repos, on met cette routine a active"""
    user = getCurrentUserOrAbort401()

    routine = Routine(user_id=user.id, name=data["name"], is_active=False)
    db.session.add(routine)
    db.session.flush()  # Permet de générer l'id de la routine sans faire un commit complet

    for day in DayOfWeek:
        seance = Seance(routine_id=routine.id, day=day, title="Jour de Repos", is_rest_day=True)
        db.session.add(seance)

    user.setActiveRoutine(routine.id)
    db.session.commit()
    route_logger.info(f"ROUTINE CREATED | user_id={user.id} | routine_id={routine.id}")

    return {"message": "Routine créée !"}
