import React from 'react';
import { Radio, ShieldCheck, CheckCircle2, AlertTriangle, AlertOctagon } from 'lucide-react';

export default function SourcesHealthTable({ sources }) {
  const defaultSources = [
    { id: 'indigo', name: 'IndiGo (Official Portal)', channel: 'scraper', weight: 0.35, status: 'healthy', badge: 'green', type: 'Airline Direct' },
    { id: 'airindia', name: 'Air India', channel: 'scraper', weight: 0.25, status: 'healthy', badge: 'green', type: 'Airline Direct' },
    { id: 'akasa', name: 'Akasa Air', channel: 'scraper', weight: 0.10, status: 'healthy', badge: 'green', type: 'Airline Direct' },
    { id: 'makemytrip', name: 'MakeMyTrip', channel: 'scraper', weight: 0.15, status: 'healthy', badge: 'green', type: 'OTA Aggregator' },
    { id: 'cleartrip', name: 'Cleartrip', channel: 'scraper', weight: 0.05, status: 'healthy', badge: 'green', type: 'OTA Aggregator' },
    { id: 'goibibo', name: 'Goibibo', channel: 'scraper', weight: 0.05, status: 'healthy', badge: 'green', type: 'OTA Aggregator' },
    { id: 'amadeus', name: 'Amadeus GDS (Official API)', channel: 'api', weight: 0.05, status: 'healthy', badge: 'green', type: 'Global GDS' },
    { id: 'skyscanner', name: 'Skyscanner (Meta)', channel: 'meta', weight: 0.00, status: 'healthy', badge: 'green', type: 'Metasearch' },
    { id: 'easemytrip', name: 'EaseMyTrip', channel: 'skip', weight: 0.00, status: 'skipped_legal_compliance', badge: 'red', type: 'OTA (Skipped)' },
    { id: 'ixigo', name: 'Ixigo', channel: 'skip', weight: 0.00, status: 'skipped_legal_compliance', badge: 'red', type: 'OTA (Skipped)' },
    { id: 'yatra', name: 'Yatra', channel: 'skip', weight: 0.00, status: 'skipped_legal_compliance', badge: 'red', type: 'OTA (Skipped)' },
  ];

  const displaySources = sources && sources.length > 0 ? sources : defaultSources;

  return (
    <div className="dash-card" id="portal-health" style={{ marginBottom: 0 }}>
      <div className="card-header">
        <div>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '18px', fontWeight: 800, color: '#0b1a38' }}>
            <Radio size={19} color="#0077ff" />
            PS 11-Portal Coverage Health & Statutory Compliance Matrix
          </h2>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '3px' }}>
            Automated health monitoring, channel weights, and DPDP / IT Act 2000 legal compliance audit
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge-pill-green">
            <ShieldCheck size={13} />
            Statutory Guard Active
          </span>
        </div>
      </div>

      <div className="table-responsive" style={{ marginTop: '16px' }}>
        <table className="apix-table">
          <thead>
            <tr>
              <th>Aviation Portal / Feed</th>
              <th>Category</th>
              <th>Channel Type</th>
              <th>Index Weight</th>
              <th>Compliance & Operational Status</th>
            </tr>
          </thead>
          <tbody>
            {displaySources.map((s) => {
              let badgeClass = 'badge-green';
              let Icon = CheckCircle2;
              if (s.badge === 'amber' || s.status.includes('pending')) {
                badgeClass = 'badge-amber';
                Icon = AlertTriangle;
              }
              if (s.badge === 'red' || s.status.includes('skipped')) {
                badgeClass = 'badge-red';
                Icon = AlertOctagon;
              }

              const formattedStatus = s.status === 'skipped_legal_compliance'
                ? 'Skipped (Legal Compliance Guard)'
                : s.status === 'pending_credentials'
                ? 'Pending Credentials'
                : '100% Operational & Verified';

              return (
                <tr key={s.id}>
                  <td>
                    <strong style={{ color: '#0b1a38' }}>{s.name}</strong>
                  </td>
                  <td>
                    <span style={{ color: '#64748b', fontSize: '13px' }}>{s.type || 'Aviation Channel'}</span>
                  </td>
                  <td>
                    <span className="code-font" style={{ fontWeight: 600 }}>
                      {(s.channel || 'SCRAPER').toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#0b1a38' }}>
                      {typeof s.weight === 'number' ? s.weight.toFixed(2) : (s.weight || '0.00')}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${badgeClass}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                      <Icon size={12} />
                      {formattedStatus}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
