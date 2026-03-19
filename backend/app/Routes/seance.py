# Blueprint pour la gestion des séances prévues
import sqlalchemy as sa
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import (
    checkExoExists,
    getCurrentUserOrAbort401,
    getPlanForSeanceOrAbort404,
    getRoutineForUserOrAbort404,
    getSeanceByIdForUserOrAbort404,
    getSeanceForRoutineAndDayOrAbort404,
    seanceResponse,
)
from app.models import SeanceExercise
from app.schemas import (
    ActiveRoutineSchema,
    AddExerciseToSeanceSchema,
    BaseErrorSchema,
    MessageSchema,
    MoveExerciseOrderSchema,
    RemoveExerciseFromSeanceSchema,
    RenameSeanceSchema,
    SeanceResponseSchema,
    SeancesResponseSchema,
    UpdateExerciseConfigSchema,
    ValidationErrorSchema,
    getSeanceByDay,
)
from app.utils.logger import QueryTimer, route_logger

seanceBLP = Blueprint("seance", __name__, url_prefix="/seance", description="Gestion des séances prévues")


@seanceBLP.route("/getSeancesPrevu", methods=["POST"])
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.arguments(ActiveRoutineSchema)
@seanceBLP.response(200, SeancesResponseSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune routine active ou aucune séance trouvée")
@jwt_required()
def getSeancesPrevu(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    route_logger.info(f"GET SEANCES | user_id={user.id} | routine={routine.id}")
    seances = [seanceResponse(s) for s in routine.seances]
    if not seances:
        abort(404, message="Aucune séance trouvée pour la routine active.")
    return {"seances": seances}


@seanceBLP.route("/ajouterExoSeance", methods=["POST"])
@seanceBLP.arguments(AddExerciseToSeanceSchema)
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.response(201, MessageSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice introuvable")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def ajouterExoSeance(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    exercise = checkExoExists(data["exercise_id"])
    if not exercise:
        abort(404, message="Exercice non trouvé.")

    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    plan = seance.ajouterPlan(exercise, data["planned_sets"], data["planned_reps"], data["planned_weight"])

    db.session.commit()
    route_logger.info(
        f"SEANCE EXO ADDED | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | day={seance.day.value} | exercise_id={exercise.id} | ordre={plan.ordre}"
    )
    return {"message": "Exercice ajouté à la séance avec succès."}


@seanceBLP.route("/deplacerOrdreExoSeance", methods=["POST"])
@seanceBLP.arguments(MoveExerciseOrderSchema)
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.response(200, MessageSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def deplacerOrdreExoSeance(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    try:
        moved = seance.moveExercice(data["seance_exercise_id"], data["direction"])
    except ValueError:
        abort(404, message="Exercice prévu non trouvé dans cette séance.")
    with QueryTimer("commitMoveExerciseOrder"):
        db.session.commit()
    if not moved:
        if data["direction"] == "up":
            route_logger.info(
                f"SEANCE EXO ORDER | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | plan_id={data['seance_exercise_id']} | direction=up"
            )
            return {"message": "Exercice déjà en première position."}
        route_logger.info(
            f"SEANCE EXO ORDER | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | plan_id={data['seance_exercise_id']} | direction=down"
        )
        return {"message": "Exercice déjà en dernière position."}
    route_logger.info(
        f"SEANCE EXO ORDER MOVED | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | plan_id={data['seance_exercise_id']} | direction={data['direction']}"
    )
    return {"message": "Ordre de l'exercice mis à jour avec succès."}


@seanceBLP.route("/getSeanceDuJour", methods=["POST"])
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.arguments(getSeanceByDay)
@seanceBLP.response(200, SeanceResponseSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Séance non trouvée")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getSeanceDuJour(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    return {"seance": seanceResponse(seance)}


@seanceBLP.route("/changerConfigurationExo", methods=["POST"])
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.arguments(UpdateExerciseConfigSchema)
@seanceBLP.response(200, MessageSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def changerConfigurationExo(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    plan = getPlanForSeanceOrAbort404(seance, data["seance_exercise_id"])
    plan.updateConfig(data["planned_sets"], data["planned_reps"], data["planned_weight"])
    db.session.commit()
    route_logger.info(
        f"SEANCE EXO CONFIG UPDATED | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | plan_id={plan.id} | sets={plan.planned_sets} | reps={plan.planned_reps} | weight={plan.planned_weight}"
    )
    return {"message": "Configuration de l'exercice mise à jour avec succès."}


@seanceBLP.route("/modifierNomSeance", methods=["POST"])
@seanceBLP.arguments(RenameSeanceSchema)
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.response(200, MessageSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Séance introuvable")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modifierNomSeance(data):
    user = getCurrentUserOrAbort401()
    seance = getSeanceByIdForUserOrAbort404(user, data["seance_id"])
    old_title = seance.title
    seance.title = data["title"]
    with QueryTimer("commitUpdateSeanceTitle"):
        db.session.commit()
    route_logger.info(
        f"SEANCE TITLE UPDATED | user_id={user.id} | seance_id={seance.id} | old_title={old_title} | new_title={seance.title}"
    )
    return {"message": "Nom de la séance mis à jour avec succès."}


@seanceBLP.route("/supprimerExoSeance", methods=["DELETE"])
@seanceBLP.arguments(RemoveExerciseFromSeanceSchema)
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.response(200, MessageSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def supprimerExoSeance(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    seance = getSeanceForRoutineAndDayOrAbort404(routine, data["day"])
    with QueryTimer("checkExoPlanExistant"):
        plan = db.session.scalar(
            sa.select(SeanceExercise).where(
                SeanceExercise.id == data["seance_exercise_id"],
                SeanceExercise.seance_id == seance.id,
            )
        )
    if not plan:
        abort(404, message="Exercice prévu non trouvé dans cette séance.")
    planIdRemoved = plan.id
    exerciceIdRemoved = plan.exercise_id
    with QueryTimer("commitDeleteExercisePlan"):
        db.session.delete(plan)
        db.session.flush()
        remaining_plans = db.session.scalars(
            sa.select(SeanceExercise)
            .where(SeanceExercise.seance_id == seance.id)
            .order_by(SeanceExercise.ordre, SeanceExercise.id)
        ).all()
        for index, remaining_plan in enumerate(remaining_plans, start=1):
            remaining_plan.ordre = index
        if remaining_plans:
            seance.is_rest_day = False
        else:
            seance.is_rest_day = True
            seance.title = "Jour de Repos"
        db.session.commit()
    route_logger.info(
        f"SEANCE EXO DELETED | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | plan_id={planIdRemoved} | exercise_id={exerciceIdRemoved}"
    )
    return {"message": "Exercice supprimé de la séance avec succès."}
