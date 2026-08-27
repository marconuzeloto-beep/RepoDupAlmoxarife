"""Leitura de planilhas Excel (.xlsx) via pandas/openpyxl (Sprint 1).

Responsavel apenas por acesso a arquivo/planilha e conversao para
``Material``. Nao contem nenhuma regra de normalizacao ou comparacao.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.models.material import Material


class ExcelFileError(Exception):
    """Erro ao abrir ou interpretar o arquivo Excel."""


class ColumnNotFoundError(Exception):
    """Coluna solicitada nao existe na planilha."""


def list_sheet_names(file_path: str | Path) -> list[str]:
    """Retorna os nomes das planilhas (abas) de um arquivo .xlsx."""
    path = Path(file_path)
    if not path.exists():
        raise ExcelFileError(f"Arquivo nao encontrado: {path}")
    if path.suffix.lower() != ".xlsx":
        raise ExcelFileError(f"Formato nao suportado: {path.suffix} (esperado .xlsx)")
    try:
        with pd.ExcelFile(path, engine="openpyxl") as excel_file:
            return list(excel_file.sheet_names)
    except Exception as exc:  # arquivo corrompido, nao e um xlsx valido, etc.
        raise ExcelFileError(f"Nao foi possivel abrir o arquivo: {exc}") from exc


def list_columns(file_path: str | Path, sheet_name: str) -> list[str]:
    """Retorna os nomes das colunas (cabecalho) de uma planilha especifica."""
    df = _read_sheet(file_path, sheet_name, nrows=0)
    return [str(c) for c in df.columns]


def load_materials(
    file_path: str | Path,
    sheet_name: str,
    code_column: str,
    analysis_column: str,
) -> list[Material]:
    """Le a planilha e converte cada linha em um ``Material``.

    Linhas com o texto de analise vazio sao ignoradas (nao ha o que
    comparar). Codigo vazio e mantido como string vazia — a decisao de
    como tratar isso fica a cargo das camadas superiores.
    """
    df = _read_sheet(file_path, sheet_name)

    for column in (code_column, analysis_column):
        if column not in df.columns:
            raise ColumnNotFoundError(
                f"Coluna '{column}' nao encontrada. Colunas disponiveis: "
                f"{list(df.columns)}"
            )

    materials: list[Material] = []
    for row_index, row in df.iterrows():
        analysis_text = _cell_to_text(row[analysis_column])
        if not analysis_text:
            continue
        code = _cell_to_text(row[code_column])
        raw_fields = {str(col): _cell_to_text(row[col]) for col in df.columns}
        materials.append(
            Material(
                row_index=int(row_index),
                code=code,
                analysis_text=analysis_text,
                raw_fields=raw_fields,
            )
        )
    return materials


def _read_sheet(file_path: str | Path, sheet_name: str, nrows: int | None = None) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise ExcelFileError(f"Arquivo nao encontrado: {path}")
    if path.suffix.lower() != ".xlsx":
        raise ExcelFileError(f"Formato nao suportado: {path.suffix} (esperado .xlsx)")
    try:
        return pd.read_excel(
            path,
            sheet_name=sheet_name,
            engine="openpyxl",
            dtype=str,
            nrows=nrows,
        )
    except ValueError as exc:
        raise ExcelFileError(f"Planilha '{sheet_name}' nao encontrada: {exc}") from exc
    except Exception as exc:
        raise ExcelFileError(f"Nao foi possivel ler a planilha: {exc}") from exc


def _cell_to_text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()
