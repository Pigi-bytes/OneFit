# Blueprint pour la gestion des séances réelles (effectuées)
from datetime import datetime

import sqlalchemy as sa
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app.communRoutes import addAndCommit

from app import db
from app.communRoutes import getCurrentUserOrAbort401, getRoutineForUserOrAbort404, getSeanceForRoutineAndDayOrAbort404
from app.models import Routine, Seance, SeanceExercise, WorkoutLog, WorkoutSession
from app.schemas import (
    AddPerformedExerciseSchema,
    BaseErrorSchema,
    MessageSchema,
    StartEndSeanceEffectueeSchema,
    TimeTotakSchema,
    ValidationErrorSchema,
    ReposSchema,
)
from app.utils.logger import QueryTimer, route_logger

seanceReelleBLP = Blueprint("seanceReelle", __name__, url_prefix="/seanceReelle", description="Gestion des séances réelles")


@seanceReelleBLP.route("/ajouterExoEffectue", methods=["POST"])
@seanceReelleBLP.arguments(AddPerformedExerciseSchema)
@seanceReelleBLP.doc(security=[{"bearerAuth": []}])
@seanceReelleBLP.response(201, MessageSchema)
@seanceReelleBLP.alt_response(404, schema=BaseErrorSchema, description="Exercice prévu introuvable")
@seanceReelleBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def ajouterExoEffectue(data):
    user = getCurrentUserOrAbort401()
    with QueryTimer("checkExoPlanForUser"):
        plan = db.session.scalar(
            sa.select(SeanceExercise)
            .join(Seance, SeanceExercise.seance_id == Seance.id)
            .join(Routine, Seance.routine_id == Routine.id)
            .where(
                SeanceExercise.id == data["seance_exercise_id"],
                Routine.user_id == user.id,
            )
        )
    if not plan:
        abort(404, message="Exercice prévu non trouvé ou n'appartient pas à l'utilisateur")
    workout_logs = [
        WorkoutLog(
            user_id=user.id,
            exercise_id=plan.exercise_id,
            seance_id=plan.seance_id,
            reps=set_data["reps"],
            weight=set_data["weight"],
        )
        for set_data in data["sets"]
    ]
    with QueryTimer("commitAddPerformedSets"):
        db.session.add_all(workout_logs)
        db.session.commit()
    route_logger.info(
        f"WORKOUT LOG ADDED | user_id={user.id} | plan_id={plan.id} | seance_id={plan.seance_id} | exercise_id={plan.exercise_id} | sets={len(workout_logs)}"
    )
    return {"message": f"{len(workout_logs)} sets effectués ajoutés."}


@seanceReelleBLP.route("/startSeanceEffectuee", methods=["POST"])
@seanceReelleBLP.arguments(StartEndSeanceEffectueeSchema)
@seanceReelleBLP.doc(security=[{"bearerAuth": []}])
@seanceReelleBLP.response(201, MessageSchema)
@seanceReelleBLP.alt_response(404, schema=BaseErrorSchema, description="Séance introuvable")
@seanceReelleBLP.alt_response(409, schema=BaseErrorSchema, description="Séance déjà en cours ou jour de repos")
@seanceReelleBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def startSeanceEffectuee(data):
    user = getCurrentUserOrAbort401()
    with QueryTimer("checkActiveWorkoutSession"):
        active_session = db.session.scalar(
            sa.select(WorkoutSession).where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.ended_at.is_(None),
            )
        )
    if active_session:
        abort(409, message="Une séance effectuée est déjà en cours.")
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    if seance.is_rest_day:
        abort(409, message="Impossible de démarrer une séance sur un jour de repos.")
    session = WorkoutSession(user_id=user.id, seance_id=seance.id)
    with QueryTimer("commitStartWorkoutSession"):
        db.session.add(session)
        db.session.commit()
        db.session.refresh(session)
    route_logger.info(
        f"WORKOUT SESSION STARTED | user_id={user.id} | session_id={session.id} | seance_id={session.seance_id} | start_time={session.started_at}"
    )
    return {"message": "Séance effectuée démarrée."}


@seanceReelleBLP.route("/endSeanceEffectuee", methods=["POST"])
@seanceReelleBLP.arguments(StartEndSeanceEffectueeSchema)
@seanceReelleBLP.doc(security=[{"bearerAuth": []}])
@seanceReelleBLP.response(200, TimeTotakSchema)
@seanceReelleBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou session active introuvable")
@seanceReelleBLP.alt_response(409, schema=BaseErrorSchema, description="Séance déjà terminée")
@seanceReelleBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def endSeanceEffectuee(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    with QueryTimer("checkWorkoutSessionForUser"):
        session = db.session.scalar(
            sa.select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user.id,
                WorkoutSession.seance_id == seance.id,
                WorkoutSession.ended_at.is_(None),
            )
            .order_by(WorkoutSession.started_at.desc())
        )
    if not session:
        abort(404, message="Aucune séance effectuée en cours pour cette routine et ce jour.")
    session.ended_at = datetime.utcnow()
    with QueryTimer("commitEndWorkoutSession"):
        db.session.commit()
    route_logger.info(
        f"WORKOUT SESSION ENDED | user_id={user.id} | session_id={session.id} | seance_id={session.seance_id} | start_time={session.started_at} | end_time={session.ended_at} "
    )
    return {
        "message": "Séance effectuée terminée.",
        "time": int((session.ended_at - session.started_at).total_seconds()),
    }


@seanceReelleBLP.route("/abandonSeanceReelle", methods=["DELETE"])
@seanceReelleBLP.doc(security=[{"bearerAuth": []}])
@seanceReelleBLP.response(200, MessageSchema)
@seanceReelleBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune séance en cours")
@jwt_required()
def abandonSeanceReelle():
    user = getCurrentUserOrAbort401()

    # Récupérer la session active
    with QueryTimer("findActiveSessionToAbort"):
        session = db.session.scalar(
            sa.select(WorkoutSession).where(WorkoutSession.user_id == user.id, WorkoutSession.ended_at.is_(None))
        )

    if not session:
        abort(404, message="Aucune séance en cours à annuler.")

    # Supprimer les logs enregistrés durant cette session
    # On se base sur le seance_id et le fait que les logs soient arrivés après started_at
    with QueryTimer("deleteWorkoutLogsForAbortedSession"):
        db.session.execute(
            sa.delete(WorkoutLog).where(
                WorkoutLog.user_id == user.id, WorkoutLog.seance_id == session.seance_id, WorkoutLog.date >= session.started_at
            )
        )

    # Supprimer la session elle-même
    with QueryTimer("deleteActiveSession"):
        db.session.delete(session)
        db.session.commit()

    route_logger.info(f"WORKOUT SESSION ABORTED | user_id={user.id} | session_id={session.id} | seance_id={session.seance_id}")

    return {"message": "Séance annulée et données supprimées avec succès."}



@seanceReelleBLP.route("/enregSceanceRepos", methods=["POST"])
@seanceReelleBLP.arguments(ReposSchema)
@seanceReelleBLP.doc(security=[{"bearerAuth": []}])
@seanceReelleBLP.response(200, MessageSchema)
@seanceReelleBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune séance en cours")
@jwt_required()
def enrgRepo(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])

    # Récupérer la session active
    sceance = WorkoutSession(user_id=user.id,seance_id=seance.id,started_at=data["date"],ended_at=data["date"])

    addAndCommit(sceance, "commitRepos")

    return {"message": "Repos bien enregistré!"}
