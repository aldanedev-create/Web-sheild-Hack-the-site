# -*- coding: utf-8 -*-

"""
WebShield Scanner - Subscription Model
Manages user subscription plans and payment status.
"""

from datetime import datetime, timedelta
from extensions import db


class Subscription(db.Model):
    """Subscription model for premium plan management."""
    
    __tablename__ = 'subscriptions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Plan details
    plan = db.Column(db.String(20), default='free', index=True)
    # free, premium
    
    # Status
    status = db.Column(db.String(20), default='inactive', index=True)
    # active, inactive, cancelled, expired, pending
    
    # Payment details
    payment_provider = db.Column(db.String(20), index=True)
    # stripe, amazon_iap, manual
    payment_id = db.Column(db.String(100), index=True)
    amount_paid = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    
    # Subscription dates
    started_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime, index=True)
    cancelled_at = db.Column(db.DateTime)
    
    # Auto-renewal
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Metadata
    provider_metadata = db.Column('metadata', db.JSON)  # Additional data from payment provider
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, plan='free', **kwargs):
        """Initialize a new subscription."""
        self.user_id = user_id
        self.plan = plan
        self.status = 'inactive'
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            if key == 'metadata':
                key = 'provider_metadata'
            setattr(self, key, value)
    
    def activate(self, duration_days=30):
        """Activate the subscription."""
        self.status = 'active'
        self.started_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=duration_days)
        self.updated_at = datetime.utcnow()
        
        # Update user's plan
        from app.models.user import User
        user = User.query.get(self.user_id)
        if user:
            user.plan = self.plan
            user.plan_updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the subscription."""
        self.status = 'inactive'
        self.updated_at = datetime.utcnow()
        
        # Update user's plan
        from app.models.user import User
        user = User.query.get(self.user_id)
        if user:
            user.plan = 'free'
            user.plan_updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel the subscription."""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.auto_renew = False
        self.updated_at = datetime.utcnow()
    
    def is_active(self):
        """Check if subscription is currently active."""
        if self.status != 'active':
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def is_expired(self):
        """Check if the subscription has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def days_remaining(self):
        """Get number of days remaining in the subscription."""
        if not self.expires_at:
            return 0
        remaining = (self.expires_at - datetime.utcnow()).days
        return max(0, remaining)
    
    def renew(self, duration_days=30):
        """Renew the subscription."""
        if self.is_active():
            self.expires_at = self.expires_at + timedelta(days=duration_days)
        else:
            self.activate(duration_days)
        self.updated_at = datetime.utcnow()
        return self
    
    def to_dict(self):
        """Convert subscription to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan,
            'status': self.status,
            'payment_provider': self.payment_provider,
            'payment_id': self.payment_id,
            'amount_paid': self.amount_paid,
            'currency': self.currency,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'auto_renew': self.auto_renew,
            'metadata': self.provider_metadata,
            'is_active': self.is_active(),
            'days_remaining': self.days_remaining(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Subscription {self.id}: {self.plan} ({self.status})>'
