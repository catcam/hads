# Atlas MM Bot — Trading Configuration Reference
**Version 1.0.0** · Atlas Trading Systems · 2026 · HADS 1.0.0
---
## AI READING INSTRUCTION
Read `[SPEC]` and `[BUG]` blocks for authoritative facts. Read `[NOTE]` only if additional context is needed. `[?]` blocks are unverified — treat with lower confidence. If generating live-trading config or venue adapter code, read §§2–6 before writing values. Always read `[BUG]` blocks before enabling `mode: live`.
---
## 1. FILE LOCATION & MINIMUM CONFIG
**[SPEC]**
- Format: YAML
- Default path: `./config/trading-bot.yaml`
- Override via env: `ATLAS_BOT_CONFIG=/path/to/trading-bot.yaml`
- Override via flag: `--config /path/to/trading-bot.yaml`
- Modes: `paper`, `live`, `replay`
- Default timezone for schedules and risk resets: UTC
- Hot reload: unsupported; restart required after any config change
- Secrets source: environment variables only
```yaml
mode: paper
venue: kraken
symbols: [BTC/USD]
strategy:
  type: inventory_skew_mm
risk:
  max_gross_notional_usd: 25000
  max_daily_loss_usd: 750
execution:
  maker_only: true
  quote_refresh_ms: 1000
```
---
## 2. VENUE CONNECTIVITY & API ENDPOINTS
**[SPEC]**
| Venue | Live REST | Paper REST | WebSocket |
|-------|-----------|------------|-----------|
| Kraken Spot | `https://api.kraken.com` | `https://paper-api.kraken.internal` | `wss://ws.kraken.com/v2` |
| Binance USDM | `https://fapi.binance.com` | `https://testnet.binancefuture.com` | `wss://fstream.binance.com/ws` |
**[SPEC]**
Required routes:
```text
GET  /0/public/Time
GET  /0/public/AssetPairs
GET  /0/public/Depth?pair={symbol}
POST /0/private/AddOrder
POST /0/private/CancelOrder
POST /0/private/CancelAll
POST /0/private/Balance
POST /fapi/v2/positionRisk
```
- Kraken auth headers: `API-Key`, `API-Sign`
- Binance auth header: `X-MBX-APIKEY`
- Required env vars: `ATLAS_API_KEY`, `ATLAS_API_SECRET`, `ATLAS_API_PASSPHRASE` (if required)
- Request timestamp tolerance: `<= 5000 ms`
- Clock drift budget: `<= 250 ms`
- Nonce source: monotonic millisecond counter per process
- Required market-data channels: top-of-book, trades, mark price (futures only)
- Reconnect backoff: `1s, 2s, 4s, 8s, 16s`, cap `30s`
- Quoting pause threshold for stale market data: `1500 ms`
**[BUG] Order signatures fail when host clock drifts >250 ms**
Symptom: Authenticated order requests return `EAPI:Invalid signature` or Binance `-1021`.
Cause: Request signing uses local wall-clock time and does not self-correct when NTP drift exceeds the configured budget.
Fix: Restore NTP sync and restart the bot. Keep `clock_check_interval_s <= 30`.
Affected versions: all
---
## 3. MARKET UNIVERSE & EXECUTION PARAMETERS
**[SPEC]**
| Field | Type | Default | Rule |
|-------|------|---------|------|
| `symbols` | list[string] | — | At least one symbol required |
| `venue` | string | — | One venue per process |
| `max_symbols` | integer | `8` | Range `1–32` |
| `base_order_notional_usd` | number | `250` | Range `10–5000` |
| `levels_per_side` | integer | `2` | Range `1–5` |
| `level_spacing_bps` | number | `4` | Range `1–25` |
| `quote_refresh_ms` | integer | `1000` | Range `100–5000` |
| `cancel_after_ms` | integer | `3000` | Must be `>= quote_refresh_ms` |
| `maker_only` | boolean | `true` | Must remain true for market making |
| `min_spread_bps` | number | `8` | Range `2–100` |
| `max_spread_bps` | number | `45` | Must be `>= min_spread_bps` |
| `order_ttl_ms` | integer | `5000` | Range `500–30000` |
**[SPEC]**
- Per-symbol metadata required at startup: `tick_size`, `lot_size`, `min_order_size`, `price_band_bps`
- Venue metadata is loaded once at startup and cached for the process lifetime
- Startup must fail if any configured symbol lacks venue metadata
- Price precision must match tick size; quantity precision must match lot size
---
## 4. RISK RULES
**[SPEC]**
| Field | Default | Limit semantics |
|-------|---------|-----------------|
| `max_gross_notional_usd` | `25000` | Sum of absolute long and short exposure |
| `max_net_position_usd` | `5000` | Directional inventory cap per symbol |
| `max_order_notional_usd` | `1000` | Hard cap per order |
| `max_open_orders_per_symbol` | `6` | Includes working replace orders |
| `max_daily_loss_usd` | `750` | Stops new entry orders when breached |
| `max_drawdown_pct` | `4.0` | Relative to session starting equity |
| `max_slippage_bps` | `12` | Cap for aggressive exit or hedge |
| `max_leverage` | `2.0` | Futures only |
| `kill_switch_file` | `./run/KILL_SWITCH` | Presence triggers immediate cancel-all |
| `risk_reset_time_utc` | `00:00` | Daily loss counters reset here |
**[SPEC]**
- On `max_daily_loss_usd` breach: cancel resting entry orders; continue reduce-only exits; reject position-increasing orders until reset
- On `max_drawdown_pct` breach: cancel all orders; flatten at `max_slippage_bps`; set process state to `halted`
- On kill switch file detection: cancel all orders immediately; do not auto-flatten; require operator restart to resume
**[BUG] Daily loss resets on local midnight if `risk_reset_time_utc` is omitted in legacy configs**
Symptom: Session PnL resets at the host timezone boundary instead of UTC, extending allowed loss during overlap hours.
Cause: Legacy internal configs inherited the container locale when `risk_reset_time_utc` was absent.
Fix: Set `risk_reset_time_utc` explicitly in every deployment config. Schema `1.0` removes locale fallback.
Affected versions: legacy configs before schema `1.0`
---
## 5. STRATEGY LOGIC
**[SPEC]**
- Mid-price source: top-of-book midpoint
- Short-term fair value: `fair = mid + alpha_microprice + alpha_trade_imbalance`
- `alpha_microprice` window: last `20` book updates
- `alpha_trade_imbalance` window: last `30` seconds of trades
- Missing alpha inputs default to `0`
```text
bid_px = floor_to_tick(fair * (1 - bid_spread_bps / 10000))
ask_px = ceil_to_tick(fair * (1 + ask_spread_bps / 10000))
order_qty = clamp(base_order_notional_usd / fair, min_order_size, max_order_notional_usd / fair)
inventory_ratio = position_usd / max_net_position_usd
bid_spread_bps = min_spread_bps + max(0, inventory_ratio) * skew_bps_per_unit
ask_spread_bps = min_spread_bps + max(0, -inventory_ratio) * skew_bps_per_unit
```
- Default `skew_bps_per_unit = 18`
- If `abs(inventory_ratio) >= 1`, disable the position-increasing side completely
- Level `n` adds `n * level_spacing_bps` to each side
- Never cross the opposite best quote when `maker_only = true`
- Do not quote if top-of-book spread `< min_spread_bps`
- Do not quote if market-data age `> stale_data_threshold_ms`
- Do not quote if remaining risk budget `< base_order_notional_usd`
- Do not quote if exchange status for symbol is not `online`
- If `trading_window_utc` is set, new entries are allowed only inside that window
---
## 6. CONTROL API
**[SPEC]**
- Bind address default: `127.0.0.1:9091`
- Auth: static bearer token from `ATLAS_CONTROL_TOKEN`
- Response format: JSON
| Method | Path | Behavior |
|--------|------|----------|
| `GET` | `/healthz` | Process, venue, WebSocket, and risk status |
| `GET` | `/positions` | Per-symbol quantity, notional, unrealized PnL |
| `GET` | `/orders` | Working orders with side, price, size, age |
| `POST` | `/pause` | Stop new entry orders |
| `POST` | `/resume` | Resume quoting if not risk-halted |
| `POST` | `/flatten` | Cancel all and reduce inventory to zero |
| `POST` | `/reload-market-data` | Reconnect market-data subscriptions only |

