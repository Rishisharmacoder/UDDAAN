import React from 'react';
import { PlaneTakeoff, MapPin, Calendar, Users, ArrowLeftRight, Search } from 'lucide-react';

const CITIES = [
  { code: 'DEL', name: 'New Delhi', label: 'New Delhi (DEL)' },
  { code: 'BOM', name: 'Mumbai', label: 'Mumbai (BOM)' },
  { code: 'BLR', name: 'Bengaluru', label: 'Bengaluru (BLR)' },
  { code: 'CCU', name: 'Kolkata', label: 'Kolkata (CCU)' },
  { code: 'HYD', name: 'Hyderabad', label: 'Hyderabad (HYD)' },
  { code: 'MAA', name: 'Chennai', label: 'Chennai (MAA)' }
];

export default function HeroSearch({
  origin,
  dest,
  onOriginChange,
  onDestChange,
  onSwap,
  departDate,
  onDepartDateChange,
  returnDate,
  onReturnDateChange,
  passengers,
  onPassengersChange,
  cabin,
  onCabinChange,
  onSearch,
  loading
}) {
  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <section className="hero-section" id="flights">
      <div className="hero-backdrop-aircraft" />
      <div className="content-wrapper">
        <div className="hero-content">
          <h1 className="hero-title">
            Track Flight Prices.<br />
            Book at the Best Time.
          </h1>
          <p className="hero-subtitle">
            Get real-time flight rates, price trends, and personalized recommendations to save more on your next trip.
          </p>
        </div>

        {/* Floating Search Bar */}
        <div className="search-card-float">
          {/* From */}
          <div className="search-field">
            <PlaneTakeoff size={18} className="search-field-icon" />
            <div className="search-field-content">
              <span className="search-field-label">From</span>
              <select
                className="search-field-select"
                value={origin}
                onChange={(e) => onOriginChange(e.target.value)}
              >
                {CITIES.map((c) => (
                  <option key={c.code} value={c.code} disabled={c.code === dest}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Swap Button */}
          <button className="swap-btn" onClick={onSwap} title="Swap Route" aria-label="Swap Route">
            <ArrowLeftRight size={15} />
          </button>

          {/* To */}
          <div className="search-field">
            <MapPin size={18} className="search-field-icon" />
            <div className="search-field-content">
              <span className="search-field-label">To</span>
              <select
                className="search-field-select"
                value={dest}
                onChange={(e) => onDestChange(e.target.value)}
              >
                {CITIES.map((c) => (
                  <option key={c.code} value={c.code} disabled={c.code === origin}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Departure Date */}
          <div className="search-field">
            <Calendar size={18} className="search-field-icon" />
            <div className="search-field-content">
              <span className="search-field-label">Departure Date</span>
              <input
                type="date"
                className="search-field-input"
                value={departDate}
                min={todayStr}
                onChange={(e) => onDepartDateChange(e.target.value)}
              />
            </div>
          </div>

          {/* Return Date */}
          <div className="search-field">
            <Calendar size={18} className="search-field-icon" />
            <div className="search-field-content">
              <span className="search-field-label">Return Date</span>
              <input
                type="date"
                className="search-field-input"
                value={returnDate}
                min={departDate || todayStr}
                onChange={(e) => onReturnDateChange(e.target.value)}
              />
            </div>
          </div>

          {/* Passengers */}
          <div className="search-field">
            <Users size={18} className="search-field-icon" />
            <div className="search-field-content">
              <span className="search-field-label">Travellers & Cabin</span>
              <select
                className="search-field-select"
                value={`${passengers}-${cabin || 'ECONOMY'}`}
                onChange={(e) => {
                  const parts = e.target.value.split('-');
                  onPassengersChange(Number(parts[0]));
                  if (onCabinChange) onCabinChange(parts[1]);
                }}
              >
                <option value="1-ECONOMY">1 Passenger, Economy</option>
                <option value="2-ECONOMY">2 Passengers, Economy</option>
                <option value="3-ECONOMY">3 Passengers, Economy</option>
                <option value="4-ECONOMY">4 Passengers, Economy</option>
                <option value="1-BUSINESS">1 Passenger, Business</option>
                <option value="2-BUSINESS">2 Passengers, Business</option>
              </select>
            </div>
          </div>

          {/* Search Button */}
          <button
            className="search-action-btn"
            onClick={onSearch}
            disabled={loading}
          >
            <Search size={16} />
            <span>{loading ? 'Searching...' : 'Search Flights'}</span>
          </button>
        </div>
      </div>
    </section>
  );
}
