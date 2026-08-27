"""Testes de importacao de Excel (Sprint 1)."""

from __future__ import annotations

import pandas as pd
import pytest

from app.services.excel_service import (
    ColumnNotFoundError,
    ExcelFileError,
    list_columns,
    list_sheet_names,
    load_materials,
)


@pytest.fixture
def sample_xlsx(tmp_path):
    path = tmp_path / "materiais.xlsx"
    df = pd.DataFrame(
        {
            "Codigo Material": ["5000000001", "5000000002", "5000000003", ""],
            "Texto Dados Basicos": [
                "PARAFUSO 20 CM X 1/2 MM",
                "PARAFUSO 20CMX1/2MM",
                None,
                "SEM CODIGO",
            ],
        }
    )
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
        df.head(1).to_excel(writer, sheet_name="Resumo", index=False)
    return path


def test_list_sheet_names(sample_xlsx):
    assert list_sheet_names(sample_xlsx) == ["Data", "Resumo"]


def test_list_columns(sample_xlsx):
    assert list_columns(sample_xlsx, "Data") == ["Codigo Material", "Texto Dados Basicos"]


def test_load_materials_skips_empty_analysis_text(sample_xlsx):
    materials = load_materials(sample_xlsx, "Data", "Codigo Material", "Texto Dados Basicos")
    assert len(materials) == 3
    assert materials[0].code == "5000000001"
    assert materials[0].analysis_text == "PARAFUSO 20 CM X 1/2 MM"
    assert materials[2].code == ""
    assert materials[2].analysis_text == "SEM CODIGO"


def test_load_materials_missing_column_raises(sample_xlsx):
    with pytest.raises(ColumnNotFoundError):
        load_materials(sample_xlsx, "Data", "Codigo Inexistente", "Texto Dados Basicos")


def test_file_not_found_raises():
    with pytest.raises(ExcelFileError):
        list_sheet_names("nao_existe.xlsx")


def test_invalid_extension_raises(tmp_path):
    bad = tmp_path / "materiais.txt"
    bad.write_text("nao e um excel")
    with pytest.raises(ExcelFileError):
        list_sheet_names(bad)


def test_corrupted_file_raises(tmp_path):
    bad = tmp_path / "materiais.xlsx"
    bad.write_bytes(b"isto nao e um arquivo xlsx valido")
    with pytest.raises(ExcelFileError):
        list_sheet_names(bad)
