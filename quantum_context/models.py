"""
Non-essentialist types with extra="allow".

Wave functions evolve. Observers change. Structure persists.
"""

from pydantic import BaseModel, ConfigDict, Field


class Measurement(BaseModel):
    """Raw observation - source of truth."""

    model_config = ConfigDict(extra="allow")  # Wu wei

    subject: str
    predicate: str
    object: str
    confidence: float = Field(ge=0.0, le=0.7, default=0.5)  # Ceiling at 0.7
    observer: str = "unknown"
    timestamp: str  # ISO format
    evidence: list[str] = []  # Evidence URLs/citations to boost confidence


class WaveAmplitude(BaseModel):
    """Wave function ψ projected onto entity."""

    model_config = ConfigDict(extra="allow")

    entity: str
    coefficients: list[float]  # aₙ in ψ = Σ aₙ·φₙ
    magnitude: float  # |ψ|
    phase: float | None = None  # Future: complex amplitudes


class DependencyGraph(BaseModel):
    """Divisibility structure (causal relationships)."""

    model_config = ConfigDict(extra="allow")

    subject: str
    depends_on: list[str] = []  # Things with high projection
    independent_of: list[str] = []  # Orthogonal concepts
    shared_structure: dict[str, float] = {}  # GCD-like overlaps
