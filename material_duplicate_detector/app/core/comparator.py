"""Comparador tecnico profundo e explicavel (Sprint 6).

Nunca decide duplicidade sozinho: produz uma comparacao estruturada por
categoria (termos, numeros, unidades, simbolos, ordem) que o classificador
(Sprint 7) usa para decidir a classificacao final. A similaridade textual
e calculada apenas como sinal auxiliar (``textual_similarity``), nunca
como criterio de decisao.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from app.models.parsed_material import ParsedMaterial
from app.rules.rule_loader import RuleSet

_FORMATTING_LABELS: dict[str, str] = {
    "espacos_nas_bordas": "espacos nas bordas",
    "maiusculizacao": "uso de maiusculas/minusculas",
    "normalizacao_de_acentos": "acentuacao",
    "separacao_numero_letra": "agrupamento dos caracteres (numero colado a unidade)",
    "separacao_de_x_dimensional": "utilizacao do X como separador dimensional",
    "colapso_de_espacos": "espacos multiplos",
}


@dataclass(frozen=True)
class ComparisonOutcome:
    material_a: ParsedMaterial
    material_b: ParsedMaterial
    equal_elements: list[str] = field(default_factory=list)
    formatting_differences: list[str] = field(default_factory=list)
    technical_differences: list[str] = field(default_factory=list)
    order_differs_only: bool = False
    ambiguous: bool = False
    textual_similarity: float = 0.0

    @property
    def has_technical_difference(self) -> bool:
        return len(self.technical_differences) > 0


def compare(parsed_a: ParsedMaterial, parsed_b: ParsedMaterial, rules: RuleSet) -> ComparisonOutcome:
    equal_elements: list[str] = []
    technical_differences: list[str] = []

    terms_a = set(parsed_a.normalized_terms)
    terms_b = set(parsed_b.normalized_terms)
    equal_elements.extend(sorted(terms_a & terms_b))

    only_a = terms_a - terms_b
    only_b = terms_b - terms_a
    _compare_term_sets(only_a, only_b, rules, technical_differences)

    numbers_a = {_number_key(n) for n in parsed_a.numbers}
    numbers_b = {_number_key(n) for n in parsed_b.numbers}
    if numbers_a != numbers_b:
        only_numbers_a = sorted(numbers_a - numbers_b)
        only_numbers_b = sorted(numbers_b - numbers_a)
        if only_numbers_a or only_numbers_b:
            technical_differences.append(
                f"numeros divergentes: A={only_numbers_a or '-'} B={only_numbers_b or '-'}"
            )

    units_a = set(parsed_a.units)
    units_b = set(parsed_b.units)
    if units_a != units_b:
        technical_differences.append(
            f"unidades divergentes: A={sorted(units_a - units_b) or '-'} "
            f"B={sorted(units_b - units_a) or '-'}"
        )

    symbols_a = set(parsed_a.symbols)
    symbols_b = set(parsed_b.symbols)
    formatting_differences: list[str] = []
    for symbol in symbols_a ^ symbols_b:
        if rules.is_protected_symbol(symbol):
            side = "A" if symbol in symbols_a else "B"
            technical_differences.append(
                f"simbolo tecnico presente apenas em {side}: '{symbol}'"
            )
        else:
            formatting_differences.append(f"simbolo de formatacao: '{symbol}'")

    formatting_transformations = set(parsed_a.applied_transformations) | set(
        parsed_b.applied_transformations
    )
    for key in sorted(formatting_transformations):
        formatting_differences.append(_FORMATTING_LABELS.get(key, key))

    order_differs_only = False
    if not technical_differences and terms_a == terms_b:
        ordered_a = [t for t in parsed_a.normalized_terms]
        ordered_b = [t for t in parsed_b.normalized_terms]
        if ordered_a != ordered_b:
            order_differs_only = True
            formatting_differences.append("ordem dos elementos")

    similarity = SequenceMatcher(None, parsed_a.normalized_text, parsed_b.normalized_text).ratio()

    ambiguous = _is_ambiguous(only_a, only_b, technical_differences)

    return ComparisonOutcome(
        material_a=parsed_a,
        material_b=parsed_b,
        equal_elements=equal_elements,
        formatting_differences=sorted(set(formatting_differences)),
        technical_differences=technical_differences,
        order_differs_only=order_differs_only,
        ambiguous=ambiguous,
        textual_similarity=similarity,
    )


def _compare_term_sets(
    only_a: set[str], only_b: set[str], rules: RuleSet, technical_differences: list[str]
) -> None:
    """Para cada termo exclusivo de A, verifica se ele e explicitamente
    incompativel com algum termo exclusivo de B (ex.: DIANTEIRO x
    TRASEIRO). Termos exclusivos que sobram sem correspondencia tambem
    sao reportados como diferenca tecnica (ex.: M10 x M12)."""
    matched_a: set[str] = set()
    matched_b: set[str] = set()

    for term_a in only_a:
        for term_b in only_b:
            if rules.are_incompatible(term_a, term_b):
                technical_differences.append(f"termos tecnicamente incompativeis: {term_a} x {term_b}")
                matched_a.add(term_a)
                matched_b.add(term_b)

    remaining_a = sorted(only_a - matched_a)
    remaining_b = sorted(only_b - matched_b)
    if remaining_a or remaining_b:
        technical_differences.append(
            f"termos exclusivos: A={remaining_a or '-'} B={remaining_b or '-'}"
        )


def _number_key(token_value: str) -> str:
    from app.core.tokenizer import numeric_value

    value = numeric_value(token_value)
    return str(int(value)) if value == int(value) else f"{value:g}"


def _is_ambiguous(only_a: set[str], only_b: set[str], technical_differences: list[str]) -> bool:
    """Marca como ambiguo quando ha termos exclusivos de um lado sem
    contrapartida clara do outro (nem iguais, nem incompativeis
    conhecidos) — situacao que exige revisao humana."""
    has_unmatched_terms = bool(only_a) or bool(only_b)
    has_incompatible = any("incompativeis" in diff for diff in technical_differences)
    return has_unmatched_terms and not has_incompatible
