import sqlalchemy as sa
from flask_jwt_extended import get_jwt_identity
from flask_smorest import abort

from app import Config, db
from app.models import DayOfWeek, Exercise, Routine, Seance, SeanceExercise, User
from app.smart_client import SmartApiClient
from app.utils.logger import QueryTimer, auth_logger, route_logger

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


def getRoutineForUserOrAbort404(user: User, routineId: int, queryNameLog: str = "checkRoutineExistant"):
    """Récupère une routine de l'utilisateur (ou active si -1) et abort 404 si introuvable"""
    if routineId == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer(queryNameLog):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == routineId, Routine.user_id == user.id))

    if routine is None:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    return routine


def getSeanceForRoutineAndDayOrAbort404(routine: Routine, day: str, queryNameLog: str = "checkSeanceExistant"):
    """Récupère la séance d'une routine pour un jour donné ou abort 404"""
    with QueryTimer(queryNameLog):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(day)))

    if seance is None:
        abort(404, message="Séance non trouvée pour ce jour.")

    return seance


def exerciseResponse(exercise: Exercise):
    """Construit le dict de réponse standard pour un exercice"""
    return {
        "idExo": exercise.id_api,
        "name": exercise.name,
        "img_url": exercise.img_url,
        "video_url": exercise.video_url,
        "overview": exercise.overview,
        "instructions": exercise.instructions,
        "body_part": exercise.body_part,
    }


def plannedExerciseResponse(plan: SeanceExercise):
    """Construit le dict de réponse standard d'un exercice planifié"""
    return {
        "seance_exercise_id": plan.id,
        "exoId": plan.exercise.id_api,
        "name": plan.exercise.name,
        "ordre": plan.ordre,
        "planned_sets": plan.planned_sets,
        "planned_reps": plan.planned_reps,
        "planned_weight": plan.planned_weight,
        "img_url": plan.exercise.img_url,
    }


def seanceResponse(seance: Seance):
    """Construit le dict de réponse standard pour une séance planifiée"""
    return {
        "id": seance.id,
        "routine_id": seance.routine_id,
        "day": seance.day.value,
        "title": seance.title,
        "is_rest_day": seance.is_rest_day,
        "exercises": [plannedExerciseResponse(plan) for plan in seance.trieParOrdre()],
    }
