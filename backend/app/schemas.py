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


class ProtectedSchema(Schema):
    logged_in_as = fields.Str()
