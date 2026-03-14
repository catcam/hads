# Orion Config — Reference
**Version 3.0.0** · Orion Project · 2026 · HADS 1.0.0

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts. Read `[NOTE]` only if additional context is needed. `[?]` blocks are unverified. If generating config files, read §3 (types) and §4 (validation) before writing any values.

---

## 1. CONFIG FILE

**[SPEC]**
- Format: TOML
- Default location: `~/.config/orion/config.toml`
- Override via env: `ORION_CONFIG=/path/to/config.toml`
- Override via flag: `--config /path/to/config.toml`
- Precedence (highest to lowest): CLI flag → env var → file → defaults

**[NOTE]**
Orion used JSON config until v2.x. TOML was adopted in v3.0 for comment support and better human readability. JSON configs from v2.x are not automatically migrated — run `orion migrate-config` to convert.

---

## 2. MINIMAL VALID CONFIG

**[SPEC]**
```toml
[server]
host = "127.0.0.1"
port = 8080
```

All other fields have defaults. A config with only `[server]` host and port is fully functional.

---

## 3. FIELD REFERENCE

### 3.1 [server]

**[SPEC]**
```toml
[server]
host     = "127.0.0.1"   # string, default: "127.0.0.1"
port     = 8080           # integer, 1–65535, default: 8080
tls      = false          # bool, default: false
tls_cert = ""             # string, path to PEM cert (required if tls=true)
tls_key  = ""             # string, path to PEM key (required if tls=true)
timeout  = 30             # integer, seconds, default: 30
workers  = 4              # integer, 1–256, default: CPU count
```

**[BUG] workers = 0 causes immediate crash on startup**
Symptom: `panic: runtime error: invalid memory address` on start.
Cause: Worker pool initialized with size 0 — not validated before use.
Affected: All versions ≤ 3.0.2.
Fix: Set `workers` to any value ≥ 1, or omit (uses CPU count). Fixed in 3.0.3.

### 3.2 [database]

**[SPEC]**
```toml
[database]
driver   = "sqlite"       # string: "sqlite" | "postgres" | "mysql"
dsn      = ""             # string, driver-specific connection string
pool_min = 2              # integer, min connections, default: 2
pool_max = 10             # integer, max connections, default: 10
timeout  = 5              # integer, seconds, query timeout, default: 5
```

DSN format by driver:
```
sqlite:   /path/to/file.db  (relative paths resolved from config dir)
postgres: postgres://user:pass@host:5432/dbname?sslmode=disable
mysql:    user:pass@tcp(host:3306)/dbname?parseTime=true
```

**[NOTE]**
SQLite is the default driver and requires no additional setup. For production deployments with multiple workers, use Postgres or MySQL — SQLite has write contention issues above ~50 concurrent writes/second.

**[BUG] SQLite relative path resolves from working directory, not config dir**
Symptom: Database not found when Orion is started from a directory other than the config dir.
Cause: Path resolution uses `os.Getwd()` instead of config file location.
Affected: All versions (known issue, fix pending).
Fix: Use absolute paths for SQLite DSN.

### 3.3 [logging]

**[SPEC]**
```toml
[logging]
level  = "info"           # string: "debug"|"info"|"warn"|"error", default: "info"
format = "text"           # string: "text"|"json", default: "text"
output = "stdout"         # string: "stdout"|"stderr"|"/path/to/file", default: "stdout"
rotate = false            # bool, only applies when output is a file path
```

**[NOTE]**
`json` format outputs one JSON object per line (NDJSON). Useful for log aggregation systems (Loki, Elasticsearch). `text` format is human-readable and the default for local development.

### 3.4 [cache]

**[SPEC]**
```toml
[cache]
enabled  = true           # bool, default: true
driver   = "memory"       # string: "memory"|"redis", default: "memory"
ttl      = 300            # integer, seconds, default: 300
max_size = 128            # integer, MB, only for "memory" driver, default: 128

[cache.redis]             # only used when driver = "redis"
host     = "127.0.0.1"
port     = 6379
password = ""
db       = 0
```

**[?]**
- `max_size` enforcement — documented but behavior when limit is exceeded (eviction policy) is not specified.
- Redis cluster support — only standalone Redis tested.

---

## 4. VALIDATION RULES

**[SPEC]**
Orion validates config on startup. Invalid config = immediate exit with error message.

| Field | Rule |
|-------|------|
| `server.port` | 1–65535 |
| `server.workers` | 1–256 |
| `server.tls_cert` | Must exist on disk if `tls=true` |
| `server.tls_key` | Must exist on disk if `tls=true` |
| `database.pool_min` | ≤ `pool_max` |
| `database.pool_max` | 1–100 |
| `logging.level` | One of: debug, info, warn, error |
| `logging.format` | One of: text, json |
| `cache.ttl` | ≥ 1 |
| `cache.max_size` | ≥ 1 (MB) |

**[NOTE]**
Validation errors include the field name and a human-readable message. Example:
```
config error: server.workers must be between 1 and 256 (got: 0)
```
All validation errors are collected and printed together — Orion does not stop at the first error.

---

## 5. ENVIRONMENT VARIABLE OVERRIDES

**[SPEC]**
Any config field can be overridden via environment variable.
Format: `ORION_<SECTION>_<FIELD>` (uppercase, sections separated by `_`).

Examples:
```
ORION_SERVER_PORT=9090
ORION_DATABASE_DRIVER=postgres
ORION_LOGGING_LEVEL=debug
ORION_CACHE_REDIS_HOST=redis.internal
```

Type coercion:
- Strings: verbatim
- Integers: parsed as base-10
- Booleans: `"true"`, `"1"`, `"yes"` → true; `"false"`, `"0"`, `"no"` → false

**[BUG] Boolean env vars case-sensitive**
Symptom: `ORION_SERVER_TLS=True` (capital T) does not enable TLS.
Cause: Boolean parser is case-sensitive. Only lowercase `true` is accepted.
Affected: All versions ≤ 3.0.1. Fixed in 3.0.2.
Fix: Use lowercase: `ORION_SERVER_TLS=true`.

---

## 6. COMPLETE EXAMPLE CONFIG

**[SPEC]**
```toml
[server]
host    = "0.0.0.0"
port    = 443
tls     = true
tls_cert = "/etc/orion/cert.pem"
tls_key  = "/etc/orion/key.pem"
workers = 8

[database]
driver   = "postgres"
dsn      = "postgres://orion:secret@db.internal:5432/orion?sslmode=require"
pool_min = 5
pool_max = 20

[logging]
level  = "warn"
format = "json"
output = "/var/log/orion/app.log"
rotate = true

[cache]
enabled = true
driver  = "redis"

[cache.redis]
host = "redis.internal"
port = 6379
db   = 1
```
