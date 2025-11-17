"""
Voice Generator Module
Generates voices using ElevenLabs API
"""

import os
import requests
import config

class VoiceGenerator:
    def __init__(self):
        """Initialize Voice Generator"""
        self.api_key = config.ELEVENLABS_API_KEY
        self.audio_dir = config.AUDIO_DIR
        os.makedirs(self.audio_dir, exist_ok=True)

        # ElevenLabs API endpoints
        self.base_url = "https://api.elevenlabs.io/v1"

        # Popular voice IDs (you can get more from ElevenLabs dashboard)
        self.preset_voices = {
            'male_1': '21m00Tcm4TlvDq8ikWAM',  # Rachel (actually female, but keeping for example)
            'male_2': 'AZnzlk1XvdvUeBnXmlld',  # Domi
            'female_1': 'EXAVITQu4vr4xnSDxMaL',  # Bella
            'female_2': 'ErXwobaYiN019PkySvjV',  # Antoni
            'male_energetic': 'VR6AewLTigWG4xSOukaG',  # Arnold
            'female_calm': 'MF3mGyEYCl7XYWbV9V6O',  # Elli
        }

    def list_available_voices(self):
        """
        Get list of available voices from ElevenLabs

        Returns:
            list: Available voices
        """
        if not self.api_key:
            print("⚠ ElevenLabs API key not set. Using preset voice IDs.")
            return self.preset_voices

        try:
            headers = {
                "xi-api-key": self.api_key
            }
            response = requests.get(f"{self.base_url}/voices", headers=headers)
            response.raise_for_status()

            voices = response.json()['voices']
            return {voice['name']: voice['voice_id'] for voice in voices}

        except Exception as e:
            print(f"⚠ Error fetching voices: {str(e)}")
            print("Using preset voice IDs instead.")
            return self.preset_voices

    def generate_audio(self, text, voice_id=None, voice_name='male_1', output_filename=None):
        """
        Generate audio from text using ElevenLabs

        Args:
            text (str): Text to convert to speech
            voice_id (str): Optional voice ID (overrides voice_name)
            voice_name (str): Preset voice name
            output_filename (str): Optional custom output filename

        Returns:
            str: Path to generated audio file
        """
        if not self.api_key:
            print("⚠ ElevenLabs API key not set. Cannot generate audio.")
            print("Please set ELEVENLABS_API_KEY in your .env file")
            return None

        # Get voice ID
        if voice_id is None:
            voice_id = self.preset_voices.get(voice_name, self.preset_voices['male_1'])

        print(f"Generating audio with voice: {voice_name} ({voice_id})")

        # Prepare output filename
        if output_filename is None:
            output_filename = f"audio_{voice_name}_{len(text)}.mp3"

        output_path = os.path.join(self.audio_dir, output_filename)

        try:
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=data
            )
            response.raise_for_status()

            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✓ Audio generated: {output_path}")
            return output_path

        except Exception as e:
            print(f"✗ Error generating audio: {str(e)}")
            raise

    def generate_multiple_voices(self, text, voice_names=None, base_filename='audio'):
        """
        Generate audio with multiple different voices

        Args:
            text (str): Text to convert
            voice_names (list): List of voice names to use
            base_filename (str): Base filename for outputs

        Returns:
            list: Paths to generated audio files
        """
        if voice_names is None:
            voice_names = ['male_1', 'male_2', 'female_1', 'female_2']

        audio_files = []

        for i, voice_name in enumerate(voice_names, 1):
            output_filename = f"{base_filename}_voice_{i}_{voice_name}.mp3"
            try:
                audio_path = self.generate_audio(text, voice_name=voice_name, output_filename=output_filename)
                if audio_path:
                    audio_files.append({
                        'voice_name': voice_name,
                        'path': audio_path,
                        'variation_number': i
                    })
            except Exception as e:
                print(f"⚠ Skipping voice {voice_name}: {str(e)}")

        return audio_files

if __name__ == "__main__":
    # Example usage
    generator = VoiceGenerator()
    print("Voice generator ready!")
    print(f"Audio directory: {generator.audio_dir}")
    print(f"Available preset voices: {list(generator.preset_voices.keys())}")
