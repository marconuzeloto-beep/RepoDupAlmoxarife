"""Geracao de candidatos para comparacao profunda (Sprint 5).

Combina indice invertido + indice de assinaturas para localizar pares
plausiveis sem comparar todos-contra-todos. Retorna pares (i, j) com
i < j, ja deduplicados.

Os dois indices aplicam um limite de frequencia (ver InvertedIndex e
SignatureIndex) para evitar explosao combinatoria quando um termo ou
assinatura e compartilhado por muitos materiais nao relacionados. Isso
tem um efeito colateral: um grupo de materiais praticamente IDENTICOS
tambem pode ultrapassar esse limite e ficar de fora — o pior cenario
possivel, ja que sao os duplicados mais obvios de todos. Por isso, um
terceiro agrupamento, por texto normalizado EXATO, roda sem limite de
frequencia (uma correspondencia exata nunca e um termo generico demais
para ser util). Para nao gerar C(k,2) pares num grupo gigantesco de
duplicados identicos, esse agrupamento gera apenas uma cadeia
(cada item com o seguinte), que ja e suficiente para que todos os
membros apareçam no resultado e sejam classificados como duplicados.
"""

from __future__ import annotations

from collections import defaultdict

from app.indexes.inverted_index import InvertedIndex
from app.indexes.signature_index import SignatureIndex
from app.models.parsed_material import ParsedMaterial
from app.models.technical_signature import TechnicalSignature


def generate_candidate_pairs(
    parsed_materials: list[ParsedMaterial],
    signatures: list[TechnicalSignature],
) -> list[tuple[int, int]]:
    """Gera pares candidatos (indices em ``parsed_materials``).

    Um par entra na lista se: compartilhar ao menos um termo tecnico
    indexado (inverted index) nao generico demais; OU tiver a mesma
    assinatura nao-ordenada/numerica (signature index) nao generica
    demais; OU tiver o mesmo texto normalizado exato (sempre, sem
    limite de frequencia).
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

    pairs.update(_exact_match_chain_pairs(parsed_materials))

    return sorted(pairs)


def _exact_match_chain_pairs(parsed_materials: list[ParsedMaterial]) -> set[tuple[int, int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for position, parsed in enumerate(parsed_materials):
        groups[parsed.normalized_text].append(position)

    chain_pairs: set[tuple[int, int]] = set()
    for positions in groups.values():
        if len(positions) < 2:
            continue
        for a, b in zip(positions, positions[1:]):
            chain_pairs.add((a, b))
    return chain_pairs
