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


def _note(**kw):
    d = {"allow_none": True, "load_default": None, "metadata": {"description": "Note"}}
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
    poids = fields.Float(required=True)
    date = fields.Str(required=True)
    note = fields.Str(allow_none=True)


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
