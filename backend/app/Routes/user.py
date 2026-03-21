from datetime import date, timedelta

import sqlalchemy as sa
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import getCurrentUserOrAbort401, userResponse
from app.models import HistoriquePoids, WorkoutLog, WorkoutSession
from app.schemas import (
    BaseErrorSchema,
    ExoStatQuerySchema,
    ExoStatResponseSchema,
    MessageSchema,
    UserAjouterPoidsSchema,
    UserHistoriqueResponseSchema,
    UserSchema,
    UserSuppPoidSchema,
    UserWorkoutStreakResponseSchema,
    ValidationErrorSchema,
)
from app.utils.logger import QueryTimer, db_logger, route_logger

userBLP = Blueprint("user", __name__, url_prefix="/user", description="Gestion utilisateur")


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

    with QueryTimer("checkPoidsExistant"):
        poids_existant = db.session.scalar(
            sa.select(HistoriquePoids).where(
                HistoriquePoids.user_id == user.id,
                HistoriquePoids.date == poids_date,
            )
        )

    if poids_existant:
        ancien_poids = poids_existant.poids
        poids_existant.poids = poids_val
        poids_existant.note = note
        route_logger.info(f"POIDS MODIFIER | user_id={user.id} | date={poids_date} | {ancien_poids}kg -> {poids_val}kg")
    else:
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


@userBLP.route("/getStreak", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, UserWorkoutStreakResponseSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@jwt_required()
def getStreak():
    """Récupère les jours avec séance réelle et la streak en cours"""
    user = getCurrentUserOrAbort401()
    route_logger.debug(f"GET STREAK | user_id={user.id}")

    with QueryTimer("getWorkoutDays"):
        started_at_values = db.session.scalars(
            sa.select(WorkoutSession.started_at)
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.started_at.is_not(None),
            )
            .order_by(WorkoutSession.started_at.asc())
        ).all()

    days_set = {started_at.date() for started_at in started_at_values}
    days = sorted(days_set)

    current_streak = 0
    cursor = date.today()
    while cursor in days_set:
        current_streak += 1
        cursor -= timedelta(days=1)

    route_logger.info(f"GET STREAK | user_id={user.id} | days={len(days)} | current_streak={current_streak}")
    return {"days": days, "current_streak": current_streak}


@userBLP.route("/getExoStat", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.arguments(ExoStatQuerySchema, location="query")
@userBLP.response(200, ExoStatResponseSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur non trouvé")
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getExoStat(data):
    """Récupère les statistiques d'un exercice pour l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()
    exercise_id = data["exercise_id"]

    route_logger.debug(f"GET EXO STAT | user_id={user.id} | exercise_id={exercise_id}")

    with QueryTimer("getExoStat"):
        df = WorkoutLog.getExoStat(user.id, exercise_id)

    stats = [] if df.empty else df.to_dict(orient="records")

    route_logger.info(f"GET EXO STAT | user_id={user.id} | exercise_id={exercise_id} | rows={len(stats)}")
    return {"stats": stats}


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
