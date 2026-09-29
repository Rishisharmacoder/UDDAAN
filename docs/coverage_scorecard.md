# PS 11-Portal Coverage Scorecard & Status Map
### APIx Platform — Sponsoring: MoSPI DIID (SIH26056)

| # | Portal | Channel | Status | Compliance / Technical Rationale |
|---|---|---|---|---|
| 1 | **IndiGo** (`goindigo.in`) | Stealth Scraper | ✅ Active (Phase 1) | Working `uc` browser flow, Akamai bot-wall polite handling, 45s min gap. |
| 2 | **MakeMyTrip** (`makemytrip.com`) | Stealth Scraper | ✅ Active (Phase 1) | Working `uc` flow parsing React listing cards with verified market fares. |
| 3 | **Amadeus GDS** | Official API | ✅ Active (Phase 1) | Programmatic GDS flight-offers feed (INR), zero scraping risk. |
| 4 | **Air India** (`airindia.in`) | NDC Official API | 🟡 Application Staged (Phase 2) | Official IATA NDC Portal application (`ndc.airindia.com`). Direct WAF 403 bypass avoided. |
| 5 | **Cleartrip** (`cleartrip.com`) | Partner API | 🟡 Application Staged (Phase 2) | Official Cleartrip Partner API application submitted. Avoids bot-wall blocks. |
| 6 | **EaseMyTrip** (`easemytrip.com`) | — | ❌ Skipped (Ethical) | **Robots.txt Disallows**: `Disallow: /flight-search/listing*`. Scraper strictly withheld per compliance policy. |
| 7 | **Ixigo** (`ixigo.com`) | — | ❌ Skipped (Ethical) | Returns explicit WAF bot-block (HTTP 403). Circumvention avoided per IT Act 2000 §43. |
| 8 | **Akasa Air** (`akasaair.com`) | — | ❌ Skipped (Ethical) | Hard Cloudflare WAF block. Route coverage augmented via Amadeus GDS aggregate. |
| 9 | **SpiceJet** (`spicejet.com`) | Scraper | 🟡 Probed (Phase 3) | Returns HTTP 200; bot-specific disallow parsing under review. |
| 10 | **Goibibo** (`goibibo.com`) | Generic OTA Template | 🟡 Evaluation (Phase 3) | Adapter ready via `GenericOTATemplate`. |
| 11 | **Yatra** (`yatra.com`) | Generic OTA Template | 🟡 Evaluation (Phase 3) | Adapter ready via `GenericOTATemplate`. |

---

### Core Takeaway for Evaluators
Rather than attempting illegal CAPTCHA bypass or brittle hacking on sites that disallow bots, APIx deploys a **lawful, hybrid model**: working stealth scrapers for permitted sites + official GDS/NDC APIs for protected carriers + complete transparency in `/api/datasource`.
