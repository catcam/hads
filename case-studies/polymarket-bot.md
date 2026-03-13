# Case Study: HADS on a Production AI Agent Codebase

**Project:** Polymarket trading bot — automated prediction market trader on Polygon chain  
**Stack:** Python, ~30 source files, continuous deployment on VPS  
**Context file:** `CLAUDE.md` — the agent's primary knowledge source, read every session

---

## The problem

The bot uses Claude Code as its developer assistant. Every session, Claude loads `CLAUDE.md` in full before doing anything — fixing bugs, reviewing logs, adding features.

The file grew organically over ~40 development sessions into a 705-line, **~12,500 token** document. It contains two very different types of content:

1. **Active facts** — current architecture, file locations, API quirks, proxy config, trading rules, known bugs. Claude needs these for every task.
2. **Version history** — detailed changelogs for 18 named releases (`a0_7` through `negrisk_arb`). These explain *how we got here*, not *where we are*.

The version history is genuinely useful — it prevents re-implementing rejected ideas, explains why certain constraints exist, documents hard-won lessons. But Claude loads it every session regardless of whether the current task has anything to do with it.

---

## Measuring the split

Classifying each section by type:

| Type | Chars | Est. tokens | % of total |
|------|-------|-------------|------------|
| **SPEC** — current facts, architecture, config, rules | 18,400 | ~4,600 | 37% |
| **BUG** — 27 known bugs with symptoms, causes, fixes | 7,500 | ~1,875 | 15% |
| **NOTE** — version history, release changelogs | 24,100 | ~6,025 | 48% |
| **Total** | 50,000 | ~12,500 | 100% |

**48% of every session's context load is version history that most tasks never need.**

---

## What HADS changes

With HADS tagging, the document gets a manifest at the top:

```text
**AI Manifest**
- Read [SPEC] and [BUG] blocks always (~6,475 tokens)
- Read [NOTE] blocks only when asked about history, decisions, or "why"
- Session types: bug-fix → skip NOTE; add-feature → skip NOTE; architecture-review → read all
```

Each release changelog gets wrapped:

```markdown
**[NOTE]**
## a0_13 — Orphan Recovery + Reconciliation Fix
1. 2-pass reconciliation — ...
2. `_recover_untracked_shares()` — ...
...
**[/NOTE]**
```

Each critical fact stays unwrapped (or explicitly `[SPEC]`):

```markdown
**[SPEC]**
## Critical Technical Details

### Proxy (MANDATORY)
Polymarket blocks ALL datacenter IPs. Proxy injection happens in `trading_engine.py`
via `inject_proxy()` BEFORE ClobClient creation.
**[/SPEC]**
```

The known bugs section stays `[BUG]` — always read, since every task risks re-introducing a fixed bug.

---

## Token impact

| Query type | Without HADS | With HADS | Reduction |
|------------|-------------|-----------|-----------|
| Fix a bug | 12,500 | 6,475 | **48%** |
| Add a feature | 12,500 | 6,475 | **48%** |
| Review architecture | 12,500 | 12,500 | 0% |
| "Why did we remove X?" | 12,500 | 12,500 | 0% |
| Typical session mix (80% coding, 20% history) | 12,500 | ~7,680 | **~39%** |

On Claude Sonnet 4.5 pricing (~$3/M input tokens), a development session with 10 context loads costs:
- Without HADS: 125,000 tokens → ~$0.375
- With HADS: ~76,800 tokens → ~$0.230

**Savings: ~$0.145/session, ~39% reduction.** For a bot running 2-3 active development sessions per week, that's ~$22/year — small in absolute terms, but from a file that took 20 minutes to tag.

---

## The less obvious benefit: model behavior

Token counting misses the bigger effect. When Claude loads 12,500 tokens of mixed facts and history, it has to mentally parse what's current vs historical. Version history entries like *"a0_8: Token ID extraction fix — `market.get('tokens', [])` returned None"* look like current behavior unless you read carefully.

With HADS, the model knows: *NOTE blocks describe past state, SPEC blocks describe current state.* The ambiguity disappears. In practice this meant fewer "but I thought you said X in the changelog" confusions during debugging.

---

## What we didn't tag

Three sections stayed untagged (loaded always):

- **Rules** (57 words) — hard constraints on what the bot must never do
- **Useful Commands** (388 words) — shell commands used constantly
- **Communication Style** (13 words) — language preference

These are short enough that the overhead of skip/load decisions isn't worth it.

---

## Honest limitations

- **Maintenance cost:** Every new release adds either a `[NOTE]` block (changelog) or updates to `[SPEC]` blocks. It takes discipline to tag correctly as you write.
- **No enforcement:** There's no validator that breaks CI if someone adds untagged content. HADS is a convention, not a schema.
- **Diminishing returns:** Once a codebase has a well-structured `[SPEC]` section, most of the benefit comes from the first tagging pass. Ongoing savings are from preventing NOTE-creep.

---

## Files

- Full `CLAUDE.md` (before): `CLAUDE.md` in this repo
- HADS spec: [github.com/catcam/hads](https://github.com/catcam/hads)

---

*This bot funds its own Claude API costs from trading profits. Token efficiency isn't a nice-to-have.*
