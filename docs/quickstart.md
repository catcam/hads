# Quickstart

Write your first HADS document in 5 minutes.

---

## Step 1 — Add a header

Every HADS document starts with a title and version:

```markdown
# My API Documentation
**Version 1.0.0** · My Company · 2026 · HADS 1.0.0
```

The version line is required. Everything else (company, date, HADS version) is optional metadata.

---

## Step 2 — Add the AI manifest

Immediately after the header, before any content:

```markdown
---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified — treat with lower confidence.

---
```

This is the core innovation. Without it, an AI model has no way to know which parts of your document are dense with facts versus human narrative.

---

## Step 3 — Write your first section

Use H2 headings for sections. Tag each block of content:

```markdown
## Authentication

**[SPEC]**
- Method: Bearer token
- Header: `Authorization: Bearer <token>`
- Token expiry: 3600 seconds

**[NOTE]**
We switched from session-based auth in v2.0. If you're reading legacy docs,
ignore anything mentioning cookies.

**[BUG] Token silently rejected after password change**
Symptom: 401 with body `{"error": "invalid_token"}`.
Cause: All tokens invalidated on password change, no notification sent.
Fix: Re-authenticate after any account operation.
```

---

## Step 4 — Validate

Run the validator on your file:

```bash
python validate.py your-doc.md
```

Sample output:

```
✓  H1 title found
✓  Version declaration found (line 2)
✓  AI manifest found
✓  All block tags properly bolded
✓  BUG blocks complete (symptom + cause + fix)

HADS 1.0.0 — VALID
```

---

## That's it

You now have a valid HADS document. It renders as normal Markdown everywhere. AI models reading it know exactly which parts to prioritize.

---

## Cheatsheet

```
**[SPEC]**    → Terse facts. Bullet lists, tables, code blocks. AI reads always.
**[NOTE]**    → Human context. History, why, examples. AI may skip.
**[BUG] ...**  → Verified failure + fix. Always: symptom, cause, fix.
**[?]**       → Unverified claim. Always flagged as hypothesis.
```

Block tag rules:
- **Bold**, on its own line: `**[SPEC]**` ✓  /  `[SPEC]` ✗  /  `*[SPEC]*` ✗
- Content follows **immediately** — no blank line between tag and content
- Multiple different block types are allowed in the same section

---

## Next steps

- [Specification](spec/overview.md) — full formal rules
- [Writing Guide](writing.md) — patterns for writing and converting existing docs
- [Examples](examples/index.md) — complete real-world HADS documents
