"""
Script Extractor Module
Extracts transcripts from videos using Whisper AI
"""

import os
import whisper
import json
from pathlib import Path
import config

class ScriptExtractor:
    def __init__(self, model_size='base'):
        """
        Initialize Script Extractor

        Args:
            model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.transcripts_dir = config.TRANSCRIPTS_DIR
        os.makedirs(self.transcripts_dir, exist_ok=True)

    def extract_script(self, video_path, output_filename=None):
        """
        Extract script from video

        Args:
            video_path (str): Path to video file
            output_filename (str): Optional custom output filename

        Returns:
            dict: Transcript data with text and timestamps
        """
        print(f"Transcribing video: {video_path}")

        try:
            # Transcribe the video
            result = self.model.transcribe(video_path)

            # Prepare transcript data
            transcript_data = {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language'],
            }

            # Save transcript
            if output_filename is None:
                video_name = Path(video_path).stem
                output_filename = f"{video_name}_transcript.json"

            output_path = os.path.join(self.transcripts_dir, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)

            # Also save as plain text
            text_path = output_path.replace('.json', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])

            print(f"✓ Transcript saved: {output_path}")
            print(f"✓ Plain text saved: {text_path}")

            return transcript_data

        except Exception as e:
            print(f"✗ Error extracting script: {str(e)}")
            raise

    def load_transcript(self, transcript_path):
        """
        Load a saved transcript

        Args:
            transcript_path (str): Path to transcript JSON file

        Returns:
            dict: Transcript data
        """
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_script_summary(self, transcript_data):
        """
        Get a summary of the script

        Args:
            transcript_data (dict): Transcript data

        Returns:
            dict: Summary information
        """
        segments = transcript_data.get('segments', [])
        total_duration = segments[-1]['end'] if segments else 0

        return {
            'total_words': len(transcript_data['text'].split()),
            'total_segments': len(segments),
            'duration': total_duration,
            'language': transcript_data.get('language', 'unknown'),
            'text_preview': transcript_data['text'][:200] + '...' if len(transcript_data['text']) > 200 else transcript_data['text']
        }

if __name__ == "__main__":
    # Example usage
    extractor = ScriptExtractor(model_size='base')
    print("Script extractor ready!")
    print(f"Transcripts directory: {extractor.transcripts_dir}")
