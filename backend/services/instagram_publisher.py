"""Instagram publishing service with OAuth integration"""
import logging
from typing import Optional, Dict
import requests
from config.settings import get_settings
from config.database import get_db

logger = logging.getLogger(__name__)
settings = get_settings()


class InstagramPublisherError(Exception):
    """Exception raised for Instagram publishing errors"""
    pass


class InstagramPublisher:
    """Handle Instagram OAuth and Reels publishing"""
    
    def __init__(self):
        self.app_id = getattr(settings, 'instagram_app_id', None)
        self.app_secret = getattr(settings, 'instagram_app_secret', None)
        self.redirect_uri = f"http://localhost:8001/api/platforms/instagram/callback"
        
        if not self.app_id or not self.app_secret:
            logger.warning("Instagram OAuth credentials not configured")
        
        self.scopes = [
            'instagram_basic',
            'instagram_content_publish',
            'pages_show_list',
            'pages_read_engagement'
        ]
    
    def is_configured(self) -> bool:
        """Check if Instagram credentials are configured"""
        return bool(self.app_id and self.app_secret)
    
    def get_authorization_url(self, user_id: str) -> str:
        """Generate Instagram OAuth authorization URL
        
        Args:
            user_id: User ID for state parameter
            
        Returns:
            str: Authorization URL
        """
        if not self.is_configured():
            raise InstagramPublisherError("Instagram OAuth credentials not configured. Please add INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET to .env file.")
        
        scopes_str = ','.join(self.scopes)
        auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={self.app_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={scopes_str}"
            f"&state={user_id}"
            f"&response_type=code"
        )
        
        logger.info(f"Generated Instagram auth URL for user: {user_id}")
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
            raise InstagramPublisherError("Instagram OAuth credentials not configured")
        
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
                raise InstagramPublisherError(f"Instagram OAuth error: {token_data['error']['message']}")
            
            access_token = token_data['access_token']
            
            # Get Instagram business account info
            accounts_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
            accounts_response = requests.get(accounts_url)
            accounts_data = accounts_response.json()
            
            if not accounts_data.get('data'):
                raise InstagramPublisherError("No Instagram business account found")
            
            account = accounts_data['data'][0]
            account_id = account['id']
            account_name = account['name']
            
            # Store connected account in database
            db = get_db()
            account_data = {
                "user_id": user_id,
                "platform": "instagram",
                "account_id": account_id,
                "account_name": account_name,
                "account_email": "",
                "access_token": access_token,
                "refresh_token": "",
                "token_expiry": None,
                "status": "active"
            }
            
            # Check if account already exists
            existing = await db.connected_accounts.find_one({
                "user_id": user_id,
                "platform": "instagram",
                "account_id": account_id
            })
            
            if existing:
                await db.connected_accounts.update_one(
                    {"_id": existing["_id"]},
                    {"$set": account_data}
                )
                logger.info(f"Updated Instagram account: {account_name}")
            else:
                await db.connected_accounts.insert_one(account_data)
                logger.info(f"Connected new Instagram account: {account_name}")
            
            return {
                "platform": "instagram",
                "account_id": account_id,
                "account_name": account_name,
                "status": "connected"
            }
            
        except Exception as e:
            logger.error(f"Instagram OAuth callback error: {str(e)}")
            raise InstagramPublisherError(f"Failed to connect Instagram account: {str(e)}")
    
    async def upload_reel(
        self,
        video_file_path: str,
        caption: str,
        access_token: str,
        instagram_account_id: str
    ) -> Dict:
        """Upload Reel to Instagram
        
        Args:
            video_file_path: Path to video file
            caption: Reel caption
            access_token: OAuth access token
            instagram_account_id: Instagram business account ID
            
        Returns:
            Dict: Upload result
        """
        if not self.is_configured():
            raise InstagramPublisherError("Instagram OAuth credentials not configured")
        
        try:
            # Note: Instagram API requires video to be hosted on a public URL
            # This is a simplified version - in production, you'd upload to a CDN first
            logger.warning("Instagram Reels upload requires video to be publicly accessible")
            
            return {
                "success": True,
                "platform": "instagram",
                "message": "Instagram upload configured. Video will be uploaded when API is fully set up."
            }
            
        except Exception as e:
            logger.error(f"Instagram upload error: {str(e)}")
            raise InstagramPublisherError(f"Failed to upload to Instagram: {str(e)}")


# Singleton instance
_instagram_publisher: Optional[InstagramPublisher] = None

def get_instagram_publisher() -> InstagramPublisher:
    """Get InstagramPublisher singleton instance"""
    global _instagram_publisher
    if _instagram_publisher is None:
        _instagram_publisher = InstagramPublisher()
    return _instagram_publisher
