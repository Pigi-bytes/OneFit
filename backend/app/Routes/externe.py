import sqlalchemy as sa
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

from app import db
from app.communRoutes import APISALLE, APISPORT
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
from app.utils.logger import QueryTimer, route_logger

externeBLP = Blueprint("externe", __name__, url_prefix="/externe", description="Call a l'autre api")


@externeBLP.route("/salle", methods=["POST"])
@externeBLP.arguments(SalleSchema)
@externeBLP.response(200)
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def getSalle(data):
    "trouve les salles en fonction d'un nom de ville"

    route_logger.info(f"SALLE SEARCH | ville={data['ville']}")

    params = {"near": data["ville"], "limit": 50, "query": "gym"}
    response = APISALLE.get("search", params=params, useCache=True)

    return response


@externeBLP.route("/salleByLoc", methods=["POST"])
@externeBLP.arguments(SalleSchemaByLoc)
@externeBLP.response(200)
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
def getSalleLoc(data):
    "trouve les salles en fonction d'un nom de ville"

    route_logger.info(f"SALLE LOC SEARCH | lat={data['lat']} | lng={data['lng']}")

    params = {"ll": f"{data['lat']},{data['lng']}", "limit": 50, "query": "gym"}
    response = APISALLE.get("search", params=params, useCache=True)

    return response


@externeBLP.route("/getExo", methods=["POST"])
@externeBLP.arguments(ExerciceRequestSchema)
@externeBLP.doc(security=[{"bearerAuth": []}])
@externeBLP.response(200, ExerciceResponseSchema)
@externeBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération de l'exercice")
@externeBLP.alt_response(404, schema=BaseErrorSchema, description="Exercice non trouvé sur l'API externe")
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def getExo(data):
    """Récupère un exercice depuis la BDD si existant, sinon depuis l'API externe puis le sauvegarde"""

    idExo = data["exoId"]
    if not idExo:
        abort(400, message="exerciseId manquant")

    route_logger.info(f"EXO FETCH ATTEMPT | user_id={get_jwt_identity()} | exoId={idExo}")

    with QueryTimer("checkExoExistant"):
        exo = db.session.scalar(sa.select(Exercise).where(Exercise.id_api == idExo))

    if exo:
        route_logger.warning(f"EXO FETCH WIN | user_id={get_jwt_identity()} | exoId={idExo}")
        return {
            "idExo": exo.id_api,
            "name": exo.name,
            "img_url": exo.img_url,
            "video_url": exo.video_url,
            "overview": exo.overview,
            "instructions": exo.instructions,
            "body_part": exo.body_part,
        }

    route_logger.warning(f"EXO FETCH FAIL | user_id={get_jwt_identity()} | exoId={idExo}")
    exo = APISPORT.get(f"exercises/{idExo}")
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

    with QueryTimer("addExo"):
        db.session.add(exercise)
        db.session.commit()

    route_logger.info(f"EXO CREATED | user_id={get_jwt_identity()} | exoId={exercise.id_api}")

    return {
        "idExo": exercise.id_api,
        "name": exercise.name,
        "img_url": exercise.img_url,
        "video_url": exercise.video_url,
        "overview": exercise.overview,
        "instructions": exercise.instructions,
        "body_part": exercise.body_part,
    }


@externeBLP.route("/searchExo", methods=["POST"])
@externeBLP.arguments(SearchExoRequestSchema)
@externeBLP.doc(security=[{"bearerAuth": []}])
@externeBLP.response(200, SearchExoResponseSchema)
@externeBLP.alt_response(400, schema=BaseErrorSchema, description="Erreur lors de la récupération des exercices")
@externeBLP.alt_response(422, schema=ValidationErrorSchema, description="Données invalides")
@jwt_required()
def searchExo(data):
    """Recherche des exercices par nom (fuzzy matching) et retourne les n plus proches."""

    recherche = data["recherche"]
    n = int(data["limit"])

    route_logger.info(f"EXO SEARCH | recherche={recherche} | limit={n}")
    params = {"search": recherche, "limit": n}
    response = APISPORT.get("exercises/search", params=params)

    if not response:
        route_logger.warning(f"EXO SEARCH FAIL | recherche={recherche}")
        abort(400, message="Erreur")

    resultat = [(exo["name"], exo["exerciseId"], exo["imageUrl"]) for exo in response]
    return {"resultats": resultat}
