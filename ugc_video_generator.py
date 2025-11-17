#!/usr/bin/env python3
"""
UGC Video Variation Generator
Main orchestration script for creating AI-generated variations of UGC videos
"""

import argparse
import json
import os
from pathlib import Path

from modules.video_downloader import VideoDownloader
from modules.script_extractor import ScriptExtractor
from modules.script_variation_generator import ScriptVariationGenerator
from modules.voice_generator import VoiceGenerator
from modules.avatar_generator import AvatarGenerator
import config

class UGCVideoGenerator:
    def __init__(self):
        """Initialize the UGC Video Generator"""
        self.downloader = VideoDownloader()
        self.extractor = None  # Lazy load (Whisper model is heavy)
        self.script_generator = ScriptVariationGenerator()
        self.voice_generator = VoiceGenerator()
        self.avatar_generator = None  # Will be initialized based on service choice

    def process_video_url(self, url, num_variations=3, avatar_service='heygen'):
        """
        Complete workflow: Download video, extract script, create variations

        Args:
            url (str): YouTube video URL
            num_variations (int): Number of variations to create
            avatar_service (str): 'heygen' or 'did'

        Returns:
            dict: Results of the process
        """
        print("="*60)
        print("UGC VIDEO VARIATION GENERATOR")
        print("="*60)

        # Step 1: Download video
        print("\n[Step 1/5] Downloading video...")
        video_path = self.downloader.download(url)
        video_name = Path(video_path).stem

        # Step 2: Extract script
        print("\n[Step 2/5] Extracting script from video...")
        if self.extractor is None:
            self.extractor = ScriptExtractor(model_size='base')

        transcript_data = self.extractor.extract_script(video_path)
        original_script = transcript_data['text']

        print(f"\nOriginal Script Preview:")
        print("-" * 60)
        print(original_script[:300] + "..." if len(original_script) > 300 else original_script)
        print("-" * 60)

        # Step 3: Generate script variations
        print(f"\n[Step 3/5] Generating {num_variations} script variations...")
        variations = self.script_generator.generate_variations(
            original_script,
            num_variations=num_variations
        )

        self.script_generator.save_variations(variations, video_name)

        # Step 4: Generate voice variations
        print(f"\n[Step 4/5] Generating voice variations...")
        voice_files = []
        voice_names = ['male_1', 'male_2', 'female_1', 'female_2', 'male_energetic']

        for i, variation in enumerate(variations):
            voice_name = voice_names[i % len(voice_names)]
            print(f"\nGenerating voice for variation {i+1} ({voice_name})...")

            try:
                audio_path = self.voice_generator.generate_audio(
                    text=variation['script'],
                    voice_name=voice_name,
                    output_filename=f"{video_name}_variation_{i+1}.mp3"
                )
                if audio_path:
                    voice_files.append({
                        'variation_number': i + 1,
                        'audio_path': audio_path,
                        'voice_name': voice_name
                    })
            except Exception as e:
                print(f"⚠ Error generating voice: {str(e)}")
                voice_files.append({
                    'variation_number': i + 1,
                    'audio_path': None,
                    'voice_name': voice_name,
                    'error': str(e)
                })

        # Step 5: Generate avatar videos (optional - requires API keys)
        print(f"\n[Step 5/5] Generating avatar videos...")

        if config.HEYGEN_API_KEY or config.DID_API_KEY:
            self.avatar_generator = AvatarGenerator(service=avatar_service)

            avatar_jobs = self.avatar_generator.create_variations(variations)

            print(f"\n✓ Created {len(avatar_jobs)} avatar video jobs")
            print("Videos are being generated. You can check their status later.")

        else:
            print("⚠ No avatar API keys configured. Skipping avatar generation.")
            print("To generate avatar videos, set HEYGEN_API_KEY or DID_API_KEY in .env")
            avatar_jobs = []

        # Summary
        print("\n" + "="*60)
        print("GENERATION COMPLETE!")
        print("="*60)
        print(f"Original video: {video_path}")
        print(f"Script variations: {len(variations)}")
        print(f"Voice files generated: {len([v for v in voice_files if v.get('audio_path')])}")
        print(f"Avatar jobs created: {len(avatar_jobs)}")
        print(f"\nOutput directory: {config.OUTPUT_DIR}")
        print("="*60)

        return {
            'video_path': video_path,
            'video_name': video_name,
            'original_script': original_script,
            'variations': variations,
            'voice_files': voice_files,
            'avatar_jobs': avatar_jobs
        }

    def process_local_video(self, video_path, num_variations=3):
        """
        Process a local video file

        Args:
            video_path (str): Path to local video file
            num_variations (int): Number of variations to create

        Returns:
            dict: Results of the process
        """
        print(f"Processing local video: {video_path}")

        video_name = Path(video_path).stem

        # Extract script
        if self.extractor is None:
            self.extractor = ScriptExtractor(model_size='base')

        transcript_data = self.extractor.extract_script(video_path)
        original_script = transcript_data['text']

        # Generate variations
        variations = self.script_generator.generate_variations(
            original_script,
            num_variations=num_variations
        )

        self.script_generator.save_variations(variations, video_name)

        return {
            'video_path': video_path,
            'video_name': video_name,
            'variations': variations
        }

    def create_variations_from_script(self, script_text, base_name, num_variations=3):
        """
        Create variations from a script (no video needed)

        Args:
            script_text (str): Original script text
            base_name (str): Base name for output files
            num_variations (int): Number of variations

        Returns:
            list: Script variations
        """
        print(f"Creating {num_variations} variations from script...")

        variations = self.script_generator.generate_variations(
            script_text,
            num_variations=num_variations
        )

        self.script_generator.save_variations(variations, base_name)

        return variations


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='UGC Video Variation Generator - Create AI variations of product review videos'
    )

    parser.add_argument(
        '--url',
        help='YouTube video URL to process'
    )

    parser.add_argument(
        '--video',
        help='Local video file path'
    )

    parser.add_argument(
        '--script',
        help='Text script file path'
    )

    parser.add_argument(
        '--variations',
        type=int,
        default=3,
        help='Number of variations to generate (default: 3)'
    )

    parser.add_argument(
        '--avatar-service',
        choices=['heygen', 'did'],
        default='heygen',
        help='Avatar generation service (default: heygen)'
    )

    args = parser.parse_args()

    generator = UGCVideoGenerator()

    if args.url:
        # Process YouTube URL
        generator.process_video_url(
            url=args.url,
            num_variations=args.variations,
            avatar_service=args.avatar_service
        )

    elif args.video:
        # Process local video
        generator.process_local_video(
            video_path=args.video,
            num_variations=args.variations
        )

    elif args.script:
        # Process script file
        with open(args.script, 'r', encoding='utf-8') as f:
            script_text = f.read()

        base_name = Path(args.script).stem
        generator.create_variations_from_script(
            script_text=script_text,
            base_name=base_name,
            num_variations=args.variations
        )

    else:
        parser.print_help()
        print("\n" + "="*60)
        print("QUICK START EXAMPLES:")
        print("="*60)
        print("\n1. Process a YouTube video:")
        print("   python ugc_video_generator.py --url 'https://youtube.com/watch?v=...'")
        print("\n2. Process a local video:")
        print("   python ugc_video_generator.py --video /path/to/video.mp4")
        print("\n3. Process a script file:")
        print("   python ugc_video_generator.py --script my_script.txt --variations 5")
        print("\n4. Specify avatar service:")
        print("   python ugc_video_generator.py --url '...' --avatar-service did")
        print("="*60)


if __name__ == "__main__":
    main()
