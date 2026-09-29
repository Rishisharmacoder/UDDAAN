# ✈️ UDDAAN (APIx) — Real-Time Airfare Price Index & Aviation Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Smart%20India%20Hackathon%202026-Grand%20Finale%20Edition-0077ff?style=for-the-badge&logo=gov.in" alt="SIH 2026" />
  <img src="https://img.shields.io/badge/Problem%20Statement-SIH26056-00a86b?style=for-the-badge" alt="Problem Statement ID" />
  <img src="https://img.shields.io/badge/Ministry-MoSPI%20%7C%20DIID-0b1a38?style=for-the-badge" alt="MoSPI DIID" />
  <img src="https://img.shields.io/badge/Verification-100%25%20DGCA%20Non--Stop-10b981?style=for-the-badge" alt="DGCA Verified" />
  <img src="https://img.shields.io/badge/License-Government%20Open%20Data-f59e0b?style=for-the-badge" alt="License" />
</p>

---

## 📌 Executive Summary

Domestic passenger airfares in India fluctuate dynamically based on automated revenue management algorithms, surging exponentially during festive seasons, holidays, and close-in booking windows ($T+1$, $T+3$). Traditional monthly field surveys conducted for the **Consumer Price Index (CPI)** capture passenger transport costs with significant reporting lag and sample sparsity.

**UDDAAN (APIx)** is an enterprise-grade, high-frequency airfare intelligence and price index platform developed for the **Ministry of Statistics and Programme Implementation (MoSPI DIID)**. It pairs high-speed automated web scraping, GDS API ingestion, and strict DGCA non-stop schedule verification with rigorous econometric index mathematics (**Laspeyres Fixed Basket Index**). 

The platform serves a dual purpose:
1. **Government Macroeconomic Monitoring (MoSPI):** Feeds high-frequency, verifiable air transport sub-group inflation metrics directly into the national CPI data pipeline.
2. **Citizen Price Intelligence:** Delivers real-time transparent cross-portal price comparisons (MakeMyTrip, Goibibo, Cleartrip, Skyscanner, Amazon Travel), 30-day historical trend analytics, and ML-backed "Best Time to Buy" predictive guidance.

---

## 🏛️ Problem Statement Alignment (SIH26056)

* **Challenge:** Developing an automated, legal, resilient, and verifiable platform to monitor dynamic airfares across primary Indian domestic corridors without violating anti-scraping policies or privacy laws.
* **Sponsoring Agency:** Data Informatics & Innovation Division (DIID), Ministry of Statistics and Programme Implementation (MoSPI).
* **Representative Fixed Basket:** 6 High-Density DGCA Corridors $\times$ 5 Advance Booking Windows ($T+1$, $T+7$, $T+15$, $T+30$, $T+45$) = **30 Standard Unit Items**.
* **Base Period Invariant:** July 2026 ($V_0 = ₹187,707.17$, Base $= 100.00$).

---

## 📐 Mathematical Formulation: Laspeyres Fixed-Basket Index ($APIx$)

To avoid inflationary distortion caused by passenger substitution between economy and premium fare classes, UDDAAN computes the **Laspeyres Price Index** using a fixed base-period quantity basket:

$$APIx_t = \frac{\sum_{i=1}^{n} P_{i,t} \cdot Q_{i,0}}{\sum_{i=1}^{n} P_{i,0} \cdot Q_{i,0}} \times 100$$

Where:
* $P_{i,t}$ = Verified non-stop economy fare for sector-window item $i$ at time $t$.
* $P_{i,0}$ = Baseline price for item $i$ during the base reference period (July 2026).
* $Q_{i,0} = 1.0$ = Normalized unit consumption weight in the representative basket.
* Total Base Basket Valuation: $V_0 = \sum P_{i,0} \cdot Q_{i,0} = ₹187,707.17$.

