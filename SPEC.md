# HADS Specification
**Version 1.0.0** · Human-AI Document Standard · Open Standard · 2026

---

## AI READING INSTRUCTION

This document is written in HADS format. Read `[SPEC]` and `[BUG]` blocks for authoritative facts. Read `[NOTE]` blocks only if additional context is needed. `[?]` blocks are hypotheses — treat with lower confidence.

---

## 1. OVERVIEW

**[SPEC]**
- HADS is a tagging convention for Markdown technical documentation
- File extension: `.md` (standard Markdown — no new extension)
- AI manifest required at top of every HADS document
- Four block types: `[SPEC]`, `[NOTE]`, `[BUG]`, `[?]`
- Block tags are bold, on their own line, immediately before content
- A HADS document is valid Markdown — renders correctly without any tooling

**[NOTE]**
HADS does not invent a new format. The decision to use Markdown was deliberate: zero adoption friction. Any editor, any renderer, any AI context window already handles Markdown. HADS adds meaning through convention, not syntax.

---

## 2. DOCUMENT STRUCTURE

**[SPEC]**
A valid HADS document has three required parts, in order:

```
1. Header block       — title, version, metadata
2. AI manifest        — reading instruction for AI models
3. Content sections   — tagged blocks organized by topic
```

### 2.1 Header block

**[SPEC]**
```markdown
# Document Title
**Version N.N.N** · Author · Date · [additional metadata]
```

Required fields: title (H1), version. Optional: author, date, status, license.

### 2.2 AI manifest

**[SPEC]**
The AI manifest is a plain paragraph immediately after the header. It must:
- Appear before any content sections
- Explicitly name which block types the AI should prioritize
- Explicitly name which block types the AI may skip

Minimal valid manifest:
```markdown
## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified — treat with lower confidence.
```

**[NOTE]**
The manifest is the core innovation of HADS. Without it, an AI model has no way to know which parts of a document are dense with facts versus human narrative. Even a three-sentence manifest measurably reduces token waste for models processing long documents.

The manifest can be extended. A document about a dangerous API might add: "Always read `[BUG]` blocks before generating any code." A tutorial might say: "Read `[NOTE]` blocks — they contain required conceptual background."

### 2.3 Content sections

**[SPEC]**
- Sections use H2 headings (`##`)
- Subsections use H3 (`###`)
- Each section contains one or more tagged blocks
- Untagged content is permitted but treated as `[NOTE]` by AI readers
- Section order: general to specific, required before optional

---

## 3. BLOCK TYPES

**[SPEC]**
Four block types. Each starts with a bold tag on its own line.

```
**[SPEC]**    Authoritative fact. Machine-readable. Terse.
**[NOTE]**    Human context. Narrative. History. Examples.
**[BUG]**     Verified failure mode + confirmed fix.
**[?]**       Unverified or inferred. Lower confidence.
```

A section may contain multiple blocks of different types. Order within a section: `[SPEC]` first, then `[NOTE]`, then `[BUG]`, then `[?]`.

### 3.1 [SPEC] block

**[SPEC]**
- Contains facts that are verified and authoritative
- Written in the most concise form possible
- Prefer: bullet lists, tables, code blocks, key-value pairs
- Avoid: narrative prose, historical context, subjective statements
- If a fact requires more than two sentences of prose, it belongs in `[NOTE]`

Good `[SPEC]`:
```markdown
**[SPEC]**
- Max payload size: 10 MB
- Accepted formats: JSON, MessagePack
- Timeout: 30 seconds (no retry on timeout)
- Rate limit: 1000 req/min per API key
```

Bad `[SPEC]` (too narrative):
```markdown
**[SPEC]**
The system was designed to accept payloads up to 10 MB, which was chosen
after extensive benchmarking in 2021. JSON is the primary format although
MessagePack is also supported for performance-sensitive use cases.
```

### 3.2 [NOTE] block

**[SPEC]**
- Contains context that aids human understanding
- May be verbose, narrative, historical
- AI readers may skip unless context is needed
- Common content: why a decision was made, migration notes, caveats, analogies, examples that illustrate rather than define

**[NOTE]**
`[NOTE]` blocks are where good documentation lives for human readers. They answer "why" not "what." A spec without notes is usable by machines but alienating for humans. A document with only notes wastes AI tokens. HADS keeps both.

### 3.3 [BUG] block

**[SPEC]**
- Documents a verified failure mode with a confirmed fix
- Required fields: symptom, cause, fix
- Optional: affected versions, workarounds
- Always read by both AI and human readers — never skip
- Title line format: `**[BUG] Short description of the bug**`

