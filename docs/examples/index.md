# Examples

Complete HADS documents demonstrating the standard in real use cases.

---

| Example | What it shows |
|---------|--------------|
| [REST API Reference](api-reference.md) | Endpoint definitions, auth, error codes, BUG blocks for API quirks |
| [File Format Spec](file-format.md) | Binary format with magic bytes, field layout, encoding rules |
| [Configuration System](configuration.md) | TOML config with required/optional fields, env overrides |
| [Trading Bot Config](trading-bot-config.md) | Algorithmic trading parameters, venue endpoints, risk rules, strategy logic |

---

## What to look for

Each example demonstrates:

- **Header format** — title, version, metadata line
- **AI manifest** — adapted to the document type (e.g. API reference adds "always read BUG blocks before generating code")
- **[SPEC] block density** — facts only, no narrative
- **[NOTE] placement** — history and context where it belongs
- **[BUG] completeness** — symptom, cause, fix, affected versions
- **Section organization** — general to specific, required before optional

---

## Use them as templates

These documents are designed to be copied and modified. Fork the structure, replace the content, add your own `[BUG]` blocks.

The [validator](../spec/validation.md) will tell you if the result is valid HADS.
