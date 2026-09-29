import React from 'react';
import { Send, Zap, RefreshCw, ExternalLink } from 'lucide-react';

export default function Navbar({
  onRefresh,
  loading,
  onTriggerScrape,
  scraping,
  activeFeedName
}) {
  return (
    <header className="navbar-wrapper">
      <div className="content-wrapper">
        <nav className="navbar">
          {/* Logo with UDDAAN */}
          <div className="nav-brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="brand-icon">
              <Send size={20} style={{ transform: 'rotate(-45deg)', marginTop: '2px', marginLeft: '-2px' }} />
            </div>
            <div>
              <div className="brand-title">UDDAAN</div>
              <div className="brand-sub">Fly Smart. Pay Less.</div>
            </div>
          </div>

          {/* Navigation Links */}
          <ul className="nav-menu">
            <li><a className="nav-link active" href="#flights">Flights</a></li>
            <li><a className="nav-link" href="#tracker">Price Tracker</a></li>
            <li><a className="nav-link" href="#apix-index">MoSPI Index</a></li>
            <li><a className="nav-link" href="#audit-stream">Live Audit</a></li>
            <li><a className="nav-link" href="#portal-health">Portal Health</a></li>
          </ul>

          {/* Right Action Controls: Scrape, Refresh, API Docs & Feed Pill (NO Login/Sign Up) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* Live Feed Status */}
            <div className="nav-badge-pill" title="Verified Real Web Ingestion">
              <span className="nav-pulse-dot" />
              <span>{activeFeedName ? activeFeedName.split(' ')[0].toUpperCase() : 'LIVE FEED'}</span>
            </div>

            {/* Instant Live Scrape Button */}
            {onTriggerScrape && (
              <button
                onClick={onTriggerScrape}
                disabled={scraping}
                className="btn-nav-scrape"
                title="Trigger immediate live web scraper for current corridor"
              >
                <Zap size={14} className={scraping ? 'spin-icon' : ''} />
                <span>{scraping ? 'Scraping...' : '⚡ Scrape Live'}</span>
              </button>
            )}

            {/* Refresh Button */}
            {onRefresh && (
              <button
                onClick={onRefresh}
                disabled={loading}
                className="btn-nav-refresh"
                title="Refresh All Index & Corridor Metrics"
              >
                <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
                <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
              </button>
            )}

            {/* API Docs Link */}
            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="btn-nav-docs"
              title="Open OpenAPI / Swagger Documentation"
            >
              <ExternalLink size={14} />
              <span>Docs</span>
            </a>
          </div>
        </nav>
      </div>
    </header>
  );
}