Template:
```markdown
**[BUG] Short description**
Symptom: What the user/system observes.
Cause: Root cause.
Fix: Exact remediation.
```

**[NOTE]**
`[BUG]` blocks are the most valuable content in technical documentation. They represent hard-won knowledge — someone hit this, debugged it, and wrote it down. HADS elevates them to first-class status so neither AI nor human readers skip them. An AI generating code from a HADS document should always read all `[BUG]` blocks first.

### 3.4 [?] block

**[SPEC]**
- Marks content that is inferred, untested, or uncertain
- AI readers should apply lower confidence to this content
- Human readers should verify before relying on it
- Format: inline in a list or as a paragraph, prefixed with `**[?]**`

```markdown
**[?]**
- Behavior on empty input — assumed to return 400, not verified.
- Thread safety of the connection pool — documentation is silent on this.
```

---

## 4. FORMATTING RULES

**[SPEC]**
- Block tags are always bold: `**[SPEC]**`, `**[NOTE]**`, `**[BUG]**`, `**[?]**`
- Tag is on its own line, immediately followed by content (no blank line between tag and content)
- Code examples use fenced code blocks with language hint where applicable
- Tables are permitted in any block type
- Inline code uses backticks
- No custom HTML — HADS must render in plain Markdown renderers

**[NOTE]**
The no-HTML rule keeps HADS portable. GitHub, GitLab, Obsidian, VS Code, AI context windows — all handle Markdown. None require HTML. Documents that embed HTML break in at least one of these environments.

---

## 5. VERSIONING

**[SPEC]**
- HADS version follows Semantic Versioning (semver.org)
- Document version is declared in the header block
- `**Version 1.0.0**` format required
- Breaking changes to block syntax = major version bump
- New block types = minor version bump
- Clarifications = patch version bump

**[?]**
- Per-section versioning (tracking when a section last changed) — useful but not yet in spec.
- Machine-readable version declaration (for validators) — under consideration for v1.1.

---

## 6. DESIGN PRINCIPLES

**[NOTE]**
These principles explain why HADS is the way it is. They are not rules — they are the reasoning behind the rules. If you are extending HADS or writing a HADS-compatible tool, read these.

**Principle 1: One document, two readers.**
The same file serves humans and AI. No separate "AI context" file. No duplication. If a fact changes, it changes in one place.

**Principle 2: AI reads first, humans read when needed.**
Most documentation interactions will be AI-mediated. A developer asks their coding assistant about an API — the assistant reads the docs. HADS optimizes for this case without sacrificing human readability.

**Principle 3: Small models matter.**
A standard that only works with frontier models is not a standard — it is a workaround. HADS must be usable by 7B parameter local models. This means the manifest must be explicit, the tags must be unambiguous, and the structure must not require reasoning to parse.

**Principle 4: Zero tooling to read.**
A HADS document must be useful without any HADS-specific tooling. The validator is helpful but optional. The format renders correctly in any Markdown viewer. An AI can follow the manifest without knowing what HADS is.

**Principle 5: Conventions over schemas.**
HADS does not define a schema. There is no parser, no AST, no required front matter. It is a convention. This makes adoption trivial and failure modes minimal.

---

## 7. VALIDATION

**[SPEC]**
A HADS document is valid if:
1. It begins with an H1 title
2. It contains a version declaration in the header
3. It contains an AI manifest before the first content section
4. All block tags are bold and on their own line
5. No block contains another block tag inside it (no nesting)
6. `[BUG]` blocks contain at minimum: symptom and fix

A validator script is provided at `validator/validate.py`.

**[SPEC] Validator exit codes**
```
0 — valid HADS document
1 — missing required element (title, version, manifest)
2 — malformed block tag
3 — [BUG] block missing required fields
```

---

## 8. EXAMPLE DOCUMENT SKELETON

**[SPEC]**
```markdown
# My System — Reference
**Version 1.0.0** · Author Name · 2026

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified.

---

## 1. Overview

**[SPEC]**
- What the system is, in one sentence
- Key constraints or requirements

**[NOTE]**
Why the system exists. Historical context if relevant.

---

## 2. Core Concept

**[SPEC]**
- Fact
- Fact
- Fact

**[NOTE]**
Human explanation.

**[BUG] Known issue title**
Symptom: ...
Cause: ...
Fix: ...

**[?]**
- Unverified behavior X
- Untested edge case Y
```

---

## 9. CHANGELOG

### 1.0.0 — 2026
- Initial release
- Four block types: SPEC, NOTE, BUG, ?
- AI manifest requirement
- Validator specification

---

*HADS is an open standard. MIT License.*
*Contributions: open an issue or pull request on GitHub.*
