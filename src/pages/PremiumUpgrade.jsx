import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { subscriptionApi } from '../api/subscriptionApi.js';
import { getToken } from '../api/client.js';
import '../styles/global.css';

const PremiumUpgrade = ({ isPremium, onUpgrade }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [subscription, setSubscription] = useState(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      navigate('/login');
      return;
    }

    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      const response = await subscriptionApi.getCurrent();
      if (response.success) {
        setSubscription(response.subscription);
      }
    } catch (err) {
      console.error('Subscription error:', err);
    }
  };

  const handleUpgrade = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await subscriptionApi.createCheckout('premium');
      if (response.success && response.checkout_url) {
        if (isTrustedStripeCheckout(response.checkout_url)) {
          window.location.href = response.checkout_url;
        } else {
          setError('Checkout URL was not trusted.');
        }
      } else {
        setError(response.message || 'Failed to start upgrade.');
      }
    } catch (err) {
      console.error('Upgrade error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your premium subscription?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await subscriptionApi.cancel();
      if (response.success) {
        alert('Subscription cancelled successfully.');
        window.location.reload();
      } else {
        setError(response.message || 'Failed to cancel subscription.');
      }
    } catch (err) {
      console.error('Cancel error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (isPremium) {
    return (
      <div className="page-container">
        <div className="already-premium">
          <div className="icon"><i className="fas fa-crown"></i></div>
          <h3>You're a Premium User!</h3>
          <p style={{ color: '#8899aa' }}>
            Enjoy unlimited scans, PDF reports, and all premium features.
          </p>
          {subscription && (
            <p style={{ fontSize: '0.8rem', color: '#667', marginTop: '10px' }}>
              Plan: {subscription.plan?.charAt(0).toUpperCase() + subscription.plan?.slice(1)} | 
              {subscription.days_remaining > 0 
                ? ` ${subscription.days_remaining} days remaining`
                : ' Expired'}
            </p>
          )}
          <div className="cancel-sub">
            <button className="btn-cancel" onClick={handleCancel} disabled={loading}>
              {loading ? 'Processing...' : <><i className="fas fa-times"></i> Cancel Subscription</>}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="premium-hero">
        <div className="crown"><i className="fas fa-crown"></i></div>
        <h2>Go Premium</h2>
        <div className="sub">Unlock the full power of WebShield Scanner</div>
      </div>

      <div className="price-card">
        <div className="price">$5</div>
        <div className="period">per month</div>
        <div className="savings">🔥 Cancel anytime</div>
      </div>

      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          <i className="fas fa-exclamation-circle me-2"></i>
          {error}
          <button type="button" className="btn-close" onClick={() => setError('')}></button>
        </div>
      )}

      <div className="features-list">
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Unlimited</span> scans</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">PDF</span> report export</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Ad-free</span> experience</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Authenticated</span> scanning</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Advanced</span> crawling</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Security trend</span> tracking</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Full learning center</span> access</span>
        </div>
        <div className="feature">
          <span className="icon"><i className="fas fa-check-circle"></i></span>
          <span className="text"><span className="highlight">Priority</span> support</span>
        </div>
      </div>

      <table className="comparison-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Free</th>
            <th>Premium</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Scans per day</td>
            <td>5</td>
            <td><span className="premium-highlight">Unlimited</span></td>
          </tr>
          <tr>
            <td>PDF Reports</td>
            <td><span className="cross"><i className="fas fa-times"></i></span></td>
            <td><span className="check"><i className="fas fa-check"></i></span></td>
          </tr>
          <tr>
            <td>Ads</td>
            <td><span className="cross"><i className="fas fa-times"></i></span></td>
            <td><span className="check"><i className="fas fa-check"></i></span></td>
          </tr>
          <tr>
            <td>Authenticated Scanning</td>
            <td><span className="cross"><i className="fas fa-times"></i></span></td>
            <td><span className="check"><i className="fas fa-check"></i></span></td>
          </tr>
          <tr>
            <td>Advanced Crawling</td>
            <td><span className="cross"><i className="fas fa-times"></i></span></td>
            <td><span className="check"><i className="fas fa-check"></i></span></td>
          </tr>
          <tr>
            <td>Security Trends</td>
            <td><span className="cross"><i className="fas fa-times"></i></span></td>
            <td><span className="check"><i className="fas fa-check"></i></span></td>
          </tr>
          <tr>
            <td>Learning Center (Full)</td>
            <td><span className="cross"><i className="fas fa-times"></i></span></td>
            <td><span className="check"><i className="fas fa-check"></i></span></td>
          </tr>
        </tbody>
      </table>

      <button
        className="btn-upgrade"
        onClick={handleUpgrade}
        disabled={loading}
      >
        {loading ? (
          <><i className="fas fa-spinner fa-spin"></i> Processing...</>
        ) : (
          <><i className="fas fa-crown"></i> Upgrade Now - $5/month</>
        )}
      </button>

      <p style={{ textAlign: 'center', fontSize: '0.7rem', color: '#667', marginTop: '15px' }}>
        <i className="fas fa-lock"></i> Secure payment powered by Stripe
      </p>
    </div>
  );
};

const isTrustedStripeCheckout = (value) => {
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'https:' &&
      ['checkout.stripe.com', 'billing.stripe.com'].includes(parsed.hostname);
  } catch {
    return false;
  }
};

export default PremiumUpgrade;
