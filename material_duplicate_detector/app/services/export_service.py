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

# Limite real do Excel (.xlsx): 1.048.576 linhas por planilha, contando
# o cabecalho. Quando o numero de resultados ultrapassa isso, o pandas
# lanca ValueError ("This sheet is too large!") — em bases muito
# grandes/com muitos termos em comum, o numero de pares candidatos pode
# passar de um milhao. Em vez de falhar, os resultados sao divididos em
# varias planilhas dentro do mesmo arquivo.
_EXCEL_MAX_ROWS_PER_SHEET = 1_048_576


def export_results_to_excel(
    results: list[ComparisonResult],
    output_path: str | Path,
    max_rows_per_sheet: int = _EXCEL_MAX_ROWS_PER_SHEET,
) -> list[str]:
    """Exporta os resultados para ``output_path``.

    Se ``results`` tiver mais linhas do que uma planilha do Excel
    suporta, os dados sao divididos automaticamente em varias planilhas
    ("Resultados", "Resultados_2", ...) dentro do mesmo arquivo, em vez
    de falhar. Retorna a lista de nomes de planilhas criadas.
    """
    rows = [_result_to_row(r) for r in results]
    max_data_rows = max(1, max_rows_per_sheet - 1)  # a linha 1 e o cabecalho

    sheet_names: list[str] = []
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        chunks = [rows[i : i + max_data_rows] for i in range(0, len(rows), max_data_rows)] or [[]]
        for index, chunk in enumerate(chunks, start=1):
            sheet_name = "Resultados" if index == 1 else f"Resultados_{index}"
            df = pd.DataFrame(chunk, columns=_COLUMNS)
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            sheet_names.append(sheet_name)

    return sheet_names


def _result_to_row(r: ComparisonResult) -> dict:
    return {
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
