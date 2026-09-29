# APIx — System Architecture Specification
### Smart India Hackathon 2026 · Software Track (PS SIH26056)
**Sponsoring Ministry:** Ministry of Statistics and Programme Implementation (MoSPI DIID)

---

## 1. Multi-Layered Architecture

```
[L1]  APScheduler (24x7 Automation: 06:00 & 18:00 Sweeps, 21:00 Index)
        │
        ▼
[L2]  ScraperFactory Dynamic Registry ("indigo", "makemytrip", "amadeus", etc.)
        │
        ▼
[L3]  Source Adapters (FlightScraper ABC: RateLimiter -> ProxyPool -> DOM/API hook)
        │
        ▼
[L4]  FlightResult DTO (Strict Pydantic v2 validation, zero PII assertion)
        │
        ▼
[L5]  Data Pipeline (Normalizer -> Dedup filter <1hr -> MAD Z-score Anomaly Filter)
        │
        ▼
[L6]  Triple-Tier Storage:
        ├── Hot Cache : Redis (Sub-ms API & Dashboard state)
        ├── Warm Store: PostgreSQL + TimescaleDB (Time-series 'fares' hypertable)
        └── Cold Fallback: Daily CSV Snapshot & Offline Synthetic Seed Replay
        │
        ▼
[L7]  Laspeyres Index Engine (Fixed Basket: 6 DGCA Routes x 5 Windows, Base=100.0)
        │
        ▼
[L8]  FastAPI Application Layer (REST API: /api/index, /api/fares, /api/datasource)
        │
        ▼
[L9]  Single-Page Dashboard (Chart.js Dark Theme, Live Provenance Badge)
        │
        ▼
[L10] Monitoring & Forensics (Loguru structured logs, quality audit reports)
        │
        ▼
[L11] Containerized Deployment (Docker Compose 5-container service stack)
```

---

## 2. Ingestion Core & LLD Design Patterns
- **Template Method Pattern:** Encapsulated in `FlightScraper.fetch_fare()` enforcing uniform rate-limiting, compliance checks, DOM interaction, price extraction, DTO normalization, and DPDP Act assertions.
- **Factory & Registry Pattern:** `ScraperFactory` allows adding new airlines or OTAs by writing one adapter file and registering it at runtime without altering core ingestion logic.
- **Strategy Pattern:** Interchangeable data retrieval strategies (undetected browser scraping vs. official GDS REST APIs).

---

## 3. Storage Hierarchy
1. **Redis Hot Cache:** Stores latest computed index curves (`daily`, `weekly`, `monthly`), recent fare feeds, and active data source provenance.
2. **TimescaleDB Hypertable:** Auto-partitions incoming airfare records by `scraped_at` timestamp with 7-day chunk intervals and 30-day compression policies for extreme query speed over millions of quotes.
3. **Snapshot Fallback:** In the event of network disconnection or database server restart, the application automatically fails over to `data/snapshot.csv`, preserving 100% demo availability.
