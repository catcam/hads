# Zephyr API — Reference
**Version 2.3.0** · Fictionware Inc. · 2026 · HADS 1.0.0

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts. Read `[NOTE]` only if additional context is needed. `[?]` blocks are unverified — treat with lower confidence. Always read all `[BUG]` blocks before generating code that calls this API.

---

## 1. BASE URL & VERSIONING

**[SPEC]**
- Base URL: `https://api.zephyr.example/v2`
- Version in path, not header
- Previous version (`/v1`) deprecated — sunset 2026-12-01
- All responses: JSON
- All timestamps: ISO 8601 UTC (`2026-03-01T12:00:00Z`)

**[NOTE]**
Zephyr moved from header-based versioning (`X-API-Version`) to path versioning in v2. If you see old docs or Stack Overflow answers using the header, they describe v1 behavior.

---

## 2. AUTHENTICATION

**[SPEC]**
- Method: Bearer token
- Header: `Authorization: Bearer <token>`
- Token lifetime: 3600 seconds
- Refresh: `POST /auth/refresh` with `{"refresh_token": "<rt>"}`
- Refresh token lifetime: 30 days, single use
- Scope system: `read`, `write`, `admin` (space-separated in token payload)

**[NOTE]**
Tokens are JWTs. You can decode the payload (base64) to inspect expiry and scopes without an API call. The signature uses RS256 — public key available at `GET /auth/jwks`.

**[BUG] Token silently rejected after password change**
Symptom: `401 {"error": "invalid_token"}` — identical to expired token response.
Cause: All tokens for an account are invalidated on password change. No distinct error code.
Fix: Re-authenticate on any 401. Do not assume 401 always means expiry.

**[BUG] Refresh token consumed even on network failure**
Symptom: Refresh request times out; retrying with same refresh token returns `invalid_grant`.
Cause: Server consumes refresh token before confirming response delivery.
Fix: On timeout, attempt re-authentication with credentials rather than retrying refresh.

---

## 3. RATE LIMITING

**[SPEC]**
- Limit: 1000 requests/minute per API key
- Headers returned on every response:
  - `X-RateLimit-Limit: 1000`
  - `X-RateLimit-Remaining: N`
  - `X-RateLimit-Reset: <unix timestamp>`
- Exceeded: `429 Too Many Requests`
- Retry-After header included on 429

**[NOTE]**
Rate limits are per API key, not per IP. Multiple servers sharing one key share the budget. If you run parallel workers, account for this. The limit resets on a rolling 60-second window, not a fixed clock minute.

**[?]**
- Burst allowance above 1000 req/min — documented in internal notes but not confirmed in public spec.
- Rate limits for `admin` scope tokens — assumed same as `write`, unverified.

---

## 4. ENDPOINTS

### 4.1 Items

**[SPEC]**
```
GET    /items              List items
POST   /items              Create item
GET    /items/{id}         Get item by ID
PATCH  /items/{id}         Update item (partial)
DELETE /items/{id}         Delete item
```

**[SPEC] GET /items parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Max results (1–100) |
| `offset` | integer | 0 | Pagination offset |
| `status` | string | — | Filter: `active`, `archived`, `deleted` |
| `sort` | string | `created_desc` | `created_asc`, `created_desc`, `name_asc` |

**[SPEC] Item object**
```json
{
  "id": "itm_a1b2c3",
  "name": "string",
  "status": "active | archived | deleted",
  "tags": ["string"],
  "metadata": {},
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**[NOTE]**
`metadata` is a freeform JSON object. Max size 4KB. Keys must be strings; values can be string, number, or boolean — nested objects are rejected with `400`.

**[BUG] DELETE returns 200 instead of 204**
Symptom: `DELETE /items/{id}` returns `200 OK` with empty body, not `204 No Content`.
Cause: Known deviation from REST convention, will not be fixed until v3 (breaking change).
Fix: Treat both 200 and 204 as success on DELETE.

### 4.2 Webhooks

**[SPEC]**
- Register: `POST /webhooks` with `{"url": "...", "events": ["item.created", "item.deleted"]}`
- Events: `item.created`, `item.updated`, `item.deleted`, `auth.token_revoked`
- Delivery: POST to registered URL within 5 seconds of event
- Retry: 3 attempts at 30s, 5min, 30min intervals
- Signature header: `X-Zephyr-Signature: sha256=<hmac>`
- HMAC key: webhook secret returned on registration (shown once)

**[SPEC] Verifying webhook signature**
```python
import hmac, hashlib

def verify(secret: str, payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**[BUG] Webhook fires twice on PATCH if name field changes**
Symptom: `item.updated` event delivered twice within milliseconds.
Cause: Internal denormalization triggers two write paths when `name` is updated.
Affected versions: 2.0.0–2.3.0 (unresolved).
Fix: Deduplicate on `event_id` field in payload. All deliveries for same event share identical `event_id`.

---

## 5. ERROR FORMAT

**[SPEC]**
All errors follow this structure:
```json
{
  "error": "snake_case_code",
  "message": "Human-readable description",
  "details": {}
}
```

Common error codes:
| Code | HTTP status | Meaning |
|------|-------------|---------|
| `invalid_token` | 401 | Token expired, invalid, or revoked |
| `insufficient_scope` | 403 | Token lacks required scope |
| `not_found` | 404 | Resource does not exist |
| `validation_error` | 400 | Request body failed validation |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Server error |

**[NOTE]**
`details` is populated on `validation_error` — it contains field-level errors:
```json
{"details": {"name": ["required"], "tags": ["max 10 items"]}}
```
For all other error codes, `details` is an empty object.

---

## 6. PAGINATION

**[SPEC]**
- Style: offset-based
- Default page size: 20
- Max page size: 100
- Response envelope:
```json
{
  "data": [...],
  "total": 342,
  "limit": 20,
  "offset": 0
}
```

**[?]**
- Cursor-based pagination — referenced in v3 roadmap, not available in v2.
- Behavior when `offset` exceeds `total` — assumed returns empty `data` array, not verified.
