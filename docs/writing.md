# Writing Guide

Practical patterns for writing HADS documentation — from scratch or converting existing docs.

---

## Writing from scratch

### Start with the structure, fill in the facts

Don't try to write `[SPEC]` blocks by expanding notes. Work the other way: extract the minimal set of facts a reader needs, write those as `[SPEC]`, then add `[NOTE]` for context.

**The question to ask for each block:** *"If an AI model only reads this, does it have everything it needs?"*

If yes → `[SPEC]`
If no → the missing context goes in `[NOTE]`

---

### Writing [SPEC] blocks

The goal is maximum information density. Prefer:

=== "Good"
    ```markdown
    **[SPEC]**
    - Endpoint: `POST /messages`
    - Auth: Bearer token required
    - Body: JSON `{ "to": string, "text": string, "priority": "high"|"normal" }`
    - Response: 201 Created, body `{ "id": string, "queued_at": ISO8601 }`
    - Rate limit: 60/min per token
    ```

=== "Bad"
    ```markdown
    **[SPEC]**
    To send a message, you should make a POST request to the /messages endpoint.
    Authentication is required using a Bearer token. The body should be a JSON
    object containing the recipient ("to"), message text ("text"), and an optional
    priority field which can be either "high" or "normal". The API will respond with
    a 201 status code if the message was successfully queued.
    ```

The "bad" example is 78 words. The "good" example is 5 bullets. An AI extracting facts from the "good" example makes fewer errors.

---

### Writing [BUG] blocks

BUG blocks are the most valuable content you can write. Be specific:

=== "Good"
    ```markdown
    **[BUG] Messages silently dropped when `text` contains emoji**
    Symptom: POST /messages returns 201, but message is never delivered.
    Cause: Message queue serializer uses `latin-1` encoding — emoji causes silent truncation.
    Fix: Escape emoji before sending, or upgrade to v2.1.0 which uses UTF-8 throughout.
    Affected versions: v1.0.0 – v2.0.3
    ```

=== "Too vague"
    ```markdown
    **[BUG] Emoji issues**
    Emoji sometimes causes problems with message delivery. Make sure to test emoji.
    ```

The vague version gives a developer nothing actionable. The specific version tells them exactly what they'll see, why, and how to fix it.

---

### When to use [?]

`[?]` is for things you believe are true but haven't confirmed:

```markdown
**[?]**
The rate limit may be per-account rather than per-token for enterprise plans.
Observed on 2026-02-15 testing an enterprise account — 1000 req/min instead of 60.
Not officially documented. Verify with support before relying on this.
```

Don't use `[?]` as a way to avoid doing the research. Use it when research isn't possible (no access, time pressure, unconfirmed report) and the information is still useful.

---

## Converting existing documentation

### The conversion workflow

1. **Read the whole document first** — understand what facts it contains
2. **Extract all facts** into `[SPEC]` blocks — one per logical section
3. **Move narrative to `[NOTE]`** — don't delete it, humans still need it
4. **Surface known issues as `[BUG]`** — check issue trackers, FAQ, support tickets
5. **Add the header and manifest**
6. **Validate**

### Before and after

**Before (untagged Markdown):**

```markdown
## Configuration

The application reads its configuration from `config.toml` in the current directory,
or from `~/.config/myapp/config.toml` if the first doesn't exist. You can also set
`MYAPP_CONFIG` environment variable to point to a custom path.

The config file uses TOML format. The most important field is `server.port` — if you
forget to set it, the app uses 3000 by default, which often conflicts with other
development servers.

We had a bug in v1.0 where setting `server.host = "localhost"` would cause the app to
only accept connections from IPv4 loopback, silently dropping IPv6 connections. This was
fixed in v1.1.0 — use `"127.0.0.1"` explicitly if you need to guarantee IPv4-only.
```

**After (HADS):**

```markdown
## Configuration

**[SPEC]**
- Config file search order:
  1. `./config.toml` (current directory)
  2. `~/.config/myapp/config.toml`
  3. Path in `MYAPP_CONFIG` env var (overrides both)
- Format: TOML
- Default port: `server.port = 3000`

**[NOTE]**
Port 3000 conflicts with many development servers (Create React App, Rails default).
Set `server.port` explicitly in production configs.

**[BUG] `server.host = "localhost"` drops IPv6 connections**
Symptom: App accepts IPv4 connections only; IPv6 clients get connection refused with no error.
Cause: `"localhost"` resolved to IPv4 loopback only on certain systems.
Fix: Use `"127.0.0.1"` for explicit IPv4-only, or `"0.0.0.0"` for all interfaces.
Affected versions: v1.0.x. Fixed in v1.1.0.
```

---

## Common pitfalls

**Putting too much in [SPEC]**

`[SPEC]` should contain facts, not guidance. "Use Bearer tokens" is a fact. "We recommend rotating tokens every 24 hours for security" is advice — it goes in `[NOTE]`.

---

**Not writing [BUG] blocks**

Many developers skip `[BUG]` blocks because it feels like admitting the software has problems. This is backwards: `[BUG]` blocks are the most valuable content you can write. They save every future reader from hitting the same wall.

---

**Skipping the manifest**

The manifest is the whole point. A tagged document without a manifest is just regular Markdown with bold annotations — an AI model won't know to prioritize `[SPEC]` over `[NOTE]`.

---

**Long prose in [SPEC]**

If you find yourself writing more than 2–3 sentences in a `[SPEC]` block, stop. Ask: is this a fact or is this narrative? Narrative belongs in `[NOTE]`.
