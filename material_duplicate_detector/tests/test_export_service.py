"""Testes de exportacao de resultados para Excel (Sprint 9)."""

from __future__ import annotations

import pandas as pd

from app.models.comparison_result import ComparisonResult
from app.services.export_service import export_results_to_excel


def test_export_results_to_excel(tmp_path):
    results = [
        ComparisonResult(
            code_a="5000000001",
            code_b="5000000002",
            text_a="PARAFUSO 20 CM X 1/2 MM",
            text_b="PARAFUSO 20CMX1/2MM",
            classification="DUPLICADO_CONFIRMADO",
            confidence=0.95,
            equal_elements=["PARAFUSO"],
            formatting_differences=["espacos"],
            technical_differences=[],
            ambiguous_differences=[],
        ),
        ComparisonResult(
            code_a="5000000003",
            code_b="5000000004",
            text_a="PARAFUSO M10",
            text_b="PARAFUSO M12",
            classification="SEMELHANTE_DIFERENTE",
            confidence=0.9,
            equal_elements=["PARAFUSO"],
            formatting_differences=[],
            technical_differences=["codigos tecnicos exclusivos: A=['M10'] B=['M12']"],
            ambiguous_differences=[],
        ),
    ]
    output_path = tmp_path / "resultados.xlsx"

    export_results_to_excel(results, output_path)

    assert output_path.exists()
    df = pd.read_excel(output_path, engine="openpyxl", dtype=str)
    assert list(df["Codigo A"]) == ["5000000001", "5000000003"]
    assert list(df["Classificacao"]) == ["DUPLICADO_CONFIRMADO", "SEMELHANTE_DIFERENTE"]
    assert df.loc[0, "Elementos Tecnicos Iguais"] == "PARAFUSO"


def test_export_empty_results(tmp_path):
    output_path = tmp_path / "vazio.xlsx"
    export_results_to_excel([], output_path)
    df = pd.read_excel(output_path, engine="openpyxl")
    assert df.empty
