# Validation

How to check if a document is valid HADS.

---

## Validity rules

A valid HADS document must have all of the following:

| Rule | Check |
|------|-------|
| H1 title | First non-empty line is `# Title` |
| Version declaration | `**Version X.Y.Z**` appears in first 20 lines |
| AI manifest | Section titled `AI READING INSTRUCTION` before first content section |
| Bold block tags | All tags are `**[SPEC]**`, never `[SPEC]` or `*[SPEC]*` |
| BUG completeness | Every `[BUG]` block contains symptom, cause, and fix |

---

## validate.py

The repo includes a CLI validator:

```bash
# Install (no dependencies — stdlib only)
curl -O https://raw.githubusercontent.com/catcam/hads/main/validate.py

# Validate a file
python validate.py your-doc.md

# Validate multiple files
python validate.py docs/*.md
```

**Sample output — valid:**

```
✓  H1 title found (line 1)
✓  Version declaration found (line 2)
✓  AI manifest found (line 6)
✓  All block tags properly bolded (7 blocks)
✓  BUG blocks complete (3 bugs checked)

HADS 1.0.0 — VALID
```

**Sample output — invalid:**

```
✓  H1 title found (line 1)
✓  Version declaration found (line 2)
✗  AI manifest not found — add "## AI READING INSTRUCTION" section before first content section
✓  All block tags properly bolded (4 blocks)
✗  BUG block at line 47: missing "Fix:" field

HADS 1.0.0 — INVALID (2 errors)
```

---

## Common errors

**Missing version declaration**

```markdown
# My Docs
<!-- missing version line -->

## AI READING INSTRUCTION
...
```

Fix: add `**Version X.Y.Z**` on line 2.

---

**Unbolded block tag**

```markdown
[SPEC]           ← wrong
- endpoint: /api
```

```markdown
**[SPEC]**       ← correct
- endpoint: /api
```

---

**Blank line between tag and content**

```markdown
**[SPEC]**

- endpoint: /api  ← the blank line breaks the block association
```

```markdown
**[SPEC]**
- endpoint: /api  ← correct
```

---

**Incomplete BUG block**

```markdown
**[BUG] Token expires too quickly**
The token expires after 5 minutes sometimes.
← missing Symptom:, Cause:, Fix: fields
```

Correct:

```markdown
**[BUG] Token expires after 5 minutes instead of 60**
Symptom: Requests return 401 after ~5 minutes even with a fresh token.
Cause: Server timezone misconfiguration — token expiry calculated in UTC+7 instead of UTC.
Fix: Update server timezone to UTC. Fixed in v1.2.1.
```

---

## Checking without the validator

Quick manual checklist:

- [ ] First line is `# Title`
- [ ] Second line (or nearby) has `**Version X.Y.Z**`
- [ ] `## AI READING INSTRUCTION` section exists before first content section
- [ ] All block tags are **bold**: `**[SPEC]**`, `**[NOTE]**`, `**[BUG] ...**`, `**[?]**`
- [ ] No blank lines between block tags and their content
- [ ] Every `[BUG]` block has Symptom, Cause, and Fix