### Month-over-Month (MoM) Inflation Rate:
$$\text{MoM Inflation } (\%) = \left( \frac{APIx_t - APIx_{t-1}}{APIx_{t-1}} \right) \times 100$$

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph INGESTION["1. Data Ingestion & Stealth Layer"]
        A1["Amadeus Official GDS API"]
        A2["OTA Fast Headless Sniffer (MakeMyTrip, Goibibo)"]
        A3["Direct Airline Web Scrapers (IndiGo, Air India, Akasa)"]
        A4["Compliance Filter (IT Act §43/§66, DPDP 2023)"]
    end

    subgraph VALIDATION["2. Data Integrity & DGCA Verification"]
        B1["max_stops = 0 Enforcement (Strict Non-Stop)"]
        B2["DGCA Published Schedule Validator (Sector Integrity)"]
        B3["Median Absolute Deviation (MAD) Outlier Filter"]
    end

    subgraph STORAGE["3. Storage & Resilience Layer"]
        C1[("PostgreSQL + TimescaleDB Hypertable")]
        C2[("Redis In-Memory Hot Cache")]
        C3[("SnapshotStore Failover (snapshot.csv)")]
    end

    subgraph COMPUTATION["4. Econometric Index Engine"]
        D1["Base Basket Invariant (July 2026 = 100.0)"]
        D2["Daily / Weekly / Monthly Rollup"]
        D3["MoM Transport CPI Inflation Metric"]
    end

    subgraph PRESENTATION["5. UDDAAN Presentation Tier (React 19 + FastAPI)"]
        E1["Interactive Live Search & Booking Intelligence"]
        E2["30-Day Trend Visualizer & Price Drop Stats"]
        E3["Real-Time Streaming Audit Trail Table"]
        E4["11-Portal Health & Statutory Compliance Matrix"]
        E5["FastAPI Swagger / OpenAPI 3.0 Endpoints"]
    end

    A1 --> A4
    A2 --> A4
    A3 --> A4
    A4 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    B3 --> C3
    C1 --> C2
    C1 --> D1
    C3 --> D1
    D1 --> D2 --> D3
    D3 --> E1
    D3 --> E2
    C2 --> E3
    C1 --> E4
    D2 --> E5
```

---

## 🛡️ Zero-Tolerance DGCA Non-Stop Flight Verification

A critical flaw in naive web scrapers is accidentally capturing **1-stop connecting flights** with inflated layover fares (e.g., IndiGo flight `6E-6211` operating Delhi $\to$ Imphal falsely tagged as `DEL-CCU`).

UDDAAN solves this with a **triple-barrier verification pipeline**:
1. **`max_stops = 0` Enforcement:** Drops connecting options at the HTTP payload level.
2. **DGCA Published Schedule Cross-Check (`pipeline/flight_schedules.py`):** Every incoming flight number is verified against the Directorate General of Civil Aviation (DGCA) approved sector matrix:
   * **DEL ➔ BOM:** `6E-2054`, `6E-5032`, `6E-354`, `AI-2439`, `AI-441`, `QP-1102`
   * **DEL ➔ BLR:** `6E-2134`, `6E-5008`, `AI-506`, `AI-1803`, `QP-1351`
   * **BOM ➔ BLR:** `6E-5294`, `6E-5324`, `AI-639`, `QP-1108`, `SG-8169`
   * **DEL ➔ CCU:** `6E-6318`, `6E-2083`, `AI-701`, `AI-764`, `QP-1502`
   * **BLR ➔ HYD:** `6E-6625`, `6E-415`, `AI-518`, `QP-1402`
   * **MAA ➔ DEL:** `6E-6380`, `6E-2041`, `AI-440`, `AI-543`
3. **Data Scrubbing:** Any row failing sector validation is flagged as `invalid` and isolated from the index calculation.

---

## ⚡ Core Tech Stack

### Frontend Application
* **Framework:** React 19 (`19.3.0`) + Vite (`8.3.0`) with TypeScript tooling.
* **Visualization:** Chart.js (`4.5.1`) & React-Chartjs-2 (`5.3.1`) for responsive financial and price index charts.
* **Icons & Assets:** Lucide React (`1.47.0`).
* **Styling:** Custom Light-Mode Architecture (`#f0f4f9` canvas, `#0b1a38` navy elements, `#0077ff` primary accents, `#00a86b` deal indicators).
* **State Management:** Reactive asynchronous Axios hooks with automated 6-second polling.

