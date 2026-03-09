import enum
import logging
from datetime import date, datetime
from typing import Optional

import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import check_password_hash

from app import db

model_logger = logging.getLogger("OneFit.Models")


class DayOfWeek(enum.Enum):
    Lundi = "Lundi"
    Mardi = "Mardi"
    Mercredi = "Mercredi"
    Jeudi = "Jeudi"
    Vendredi = "Vendredi"
    Samedi = "Samedi"
    Dimanche = "Dimanche"


class User(db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256))
    date_naissance: so.Mapped["date"] = so.mapped_column(sa.Date)
    taille: so.Mapped[int] = so.mapped_column(sa.Integer)

    historique_poids: so.Mapped[list["HistoriquePoids"]] = so.relationship(back_populates="user", cascade="all, delete-orphan")
    routines: so.Mapped[list["Routine"]] = so.relationship(back_populates="user", cascade="all, delete-orphan")
    workout_logs: so.Mapped[list["WorkoutLog"]] = so.relationship(back_populates="user")

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

    def activeRoutine(self):
        return next((r for r in self.routines if r.is_active), None)

    def setActiveRoutine(self, routine_id: int):
        for routine in self.routines:
            if routine.id == routine_id:
                if not routine.is_active:
                    model_logger.info(f"Routine activée | user_id={self.id} | routine_id={routine.id} | name={routine.name}")
                routine.is_active = True
            else:
                if routine.is_active:
                    model_logger.info(f"Routine désactivée | user_id={self.id} | routine_id={routine.id} | name={routine.name}")
                routine.is_active = False

class Routine(db.Model):
    __tablename__ = "routines"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    name: so.Mapped[str] = so.mapped_column(sa.String, nullable=False)
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    user: so.Mapped["User"] = so.relationship(back_populates="routines")
    seances: so.Mapped[list["Seance"]] = so.relationship(back_populates="routine", cascade="all, delete-orphan")


class Seance(db.Model):
    __tablename__ = "seances"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    routine_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("routines.id"), nullable=False)
    day: so.Mapped[DayOfWeek] = so.mapped_column(sa.Enum(DayOfWeek), nullable=False)
    title: so.Mapped[Optional[str]] = so.mapped_column(sa.String)
    is_rest_day: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    routine: so.Mapped["Routine"] = so.relationship(back_populates="seances")
    exercises_plan: so.Mapped[list["SeanceExercise"]] = so.relationship(back_populates="seance", cascade="all, delete-orphan")


class SeanceExercise(db.Model):
    __tablename__ = "seance_exercises"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    seance_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("seances.id"), nullable=False)
    exercise_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("exercise.id"), nullable=False)
    ordre: so.Mapped[int] = so.mapped_column(sa.Integer, default=1)
    planned_sets: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    planned_reps: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    planned_weight: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)

    seance: so.Mapped["Seance"] = so.relationship(back_populates="exercises_plan")
    exercise: so.Mapped["Exercise"] = so.relationship()


class WorkoutLog(db.Model):
    __tablename__ = "workout_logs"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    exercise_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("exercise.id"), nullable=False)
    seance_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("seances.id"))
    reps: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    weight: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=sa.func.now())
    note: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    user: so.Mapped["User"] = so.relationship(back_populates="workout_logs")
    exercise: so.Mapped["Exercise"] = so.relationship()


class HistoriquePoids(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"))

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
