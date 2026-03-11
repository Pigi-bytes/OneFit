from marshmallow import Schema, fields, validate


# ---------------------------------------------------------------------------
# Champs
# ---------------------------------------------------------------------------
def _username(**kw):
    d = {"required": True, "validate": validate.Length(1, 64), "metadata": {"description": "Pseudo"}}
    return fields.Str(**{**d, **kw})


def _password(**kw):
    d = {"required": True, "load_only": True, "validate": validate.Length(6, 255), "metadata": {"description": "MDP"}}
    return fields.Str(**{**d, **kw})


def _poids(**kw):
    d = {"required": True, "validate": validate.Range(20, 500), "metadata": {"description": "Poids (kg)"}}
    return fields.Float(**{**d, **kw})


def _date(**kw):
    d = {"required": True, "metadata": {"description": "Date (YYYY-MM-DD)"}}
    return fields.Date(**{**d, **kw})


def _taille(**kw):
    d = {"required": True, "validate": validate.Range(50, 300), "metadata": {"description": "Taille (cm)"}}
    return fields.Int(**{**d, **kw})


def _ville(**kw):
    d = {"required": True, "validate": validate.Length(min=2, max=100), "metadata": {"description": "nom de la ville"}}
    return fields.String(**{**d, **kw})


def _note(**kw):
    d = {"allow_none": True, "load_default": None, "metadata": {"description": "Note"}}
    return fields.Str(**{**d, **kw})


def _lat(**kw):
    d = {"required": True, "metadata": {"description": "Latitude"}}
    return fields.Float(**{**d, **kw})


def _lng(**kw):
    d = {"required": True, "metadata": {"description": "Longitude"}}
    return fields.Float(**{**d, **kw})


def _exo(**kw):
    d = {"metadata": {"description": "ID de l'exercice externe"}}
    return fields.Str(**{**d, **kw})


def _day(**kw):
    d = {
        "required": True,
        "validate": validate.OneOf(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]),
        "metadata": {"description": "Jour de la séance"},
    }
    return fields.Str(**{**d, **kw})


def _name(**kw):
    d = {"required": True, "metadata": {"description": "Nom"}}
    return fields.Str(**{**d, **kw})


def _routine_id(**kw):
    d = {"required": True, "metadata": {"description": "ID de la routine"}}
    return fields.Int(**{**d, **kw})


def _planned_sets(**kw):
    d = {"required": True, "metadata": {"description": "Nombre de séries prévues"}}
    return fields.Int(**{**d, **kw})


def _planned_reps(**kw):
    d = {"required": True, "metadata": {"description": "Nombre de répétitions prévues"}}
    return fields.Int(**{**d, **kw})


def _planned_weight(**kw):
    d = {"required": True, "metadata": {"description": "Charge prévue"}}
    return fields.Float(**{**d, **kw})


def _routine(**kw):
    d = {"load_default": -1, "metadata": {"description": "ID de la routine cible (-1 = routine active)"}}
    return fields.Int(**{**d, **kw})


def _seance_exercise_id(**kw):
    d = {"required": True, "metadata": {"description": "ID de l'exercice prévu dans la séance"}}
    return fields.Int(**{**d, **kw})


def _direction(**kw):
    d = {
        "required": True,
        "validate": validate.OneOf(["up", "down"]),
        "metadata": {"description": "Direction du déplacement (up/down)"},
    }
    return fields.Str(**{**d, **kw})


# ---------------------------------------------------------------------------
# Erreurs
# ---------------------------------------------------------------------------
class BaseErrorSchema(Schema):
    code = fields.Int(metadata={"example": 400})
    message = fields.Str(metadata={"example": "Erreur"})
    status = fields.Str(metadata={"example": "Bad Request"})

    class Meta:
        unknown = "EXCLUDE"


class ValidationErrorSchema(BaseErrorSchema):
    """Erreur de validation des données (422)"""

    errors = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Str()),
        metadata={"example": {"field": ["Unknown field."]}},
    )


# ---------------------------------------------------------------------------
# Schémas de Auth / Messages
# ---------------------------------------------------------------------------
class MessageSchema(Schema):
    message = fields.Str(metadata={"example": "Opération réussie"})


class LoginSchema(Schema):
    username = _username(required=True)
    password = _password(required=True)


class RegisterSchema(Schema):
    username = _username(required=True)
    password = _password(required=True)


