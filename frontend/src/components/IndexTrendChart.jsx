import React from 'react';
import { Line } from 'react-chartjs-2';
import { Activity } from 'lucide-react';

export default function IndexTrendChart({ indexData, frequency = 'monthly', onFrequencyChange }) {
  const labels = indexData?.labels || ['2026-07', '2026-08', '2026-09'];
  const values = indexData?.values || [100.0, 105.06, 105.75];

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: `APIx ${frequency.toUpperCase()} Index`,
        data: values,
        borderColor: '#0077ff',
        backgroundColor: 'rgba(0, 119, 255, 0.08)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#0077ff',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Base Period Invariant (100.00)',
        data: Array(labels.length).fill(100.0),
        borderColor: '#f59e0b',
        borderDash: [6, 6],
        borderWidth: 1.5,
        pointRadius: 0,
        fill: false
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: '#475569', font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' } }
      },
      tooltip: {
        backgroundColor: '#0b1a38',
        borderColor: '#1e293b',
        borderWidth: 1,
        titleColor: '#f9fafb',
        bodyColor: '#38bdf8',
        bodyFont: { weight: 'bold', family: 'JetBrains Mono' },
        padding: 10,
        callbacks: {
          label: (context) => ` ${context.dataset.label}: ${context.parsed.y.toFixed(2)}`
        }
      }
    },
    scales: {
      x: {
        grid: { color: '#f1f5f9' },
        ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' } }
      },
      y: {
        grid: { color: '#f1f5f9' },
        ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' } }
      }
    }
  };

  return (
    <div className="dash-card">
      <div className="card-header">
        <div>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '17px', fontWeight: 800, color: '#0b1a38' }}>
            <Activity size={18} color="#0077ff" />
            APIx Airfare Price Index Trend (Laspeyres Fixed Basket)
          </h2>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '3px' }}>
            Official MoSPI DIID benchmark relative to Base Period (July 2026 = 100.00)
          </p>
        </div>

        <div className="btn-toggle-group">
          <button
            className={`toggle-btn ${frequency === 'monthly' ? 'active' : ''}`}
            onClick={() => onFrequencyChange('monthly')}
          >
            Monthly
          </button>
          <button
            className={`toggle-btn ${frequency === 'weekly' ? 'active' : ''}`}
            onClick={() => onFrequencyChange('weekly')}
          >
            Weekly
          </button>
          <button
            className={`toggle-btn ${frequency === 'daily' ? 'active' : ''}`}
            onClick={() => onFrequencyChange('daily')}
          >
            Daily
          </button>
        </div>
      </div>

      <div style={{ height: '310px', position: 'relative', marginTop: '16px' }}>
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}
