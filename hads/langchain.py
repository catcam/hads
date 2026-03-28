from __future__ import annotations

"""LangChain integration for loading HADS documents as Documents."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from hads.parser import parse_file

if TYPE_CHECKING:
    from langchain_core.documents import Document


_LANGCHAIN_IMPORT_ERROR: ImportError | None = None

try:
    from langchain_core.document_loaders import BaseLoader
    from langchain_core.documents import Document
except ImportError as exc:  # pragma: no cover - exercised in environments without LangChain
    _LANGCHAIN_IMPORT_ERROR = exc
    BaseLoader = object  # type: ignore[assignment,misc]
    Document = Any  # type: ignore[assignment,misc]


def _require_langchain() -> None:
    """Raise a helpful error when langchain-core is unavailable."""

    if _LANGCHAIN_IMPORT_ERROR is not None:
        raise ImportError(
            "HADSLoader requires langchain-core. Install it with "
            "`pip install langchain-core`."
        ) from _LANGCHAIN_IMPORT_ERROR


def _normalize_block_type(block_type: str) -> str:
    """Normalize user-supplied block types to parser-compatible values."""

    value = block_type.strip().upper()
    aliases = {
        "SPEC": "SPEC",
        "[SPEC]": "SPEC",
        "NOTE": "NOTE",
        "[NOTE]": "NOTE",
        "BUG": "BUG",
        "[BUG]": "BUG",
        "QUESTION": "QUESTION",
        "?": "QUESTION",
        "[?]": "QUESTION",
    }
    try:
        return aliases[value]
    except KeyError as exc:
        raise ValueError(f"unknown HADS block type: {block_type}") from exc


def _normalize_block_types(block_types: list[str] | None) -> set[str] | None:
    """Normalize a block-type filter when one is provided."""

    if block_types is None:
        return None
    return {_normalize_block_type(block_type) for block_type in block_types}


class HADSLoader(BaseLoader):
    """Load each HADS block as a LangChain Document."""

    def __init__(self, file_path: str, block_types: list[str] | None = None) -> None:
        self.file_path = file_path
        self.block_types = _normalize_block_types(block_types)

    def lazy_load(self) -> Iterator[Document]:
        """Yield one LangChain Document per parsed HADS block."""

        _require_langchain()
        hads_doc = parse_file(self.file_path)

        for block in hads_doc.blocks:
            if self.block_types is not None and block.type not in self.block_types:
                continue

            yield Document(
                page_content=block.content,
                metadata={
                    "source": self.file_path,
                    "block_type": block.type,
                    "section": block.section,
                    "hads_version": hads_doc.version,
                    "document_name": hads_doc.name,
                    "line_start": block.line_start,
                    "line_end": block.line_end,
                },
            )

    def load(self) -> list[Document]:
        """Return all HADS blocks as LangChain Documents."""

        return list(self.lazy_load())


def load_hads(path: str, block_types: list[str] | None = None) -> list[Document]:
    """Convenience wrapper around HADSLoader.load()."""

    return HADSLoader(path, block_types=block_types).load()
