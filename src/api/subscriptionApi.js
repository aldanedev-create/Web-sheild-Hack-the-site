/**
 * WebShield Scanner - Subscription API
 */

import { paymentApi } from './paymentApi.js';

export const subscriptionApi = {
  getPlans: paymentApi.getPlans,
  getCurrent: paymentApi.getCurrentSubscription,
  createCheckout: paymentApi.createCheckout,
  cancel: paymentApi.cancelSubscription,
  verifyAmazonIAP: paymentApi.verifyAmazonIAP
};

export default subscriptionApi;
