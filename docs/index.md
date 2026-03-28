# HADS — Human-AI Document Standard

**Version 1.0.0** · MIT License · Open Standard

---

> Documentation is increasingly read by AI models before humans ever see it.
> HADS is a convention that makes Markdown work for both audiences — at the same time.

---

## What is HADS?

HADS is a lightweight tagging convention for technical documentation written in Markdown.

It adds four semantic block types — `[SPEC]`, `[NOTE]`, `[BUG]`, `[?]` — and an **AI manifest** at the top of every document. The manifest tells AI models exactly what to read and what to skip. This is the core innovation.

HADS is **not** a new file format. Every HADS document is valid, standard Markdown. It renders correctly in GitHub, VS Code, Obsidian, Notion — anywhere. No tooling required to write or read it.

---

## The four block types

| Tag | Meaning | Who reads it |
|-----|---------|--------------|
| `**[SPEC]**` | Authoritative fact. Terse. Bullet lists, tables, code. | AI (always) |
| `**[NOTE]**` | Human context — history, why, caveats, examples. | Human (skip if time-limited) |
| `**[BUG]**` | Verified failure + fix. Symptom, cause, fix always present. | Both (always) |
| `**[?]**` | Unverified / inferred. Treat as hypothesis. | Both (with caution) |

---

## Why it works

An AI model reading a HADS document knows:

1. The manifest tells it which blocks are authoritative
2. `[SPEC]` blocks contain only machine-readable facts — no filler
3. `[BUG]` blocks contain hard-won knowledge it should never skip
4. `[NOTE]` blocks are safe to skip under token pressure

The result: **smaller models extract correct facts**, larger models waste fewer tokens, and human readers still get the narrative context they need.

---

## Quick example

```markdown
# Zephyr API

**Version 2.1.0** · Fictionware Inc. · 2026 · HADS 1.0.0

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.

---

## Authentication

**[SPEC]**
- Method: Bearer token
- Header: `Authorization: Bearer <token>`
- Token expiry: 3600 seconds
- Refresh endpoint: `POST /auth/refresh`

**[NOTE]**
Tokens were originally session-based (pre-v2.0). If you see legacy docs
mentioning cookie auth, ignore them. The switch happened in 2022.

**[BUG] Token silently rejected after password change**
Symptom: 401 with body `{"error": "invalid_token"}` — identical to expired token.
Cause: All tokens invalidated on password change, no error returned.
Fix: Re-authenticate and store new token. Check for 401 after any account operation.
```

---

## Get started

<div class="grid cards" markdown>

- :material-rocket-launch: **[Quickstart](quickstart.md)**
  Write your first HADS document in 5 minutes

- :material-book-open: **[Specification](spec/overview.md)**
  Full formal spec with all rules and edge cases

- :material-pencil: **[Writing Guide](writing.md)**
  Practical patterns for writing and converting docs

- :material-flask: **[Examples](examples/index.md)**
  Real HADS documents — API reference, config, file formats

</div>

---

## Ecosystem

| Tool | What it does |
|------|-------------|
| [hads-skills](https://github.com/catcam/hads-skills) | Universal skill — converts any doc to HADS in Claude Code, Cursor, system prompt |
| [LangChain HADSLoader](ecosystem.md#langchain) | Document loader that filters by block type. 34–55% token reduction vs full load (measured) |
| [validate.py](spec/validation.md) | CLI validator — checks any Markdown file for HADS compliance |

---

*HADS exists because documentation should serve everyone who reads it — human or machine.*
