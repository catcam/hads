# NLnet / NGI Zero Commons Fund — Grant Proposal: HADS
**Version 1.2.0** · Nikša Barlović · 2026-03-28 · Deadline: 2026-04-01

---

## Identification

- Fund: NGI Zero Commons Fund (NLnet Foundation)
- Form: https://nlnet.nl/propose/
- Deadline: 2026-04-01, 12:00 CEST
- Requested amount: €28,000
- License: MIT (code) + CC BY 4.0 (documentation, papers)
- Applicant: Nikša Barlović, Independent researcher, Zagreb, HR
- ORCID: 0009-0004-7421-0913
- GitHub: https://github.com/catcam/hads
- DOI: 10.5281/zenodo.19288202 (v1.1.0, current) — previous version: 10.5281/zenodo.19019719

---

## 1. Abstract

**Problem:**
- Technical documentation is written by humans, but read by AI models first
- The same document must serve two fundamentally different readers
- A typical API documentation page: ~5,000 tokens; AI needs <1,500 for a single fact
- Excess tokens = wasted inference cost, context window overflow, hallucinations in smaller models
- Today: two separate sources (for humans + for AI) = double maintenance, guaranteed divergence

**Solution — HADS (Human-AI Document Standard):**
- Markdown tagging convention, 4 block types: [SPEC], [NOTE], [BUG], [?]
- AI manifest in the header — the document teaches the model how to read it
- One source, two readers, zero duplication
- Preliminary benchmark (4 document types, tiktoken cl100k): **7.91–36.68% token reduction, avg 24.34%**, with fact-retrieval accuracy preserved on all manually tested queries
- Production confirmation: Polymarket trading bot, **48% reduction** in live session

