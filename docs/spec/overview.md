# Specification — Overview

**HADS Version 1.0.0** · Open Standard

The formal HADS specification. Read this to understand every rule. See [SPEC.md](https://github.com/catcam/hads/blob/main/SPEC.md) in the repo for the raw source.

---

## What HADS is

HADS is a tagging convention for Markdown technical documentation. It defines:

- Four semantic block types tagged with `[SPEC]`, `[NOTE]`, `[BUG]`, `[?]`
- A required AI manifest that tells models what to read and skip
- A document structure (H1 title, version, manifest, numbered sections)

**What HADS is not:**

- A new file format — every HADS document is valid `.md`
- A build tool or parser — no tooling required
- A replacement for existing documentation systems — it sits on top of them

---

## Design principles

**1. Convention over syntax.** Adding a new block type should not require updating a parser. HADS block tags are bold Markdown — `**[SPEC]**` — recognized by pattern, not grammar.

**2. Zero adoption friction.** Any existing Markdown document can be converted to HADS by adding block tags and a manifest. Nothing breaks. Nothing needs to be installed.

**3. Explicit over implicit.** The AI manifest tells the model exactly what to read. Guessing from structure is fragile; explicit instruction is reliable across model sizes and versions.

**4. Humans and AI share the same document.** HADS does not create separate "AI context files." The same file serves both audiences. This prevents the inevitable drift between documentation and AI context.

---

## Token efficiency rationale

A standard technical document mixes three types of content:

| Content type | Example | AI value |
|-------------|---------|----------|
| Facts | "Header: `Authorization: Bearer <token>`" | High |
| Narrative | "We switched from session auth in 2022 because..." | Low |
| Failure knowledge | "After password change, all tokens are silently invalidated" | Critical |

An AI reading a HADS document can skip all narrative content and focus only on `[SPEC]` and `[BUG]` blocks. For a typical 2000-word technical document, this reduces token consumption by 50–70% with no loss of factual accuracy.

---

## Sections of the spec

| Section | Content |
|---------|---------|
| [Block Types](block-types.md) | Full rules for SPEC, NOTE, BUG, ? blocks |
| [Document Structure](structure.md) | Header, manifest, section organization |
| [Validation](validation.md) | What makes a document valid, how to check |
