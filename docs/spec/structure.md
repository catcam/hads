# Document Structure

Every valid HADS document has three required parts, in order.

---

## Required structure

```
1. Header block      — H1 title + version line
2. AI manifest       — reading instruction for AI models
3. Content sections  — tagged blocks organized by topic
```

---

## 1. Header block

The header is the first thing in the file:

```markdown
# Document Title
**Version X.Y.Z** · Author · Date · [additional metadata]
```

**Required:**
- H1 title (first line)
- `**Version X.Y.Z**` in the first 20 lines of the file

**Optional metadata** (all on the version line, separated by `·`):
- Author or organization
- Date
- HADS version: `HADS 1.0.0`
- Status: `Draft`, `Stable`, `Deprecated`
- License

**Examples:**

```markdown
# Zephyr API Reference
**Version 2.3.0** · Fictionware Inc. · 2026 · HADS 1.0.0

# Internal Config System
**Version 0.4.1** · Platform Team · Draft

# My Library Format Spec
**Version 1.0.0** · CC BY · HADS 1.0.0
```

---

## 2. AI manifest

The manifest appears immediately after the header, before any content sections. It is the core innovation of HADS.

**Minimal valid manifest:**

```markdown
---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified — treat with lower confidence.

---
```

The horizontal rules (`---`) are recommended for visual separation but not required.

**The manifest can be extended** to give model-specific guidance:

```markdown
## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified — treat with lower confidence.

Always read all `[BUG]` blocks before generating any code that calls this API.
The authentication section ([SPEC] blocks) must be read before any other section.
```

**Why the manifest matters:**

Without it, an AI model must guess which parts of the document are authoritative. With it, even small (7B) models know exactly what to read and what to skip. The difference is measurable in factual accuracy, especially on longer documents.

---

## 3. Content sections

Sections use H2 headings. Subsections use H3.

```markdown
## Section Name

**[SPEC]**
...

**[NOTE]**
...

### Subsection Name

**[SPEC]**
...
```

**Section ordering conventions:**

- General before specific
- Required before optional
- Common before edge cases

**Recommended sections for common document types:**

=== "API Reference"
    1. Overview / Base URL
    2. Authentication
    3. Endpoints (one H2 per resource or group)
    4. Error codes
    5. Rate limits
    6. Changelog

=== "File Format"
    1. Overview
    2. Magic bytes / header
    3. Structure / layout
    4. Field definitions
    5. Encoding rules
    6. Known edge cases

=== "Configuration"
    1. Overview
    2. File location / format
    3. Required fields
    4. Optional fields
    5. Environment variable overrides
    6. Examples

---

## Full minimal example

```markdown
# My Service — Configuration Reference
**Version 1.2.0** · My Team · 2026 · HADS 1.0.0

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified — treat with lower confidence.

---

## 1. File Location

**[SPEC]**
- Default path: `~/.config/myservice/config.toml`
- Override with env var: `MYSERVICE_CONFIG=/path/to/config.toml`
- Format: TOML

**[NOTE]**
On Windows, the default path is `%APPDATA%\myservice\config.toml`.

## 2. Required Fields

**[SPEC]**
```toml
[server]
host = "0.0.0.0"   # required
port = 8080         # required

[auth]
secret = "..."      # required, min 32 chars
` ``

**[BUG] Service fails silently with secret shorter than 32 chars**
Symptom: Service starts but all authenticated requests return 401.
Cause: Secret is silently truncated to 32 chars; if shorter, the HMAC is invalid.
Fix: Ensure `auth.secret` is at least 32 characters. Use `openssl rand -hex 32` to generate.
```

---

## Changelog section

Recommended as the last section:

```markdown
## Changelog

**[SPEC]**

| Version | Date | Change |
|---------|------|--------|
| 1.2.0 | 2026-03-01 | Added `auth.secret` minimum length validation |
| 1.1.0 | 2026-01-15 | Added Windows path support |
| 1.0.0 | 2025-11-01 | Initial release |
```