class TokenSchema(Schema):
    access_token = fields.Str(metadata={"description": "JWT d'accès"})


# ---------------------------------------------------------------------------
# Schéma de Utilisateur
# ---------------------------------------------------------------------------
class UserSchema(Schema):
    username = _username()
    date_naissance = _date()
    taille = _taille()
    dernierPoids = _poids()


class UserConfigurerSchema(Schema):
    date_naissance = _date(required=False, load_default=None)
    taille = _taille(required=False, load_default=None)


class UserChangementMdpSchema(Schema):
    password = _password(metadata={"description": "Mot de passe actuel"})
    new_password = _password(metadata={"description": "Nouveau mot de passe"})


class UserChangementUsernameSchema(Schema):
    username = _username()


# ---------------------------------------------------------------------------
# Poids / Historique
# ---------------------------------------------------------------------------
class UserHistoriqueItem(Schema):
    date = _date()
    poids = _poids()
    note = _note()


class UserAjouterPoidsSchema(Schema):
    date = _date()
    poids = _poids()
    note = _note()


class UserSuppPoidSchema(Schema):
    date = _date()


class UserHistoriqueItemSchema(Schema):
    poids = _poids()
    date = _date()
    note = _note()


class UserHistoriqueResponseSchema(Schema):
    historique = fields.List(fields.Nested(UserHistoriqueItemSchema), required=True)


# ---------------------------------------------------------------------------
# API Salle de sport
# ---------------------------------------------------------------------------
class SalleSchema(Schema):
    ville = _ville()


# ---------------------------------------------------------------------------
# API Exo
# ---------------------------------------------------------------------------
class ExerciceRequestSchema(Schema):
    exoId = _exo()


class ExerciceResponseSchema(Schema):
    exoId = _exo()
    name = fields.Str()
    img_url = fields.Str()
    video_url = fields.Str()
    overview = fields.Str()
    instructions = fields.Str()
    body_part = fields.Str()


class SearchExoRequestSchema(Schema):
    recherche = fields.Str(required=True, metadata={"description": "Chaîne de recherche"})
    limit = fields.Int(
        required=False,
        load_default=25,
        validate=validate.Range(min=1, max=25),
        metadata={"description": "Nombre de résultats (1-25)"},
    )


class SearchExoResponseSchema(Schema):
    resultats = fields.List(
        fields.Tuple((_exo(), fields.Str(), fields.Str())),
        metadata={"description": "Liste de tuples [(idExo, nom, img)]"},
    )


class SalleSchemaByLoc(Schema):
    lat = _lat()
    lng = _lng()


# ---------------------------------------------------------------------------
# API Sport
# ---------------------------------------------------------------------------
class RoutineSchema(Schema):
    id = _routine_id()
    name = _name()
    is_active = fields.Bool(required=True)


class RoutinesResponseSchema(Schema):
    routines = fields.List(fields.Nested(RoutineSchema))


class PlannedExerciseSchema(Schema):
    seance_exercise_id = _seance_exercise_id()
    exoId = _exo()
    name = _name()
    ordre = fields.Int(required=True)
    planned_sets = _planned_sets()
    planned_reps = _planned_reps()
    planned_weight = _planned_weight()
    img_url = fields.Str(allow_none=True)


class SeanceSchema(Schema):
    routine_id = _routine_id()
    day = _day()
    title = fields.Str(allow_none=True)
    is_rest_day = fields.Bool(required=True)
    exercises = fields.List(fields.Nested(PlannedExerciseSchema), required=False)


class SeancesResponseSchema(Schema):
    seances = fields.List(fields.Nested(SeanceSchema), required=True)


class CreateRoutineSchema(Schema):
    name = _name(metadata={"description": "Nom de la nouvelle routine"})


class ActiveRoutineSchema(Schema):
    routine_id = _routine_id()


class AddExerciseToSeanceSchema(Schema):
    routine_id = _routine()
    day = _day()
    exercise_id = _exo()

    planned_sets = _planned_sets(validate=validate.Range(min=1, max=30))
    planned_reps = _planned_reps(validate=validate.Range(min=1, max=200))
    planned_weight = _planned_weight(validate=validate.Range(min=0, max=1000))


class MoveExerciseOrderSchema(Schema):
    routine_id = _routine()
    day = _day()
    seance_exercise_id = _seance_exercise_id()
    direction = _direction()
