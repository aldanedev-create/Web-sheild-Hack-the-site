/**
 * WebShield Scanner - Payment API
 * Handles subscriptions and payments.
 */

import apiClient from './client.js';
import { API_ENDPOINTS } from '../config.js';

export const paymentApi = {
  /**
   * Get available plans
   */
  getPlans: () => {
    return apiClient.get(API_ENDPOINTS.SUBSCRIPTION.PLANS, { includeAuth: false });
  },

  /**
   * Get current subscription
   */
  getCurrentSubscription: () => {
    return apiClient.get(API_ENDPOINTS.SUBSCRIPTION.CURRENT);
  },

  /**
   * Create checkout session
   */
  createCheckout: (planId = 'premium') => {
    return apiClient.post(API_ENDPOINTS.SUBSCRIPTION.CHECKOUT, {
      plan_id: planId
    });
  },

  /**
   * Cancel subscription
   */
  cancelSubscription: () => {
    return apiClient.post(API_ENDPOINTS.SUBSCRIPTION.CANCEL, {});
  },

  /**
   * Verify Amazon IAP purchase
   */
  verifyAmazonIAP: (receipt, signature) => {
    return apiClient.post(API_ENDPOINTS.SUBSCRIPTION.AMAZON_IAP, {
      receipt: receipt,
      signature: signature
    });
  },

  /**
   * Handle Stripe webhook (public endpoint)
   */
  handleWebhook: (payload, signature) => {
    return apiClient.post('/subscription/webhook', payload, {
      includeAuth: false,
      headers: {
        'Stripe-Signature': signature
      }
    });
  }
};

export default paymentApi;