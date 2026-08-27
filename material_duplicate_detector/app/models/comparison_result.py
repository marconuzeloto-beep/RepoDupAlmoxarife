"""Modelo do resultado de comparacao explicavel (Sprint 6/7)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Classification = Literal["DUPLICADO_CONFIRMADO", "PROVAVEL_DUPLICADO", "SEMELHANTE_DIFERENTE"]
ReviewStatus = Literal["PENDENTE", "APROVADO", "REJEITADO"]


@dataclass(frozen=True)
class ComparisonResult:
    code_a: str
    code_b: str
    text_a: str
    text_b: str
    classification: Classification
    confidence: float
    equal_elements: list[str] = field(default_factory=list)
    formatting_differences: list[str] = field(default_factory=list)
    technical_differences: list[str] = field(default_factory=list)
    ambiguous_differences: list[str] = field(default_factory=list)
    review_status: ReviewStatus = "PENDENTE"
    observation: str = ""
