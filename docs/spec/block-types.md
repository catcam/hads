# Block Types

The four HADS block types. Every tagged block in a HADS document is one of these.

---

## Tag format

All block tags are **bold, on their own line**, immediately before their content:

```markdown
**[SPEC]**
- fact one
- fact two
```

No blank line between the tag and the content that follows it.

Valid: `**[SPEC]**` &nbsp;&nbsp; Invalid: `[SPEC]` · `*[SPEC]*` · `**[SPEC] Title**` (except BUG)

---

## [SPEC] — Authoritative fact

**Primary reader:** AI models (always read)

`[SPEC]` blocks contain machine-readable facts. They are the ground truth of a HADS document.

**Content rules:**
- Prefer bullet lists over prose
- Prefer tables for multi-field facts
- Prefer code blocks for syntax, formats, examples
- Maximum 2 sentences of prose — if more is needed, move to `[NOTE]`
- No filler words, no "note that", no "please be aware"

**Example:**

```markdown
**[SPEC]**
- Endpoint: `GET /users/{id}`
- Response: JSON object with fields `id`, `email`, `created_at`
- Auth required: yes (Bearer token)
- Rate limit: 100 req/min per token
```

**What does NOT belong in [SPEC]:**
- History or context ("this was added in v3 because...")
- Recommendations or opinions ("we suggest using...")
- Examples with narrative explanation — use `[NOTE]` for context, code block for the example itself

---

## [NOTE] — Human context

**Primary reader:** Humans (AI may skip under token pressure)

`[NOTE]` blocks contain the "why" — history, design decisions, caveats, examples with explanation, gotchas that don't rise to bug-level.

**Content rules:**
- Write for a human reading the document for the first time
- Prose is fine here — this is where narrative lives
- Include examples, analogies, historical context
- AI models can skip this and still extract all facts from `[SPEC]`

**Example:**

```markdown
**[NOTE]**
The `/users` endpoint originally returned a flat list with pagination via `Link` headers
(RFC 5988 style). We switched to cursor-based pagination in v3.0 after users reported
issues with the page-based approach on large datasets. If you're reading old blog posts
or tutorials, they'll show the old `?page=1&per_page=20` pattern — ignore those.
```

---

## [BUG] — Verified failure

**Primary reader:** Both humans and AI (always read)

`[BUG]` blocks document verified failure modes with confirmed fixes. They are the most valuable content in a HADS document — hard-won knowledge that saves others from hitting the same wall.

**Required fields — all three must be present:**

| Field | What it contains |
|-------|-----------------|
| `Symptom:` | Observable behavior — what the user sees |
| `Cause:` | Root cause — why it happens |
| `Fix:` | Concrete action to resolve it |

**Optional fields:** `Affected versions:`, `Workaround:`

**Tag format:** Title on the same line as the tag — `**[BUG] Short description**`

**Example:**

```markdown
**[BUG] Token silently rejected after password change**
Symptom: 401 with body `{"error": "invalid_token"}` — identical to an expired token.
Cause: All tokens are invalidated on password change. No notification is sent to other sessions.
Fix: Re-authenticate and store the new token. Check for 401 after any account operation.
Affected versions: all
```

**Content rules:**
- The title (on the tag line) should be a short, searchable description of the symptom
- Do not write hypothetical bugs — `[BUG]` means confirmed, with a known fix
- If the fix is unknown, use `[?]` instead

---

## [?] — Unverified

**Primary reader:** Both humans and AI (always flagged as hypothesis)

`[?]` blocks mark content that is inferred, unverified, or provisional. AI models and humans should treat this content with lower confidence.

**When to use:**
- You believe something is true but haven't confirmed it
- A behavior is observed but the cause is unclear
- Documentation came from a source you can't verify
- A fix worked in one case but may not generalize

**Example:**

```markdown
**[?]**
The rate limit may be higher for enterprise accounts (1000 req/min). This is not
documented officially — inferred from observed behavior on a test account. Verify
with your account team before building against this assumption.
```

**Content rules:**
- Always explain *why* you're uncertain
- Include what you do know vs. what is assumed
- If you later confirm the content, convert to `[SPEC]` or `[BUG]`

---

## Multiple blocks per section

Sections can contain multiple blocks of different types. Order is flexible:

```markdown
## Rate Limiting

**[SPEC]**
- Default limit: 100 req/min per token
- Headers returned: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- On limit exceeded: 429 with `Retry-After` header

**[NOTE]**
Rate limits are per-token, not per-IP. A single IP can make unlimited requests
as long as it uses different tokens. This is by design for distributed systems.

**[BUG] Retry-After value off by one second**
Symptom: Retrying exactly at `Retry-After` seconds returns a second 429.
Cause: Server clock skew — the reset timestamp is calculated at request time, not response time.
Fix: Add 1 second to `Retry-After` before retrying.
Affected versions: v2.0.0 – v2.3.1. Fixed in v2.4.0.

**[?]**
Some users report that the rate limit resets faster than the documented 60-second window
for small request volumes (< 10 req/min). Not reproducible in testing.
```

---

## Untagged content

Content without a block tag is treated as `[NOTE]` by AI readers — informational, potentially skippable. Use tagged blocks for anything authoritative.
