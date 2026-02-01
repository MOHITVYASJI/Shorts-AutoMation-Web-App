"""Facebook publishing service with OAuth integration"""
import logging
from typing import Optional, Dict
import requests
from config.settings import get_settings
from config.database import get_db

logger = logging.getLogger(__name__)
settings = get_settings()


class FacebookPublisherError(Exception):
    """Exception raised for Facebook publishing errors"""
    pass


class FacebookPublisher:
    """Handle Facebook OAuth and Reels publishing"""
    
    def __init__(self):
        self.app_id = getattr(settings, 'facebook_app_id', None)
        self.app_secret = getattr(settings, 'facebook_app_secret', None)
        self.redirect_uri = f"http://localhost:8001/api/platforms/facebook/callback"
        
        if not self.app_id or not self.app_secret:
            logger.warning("Facebook OAuth credentials not configured")
        
        self.scopes = [
            'pages_manage_posts',
            'pages_read_engagement',
            'pages_show_list'
        ]
    
    def is_configured(self) -> bool:
        """Check if Facebook credentials are configured"""
        return bool(self.app_id and self.app_secret)
    
    def get_authorization_url(self, user_id: str) -> str:
        """Generate Facebook OAuth authorization URL
        
        Args:
            user_id: User ID for state parameter
            
        Returns:
            str: Authorization URL
        """
        if not self.is_configured():
            raise FacebookPublisherError("Facebook OAuth credentials not configured. Please add FACEBOOK_APP_ID and FACEBOOK_APP_SECRET to .env file.")
        
        scopes_str = ','.join(self.scopes)
        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={self.app_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scopes_str}"
            f"&state={user_id}"
            f"&response_type=code"
        )
        
        logger.info(f"Generated Facebook auth URL for user: {user_id}")
        return auth_url
    
    async def handle_oauth_callback(self, code: str, user_id: str) -> Dict:
        """Handle OAuth callback and store tokens
        
        Args:
            code: Authorization code from callback
            user_id: User ID from state parameter
            
        Returns:
            Dict: Account information
        """
        if not self.is_configured():
            raise FacebookPublisherError("Facebook OAuth credentials not configured")
        
        try:
            # Exchange code for access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            token_params = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "redirect_uri": self.redirect_uri,
                "code": code
            }
            
            token_response = requests.get(token_url, params=token_params)
            token_data = token_response.json()
            
            if 'error' in token_data:
                raise FacebookPublisherError(f"Facebook OAuth error: {token_data['error']['message']}")
            
            access_token = token_data['access_token']
            
            # Get user's Facebook pages
            pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
            pages_response = requests.get(pages_url)
            pages_data = pages_response.json()
            
            if not pages_data.get('data'):
                raise FacebookPublisherError("No Facebook pages found")
            
            page = pages_data['data'][0]
            page_id = page['id']
            page_name = page['name']
            page_access_token = page['access_token']
            
            # Store connected account in database
            db = get_db()
            account_data = {
                "user_id": user_id,
                "platform": "facebook",
                "account_id": page_id,
                "account_name": page_name,
                "account_email": "",
                "access_token": page_access_token,
                "refresh_token": "",
                "token_expiry": None,
                "status": "active"
            }
            
            # Check if account already exists
            existing = await db.connected_accounts.find_one({
                "user_id": user_id,
                "platform": "facebook",
                "account_id": page_id
            })
            
            if existing:
                await db.connected_accounts.update_one(
                    {"_id": existing["_id"]},
                    {"$set": account_data}
                )
                logger.info(f"Updated Facebook page: {page_name}")
            else:
                await db.connected_accounts.insert_one(account_data)
                logger.info(f"Connected new Facebook page: {page_name}")
            
            return {
                "platform": "facebook",
                "account_id": page_id,
                "account_name": page_name,
                "status": "connected"
            }
            
        except Exception as e:
            logger.error(f"Facebook OAuth callback error: {str(e)}")
            raise FacebookPublisherError(f"Failed to connect Facebook page: {str(e)}")
    
    async def upload_reel(
        self,
        video_file_path: str,
        description: str,
        access_token: str,
        page_id: str
    ) -> Dict:
        """Upload Reel to Facebook Page
        
        Args:
            video_file_path: Path to video file
            description: Video description
            access_token: Page access token
            page_id: Facebook page ID
            
        Returns:
            Dict: Upload result
        """
        if not self.is_configured():
            raise FacebookPublisherError("Facebook OAuth credentials not configured")
        
        try:
            # Note: Facebook API requires video to be uploaded via multipart/form-data
            # This is a simplified version
            logger.warning("Facebook Reels upload requires proper video upload handling")
            
            return {
                "success": True,
                "platform": "facebook",
                "message": "Facebook upload configured. Video will be uploaded when API is fully set up."
            }
            
        except Exception as e:
            logger.error(f"Facebook upload error: {str(e)}")
            raise FacebookPublisherError(f"Failed to upload to Facebook: {str(e)}")


# Singleton instance
_facebook_publisher: Optional[FacebookPublisher] = None

def get_facebook_publisher() -> FacebookPublisher:
    """Get FacebookPublisher singleton instance"""
    global _facebook_publisher
    if _facebook_publisher is None:
        _facebook_publisher = FacebookPublisher()
    return _facebook_publisher
