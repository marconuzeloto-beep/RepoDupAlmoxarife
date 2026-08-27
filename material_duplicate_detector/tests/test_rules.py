"""Testes de regras e equivalencias configuraveis (Sprint 4)."""

from __future__ import annotations

import json

import pytest

from app.rules.abbreviations import canonical_term
from app.rules.critical_terms import are_incompatible, find_incompatible_terms
from app.rules.equivalents import are_equivalent
from app.rules.protected_symbols import is_protected
from app.rules.rule_loader import load_rules


@pytest.fixture(scope="module")
def rules():
    return load_rules()


def test_load_rules_from_project_config():
    rules = load_rules()
    assert rules.abbreviation_to_canonical
    assert rules.incompatible_groups
    assert rules.protected_symbols


def test_abbreviation_equivalence_diant(rules):
    assert canonical_term("DIANT", rules) == canonical_term("DIANTEIRO", rules)
    assert are_equivalent("DIANT", "DIANTEIRO", rules)
    assert are_equivalent("DIANTEIRA", "DIANTEIRO", rules)


def test_dianteiro_traseiro_never_equivalent(rules):
    assert not are_equivalent("DIANTEIRO", "TRASEIRO", rules)
    assert are_incompatible("DIANTEIRO", "TRASEIRO", rules)


def test_masculino_feminino_incompatible(rules):
    assert are_incompatible("MASCULINO", "FEMININO", rules)


def test_azul_preto_incompatible(rules):
    assert are_incompatible("AZUL", "PRETO", rules)


def test_same_term_is_never_incompatible(rules):
    assert not are_incompatible("AZUL", "AZUL", rules)


def test_find_incompatible_terms(rules):
    pairs = find_incompatible_terms(["PARAFUSO", "DIANTEIRO"], ["PARAFUSO", "TRASEIRO"], rules)
    assert ("DIANTEIRO", "TRASEIRO") in pairs


def test_protected_symbol_inch(rules):
    assert is_protected('"', rules)
    assert not is_protected("Z", rules)


def test_load_rules_custom_directory(tmp_path):
    (tmp_path / "abbreviations.json").write_text(
        json.dumps({"ABC": "ABCD"}), encoding="utf-8"
    )
    (tmp_path / "equivalents.json").write_text(json.dumps({"groups": []}), encoding="utf-8")
    (tmp_path / "critical_terms.json").write_text(
        json.dumps({"incompatible_groups": [["X", "Y"]]}), encoding="utf-8"
    )
    (tmp_path / "protected_symbols.json").write_text(
        json.dumps({"protected": ["@"]}), encoding="utf-8"
    )

    rules = load_rules(tmp_path)
    assert rules.canonical_term("ABC") == "ABCD"
    assert rules.are_incompatible("X", "Y")
    assert rules.is_protected_symbol("@")


def test_load_rules_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_rules(tmp_path)
