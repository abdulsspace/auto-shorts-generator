"""
Voiceover Generator Module
Creates audio voiceovers from scripts using free TTS services
"""

import os
from gtts import gTTS
from pydub import AudioSegment
import tempfile

class VoiceoverGenerator:
    def __init__(self, config):
        """Initialize voiceover generator"""
        self.config = config
        self.provider = config['audio']['provider']
        self.language = config['audio']['language']
        self.sample_rate = config['audio']['sample_rate']
    
    def generate_voiceover(self, script, output_path):
        """
        Generate voiceover audio from script text
        
        Args:
            script (str): Text to convert to speech
            output_path (str): Where to save the audio file
            
        Returns:
            str: Path to generated audio file
        """
        if self.provider == "gtts":
            return self._generate_gtts(script, output_path)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _generate_gtts(self, script, output_path):
        """Generate voiceover using Google Text-to-Speech (FREE)"""
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Generate speech
            tts = gTTS(text=script, lang=self.language, slow=False)
            tts.save(tmp_path)
            
            # Convert to wav for better compatibility
            audio = AudioSegment.from_mp3(tmp_path)
            audio.export(output_path, format="wav")
            
            # Cleanup
            os.remove(tmp_path)
            
            print(f"✓ Voiceover generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating voiceover: {e}")
            return None
    
    def adjust_speed(self, audio_path, speed_factor=1.0):
        """
        Adjust audio playback speed
        
        Args:
            audio_path (str): Path to audio file
            speed_factor (float): Speed multiplier (1.0 = normal, 0.8 = slower, 1.2 = faster)
            
        Returns:
            AudioSegment: Modified audio
        """
        audio = AudioSegment.from_wav(audio_path)
        
        if speed_factor != 1.0:
            # Speed up or slow down by changing frame rate
            audio = audio.speedup(playback_speed=speed_factor)
        
        return audio
    
    def add_audio_effects(self, audio_path, effects=None):
        """
        Add audio effects (fade in/out, normalization)
        
        Args:
            audio_path (str): Path to audio file
            effects (list): List of effects to apply
            
        Returns:
            AudioSegment: Modified audio
        """
        audio = AudioSegment.from_wav(audio_path)
        
        if not effects:
            effects = ['fade_in', 'fade_out']
        
        if 'fade_in' in effects:
            audio = audio.fade_in(duration=500)  # 500ms fade in
        
        if 'fade_out' in effects:
            audio = audio.fade_out(duration=500)  # 500ms fade out
        
        if 'normalize' in effects:
            # Normalize volume
            max_amplitude = audio.max
            if max_amplitude > 0:
                normalized = audio.apply_gain(-(max_amplitude - (-1)))
                return normalized
        
        return audio
    
    def export_audio(self, audio, output_path, format="wav"):
        """Export audio to file"""
        audio.export(output_path, format=format)
        print(f"✓ Audio exported: {output_path}")
        return output_path
