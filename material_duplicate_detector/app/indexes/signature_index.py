"""Indice por assinatura tecnica — Hash Map (Sprint 5).

Agrupa materiais que compartilham exatamente a mesma assinatura
(ex.: mesma ``unordered_signature``), o caminho mais rapido para achar
fortes candidatos a duplicidade.
"""

from __future__ import annotations

from collections import defaultdict

from app.models.technical_signature import TechnicalSignature


class SignatureIndex:
    def __init__(self) -> None:
        self._by_unordered_signature: dict[frozenset[str], set[int]] = defaultdict(set)
        self._by_numeric_signature: dict[str, set[int]] = defaultdict(set)

    def build(self, signatures: list[TechnicalSignature]) -> None:
        for position, signature in enumerate(signatures):
            self._by_unordered_signature[signature.unordered_signature].add(position)
            if signature.numeric_signature:
                self._by_numeric_signature[signature.numeric_signature].add(position)

    def candidates_for(self, signature: TechnicalSignature, exclude_position: int) -> set[int]:
        candidates = set(self._by_unordered_signature.get(signature.unordered_signature, set()))
        if signature.numeric_signature:
            candidates |= self._by_numeric_signature.get(signature.numeric_signature, set())
        candidates.discard(exclude_position)
        return candidates
