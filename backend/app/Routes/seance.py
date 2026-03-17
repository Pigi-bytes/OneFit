# Blueprint pour la gestion des séances prévues
import sqlalchemy as sa
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import getCurrentUserOrAbort401
from app.models import DayOfWeek, Exercise, Routine, Seance, SeanceExercise
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
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
    route_logger.info(f"GET SEANCES | user_id={user.id} | routine={routine.id}")
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
                        "seance_exercise_id": plan.id,
                        "exoId": plan.exercise.id_api,
                        "name": plan.exercise.name,
                        "ordre": plan.ordre,
                        "planned_sets": plan.planned_sets,
                        "planned_reps": plan.planned_reps,
                        "planned_weight": plan.planned_weight,
                        "img_url": plan.exercise.img_url,
                    }
                    for plan in s.trieParOrdre()
                ],
            }
        )
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
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
    exercise = db.session.scalar(sa.select(Exercise).where(Exercise.id_api == data["exercise_id"]))
    if not exercise:
        abort(404, message="Exercice non trouvé.")
    day_enum = DayOfWeek(data["day"])
    seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == day_enum))
    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")
    ordre = max((plan.ordre for plan in seance.exercises_plan), default=0) + 1
    plan = SeanceExercise(
        seance_id=seance.id,
        exercise_id=exercise.id,
        ordre=ordre,
        planned_sets=data["planned_sets"],
        planned_reps=data["planned_reps"],
        planned_weight=data["planned_weight"],
    )
    with QueryTimer("addExoPlan"):
        db.session.add(plan)
        seance.is_rest_day = False
        seance.title = f"Séance {seance.day.value}"
        db.session.commit()
    route_logger.info(
        f"SEANCE EXO ADDED | user_id={user.id} | routine_id={routine.id} | seance_id={seance.id} | day={seance.day.value} | exercise_id={exercise.id} | ordre={ordre}"
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
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
    with QueryTimer("checkSeanceExistant"):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(data["day"])))
    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")
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
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
    with QueryTimer("checkSeanceExistant    "):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(data["day"])))
    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")
    res = {
        "id": seance.id,
        "routine_id": seance.routine_id,
        "day": seance.day.value,
        "title": seance.title,
        "is_rest_day": seance.is_rest_day,
        "exercises": [
            {
                "seance_exercise_id": plan.id,
                "exoId": plan.exercise.id_api,
                "name": plan.exercise.name,
                "ordre": plan.ordre,
                "planned_sets": plan.planned_sets,
                "planned_reps": plan.planned_reps,
                "planned_weight": plan.planned_weight,
                "img_url": plan.exercise.img_url,
            }
            for plan in seance.trieParOrdre()
        ],
    }
    return {"seance": res}


@seanceBLP.route("/changerConfigurationExo", methods=["POST"])
@seanceBLP.doc(security=[{"bearerAuth": []}])
@seanceBLP.arguments(UpdateExerciseConfigSchema)
@seanceBLP.response(200, MessageSchema)
@seanceBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@seanceBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def changerConfigurationExo(data):
    user = getCurrentUserOrAbort401()
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
    with QueryTimer("checkSeanceExistant"):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(data["day"])))
    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")
    with QueryTimer("checkExoExiste"):
        plan = db.session.scalar(
            sa.select(SeanceExercise).where(
                SeanceExercise.id == data["seance_exercise_id"], SeanceExercise.seance_id == seance.id
            )
        )
    if not plan:
        abort(404, message="Exercice non trouvée pour ce jour.")
    plan.planned_sets = data["planned_sets"]
    plan.planned_reps = data["planned_reps"]
    plan.planned_weight = data["planned_weight"]
    with QueryTimer("commitUpdateExerciseConfig"):
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
    with QueryTimer("checkSeanceExistant"):
        seance = db.session.scalar(
            sa.select(Seance)
            .join(Routine, Seance.routine_id == Routine.id)
            .where(Seance.id == data["seance_id"], Routine.user_id == user.id)
        )
    if not seance:
        abort(404, message="Séance non trouvée ou n'appartient pas à l'utilisateur.")
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
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
    with QueryTimer("checkSeanceExistant"):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(data["day"])))
    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")
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
