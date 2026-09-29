import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Plane } from 'lucide-react';

export default function RouteComparisonChart() {
  const chartData = {
    labels: ['DEL-BOM', 'DEL-BLR', 'BOM-BLR', 'DEL-CCU', 'BLR-HYD', 'MAA-DEL'],
    datasets: [
      {
        label: 'Average Baseline Market Fare (INR)',
        data: [6442, 7250, 4890, 5620, 3850, 6910],
        backgroundColor: '#0077ff',
        hoverBackgroundColor: '#005fcc',
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
          label: (ctx) => ` Baseline Rate: ₹${ctx.parsed.y.toLocaleString()}`
        }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#475569', font: { family: 'Plus Jakarta Sans', size: 12, weight: '700' } }
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
            <Plane size={18} color="#0077ff" />
            Route Baseline Price (6 DGCA Pairs)
          </h2>
          <p style={{ fontSize: '12px', color: '#64748b', marginTop: '3px' }}>
            Cross-corridor baseline fare distribution across primary Indian trunk aviation routes
          </p>
        </div>
      </div>
      <div style={{ height: '260px', position: 'relative', marginTop: '16px' }}>
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}
