import React, { useState, useEffect } from 'react';
import '../styles/mobile.css';

const AdBanner = () => {
  const [visible, setVisible] = useState(false);
  const [closed, setClosed] = useState(false);

  useEffect(() => {
    // Show ad after 5 seconds
    const timer = setTimeout(() => {
      setVisible(true);
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setVisible(false);
    setClosed(true);
  };

  if (closed) return null;

  return (
    <div className={`ad-banner ${visible ? 'visible' : ''}`}>
      <div className="ad-banner-content">
        <div className="ad-label">Sponsored</div>
        <div className="ad-placeholder">
          <i className="fas fa-ad"></i>
          <span>Ad Placeholder - Google AdMob</span>
        </div>
        <button className="ad-close" onClick={handleClose}>
          <i className="fas fa-times"></i>
        </button>
      </div>

      <style>{`
        .ad-banner {
          position: fixed;
          bottom: 60px;
          left: 0;
          right: 0;
          z-index: 1030;
          padding: 8px 12px;
          background: rgba(10, 10, 26, 0.95);
          backdrop-filter: blur(10px);
          border-top: 1px solid rgba(255, 255, 255, 0.05);
          transform: translateY(100%);
          transition: transform 0.3s ease, opacity 0.3s ease;
          opacity: 0;
        }
        .ad-banner.visible {
          transform: translateY(0);
          opacity: 1;
        }
        .ad-banner-content {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 8px;
          padding: 8px 12px;
          border: 1px solid rgba(255, 255, 255, 0.03);
          position: relative;
          min-height: 44px;
          max-width: 500px;
          margin: 0 auto;
        }
        .ad-label {
          font-size: 0.5rem;
          color: #667;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          position: absolute;
          top: -6px;
          left: 12px;
          background: rgba(10, 10, 26, 0.95);
          padding: 0 6px;
        }
        .ad-placeholder {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          color: #556;
          font-size: 0.7rem;
          padding: 4px 0;
        }
        .ad-placeholder i {
          font-size: 1.2rem;
          color: #445;
        }
        .ad-close {
          background: none;
          border: none;
          color: #667;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 4px;
          transition: all 0.3s ease;
          font-size: 0.8rem;
        }
        .ad-close:hover {
          color: #fff;
          background: rgba(255, 255, 255, 0.05);
        }
        @media (min-width: 768px) {
          .ad-banner {
            bottom: 0;
          }
        }
        @supports (padding: max(0px)) {
          .ad-banner {
            padding-bottom: max(8px, env(safe-area-inset-bottom));
          }
        }
      `}</style>
    </div>
  );
};

export default AdBanner;
