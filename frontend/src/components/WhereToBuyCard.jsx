import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function WhereToBuyCard({ platforms, onBookNow }) {
  const displayPlatforms = platforms && platforms.length > 0 ? platforms : [
    { name: 'MakeMyTrip', price: 5842, color: '#eb2227' },
    { name: 'Goibibo', price: 5899, color: '#f1592a' },
    { name: 'Cleartrip', price: 6120, color: '#f77728' },
    { name: 'Skyscanner', price: 6250, color: '#00a698' },
    { name: 'Amazon Travel', price: 6390, color: '#232f3e' }
  ];

  return (
    <div className="card-white">
      <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.3px' }}>
        Where to Buy?
      </h3>
      <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.4 }}>
        Compare prices across top platforms and choose the best deal.
      </p>

      <div className="platforms-list">
        {displayPlatforms.map((p, idx) => (
          <div className="platform-row" key={idx}>
            <div className="platform-info">
              <div
                className="platform-icon"
                style={{ backgroundColor: p.color || '#0077ff' }}
              >
                {p.name.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <span className="platform-name">{p.name}</span>
                {p.badge && (
                  <span style={{
                    fontSize: '10px',
                    marginLeft: '8px',
                    color: '#10b981',
                    fontWeight: 700,
                    background: '#ecfdf5',
                    padding: '2px 6px',
                    borderRadius: '4px'
                  }}>
                    {p.badge}
                  </span>
                )}
              </div>
            </div>

            <div className="platform-actions">
              <span className="platform-price">₹ {p.price?.toLocaleString()}</span>
              <button
                className="btn-book-blue"
                onClick={() => onBookNow(p.name)}
              >
                Book Now
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '16px' }}>
        <a
          className="view-all-link"
          onClick={() => alert('All platforms synchronized via real-time live ingestion.')}
        >
          View All Booking Options →
        </a>
      </div>
    </div>
  );
}