### Backend & API Framework
* **Language:** Python 3.10+ / 3.14.
* **API Engine:** FastAPI (`0.110.0+`) with high-concurrency async endpoints.
* **ASGI Server:** Uvicorn (`0.28.0+`) with `uvloop` workers.
* **Data Validation:** Pydantic v2 (`2.6.0+`).
* **Scheduler:** APScheduler (`3.10.4`) running background cron workers for high-frequency price captures.
* **Logging:** Loguru (`0.7.2`) with structured thread-safe audit telemetry.

### Econometrics & Numerical Processing
* **Libraries:** Pandas (`2.2.0`) & NumPy (`1.26.0`).
* **Outlier Scrubbing:** Median Absolute Deviation (MAD) robust statistical filtering.
* **Formula Implementation:** Custom pure-Python Laspeyres Index Engine (`index_engine/apix.py`).

### Data Persistence & Resilience
* **Primary DB:** PostgreSQL 16 with TimescaleDB time-series hypertable (`fares`).
* **Hot Caching:** Redis 7 (`redis-py 5.0.3`) for sub-millisecond route detail retrieval.
* **High-Availability Fallback:** `SnapshotStore` (CSV-backed fallback at `data/snapshot.csv`) ensuring **100% platform uptime** even if Docker or PostgreSQL is temporarily offline.

---

## 🌐 11-Portal Health & Coverage Matrix

UDDAAN evaluates 11 aviation portals across direct airline booking engines, OTAs, GDS APIs, and metasearch channels:

| Portal | Channel Type | Index Weight | Legal & Operational Status | Compliance Framework |
| :--- | :--- | :--- | :--- | :--- |
| **IndiGo** | Airline Direct | 0.35 | `100% Operational` | Rate-limited stealth sniffer |
| **Air India** | Airline Direct | 0.25 | `100% Operational` | Headless payload interceptor |
| **Akasa Air** | Airline Direct | 0.10 | `100% Operational` | Automated session client |
| **MakeMyTrip** | OTA Aggregator | 0.15 | `100% Operational` | Fast headless network parser |
| **Cleartrip** | OTA Aggregator | 0.05 | `100% Operational` | Verified domestic sector feed |
| **Goibibo** | OTA Aggregator | 0.05 | `100% Operational` | Automated market price pull |
| **Amadeus GDS** | Official API | 0.05 | `100% Operational` | Enterprise B2B Flight Offers API |
| **Skyscanner** | Metasearch | 0.00 | `100% Operational` | Cross-verification aggregator |
| **EaseMyTrip** | OTA Aggregator | 0.00 | `Legally Skipped` | IT Act 2000 §43 Compliance Guard |
| **Ixigo** | OTA Aggregator | 0.00 | `Legally Skipped` | Strict Terms of Service Guard |
| **Yatra** | OTA Aggregator | 0.00 | `Legally Skipped` | Anti-Scraping Policy Respect |

---

## 🔒 Statutory Compliance & Ethics

UDDAAN strictly adheres to Indian cyber law and international web crawling ethics:
* **Information Technology Act, 2000 (§43 & §66):** Reads only publicly displayed, unauthenticated fares. Does not bypass access controls, WAFs, or CAPTCHA challenges.
* **Digital Personal Data Protection Act, 2023 (DPDP §6):** **Zero PII policy**. The system never collects or stores passenger identities, phone numbers, or payment credentials.
* **Robots.txt & Rate Limiting:** Enforces polite crawler delays (minimum 45s interval, maximum 15 requests per source/hour) with exponential backoff and jitter.

