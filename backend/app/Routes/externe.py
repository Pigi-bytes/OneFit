from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from app.communRoutes import APISALLE, APISPORT, addAndCommit, checkExoExists, exerciseResponse
from app.models import Exercise
from app.schemas import (
    BaseErrorSchema,
    ExerciceRequestSchema,
    ExerciceResponseSchema,
    SalleSchema,
    SalleSchemaByLoc,
    SearchExoRequestSchema,
    SearchExoResponseSchema,
    ValidationErrorSchema,
)
from app.utils.logger import route_logger

externeBLP = Blueprint("externe", __name__, url_prefix="/externe", description="Call à l'autre API")

TEMPS_DISTANCE_MOTS = {
    "run",
    "running",
    "jog",
    "sprint",
    "walk",
    "treadmill",
    "bike",
    "cycling",
    "cycle",
    "elliptical",
    "rowing",
    "jump rope",
    "skip",
    "skipping",
    "stair",
    "step",
    "cardio",
    "hiit",
    "burpee",
    "mountain climber",
    "box jump",
    "plank",
    "hold",
    "isometric",
    "wall sit",
    "static",
    "flutter kick",
    "hollow body",
    "dead hang",
}


@externeBLP.route("/salle", methods=["POST"])
@externeBLP.arguments(SalleSchema)
@externeBLP.response(200)
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def getSalle(data):
    "trouve les salles en fonction d'un nom de ville"
    route_logger.info(f"SALLE SEARCH | ville={data['ville']}")
    return APISALLE.get("search", params={"near": data["ville"], "limit": 50, "query": "gym"}, useCache=True)


@externeBLP.route("/salleByLoc", methods=["POST"])
@externeBLP.arguments(SalleSchemaByLoc)
@externeBLP.response(200)
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def getSalleLoc(data):
    "trouve les salles en fonction d'un nom de ville"
    route_logger.info(f"SALLE LOC SEARCH | lat={data['lat']} | lng={data['lng']}")
    return APISALLE.get("search", params={"ll": f"{data['lat']},{data['lng']}", "limit": 50, "query": "gym"}, useCache=True)


@externeBLP.route("/getExo", methods=["POST"])
@externeBLP.arguments(ExerciceRequestSchema)
@externeBLP.doc(security=[{"bearerAuth": []}])
@externeBLP.response(200, ExerciceResponseSchema)
@externeBLP.alt_response(404, schema=BaseErrorSchema, description="Exercice introuvable dans l'API externe")
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getExo(data):
    """Récupère un exercice depuis la BDD si existant, sinon depuis l'API externe puis le sauvegarde"""
    route_logger.info(f"EXO FETCH ATTEMPT | exoId={data['exoId']}")

    exo = checkExoExists(data["exoId"])
    if exo:
        route_logger.warning(f"EXO FETCH WIN | exoId={data['exoId']}")
        return exerciseResponse(exo)

    route_logger.warning(f"EXO FETCH FAIL | exoId={data['exoId']}")
    exo = APISPORT.get(f"exercises/{data['exoId']}")
    if not exo:
        abort(404, message="Erreur lors de la récupération de l'exercice externe")

    exercise = Exercise(
        id_api=exo["exerciseId"],
        name=exo["name"],
        img_url=exo["imageUrl"],
        video_url=exo["videoUrl"],
        overview=exo["overview"],
        instructions="\n".join(exo["instructions"]) if isinstance(exo["instructions"], list) else exo["instructions"],
        body_part=", ".join(exo["bodyParts"]) if isinstance(exo["bodyParts"], list) else exo["bodyParts"],
    )

    addAndCommit(exercise, "addExo")

    route_logger.info(f"EXO CREATED | exoId={exercise.id_api}")
    return exerciseResponse(exercise)


@externeBLP.route("/searchExo", methods=["POST"])
@externeBLP.arguments(SearchExoRequestSchema)
@externeBLP.doc(security=[{"bearerAuth": []}])
@externeBLP.response(200, SearchExoResponseSchema)
@externeBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération des exercices")
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def searchExo(data):
    """Recherche des exercices par nom (fuzzy matching) et retourne les n plus proches."""

    route_logger.info(f"EXO SEARCH | recherche={data['recherche']} | limit={int(data['limit'])}")
    params = {"search": data["recherche"], "limit": int(data["limit"])}
    response = APISPORT.get("exercises/search", params=params)

    if not response:
        route_logger.warning(f"EXO SEARCH FAIL | recherche={data['recherche']}")
        abort(400, message="Erreur")

    # FIX LE CARDIO !! PAS PARFAIT. La base de donnée n'a pas été designé pour du cardio alors on exclu la plupart des exercices de cardio
    # Lors de la recherche
    resultats = []
    for exo in response:
        if not any(mot in exo["name"].lower() for mot in TEMPS_DISTANCE_MOTS):
            resultats.append((exo["name"], exo["exerciseId"], exo["imageUrl"]))
        else:
            route_logger.debug(f"EXO EXCLUDED | name={exo['name']}")

    return {"resultats": resultats}
