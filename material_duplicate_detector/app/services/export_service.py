"""Exportacao dos resultados para Excel (Sprint 9).

Escreve com ``openpyxl`` no modo ``write_only`` (streaming): cada linha
e serializada e descartada da memoria assim que e escrita, em vez de
manter todas as celulas da planilha como objetos Python (o que e o que
``pandas.DataFrame.to_excel``/``openpyxl`` no modo normal fazem, e o
que causava ``MemoryError`` ao exportar centenas de milhares de pares).
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

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
# o cabecalho. Quando o numero de resultados ultrapassa isso, os dados
# sao divididos em varias planilhas dentro do mesmo arquivo.
_EXCEL_MAX_ROWS_PER_SHEET = 1_048_576


def export_results_to_excel(
    results: list[ComparisonResult],
    output_path: str | Path,
    max_rows_per_sheet: int = _EXCEL_MAX_ROWS_PER_SHEET,
) -> list[str]:
    """Exporta ``results`` para ``output_path`` em modo streaming.

    Se ``results`` tiver mais linhas do que uma planilha do Excel
    suporta, os dados sao divididos automaticamente em varias planilhas
    ("Resultados", "Resultados_2", ...) dentro do mesmo arquivo, em vez
    de falhar. Retorna a lista de nomes de planilhas criadas.
    """
    max_data_rows = max(1, max_rows_per_sheet - 1)  # a linha 1 e o cabecalho

    workbook = Workbook(write_only=True)
    sheet_names: list[str] = []

    def start_sheet():
        sheet_index = len(sheet_names) + 1
        name = "Resultados" if sheet_index == 1 else f"Resultados_{sheet_index}"
        sheet_names.append(name)
        worksheet = workbook.create_sheet(title=name)
        worksheet.append(_COLUMNS)
        return worksheet

    current_sheet = start_sheet()
    rows_in_current_sheet = 0
    for result in results:
        if rows_in_current_sheet >= max_data_rows:
            current_sheet = start_sheet()
            rows_in_current_sheet = 0
        current_sheet.append(_result_to_row(result))
        rows_in_current_sheet += 1

    workbook.save(output_path)
    return sheet_names


def _result_to_row(r: ComparisonResult) -> list:
    return [
        r.code_a,
        r.code_b,
        r.text_a,
        r.text_b,
        r.classification,
        r.confidence,
        "; ".join(r.equal_elements),
        "; ".join(r.formatting_differences),
        "; ".join(r.technical_differences),
        "; ".join(r.ambiguous_differences),
        r.review_status,
        r.observation,
    ]
