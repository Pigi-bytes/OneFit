from marshmallow import Schema, fields, validate

USERNAME = fields.Str(
    required=True,
    validate=validate.Length(min=1, max=255),
    metadata={"description": "Nom d'utilisateur"},
)

PASSWORD = fields.Str(
    required=True,
    load_only=True,
    validate=validate.Length(min=1, max=255),
    metadata={"description": "Mot de passe"},
)


# Classe mère pour les schémas d'erreur
class BaseErrorSchema(Schema):
    code = fields.Int()
    message = fields.Str()
    status = fields.Str()

    class Meta:
        unknown = "EXCLUDE"


# Spécialisations pour chaque type d'erreur
class AuthErrorResponseSchema(BaseErrorSchema):
    """Erreur d'authentification (format API)"""

    code = fields.Int(metadata={"example": 401})
    message = fields.Str(metadata={"example": "Identifiants invalides"})
    status = fields.Str(metadata={"example": "Unauthorized"})


class RegisterErrorResponseSchema(BaseErrorSchema):
    """Erreur d'inscription (format API)"""

    code = fields.Int(metadata={"example": 409})
    message = fields.Str(metadata={"example": "Nom d'utilisateur déjà pris"})
    status = fields.Str(metadata={"example": "Conflict"})


class ValidationErrorSchema(BaseErrorSchema):
    """Erreur de validation des données (422)"""

    code = fields.Int(metadata={"example": 422})
    message = fields.Str(metadata={"example": "Unprocessable Entity"})
    status = fields.Str(metadata={"example": "Unprocessable Entity"})
    errors = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Str()),
        metadata={"example": {"USERnAmES": ["Unknown field."]}},
    )


class UserNotFoundErrorSchema(BaseErrorSchema):
    """Erreur lorsque l'utilisateur n'est pas trouvé (404)"""

    code = fields.Int(metadata={"example": 404})
    message = fields.Str(metadata={"example": "Utilisateur non trouvé"})
    status = fields.Str(metadata={"example": "Not Found"})


class LoginSchema(Schema):
    username = USERNAME
    password = PASSWORD


class RegisterSchema(Schema):
    username = USERNAME
    password = PASSWORD


class TokenSchema(Schema):
    access_token = fields.Str()


class MessageSchema(Schema):
    message = fields.Str()


class UserSchema(Schema):
    username = fields.Str()
    date_naissance = fields.Date()
    taille = fields.Int()
    dernierPoids = fields.Float()


class UserAjouterPoidsSchema(Schema):
    date = fields.Date(required=True)
    poids = fields.Float(required=True, validate=validate.Range(min=20, max=500))
    note = fields.Str(allow_none=True)


class UserConfigurer(Schema):
    date_naissance = fields.Date(required=False)
    taille = fields.Int(required=False)


class UserHistoriqueItem(Schema):
    poids = fields.Float(required=True)
    date = fields.Str(required=True)
    note = fields.Str(allow_none=True)


class UserHistoriqueResponse(Schema):
    historique = fields.List(fields.Nested(UserHistoriqueItem), required=True)


class UserChangementMdp(Schema):
    password = PASSWORD
    new_password = PASSWORD


class ChangementMdpInvalideSchema(BaseErrorSchema):
    """Erreur lors du changement de mot de passe"""

    code = fields.Int(metadata={"example": 401})
    message = fields.Str(metadata={"example": "Mot de passe actuel invalide"})
    status = fields.Str(metadata={"example": "Unauthorized"})


class ChangementMdpReussiSchema(Schema):
    """Réponse succès pour changement de mot de passe"""

    message = fields.Str(metadata={"example": "Mot de passe changé avec succès"})


class UserChangementUsername(Schema):
    """Réponse succès pour changement de mot de passe"""

    username = USERNAME


class ChangementUsernameReussiSchema(Schema):
    """Réponse succès pour changement de nom d'utilisateur"""

    message = fields.Str(metadata={"example": "Nom d'utilisateur changé avec succès"})
