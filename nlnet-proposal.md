# NLnet / NGI Zero Commons Fund — Grant Proposal: HADS
**Version 1.2.0** · Nikša Barlović · 2026-03-28 · Deadline: 2026-04-01

## AI READING INSTRUCTION

Read `[SPEC]` blocks for all factual claims, amounts, and deadlines.
Read `[NOTE]` for context and framing strategy.
`[?]` blocks are estimates — treat with lower confidence.
Always read `[BUG]` before reviewing eligibility sections.

---

## Identifikacija

[SPEC]
- Fond: NGI Zero Commons Fund (NLnet Foundation)
- Forma: https://nlnet.nl/propose/
- Rok: 2026-04-01, 12:00 CEST (tvrdi rok)
- Traženi iznos: €28,000
- Licenca: MIT (kod) + CC BY 4.0 (dokumentacija, paperi)
- Podnositelj: Nikša Barlović, Independent researcher, Zagreb, HR
- ORCID: 0009-0004-7421-0913
- GitHub: https://github.com/catcam/hads
- DOI: 10.5281/zenodo.19019719

---

## 1. Abstract

[SPEC]
Problem:
- Tehnička dokumentacija pišu ljudi, čita je AI model prije čovjeka
- Isti dokument mora zadovoljiti dva potpuno različita čitača
- Tipična stranica API dokumentacije: ~5,000 tokena; AI-u treba <1,500 za jedan fact
- Višak = potrošeni tokeni, prekoračeni context window, halucinacije na malim modelima
- Danas: dva odvojena izvora (za ljude + za AI) = dupli maintenance, divergencija

Rješenje — HADS (Human-AI Document Standard):
- Markdown tagging konvencija, 4 tipa blokova: [SPEC], [NOTE], [BUG], [?]
- AI manifest u headeru — dokument uči model kako ga čitati
- Jedan izvor, dva čitača, nula dupliciranja
- Preliminarni benchmark (4 dokumentna tipa, tiktoken cl100k): **7.91–36.68% token redukcija, prosjek 24.34%** uz zadržan fact-retrieval accuracy na svim ručno testiranim upitima
- Produkcijska potvrda: Polymarket trading bot, **48% redukcija** u živoj sesiji

[NOTE]
HADS nije novi format datoteke — to je konvencija unutar standardnog Markdowna.
Svaki editor koji renderira Markdown renderira HADS ispravno bez ikakvih pluginova.
Ovo je ključno za adoption: nema tooling lock-ina, nema migration cost-a.

