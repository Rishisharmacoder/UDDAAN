import React from 'react';
import { Lightbulb, Calendar, TrendingUp, CheckCircle2 } from 'lucide-react';

export default function BestTimeToBuyCard({ bestTimeData }) {
  const idealWindow = bestTimeData?.ideal_window || '10 – 20 days before departure';
  const recommendation = bestTimeData?.recommendation || 'For this route, prices are usually lowest around 10–20 days before your travel date.';
  const prediction = bestTimeData?.prediction || 'Prices are expected to increase by 5–10% in the next 7 days due to higher demand.';

  return (
    <div className="card-white" id="best-time">
      <div className="card-header-clean">
        <Lightbulb size={20} color="var(--accent-blue)" />
        <h3>Best Time to Buy</h3>
      </div>

      {/* Ideal Time to Buy Green Banner */}
      <div className="ideal-time-banner">
        <div className="banner-icon-circle">
          <Calendar size={18} />
        </div>
        <div>
          <div className="ideal-time-title">
            Ideal time to Buy: {idealWindow}
          </div>
          <div className="ideal-time-desc">
            {recommendation}
          </div>
        </div>
      </div>

      {/* Price Prediction Box */}
      <div className="prediction-box">
        <div className="prediction-title">
          <TrendingUp size={16} />
          <span>Price Prediction</span>
        </div>
        <div className="prediction-desc">
          {prediction}
        </div>
      </div>

      {/* Quick Tips */}
      <div>
        <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-main)', marginBottom: '10px' }}>
          Quick Tips
        </div>
        <div className="quick-tips-list">
          <div className="quick-tip-item">
            <CheckCircle2 size={16} color="#00a86b" />
            <span>Book 10–20 days in advance for best rates</span>
          </div>
          <div className="quick-tip-item">
            <CheckCircle2 size={16} color="#00a86b" />
            <span>Avoid peak travel dates (weekends & holidays)</span>
          </div>
          <div className="quick-tip-item">
            <CheckCircle2 size={16} color="#00a86b" />
            <span>Use price alerts to track changes</span>
          </div>
          <div className="quick-tip-item">
            <CheckCircle2 size={16} color="#00a86b" />
            <span>Consider nearby airports for more options</span>
          </div>
        </div>
      </div>
    </div>
  );
}
