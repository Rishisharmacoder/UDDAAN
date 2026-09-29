import React from 'react';
import { ArrowDown, Plane } from 'lucide-react';

export default function ActiveDealCard({ routeData, onBookNow }) {
  if (!routeData) return null;

  const {
    origin,
    origin_city,
    destination,
    dest_city,
    current_lowest_price,
    was_price,
    discount_pct,
    flight_depart,
    flight_return
  } = routeData;

  return (
    <div className="card-white" id="tracker">
      {/* Header */}
      <div className="deal-header">
        <div>
          <h2 className="deal-title">
            {origin_city} ({origin}) → {dest_city} ({destination})
          </h2>
          <div className="deal-meta">
            Round Trip • 15 May 2025 – 18 May 2025 • 1 Passenger • Economy
          </div>
        </div>
        <span className="badge-best-price">Best Price Right Now</span>
      </div>

      {/* Split Content */}
      <div className="deal-split">
        {/* Left: Price Box */}
        <div className="price-box">
          <div>
            <span className="price-box-label">Current Lowest Price</span>
            <div className="price-main">
              <span>₹ {current_lowest_price?.toLocaleString()}</span>
              <span className="price-discount-tag">
                <ArrowDown size={14} /> {discount_pct || 12}%
              </span>
            </div>
            <div className="price-was">
              (was ₹ {was_price?.toLocaleString() || (current_lowest_price * 1.15).toFixed(0)})
            </div>
          </div>

          <div>
            <button className="btn-book-green" onClick={() => onBookNow('MakeMyTrip')}>
              Book Now
            </button>
            <div className="price-caption">
              Price may change. Real-time live market fare.
            </div>
          </div>
        </div>

        {/* Right: Flight Segments */}
        <div className="flight-segments">
          {/* Depart Segment */}
          <div className="segment-item">
            <div className="segment-top">
              <div className="segment-carrier">
                <div className="carrier-logo-badge">
                  <Plane size={14} />
                </div>
                <div>
                  <div className="carrier-name">
                    {flight_depart?.airline || 'IndiGo'}
                  </div>
                  <div className="carrier-fnum">
                    {flight_depart?.flight_number || '6E-6318'}
                  </div>
                </div>
              </div>
              <span className="segment-date-tag">Depart 15 May 2025</span>
            </div>

            <div className="timeline-row">
              <div className="time-col">
                <span className="time-val">{flight_depart?.depart_time || '08:20'}</span>
                <span className="airport-code">{origin}</span>
                <span className="city-name">{origin_city}</span>
              </div>

              <div className="path-col">
                <span className="path-duration">{flight_depart?.duration || '2h 10m'}</span>
                <div className="path-line" />
                <span className="path-stops">✓ Non-stop</span>
              </div>

              <div className="time-col" style={{ textAlign: 'right' }}>
                <span className="time-val">{flight_depart?.arrival_time || '10:30'}</span>
                <span className="airport-code">{destination}</span>
                <span className="city-name">{dest_city}</span>
              </div>
            </div>
          </div>

          {/* Return Segment */}
          <div className="segment-item">
            <div className="segment-top">
              <div className="segment-carrier">
                <div className="carrier-logo-badge" style={{ background: '#0284c7' }}>
                  <Plane size={14} />
                </div>
                <div>
                  <div className="carrier-name">
                    {flight_return?.airline || 'IndiGo'}
                  </div>
                  <div className="carrier-fnum">
                    {flight_return?.flight_number || '6E-675'}
                  </div>
                </div>
              </div>
              <span className="segment-date-tag">Return 18 May 2025</span>
            </div>

            <div className="timeline-row">
              <div className="time-col">
                <span className="time-val">{flight_return?.depart_time || '11:25'}</span>
                <span className="airport-code">{destination}</span>
                <span className="city-name">{dest_city}</span>
              </div>

              <div className="path-col">
                <span className="path-duration">{flight_return?.duration || '2h 05m'}</span>
                <div className="path-line" />
                <span className="path-stops">✓ Non-stop</span>
              </div>

              <div className="time-col" style={{ textAlign: 'right' }}>
                <span className="time-val">{flight_return?.arrival_time || '13:30'}</span>
                <span className="airport-code">{origin}</span>
                <span className="city-name">{origin_city}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
