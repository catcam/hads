# NLnet Grant Readiness Assessment — HADS
**Date:** 2026-03-19
**Deadline:** 2026-04-01 (12 days remaining)

---

## Executive Summary

The repository contains a well-written **specification and documentation site** but is missing the three deliverables the grant requires as working code. The validator (`validate.py`) is a structural checker, not a parser. There is no AI framework integration code in the repo. There are no automated benchmarks. All three must be built.

---

## Requirement 1: Parser that extracts [SPEC]/[NOTE]/[BUG]/[?] blocks

### What exists

| File | What it does | What it does NOT do |
|------|-------------|---------------------|
| `validate.py` | Regex-checks for H1, version, manifest, bold tags, [BUG] fields, loose tags | Does not return parsed blocks; no AST; no structured output; no `parse()` API |

Key functions in `validate.py`:
- `find_h1()`, `find_version()`, `find_manifest()` — locate structural elements (return line index or None)
- `find_bug_blocks()` — finds [BUG] blocks and collects their content lines, but only for validation, not extraction
- `check_loose_tags()` — detects malformatted tags
- `validate()` — orchestrates checks, prints pass/fail, returns exit code

**Critical gap:** There is no function that parses a HADS document into structured data. `find_bug_blocks()` comes closest but only handles [BUG], returns raw line lists, and doesn't track the parent section.

### What must be built

A `hads/parser.py` module (or similar) that:

1. **`parse(text_or_path) -> HADSDocument`** — parses a full HADS document into a structured object
2. **`HADSDocument`** dataclass with:
   - `title: str`
   - `version: str`
   - `manifest: str`
   - `blocks: list[HADSBlock]`
3. **`HADSBlock`** dataclass with:
   - `block_type: Literal["SPEC", "NOTE", "BUG", "?"]`
   - `content: str`
   - `section: str` (parent H2/H3 heading)
   - `title: str | None` (for titled blocks like `**[BUG] Token fails**`)
   - `line_start: int`
   - `line_end: int`
4. **`filter_blocks(doc, block_types)`** — returns subset of blocks by type
5. **`to_markdown(blocks)`** — reconstructs filtered Markdown from selected blocks

**Estimated scope:** ~200-300 lines of Python. Can reuse regex constants from `validate.py`.

### Priority: **CRITICAL — build first (days 1-3)**

---

## Requirement 2: Integration with at least one AI framework

### What exists

| Location | Status |
|----------|--------|
| `docs/ecosystem.md` lines 31-68 | Documents a "LangChain HADSLoader" with code examples |
| langchain-community PR #593 | Referenced but external; code is not in this repo |

The ecosystem docs describe the API surface (`HADSLoader`, `block_types` parameter, metadata schema) but the implementation is entirely absent from this repository.

### What must be built

A `hads/langchain.py` (or `integrations/langchain_loader.py`) implementing:

1. **`HADSLoader(BaseLoader)`** — LangChain document loader
   - Constructor: `HADSLoader(file_path, block_types=None, encoding="utf-8")`
   - `.load() -> list[Document]` — returns LangChain `Document` objects
   - `.lazy_load() -> Iterator[Document]` — streaming variant
   - Each `Document.page_content` = block content
   - Each `Document.metadata` = `{source, block_type, section, hads_version}`
2. Depends on: Requirement 1 (the parser)
3. Should work with `langchain-core` (avoid heavy `langchain` dependency)

Optional but impressive for the grant:
- A simple RAG demo script showing: load HADS doc → embed SPEC blocks → query → answer
- A LlamaIndex reader (port of the same loader)

**Estimated scope:** ~100-150 lines for the loader, ~50 lines for a demo script.

### Priority: **CRITICAL — build second (days 3-5)**

---

## Requirement 3: Benchmark showing token reduction

### What exists

| Location | Content | Automated? |
|----------|---------|------------|
| `paper.md` lines 86-114 | "5,000 → 1,500 tokens, ~70%" | No — prose estimate |
| `case-studies/polymarket-bot.md` | "12,500 tokens → 6,475 (48%)" | No — manual count |
| `README.md` lines 62-66 | "~4,200 → ~1,100 (74%)" | No — table only |
| `docs/ecosystem.md` line 55 | "~70% reduction" | No — claim only |

**There is zero token-counting code anywhere in the repo.** All numbers are manual estimates or back-of-envelope calculations.

### What must be built

A `benchmarks/` directory with:

