import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import HeroSearch from './components/HeroSearch';
import ActiveDealCard from './components/ActiveDealCard';
import WhereToBuyCard from './components/WhereToBuyCard';
import PriceTrendCard from './components/PriceTrendCard';
import BestTimeToBuyCard from './components/BestTimeToBuyCard';
import OurServices from './components/OurServices';
import KpiCards from './components/KpiCards';
import IndexTrendChart from './components/IndexTrendChart';
import AdvanceWindowChart from './components/AdvanceWindowChart';
import RouteComparisonChart from './components/RouteComparisonChart';
import RecentFaresTable from './components/RecentFaresTable';
import SourcesHealthTable from './components/SourcesHealthTable';
import Footer from './components/Footer';
import AuditModal from './components/AuditModal';
import { Sparkles, ShieldCheck } from 'lucide-react';

export default function App() {
  const [origin, setOrigin] = useState('DEL');
  const [dest, setDest] = useState('BOM');
  const [routeData, setRouteData] = useState(null);
  const [fares, setFares] = useState([]);
  const [summary, setSummary] = useState(null);
  const [indexData, setIndexData] = useState(null);
  const [frequency, setFrequency] = useState('monthly');
  const [sources, setSources] = useState([]);
  const [datasource, setDatasource] = useState(null);
  const [auditRoute, setAuditRoute] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [auditOpen, setAuditOpen] = useState(false);

  const currentRoute = `${origin}-${dest}`;

  // Fetch dynamic route intelligence from backend
  const fetchRouteData = async (routeKey = currentRoute) => {
    try {
      const res = await axios.get(`/api/fares/route-detail?route=${routeKey}`);
      setRouteData(res.data);
    } catch (err) {
      console.error('Error fetching route detail:', err);
    }
  };

  // Fetch recent audit stream
  const fetchRecentAudit = async (routeFilter = auditRoute) => {
    try {
      const routeParam = routeFilter === 'ALL' ? '' : `route=${routeFilter}&`;
      const res = await axios.get(`/api/fares/recent?${routeParam}limit=20`);
      setFares(res.data);
    } catch (err) {
      console.error('Error fetching recent audit:', err);
    }
  };

  // Fetch summary KPIs
  const fetchSummary = async () => {
    try {
      const res = await axios.get('/api/summary');
      setSummary(res.data);
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  // Fetch APIx Index Trend
  const fetchIndexData = async (freq = frequency) => {
    try {
      const res = await axios.get(`/api/index?frequency=${freq}`);
      setIndexData(res.data);
    } catch (err) {
      console.error('Error fetching index data:', err);
    }
  };

  // Fetch Portal Sources Health
  const fetchSources = async () => {
    try {
      const res = await axios.get('/api/sources/health');
      setSources(res.data);
    } catch (err) {
      console.error('Error fetching sources health:', err);
    }
  };

  // Fetch Active Datasource Provenance
  const fetchDatasource = async () => {
    try {
      const res = await axios.get('/api/datasource');
      setDatasource(res.data);
    } catch (err) {
      console.error('Error fetching datasource provenance:', err);
    }
  };

  // Route swap
  const handleSwap = () => {
    const oldOrig = origin;
    const oldDest = dest;
    setOrigin(oldDest);
    setDest(oldOrig);
  };

  // Search Button Click
  const handleSearch = async () => {
    setLoading(true);
    await Promise.all([
      fetchRouteData(`${origin}-${dest}`),
      fetchRecentAudit(auditRoute),
      fetchSummary(),
      fetchIndexData(frequency)
    ]);
    setTimeout(() => setLoading(false), 300);
  };

  // Trigger Live Scraper
  const handleTriggerScrape = async () => {
    setScraping(true);
    try {
      await axios.post(`/api/scrape/trigger?route=${currentRoute}`);
      await Promise.all([
        fetchRouteData(currentRoute),
        fetchRecentAudit(auditRoute),
        fetchSummary(),
        fetchIndexData(frequency),
        fetchSources()
      ]);
    } catch (err) {
      console.error('Live scrape failed:', err);
    } finally {
      setTimeout(() => setScraping(false), 800);
    }
  };

  // Refresh All Data
  const handleRefreshAll = async () => {
    setLoading(true);
    await Promise.all([
      fetchRouteData(`${origin}-${dest}`),
      fetchRecentAudit(auditRoute),
      fetchSummary(),
      fetchIndexData(frequency),
      fetchSources(),
      fetchDatasource()
    ]);
    setTimeout(() => setLoading(false), 400);
  };

  // Handle Frequency Toggle for Index Trend
  const handleFrequencyChange = (newFreq) => {
    setFrequency(newFreq);
    fetchIndexData(newFreq);
  };

  // Handle Audit Corridor Change
  const handleAuditRouteChange = (newRoute) => {
    setAuditRoute(newRoute);
    fetchRecentAudit(newRoute);
  };

  const handleBookNow = (platformName) => {
    const orig = origin;
    const dst = dest;
    const urls = {
      'MakeMyTrip': `https://www.makemytrip.com/flight/search?itinerary=${orig}-${dst}-15/10/2026&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E`,
      'Goibibo': `https://www.goibibo.com/flights/air-${orig}-${dst}-20261015--1-0-0-E-D/`,
      'Cleartrip': `https://www.cleartrip.com/flights/results?from=${orig}&to=${dst}&depart_date=15/10/2026&adults=1&childs=0&infants=0&class=Economy&airline=&carrier=&intl=n&sd=1727000000000&page=loaded`,
      'Skyscanner': `https://www.skyscanner.co.in/transport/flights/${orig.toLowerCase()}/${dst.toLowerCase()}/`,
      'Amazon Travel': `https://www.amazon.in/flights?from=${orig}&to=${dst}`
    };
    const target = urls[platformName] || urls['MakeMyTrip'];
    window.open(target, '_blank');
  };

  // Auto-fetch on corridor change
  useEffect(() => {
    fetchRouteData(`${origin}-${dest}`);
  }, [origin, dest]);

  // Initial load
  useEffect(() => {
    handleRefreshAll();
    const interval = setInterval(() => {
      fetchRouteData(`${origin}-${dest}`);
      fetchRecentAudit(auditRoute);
      fetchSummary();
    }, 6000);
    return () => clearInterval(interval);
  }, [origin, dest, auditRoute, frequency]);

  return (
    <div className="page-container">
      {/* 1. Header / Navbar with UDAAN brand, Navigation & Live Controls */}
      <Navbar
        onRefresh={handleRefreshAll}
        loading={loading}
        onTriggerScrape={handleTriggerScrape}
        scraping={scraping}
        activeFeedName={datasource?.active || summary?.active_datasource}
      />

      {/* 2. Hero Section with Airplane Background & Floating Search */}
      <div id="flights">
        <HeroSearch
          origin={origin}
          dest={dest}
          onOriginChange={setOrigin}
          onDestChange={setDest}
          onSwap={handleSwap}
          onSearch={handleSearch}
          loading={loading}
        />
      </div>

      {/* 3. Main Content Container */}
      <main className="content-wrapper section-spacer">
        {/* Row 1: Active Deal Card (Left) + Where to Buy? (Right) */}
        <div className="grid-2col" id="deals">
          <ActiveDealCard
            routeData={routeData}
            onBookNow={handleBookNow}
          />
          <WhereToBuyCard
            platforms={routeData?.platforms}
            onBookNow={handleBookNow}
          />
        </div>

        {/* Row 2: Price Trend (Last 30 Days) (Left) + Best Time to Buy (Right) */}
        <div className="grid-2col" id="tracker">
          <PriceTrendCard
            trendData={routeData?.trend_30d}
            stats={routeData?.stats_30d}
          />
          <BestTimeToBuyCard
            bestTimeData={routeData?.best_time_to_buy}
          />
        </div>

        {/* Row 3: Our Services */}
        <div id="services">
          <OurServices />
        </div>

        {/* ==========================================================
            4. OFFICIAL MoSPI CPI TRANSPORTATION INDEX (APIx) SECTION
            ========================================================== */}
        <section id="apix-index" style={{ marginTop: '54px' }}>
          <div className="section-title-box">
            <div className="badge-pill-navy">
              <Sparkles size={14} color="#38bdf8" />
              <span>MoSPI DIID · SIH26056</span>
            </div>
            <h2 className="section-main-heading">
              Official Airfare Price Index (APIx) Intelligence
            </h2>
            <p className="section-sub-heading">
              High-frequency web-scraped CPI transportation index with Laspeyres fixed-basket weighting & DGCA schedule verification.
            </p>
          </div>

          {/* MoSPI KPI Cards */}
          <KpiCards summary={summary} />

          {/* 2-Column Analytical Charts: APIx Index Trend + Advance Window Curve */}
          <div className="grid-2col" id="market-curves" style={{ marginTop: '24px' }}>
            <IndexTrendChart
              indexData={indexData}
              frequency={frequency}
              onFrequencyChange={handleFrequencyChange}
            />
            <AdvanceWindowChart />
          </div>

          {/* Route Baseline Comparison Chart */}
          <div style={{ marginTop: '24px' }}>
            <RouteComparisonChart />
          </div>
        </section>

        {/* ==========================================================
            5. REAL-TIME LIVE INGESTION AUDIT TRAIL STREAM
            ========================================================== */}
        <section style={{ marginTop: '48px' }}>
          <RecentFaresTable
            fares={fares}
            selectedRoute={auditRoute}
            onRouteChange={handleAuditRouteChange}
            onScrape={handleTriggerScrape}
            scraping={scraping}
            totalRecords={summary?.total_records || routeData?.total_records}
          />
        </section>

        {/* ==========================================================
            6. PS 11-PORTAL COVERAGE HEALTH & STATUTORY COMPLIANCE
            ========================================================== */}
        <section style={{ marginTop: '28px', marginBottom: '32px' }}>
          <SourcesHealthTable sources={sources} />
        </section>
      </main>

      {/* 7. Footer (without social media & follow us) */}
      <Footer />

      {/* 8. Deep Inspection Modal */}
      <AuditModal
        isOpen={auditOpen}
        onClose={() => setAuditOpen(false)}
        fares={fares}
        selectedRoute={auditRoute}
        onScrape={handleTriggerScrape}
        scraping={scraping}
        totalRecords={summary?.total_records || routeData?.total_records}
      />
    </div>
  );
}
