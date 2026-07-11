# -*- coding: utf-8 -*-

"""
WebShield Scanner - Ad Service
Handles ad serving and ad-related business logic.
"""

from flask import current_app
from app.models.user import User


class AdService:
    """Service for handling ad operations."""
    
    @staticmethod
    def should_show_ads(user_id=None):
        """
        Determine if ads should be shown to a user.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            bool: True if ads should be shown
        """
        if not user_id:
            return True
        
        user = User.query.get(user_id)
        
        if not user:
            return True
        
        # Premium users don't see ads
        if user.is_premium() or user.is_admin:
            return False
        
        return True
    
    @staticmethod
    def get_ad_config():
        """
        Get ad configuration.
        
        Returns:
            dict: Ad configuration
        """
        return {
            'ad_unit_id': current_app.config.get('ADMOB_BANNER_ID'),
            'interstitial_id': current_app.config.get('ADMOB_INTERSTITIAL_ID'),
            'rewarded_id': current_app.config.get('ADMOB_REWARDED_ID'),
            'is_enabled': bool(current_app.config.get('ADMOB_APP_ID'))
        }
    
    @staticmethod
    def get_ad_frequency(user_id=None):
        """
        Get ad frequency for a user.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            int: Ad frequency (seconds between ads)
        """
        # Premium users get no ads
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_premium():
                return 0
        
        # Free users get ads every 60 seconds
        return 60
    
    @staticmethod
    def should_show_interstitial(user_id=None):
        """
        Determine if an interstitial ad should be shown.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            bool: True if interstitial should be shown
        """
        # Premium users don't see interstitial ads
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_premium():
                return False
        
        # Show interstitial for free users occasionally
        # In production, track impression history
        return True
    
    @staticmethod
    def track_ad_impression(user_id=None, ad_type='banner'):
        """
        Track an ad impression.
        
        Args:
            user_id: User ID (optional)
            ad_type: Type of ad (banner, interstitial, rewarded)
            
        Returns:
            bool: Success status
        """
        # In production, store ad impressions for analytics
        # For now, just log
        current_app.logger.info(f"Ad impression: {ad_type} for user {user_id or 'anonymous'}")
        return True
    
    @staticmethod
    def track_ad_click(user_id=None, ad_type='banner'):
        """
        Track an ad click.
        
        Args:
            user_id: User ID (optional)
            ad_type: Type of ad (banner, interstitial, rewarded)
            
        Returns:
            bool: Success status
        """
        # In production, store ad clicks for analytics
        # For now, just log
        current_app.logger.info(f"Ad click: {ad_type} for user {user_id or 'anonymous'}")
        return True
    
    @staticmethod
    def get_ad_units():
        """
        Get all ad unit IDs.
        
        Returns:
            dict: Ad unit IDs
        """
        return {
            'banner': current_app.config.get('ADMOB_BANNER_ID'),
            'interstitial': current_app.config.get('ADMOB_INTERSTITIAL_ID'),
            'rewarded': current_app.config.get('ADMOB_REWARDED_ID')
        }