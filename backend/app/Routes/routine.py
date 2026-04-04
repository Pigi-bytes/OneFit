import json
from pathlib import Path

from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import APISPORT, checkExoExists, getCurrentUserOrAbort401, getRoutineForUserOrAbort404
from app.models import DayOfWeek, Exercise, Routine, Seance
from app.schemas import (
    ActiveRoutineSchema,
    BaseErrorSchema,
    CreateRoutineSchema,
    MessageSchema,
    RenameRoutineSchema,
    RoutinePref,
    RoutinePrefaitesResponseSchema,
    RoutineSchema,
    RoutinesResponseSchema,
    ValidationErrorSchema,
)
from app.utils.logger import QueryTimer, route_logger

routineBLP = Blueprint("routine", __name__, url_prefix="/routine", description="Gestion des routines")


def _loadRoutinePrefaites():
    data = Path(__file__).resolve().parent.parent / "data" / "routines_prefaites.json"
    with data.open("r", encoding="utf-8") as f:
        data = json.load(f)

    routines = {}
    for key, value in data.items():
        exo_par_jour = []
        for day in value["days"]:
            exo_par_jour.append(
                [
                    (
                        exo["exercise_id"],
                        exo["planned_sets"],
                        exo["planned_reps"],
                        exo["planned_weight"],
                    )
                    for exo in day
                ]
            )
        routines[int(key)] = (value["name"], exo_par_jour, value["description"])
    return routines

ROUTINES_PREFAITES = _loadRoutinePrefaites()


def create_routine_for_user(user, routine_name):
    routine = Routine(user_id=user.id, name=routine_name, is_active=False)
    with QueryTimer("ajoutRoutineDatabase"):
        db.session.add(routine)
        db.session.flush()
    for day in DayOfWeek:
        seance = Seance(routine_id=routine.id, day=day, title="Jour de Repos", is_rest_day=True)
        db.session.add(seance)
    user.setActiveRoutine(routine.id)
    db.session.commit()
    route_logger.info(f"ROUTINE CREATED | user_id={user.id} | routine_id={routine.id}")
    return routine


def create_routine_Pre(user, routine_name, exo):
    routine = Routine(user_id=user.id, name=routine_name, is_active=False)
    with QueryTimer("ajoutRoutineDatabase"):
        db.session.add(routine)
        db.session.flush()

    for i, day in enumerate(DayOfWeek):
        seance = Seance(routine_id=routine.id, day=day, title="Jour de Repos", is_rest_day=True)
        db.session.add(seance)
        db.session.flush()

        exercises_du_jour = exo[i] if i < len(exo) else []

        if exercises_du_jour:
            seance.is_rest_day = False
            seance.title = day.value

            for exercise_data in exercises_du_jour:
                exercise_id, planned_sets, planned_reps, planned_weight = exercise_data
                exercise = checkExoExists(exercise_id)
                if not exercise:
                    route_logger.info(f"EXO AUTO-FETCH | exoId={exercise_id}")
                    exo_api = APISPORT.get(f"exercises/{exercise_id}")
                    if not exo_api:
                        abort(404, message=f"Exercice {exercise_id} introuvable (API externe).")

                    exercise = Exercise(
                        id_api=exo_api["exerciseId"],
                        name=exo_api["name"],
                        img_url=exo_api["imageUrl"],
                        video_url=exo_api["videoUrl"],
                        overview=exo_api["overview"],
                        instructions="\n".join(exo_api["instructions"])
                        if isinstance(exo_api["instructions"], list)
                        else exo_api["instructions"],
                        body_part=", ".join(exo_api["bodyParts"])
                        if isinstance(exo_api["bodyParts"], list)
                        else exo_api["bodyParts"],
                    )
                    db.session.add(exercise)
                    db.session.flush()
                    route_logger.info(f"EXO AUTO-CREATED | exoId={exercise.id_api}")
                seance.ajouterPlan(exercise, planned_sets, planned_reps, planned_weight)

    user.setActiveRoutine(routine.id)
    db.session.commit()
    route_logger.info(f"ROUTINE CREATED | user_id={user.id} | routine_id={routine.id}")
    return routine


