"""
YouTube Uploader Module
Handles uploading videos to YouTube Shorts
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

class YouTubeUploader:
    def __init__(self, config, credentials_file='credentials.json'):
        """
        Initialize YouTube uploader
        
        Args:
            config (dict): Configuration dictionary
            credentials_file (str): Path to credentials JSON file
        """
        self.config = config
        self.credentials_file = credentials_file
        self.youtube = None
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        # Authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        # Check if token.pickle exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ {self.credentials_file} not found!")
                    print("Please follow the setup instructions in README.md")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the token for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✓ YouTube authentication successful")
        return True
    
    def upload_short(self, video_path, title, description, tags=None, playlist_id=None):
        """
        Upload video as YouTube Short
        
        Args:
            video_path (str): Path to video file
            title (str): Video title
            description (str): Video description
            tags (list): List of tags/keywords
            playlist_id (str): Optional playlist ID to add to
            
        Returns:
            str: Video ID if successful, None otherwise
        """
        try:
            if not os.path.exists(video_path):
                print(f"❌ Video file not found: {video_path}")
                return None
            
            print(f"Uploading: {title}")
            
            # Prepare request body
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '24',  # Entertainment category
                    'defaultLanguage': 'en'
                },
                'status': {
                    'privacyStatus': 'public',
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=MediaFileUpload(
                    video_path,
                    mimetype='video/mp4',
                    resumable=True
                )
            )
            
            # Execute with resumable upload
            response = None
            status = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        file_size = os.path.getsize(video_path)
                        progress = int(status.progress() * 100)
                        print(f"  Upload progress: {progress}%")
                except Exception as e:
                    print(f"  Error during upload: {e}")
                    return None
            
            video_id = response['id']
            print(f"✓ Video uploaded successfully!")
            print(f"  Video ID: {video_id}")
            print(f"  URL: https://www.youtube.com/watch?v={video_id}")
            
            # Add to playlist if specified
            if playlist_id:
                self._add_to_playlist(video_id, playlist_id)
            
            return video_id
            
        except Exception as e:
            print(f"❌ Error uploading video: {e}")
            return None
    
    def _add_to_playlist(self, video_id, playlist_id):
        """Add video to playlist"""
        try:
            request = self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            )
            
            request.execute()
            print(f"✓ Added to playlist: {playlist_id}")
            
        except Exception as e:
            print(f"⚠ Could not add to playlist: {e}")
    
    def get_channel_info(self):
        """Get authenticated channel info"""
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'channel_id': channel['id'],
                    'channel_name': channel['snippet']['title'],
                    'subscribers': channel['statistics'].get('subscriberCount', 'Private'),
                    'views': channel['statistics'].get('viewCount', 0)
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None
    
    def batch_upload(self, videos_data):
        """
        Upload multiple videos
        
        Args:
            videos_data (list): List of dicts with video_path, title, description, tags
            
        Returns:
            list: List of uploaded video IDs
        """
        uploaded_ids = []
        
        for i, video_info in enumerate(videos_data, 1):
            print(f"\n[{i}/{len(videos_data)}] Uploading video...")
            video_id = self.upload_short(
                video_path=video_info['video_path'],
                title=video_info['title'],
                description=video_info['description'],
                tags=video_info.get('tags'),
                playlist_id=video_info.get('playlist_id')
            )
            
            if video_id:
                uploaded_ids.append(video_id)
        
        print(f"\n✓ Batch upload complete! {len(uploaded_ids)}/{len(videos_data)} videos uploaded")
        return uploaded_ids
