import logging
from datetime import date, datetime
from typing import Optional

import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import check_password_hash

from app import db

model_logger = logging.getLogger("OneFit.Models")


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256))
    date_naissance: so.Mapped["date"] = so.mapped_column(sa.Date)
    taille: so.Mapped[int] = so.mapped_column(sa.Integer)

    historique_poids: so.Mapped[list["HistoriquePoids"]] = so.relationship(back_populates="user", cascade="all, delete-orphan")

    def checkPassword(self, password: str) -> bool:
        result = check_password_hash(self.password, password)
        if not result:
            model_logger.debug(f"Password check fail | user_id={self.id}")
        return result

    def getHistoriquePoidsPanda(self):
        df = pd.DataFrame([{"poids": p.poids, "date": p.date, "note": p.note} for p in self.historique_poids])
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
        model_logger.debug(f"Load historique | user_id={self.id} | rows={len(df)}")
        return df


class HistoriquePoids(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"))

    poids: so.Mapped[float] = so.mapped_column()
    date: so.Mapped["date"] = so.mapped_column(sa.Date, default=date.today)
    note: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200), nullable=True)

    user: so.Mapped["User"] = so.relationship(back_populates="historique_poids")


class Exercise(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    id_api: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), unique=True, index=True)

    name: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True)

    img_url: so.Mapped[str] = so.mapped_column(sa.String)
    video_url: so.Mapped[str] = so.mapped_column(sa.String)

    overview: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)
    instructions: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)
    body_part: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))


class RequestLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    cache_key: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), nullable=True, index=True)
    status_code: so.Mapped[int] = so.mapped_column()

    cache_hits: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    timestamp: so.Mapped["datetime"] = so.mapped_column(sa.DateTime, server_default=sa.func.now())

    response_body: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)
