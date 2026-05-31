"""SQLAlchemy ORM models — the persistence layer for the Personal Health Graph."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    sex: Mapped[str] = mapped_column(String(10))  # "male" | "female"
    birth_date: Mapped[date] = mapped_column(Date)
    # Lightweight lifestyle / history flags used by the risk + screening engines.
    smoker: Mapped[bool] = mapped_column(default=False)
    family_history: Mapped[str] = mapped_column(String(500), default="")  # csv tags
    region: Mapped[str] = mapped_column(String(10), default="intl")  # screening guideline region
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # --- Auth / accounts ---
    # Login identity. Dependent profiles (children) have no credentials of their own
    # and are managed by the account in managed_by_user_id.
    email: Mapped[str | None] = mapped_column(String(190), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    managed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    lab_results: Mapped[list["LabResult"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    policies: Mapped[list["InsurancePolicy"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    medications: Mapped[list["Medication"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    family_members: Mapped[list["FamilyMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class LabResult(Base):
    """A single measured marker at a point in time (e.g. LDL = 160 on 2024-01-02)."""

    __tablename__ = "lab_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    marker: Mapped[str] = mapped_column(String(40))  # canonical key, e.g. "ldl"
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20), default="")
    taken_on: Mapped[date] = mapped_column(Date)

    user: Mapped[User] = relationship(back_populates="lab_results")


class InsurancePolicy(Base):
    """A coverage line item parsed from an insurance policy."""

    __tablename__ = "insurance_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[str] = mapped_column(String(120))
    coverage_type: Mapped[str] = mapped_column(String(60))  # canonical key
    monthly_premium: Mapped[float] = mapped_column(Float, default=0.0)
    renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Extracted policy clauses (best-effort from PDF; 0/empty when unknown).
    deductible: Mapped[float] = mapped_column(Float, default=0.0)
    ceiling: Mapped[float] = mapped_column(Float, default=0.0)
    exclusions: Mapped[str] = mapped_column(String(1000), default="")

    user: Mapped[User] = relationship(back_populates="policies")


class Medication(Base):
    """A medication or supplement the user is taking."""

    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(80))  # canonical drug key
    dose: Mapped[str] = mapped_column(String(60), default="")

    user: Mapped[User] = relationship(back_populates="medications")


class FamilyMember(Base):
    """A relative and their relevant conditions, for the Family Health Graph."""

    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    relation: Mapped[str] = mapped_column(String(30))  # father, mother, sibling...
    conditions: Mapped[str] = mapped_column(String(500), default="")  # csv tags

    user: Mapped[User] = relationship(back_populates="family_members")


class ShareToken(Base):
    """A time-limited token that grants read-only access to a profile's report.

    Used to share a snapshot of the report with a clinician without requiring
    them to register. The token is opaque (URL-safe random) and expires after
    `expires_at`. Revoking = deletion.
    """

    __tablename__ = "share_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class HealthGoal(Base):
    """A user-defined target for a marker, evaluated against the latest LabResult."""

    __tablename__ = "health_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    marker: Mapped[str] = mapped_column(String(40))
    target_value: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(10))  # "below" | "above"
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
