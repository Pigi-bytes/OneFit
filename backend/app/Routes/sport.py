from datetime import datetime

import sqlalchemy as sa
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.coreRoutes import getCurrentUserOrAbort401
from app.models import DayOfWeek, Exercise, Routine, Seance, SeanceExercise, WorkoutLog, WorkoutSession
from app.schemas import (
    ActiveRoutineSchema,
    AddExerciseToSeanceSchema,
    AddPerformedExerciseSchema,
    BaseErrorSchema,
    CreateRoutineSchema,
    MessageSchema,
    MoveExerciseOrderSchema,
    RemoveExerciseFromSeanceSchema,
    RenameRoutineSchema,
    RenameSeanceSchema,
    RoutineSchema,
    RoutinesResponseSchema,
    SeanceResponseSchema,
    SeancesResponseSchema,
    StartEndSeanceEffectueeSchema,
    TimeTotakSchema,
    UpdateExerciseConfigSchema,
    ValidationErrorSchema,
    getSeanceByDay,
)
from app.utils.logger import QueryTimer, route_logger

sportBLP = Blueprint("sport", __name__, url_prefix="/sport", description="Pour gerer tout ce qui est lié a la séance/routine/exo")


@sportBLP.route("/getRoutines", methods=["GET"])
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


@sportBLP.route("/getRoutine", methods=["POST"])
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, RoutineSchema)
@sportBLP.arguments(ActiveRoutineSchema)
@sportBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération de la routine")
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune routine trouvée")
@jwt_required()
def getRoutine(data):
    """Renvoie les informations de la routine dont l'id est passé en paramètres"""
    user = getCurrentUserOrAbort401()

    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    route_logger.info(f"GET ROUTINE | user_id={user.id} | routine={routine.id}")

    return routine