1. **`benchmarks/token_benchmark.py`** — automated benchmark script
   - Uses `tiktoken` (GPT-4 tokenizer) or similar for reproducible counts
   - For each example doc (`api-reference.md`, `file-format.md`, `configuration.md`):
     - Count tokens in full document
     - Parse with HADS parser
     - Count tokens in SPEC-only subset
     - Count tokens in SPEC+BUG subset
     - Calculate and report reduction percentage
   - Output: table (stdout + CSV/JSON) with per-document and aggregate results
   - Include wall-clock parse time

2. **`benchmarks/results/`** — committed benchmark output for the grant submission

3. Optional: comparison against naive chunking (RAG baseline)

**Estimated scope:** ~150 lines for the benchmark script.

### Priority: **CRITICAL — build third (days 5-7)**

---

## What else exists (assets, not gaps)

These are strong and do NOT need rework:

| Asset | Status | Notes |
|-------|--------|-------|
| `SPEC.md` | Complete | Well-written formal spec, 304 lines |
| `README.md` | Complete | Clear motivation, examples, Fermi estimates |
| `paper.md` | Complete | Position paper with DOI |
| `api-reference.md` | Complete | Good example doc for benchmarks |
| `file-format.md` | Complete | Good example doc for benchmarks |
| `configuration.md` | Complete | Good example doc for benchmarks |
| `case-studies/polymarket-bot.md` | Complete | Real-world case study |
| MkDocs site (`docs/`) | Complete | GitHub Pages deployment working |
| `SKILL.md` | Complete | Claude skill definition |
| `.github/workflows/docs.yml` | Working | Auto-deploys docs |

---

## Recommended 12-Day Plan

### Days 1-3: Parser (`hads/parser.py`)
- Create Python package structure (`hads/__init__.py`, `hads/parser.py`)
- Implement `parse()`, `HADSDocument`, `HADSBlock` dataclasses
- Implement `filter_blocks()` and `to_markdown()`
- Write tests (`tests/test_parser.py`) against the 3 example docs
- Refactor `validate.py` to use the parser internally

### Days 4-5: LangChain Integration (`hads/langchain.py`)
- Implement `HADSLoader(BaseLoader)` with `load()` and `lazy_load()`
- Write tests (`tests/test_langchain.py`)
- Create a minimal RAG demo script (`examples/rag_demo.py`)

### Days 6-7: Benchmark (`benchmarks/token_benchmark.py`)
- Install `tiktoken`, write benchmark script
- Run against all 3 example docs + case study
- Generate results table, commit output
- Verify numbers match (or correct) the claims in paper.md and README

### Days 8-9: Polish and Package
- Add `pyproject.toml` with proper metadata and dependencies
- Add `pip install hads` support
- Update `README.md` with installation and API usage
- Add CI workflow for tests (`pytest`) and validation
- Ensure `validate.py` still works standalone

### Days 10-11: Documentation and Demo
- Update `docs/ecosystem.md` with actual working code examples
- Add a "Getting Started with the Python Library" page
- Record a short demo or add screenshots
- Update paper.md if benchmark numbers differ from estimates

### Day 12: Buffer
- Final review, edge case fixes, grant submission prep

---

## Files to Create

```
hads/
├── hads/
│   ├── __init__.py          # Package exports
│   ├── parser.py            # Core parser (Requirement 1)
│   ├── langchain.py         # LangChain loader (Requirement 2)
│   └── models.py            # HADSDocument, HADSBlock dataclasses
├── tests/
│   ├── test_parser.py       # Parser tests
│   ├── test_langchain.py    # LangChain integration tests
│   └── test_validate.py     # Existing validator tests
├── benchmarks/
│   ├── token_benchmark.py   # Benchmark script (Requirement 3)
│   └── results/             # Committed benchmark output
├── examples/
│   └── rag_demo.py          # RAG demo with LangChain
└── pyproject.toml           # Package metadata
```

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Parser edge cases (nested code blocks, front matter, etc.) | Medium | Test against all 3 examples + SPEC.md itself |
| LangChain API changes | Low | Depend on `langchain-core` only, pin version |
| Benchmark numbers don't match paper claims | Medium | Update paper.md if needed; actual data is better than estimates |
| Not enough time for polish | Low | Parser + LangChain + Benchmark are the hard requirements; packaging is nice-to-have |

---

*This assessment was generated by reviewing every file in the repository. The three grant requirements map to three code deliverables that do not currently exist.*