**Current status (v1.0.0, published):**
- Formal specification (SPEC.md)
- Python parser (`hads/parser.py`) — production-ready, tested, PyPI-ready
- LangChain document loader (`hads/langchain.py`) — filters by block type
- Python validator (validate.py)
- Benchmark script with results (`benchmarks/results.json`) — tiktoken, 4 documents, CC0 corpus
- Case study: Polymarket bot (48% token reduction in production)
- Conversion skill (hads-skills): converts existing documents to HADS format
- Position paper: Zenodo DOI 10.5281/zenodo.19288202
- Open PRs: Anthropic skills repo (#622), LangChain community (#593)

---

## 2. Alignment with NGI Zero Commons Fund

- Open standard: MIT license, vendor-independent, no tooling lock-in
- Interoperability: works with any AI model and any Markdown renderer
- Open AI systems: reduces computational cost → smaller/local models become competitive
- Market failure correction: documentation AI-readiness = collective action problem
- Digital sovereignty: organizations don't depend on a cloud provider for AI-readable docs

*NGI Zero Commons Fund finances "open knowledge commons infrastructure." HADS is exactly that — infrastructure for the layer through which people increasingly communicate with software, services, and each other (AI-mediated internet).*

---

## 3. Technical Challenges

1. Validator robustness — edge cases: nested blocks, multilingual documents, legacy tagging
2. Reference parser API — stabilization for PyPI, versioning, backwards-compatibility
3. Documentation system integration — MkDocs, Sphinx (Docusaurus in phase 3 if capacity allows)
4. RAG adapter — HADS-aware chunking for vector databases (Chroma, Weaviate, pgvector)
5. Reproducible benchmarks — expand corpus to 10+ types, 5 AI models, formal accuracy methodology

---

## 4. Comparison with Existing Solutions

| Approach | Problem |
|---|---|
| Separate AI documents (llms.txt, ai.txt) | Two sources, divergence guaranteed |
| RAG chunking (default LangChain) | Blind character-count chunking, loses semantic boundaries |
| Structured formats (JSON-LD, OpenAPI) | Machine-readable only, requires separate human docs |
| Embedding compression | Lossy, proprietary services, no human-readable output |
| **HADS** | One Markdown source, zero tooling to read, open standard |

*Closest related work: the informal llms.txt proposal (2024) — adds a separate AI summary file. HADS differs fundamentally: one document, semantically tagged, block-level granularity. llms.txt solves "where does AI look for documentation" — HADS solves "how is documentation structured." They are complementary, not competitive.*

---

## 5. Ecosystem and Adoption Strategy

**Phase 1 (months 1–3): Foundation + Empirical Validation — ~€11,000, ~9 weeks**
- Parser stabilization + PyPI release (parser.py base already exists)
- **Benchmark suite v1.0** — expand to 10+ document types, 5 AI models, formal accuracy methodology
  - Accuracy definition: % correct answers on fact-retrieval queries from [SPEC]-only vs full doc
  - Corpus: CC0, publicly available for independent replication
  - Goal: empirically confirm or correct 24.34% preliminary findings
- GitHub Action for CI validation (badge)
- Initial contact with 5 pilot projects (requests, FastAPI, Pydantic, httpx, rich)

**Phase 2 (months 4–6): Integrations — ~€13,500, ~10 weeks**
- MkDocs plugin (~50,000 projects on GitHub)
- Sphinx plugin (NumPy, SciPy, pandas ecosystem)
- LlamaIndex HADS document loader (LangChain loader already exists)
- Technical documentation, adoption guide, API docs

**Phase 3 (months 7–9): Community and Stabilization — ~€3,500, ~3 weeks**
- Docusaurus plugin (JS/TS ecosystem) — conditional on capacity
- Open source maintainer adoption guide
- RAG adapter for vector databases

**Key leverage:**
- Anthropic PR #622: if merged → HADS available to all Claude Code users automatically
- LangChain PR #593: if merged → 80,000+ GitHub stars userbase

**Plan B (if PRs are not merged):**
- Direct contact with project maintainers via benchmark results and case studies
- Standalone adoption guide for manual integration
- Focus on MkDocs + Sphinx as independent distribution channel (not dependent on PR approvals)

---

## 6. Prior Experience

- HADS v1.0.0 designed and published independently
- Production-ready Python parser (`hads/parser.py`) — written, tested, PyPI-ready
- LangChain document loader (`hads/langchain.py`) — implemented
- Benchmark infrastructure — tiktoken, 4 documents, results published (benchmarks/results.json)
- Active PRs in two major open-source repositories
- Production deployment: Polymarket trading bot, 48% token reduction in live session
- Position paper published: Zenodo DOI 10.5281/zenodo.19288202
- Background: full-stack developer, 10+ years experience, AI-integrated systems

*A significant portion of "Phase 1" (parser, LangChain loader, benchmark infrastructure) already exists. The grant funds: stabilization for production use, benchmark expansion, and integrations into ecosystems (MkDocs, Sphinx) requiring specific plugin architecture.*

---

## 7. Budget

| Task | Amount | Effort | Description |
|---|---|---|---|
| Specification v1.1 | €2,000 | ~1 week | Edge cases, multilingual, community feedback |
| Parser stabilization + PyPI | €3,000 | ~2 weeks | Backwards-compat API, versioning, test suite (base exists) |
| **Benchmark suite v1.0** | **€4,000** | ~3 weeks | 10+ document types, 5 models, formal accuracy, CC0 corpus |
| GitHub Action + CI | €500 | ~2 days | Badge, auto-validation on PR |
| MkDocs plugin | €4,000 | ~3 weeks | Build integration, auto-manifest, validation |
| Sphinx plugin | €4,000 | ~3 weeks | Extension architecture, scientific Python testing |
| LlamaIndex adapter | €2,000 | ~1.5 weeks | LangChain loader exists, LlamaIndex is new |
| Technical documentation | €1,500 | ~1 week | Adoption guide, API docs, project website |
| Docusaurus plugin | €2,000 | ~1.5 weeks | JS/TS implementation — conditional on capacity |
| **Subtotal** | **€26,500** | ~22 weeks | |
| **+ Contingency** | **€1,500** | — | CI matrix edge cases, unexpected breaking changes |
| **Total** | **€28,000** | | |

*Total effort: ~22 weeks distributed across 9 months (part-time + sprint phases). At €28,000 / 22 weeks ≈ €1,273/week — realistic for an independent researcher in Croatia.*

*No other funding sources. Solo open-source project.*

---

## 8. Long-term Sustainability

- HADS is a specification, not software requiring a server or infrastructure
- Once plugins are published on PyPI/npm, maintenance = patch releases as needed
- Parser and validator are stable code — no continuous development required
- Community-driven: GitHub Issues + PRs enable contributions without a central maintainer
- Goal: HADS becomes a de facto convention, like README or CHANGELOG conventions

*If the project gains traction (pilot projects adopt it), options for long-term funding exist: open collective, sponsorship from AI companies that benefit from better AI-readability ecosystems.*

---

## 9. Success Metrics

- Benchmark: published reproducible results on 10+ document types with accuracy methodology
- Parser: published on PyPI, ≥2 dependent projects within 12 months
- Plugins: MkDocs + Sphinx plugins functional, in respective plugin registries
- Pilot projects: ≥3 open-source projects contacted + ≥1 confirmed interest
- GitHub stars: ≥200 within 12 months (community awareness indicator)

---

## 10. Licenses

- All code: MIT License
- Documentation, papers, guides: CC BY 4.0
- Benchmark corpus: CC0 (publicly available for replication)
- Everything developed publicly on GitHub from day one

---

## NLnet Obligations (after approval)

- Milestones: agreed after approval, typically 3–4 deliveries in 9–12 months
- Payment per milestone (not upfront)
- Brief reports per milestone (a few paragraphs + GitHub link)
- No equity, no lock-in
- Applicant is an individual (not a company). NLnet accepts this — contract + IBAN as individual.
- In the "Organisation" field on the form: Independent researcher
