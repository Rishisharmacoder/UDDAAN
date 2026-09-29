# APIx — 10-Slide Pitch Deck Outline
### Smart India Hackathon 2026 · Grand Finale Presentation

---

### Slide 1: Problem Statement & Context
- **Title:** The CPI Inflation Blindspot in Modern India
- **Problem:** MoSPI CPI Transport sub-group relies on manual fare collection from ticketing booths.
- **Reality:** 90%+ tickets booked online dynamically; intra-day price swings reach 200–400%.
- **Impact:** RBI monetary policy lacks real-time high-frequency retail airfare inflation signals.

---

### Slide 2: The Solution — APIx
- **Tagline:** India's First Real-time, Legally-Compliant Airfare Price Index Platform.
- **Three Pillars:**
  1. **Works:** Fully automated 24x7 scraping + official GDS API ingestion.
  2. **Honest:** Full data provenance (`/api/datasource`) per observation.
  3. **Lawful:** Zero CAPTCHA cracking, no PII, strict robots.txt adherence.

---

### Slide 3: Representative Airfare Basket (DGCA-Calibrated)
- **6 High-Density Routes:** `DEL-BOM`, `DEL-BLR`, `BOM-BLR`, `DEL-CCU`, `BLR-HYD`, `MAA-DEL`.
- **5 Advance Purchase Windows:** `T+1` (urgent), `T+7`, `T+15`, `T+30`, `T+45` (vacation).
- **Total Fixed Cohorts:** 30 representative basket items, each weighted $q = 1.0$.

---

### Slide 4: Data Strategy & Ingestion Coverage
- **11 Problem Statement Portals Managed:**
  - Active Scrapers: IndiGo (Akamai-stealth), MakeMyTrip (React DOM).
  - Programmatic Ingestion: Amadeus GDS (INR flight-offers), Air India NDC, Cleartrip Partner API.
  - Ethical Skip Policy: EaseMyTrip (`Disallow: /flight-search/listing*`), Ixigo (403 bot-wall).

---

### Slide 5: System Architecture & Low-Level Design (LLD)
- **Architecture Flow:** Scheduler ➔ ScraperFactory ➔ FlightScraper ABC ➔ DTO ➔ Pipeline (Dedup + MAD Anomaly) ➔ TimescaleDB + Redis ➔ Index Engine ➔ FastAPI + Chart.js Dashboard.
- **Design Patterns:** Strategy, Template Method, Factory Registry, Pydantic DTO.

---

### Slide 6: Laspeyres Index Engine Methodology
- **CPI Consistency:** Uses official Laspeyres fixed-basket formula mirroring MoSPI's NSO guidelines:
  $$APIx_t = \frac{\sum P_t(r,w) \times q}{\sum P_0(r,w) \times q} \times 100$$
- **Weights:** Airlines 70%, OTAs 30%. Base Month (July 2026 = 100.0).
- **Output:** August 2026 = 105.06, September 2026 = 105.75 (+0.66% MoM).

---

### Slide 7: Live Platform Demonstration
- **Interactive UI:** Chart.js dark-themed dashboard with live sub-second updates.
- **Auditable Quality:** Fail-closed anomaly isolation; recent fares stream.
- **Provenance Pill:** Continuous display of active ingestion source.

---

### Slide 8: Compliance & Legal Moat
- **IT Act 2000 (§43 & §66):** Avoids unauthorized computer access penalties by eliminating WAF evasion and CAPTCHA bypass.
- **DPDP Act 2023 (§6):** Strict no-PII assertion filter on every quote.
- **Polite Crawling:** 45s min gap, 15 req/hr crawl budget, 24h block cooldown.

---

### Slide 9: Automated 24x7 Production Deployment
- **Docker Compose Stack:** 5 microservices (`api`, `postgres/timescaledb`, `redis`, `worker`, `scheduler`).
- **Triple-Tier Storage:** Redis hot cache, TimescaleDB partitioned hypertable, daily CSV snapshot failover.

---

### Slide 10: Future Vision & National Scale
- **Phase 3+ Rollout:** Expand to 100+ tier-2/tier-3 UDAN routes.
- **AI Forecasting:** Predict festive airfare surges (Diwali, Chhath, Summer rush).
- **Intermodal Index:** Extend architecture to Vande Bharat rail fares and interstate bus networks.
