import React from 'react';
import { Plane, TrendingUp, Calendar, Headphones, Briefcase, Check } from 'lucide-react';

export default function OurServices() {
  return (
    <section className="services-section" id="services">
      <div className="section-heading">
        <Plane size={22} color="var(--accent-blue)" />
        <span>Our Services</span>
      </div>

      <div className="services-grid">
        {/* 1. Price Tracking */}
        <div className="service-card">
          <div className="service-icon-box">
            <TrendingUp size={22} />
          </div>
          <h4 className="service-title">Price Tracking</h4>
          <p className="service-desc">
            Get real-time updates on flight prices and set alerts for your preferred route.
          </p>
        </div>

        {/* 2. Flexible Dates */}
        <div className="service-card">
          <div className="service-icon-box" style={{ background: '#ecfdf5', color: '#00a86b' }}>
            <Calendar size={22} />
          </div>
          <h4 className="service-title">Flexible Dates</h4>
          <p className="service-desc">
            Find the cheapest dates with our flexible search calendar.
          </p>
        </div>

        {/* 3. Compare Airlines */}
        <div className="service-card">
          <div className="service-icon-box" style={{ background: '#f0f7ff', color: '#0077ff' }}>
            <Plane size={22} />
          </div>
          <h4 className="service-title">Compare Airlines</h4>
          <p className="service-desc">
            See prices from multiple airlines and choose the best deal.
          </p>
        </div>

        {/* 4. 24/7 Support */}
        <div className="service-card">
          <div className="service-icon-box" style={{ background: '#f0f7ff', color: '#0284c7' }}>
            <Headphones size={22} />
          </div>
          <h4 className="service-title">24/7 Support</h4>
          <p className="service-desc">
            We're here to help anytime, anywhere.
          </p>
        </div>

        {/* 5. Extra Services */}
        <div className="service-card">
          <div className="service-icon-box" style={{ background: '#eff6ff', color: '#1d4ed8' }}>
            <Briefcase size={22} />
          </div>
          <h4 className="service-title">Extra Services</h4>
          <ul className="service-checklist">
            <li><Check size={12} color="#00a86b" /> Meal Selection</li>
            <li><Check size={12} color="#00a86b" /> Extra Baggage</li>
            <li><Check size={12} color="#00a86b" /> Seat Selection</li>
            <li><Check size={12} color="#00a86b" /> Travel Insurance</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
