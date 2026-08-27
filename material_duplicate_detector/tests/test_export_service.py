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

    sheet_names = export_results_to_excel(results, output_path)

    assert output_path.exists()
    assert sheet_names == ["Resultados"]
    df = pd.read_excel(output_path, engine="openpyxl", dtype=str)
    assert list(df["Codigo A"]) == ["5000000001", "5000000003"]
    assert list(df["Classificacao"]) == ["DUPLICADO_CONFIRMADO", "SEMELHANTE_DIFERENTE"]
    assert df.loc[0, "Elementos Tecnicos Iguais"] == "PARAFUSO"


def test_export_empty_results(tmp_path):
    output_path = tmp_path / "vazio.xlsx"
    sheet_names = export_results_to_excel([], output_path)
    assert sheet_names == ["Resultados"]
    df = pd.read_excel(output_path, engine="openpyxl")
    assert df.empty


def test_export_splits_across_multiple_sheets_when_exceeding_row_limit(tmp_path):
    # Regressao: planilhas reais com muitos candidatos podem gerar mais
    # resultados do que uma unica planilha do Excel suporta (limite real:
    # 1.048.576 linhas). Antes da correcao, pandas.to_excel lancava
    # ValueError ("This sheet is too large!") e a exportacao falhava por
    # completo. Usa um limite pequeno via `max_rows_per_sheet` para nao
    # precisar gerar milhoes de linhas neste teste.
    results = [
        ComparisonResult(
            code_a=str(i),
            code_b=str(i + 1),
            text_a="PARAFUSO A",
            text_b="PARAFUSO B",
            classification="SEMELHANTE_DIFERENTE",
            confidence=0.5,
        )
        for i in range(25)
    ]
    output_path = tmp_path / "resultados_grandes.xlsx"

    sheet_names = export_results_to_excel(results, output_path, max_rows_per_sheet=10)

    # 10 linhas por planilha, 1 delas e o cabecalho -> 9 linhas de dados
    # por planilha; 25 resultados / 9 = 3 planilhas.
    assert sheet_names == ["Resultados", "Resultados_2", "Resultados_3"]

    total_rows = 0
    for sheet_name in sheet_names:
        df = pd.read_excel(output_path, sheet_name=sheet_name, engine="openpyxl", dtype=str)
        assert len(df) <= 9
        total_rows += len(df)
    assert total_rows == 25
