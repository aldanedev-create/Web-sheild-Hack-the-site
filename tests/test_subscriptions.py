# -*- coding: utf-8 -*-

"""
WebShield Scanner - Subscription Tests
Tests for premium plan subscriptions and payment handling.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.models.subscription import Subscription
from app.models.user import User


class TestSubscriptions:
    """Test subscription functionality."""

    def test_get_plans(self, client):
        """Test getting available plans."""
        response = client.get('/api/subscription/plans')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'plans' in data
        assert len(data['plans']) == 2  # free and premium

        # Check free plan
        free_plan = data['plans'][0]
        assert free_plan['id'] == 'free'
        assert free_plan['price'] == 0

        # Check premium plan
        premium_plan = data['plans'][1]
        assert premium_plan['id'] == 'premium'
        assert premium_plan['price'] == 5.00
        assert premium_plan['is_recommended'] is True

    def test_get_current_subscription_free(self, client, auth_headers, test_user):
        """Test getting current subscription for free user."""
        response = client.get('/api/subscription/current',
            headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user_plan'] == 'free'
        assert data['is_premium'] is False
        assert data['subscription']['plan'] == 'free'

    def test_get_current_subscription_premium(self, client, auth_headers_premium, test_premium_user):
        """Test getting current subscription for premium user."""
        response = client.get('/api/subscription/current',
            headers=auth_headers_premium)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user_plan'] == 'premium'
        assert data['is_premium'] is True
        assert data['subscription']['plan'] == 'premium'
        assert data['subscription']['status'] == 'active'

    def test_create_checkout(self, client, auth_headers, test_user):
        """Test creating checkout session."""
        with patch('stripe.checkout.Session.create') as mock_create:
            mock_create.return_value = MagicMock(url='https://checkout.stripe.com/test')

            response = client.post('/api/subscription/create-checkout',
                headers=auth_headers,
                json={'plan_id': 'premium'})

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'checkout_url' in data

    def test_create_checkout_stripe_error(self, client, auth_headers, test_user):
        """Test checkout with Stripe error."""
        with patch('stripe.checkout.Session.create') as mock_create:
            mock_create.side_effect = Exception('Stripe error')

            response = client.post('/api/subscription/create-checkout',
                headers=auth_headers,
                json={'plan_id': 'premium'})

            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False

    def test_cancel_subscription(self, client, auth_headers_premium, test_premium_user):
        """Test cancelling subscription."""
        # Create active subscription
        subscription = Subscription(
            user_id=test_premium_user.id,
            plan='premium',
            status='active',
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(subscription)
        db.session.commit()

        response = client.post('/api/subscription/cancel',
            headers=auth_headers_premium)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

        # Verify subscription was cancelled
        db.session.refresh(subscription)
        assert subscription.status == 'cancelled'

        # Verify user plan was downgraded
        db.session.refresh(test_premium_user)
        assert test_premium_user.plan == 'free'

    def test_cancel_subscription_not_found(self, client, auth_headers, test_user):
        """Test cancelling when no active subscription exists."""
        response = client.post('/api/subscription/cancel',
            headers=auth_headers)

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'active subscription' in data['message'].lower()

    def test_webhook_checkout_completed(self, client, test_user):
        """Test Stripe webhook for checkout completion."""
        payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'client_reference_id': str(test_user.id),
                    'amount_total': 500
                }
            }
        }

        with patch('stripe.Webhook.construct_event') as mock_event:
            mock_event.return_value = payload

            response = client.post('/api/subscription/webhook',
                data=json.dumps(payload),
                headers={'Stripe-Signature': 'test_signature'})

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True

            # Verify subscription was created
            subscription = Subscription.query.filter_by(user_id=test_user.id).first()
            assert subscription is not None
            assert subscription.plan == 'premium'
            assert subscription.status == 'active'

    def test_webhook_subscription_deleted(self, client, test_premium_user):
        """Test Stripe webhook for subscription deletion."""
        # Create subscription
        subscription = Subscription(
            user_id=test_premium_user.id,
            plan='premium',
            status='active',
            payment_id='sub_123'
        )
        db.session.add(subscription)
        db.session.commit()

        payload = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_123',
                    'metadata': {'user_id': str(test_premium_user.id)}
                }
            }
        }

        with patch('stripe.Webhook.construct_event') as mock_event:
            mock_event.return_value = payload

            response = client.post('/api/subscription/webhook',
                data=json.dumps(payload),
                headers={'Stripe-Signature': 'test_signature'})

            assert response.status_code == 200

            # Verify subscription was cancelled
            db.session.refresh(subscription)
            assert subscription.status == 'cancelled'

    def test_premium_user_unlimited_scans(self, test_premium_user):
        """Test premium user has unlimited scans."""
        assert test_premium_user.can_scan() is True
        assert test_premium_user.get_remaining_scans() == float('inf')

    def test_free_user_scan_limit(self, test_user):
        """Test free user scan limit."""
        # Initially should have scans remaining
        assert test_user.can_scan() is True
        assert test_user.get_remaining_scans() == 5

        # Use all scans
        for _ in range(5):
            test_user.increment_scans()

        assert test_user.can_scan() is False
        assert test_user.get_remaining_scans() == 0

    def test_free_user_scan_reset(self, test_user):
        """Test free user scan count resets daily."""
        # Use all scans
        for _ in range(5):
            test_user.increment_scans()

        # Set last scan date to yesterday
        test_user.last_scan_date = datetime.utcnow() - timedelta(days=1)
        db.session.commit()

        # Should have scans available again
        assert test_user.can_scan() is True
        assert test_user.get_remaining_scans() == 5