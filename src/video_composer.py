"""
Video Composer Module
Combines background video, voiceover, and subtitles into final video
"""

import os
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip, 
    CompositeVideoClip, TextClip, concatenate_videoclips
)
from PIL import Image
import numpy as np

class VideoComposer:
    def __init__(self, config):
        """Initialize video composer"""
        self.config = config
        self.resolution = tuple(map(int, config['video']['resolution'].split('x')))
        self.fps = config['video']['fps']
        self.duration = config['video']['duration']
    
    def compose_video(self, background_path, audio_path, subtitle_frames, output_path):
        """
        Compose final video from components
        
        Args:
            background_path (str): Path to background video or image
            audio_path (str): Path to voiceover audio
            subtitle_frames (list): List of PIL Images with subtitles
            output_path (str): Output video path
            
        Returns:
            str: Path to composed video
        """
        try:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            # Load or generate background
            if background_path.endswith(('.mp4', '.avi', '.mov')):
                # Use video background
                from moviepy.editor import VideoFileClip
                bg_clip = VideoFileClip(background_path)
                # Trim to duration
                bg_clip = bg_clip.subclipped(0, min(audio_duration, self.duration))
            else:
                # Use image background and loop/extend
                bg_clip = self._create_image_background(background_path, audio_duration)
            
            # Create subtitle video from frames
            subtitle_clip = self._create_subtitle_video(subtitle_frames, audio_duration)
            
            # Composite video and subtitles
            final_video = CompositeVideoClip([bg_clip, subtitle_clip])
            
            # Set audio
            final_video = final_video.set_audio(audio_clip)
            
            # Set duration
            final_video = final_video.set_duration(audio_duration)
            
            # Write to file
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            bg_clip.close()
            audio_clip.close()
            
            print(f"✓ Video composed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error composing video: {e}")
            return None
    
    def _create_image_background(self, image_path, duration):
        """Create video background from static image"""
        img = Image.open(image_path)
        
        # Resize to resolution
        img = img.resize(self.resolution)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Create clip
        clip = ImageClip(img_array).set_duration(duration)
        return clip
    
    def _create_subtitle_video(self, subtitle_frames, duration):
        """Create video clip from subtitle frames"""
        # Calculate frame rate needed
        num_frames = len(subtitle_frames)
        fps_needed = num_frames / duration
        
        # Create numpy arrays from PIL images
        frame_arrays = []
        for frame in subtitle_frames:
            # Convert RGBA to RGB if needed
            if frame.mode == 'RGBA':
                rgb_frame = Image.new('RGB', frame.size, (0, 0, 0))
                rgb_frame.paste(frame, mask=frame.split()[3])
                frame_arrays.append(np.array(rgb_frame))
            else:
                frame_arrays.append(np.array(frame))
        
        # Create video clip from frames
        # Use ImageSequenceClip if available, otherwise create composite
        try:
            from moviepy.editor import ImageSequenceClip
            clip = ImageSequenceClip(frame_arrays, fps=fps_needed)
        except:
            # Fallback: use first frame
            clip = ImageClip(frame_arrays[0]).set_duration(duration)
        
        return clip
    
    def add_effects(self, video_path, effects=None):
        """
        Add effects to video
        
        Args:
            video_path (str): Path to video
            effects (list): List of effects to apply
            
        Returns:
            VideoClip: Modified video
        """
        from moviepy.editor import VideoFileClip, vfx
        
        video = VideoFileClip(video_path)
        
        if not effects:
            effects = []
        
        if 'fade_in' in effects:
            video = video.fx(vfx.fadein, duration=0.5)
        
        if 'fade_out' in effects:
            video = video.fx(vfx.fadeout, duration=0.5)
        
        if 'brightness' in effects:
            video = video.fx(vfx.colorx, 1.1)  # 10% brighter
        
        return video
    
    def validate_composition(self, output_path):
        """Validate that video was created correctly"""
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✓ Video validated: {output_path}")
            return True
        else:
            print(f"✗ Video validation failed: {output_path}")
            return False
