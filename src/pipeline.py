"""
Main Pipeline
Orchestrates the entire shorts generation workflow
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

from src.script_generator import ScriptGenerator
from src.voiceover_generator import VoiceoverGenerator
from src.subtitle_generator import SubtitleGenerator
from src.background_provider import BackgroundProvider
from src.video_composer import VideoComposer
from src.youtube_uploader import YouTubeUploader

class ShortsGenerationPipeline:
    def __init__(self, config_path='config.yaml'):
        """Initialize the pipeline with config"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Create output directory
        self.output_dir = Path(self.config['processing']['output_directory'])
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.script_gen = ScriptGenerator(self.config)
        self.voiceover_gen = VoiceoverGenerator(self.config)
        self.subtitle_gen = SubtitleGenerator(self.config)
        self.bg_provider = BackgroundProvider(self.config)
        self.video_composer = VideoComposer(self.config)
        
        # Initialize uploader (optional, requires auth)
        try:
            self.youtube_uploader = YouTubeUploader(self.config)
        except:
            print("⚠ YouTube uploader not available (authentication required)")
            self.youtube_uploader = None
        
        self.shorts_created = []
    
    def generate_short(self, topic=None, upload=False):
        """
        Generate a single YouTube Short
        
        Args:
            topic (str): Optional topic
            upload (bool): Whether to upload to YouTube
            
        Returns:
            dict: Metadata about created short
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_id = f"short_{timestamp}"
        short_dir = self.output_dir / short_id
        short_dir.mkdir(exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"Generating Short: {short_id}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Generate Script
            print("\n[1/5] Generating script...")
            script_data = self.script_gen.generate_script(topic)
            if not script_data:
                print("❌ Failed to generate script")
                return None
            
            print(f"Topic: {script_data['topic']}")
            print(f"Title: {script_data['title']}")
            
            # Step 2: Generate Voiceover
            print("\n[2/5] Generating voiceover...")
            audio_path = short_dir / "voiceover.wav"
            self.voiceover_gen.generate_voiceover(
                script_data['full_script'],
                str(audio_path)
            )
            
            # Step 3: Generate Subtitles
            print("\n[3/5] Generating subtitles...")
            fps = self.config['video']['fps']
            duration = self.config['video']['duration']
            subtitle_frames = self.subtitle_gen.generate_subtitle_frames(
                script_data['full_script'],
                duration,
                fps
            )
            print(f"✓ Generated {len(subtitle_frames)} subtitle frames")
            
            # Step 4: Get Background
            print("\n[4/5] Getting background video...")
            bg_path = short_dir / "background.mp4"
            background = self.bg_provider.get_background(
                search_term=script_data['topic'],
                output_path=str(bg_path)
            )
            
            if not background:
                # Create fallback
                bg_path = short_dir / "background.png"
                background = self.bg_provider.get_fallback_background(str(bg_path))
            
            # Step 5: Compose Video
            print("\n[5/5] Composing final video...")
            video_path = short_dir / "final_short.mp4"
            self.video_composer.compose_video(
                background,
                str(audio_path),
                subtitle_frames,
                str(video_path)
            )
            
            # Validate
            if not self.video_composer.validate_composition(str(video_path)):
                print("❌ Video validation failed")
                return None
            
            # Prepare metadata
            metadata = {
                'id': short_id,
                'title': script_data['title'],
                'topic': script_data['topic'],
                'description': self._generate_description(script_data),
                'tags': self.config['upload']['tags'],
                'video_path': str(video_path),
                'created_at': timestamp,
                'uploaded': False,
                'video_id': None
            }
            
            self.shorts_created.append(metadata)
            
            # Upload if requested
            if upload and self.youtube_uploader:
                print("\n[BONUS] Uploading to YouTube...")
                video_id = self.youtube_uploader.upload_short(
                    video_path=str(video_path),
                    title=metadata['title'],
                    description=metadata['description'],
                    tags=metadata['tags']
                )
                
                if video_id:
                    metadata['uploaded'] = True
                    metadata['video_id'] = video_id
            
            self._save_metadata(short_dir, metadata)
            
            print(f"\n✅ Short created successfully!")
            print(f"Location: {video_path}")
            
            return metadata
            
        except Exception as e:
            print(f"\n❌ Error generating short: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_batch(self, count=5, upload=False):
        """Generate multiple shorts"""
        print(f"\nGenerating batch of {count} shorts...")
        
        for i in range(count):
            print(f"\n>>> Short {i+1}/{count}")
            self.generate_short(upload=upload)
    
    def _generate_description(self, script_data):
        """Generate YouTube description from script"""
        template = self.config['upload']['description_template']
        description = template.replace(
            "{topic}",
            script_data['topic']
        )
        return description
    
    def _save_metadata(self, output_dir, metadata):
        """Save metadata about generated short"""
        import json
        metadata_path = output_dir / "metadata.json"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_stats(self):
        """Get pipeline statistics"""
        stats = {
            'shorts_created': len(self.shorts_created),
            'shorts_uploaded': sum(1 for s in self.shorts_created if s['uploaded']),
            'output_directory': str(self.output_dir)
        }
        
        if self.youtube_uploader:
            try:
                channel_info = self.youtube_uploader.get_channel_info()
                if channel_info:
                    stats['channel'] = channel_info
            except:
                pass
        
        return stats
    
    def print_stats(self):
        """Print pipeline statistics"""
        stats = self.get_stats()
        
        print(f"\n{'='*60}")
        print(f"Pipeline Statistics")
        print(f"{'='*60}")
        print(f"Shorts Created: {stats['shorts_created']}")
        print(f"Shorts Uploaded: {stats['shorts_uploaded']}")
        print(f"Output Directory: {stats['output_directory']}")
        
        if 'channel' in stats:
            channel = stats['channel']
            print(f"\nChannel Info:")
            print(f"  Name: {channel['channel_name']}")
            print(f"  Subscribers: {channel['subscribers']}")
            print(f"  Total Views: {channel['views']}")
