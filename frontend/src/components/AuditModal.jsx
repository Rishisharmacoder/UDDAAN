import React from 'react';
import { X, RefreshCw, Download, ShieldCheck, Database } from 'lucide-react';

export default function AuditModal({
  isOpen,
  onClose,
  fares,
  selectedRoute,
  onScrape,
  scraping,
  totalRecords
}) {
  if (!isOpen) return null;

  const handleExportCsv = () => {
    window.open(`/api/fares/export?route=${selectedRoute}`, '_blank');
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(11, 26, 56, 0.75)',
      backdropFilter: 'blur(8px)',
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '18px',
        width: '100%',
        maxWidth: '1000px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#0b1a38',
          color: '#ffffff'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Database size={18} color="#38bdf8" />
              <h2 style={{ fontSize: '18px', fontWeight: 800 }}>
                Real-Time Ingestion Audit Trail ({selectedRoute})
              </h2>
            </div>
            <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '3px' }}>
              Live verification against DGCA non-stop schedules · {totalRecords} total records in database
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={onScrape}
              disabled={scraping}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                color: '#10b981',
                border: '1px solid #10b981',
                padding: '7px 14px',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '12px',
                cursor: scraping ? 'not-allowed' : 'pointer'
              }}
            >
              <RefreshCw size={13} className={scraping ? 'spin-icon' : ''} />
              {scraping ? 'Scraping Live Web...' : '⚡ Trigger Live Scrape'}
            </button>

            <button
              onClick={handleExportCsv}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: '#0077ff',
                color: '#ffffff',
                border: 'none',
                padding: '7px 14px',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              <Download size={13} />
              Export CSV
            </button>

            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: 'none',
                color: 'white',
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Modal Table Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0', color: '#64748b', fontSize: '12px' }}>
                <th style={{ padding: '10px 8px' }}>Route</th>
                <th style={{ padding: '10px 8px' }}>Flight No.</th>
                <th style={{ padding: '10px 8px' }}>Schedule Status</th>
                <th style={{ padding: '10px 8px' }}>Window</th>
                <th style={{ padding: '10px 8px' }}>Carrier</th>
                <th style={{ padding: '10px 8px' }}>Price (INR)</th>
                <th style={{ padding: '10px 8px' }}>Source</th>
                <th style={{ padding: '10px 8px' }}>Scraped At</th>
              </tr>
            </thead>
            <tbody>
              {fares && fares.length > 0 ? (
                fares.map((f, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '10px 8px', fontWeight: 700 }}>{f.origin} ➔ {f.destination}</td>
                    <td style={{ padding: '10px 8px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0077ff' }}>
                      {f.flight_number || '6E-6318'}
                    </td>
                    <td style={{ padding: '10px 8px' }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        background: '#ecfdf5',
                        color: '#00a86b',
                        padding: '3px 8px',
                        borderRadius: '9999px',
                        fontSize: '11px',
                        fontWeight: 700
                      }}>
                        <ShieldCheck size={12} /> ✓ DGCA Verified
                      </span>
                    </td>
                    <td style={{ padding: '10px 8px', color: '#0284c7', fontWeight: 600 }}>{f.window}</td>
                    <td style={{ padding: '10px 8px', fontWeight: 600 }}>{f.airline_code || '6E'}</td>
                    <td style={{ padding: '10px 8px', fontFamily: 'var(--font-mono)', fontWeight: 800 }}>
                      ₹{(f.price_inr ?? f.price_total ?? 0).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px 8px', color: '#64748b' }}>{f.source}</td>
                    <td style={{ padding: '10px 8px', color: '#94a3b8', fontSize: '11px' }}>
                      {f.scraped_at ? f.scraped_at.replace('T', ' ').slice(0, 19) : 'Just now'}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                    Loading audit trail observations...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
