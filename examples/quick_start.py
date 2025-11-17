#!/usr/bin/env python3
"""
Quick Start Example - UGC Video Variation Generator
This script shows how to use the modules programmatically
"""

from modules import (
    VideoDownloader,
    ScriptExtractor,
    ScriptVariationGenerator,
    VoiceGenerator,
    AvatarGenerator
)

def example_1_download_and_transcribe():
    """Example 1: Download a video and extract the script"""
    print("Example 1: Download and Transcribe")
    print("-" * 60)

    # Initialize downloader
    downloader = VideoDownloader()

    # Download video (replace with actual URL)
    # video_path = downloader.download("https://youtube.com/watch?v=VIDEO_ID")

    # Extract script
    extractor = ScriptExtractor(model_size='base')
    # transcript = extractor.extract_script(video_path)

    # print(f"Transcript: {transcript['text'][:200]}...")
    print("(Uncomment code and add video URL to test)")


def example_2_generate_script_variations():
    """Example 2: Generate variations from a script"""
    print("\nExample 2: Generate Script Variations")
    print("-" * 60)

    original_script = """
    Hey everyone! Today I'm reviewing this awesome protein powder.
    It tastes great, mixes well, and has excellent macros.
    I highly recommend it if you're looking for quality protein!
    """

    # Generate variations
    generator = ScriptVariationGenerator()
    variations = generator.generate_variations(
        original_script,
        num_variations=3
    )

    # Save variations
    generator.save_variations(variations, "example_product")

    print(f"✓ Generated {len(variations)} variations")
    for i, var in enumerate(variations, 1):
        print(f"\nVariation {i} ({var['persona'][:50]}...):")
        print(var['script'][:150] + "...")


def example_3_generate_voices():
    """Example 3: Generate voice variations"""
    print("\nExample 3: Generate Voice Variations")
    print("-" * 60)

    script = "Hey everyone! This protein powder is amazing. Highly recommended!"

    # Generate voices
    voice_gen = VoiceGenerator()

    # Check if API key is set
    if voice_gen.api_key:
        audio_files = voice_gen.generate_multiple_voices(
            text=script,
            voice_names=['male_1', 'female_1'],
            base_filename='test_audio'
        )
        print(f"✓ Generated {len(audio_files)} audio files")
    else:
        print("⚠ ElevenLabs API key not set. Skipping voice generation.")
        print("Set ELEVENLABS_API_KEY in .env to test this feature.")


def example_4_create_avatar_video():
    """Example 4: Create avatar video"""
    print("\nExample 4: Create Avatar Video")
    print("-" * 60)

    script = "Hey everyone! This protein powder is the best I've ever tried!"

    # Create avatar video
    avatar_gen = AvatarGenerator(service='heygen')

    if avatar_gen.api_key:
        result = avatar_gen.heygen_create_video(script=script)
        print(f"✓ Video job created: {result.get('video_id')}")
    else:
        print("⚠ HeyGen API key not set. Skipping avatar generation.")
        print("Set HEYGEN_API_KEY in .env to test this feature.")


def main():
    """Run all examples"""
    print("="*60)
    print("UGC VIDEO GENERATOR - QUICK START EXAMPLES")
    print("="*60)

    # Run examples
    example_1_download_and_transcribe()
    example_2_generate_script_variations()
    example_3_generate_voices()
    example_4_create_avatar_video()

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)


if __name__ == "__main__":
    main()
