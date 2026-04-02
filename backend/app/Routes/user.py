import smtplib
from datetime import date, timedelta
from email.message import EmailMessage

import sqlalchemy as sa
from config import Config
from email_validator import EmailNotValidError, validate_email
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import getCurrentUserOrAbort401, userResponse
from app.models import Exercise, HistoriquePoids, WorkoutLog, WorkoutSession
from app.schemas import (
    BaseErrorSchema,
    ExoStatQuerySchema,
    ExoStatResponseSchema,
    LoggedExercisesResponseSchema,
    MailSchema,
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
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
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
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
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
    return {"message": "Poids ajouté ou modifié correctement!"}


@userBLP.route("/suprimerPoid", methods=["DELETE"])
@userBLP.arguments(UserSuppPoidSchema)
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, MessageSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@userBLP.alt_response(404, schema=BaseErrorSchema, description="Donnée absente")
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
        abort(404, message="Ce poids n'est pas présent dans vos données.")

    db.session.refresh(user)
    return {"message": "Poids ajouté ou modifié correctement!"}


@userBLP.route("/getAllPoids", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, UserHistoriqueResponseSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
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
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
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


@userBLP.route("/getExoStat", methods=["POST"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.arguments(ExoStatQuerySchema)
@userBLP.response(200, ExoStatResponseSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
@userBLP.alt_response(404, schema=BaseErrorSchema, description="Exercice introuvable")
@userBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getExoStat(data):
    """Récupère les statistiques d'un exercice pour l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()
    exo_id = data["exoId"]

    with QueryTimer("checkExerciseByApiId"):
        exercise = db.session.scalar(sa.select(Exercise).where(Exercise.id_api == exo_id))
    if not exercise:
        abort(404, message="Exercice introuvable")

    route_logger.debug(f"GET EXO STAT | user_id={user.id} | exo_id={exo_id} | exercise_id={exercise.id}")

    with QueryTimer("getExoStat"):
        df = WorkoutLog.getExoStat(user.id, exercise.id)

    stats = [] if df.empty else df.to_dict(orient="records")

    route_logger.info(f"GET EXO STAT | user_id={user.id} | exo_id={exo_id} | rows={len(stats)}")
    return {"stats": stats}


@userBLP.route("/getLoggedExercises", methods=["GET"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, LoggedExercisesResponseSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
@jwt_required()
def getLoggedExercises():
    """Récupère les exercices distincts présents dans les logs de l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()

    with QueryTimer("getLoggedExercises"):
        rows = db.session.execute(
            sa.select(Exercise.id_api, Exercise.name, Exercise.img_url)
            .join(WorkoutLog, WorkoutLog.exercise_id == Exercise.id)
            .where(
                WorkoutLog.user_id == user.id,
                Exercise.id_api.is_not(None),
            )
            .distinct()
            .order_by(Exercise.name.asc())
        ).all()

    exercises = [{"exoId": exo_id, "name": name, "img": img} for exo_id, name, img in rows]
    route_logger.info(f"GET LOGGED EXERCISES | user_id={user.id} | count={len(exercises)}")
    return {"exercises": exercises}


@userBLP.route("/supprimer", methods=["DELETE"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.response(200, MessageSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Utilisateur introuvable")
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


def is_valid_email(email):
    try:
        v = validate_email(email) 
        return True
    except EmailNotValidError:
        return False


@userBLP.route("/envoyer_mail", methods=["POST"])
@userBLP.doc(security=[{"bearerAuth": []}])
@userBLP.arguments(MailSchema)
@userBLP.response(200, MessageSchema)
@userBLP.alt_response(401, schema=BaseErrorSchema, description="Adresse mail invalide")
@jwt_required()
def envoyer_mail(data):
    """Envoie un email de contact à OneFit"""
    msg = EmailMessage()

    email = data['email']
    if not is_valid_email(email):
        abort(404, message="Email invalide")
    msg['Subject'] = 'Avis OneFit'
    msg['From'] = email
    msg['To'] = 'onefit.contactsport@gmail.com'
    msg['Reply-To'] = email   
    msg.set_content(data['contenue'])

    # Envoyer via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()  # Connexion sécurisée
        smtp.login('onefit.contactsport@gmail.com', Config.ONEFIT_SMTP_PASSWORD)
        smtp.send_message(msg)
        return {"message": "Email envoyé avec succès"}
        
    
    

    
    

