import React from 'react';
import { Plane, Download, RefreshCw, Layers, ShieldCheck, TrendingUp, IndianRupee } from 'lucide-react';

const ROUTES_LIST = [
  { id: 'ALL', label: 'All Routes (Consolidated)', orig: 'ALL', dest: 'ALL' },
  { id: 'DEL-BOM', label: 'DEL ➔ BOM (Delhi – Mumbai)', orig: 'DEL', dest: 'BOM' },
  { id: 'DEL-BLR', label: 'DEL ➔ BLR (Delhi – Bengaluru)', orig: 'DEL', dest: 'BLR' },
  { id: 'BOM-BLR', label: 'BOM ➔ BLR (Mumbai – Bengaluru)', orig: 'BOM', dest: 'BLR' },
  { id: 'DEL-CCU', label: 'DEL ➔ CCU (Delhi – Kolkata)', orig: 'DEL', dest: 'CCU' },
  { id: 'BLR-HYD', label: 'BLR ➔ HYD (Bengaluru – Hyderabad)', orig: 'BLR', dest: 'HYD' },
  { id: 'MAA-DEL', label: 'MAA ➔ DEL (Chennai – Delhi)', orig: 'MAA', dest: 'DEL' },
];

export default function RouteSelector({
  selectedRoute,
  onRouteChange,
  routesStats,
  onScrapeRoute,
  scraping,
  totalRecords
}) {
  const currentStats = routesStats?.find(s => s.route === selectedRoute);

  const handleDownloadCsv = () => {
    const url = selectedRoute === 'ALL'
      ? '/api/fares/export'
      : `/api/fares/export?route=${selectedRoute}`;
    window.open(url, '_blank');
  };

  return (
    <div className="dash-card" style={{ marginBottom: '24px', border: '1px solid var(--border-highlight)' }}>
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <h2>
            <Plane size={20} color="var(--accent-cyan)" />
            Route Corridor Selector & Live Ingestion Hub
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Select any flight corridor to filter time-series audit trail, view sector analytics, or trigger live web scraping.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={() => onScrapeRoute(selectedRoute)}
            disabled={scraping}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              color: 'var(--accent-green)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              padding: '9px 16px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '13px',
              cursor: scraping ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <RefreshCw size={15} className={scraping ? 'spin-icon' : ''} />
            {scraping ? 'Scraping Live Web...' : `⚡ Scrape Real Web (${selectedRoute === 'ALL' ? 'Auto-Cycle' : selectedRoute})`}
          </button>

          <button
            onClick={handleDownloadCsv}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: 'rgba(6, 182, 212, 0.12)',
              color: 'var(--accent-cyan)',
              border: '1px solid rgba(6, 182, 212, 0.35)',
              padding: '9px 16px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <Download size={15} />
            Export Route CSV
          </button>
        </div>
      </div>

      {/* Route Switcher Buttons */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        marginTop: '16px',
        paddingTop: '16px',
        borderTop: '1px solid var(--border)'
      }}>
        {ROUTES_LIST.map((r) => {
          const isSelected = selectedRoute === r.id;
          return (
            <button
              key={r.id}
              onClick={() => onRouteChange(r.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: isSelected ? 700 : 500,
                border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid var(--border)',
                background: isSelected ? 'rgba(6, 182, 212, 0.15)' : 'var(--bg-main)',
                color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isSelected ? 'var(--accent-cyan)' : 'var(--text-muted)'
              }} />
              {r.label}
            </button>
          );
        })}
      </div>

      {/* Selected Route Real-Time Metrics Strip */}
      {selectedRoute !== 'ALL' && currentStats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '12px',
          marginTop: '18px',
          padding: '14px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: '10px',
          border: '1px solid var(--border)'
        }}>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Active Route Sector
            </div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              {currentStats.label}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
              <ShieldCheck size={13} /> DGCA Verified Corridor
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Latest Live Market Fare
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
              ₹{currentStats.latest_fare?.toLocaleString() || 'N/A'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Flight: <span className="code-font" style={{ color: 'var(--accent-green)' }}>{currentStats.latest_flight}</span>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Average Market Fare
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
              ₹{currentStats.avg_fare?.toLocaleString() || 'N/A'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Min: ₹{currentStats.min_fare?.toLocaleString()} · Max: ₹{currentStats.max_fare?.toLocaleString()}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Total Real Observations
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
              {currentStats.total_records?.toLocaleString()}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--accent-green)', marginTop: '2px' }}>
              100% Real Live Ingested
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
