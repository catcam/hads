# HADS — Human-AI Document Standard
**Version 1.0.0** · Open Standard · 2026-03-26 · HADS 1.0.0

---

## AI READING INSTRUCTION

Read `[SPEC]` blocks for authoritative facts. `SPEC.md` je kompletna specifikacija.

---

## 1. Što je HADS

**[SPEC]**
HADS je tagging konvencija za Markdown tehničku dokumentaciju.
Cilj: AI modeli mogu brzo identificirati što je autoritativna činjenica vs. narativ.

Četiri taga: `[SPEC]` (fakti), `[NOTE]` (kontekst), `[BUG]` (poznati bugovi), `[?]` (neverificirano)

Svaki HADS dokument mora imati AI manifest koji govori modelu što čitati.

**[NOTE]**
HADS ne izmišlja novi format — koristi standardni Markdown. Zero adoption friction.

---

## 2. Lokalne kopije

**[SPEC]**
```
/home/botuser/hads/          — lokalna kopija repozitorija
  SPEC.md                    — kompletna specifikacija (ground truth)
  SKILL.md                   — Claude Code skill za pisanje HADS dokumenata
  api-reference.md           — API referenca
  validate.py                — validator
  paper.md                   — akademski rad
  hads_paper.pdf             — PDF verzija rada
```

GitHub: `catcam/hads` (public), `catcam/hads-skills` (public)

---

## 3. Status projekta

**[SPEC]**
- arXiv submission: **odbijen** (independent researcher, nema institucijsku afiliaciju)
- Zenodo: nije submitano
- PRs: LangChain `langchain-ai/langchain-community` #593, Anthropic skills

**[NOTE]**
HADS rok: NLnet grant prijava bila 1.4.2026 — prošlo. Grant nije podnesen.
NLnet proposal: `/home/botuser/hads-nlnet-proposal.md`

---

## 4. Korištenje

**[SPEC]**
```bash
# Validacija HADS dokumenta
cd /home/botuser/hads
venv/bin/python3 validate.py path/to/doc.md

# GitHub sync
cd /home/botuser/hads && git pull
gh repo view catcam/hads
```

**[SPEC]**
HADS skill za Claude Code (za pisanje novih HADS dokumenata):
```
Skill: hads
```

---

## 5. Benchmark

**[SPEC]**
`/home/botuser/hads-benchmark/` — benchmark infrastruktura + hooks
- Hooks: PreCompact, Stop, PostToolUse (browsing reminder)
- Docs: `/home/botuser/hads-benchmark/`