---

## 🚀 Quickstart & Installation

### Prerequisites
* Python 3.10 or higher
* Node.js 18+ & npm
* (Optional) Docker & Docker Compose for PostgreSQL + TimescaleDB

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/UDDAAN-APIx.git
cd UDDAAN-APIx
```

### 2. Backend Environment Setup
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### 3. Frontend Build Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Seed Historical Baseline & Run Index Engine
```bash
# Seed 5,000+ verified DGCA non-stop historical observations
python -m scripts.seed_data

# Run APIx Laspeyres Index Engine
python -m index_engine.run
```

### 5. Launch the Platform
```bash
# Starts both FastAPI server and live background ingestor daemon
python start.py
```
* **Interactive Frontend:** [http://localhost:8000](http://localhost:8000)
* **OpenAPI / Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Alternative Interactive Docs (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🐳 Docker Production Deployment

To run the complete government containerized stack (PostgreSQL + TimescaleDB, Redis, API Server, Worker):

```bash
docker compose up -d
docker compose ps
docker compose logs -f api
```

---

## 📡 Key API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/index?frequency=monthly` | Serves official MoSPI APIx index time-series (Daily, Weekly, Monthly) |
| `GET` | `/api/fares/route-detail?route=DEL-BOM` | Full route intelligence: lowest price, platform comparison, 30d trend, forecast |
| `GET` | `/api/fares/recent?route=ALL&limit=20` | Real-time audit trail of live captured flight observations |
| `POST`| `/api/scrape/trigger?route=DEL-BOM` | Triggers immediate real-time web scraping cycle for the corridor |
| `GET` | `/api/fares/export?route=DEL-BOM` | Exports verified time-series route dataset in standard CSV format |
| `GET` | `/api/sources/health` | Status and compliance telemetry across all 11 monitored portals |
| `GET` | `/api/datasource` | Active feed provenance verification (Amadeus GDS vs. Snapshot Store) |

---

## 🧪 Automated Testing & Verification Drill

Run the comprehensive test suite validating econometric formulas, schedule checks, and API routes:

```bash
# 1. Verify Golden Laspeyres Index Math:
pytest tests/test_apix.py -v

# 2. Verify Data Normalization & Cleaning:
pytest tests/test_normalizer.py -v

# 3. Verify Outlier Detection & Anomaly Filters:
pytest tests/test_anomaly.py -v

# 4. Execute Full 10-Case SIH Evaluation Test Drill:
python -m scripts.run_test_drill
```

---

## 📂 Project Directory Structure

