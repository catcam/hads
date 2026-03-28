# HADS — Human-AI Document Standard

**Version 1.0.0** · MIT License · Open Standard

📖 **[Read the article on Medium](https://medium.com/@catcam_46604/ai-is-now-the-primary-reader-of-your-docs-nobody-told-your-docs-5f7103ea3281)** — *AI Is Now the Primary Reader of Your Docs. Nobody Told Your Docs.*
📚 **[Full documentation](https://catcam.github.io/hads/)** — specification, writing guide, examples, ecosystem
📄 **[Position paper](https://doi.org/10.5281/zenodo.19019719)** — DOI: 10.5281/zenodo.19019719
👤 **Author**: Nikša Barlović — [ORCID: 0009-0004-7421-0913](https://orcid.org/0009-0004-7421-0913)

---

## What is HADS?

HADS is a lightweight convention for writing technical documentation that works equally well for humans and AI language models — with AI as the primary consumer.

It is not a new file format. It is a set of tagging and structural rules applied to standard Markdown. Any editor renders it. Any AI reads it. No tooling required.

---

## Why does this exist?

Technical documentation is increasingly read by AI models before humans ever see it. Models are used to look up APIs, understand file formats, debug errors, generate code. But documentation is written for humans — verbose, contextual, narrative.

This creates waste:
- AI consumes thousands of tokens to extract a handful of facts
- Smaller / local models lose context and hallucinate
- Humans still need the context that AI wants to skip

HADS solves this by separating signal from context — in the same document, without duplication.

---

## Core idea

Every block in a HADS document is tagged with its intended reader:

| Tag | Meaning | Primary reader |
|-----|---------|----------------|
| `[SPEC]` | Machine-readable fact. Terse. Authoritative. | AI |
| `[NOTE]` | Human context — why, history, caveats, examples | Human |
| `[BUG]` | Verified failure mode + fix. Always authoritative. | Both |
| `[?]` | Unverified / inferred. Treat as hypothesis. | Both |

AI instruction at the top of every HADS document tells the model what to read and what to skip. This is the key innovation: **the document teaches the model how to read it.**

---

## Who benefits?

- **Small / local models** — can extract facts without reading everything
- **Large models** — spend fewer tokens, reduce hallucination risk
- **Developers** — write once, serves both audiences
- **Teams** — single source of truth, no separate "AI context" files
- **Open source projects** — documentation that AI coding assistants actually use correctly

---

## Before → After

Same document. AI loads only what it needs.

| | Full document | `[SPEC]` only |
|--|--|--|
| Tokens loaded | ~4,200 | ~1,100–2,750 |
| Reduction | — | **34–55% (measured, avg 44%)** |
| Information lost | — | **none** (facts intact) |

The rest stays in the file for humans. One source. No duplication.

*Measured on real documents using the [benchmark script](benchmark.py). Results vary by document type — API references and config docs reduce more, narrative docs less.*

---

## Quick example

```markdown
## Authentication

**[SPEC]**
- Method: Bearer token
- Header: `Authorization: Bearer <token>`
- Token expiry: 3600 seconds
- Refresh endpoint: `POST /auth/refresh`

**[NOTE]**
Tokens were originally session-based (pre-v2.0). If you see legacy docs
mentioning cookie auth, ignore them. The switch happened in 2022 when the
API went public. Refresh tokens do not expire but can be revoked.

**[BUG] Token silently rejected after password change**
Cause: All tokens invalidated on password change, no error returned.
Symptom: 401 with body `{"error": "invalid_token"}` — identical to expired token.
Fix: Re-authenticate and store new token. Check for 401 after any account operation.
```

An AI reading this extracts: method, header format, expiry, refresh endpoint — in one `[SPEC]` block. A human reads the `[NOTE]` and understands history and context. Both read the `[BUG]`.

---

## Repository structure

```
hads/
├── README.md          — this file
├── SPEC.md            — full formal specification
├── benchmark.py       — measures token reduction and accuracy per document
├── case-studies/
│   └── polymarket-bot.md     — production AI agent codebase (48% token reduction)
├── examples/
│   ├── api-reference.md      — REST API documentation example
│   ├── file-format.md        — binary file format example
│   └── configuration.md     — configuration system example
├── validator/
│   └── validate.py    — validates a Markdown file against HADS spec
└── LICENSE
```

---

## Case studies

Real-world measurements of HADS applied to production codebases:

- **[Polymarket trading bot](case-studies/polymarket-bot.md)** — 705-line `CLAUDE.md` for an autonomous trading agent. 48% of context was version history loaded on every session. Tagging saves ~39% per typical session.

---

## Getting started

1. Read [SPEC.md](SPEC.md) — the full standard (15 min)
2. Look at [examples/](examples/) — real documents in HADS format
3. Run the validator on your own docs: `python validator/validate.py your-doc.md`

---

## Why it matters at scale

A Fermi estimate of what HADS adoption would mean globally:

**Assumptions:**
- ~1 billion AI queries/day touching technical docs (50M developers × 10 queries/day + enterprise agents, CI/CD pipelines, support bots)
- Conservative: HADS reduces tokens read per query by 44% on average (measured across document types)
- Energy cost: ~0.003 Wh per 1,000 tokens (GPT-4 class inference)
- Time saved: ~1 min/query from more precise first answers and fewer follow-ups

**Annual savings at full adoption (conservative estimate):**

| Metric | Value |
|--------|-------|
| Tokens saved/day | ~2.2 trillion |
| Electricity saved/year | **~2.4 TWh** (~14% of Croatia's annual grid consumption) |
| Developer time saved/year | **~6 billion hours** |
| Economic value (@ $50/hr) | **~$300 billion/year** |

At 10% adoption these numbers drop proportionally — still ~$30B/year in recovered productivity.

*These are Fermi estimates, not projections. The 44% reduction is measured; query volume and time savings are estimated. The point: structuring documentation for AI consumption is economically material at scale, even at conservative assumptions.*

---

## Ecosystem

**[hads-skills](https://github.com/catcam/hads-skills)** — AI skills for converting documents to HADS format. Works with Claude Code, any model via system prompt, or zero-setup paste-and-run.

---

## Contributing

HADS is an open standard. Contributions welcome:
- New block types (open an issue first)
- Additional examples
- Validator improvements
- Ports of the validator to other languages

Please read SPEC.md before contributing — especially the design principles section.

---

## License

MIT. Use freely, commercially or otherwise. Attribution appreciated but not required.

---

*HADS exists because documentation should serve everyone who reads it — human or machine.*