"""Modelo bruto do material lido diretamente da planilha (Sprint 2)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Material:
    """Representa uma linha da planilha, sem nenhuma transformacao.

    O texto original (``analysis_text``) nunca deve ser alterado em
    nenhum ponto do pipeline; ele existe para auditoria e para ser
    exibido ao usuario final.
    """

    row_index: int
    code: str
    analysis_text: str
    raw_fields: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.row_index < 0:
            raise ValueError("row_index nao pode ser negativo")
