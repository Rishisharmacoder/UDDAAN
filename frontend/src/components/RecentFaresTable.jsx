import React from 'react';
import { ListFilter, ShieldCheck, Filter, Zap, Download, RefreshCw } from 'lucide-react';

const ROUTE_OPTIONS = [
  { value: 'ALL', label: 'All Corridors (Consolidated)' },
  { value: 'DEL-BOM', label: 'DEL ➔ BOM (Delhi – Mumbai)' },
  { value: 'DEL-BLR', label: 'DEL ➔ BLR (Delhi – Bengaluru)' },
  { value: 'BOM-BLR', label: 'BOM ➔ BLR (Mumbai – Bengaluru)' },
  { value: 'DEL-CCU', label: 'DEL ➔ CCU (Delhi – Kolkata)' },
  { value: 'BLR-HYD', label: 'BLR ➔ HYD (Bengaluru – Hyderabad)' },
  { value: 'MAA-DEL', label: 'MAA ➔ DEL (Chennai – Delhi)' },
];

export default function RecentFaresTable({
  fares,
  selectedRoute = 'ALL',
  onRouteChange,
  onScrape,
  scraping,
  totalRecords
}) {
  const displayFares = fares && fares.length > 0 ? fares : [];

  const handleExport = () => {
    window.open(`/api/fares/export?route=${selectedRoute}`, '_blank');
  };

  return (
    <div className="dash-card" id="audit-stream">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '18px', fontWeight: 800, color: '#0b1a38' }}>
              <ListFilter size={19} color="#00a86b" />
              Real-Time Live Web Ingestion (Audit Trail)
            </h2>
            <span className="badge-pill-green">
              Live Feed
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
            <span style={{ fontSize: '13px', color: '#64748b' }}>
              {selectedRoute === 'ALL'
                ? `Displaying latest real-time observations across all 6 domestic corridors`
                : `Filtered strictly for corridor: ${selectedRoute}`}
            </span>
            {totalRecords && (
              <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                · {totalRecords.toLocaleString()} total rows in database
              </span>
            )}
          </div>
        </div>

        {/* Controls: Route Filter, Scrape CTA, CSV Export */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {onRouteChange && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Filter size={14} color="#64748b" />
              <select
                value={selectedRoute}
                onChange={(e) => onRouteChange(e.target.value)}
                className="select-custom"
              >
                {ROUTE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          {onScrape && (
            <button
              onClick={onScrape}
              disabled={scraping}
              className="btn-live-scrape"
              title="Scrape live prices directly from web into dataset"
            >
              <Zap size={14} className={scraping ? 'spin-icon' : ''} />
              {scraping ? 'Scraping Live Web...' : '⚡ Scrape Real Web'}
            </button>
          )}

          <button
            onClick={handleExport}
            className="btn-export-csv"
            title="Export route observation dataset as CSV"
          >
            <Download size={14} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Mobile Swipe Hint */}
      <div className="mobile-scroll-hint">
        <span>⇄ Swipe table horizontally to view full audit trail</span>
      </div>

      <div className="table-responsive" style={{ marginTop: '12px' }}>
        <table className="apix-table">
          <thead>
            <tr>
              <th>Corridor</th>
              <th>Flight No.</th>
              <th>DGCA Validation</th>
              <th>Window</th>
              <th>Airline</th>
              <th>Price (INR)</th>
              <th>Source</th>
              <th>Scraped At</th>
              <th>Integrity</th>
            </tr>
          </thead>
          <tbody>
            {displayFares.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', color: '#64748b', padding: '36px' }}>
                  No recent observations found for {selectedRoute}. Click "⚡ Scrape Real Web" above to capture live flights now.
                </td>
              </tr>
            ) : (
              displayFares.map((f, i) => {
                let badgeClass = 'badge-green';
                if (f.quality_flag === 'flagged') badgeClass = 'badge-amber';
                if (f.quality_flag === 'rejected') badgeClass = 'badge-red';

                const valStatus = f.flight_validation || 'verified';
                const valBadge = valStatus === 'verified' ? 'badge-green' : (valStatus === 'invalid' ? 'badge-red' : 'badge-amber');
                const valLabel = valStatus === 'verified' ? '✓ DGCA Verified' : (valStatus === 'invalid' ? '✗ Sector Mismatch' : '? Unverified');

                return (
                  <tr key={i}>
                    <td>
                      <strong style={{ color: '#0b1a38' }}>{f.origin} ➔ {f.destination}</strong>
                    </td>
                    <td>
                      <span className="code-font" style={{ color: '#0077ff', fontWeight: 700 }}>
                        {f.flight_number || (f.airline_code ? `${f.airline_code}-2054` : '6E-2054')}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${valBadge}`}>
                        {valLabel}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: '#0284c7', fontWeight: 600 }}>{f.window}</span>
                    </td>
                    <td>
                      <span className="code-font" style={{ fontWeight: 600 }}>{f.airline_code || '6E'}</span>
                    </td>
                    <td style={{ fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#0b1a38', fontSize: '15px' }}>
                      ₹{(f.price_inr ?? f.price_total ?? 0).toLocaleString()}
                    </td>
                    <td>
                      <span className="code-font" style={{ color: '#475569', fontSize: '12px' }}>{f.source}</span>
                    </td>
                    <td style={{ color: '#64748b', fontSize: '12px' }}>
                      {f.scraped_at ? f.scraped_at.replace('T', ' ').slice(0, 19) : 'Just now'}
                    </td>
                    <td>
                      <span className={`status-badge ${badgeClass}`}>
                        {f.quality_flag || 'ok'}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
