import React from 'react';
import { ShieldCheck, RefreshCw, ExternalLink, Zap } from 'lucide-react';

export default function Header({ datasource, onRefresh, loading, onTriggerScrape, scraping }) {
  const isSeed = datasource?.active?.includes('seed');

  return (
    <header className="navbar">
      <div className="logo-section">
        <div className="logo-badge">APIx</div>
        <div className="title-box">
          <h1>
            Real-time Airfare Price Index for India
            <span style={{ fontSize: '11px', background: '#0369a1', padding: '3px 8px', borderRadius: '6px', textTransform: 'uppercase' }}>
              MoSPI DIID
            </span>
          </h1>
          <p>Automated High-Frequency Scraping & GDS Ingestion for CPI Transport Augmentation (SIH26056)</p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {/* Live Provenance Pill */}
        <div className="provenance-pill" title="Provenance Guarantee: Verified Active Data Source">
          <div
            className="pulse-dot"
            style={{
              background: isSeed ? 'var(--accent-amber)' : 'var(--accent-green)',
              boxShadow: isSeed ? '0 0 10px var(--accent-amber)' : '0 0 10px var(--accent-green)'
            }}
          />
          <span>
            <strong>Feed:</strong> {datasource?.active || 'Detecting feed...'}
          </span>
        </div>

        {/* Live Scrape CTA Button */}
        <button
          onClick={onTriggerScrape}
          className="cta-button"
          disabled={scraping}
          style={{
            background: 'linear-gradient(135deg, #059669, #10b981)',
            boxShadow: '0 2px 10px rgba(16, 185, 129, 0.3)'
          }}
          title="Instantly Scrape a Live Flight Quote into Database & CSV"
        >
          <Zap size={15} className={scraping ? 'animate-bounce' : ''} />
          {scraping ? 'Scraping Live...' : '⚡ Scrape Live Flight'}
        </button>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="cta-button"
          disabled={loading}
          style={{ background: '#1e293b', border: '1px solid #334155' }}
          title="Refresh All Real-time Data"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>

        <a
          href="/docs"
          target="_blank"
          rel="noreferrer"
          className="cta-button"
          style={{ textDecoration: 'none' }}
        >
          <ExternalLink size={15} />
          API Docs
        </a>
      </div>
    </header>
  );
}
