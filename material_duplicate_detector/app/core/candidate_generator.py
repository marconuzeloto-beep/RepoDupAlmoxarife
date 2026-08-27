"""Geracao de candidatos para comparacao profunda (Sprint 5).

Combina indice invertido + indice de assinaturas para localizar pares
plausiveis sem comparar todos-contra-todos. Retorna pares (i, j) com
i < j, ja deduplicados.
"""

from __future__ import annotations

from app.indexes.inverted_index import InvertedIndex
from app.indexes.signature_index import SignatureIndex
from app.models.parsed_material import ParsedMaterial
from app.models.technical_signature import TechnicalSignature


def generate_candidate_pairs(
    parsed_materials: list[ParsedMaterial],
    signatures: list[TechnicalSignature],
) -> list[tuple[int, int]]:
    """Gera pares candidatos (indices em ``parsed_materials``).

    Um par so entra na lista se compartilhar ao menos um termo tecnico
    indexado (inverted index) OU tiver a mesma assinatura nao-ordenada
    ou numerica (signature index).
    """
    if len(parsed_materials) != len(signatures):
        raise ValueError("parsed_materials e signatures devem ter o mesmo tamanho")

    inverted_index = InvertedIndex()
    inverted_index.build(parsed_materials)

    signature_index = SignatureIndex()
    signature_index.build(signatures)

    pairs: set[tuple[int, int]] = set()
    for position, (parsed, signature) in enumerate(zip(parsed_materials, signatures)):
        candidates = inverted_index.candidates_for(parsed, position)
        candidates |= signature_index.candidates_for(signature, position)
        for other in candidates:
            pair = (position, other) if position < other else (other, position)
            pairs.add(pair)

    return sorted(pairs)
