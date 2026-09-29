import React from 'react';
import { BarChart3, TrendingUp, TrendingDown, Percent } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler
);

export default function PriceTrendCard({ trendData, stats }) {
  const points = trendData && trendData.length > 0 ? trendData : [
    { date: '15 Apr', price: 7040 },
    { date: '18 Apr', price: 6920 },
    { date: '21 Apr', price: 7080 },
    { date: '24 Apr', price: 7190 },
    { date: '27 Apr', price: 6730 },
    { date: '30 Apr', price: 6640 },
    { date: '3 May', price: 6280 },
    { date: '6 May', price: 6410 },
    { date: '9 May', price: 6310 },
    { date: '12 May', price: 6020 },
    { date: '15 May', price: 5842 }
  ];

  const labels = points.map(p => p.date);
  const dataValues = points.map(p => p.price);
  const latestPrice = dataValues[dataValues.length - 1];

  const chartData = {
    labels,
    datasets: [
      {
        data: dataValues,
        borderColor: '#0077ff',
        borderWidth: 2.5,
        tension: 0.35,
        pointBackgroundColor: (context) => {
          return context.dataIndex === dataValues.length - 1 ? '#00a86b' : '#0077ff';
        },
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: (context) => {
          return context.dataIndex === dataValues.length - 1 ? 6 : 4;
        },
        pointHoverRadius: 7,
        fill: false
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0b1a38',
        titleFont: { size: 12, weight: 'bold' },
        bodyFont: { size: 13 },
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: (item) => ` Fare: ₹${item.raw.toLocaleString()}`
        }
      }
    },
    scales: {
      x: {
        grid: { display: true, color: '#f1f5f9' },
        ticks: { font: { size: 11 }, color: '#94a3b8' }
      },
      y: {
        grid: { display: true, color: '#f1f5f9' },
        ticks: {
          font: { size: 11, family: 'var(--font-mono)' },
          color: '#94a3b8',
          callback: (val) => `₹${val.toLocaleString()}`
        }
      }
    }
  };

  return (
    <div className="card-white">
      <div className="card-header-clean">
        <BarChart3 size={20} color="var(--accent-blue)" />
        <h3>Price Trend (Last 30 Days)</h3>
      </div>

      {/* Chart Canvas with Today Callout */}
      <div style={{ position: 'relative', height: '260px', width: '100%', marginTop: '10px' }}>
        <Line data={chartData} options={chartOptions} />

        {/* Highlight Callout Badge like the image */}
        <div style={{
          position: 'absolute',
          top: '35%',
          right: '25px',
          backgroundColor: '#00a86b',
          color: 'white',
          padding: '4px 10px',
          borderRadius: '6px',
          fontSize: '11px',
          fontWeight: 700,
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0, 168, 107, 0.3)',
          pointerEvents: 'none'
        }}>
          <div>Today</div>
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>₹ {latestPrice?.toLocaleString()}</div>
        </div>
      </div>

      {/* 3 Summary Stats Underneath */}
      <div className="trend-stats-row">
        {/* Highest Price */}
        <div className="trend-stat-box">
          <div className="trend-stat-icon" style={{ background: '#fef2f2', color: '#ef4444' }}>
            <TrendingUp size={16} />
          </div>
          <div>
            <div className="trend-stat-label">Highest Price</div>
            <div className="trend-stat-val">₹ {stats?.highest_price?.toLocaleString() || '7,650'}</div>
            <div style={{ fontSize: '10px', color: '#94a3b8' }}>({stats?.highest_date || '22 Apr 2025'})</div>
          </div>
        </div>

        {/* Lowest Price */}
        <div className="trend-stat-box">
          <div className="trend-stat-icon" style={{ background: '#ecfdf5', color: '#00a86b' }}>
            <TrendingDown size={16} />
          </div>
          <div>
            <div className="trend-stat-label">Lowest Price</div>
            <div className="trend-stat-val">₹ {stats?.lowest_price?.toLocaleString() || '5,640'}</div>
            <div style={{ fontSize: '10px', color: '#94a3b8' }}>({stats?.lowest_date || '12 May 2025'})</div>
          </div>
        </div>

        {/* Price Drop */}
        <div className="trend-stat-box">
          <div className="trend-stat-icon" style={{ background: '#ecfdf5', color: '#00a86b' }}>
            <Percent size={14} />
          </div>
          <div>
            <div className="trend-stat-label">Price Drop</div>
            <div className="trend-stat-val" style={{ color: '#00a86b' }}>
              ↓ {stats?.drop_pct || 28}%
            </div>
            <div style={{ fontSize: '10px', color: '#94a3b8' }}>(from highest)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