| Code | Meaning |
|------|---------|
| `200` | Request applied |
| `202` | Request queued |
| `409` | State conflict |
| `503` | Venue or market-data dependency unavailable |
---
## 7. ENVIRONMENT OVERRIDES
**[SPEC]**
- Environment variables override file values
- Format: `ATLAS_<SECTION>_<FIELD>`
- Nested fields use additional `_`
- Scalar coercions: integers base-10, floats decimal, booleans `true|false|1|0`
```bash
ATLAS_MODE=paper
ATLAS_EXECUTION_QUOTE_REFRESH_MS=500
ATLAS_RISK_MAX_DAILY_LOSS_USD=500
ATLAS_STRATEGY_SKEW_BPS_PER_UNIT=24
ATLAS_CONTROL_BIND=127.0.0.1:9191
```
---
## 8. COMPLETE LIVE EXAMPLE
**[SPEC]**
```yaml
mode: live
venue: kraken
symbols: [BTC/USD, ETH/USD]
execution:
  maker_only: true
  quote_refresh_ms: 750
  cancel_after_ms: 3000
  base_order_notional_usd: 400
strategy:
  type: inventory_skew_mm
  min_spread_bps: 10
  skew_bps_per_unit: 20
risk:
  max_gross_notional_usd: 40000
  max_net_position_usd: 7500
  max_daily_loss_usd: 1200
  max_drawdown_pct: 3.5
  risk_reset_time_utc: "00:00"
```
