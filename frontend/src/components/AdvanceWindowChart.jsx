import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Clock } from 'lucide-react';

export default function AdvanceWindowChart() {
  const chartData = {
    labels: ['T+1 (Next Day)', 'T+7 (1 Week)', 'T+15 (2 Weeks)', 'T+30 (1 Month)', 'T+45 (Long Range)'],
    datasets: [
      {
        label: 'Average Price (INR)',
        data: [9340, 7410, 6442, 5670, 5280],
        backgroundColor: [
          'rgba(239, 68, 68, 0.85)',
          'rgba(245, 158, 11, 0.85)',
          'rgba(2, 132, 199, 0.85)',
          'rgba(0, 168, 107, 0.85)',
          'rgba(99, 102, 241, 0.85)'
        ],
        borderRadius: 8,
        borderWidth: 0
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
        borderColor: '#1e293b',
        borderWidth: 1,
        titleColor: '#f9fafb',
        bodyColor: '#38bdf8',
        bodyFont: { weight: 'bold', family: 'JetBrains Mono' },
        padding: 10,
        callbacks: {
          label: (ctx) => ` Average Fare: ₹${ctx.parsed.y.toLocaleString()}`
        }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11, weight: '600' } }
      },
      y: {
        grid: { color: '#f1f5f9' },
        ticks: {
          color: '#64748b',
          font: { family: 'Plus Jakarta Sans', size: 11 },
          callback: (val) => `₹${val / 1000}k`
        }
      }
    }
  };

  return (
    <div className="dash-card">
      <div className="card-header">
        <div>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '17px', fontWeight: 800, color: '#0b1a38' }}>
            <Clock size={18} color="#d97706" />
            Advance Window Price Curve (INR)
          </h2>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '3px' }}>
            Averaged booking lead time progression showing premium on last-minute purchases
          </p>
        </div>
      </div>
      <div style={{ height: '310px', position: 'relative', marginTop: '16px' }}>
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}
