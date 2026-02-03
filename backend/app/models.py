from datetime import date
from typing import Optional

import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import check_password_hash

from app import db


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256))

    historique_poids: so.Mapped[list["HistoriquePoids"]] = so.relationship(back_populates="user", cascade="all, delete-orphan")

    def checkPassword(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def getHistoriquePoidsPanda(self):
        df = pd.DataFrame([{"poids": p.poids, "date": p.date, "note": p.note} for p in self.historique_poids])
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df


class HistoriquePoids(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"))
    poids: so.Mapped[float] = so.mapped_column()
    date: so.Mapped["date"] = so.mapped_column(sa.Date, default=date.today)
    note: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200), nullable=True)

    user: so.Mapped["User"] = so.relationship(back_populates="historique_poids")

    def __repr__(self) -> str:
        return f"<HistoriquePoids {self.poids}kg @ {self.date.strftime('%d/%m/%Y')}>"
