import sqlalchemy as sa
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import getCurrentUserOrAbort401
from app.models import DayOfWeek, Routine, Seance
from app.schemas import (
    ActiveRoutineSchema,
    BaseErrorSchema,
    CreateRoutineSchema,
    MessageSchema,
    RenameRoutineSchema,
    RoutineSchema,
    RoutinesResponseSchema,
    ValidationErrorSchema,
)
from app.utils.logger import QueryTimer, route_logger

routineBLP = Blueprint("routine", __name__, url_prefix="/routine", description="Gestion des routines")


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
    if data["routine_id"] == -1:
        routine = user.activeRoutine()
    else:
        with QueryTimer("checkRoutineExistant"):
            routine = db.session.scalar(sa.select(Routine).where(Routine.id == data["routine_id"], Routine.user_id == user.id))
    if not routine:
        abort(404, message="Routine non trouvée ou n'appartient pas à l'utilisateur.")
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
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine non trouvée")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def activerRoutine(data):
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


@routineBLP.route("/supprimerRoutine", methods=["DELETE"])
@routineBLP.arguments(ActiveRoutineSchema)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, MessageSchema)
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine non trouvée")
@routineBLP.alt_response(409, schema=BaseErrorSchema, description="Impossible de supprimer une routine active")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def supprimerRoutine(data):
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


@routineBLP.route("/modiferNomRoutine", methods=["POST"])
@routineBLP.arguments(RenameRoutineSchema)
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, MessageSchema)
@routineBLP.alt_response(404, schema=BaseErrorSchema, description="Routine introuvable")
@routineBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def modiferNomRoutine(data):
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
