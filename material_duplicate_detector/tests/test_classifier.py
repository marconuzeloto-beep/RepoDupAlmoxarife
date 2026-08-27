"""Testes do classificador (Sprint 7)."""

from __future__ import annotations

import pytest

from app.core.classifier import build_comparison_result, classify
from app.core.comparator import compare
from app.core.technical_parser import parse_material
from app.models.material import Material
from app.rules.rule_loader import load_rules


@pytest.fixture(scope="module")
def rules():
    return load_rules()


def _classify(text_a: str, text_b: str, rules):
    parsed_a = parse_material(Material(row_index=0, code="A", analysis_text=text_a), rules)
    parsed_b = parse_material(Material(row_index=1, code="B", analysis_text=text_b), rules)
    outcome = compare(parsed_a, parsed_b, rules)
    return classify(outcome), outcome


def test_formatting_only_difference_is_confirmed_duplicate(rules):
    classification, _ = _classify("PARAFUSO 20 CM X 1/2 MM", "PARAFUSO 20CMX1/2MM", rules)
    assert classification == "DUPLICADO_CONFIRMADO"


def test_identical_text_is_confirmed_duplicate(rules):
    classification, _ = _classify("PARAFUSO INOX M10", "PARAFUSO INOX M10", rules)
    assert classification == "DUPLICADO_CONFIRMADO"


def test_unknown_extra_word_is_probable_duplicate(rules):
    classification, _ = _classify("PARAFUSO INOX REFORCADO", "PARAFUSO INOX", rules)
    assert classification == "PROVAVEL_DUPLICADO"


def test_m10_vs_m12_is_similar_but_different(rules):
    classification, _ = _classify("PARAFUSO M10", "PARAFUSO M12", rules)
    assert classification == "SEMELHANTE_DIFERENTE"


def test_dianteiro_vs_traseiro_is_similar_but_different(rules):
    classification, _ = _classify("SUPORTE DIANTEIRO", "SUPORTE TRASEIRO", rules)
    assert classification == "SEMELHANTE_DIFERENTE"


def test_build_comparison_result_contains_explanations(rules):
    parsed_a = parse_material(Material(row_index=0, code="5000000001", analysis_text="PARAFUSO 20 CM X 1/2 MM"), rules)
    parsed_b = parse_material(Material(row_index=1, code="5000000002", analysis_text="PARAFUSO 20CMX1/2MM"), rules)
    outcome = compare(parsed_a, parsed_b, rules)
    result = build_comparison_result(outcome)

    assert result.classification == "DUPLICADO_CONFIRMADO"
    assert result.code_a == "5000000001"
    assert result.code_b == "5000000002"
    assert result.text_a == "PARAFUSO 20 CM X 1/2 MM"
    assert result.text_b == "PARAFUSO 20CMX1/2MM"
    assert "PARAFUSO" in result.equal_elements
    assert result.formatting_differences
    assert result.technical_differences == []
    assert result.review_status == "PENDENTE"
    assert 0.0 <= result.confidence <= 1.0