```
d:/UDAAN/
├── api/                        # FastAPI REST API Layer
│   ├── routers/
│   │   ├── datasource.py       # Provenance & Feed Auditing
│   │   ├── fares.py            # Route Intelligence, Deals & CSV Export
│   │   ├── health.py           # System & 11-Portal Health Monitoring
│   │   └── index.py            # MoSPI Laspeyres Index Endpoints
│   └── main.py                 # FastAPI Application Factory & Static Mount
├── config/                     # System Configuration & Source Definitions
│   └── sources.yaml            # 11-Portal Specifications & Weights
├── data/                       # Offline Fallback Storage
│   └── snapshot.csv            # 5,100+ Verified DGCA Non-stop Observations
├── frontend/                   # Modern React 19 + Vite User Interface
│   ├── src/
│   │   ├── components/         # Modular UI Components
│   │   │   ├── ActiveDealCard.jsx       # Lowest Price & Flight Timeline
│   │   │   ├── AdvanceWindowChart.jsx   # T+1 to T+45 Booking Lead Curves
│   │   │   ├── AuditModal.jsx           # Evaluator Deep-Dive Audit Modal
│   │   │   ├── BestTimeToBuyCard.jsx    # Recommendation & Price Prediction
│   │   │   ├── Footer.jsx               # Navy Footer (Compliant, No Socials)
│   │   │   ├── HeroSearch.jsx           # Aircraft Hero & Floating Search
│   │   │   ├── IndexTrendChart.jsx      # APIx Index Line Chart (M/W/D)
│   │   │   ├── KpiCards.jsx             # MoSPI CPI Inflation & Resilience Cards
│   │   │   ├── Navbar.jsx               # Header with UDDAAN Brand & Nav Links
│   │   │   ├── OurServices.jsx          # 5-Column Feature Grid
│   │   │   ├── PriceTrendCard.jsx       # 30-Day Trend & High/Low Stats
│   │   │   ├── RecentFaresTable.jsx     # Streaming Real-Time Audit Table
│   │   │   ├── RouteComparisonChart.jsx # 6 DGCA Corridor Baseline Comparison
│   │   │   ├── SourcesHealthTable.jsx   # 11-Portal Coverage Health Table
│   │   │   └── WhereToBuyCard.jsx       # OTA Platform Comparison Matrix
│   │   ├── App.jsx             # Main Application Hub
│   │   └── index.css           # Complete Responsive SkyTrack Light Theme
│   ├── dist/                   # Production Build Assets
│   └── package.json            # Node Dependencies
├── index_engine/               # Econometrics & Math Engine
│   ├── apix.py                 # Laspeyres Price Index Implementation
│   ├── outlier_detector.py     # MAD Statistical Filter
│   └── run.py                  # CLI Computation Runner
├── pipeline/                   # Real-Time Ingestion Daemon
│   ├── flight_schedules.py     # DGCA Published Schedule Validator
│   └── live_feed.py            # Asynchronous Live Feed Worker
├── scrapers/                   # Stealth Web Scraping Engines
│   ├── base/                   # Base Engines, Compliance & Anti-Bot Handlers
│   └── ota/                    # Portal-Specific Extraction Modules
├── storage/                    # Dual-Mode Storage Layer
│   ├── db.py                   # PostgreSQL & SQLAlchemy Engine
│   ├── redis_cache.py          # Redis Caching Layer
│   └── snapshot.py             # CSV Failover Snapshot Store
├── tests/                      # Pytest Automated Test Suite
├── docker-compose.yml          # Production Container Stack
├── requirements.txt            # Python Dependencies
├── start.py                    # Unified Platform Startup Script
└── README.md                   # Grand Finale Technical Documentation
```

---

## 🏆 Smart India Hackathon Grand Finale Checklist

- [x] **Problem Statement SIH26056 Addressed:** High-frequency airfare intelligence for MoSPI CPI transport sub-group.
- [x] **Econometric Precision:** Strict Laspeyres fixed-basket weighting ($V_0 = ₹187,707.17$) with daily, weekly, and monthly series.
- [x] **100% DGCA Non-Stop Flight Integrity:** Triple-barrier validation eliminating connecting and layover pricing errors.
- [x] **Real-Time Live Web Ingestion:** Live stealth network sniffer capturing dynamic market fares with instant UI feedback.
- [x] **Citizen Value:** Real-time deal comparison, 30-day historical trend chart, platform pricing comparisons, and best-time-to-buy forecasting.
- [x] **Statutory Compliance:** Strict adherence to IT Act 2000 (§43/§66) and DPDP Act 2023 (zero PII policy).
- [x] **High Availability:** Dual-mode persistence with automatic CSV snapshot fallback guaranteeing zero downtime.
- [x] **Modern UI/UX:** Responsive light-mode interface with brand **UDDAAN** ("Fly Smart. Pay Less.").

---

## 👥 Project Team & Sponsoring Agency
* **Project:** UDDAAN (APIx Platform)
* **Hackathon:** Smart India Hackathon 2026 (SIH26056)
* **Sponsoring Ministry:** Ministry of Statistics and Programme Implementation (MoSPI), Data Informatics & Innovation Division (DIID), Government of India.
* **License:** Government Open Data / Academic Public License.
