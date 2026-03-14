# Changelog

---

## v1.0.0 — 2026-03-13

Initial release of HADS.

### Specification

- Four block types defined: `[SPEC]`, `[NOTE]`, `[BUG]`, `[?]`
- Required document structure: header, AI manifest, content sections
- Validation rules published
- `validate.py` CLI validator (stdlib only, no dependencies)

### Ecosystem

- [hads-skills](https://github.com/catcam/hads-skills) — universal document conversion skill
- [LangChain HADSLoader](https://github.com/langchain-ai/langchain-community/pull/593) — block-type-aware document loader

### Examples

- REST API reference (`api-reference.md`)
- File format specification (`file-format.md`)
- Configuration system (`configuration.md`)

---

## Versioning policy

HADS follows semantic versioning:

| Change type | Version bump | Example |
|-------------|-------------|---------|
| New block type or required field | Major | 2.0.0 |
| New optional element or validation rule | Minor | 1.1.0 |
| Clarification, documentation fix | Patch | 1.0.1 |

A document tagged `HADS 1.0.0` will be valid against any `1.x.x` reader.
Breaking changes require a major version bump and a migration guide.
