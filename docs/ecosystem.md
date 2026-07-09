# Ecosystem

Tools and integrations built on the HADS standard.

---

## hads-skills

**Repository:** [github.com/catcam/hads-skills](https://github.com/catcam/hads-skills)

A universal skill that converts any technical document to HADS format. Works in Claude Code, Cursor, any system prompt, or as a zero-setup paste.

**What it does:**
- Takes any existing Markdown, README, or API doc
- Extracts facts into `[SPEC]` blocks
- Moves narrative to `[NOTE]`
- Surfaces known issues as `[BUG]`
- Adds required header and AI manifest
- Produces a valid HADS document

**Installation (Claude Code):**

```bash
claude mcp add hads-skills
```

**Zero-setup (any AI):** copy the skill content from the repo and paste into your system prompt. No installation required.

---

## LangChain HADSLoader {#langchain}

**PR:** [langchain-ai/langchain-community #593](https://github.com/langchain-ai/langchain-community/pull/593)

A LangChain document loader that parses HADS documents and filters by block type. Load only `[SPEC]` and `[BUG]` blocks into your RAG pipeline — skip the narrative that inflates token counts.

**Usage:**

```python
from langchain_community.document_loaders import HADSLoader

# Load only authoritative facts (SPEC + BUG)
loader = HADSLoader("api-reference.md", block_types=["SPEC", "BUG"])
docs = loader.load()

# Load everything
loader = HADSLoader("api-reference.md")
docs = loader.load()

# Filter by multiple types
loader = HADSLoader("api-reference.md", block_types=["SPEC", "NOTE"])
docs = loader.load()
```

**Token reduction:** ~70% compared to loading the full document. Facts and failure modes only.

**Metadata per document chunk:**

```python
{
    "source": "api-reference.md",
    "block_type": "SPEC",
    "section": "Authentication",
    "hads_version": "1.0.0"
}
```

---

## validate.py

**Source:** [github.com/catcam/hads/blob/main/validate.py](https://github.com/catcam/hads/blob/main/validate.py)

CLI validator for HADS documents. No dependencies — stdlib only.

```bash
# Single file
python validate.py your-doc.md

# Multiple files / glob
python validate.py docs/*.md

# Exit code: 0 = valid, 1 = invalid (useful in CI)
python validate.py api-reference.md && echo "OK"
```

See [Validation](spec/validation.md) for full details.

---

## Related work

**Different problem, same instinct.** These tools aren't built on HADS, but they attack the same token-waste problem from a different angle.

### greppy — structured context for code, not docs

**Repository:** [github.com/metric-space-ai/greppy](https://github.com/metric-space-ai/greppy)

HADS structures human-written documentation. greppy structures source code itself: instead of loading full files into an agent's context, it uses local tree-sitter indexing to extract only the relevant symbol blocks, parameters, docstrings, and callers, then writes that as a compact Markdown sidecar on demand. Reported ~2.3x lower token overhead and ~4x fewer rounds across 35 code-navigation tasks compared to loading or grepping full files.

Worth pairing: HADS for the docs an agent reads, greppy-style AST extraction for the code it navigates. Same principle — structured Markdown instead of raw text — applied to two different inputs.

---

## Add your tool

Built something on HADS? Open an issue or PR at [catcam/hads](https://github.com/catcam/hads) to get listed here.

Useful things to build:
- Validators in other languages (Go, Rust, TypeScript)
- Editor plugins (VS Code syntax highlighting for block tags)
- LlamaIndex reader (port of the LangChain loader)
- Pandoc filter for converting HADS to other formats
- GitHub Action for validating HADS docs in CI
