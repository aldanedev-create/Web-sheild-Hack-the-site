# -*- coding: utf-8 -*-

"""
WebShield Scanner - Subscription Routes
Handles premium plan subscriptions and payments.
"""

from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog
from app.services.payment_service import PaymentService

subscription_bp = Blueprint('subscription', __name__)


def _is_trusted_checkout_url(value):
    try:
        parsed = urlparse(value or '')
    except Exception:
        return False
    return parsed.scheme == 'https' and parsed.hostname in {
        'checkout.stripe.com',
        'billing.stripe.com',
    }


@subscription_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans."""
    try:
        plans = [
            {
                'id': 'free',
                'name': 'Free',
                'price': 0,
                'currency': 'USD',
                'features': [
                    '5 scans per day',
                    'Basic security scanning',
                    'Attack surface mapping',
                    'HTML report export',
                    'Learning center access (basic)',
                    'Ad supported'
                ],
                'is_recommended': False
            },
            {
                'id': 'premium',
                'name': 'Premium',
                'price': 5.00,
                'currency': 'USD',
                'features': [
                    'Unlimited scans',
                    'Advanced security scanning',
                    'PDF report export',
                    'Scan history',
                    'Authenticated scanning',
                    'Advanced crawling',
                    'Security trend tracking',
                    'Ad-free experience',
                    'Full learning center access',
                    'Priority support'
                ],
                'is_recommended': True
            }
        ]
        
        return jsonify({
            'success': True,
            'plans': plans
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get plans error: {str(e)}')
        return jsonify({
            'error': 'fetch_failed',
            'message': 'Could not fetch plans'
        }), 500


@subscription_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get current user subscription."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if subscription:
            subscription_data = subscription.to_dict()
        else:
            subscription_data = {
                'plan': 'free',
                'status': 'inactive',
                'is_active': False,
                'days_remaining': 0
            }
        
        return jsonify({
            'success': True,
            'subscription': subscription_data,
            'user_plan': user.plan,
            'is_premium': user.is_premium()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get subscription error: {str(e)}')
        return jsonify({
            'error': 'fetch_failed',
            'message': 'Could not fetch subscription'
        }), 500


@subscription_bp.route('/create-checkout', methods=['POST'])
@jwt_required()
def create_checkout():
    """Create a Stripe checkout session for premium subscription."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404
        
        data = request.get_json(silent=True) or {}
        plan_id = data.get('plan_id', 'premium')
        
        if plan_id != 'premium':
            return jsonify({
                'error': 'invalid_plan',
                'message': 'Invalid plan selected'
            }), 400
        
        # Create Stripe checkout session
        payment_service = PaymentService()
        checkout_url = payment_service.create_checkout_session(
            user=user,
            plan='premium',
            price=5.00,
            currency='USD'
        )

        if not _is_trusted_checkout_url(checkout_url):
            current_app.logger.error('Untrusted checkout URL returned for user %s', user_id)
            return jsonify({
                'error': 'checkout_failed',
                'message': 'Could not create checkout session'
            }), 500
        
        AuditLog.log(
            user_id=user_id,
            action='checkout_created',
            details=f'Created checkout for premium plan',
            metadata={'plan': 'premium', 'price': 5.00}
        )
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_url
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Create checkout error: {str(e)}')
        return jsonify({
            'error': 'checkout_failed',
            'message': 'Could not create checkout session'
        }), 500


@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        payment_service = PaymentService()
        event = payment_service.handle_webhook(payload, sig_header)
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get('client_reference_id')
            
            if user_id:
                user = User.query.get(int(user_id))
                if user:
                    # Activate subscription
                    subscription = Subscription.query.filter_by(
                        user_id=user.id,
                        status='active'
                    ).first()
                    
                    if not subscription:
                        subscription = Subscription(
                            user_id=user.id,
                            plan='premium',
                            payment_provider='stripe',
                            payment_id=session.get('id'),
                            amount_paid=5.00,
                            currency='USD'
                        )
                        db.session.add(subscription)
                    
                    subscription.activate(duration_days=30)
                    db.session.commit()
                    
                    AuditLog.log(
                        user_id=user.id,
                        action='premium_upgrade',
                        details=f'User upgraded to premium via Stripe',
                        metadata={'subscription_id': subscription.id}
                    )
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        current_app.logger.error(f'Webhook error: {str(e)}')
        return jsonify({'error': 'webhook_failed'}), 500


@subscription_bp.route('/amazon-iap', methods=['POST'])
@jwt_required()
def amazon_iap_verify():
    """Verify Amazon In-App Purchase."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404
        
        data = request.get_json(silent=True) or {}
        receipt = data.get('receipt')
        signature = data.get('signature')
        
        if not receipt or not signature:
            return jsonify({
                'error': 'missing_data',
                'message': 'Receipt and signature are required'
            }), 400
        
        # Verify receipt with Amazon IAP
        payment_service = PaymentService()
        is_valid = payment_service.verify_amazon_receipt(receipt, signature)
        
        if is_valid:
            # Activate subscription
            subscription = Subscription.query.filter_by(
                user_id=user.id,
                status='active'
            ).first()
            
            if not subscription:
                subscription = Subscription(
                    user_id=user.id,
                    plan='premium',
                    payment_provider='amazon_iap',
                    payment_id=receipt
                )
                db.session.add(subscription)
            
            subscription.activate(duration_days=30)
            db.session.commit()
            
            AuditLog.log(
                user_id=user.id,
                action='premium_upgrade',
                details=f'User upgraded to premium via Amazon IAP',
                metadata={'subscription_id': subscription.id}
            )
            
            return jsonify({
                'success': True,
                'message': 'Subscription activated successfully'
            }), 200
        else:
            return jsonify({
                'error': 'invalid_receipt',
                'message': 'Invalid purchase receipt'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Amazon IAP error: {str(e)}')
        return jsonify({
            'error': 'verification_failed',
            'message': 'Could not verify purchase'
        }), 500


@subscription_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel the current subscription."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({
                'error': 'no_subscription',
                'message': 'No active subscription found'
            }), 404
        
        subscription.cancel()
        db.session.commit()
        
        AuditLog.log(
            user_id=user_id,
            action='subscription_cancelled',
            details=f'User cancelled premium subscription',
            metadata={'subscription_id': subscription.id}
        )
        
        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Cancel subscription error: {str(e)}')
        return jsonify({
            'error': 'cancel_failed',
            'message': 'Could not cancel subscription'
        }), 500