@sportBLP.route("/getSeancesPrevu", methods=["POST"])
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.arguments(ActiveRoutineSchema)
@sportBLP.response(200, SeancesResponseSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune routine active ou aucune séance trouvée")
@jwt_required()
def getSeancesPrevu(data):
    """
    Renvoie les séances de la routine active de l'utilisateur avec la liste des exercices prévus (par jour) | -1 pour la routine active
    """
    user = getCurrentUserOrAbort401()

    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

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
    with QueryTimer("ajoutRoutineDatabase"):
        db.session.add(routine)
        db.session.flush()

    for day in DayOfWeek:
        seance = Seance(routine_id=routine.id, day=day, title="Jour de Repos", is_rest_day=True)
        db.session.add(seance)

    user.setActiveRoutine(routine.id)
    db.session.commit()
    route_logger.info(f"ROUTINE CREATED | user_id={user.id} | routine_id={routine.id}")

    return {"message": "Routine créée !"}


@sportBLP.route("/activerRoutine", methods=["POST"])
@sportBLP.arguments(ActiveRoutineSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine non trouvée")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def activerRoutine(data):
    """Change la routine active de l'utilisateur"""
    user = getCurrentUserOrAbort401()
    routine_id = data["routine_id"]

    with QueryTimer("checkRoutineExistant"):
        routine = db.session.scalar(sa.select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    user.setActiveRoutine(routine_id)
    db.session.commit()

    route_logger.info(f"ROUTINE ACTIVATED | user_id={user.id} | routine_id={routine.id}")
    return {"message": f"La routine '{routine.name}' est maintenant active !"}


@sportBLP.route("/supprimerRoutine", methods=["DELETE"])
@sportBLP.arguments(ActiveRoutineSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine non trouvée")
@sportBLP.alt_response(409, schema=BaseErrorSchema, description="Impossible de supprimer une routine active")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def supprimerRoutine(data):
    """Supprime une routine de l'utilisateur sauf si elle est active"""
    user = getCurrentUserOrAbort401()
    routine_id = data["routine_id"]

    with QueryTimer("checkRoutineExistant"):
        routine = db.session.scalar(sa.select(Routine).where(Routine.id == routine_id, Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    if routine.is_active:
        abort(409, message="Impossible de supprimer une routine active. Veuillez d'abord en activer une autre.")

    with QueryTimer("deleteRoutineDB"):
        db.session.delete(routine)
        db.session.commit()
    route_logger.info(f"ROUTINE DELETED | user_id={user.id} | routine_id={routine.id} | name={routine.name}")

    return {"message": f"La routine '{routine.name}' a bien été supprimée."}


@sportBLP.route("/ajouterExoSeance", methods=["POST"])
@sportBLP.arguments(AddExerciseToSeanceSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(201, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def ajouterExoSeance(data):
    """Ajoute un exercice dans la séance d'un jour donné pour une routine."""
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


@sportBLP.route("/deplacerOrdreExoSeance", methods=["POST"])
@sportBLP.arguments(MoveExerciseOrderSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def deplacerOrdreExoSeance(data):
    """Déplace l'ordre d'un exercice prévu vers le haut ou le bas dans la séance d'un jour donné."""
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


@sportBLP.route("/getSeanceDuJour", methods=["POST"])
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.arguments(getSeanceByDay)
@sportBLP.response(200, SeanceResponseSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Séance non trouvée")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getSeanceDuJour(data):
    """
    Renvoie la séance d'un jour spécifique pour une routine donnée (ou active si -1)
    """
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


@sportBLP.route("/changerConfigurationExo", methods=["POST"])
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.arguments(UpdateExerciseConfigSchema)
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def changerConfigurationExo(data):
    """
    Modifie la configuration (sets/reps/poids) d'un exercice planifié.
    """
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


@sportBLP.route("/modiferNomRoutine", methods=["POST"])
@sportBLP.arguments(RenameRoutineSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modiferNomRoutine(data):
    """Modifie le nom d'une routine par son ID pour l'utilisateur connecté."""
    user = getCurrentUserOrAbort401()

    with QueryTimer("checkRoutineExistant"):
        routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))

    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    old_name = routine.name
    routine.name = data["name"]

    with QueryTimer("commitUpdateRoutineName"):
        db.session.commit()

    route_logger.info(
        f"ROUTINE NAME UPDATED | user_id={user.id} | routine_id={routine.id} | old_name={old_name} | new_name={routine.name}"
    )
    return {"message": "Nom de la routine mis à jour avec succès."}


@sportBLP.route("/modifierNomSeance", methods=["POST"])
@sportBLP.arguments(RenameSeanceSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Séance introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modifierNomSeance(data):
    """Modifie le nom d'une séance par son ID pour l'utilisateur connecté."""
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


@sportBLP.route("/supprimerExoSeance", methods=["DELETE"])
@sportBLP.arguments(RemoveExerciseFromSeanceSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def supprimerExoSeance(data):
    """Supprime un exercice prévu d'une séance puis remet l'ordre des exercices"""
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


@sportBLP.route("/ajouterExoEffectue", methods=["POST"])
@sportBLP.arguments(AddPerformedExerciseSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(201, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Exercice prévu introuvable")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def ajouterExoEffectue(data):
    """Ajoute les sets effectués d'un exercice planifié dans WorkoutLog"""
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


@sportBLP.route("/startSeanceEffectuee", methods=["POST"])
@sportBLP.arguments(StartEndSeanceEffectueeSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(201, MessageSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Séance introuvable")
@sportBLP.alt_response(409, schema=BaseErrorSchema, description="Séance déjà en cours ou jour de repos")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def startSeanceEffectuee(data):
    """Démarre une séance effectuée en base pour l'utilisateur connecté"""
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

    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))

    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    with QueryTimer("checkSeanceForUser"):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(data["day"])))

    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")

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


@sportBLP.route("/endSeanceEffectuee", methods=["POST"])
@sportBLP.arguments(StartEndSeanceEffectueeSchema)
@sportBLP.doc(security=[{"bearerAuth": []}])
@sportBLP.response(200, TimeTotakSchema)
@sportBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou session active introuvable")
@sportBLP.alt_response(409, schema=BaseErrorSchema, description="Séance déjà terminée")
@sportBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def endSeanceEffectuee(data):
    """Termine une séance effectuée existante en base pour l'utilisateur connecté"""
    user = getCurrentUserOrAbort401()

    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))

    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")

    with QueryTimer("checkSeanceForUser"):
        seance = db.session.scalar(sa.select(Seance).where(Seance.routine_id == routine.id, Seance.day == DayOfWeek(data["day"])))

    if not seance:
        abort(404, message="Séance non trouvée pour ce jour.")

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
        "time": session.ended_at - session.started_at,
    }
