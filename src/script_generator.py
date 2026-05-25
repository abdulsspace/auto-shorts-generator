"""
Script Generator Module
Generates engaging scripts for YouTube Shorts using Google Gemini API
"""

import os
import random
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class ScriptGenerator:
    def __init__(self, config):
        """Initialize script generator with API and config"""
        self.config = config
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_script(self, topic=None):
        """
        Generate an engaging short video script
        
        Args:
            topic (str): Optional specific topic, otherwise random from config
            
        Returns:
            dict: Contains title, script, and metadata
        """
        if not topic:
            topics = self.config['script_generation']['topics']
            topic = random.choice(topics)
        
        prompt = self._build_prompt(topic)
        
        try:
            response = self.model.generate_content(prompt)
            script_text = response.text
            
            # Parse response
            script_data = self._parse_response(script_text, topic)
            return script_data
            
        except Exception as e:
            print(f"Error generating script: {e}")
            return None
    
    def _build_prompt(self, topic):
        """Build the prompt for Gemini"""
        max_length = self.config['script_generation']['max_length']
        tone = self.config['script_generation']['tone']
        
        prompt = f"""
        Create a viral YouTube Short script about: {topic}
        
        Requirements:
        - Maximum {max_length} words
        - Tone: {tone}, engaging, hook viewers immediately
        - Start with a hook that makes people stop scrolling
        - Add one surprising fact or twist
        - End with a call-to-action (subscribe, like, comment)
        - Use simple, conversational language
        - Include [PAUSE] markers for timing
        
        Format your response as:
        TITLE: [title here]
        HOOK: [first 10 seconds - the attention grabber]
        MAIN: [main content]
        TWIST: [surprising fact or revelation]
        CTA: [call to action]
        
        Make it punchy and memorable!
        """
        
        return prompt
    
    def _parse_response(self, response, topic):
        """Parse Gemini response into structured data"""
        lines = response.strip().split('\n')
        
        data = {
            'title': '',
            'hook': '',
            'main': '',
            'twist': '',
            'cta': '',
            'topic': topic,
            'full_script': ''
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TITLE:'):
                current_section = 'title'
                data['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('HOOK:'):
                current_section = 'hook'
                data['hook'] = line.replace('HOOK:', '').strip()
            elif line.startswith('MAIN:'):
                current_section = 'main'
                data['main'] = line.replace('MAIN:', '').strip()
            elif line.startswith('TWIST:'):
                current_section = 'twist'
                data['twist'] = line.replace('TWIST:', '').strip()
            elif line.startswith('CTA:'):
                current_section = 'cta'
                data['cta'] = line.replace('CTA:', '').strip()
            elif current_section and line:
                data[current_section] += ' ' + line
        
        # Combine into full script
        data['full_script'] = f"{data['hook']} {data['main']} {data['twist']} {data['cta']}"
        
        return data
    
    def generate_batch(self, count=5):
        """Generate multiple scripts at once"""
        scripts = []
        for i in range(count):
            print(f"Generating script {i+1}/{count}...")
            script = self.generate_script()
            if script:
                scripts.append(script)
        
        return scripts
