from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from app.communRoutes import checkExoExists

from app import db
from app.communRoutes import getCurrentUserOrAbort401, getRoutineForUserOrAbort404
from app.models import DayOfWeek, Routine, Seance
from app.schemas import (
    ActiveRoutineSchema,
    BaseErrorSchema,
    CreateRoutineSchema,
    MessageSchema,
    RenameRoutineSchema,
    RoutineSchema,
    RoutinesResponseSchema,
    RoutinePrefaitesResponseSchema,
    ValidationErrorSchema,
    RoutinePref,
)
from app.utils.logger import QueryTimer, route_logger

routineBLP = Blueprint("routine", __name__, url_prefix="/routine", description="Gestion des routines")



dwarfMaxing = [
    # Lundi
    [
        ("exr_41n2hxnFMotsXTj3", 4, 10, 60),  # Bench Press
        ("exr_41n2hdkBpqwoDmVq", 4, 12, 40),  # Suspended Row
        ("exr_41n2hgCHNgtVLHna", 3, 12, 12),  # Cross Body Hammer Curl
        ("exr_41n2hndkoGHD1ogh", 3, 12, 0),   # Triceps Dip (poids du corps)
    ],
    # Mardi
    [
        ("exr_41n2hs6camM22yBG", 4, 10, 30),  # Seated Shoulder Press
        ("exr_41n2hU4y6EaYXFhr", 4, 8,  0),   # Pull Up (poids du corps)
        ("exr_41n2hxxePSdr5oN1", 4, 12, 60),  # Hip Thrust
        ("exr_41n2hmbfYcYtedgz", 3, 15, 16),  # Dumbbell Glute Bridge
    ],
    # Mercredi - repos
    [],
    # Jeudi
    [
        ("exr_41n2hsVHu7B1MTdr", 4, 10, 20),  # Palms In Incline Bench Press
        ("exr_41n2hQDiSwTZXM4F", 4, 12, 24),  # Goblet Squat
        ("exr_41n2hQtaWxPLNFwX", 4, 15, 16),  # Dumbbell Standing Calf Raise
        ("exr_41n2hUDuvCas2EB3",  3, 15, 10),  # Cable Seated Neck Flexion
    ],
    # Vendredi
    [
        ("exr_41n2hXszY7TgwKy4", 4, 8,  0),   # Chin Up (poids du corps)
        ("exr_41n2hGioS8HumEF7", 3, 12, 14),  # Hammer Curl
        ("exr_41n2hwoc6PkW1UJJ", 4, 15, 40),  # Barbell Standing Calf Raise
        ("exr_41n2hrHSqBnVWRRB", 3, 10, 0),   # Bodyweight Single Leg Deadlift
    ],
    # Samedi - repos
    [],
    # Dimanche - repos
    [],
]

OneFitMan = [
    [
        ("exr_41n2hNXJadYcfjnd", 4, 25, 0),
        ("exr_41n2hQDiSwTZXM4F", 4, 25, 0),
        ("exr_41n2hxnFMotsXTj3", 3, 15, 100),
    ]
    for _ in range(7)
]

girlyPop = [
    [("exr_41n2hGioS8HumEF7",  16, 1, 14)]  # Lundi - Hammer Curl (16 sets x 1 rep)
    if i % 2 == 0 else
    [("exr_41n2hndkoGHD1ogh", 17, 1, 0)]    # Triceps Dip
    for i in range(7)
]

debutant = [
    # Lundi
    [
        ("exr_41n2hxnFMotsXTj3", 4, 10, 20),  # Bench Press
        ("exr_41n2hsVHu7B1MTdr", 2,10,20),  # incline Bench press
        ("exr_41n2hndkoGHD1ogh", 3, 10,0), # tricep dip
        ("exr_41n2hdHtZrMPkcqY", 3, 10,20), # tricep extension
    ],

    # Mardi
    [],

    # Mercredi
    [
        ("exr_41n2hftBVLiXgtRQ", 4, 10,0),  # wide grip pull up
        ("exr_41n2hcFJpBvAkXCP", 3,12,0), # seated row with towel
        ("exr_41n2hY9EdwkdGz9a", 3,10,20), # bent over row
        ("exr_41n2hGioS8HumEF7", 3, 8, 10),  # Hammer Curl
    ],

    # Jeudi
    [],

    # Vendredi
    [
        ("exr_41n2hQtaWxPLNFwX", 4, 10, 10),  # Dumbbell Standing Calf Raise
        ("exr_41n2hhiWL8njJDZe", 3,12, 20), # seated calf raise
        ("exr_41n2hs6camM22yBG",  4, 8, 20), # shoulder press
        ("exr_41n2hjuGpcex14w7",  3, 8, 5) # lateral raise
    ],
    # Samedi
    [],
    # Dimanche
    []
]

ROUTINES_PREFAITES = {
    1 : ("DwarfMaxingUltraXX", dwarfMaxing,
    "Une routine de niveau intermédiaire ultra boostée qui vous transformera en nain cubique."),

    2 : ("OneFitMan", OneFitMan,
    "Cette routine ne rigole pas. Mais vos ennemis ne rigoleront pas non plus devant votre corps de guerrier. Choisissez-la si vous êtes à la hauteur. Résultats garantis."),

    3 : ("GirlyPop",girlyPop,
    "Vous voulez avoir des gros bras sans vous casser la tête? GirlyPop est faite pour vous. PS: L'équipe OneFit ne saurait être tenue responsable d'un quelconque incident lié à l'usage de cette routine."),
    
    4 : ("Débutant",debutant,
    "Pour ceux qui veulent se mettre au sport avec un emploi du temps serré. Cette routine de niveau débutant n'a que trois jours d'exercice : lundi pour les pectoraux et les triceps, le mercredi pour le dos et les biceps, et le vendredi pour les jambes et les épaules."),
}

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
                    abort(404, message=f"Exercice {exercise_id} non trouvé.")
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
    return {"message": "Routine ajouté au votre"}

@routineBLP.route("/getRoutinesPrefaites", methods=["GET"])
@routineBLP.doc(security=[{"bearerAuth": []}])
@routineBLP.response(200, RoutinePrefaitesResponseSchema)
@jwt_required()
def getRoutinesPrefaites():
    routines = [{"id": k,
                 "name": v[0],
                 "description": v[2],
                 "activeDays": sum(1 for day in v[1] if day)}
                 for k, v in ROUTINES_PREFAITES.items()]
    return {"routines": routines}