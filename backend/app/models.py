import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import check_password_hash

from app import db, ma


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256))

    def checkPassword(self, password):
        return check_password_hash(self.password, password)
