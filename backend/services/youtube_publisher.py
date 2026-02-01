"""YouTube publishing service with OAuth integration"""
import logging
from typing import Optional, Dict
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from config.settings import get_settings
from config.database import get_db

logger = logging.getLogger(__name__)
settings = get_settings()


class YouTubePublisherError(Exception):
    """Exception raised for YouTube publishing errors"""
    pass


class YouTubePublisher:
    """Handle YouTube OAuth and video publishing"""
    
    def __init__(self):
        self.client_id = settings.youtube_client_id
        self.client_secret = settings.youtube_client_secret
        self.redirect_uri = f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')}/api/platforms/youtube/callback"
        
        if not self.client_id or not self.client_secret:
            logger.warning("YouTube OAuth credentials not configured")
        
        self.scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
    
    def get_authorization_url(self, user_id: str) -> str:
        """Generate YouTube OAuth authorization URL
        
        Args:
            user_id: User ID for state parameter
            
        Returns:
            str: Authorization URL
        """
        if not self.client_id or not self.client_secret:
            raise YouTubePublisherError("YouTube OAuth credentials not configured")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=user_id,
            prompt='consent'
        )
        
        logger.info(f"Generated YouTube auth URL for user: {user_id}")
        return authorization_url
    
    async def handle_oauth_callback(self, code: str, user_id: str) -> Dict:
        """Handle OAuth callback and store tokens
        
        Args:
            code: Authorization code from callback
            user_id: User ID from state parameter
            
        Returns:
            Dict: Account information
        """
        if not self.client_id or not self.client_secret:
            raise YouTubePublisherError("YouTube OAuth credentials not configured")
        
        try:
            # Exchange code for tokens
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Get user's YouTube channel info
            youtube = build('youtube', 'v3', credentials=credentials)
            channels_response = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                raise YouTubePublisherError("No YouTube channel found for this account")
            
            channel = channels_response['items'][0]
            channel_id = channel['id']
            channel_title = channel['snippet']['title']
            
            # Store connected account in database
            db = get_db()
            account_data = {
                "user_id": user_id,
                "platform": "youtube",
                "account_id": channel_id,
                "account_name": channel_title,
                "account_email": "",  # YouTube API doesn't provide email directly
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
                "status": "active"
            }
            
            # Check if account already exists
            existing = await db.connected_accounts.find_one({
                "user_id": user_id,
                "platform": "youtube",
                "account_id": channel_id
            })
            
            if existing:
                # Update existing account
                await db.connected_accounts.update_one(
                    {"_id": existing["_id"]},
                    {"$set": account_data}
                )
                logger.info(f"Updated YouTube account: {channel_title}")
            else:
                # Insert new account
                await db.connected_accounts.insert_one(account_data)
                logger.info(f"Connected new YouTube account: {channel_title}")
            
            return {
                "platform": "youtube",
                "account_id": channel_id,
                "account_name": channel_title,
                "status": "connected"
            }
            
        except Exception as e:
            logger.error(f"YouTube OAuth callback error: {str(e)}")
            raise YouTubePublisherError(f"Failed to connect YouTube account: {str(e)}")
    
    async def upload_video(
        self,
        video_file_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",
        access_token: str = None,
        refresh_token: str = None
    ) -> Dict:
        """Upload video to YouTube
        
        Args:
            video_file_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (default: 22 = People & Blogs)
            privacy_status: public/private/unlisted
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            
        Returns:
            Dict: Upload result with video URL
        """
        try:
            # Create credentials object
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            
            # Build YouTube service
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            video_url = f"https://www.youtube.com/shorts/{video_id}"
            
            logger.info(f"Successfully uploaded video to YouTube: {video_id}")
            
            return {
                "success": True,
                "platform": "youtube",
                "video_id": video_id,
                "url": video_url,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"YouTube upload error: {str(e)}")
            raise YouTubePublisherError(f"Failed to upload to YouTube: {str(e)}")


# Singleton instance
_youtube_publisher: Optional[YouTubePublisher] = None

def get_youtube_publisher() -> YouTubePublisher:
    """Get YouTubePublisher singleton instance"""
    global _youtube_publisher
    if _youtube_publisher is None:
        _youtube_publisher = YouTubePublisher()
    return _youtube_publisher
