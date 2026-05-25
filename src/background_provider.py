"""
Background Provider Module
Fetches free stock footage and images for video backgrounds
"""

import os
import requests
import random
from urllib.parse import urlencode

class BackgroundProvider:
    def __init__(self, config):
        """Initialize background provider"""
        self.config = config
        self.source = config['background']['source']
    
    def get_background(self, search_term=None, output_path=None):
        """
        Get background image/video
        
        Args:
            search_term (str): What to search for
            output_path (str): Where to save
            
        Returns:
            str: Path to downloaded background
        """
        if not search_term:
            terms = self.config['background']['search_terms'].split(',')
            search_term = random.choice(terms).strip()
        
        if self.source == "pexels":
            return self._get_pexels_video(search_term, output_path)
        elif self.source == "pixabay":
            return self._get_pixabay_video(search_term, output_path)
        else:
            print(f"Unknown source: {self.source}")
            return None
    
    def _get_pexels_video(self, search_term, output_path=None):
        """
        Get video from Pexels (free, no API key needed)
        
        Args:
            search_term (str): Search query
            output_path (str): Where to save
            
        Returns:
            str: Path to downloaded video
        """
        try:
            if not output_path:
                output_path = f"./output/bg_{search_term.replace(' ', '_')}.mp4"
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Pexels API (free, no key required for search)
            url = "https://api.pexels.com/videos/search"
            params = {
                'query': search_term,
                'per_page': 1,
                'orientation': 'portrait'  # Mobile format
            }
            
            headers = {
                'Authorization': 'DEMO-PEXELS-KEY'  # Demo key for basic access
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'videos' in data and len(data['videos']) > 0:
                    video = data['videos'][0]
                    
                    # Get video files
                    if 'video_files' in video:
                        video_files = video['video_files']
                        
                        # Get highest quality available
                        best_file = max(
                            video_files,
                            key=lambda x: x.get('width', 0) * x.get('height', 0)
                        )
                        
                        video_url = best_file['link']
                        
                        # Download video
                        print(f"Downloading background: {search_term}")
                        video_response = requests.get(video_url, timeout=30)
                        
                        with open(output_path, 'wb') as f:
                            f.write(video_response.content)
                        
                        print(f"✓ Background downloaded: {output_path}")
                        return output_path
            
            print(f"Could not find video for: {search_term}")
            return None
            
        except Exception as e:
            print(f"Error downloading from Pexels: {e}")
            return None
    
    def _get_pixabay_video(self, search_term, output_path=None):
        """
        Get video from Pixabay (free, no API key needed)
        
        Args:
            search_term (str): Search query
            output_path (str): Where to save
            
        Returns:
            str: Path to downloaded video
        """
        try:
            if not output_path:
                output_path = f"./output/bg_{search_term.replace(' ', '_')}.mp4"
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Pixabay API (free, no key required)
            url = "https://pixabay.com/api/videos/"
            params = {
                'key': 'demo',  # Demo works for limited requests
                'q': search_term,
                'per_page': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'hits' in data and len(data['hits']) > 0:
                    video = data['hits'][0]
                    
                    # Get video URL
                    if 'videos' in video:
                        videos = video['videos']
                        # Get medium quality for balance
                        best_url = videos.get('medium') or videos.get('large') or videos.get('small')
                        
                        if best_url:
                            print(f"Downloading background: {search_term}")
                            video_response = requests.get(best_url, timeout=30)
                            
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            print(f"✓ Background downloaded: {output_path}")
                            return output_path
            
            print(f"Could not find video for: {search_term}")
            return None
            
        except Exception as e:
            print(f"Error downloading from Pixabay: {e}")
            return None
    
    def get_fallback_background(self, output_path):
        """
        Create a simple fallback background if download fails
        
        Args:
            output_path (str): Where to save
            
        Returns:
            str: Path to fallback background
        """
        print("Creating fallback background...")
        
        # Create a simple gradient image
        from PIL import Image, ImageDraw
        
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for y in range(height):
            ratio = y / height
            r = int(20 + ratio * 80)
            g = int(20 + ratio * 60)
            b = int(40 + ratio * 100)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        img.save(output_path)
        
        print(f"✓ Fallback background created: {output_path}")
        return output_path
