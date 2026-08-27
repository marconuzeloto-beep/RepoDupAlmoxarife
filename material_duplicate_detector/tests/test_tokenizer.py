"""Testes do tokenizador tecnico (Sprint 3)."""

from __future__ import annotations

from app.core.normalizer import normalize
from app.core.tokenizer import (
    Token,
    extract_numbers,
    extract_symbols,
    extract_units,
    extract_words,
    numeric_value,
    tokenize,
)


def _tokenize_raw(text: str) -> list[Token]:
    return tokenize(normalize(text).normalized_text)


def test_tokenize_glued_measure_matches_spaced_version():
    a = _tokenize_raw("20 CM X 1/2 MM")
    b = _tokenize_raw("20CMX1/2MM")
    assert a == b
    assert [t.type for t in a] == [
        "INTEGER", "UNIT", "SEPARATOR", "FRACTION", "UNIT",
    ]


def test_tokenize_protected_symbol_is_preserved_and_distinct():
    with_symbol = _tokenize_raw('1/2"')
    without_symbol = _tokenize_raw("1/2")
    assert extract_symbols(with_symbol) == ['"']
    assert extract_symbols(without_symbol) == []
    assert with_symbol != without_symbol


def test_tokenize_technical_codes_are_not_split():
    tokens_m10 = _tokenize_raw("PARAFUSO M10")
    tokens_m12 = _tokenize_raw("PARAFUSO M12")
    assert extract_words(tokens_m10) == ["PARAFUSO", "M10"]
    assert extract_words(tokens_m12) == ["PARAFUSO", "M12"]
    assert tokens_m10 != tokens_m12


def test_extract_numbers_and_units():
    tokens = _tokenize_raw("PARAFUSO 20CMX1/2MM INOX")
    assert extract_numbers(tokens) == ["20", "1/2"]
    assert extract_units(tokens) == ["CM", "MM"]
    assert extract_words(tokens) == ["PARAFUSO", "INOX"]


def test_numeric_value_handles_fraction_and_decimal():
    assert numeric_value("1/2") == 0.5
    assert numeric_value("12,5") == 12.5
    assert numeric_value("12.5") == 12.5
    assert numeric_value("20") == 20.0


def test_tokenize_empty_text():
    assert tokenize("") == []
