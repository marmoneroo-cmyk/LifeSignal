"""Pydantic request/response schemas (validation at the system boundary)."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

Sex = str  # "male" | "female"
Priority = str  # "critical" | "high" | "preventive" | "informational"


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sex: Sex
    birth_date: date
    smoker: bool = False
    family_history: list[str] = Field(default_factory=list)
    region: str = "intl"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    sex: str
    birth_date: date
    age: int
    smoker: bool
    region: str = "intl"
    managed_by_user_id: int | None = None


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=190)
    password: str = Field(min_length=6, max_length=128)
    sex: Sex
    birth_date: date
    smoker: bool = False
    family_history: list[str] = Field(default_factory=list)
    region: str = "intl"


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


class DependentIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sex: Sex
    birth_date: date
    smoker: bool = False
    family_history: list[str] = Field(default_factory=list)
    region: str = "intl"


class LabResultIn(BaseModel):
    marker: str
    value: float
    unit: str = ""
    taken_on: date


class LabBatchIn(BaseModel):
    results: list[LabResultIn] = Field(min_length=1)


class PolicyIn(BaseModel):
    provider: str
    coverage_type: str
    monthly_premium: float = 0.0
    renewal_date: date | None = None
    deductible: float = 0.0
    ceiling: float = 0.0
    exclusions: str = ""


class PolicyBatchIn(BaseModel):
    policies: list[PolicyIn] = Field(min_length=1)


# ---- Analysis output shapes -------------------------------------------------

class Finding(BaseModel):
    title: str
    detail: str
    priority: Priority
    source: str  # which engine produced it
    plain_language: str = ""


class TrendPoint(BaseModel):
    taken_on: date
    value: float


class MarkerTrend(BaseModel):
    marker: str
    label: str
    unit: str
    points: list[TrendPoint]
    direction: str  # "rising" | "falling" | "stable"
    status: str  # "normal" | "borderline" | "abnormal"
    # Sex-adjusted reference range so the UI can draw the "normal" band.
    ref_low: float | None = None
    ref_high: float | None = None


class ScoreComponent(BaseModel):
    domain: str
    score: int  # 0-100
    note: str


class MedicationIn(BaseModel):
    name: str
    dose: str = ""


class MedicationBatchIn(BaseModel):
    medications: list[MedicationIn] = Field(min_length=1)


class FamilyMemberIn(BaseModel):
    relation: str
    conditions: list[str] = Field(default_factory=list)


class FamilyBatchIn(BaseModel):
    members: list[FamilyMemberIn] = Field(min_length=1)


class Percentile(BaseModel):
    marker: str
    label: str
    value: float
    percentile: int
    higher_is_risk: bool


class Copilot(BaseModel):
    questions: list[str]
    changes_since_last: list[str]
    disclaimer: str


class Narrative(BaseModel):
    text: str
    generated_by: str  # "claude" | "rule_based" | "rule_based_fallback"
    model: str | None = None
    disclaimer: str


class HealthReport(BaseModel):
    user: UserOut
    health_score: int
    score_components: list[ScoreComponent]
    top_priorities: list[Finding]
    findings: list[Finding]
    trends: list[MarkerTrend]
    missing_screenings: list[Finding]
    insurance_insights: list[Finding]
    notifications: list[Finding]
    emergency_alerts: list[Finding]
    drug_interactions: list[Finding]
    family_insights: list[Finding]
    coverage_matches: list[Finding]
    projections: list[Finding]
    percentiles: list[Percentile]
    second_opinions: list[Finding] = Field(default_factory=list)
    insurance_negotiation: list[Finding] = Field(default_factory=list)
    claim_opportunities: list[Finding] = Field(default_factory=list)
    disclaimer: str
