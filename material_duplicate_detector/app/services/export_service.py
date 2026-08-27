"""Exportacao dos resultados para Excel (Sprint 9)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.models.comparison_result import ComparisonResult

_COLUMNS = [
    "Codigo A",
    "Codigo B",
    "Texto A",
    "Texto B",
    "Classificacao",
    "Confianca",
    "Elementos Tecnicos Iguais",
    "Diferencas de Formatacao",
    "Diferencas Tecnicas",
    "Termos Ambiguos",
    "Status de Revisao",
    "Observacao",
]


def export_results_to_excel(results: list[ComparisonResult], output_path: str | Path) -> None:
    rows = [
        {
            "Codigo A": r.code_a,
            "Codigo B": r.code_b,
            "Texto A": r.text_a,
            "Texto B": r.text_b,
            "Classificacao": r.classification,
            "Confianca": r.confidence,
            "Elementos Tecnicos Iguais": "; ".join(r.equal_elements),
            "Diferencas de Formatacao": "; ".join(r.formatting_differences),
            "Diferencas Tecnicas": "; ".join(r.technical_differences),
            "Termos Ambiguos": "; ".join(r.ambiguous_differences),
            "Status de Revisao": r.review_status,
            "Observacao": r.observation,
        }
        for r in results
    ]
    df = pd.DataFrame(rows, columns=_COLUMNS)
    df.to_excel(output_path, index=False, engine="openpyxl")
