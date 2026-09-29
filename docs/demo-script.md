# 5-Minute SIH Grand Finale Demo Script
### APIx — Real-time Airfare Price Index for India (PS SIH26056)

---

## ⏱ Time-Stamped Demo Walkthrough (Total: 5 Minutes)

### [0:00 – 0:30] Introduction & Dashboard Overview
- **Action:** Open browser to `http://localhost:8000`.
- **Dialogue:**  
  *"Respected Judges, welcome to APIx. Currently, the National Statistical Office under MoSPI manually collects airfare data from a handful of physical ticketing counters. But in India, 90%+ tickets are booked dynamically online where prices fluctuate up to 300% within hours. APIx is an automated, legally compliant, real-time intelligence platform that collects domestic airfares across representative city-pairs and computes an index that directly mirrors India's CPI methodology."*
- **Visual:** Point to top stats cards showing 4,980+ records, latest APIx at 105.75 (+0.66% MoM), and the 30-item basket.

---

### [0:30 – 1:00] Honesty & Data Provenance (The "Trust" Pillar)
- **Action:** Point out the top-right **Data Source** pill, then navigate to `/api/datasource`.
- **Dialogue:**  
  *"Before we look at the charts, look at this endpoint: `/api/datasource`. We believe in 100% provenance. Every data row discloses its origin. We never mask synthetic test data as live data. Our system deploys a triple fallback: Official Amadeus GDS API ➔ Daily CSV Snapshot ➔ Seed Replay. The provenance is public, auditable, and transparent."*

---

### [1:00 – 2:30] Live Ingestion & Pipeline Filtering
- **Action:** Switch to terminal and run a targeted sweep:  
  `python -m scripts.driver_loop --sites indigo,makemytrip --routes DEL-BOM --windows T+7 --dry`
- **Dialogue:**  
  *"Watch the ingestion core in action. In under 5 seconds, our ScraperFactory delegates to IndiGo and MakeMyTrip stealth adapters. The raw quotes flow through our data pipeline: normalizing currency strings, dropping duplicates within 60 minutes, and applying Median Absolute Deviation (MAD) anomaly filtering. Notice that suspicious or CAPTCHA-corrupted values fail closed — they never pollute the index."*
- **Visual:** Refresh the dashboard. Show the new rows appearing instantly in the **Recent Airfares** audit table.

---

### [2:30 – 3:30] Index Engine Methodology & CPI Mirroring
- **Action:** Toggle **Monthly ➔ Weekly ➔ Daily** on the main Chart.js trend card.
- **Dialogue:**  
  *"APIx uses a fixed Laspeyres price index formula, identical to the official Indian CPI. Our basket maintains 6 high-density DGCA city-pairs across 5 advance purchase windows: T+1, T+7, T+15, T+30, and T+45. Taking July 2026 as Base Month = 100.0, August rose to 105.06, and September reached 105.75, accurately capturing monsoon demand and holiday booking surges. Furthermore, airlines receive a 70% weight and OTAs 30%, reflecting market booking shares."*

---

### [3:30 – 4:30] Resilience & Failover Drill
- **Action:** Simulate network / database outage drill.
- **Dialogue:**  
  *"What happens if an airline blocks scrapers or the cloud database disconnects during a sweep? APIx never crashes. Our Redis hot cache serves sub-millisecond reads, and our snapshot storage provides zero-downtime fallback. When we simulate service recovery, the scheduler automatically reconnects without human intervention."*

---

### [4:30 – 5:00] Legal Compliance & National Rollout
- **Action:** Display `docs/coverage_scorecard.md` and `docs/COMPLIANCE.pdf` references.
- **Dialogue:**  
  *"We do not bypass CAPTCHAs or break WAFs — doing so violates IT Act 2000 Section 43/66. Instead, where scraping is disallowed (like EaseMyTrip's robots.txt), we legally skip and substitute coverage through official GDS and NDC APIs. APIx is containerized, zero-config, and ready for national deployment across 100+ routes for MoSPI. Thank you!"*

---

## 🎯 Evaluator Q&A — Rapid Defense Cheat Sheet

| Question | Winning Response (2 Lines) |
|---|---|
| **"Is automated web scraping legal here?"** | *"Yes, because we strictly follow IT Act 2000 and DPDP Act 2023: zero PII collection, hard-coded 45s polite rate limits, and full compliance with robots.txt disallows."* |
| **"What if an airline changes its website DOM?"** | *"Our LLD architecture isolates selectors into individual adapter files. A DOM change requires modifying only one file; the pipeline, DTO, database, and index engine remain untouched."* |
| **"How does this plug into MoSPI's existing CPI?"** | *"MoSPI can directly integrate our `/api/index?frequency=monthly` series as a high-frequency supplementary sub-index for the Transport & Communication basket."* |
| **"How do you handle CAPTCHAs?"** | *"We do not bypass CAPTCHAs. Bypassing CAPTCHAs is a legal liability. Sites that demand CAPTCHAs are covered via official APIs like Amadeus GDS or Air India NDC."* |
