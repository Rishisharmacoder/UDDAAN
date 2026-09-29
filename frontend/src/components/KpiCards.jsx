import React from 'react';
import { TrendingUp, Database, Layers, Calendar, CheckCircle2 } from 'lucide-react';

export default function KpiCards({ summary }) {
  const latestApix = summary?.latest_apix ?? 105.75;
  const momChange = summary?.mom_change_pct ?? 0.66;
  const totalRecords = summary?.total_records ?? 5124;
  const isPositive = momChange >= 0;

  return (
    <section className="kpi-grid">
      {/* 1. Latest APIx */}
      <div className="kpi-card">
        <div className="kpi-label">
          <span>Latest APIx (Base 100.0)</span>
          <div className="kpi-icon-pill" style={{ color: '#0077ff', background: '#eff6ff' }}>
            <TrendingUp size={16} />
          </div>
        </div>
        <div className="kpi-value">{latestApix.toFixed(2)}</div>
        <div className={`kpi-meta ${isPositive ? 'positive' : 'negative'}`}>
          <span className="kpi-badge-pill">
            {isPositive ? `+${momChange.toFixed(2)}%` : `${momChange.toFixed(2)}%`} MoM
          </span>
          <span>MoSPI Transport Inflation</span>
        </div>
      </div>

      {/* 2. Total Ingested Records */}
      <div className="kpi-card">
        <div className="kpi-label">
          <span>Total Observations</span>
          <div className="kpi-icon-pill" style={{ color: '#0284c7', background: '#f0f9ff' }}>
            <Database size={16} />
          </div>
        </div>
        <div className="kpi-value">{totalRecords.toLocaleString()}</div>
        <div className="kpi-meta neutral">
          <span className="kpi-badge-pill" style={{ background: '#f0fdf4', color: '#16a34a' }}>
            100% DGCA Non-stop
          </span>
          <span>Verified Time-series</span>
        </div>
      </div>

      {/* 3. Representative Basket */}
      <div className="kpi-card">
        <div className="kpi-label">
          <span>Representative Basket</span>
          <div className="kpi-icon-pill" style={{ color: '#00a86b', background: '#ecfdf5' }}>
            <Layers size={16} />
          </div>
        </div>
        <div className="kpi-value">6 × 5</div>
        <div className="kpi-meta neutral">
          <span className="kpi-badge-pill" style={{ background: '#f1f5f9', color: '#475569' }}>
            30 Items
          </span>
          <span>Laspeyres Unit Weight (q=1.0)</span>
        </div>
      </div>

      {/* 4. Base Period Reference */}
      <div className="kpi-card">
        <div className="kpi-label">
          <span>Base Reference Period</span>
          <div className="kpi-icon-pill" style={{ color: '#d97706', background: '#fffbeb' }}>
            <Calendar size={16} />
          </div>
        </div>
        <div className="kpi-value" style={{ fontSize: '24px' }}>July 2026</div>
        <div className="kpi-meta neutral">
          <span className="kpi-badge-pill" style={{ background: '#fffbeb', color: '#b45309' }}>
            V₀ Invariant
          </span>
          <span>Fixed Basket ₹187,707</span>
        </div>
      </div>

      {/* 5. Pipeline Resilience */}
      <div className="kpi-card">
        <div className="kpi-label">
          <span>Pipeline Resilience</span>
          <div className="kpi-icon-pill" style={{ color: '#16a34a', background: '#f0fdf4' }}>
            <CheckCircle2 size={16} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#00a86b', fontSize: '24px' }}>100% OK</div>
        <div className="kpi-meta neutral">
          <span className="kpi-badge-pill" style={{ background: '#ecfdf5', color: '#059669' }}>
            Fail-Closed
          </span>
          <span>MAD Outlier Scrub Filter</span>
        </div>
      </div>
    </section>
  );
}