@routineBLP.route("/getRoutines", methods=["GET"])
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, RoutinesResponseSchema)
@routineBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération des routines")
@routineBLP.alt_response(400, schema=BaseErrorSchema, description="Aucune routine trouvée")
@jwt_required()
def getRoutines():
    user = getCurrentUserOrAbort401()
    route_logger.info(f"GET ROUTINES | user_id={user.id}")
    routines = [{"id": r.id, "name": r.name, "is_active": r.is_active} for r in user.routines]
    if not routines:
        route_logger.warning(f"Aucune routine trouvé | user_id={user.id}")
        abort(404, message="Aucune routine trouvée pour cet utilisateur.")
    return {"routines": routines}


@routineBLP.route("/getRoutine", methods=["POST"])
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, RoutineSchema)
@routineBLP.arguments(ActiveRoutineSchema)
@routineBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération de la routine")
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Aucune routine trouvée")
@jwt_required()
def getRoutine(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    route_logger.info(f"GET ROUTINE | user_id={user.id} | routine={routine.id}")
    return routine


@routineBLP.route("/createRoutine", methods=["POST"])
@routineBLP.arguments(CreateRoutineSchema)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(201, MessageSchema)
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def createRoutine(data):
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


@routineBLP.route("/activerRoutine", methods=["POST"])
@routineBLP.arguments(ActiveRoutineSchema)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, MessageSchema)
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine introuvable")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def activerRoutine(data):
    user = getCurrentUserOrAbort401()
    routine_id = data["routine_id"]
    routine = getRoutineForUserOrAbort404(user, routine_id)
    user.setActiveRoutine(routine.id)
    db.session.commit()
    route_logger.info(f"ROUTINE ACTIVATED | user_id={user.id} | routine_id={routine.id}")
    return {"message": f"La routine '{routine.name}' est maintenant active !"}


@routineBLP.route("/supprimerRoutine", methods=["DELETE"])
@routineBLP.arguments(ActiveRoutineSchema)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, MessageSchema)
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine introuvable")
@routineBLP.alt_response(409, schema=BaseErrorSchema, description="Impossible de supprimer une routine active")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def supprimerRoutine(data):
    user = getCurrentUserOrAbort401()
    routine_id = data["routine_id"]
    routine = getRoutineForUserOrAbort404(user, routine_id)
    if routine.is_active:
        abort(409, message="Impossible de supprimer une routine active. Veuillez d'abord en activer une autre.")
    with QueryTimer("deleteRoutineDB"):
        db.session.delete(routine)
        db.session.commit()
    route_logger.info(f"ROUTINE DELETED | user_id={user.id} | routine_id={routine.id} | name={routine.name}")
    return {"message": f"La routine '{routine.name}' a bien été supprimée."}


@routineBLP.route("/modiferNomRoutine", methods=["POST"])
@routineBLP.arguments(RenameRoutineSchema)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, MessageSchema)
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine introuvable")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modiferNomRoutine(data):
    user = getCurrentUserOrAbort401()
    routine = getRoutineForUserOrAbort404(user, data["routine_id"])
    old_name = routine.name
    routine.name = data["name"]
    with QueryTimer("commitUpdateRoutineName"):
        db.session.commit()
    route_logger.info(
        f"ROUTINE NAME UPDATED | user_id={user.id} | routine_id={routine.id} | old_name={old_name} | new_name={routine.name}"
    )
    return {"message": "Nom de la routine mis à jour avec succès."}


@routineBLP.route("/ajouterRoutinePrefaite", methods=["POST"])
@routineBLP.arguments(RoutinePref)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, MessageSchema)
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine, séance ou exercice prévu introuvable")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def ajouterRoutinePrefaite(data):
    user = getCurrentUserOrAbort401()
    val = data["routine"]
    if val not in ROUTINES_PREFAITES:
        abort(404, message="Routine préfaite introuvable.")
    name, exo, _ = ROUTINES_PREFAITES[val]
    create_routine_Pre(user, name, exo)
    return {"message": "Routine ajoutée à vos routines personnelles avec succès."}


@routineBLP.route("/getRoutinesPrefaites", methods=["GET"])
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, RoutinePrefaitesResponseSchema)
@jwt_required()
def getRoutinesPrefaites():
    routines = [
        {"id": k, "name": v[0], "description": v[2], "activeDays": sum(1 for day in v[1] if day)}
        for k, v in ROUTINES_PREFAITES.items()
    ]
    return {"routines": routines}
