#!/usr/bin/env python3
"""Benchmark HADS token reduction on example documents."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hads.parser import parse, to_markdown

try:
    import tiktoken
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "tiktoken is required to run this benchmark. Install it with "
        "`python3 -m pip install tiktoken`."
    ) from exc


SPEC = "SPEC"
BUG = "BUG"
ENCODING_NAME = "cl100k_base"
RESULTS_PATH = REPO_ROOT / "benchmarks" / "results.json"
EXAMPLE_DIR_CANDIDATES = (
    REPO_ROOT / "examples",
    REPO_ROOT / "docs" / "examples",
)
EXCLUDED_FILENAMES = {"index.md"}


@dataclass(slots=True)
class DocumentBenchmark:
    """Token benchmark results for one HADS document."""

    document: str
    path: str
    title: str
    full_tokens: int
    spec_bug_tokens: int
    spec_only_tokens: int
    reduction_spec_bug: float
    reduction_spec_only: float


def discover_example_documents() -> list[Path]:
    """Return Markdown example documents, preferring the canonical examples directory."""

    for candidate_dir in EXAMPLE_DIR_CANDIDATES:
        if not candidate_dir.is_dir():
            continue
        documents = sorted(
            path
            for path in candidate_dir.glob("*.md")
            if path.name not in EXCLUDED_FILENAMES
        )
        if documents:
            return documents

    searched = ", ".join(str(path.relative_to(REPO_ROOT)) for path in EXAMPLE_DIR_CANDIDATES)
    raise FileNotFoundError(f"could not find example HADS documents in: {searched}")


def count_tokens(text: str, encoding: tiktoken.Encoding) -> int:
    """Count tokens using cl100k_base."""

    return len(encoding.encode(text))


def benchmark_document(path: Path, encoding: tiktoken.Encoding) -> DocumentBenchmark:
    """Benchmark token counts for one HADS document."""

    source_text = path.read_text(encoding="utf-8")
    document = parse(source_text)

    full_tokens = count_tokens(source_text, encoding)
    spec_bug_markdown = to_markdown(document, include_types=[SPEC, BUG])
    spec_only_markdown = to_markdown(document, include_types=[SPEC])
    spec_bug_tokens = count_tokens(spec_bug_markdown, encoding)
    spec_only_tokens = count_tokens(spec_only_markdown, encoding)

    return DocumentBenchmark(
        document=path.name,
        path=str(path.relative_to(REPO_ROOT)),
        title=document.name,
        full_tokens=full_tokens,
        spec_bug_tokens=spec_bug_tokens,
        spec_only_tokens=spec_only_tokens,
        reduction_spec_bug=1 - (spec_bug_tokens / full_tokens),
        reduction_spec_only=1 - (spec_only_tokens / full_tokens),
    )


def format_percent(value: float) -> str:
    """Format a decimal reduction as a percentage."""

    return f"{value * 100:6.2f}%"


def print_table(results: list[DocumentBenchmark]) -> None:
    """Print a benchmark table and summary rows."""

    headers = (
        "document",
        "full",
        "spec+bug",
        "spec_only",
        "reduction spec+bug",
        "reduction spec_only",
    )
    rows = [
        (
            result.document,
            str(result.full_tokens),
            str(result.spec_bug_tokens),
            str(result.spec_only_tokens),
            format_percent(result.reduction_spec_bug),
            format_percent(result.reduction_spec_only),
        )
        for result in results
    ]

    avg_reduction_spec_bug = sum(result.reduction_spec_bug for result in results) / len(results)
    avg_reduction_spec_only = sum(result.reduction_spec_only for result in results) / len(results)
    rows.append(
        (
            "AVERAGE REDUCTION",
            "-",
            "-",
            "-",
            format_percent(avg_reduction_spec_bug),
            format_percent(avg_reduction_spec_only),
        )
    )

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    separator = "-+-".join("-" * width for width in widths)
    print(" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print(separator)
    for row in rows:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))

    print()
    print(
        "Average reduction across all example documents: "
        f"{avg_reduction_spec_bug * 100:.2f}% for SPEC+BUG, "
        f"{avg_reduction_spec_only * 100:.2f}% for SPEC only."
    )
    if avg_reduction_spec_only >= 0.70:
        print(
            "The example corpus supports the paper's ~70% token reduction claim "
            "for SPEC-only extraction."
        )
    else:
        print(
            "The example corpus does not reach the paper's ~70% token reduction "
            f"claim for SPEC-only extraction; the measured average is "
            f"{avg_reduction_spec_only * 100:.2f}%."
        )


def write_results(results: list[DocumentBenchmark]) -> dict[str, object]:
    """Persist benchmark results to benchmarks/results.json."""

    avg_reduction_spec_bug = sum(result.reduction_spec_bug for result in results) / len(results)
    avg_reduction_spec_only = sum(result.reduction_spec_only for result in results) / len(results)
    payload: dict[str, object] = {
        "encoding": ENCODING_NAME,
        "source_directory": next(
            str(path.relative_to(REPO_ROOT))
            for path in EXAMPLE_DIR_CANDIDATES
            if path.is_dir() and any(
                child.suffix == ".md" and child.name not in EXCLUDED_FILENAMES for child in path.iterdir()
            )
        ),
        "documents": [asdict(result) for result in results],
        "summary": {
            "document_count": len(results),
            "average_reduction_spec_bug": avg_reduction_spec_bug,
            "average_reduction_spec_only": avg_reduction_spec_only,
            "paper_claim_reduction": 0.70,
            "paper_claim_verified": avg_reduction_spec_only >= 0.70,
        },
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def run_benchmark() -> dict[str, object]:
    """Run the benchmark across all example HADS documents."""

    example_paths = discover_example_documents()
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    results = [benchmark_document(path, encoding) for path in example_paths]
    print_table(results)
    return write_results(results)


def main() -> int:
    """CLI entry point."""

    try:
        run_benchmark()
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"Benchmark failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
