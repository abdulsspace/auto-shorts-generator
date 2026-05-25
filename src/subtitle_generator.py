"""
Subtitle Generator Module
Creates animated subtitles for videos
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap

class SubtitleGenerator:
    def __init__(self, config):
        """Initialize subtitle generator"""
        self.config = config
        self.font_size = config['subtitles']['font_size']
        self.font_color = config['subtitles']['font_color']
        self.outline_color = config['subtitles']['outline_color']
        self.outline_width = config['subtitles']['outline_width']
        self.position = config['subtitles']['position']
        self.animation = config['subtitles']['animation']
    
    def generate_subtitle_frames(self, text, duration, fps, resolution="1080x1920"):
        """
        Generate subtitle frames for video
        
        Args:
            text (str): Subtitle text
            duration (float): Duration in seconds
            fps (int): Frames per second
            resolution (str): Video resolution "WxH"
            
        Returns:
            list: List of PIL Image objects with subtitles
        """
        width, height = map(int, resolution.split('x'))
        total_frames = int(duration * fps)
        frames = []
        
        # Split text into lines for wrapping
        wrapped_lines = self._wrap_text(text, width)
        
        # Calculate animation timing
        fade_in_frames = int(fps * 0.5)  # 0.5 second fade in
        display_frames = total_frames - fade_in_frames * 2
        fade_out_frames = int(fps * 0.5)  # 0.5 second fade out
        
        for frame_num in range(total_frames):
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Calculate opacity based on animation type
            opacity = self._calculate_opacity(
                frame_num, 
                fade_in_frames, 
                display_frames, 
                fade_out_frames,
                self.animation
            )
            
            if opacity > 0:
                self._draw_text(
                    draw, 
                    wrapped_lines, 
                    width, 
                    height, 
                    opacity
                )
            
            frames.append(img)
        
        return frames
    
    def _wrap_text(self, text, width, chars_per_line=20):
        """Wrap text to fit on screen"""
        return textwrap.wrap(text, width=chars_per_line)
    
    def _calculate_opacity(self, frame, fade_in, display, fade_out, animation):
        """Calculate subtitle opacity for animation effect"""
        if animation == "fade":
            if frame < fade_in:
                return int(255 * (frame / fade_in))
            elif frame < fade_in + display:
                return 255
            else:
                remaining = fade_out - (frame - fade_in - display)
                return int(255 * (remaining / fade_out)) if remaining > 0 else 0
        
        elif animation == "typewriter":
            # All visible except fade out
            if frame < fade_in + display + fade_out * 0.5:
                return 255
            else:
                remaining = fade_out - (frame - fade_in - display)
                return int(255 * (remaining / fade_out)) if remaining > 0 else 0
        
        else:  # slide
            return 255 if frame < fade_in + display + fade_out else 0
    
    def _draw_text(self, draw, lines, width, height, opacity):
        """Draw text on image with effects"""
        try:
            # Try to load a nice font, fallback to default
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_height = len(lines) * self.font_size
        
        if self.position == "bottom":
            y_pos = height - text_height - 50
        elif self.position == "top":
            y_pos = 50
        else:  # center
            y_pos = (height - text_height) // 2
        
        # Draw each line
        x_start = 30
        for i, line in enumerate(lines):
            y = y_pos + i * self.font_size
            
            # Create text color with opacity
            text_color = (*self._hex_to_rgb(self.font_color), opacity)
            outline_color = (*self._hex_to_rgb(self.outline_color), opacity)
            
            # Draw outline
            for adj_x in range(-self.outline_width, self.outline_width + 1):
                for adj_y in range(-self.outline_width, self.outline_width + 1):
                    if adj_x != 0 or adj_y != 0:
                        draw.text(
                            (x_start + adj_x, y + adj_y),
                            line,
                            font=font,
                            fill=outline_color
                        )
            
            # Draw main text
            draw.text((x_start, y), line, font=font, fill=text_color)
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def split_subtitles(self, full_text, num_chunks=3):
        """
        Split text into chunks for paced display
        
        Args:
            full_text (str): Complete text
            num_chunks (int): Number of sections to split into
            
        Returns:
            list: List of text chunks
        """
        words = full_text.split()
        chunk_size = len(words) // num_chunks
        
        chunks = []
        for i in range(num_chunks):
            start = i * chunk_size
            end = start + chunk_size if i < num_chunks - 1 else len(words)
            chunks.append(' '.join(words[start:end]))
        
        return chunks
