# Team Allocation & Definition of Done (DoD)
### APIx Engineering Team (6 Members) · SIH 2026

---

## 👥 Member Role Allocations

| Role | Member | Primary Focus & File Ownership | Key Dependencies |
|---|---|---|---|
| **M1: Team Lead + Core Engine** | Lead Architect | `scrapers/base/*`, `scheduler/*`, `docker-compose.yml`, Code Reviews | Base architecture foundation |
| **M2: Airline Ingestion Specialist** | Ingestion Dev | `scrapers/airline/*` (IndiGo, SpiceJet), Air India NDC probe | M1 base classes |
| **M3: OTA Aggregator Specialist** | Ingestion Dev | `scrapers/ota/*` (MakeMyTrip, Generic OTA, Cleartrip Partner API) | M1 base classes |
| **M4: Storage & Data Pipeline Lead** | Data Engineer | `pipeline/*`, `storage/*`, `queue_worker/*`, Hypertable DDL | M2/M3 raw quote DTOs |
| **M5: Index Engine & API Architect** | Backend Dev | `index_engine/*`, `api/*`, Laspeyres formula, FastAPI endpoints | M4 normalized data store |
| **M6: UI/UX & Demo Strategist** | Fullstack Dev | `dashboard/static/*`, `docs/*`, Demo rehearsals, Pitch Deck | M5 REST APIs |

---

## 🔒 3 Golden Engineering Rules
1. **Core Base Isolation:** `scrapers/base/` is owned exclusively by M1. Site-specific DOM tricks and selectors must remain isolated inside adapter classes.
2. **Zero-Touch Core Extensibility:** Adding a new airline or OTA requires creating only 1 new adapter file and registering it in `config/sources.yaml`. The core pipeline must remain untouched.
3. **Mandatory Provenance:** Every ingested flight quote must contain a non-empty `source` identifier. Code without provenance validation will fail CI/CD testing.

---

## ✅ Definition of Done (DoD) Checklist
- [x] All 10 test cases in `scripts/run_test_drill.py` pass with 100% green status.
- [x] `python -m pytest tests/` executes without syntax or assertion errors.
- [x] The FastAPI server boots up cleanly and serves the interactive dashboard on port 8000.
- [x] Data provenance endpoint `/api/datasource` accurately reports active ingestion source.
- [x] All 11 PS portals are cataloged with transparent status in `docs/coverage_scorecard.md`.
- [x] Comprehensive test report generated in `docs/test_report.md`.