Trenutni status (v1.0.0, objavljeno):
- Formalna specifikacija (SPEC.md)
- Python parser (`hads/parser.py`) — produkcijski, testiran, PyPI-spreman
- LangChain document loader (`hads/langchain.py`) — filtrira po block tipu
- Python validator (validate.py)
- Benchmark skripta s rezultatima (`benchmarks/results.json`) — tiktoken, 4 dokumenta, CC0 corpus
- Case study: Polymarket bot (48% token redukcija u produkciji)
- Conversion skill (hads-skills): konvertira postojeće dokumente u HADS format
- Position paper: Zenodo DOI 10.5281/zenodo.19019719
- Otvoreni PR-ovi: Anthropic skills repo (#622), LangChain community (#593)

---

## 2. Veza s NGI Zero Commons Fund

[SPEC]
Alignment s prioritetima fonda:
- Open standard: MIT licenca, vendor-independent, bez tooling lock-ina
- Interoperabilnost: radi s bilo kojim AI modelom i Markdown rendererom
- Open AI systems: smanjuje computational cost → manji/lokalni modeli konkurentni
- Market failure correction: dokumentacijska AI-readiness = collective action problem
- Digital sovereignty: organizacije ne ovise o cloud provideru za AI-readable docs

[NOTE]
NGI Zero Commons Fund financira "open knowledge commons infrastructure".
HADS je točno to — infrastruktura za sloj kojim ljudi sve češće komuniciraju
sa softverom, servisima i međusobno (AI-mediated internet).

---

## 3. Tehnički izazovi

[SPEC]
1. Validator robustnost — edge cases: nested blokovi, višejezični dokumenti, legacy tagging
2. Reference parser API — stabilizacija za PyPI, versioning, backwards-compat
3. Integracija dokumentacijskih sustava — MkDocs, Sphinx (Docusaurus u fazi 3 ako ostane kapacitet)
4. RAG adapter — HADS-aware chunking za vektorske baze (Chroma, Weaviate, pgvector)
5. Reproducibilni benchmarki — proširenje corpus na 10+ tipova, 5 AI modela, formalna accuracy metodologija

---

## 4. Usporedba s postojećim rješenjima

[SPEC]
| Pristup | Problem |
|---|---|
| Odvojeni AI dokumenti (llms.txt, ai.txt) | Dva izvora, divergencija garantirana |
| RAG chunking (default LangChain) | Slijepi chunk po broju znakova, gubi semantičke granice |
| Strukturirani formati (JSON-LD, OpenAPI) | Samo strojno čitljivo, treba odvojene human docs |
| Embedding kompresija | Lossy, proprietary servisi, nema human-readable outputa |
| **HADS** | Jedan Markdown izvor, nula toolinga za čitanje, open standard |

[NOTE]
Najbliži srodan rad je neformalni llms.txt prijedlog (2024) — dodaje odvojeni AI summary file.
HADS se razlikuje fundamentalno: jedan dokument, semantički tagiran, block-level granularnost.
llms.txt rješava problem "gdje AI traži dokumentaciju" — HADS rješava "kako je dokumentacija strukturirana".
Komplementarni su, ne konkurentni. Projekt koji usvoji llms.txt može odmah koristiti HADS za iste dokumente.

---

## 5. Ecosystem i adoption strategija

[SPEC]
Faza 1 (mj. 1–3): Temelji + Empirijska validacija — ~€11,000, ~9 tjedana rada
- Parser stabilizacija + PyPI objava (parser.py osnova već postoji)
- **Benchmark suite v1.0** — proširenje na 10+ dokumentnih tipova, 5 AI modela, formalna accuracy metodologija
  - Accuracy definicija: postotak točnih odgovora na fact-retrieval upite iz [SPEC]-only vs full doc
  - Corpus: CC0, javno dostupan za neovisnu replikaciju
  - Cilj: empirijski potvrditi ili korigirati 24.34% preliminarne nalaze
- GitHub Action za CI validaciju (badge)
- Inicijalni kontakt s 5 pilot projekata (requests, FastAPI, Pydantic, httpx, rich)

Faza 2 (mj. 4–6): Integracije — ~€13,500, ~10 tjedana rada
- MkDocs plugin (~50,000 projekata na GitHubu)
- Sphinx plugin (NumPy, SciPy, pandas ekosustav)
- LlamaIndex HADS document loader (LangChain loader već postoji)
- arXiv paper s benchmark rezultatima

Faza 3 (mj. 7–9): Zajednica i stabilizacija — ~€3,500, ~3 tjedna rada
- Docusaurus plugin (JS/TS ekosustav) — uvjetovano kapacitetom
- Adoption guide za open source maintainere
- RAG adapter za vektorske baze

[NOTE]
Ukupan effort: ~22 tjedna rada rasporedjenih kroz 9 mj (part-time + sprint faze).
Na €28,000 / 22 tjedna ≈ €1,273/tjedan — realno za independent researcher u HR.

Ključni leverage:
- Anthropic PR #622: ako se mergea → HADS dostupan svim Claude Code korisnicima automatski
- LangChain PR #593: ako se mergea → 80,000+ GitHub stars userbase

**Plan B (ako PRs ne budu mergeani):**
- Direktni kontakt s project maintainerima kroz benchmark rezultate i case studies
- Standalone adoption guide za ručnu integraciju
- Focus na MkDocs + Sphinx kao nezavisni distribucijski kanal (ne ovise o PR approvals)

---

## 6. Prior experience

[SPEC]
- HADS v1.0.0 dizajniran i objavljen samostalno
- Produkcijski Python parser (`hads/parser.py`) — već napisan, testiran, PyPI-spreman
- LangChain document loader (`hads/langchain.py`) — već implementiran
- Benchmark infrastruktura — tiktoken, 4 dokumenta, rezultati objavljeni (benchmarks/results.json)
- Aktivni PR-ovi u dva major open-source repozitorija
- Produkcijska primjena: Polymarket trading bot, 48% token redukcija u živoj sesiji
- Position paper objavljen: Zenodo DOI 10.5281/zenodo.19019719
- Background: full-stack developer, 10+ godina iskustva, AI-integrirani sustavi

[NOTE]
Znatan dio "Faze 1" (parser, LangChain loader, benchmark infrastruktura) već postoji.
Grant financira: stabilizaciju za produkcijsku upotrebu, proširenje benchmarka, i integracije u
ekosustave (MkDocs, Sphinx) koji zahtijevaju specifičnu plugin arhitekturu.

---

## 7. Budžet

[SPEC]
| Task | Iznos | Effort | Opis |
|---|---|---|---|
| Specifikacija v1.1 | €2,000 | ~1 tjedan | Edge cases, multilingual, community feedback |
| Parser stabilizacija + PyPI | €3,000 | ~2 tjedna | Backwards-compat API, versioning, test suite (osnova postoji) |
| **Benchmark suite v1.0** | **€4,000** | ~3 tjedna | 10+ dokumentnih tipova, 5 modela, formalna accuracy, CC0 corpus |
| GitHub Action + CI | €500 | ~2 dana | Badge, auto-validation na PR |
| MkDocs plugin | €4,000 | ~3 tjedna | Build integracija, auto-manifest, validacija |
| Sphinx plugin | €4,000 | ~3 tjedna | Extension arhitektura, scientific Python testing |
| LlamaIndex adapter | €2,000 | ~1.5 tjedna | LangChain loader postoji, LlamaIndex je novi |
| arXiv paper | €1,500 | ~1 tjedan | Finalizacija s benchmark rezultatima, submission |
| Community infrastruktura | €1,500 | ~1 tjedan | Adoption guide, project website, docs |
| Docusaurus plugin | €2,000 | ~1.5 tjedna | JS/TS implementacija — uvjetovano kapacitetom |
| Contingency | €1,500 | — | Neočekivani tehnički problemi, CI matrix edge cases |
| **Subtotal** | **€26,500** | ~22 tjedna | |
| **+ Contingency** | **€1,500** | — | |
| **Ukupno** | **€28,000** | | |

[NOTE]
Contingency linija (€1,500) dodana na temelju realnog rizika: Sphinx plugin pokriva
4 verzije × 3 buildera × 2 Python verzije CI matrix. Jedan breaking change može
pojesti cijeli buffer bez contingency.

Ostali izvori financiranja: nema. Samostalni open-source projekt.

---

## 8. Dugoročna održivost

[SPEC]
- HADS je specifikacija, ne softver koji zahtijeva server ili infrastrukturu
- Jednom kad su plugini objavljeni na PyPI/npm, održavanje = patch releases po potrebi
- Parser i validator su stabilan kod — ne zahtijeva kontinuirani development
- Community-driven: GitHub Issues + PR-ovi omogućuju contrib bez centralnog maintainera
- Cilj: HADS postane de facto konvencija, kao što su konvencije za README ili CHANGELOG

[NOTE]
Ako projekt dobije traction (pilot projekti ga usvoje), postoje opcije za
dugoročno financiranje: otvoreni kolektiv, sponzorstvo od AI firmi koje beneficiraju
od boljeg AI-readability ecosystema.

---

## 9. Metrike uspjeha

[SPEC]
- Benchmark: publicirani reproducibilni rezultati na 10+ dokumentnih tipova, uključujući accuracy metodologiju
- Parser: objavljeno na PyPI, ≥2 dependent projekta u 12 mj
- Plugins: MkDocs + Sphinx plugini funkcionalni, u odgovarajućim plugin registrima
- Pilot projekti: ≥3 open-source projekata kontaktirana + ≥1 potvrdilo interes
- GitHub stars: ≥200 u 12 mj (indikator community awareness, ne vanity metric)

---

## 10. Licence

[SPEC]
- Sav kod: MIT License
- Dokumentacija, paperi, vodiči: CC BY 4.0
- Benchmark corpus: CC0 (javno dostupan za replikaciju)
- Sve se razvija javno na GitHubu od prvog dana

---

## Obaveze prema NLnetu (nakon odobrenja)

[SPEC]
- Milestones: dogovaraju se nakon odobrenja, tipično 3–4 isporuke u 9–12 mj
- Plaćanje po milestones (ne odjednom)
- Kratki izvještaji po milestonu (par paragrafa + GitHub link)
- Nema equity, nema lock-ina

[NOTE]
Nikša je fizička osoba (ne firma). NLnet to prihvaća — ugovor + IBAN kao fizička osoba.
U polju "Organisation" u formi upisati: Independent researcher
