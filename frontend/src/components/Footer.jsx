import React from 'react';
import { Send, Users, ShieldCheck, Headphones } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="footer-wrapper">
      <div className="content-wrapper">
        <div className="footer-top">
          {/* Brand */}
          <div className="nav-brand">
            <div className="brand-icon">
              <Send size={20} style={{ transform: 'rotate(-45deg)', marginTop: '2px', marginLeft: '-2px' }} />
            </div>
            <div>
              <div className="brand-title">UDDAAN</div>
              <div className="brand-sub">Fly Smart. Pay Less.</div>
            </div>
          </div>

          {/* Center Stats */}
          <div className="footer-stats-row">
            <div className="footer-stat-item">
              <Users size={18} color="#0077ff" />
              <div>
                <div className="footer-stat-title">1M+</div>
                <div className="footer-stat-sub">Happy Travelers</div>
              </div>
            </div>

            <div className="footer-stat-item">
              <ShieldCheck size={18} color="#00a86b" />
              <div>
                <div className="footer-stat-title">100%</div>
                <div className="footer-stat-sub">DGCA Verified</div>
              </div>
            </div>

            <div className="footer-stat-item">
              <Headphones size={18} color="#38bdf8" />
              <div>
                <div className="footer-stat-title">24/7</div>
                <div className="footer-stat-sub">Real-Time Ingestion</div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Sub-footer */}
        <div className="footer-bottom">
          <div>
            © 2026 UDDAAN Platform · Smart India Hackathon (SIH26056) · MoSPI DIID
          </div>
          <div>
            Legal Compliance: IT Act 2000 §43/§66 & DPDP Act 2023 §6 Strict Adherence
          </div>
        </div>
      </div>
    </footer>
  );
}
