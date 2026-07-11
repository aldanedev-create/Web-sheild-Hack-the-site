/**
 * WebShield Scanner - Premium JavaScript
 * Handles premium plan upgrades and subscription management.
 */

(function() {
    'use strict';

    /**
     * Check premium status on page load
     */
    document.addEventListener('DOMContentLoaded', function() {
        checkPremiumStatus();
    });

    /**
     * Check premium status
     */
    function checkPremiumStatus() {
        if (!window.api || !window.api.isAuthenticated()) return;

        window.api.subscription.getCurrent()
        .then(data => {
            if (data.success) {
                updatePremiumUI(data);
            }
        })
        .catch(error => {
            console.error('Error checking premium status:', error);
        });
    }

    /**
     * Update premium UI
     */
    function updatePremiumUI(data) {
        const isPremium = data.is_premium || false;
        const subscription = data.subscription || {};

        // Update user state
        if (window.WebShield) {
            window.WebShield.state.isPremium = isPremium;
        }

        // Update premium badge
        const badgeElements = document.querySelectorAll('.premium-badge-nav, .badge-premium');
        badgeElements.forEach(el => {
            if (isPremium) {
                el.style.display = 'inline-flex';
            } else {
                el.style.display = 'none';
            }
        });

        // Update upgrade button
        const upgradeBtn = document.getElementById('upgrade-btn');
        if (upgradeBtn) {
            if (isPremium) {
                upgradeBtn.disabled = true;
                upgradeBtn.innerHTML = '<i class="fas fa-check-circle"></i> Already Premium';
            }
        }

        // Show subscription details if premium
        if (isPremium && subscription) {
            const expiryEl = document.querySelector('.subscription-expiry');
            if (expiryEl) {
                const days = subscription.days_remaining || 0;
                expiryEl.textContent = days > 0 ? `${days} days remaining` : 'Expired';
            }
        }
    }

    /**
     * Start upgrade process
     */
    window.startUpgrade = function() {
        const btn = document.getElementById('upgrade-btn');
        if (!btn || btn.disabled) return;

        if (!window.api || !window.api.isAuthenticated()) {
            window.location.href = '/login';
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

        window.api.subscription.createCheckout('premium')
        .then(data => {
            if (data.success && data.checkout_url) {
                if (isTrustedStripeCheckout(data.checkout_url)) {
                    window.location.href = data.checkout_url;
                } else {
                    throw new Error('Checkout URL was not trusted.');
                }
            } else {
                WebShield.showToast(data.message || 'Failed to start upgrade.', 'danger');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-crown"></i> Upgrade Now - $5/month';
            }
        })
        .catch(error => {
            console.error('Upgrade error:', error);
            WebShield.showToast('An error occurred. Please try again.', 'danger');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-crown"></i> Upgrade Now - $5/month';
        });
    };

    /**
     * Cancel subscription
     */
    window.cancelSubscription = function() {
        if (!confirm('Are you sure you want to cancel your premium subscription?')) {
            return;
        }

        if (!window.api || !window.api.isAuthenticated()) {
            window.location.href = '/login';
            return;
        }

        window.api.subscription.cancel()
        .then(data => {
            if (data.success) {
                WebShield.showToast('Subscription cancelled successfully.', 'success');
                window.location.reload();
            } else {
                WebShield.showToast(data.message || 'Failed to cancel subscription.', 'danger');
            }
        })
        .catch(error => {
            console.error('Cancel subscription error:', error);
            WebShield.showToast('An error occurred. Please try again.', 'danger');
        });
    };

    function isTrustedStripeCheckout(value) {
        try {
            const parsed = new URL(value);
            return parsed.protocol === 'https:' &&
                ['checkout.stripe.com', 'billing.stripe.com'].includes(parsed.hostname);
        } catch (err) {
            return false;
        }
    }

})();
