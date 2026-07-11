# -*- coding: utf-8 -*-

"""
WebShield Scanner - Payment Service
Handles payment processing and subscription management.
"""

from flask import current_app
from extensions import db
from app.models.user import User
from app.models.subscription import Subscription


class PaymentService:
    """Service for handling payment operations."""
    
    def __init__(self):
        """Initialize the payment service."""
        self.stripe_api_key = current_app.config.get('STRIPE_SECRET_KEY')

    def _stripe(self):
        """Import and configure Stripe only when payment code is used."""
        if not self.stripe_api_key:
            if current_app.config.get('TESTING'):
                self.stripe_api_key = 'sk_test_dummy'
            else:
                raise ValueError("Stripe is not configured")

        import stripe

        stripe.api_key = self.stripe_api_key
        return stripe

    @staticmethod
    def _audit_service():
        from app.services.audit_service import AuditService

        return AuditService
    
    def create_checkout_session(self, user, plan='premium', price=5.00, currency='USD'):
        """
        Create a Stripe checkout session.
        
        Args:
            user: User object
            plan: Plan name
            price: Price amount
            currency: Currency code
            
        Returns:
            str: Checkout URL
            
        Raises:
            ValueError: Stripe not configured
        """
        stripe = self._stripe()

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'WebShield Scanner - {plan.capitalize()} Plan',
                            'description': f'Monthly subscription for {plan} plan features',
                        },
                        'unit_amount': int(price * 100),  # Convert to cents
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{current_app.config.get('APP_URL', 'http://localhost:5000')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{current_app.config.get('APP_URL', 'http://localhost:5000')}/payment/cancel",
                client_reference_id=str(user.id),
                metadata={
                    'user_id': str(user.id),
                    'plan': plan
                }
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f'Stripe error: {str(e)}')
            raise ValueError(f"Payment processing error: {str(e)}")
    
    def handle_webhook(self, payload, sig_header):
        """
        Handle Stripe webhook events.
        
        Args:
            payload: Webhook payload
            sig_header: Stripe signature header
            
        Returns:
            dict: Event data
            
        Raises:
            ValueError: Invalid signature
        """
        stripe = self._stripe()
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        
        if not webhook_secret:
            raise ValueError("Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise ValueError(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise ValueError(f"Invalid signature: {str(e)}")
        
        # Handle event
        if event['type'] == 'checkout.session.completed':
            self._handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            self._handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            self._handle_subscription_deleted(event['data']['object'])
        
        return event
    
    def _handle_checkout_completed(self, session):
        """
        Handle checkout completed event.
        
        Args:
            session: Stripe session object
        """
        user_id = session.get('client_reference_id')
        
        if not user_id:
            return
        
        user = User.query.get(int(user_id))
        if not user:
            return
        
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
        
        self._audit_service().log(
            user_id=user.id,
            action='premium_upgrade',
            details=f'User upgraded to premium via Stripe',
            metadata={'subscription_id': subscription.id}
        )
    
    def _handle_subscription_updated(self, subscription):
        """
        Handle subscription updated event.
        
        Args:
            subscription: Stripe subscription object
        """
        # Find user by customer email or metadata
        user_id = None
        if subscription.get('metadata') and subscription['metadata'].get('user_id'):
            user_id = int(subscription['metadata']['user_id'])
        
        if not user_id:
            return
        
        user = User.query.get(user_id)
        if not user:
            return
        
        # Update subscription status
        sub = Subscription.query.filter_by(
            user_id=user.id,
            payment_id=subscription.get('id')
        ).first()
        
        if sub:
            if subscription.get('status') == 'active':
                if not sub.is_active():
                    sub.activate(duration_days=30)
            elif subscription.get('status') == 'past_due':
                sub.status = 'past_due'
            elif subscription.get('status') == 'canceled':
                sub.cancel()
            
            db.session.commit()
    
    def _handle_subscription_deleted(self, subscription):
        """
        Handle subscription deleted event.
        
        Args:
            subscription: Stripe subscription object
        """
        user_id = None
        if subscription.get('metadata') and subscription['metadata'].get('user_id'):
            user_id = int(subscription['metadata']['user_id'])
        
        if not user_id:
            return
        
        user = User.query.get(user_id)
        if not user:
            return
        
        # Cancel subscription
        sub = Subscription.query.filter_by(
            user_id=user.id,
            payment_id=subscription.get('id')
        ).first()
        
        if sub:
            sub.cancel()
            db.session.commit()
            
            self._audit_service().log(
                user_id=user.id,
                action='subscription_cancelled',
                details=f'Subscription cancelled via Stripe',
                metadata={'subscription_id': sub.id}
            )
    
    def verify_amazon_receipt(self, receipt, signature):
        """
        Verify Amazon In-App Purchase receipt.
        
        Args:
            receipt: Purchase receipt
            signature: Purchase signature
            
        Returns:
            bool: Verification result
        """
        # In production, use Amazon IAP API to verify receipt
        # For now, accept any receipt
        return True
    
    def cancel_subscription(self, user_id):
        """
        Cancel a user's subscription.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: Success status
            
        Raises:
            ValueError: Validation errors
        """
        user = User.query.get(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            raise ValueError("No active subscription found")
        
        # If subscription is via Stripe, cancel in Stripe
        if subscription.payment_provider == 'stripe' and subscription.payment_id:
            stripe = self._stripe()
            try:
                stripe.Subscription.delete(subscription.payment_id)
            except stripe.error.StripeError as e:
                current_app.logger.error(f'Stripe cancel error: {str(e)}')
                # Continue with local cancellation even if Stripe fails
        
        subscription.cancel()
        db.session.commit()
        
        self._audit_service().log(
            user_id=user_id,
            action='subscription_cancelled',
            details=f'User cancelled premium subscription',
            metadata={'subscription_id': subscription.id}
        )
        
        return True
    
    def get_subscription_status(self, user_id):
        """
        Get subscription status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Subscription status
        """
        user = User.query.get(user_id)
        
        if not user:
            return {'has_subscription': False}
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if subscription:
            return {
                'has_subscription': True,
                'plan': subscription.plan,
                'status': subscription.status,
                'is_active': subscription.is_active(),
                'days_remaining': subscription.days_remaining(),
                'expires_at': subscription.expires_at.isoformat() if subscription.expires_at else None,
                'started_at': subscription.started_at.isoformat() if subscription.started_at else None
            }
        
        return {
            'has_subscription': False,
            'plan': 'free',
            'status': 'inactive'
        }
