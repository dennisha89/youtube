"""
ComfyUI Custom Nodes for UGC Video Variation Generation
"""

import os
import json
import torch
import numpy as np
from PIL import Image
import folder_paths

from .modules.video_downloader import VideoDownloader
from .modules.script_extractor import ScriptExtractor
from .modules.script_variation_generator import ScriptVariationGenerator
from .modules.voice_generator import VoiceGenerator
from .modules.avatar_generator import AvatarGenerator
import config


class UGCVideoDownloaderNode:
    """Download videos from YouTube and other platforms"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "https://youtube.com/watch?v=..."
                }),
            },
            "optional": {
                "filename": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_path", "video_info")
    FUNCTION = "download_video"
    CATEGORY = "UGC Video Generator"

    def download_video(self, url, filename=""):
        downloader = VideoDownloader()

        # Download video
        video_path = downloader.download(url, filename if filename else None)

        # Get video info
        info = downloader.get_video_info(url)
        info_str = json.dumps(info, indent=2)

        return (video_path, info_str)


class UGCScriptExtractorNode:
    """Extract script from video using Whisper AI"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "model_size": (["tiny", "base", "small", "medium", "large"], {
                    "default": "base"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("script_text", "transcript_json", "transcript_path")
    FUNCTION = "extract_script"
    CATEGORY = "UGC Video Generator"

    def __init__(self):
        self.extractor = None
        self.current_model = None

    def extract_script(self, video_path, model_size):
        # Lazy load and cache the model
        if self.extractor is None or self.current_model != model_size:
            self.extractor = ScriptExtractor(model_size=model_size)
            self.current_model = model_size

        # Extract script
        transcript_data = self.extractor.extract_script(video_path)

        script_text = transcript_data['text']
        transcript_json = json.dumps(transcript_data, indent=2)

        # Find the saved transcript path
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        transcript_path = os.path.join(config.TRANSCRIPTS_DIR, f"{video_name}_transcript.json")

        return (script_text, transcript_json, transcript_path)


class UGCScriptVariationNode:
    """Generate script variations with different personas"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_script": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "num_variations": ("INT", {
                    "default": 3,
                    "min": 1,
                    "max": 10,
                    "step": 1
                }),
            },
            "optional": {
                "custom_personas": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("variations_json", "variation_1", "variation_2")
    FUNCTION = "generate_variations"
    CATEGORY = "UGC Video Generator"

    def generate_variations(self, original_script, num_variations, custom_personas=""):
        generator = ScriptVariationGenerator()

        # Parse custom personas if provided
        persona_list = None
        if custom_personas.strip():
            persona_list = [p.strip() for p in custom_personas.split('\n') if p.strip()]

        # Generate variations
        variations = generator.generate_variations(
            original_script,
            num_variations=num_variations,
            persona_variations=persona_list
        )

        # Save variations
        generator.save_variations(variations, "comfyui_variation")

        variations_json = json.dumps(variations, indent=2)

        # Return individual variations (up to 2 for now)
        var1 = variations[0]['script'] if len(variations) > 0 else ""
        var2 = variations[1]['script'] if len(variations) > 1 else ""

        return (variations_json, var1, var2)


class UGCScriptVariationSelectorNode:
    """Select a specific variation from the variations list"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "variations_json": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "variation_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("script", "persona", "word_count")
    FUNCTION = "select_variation"
    CATEGORY = "UGC Video Generator"

    def select_variation(self, variations_json, variation_index):
        variations = json.loads(variations_json)

        if variation_index >= len(variations):
            variation_index = len(variations) - 1

        variation = variations[variation_index]

        return (
            variation['script'],
            variation['persona'],
            variation['word_count']
        )


class UGCVoiceGeneratorNode:
    """Generate voice audio using ElevenLabs"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "script": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "voice_type": ([
                    "male_1", "male_2", "male_energetic",
                    "female_1", "female_2", "female_calm"
                ], {
                    "default": "male_1"
                }),
            },
            "optional": {
                "output_filename": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_path", "status")
    FUNCTION = "generate_voice"
    CATEGORY = "UGC Video Generator"

    def generate_voice(self, script, voice_type, output_filename=""):
        generator = VoiceGenerator()

        if not generator.api_key:
            return ("", "ERROR: ElevenLabs API key not set in .env")

        try:
            audio_path = generator.generate_audio(
                text=script,
                voice_name=voice_type,
                output_filename=output_filename if output_filename else None
            )

            if audio_path:
                return (audio_path, f"SUCCESS: Audio generated at {audio_path}")
            else:
                return ("", "ERROR: Audio generation failed")

        except Exception as e:
            return ("", f"ERROR: {str(e)}")


class UGCAvatarGeneratorNode:
    """Generate AI avatar video using HeyGen or D-ID"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "script": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "service": (["heygen", "did"], {
                    "default": "heygen"
                }),
            },
            "optional": {
                "avatar_id": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "voice_id": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "background_color": ("STRING", {
                    "multiline": False,
                    "default": "#FFFFFF"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_id", "status", "service_response")
    FUNCTION = "generate_avatar"
    CATEGORY = "UGC Video Generator"

    def generate_avatar(self, script, service, avatar_id="", voice_id="", background_color="#FFFFFF"):
        generator = AvatarGenerator(service=service)

        if not generator.api_key:
            return ("", f"ERROR: {service.upper()} API key not set in .env", "")

        try:
            if service == "heygen":
                result = generator.heygen_create_video(
                    script=script,
                    avatar_id=avatar_id if avatar_id else None,
                    voice_id=voice_id if voice_id else None,
                    background=background_color
                )
            else:  # did
                result = generator.did_create_video(
                    script=script,
                    presenter_id=avatar_id if avatar_id else None,
                    voice_id=voice_id if voice_id else None
                )

            if result:
                video_id = result.get('video_id') or result.get('id')
                response_json = json.dumps(result, indent=2)
                return (
                    video_id,
                    f"SUCCESS: Video creation initiated. ID: {video_id}",
                    response_json
                )
            else:
                return ("", "ERROR: Video creation failed", "")

        except Exception as e:
            return ("", f"ERROR: {str(e)}", "")


class UGCAvatarStatusCheckerNode:
    """Check the status of avatar video generation"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_id": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "service": (["heygen", "did"], {
                    "default": "heygen"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("status", "video_url", "full_response")
    FUNCTION = "check_status"
    CATEGORY = "UGC Video Generator"

    def check_status(self, video_id, service):
        generator = AvatarGenerator(service=service)

        if not generator.api_key:
            return (f"ERROR: {service.upper()} API key not set", "", "")

        try:
            if service == "heygen":
                result = generator.heygen_check_status(video_id)
            else:
                # D-ID status check would go here
                return ("ERROR: D-ID status check not yet implemented", "", "")

            if result:
                status = result.get('status', 'unknown')
                video_url = result.get('video_url', '')
                response_json = json.dumps(result, indent=2)
                return (status, video_url, response_json)
            else:
                return ("ERROR: Status check failed", "", "")

        except Exception as e:
            return (f"ERROR: {str(e)}", "", "")


class UGCAvatarDownloaderNode:
    """Download completed avatar video"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_id": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "service": (["heygen", "did"], {
                    "default": "heygen"
                }),
            },
            "optional": {
                "output_filename": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_path", "status")
    FUNCTION = "download_video"
    CATEGORY = "UGC Video Generator"

    def download_video(self, video_id, service, output_filename=""):
        generator = AvatarGenerator(service=service)

        if not generator.api_key:
            return ("", f"ERROR: {service.upper()} API key not set")

        try:
            if service == "heygen":
                video_path = generator.heygen_download_video(
                    video_id,
                    output_filename if output_filename else None
                )

                if video_path:
                    return (video_path, f"SUCCESS: Video downloaded to {video_path}")
                else:
                    return ("", "ERROR: Video download failed or still processing")
            else:
                return ("", "ERROR: D-ID download not yet implemented")

        except Exception as e:
            return ("", f"ERROR: {str(e)}")


class UGCTextInputNode:
    """Simple text input node for scripts and prompts"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "process_text"
    CATEGORY = "UGC Video Generator"

    def process_text(self, text):
        return (text,)


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "UGCVideoDownloader": UGCVideoDownloaderNode,
    "UGCScriptExtractor": UGCScriptExtractorNode,
    "UGCScriptVariation": UGCScriptVariationNode,
    "UGCScriptVariationSelector": UGCScriptVariationSelectorNode,
    "UGCVoiceGenerator": UGCVoiceGeneratorNode,
    "UGCAvatarGenerator": UGCAvatarGeneratorNode,
    "UGCAvatarStatusChecker": UGCAvatarStatusCheckerNode,
    "UGCAvatarDownloader": UGCAvatarDownloaderNode,
    "UGCTextInput": UGCTextInputNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UGCVideoDownloader": "UGC Video Downloader",
    "UGCScriptExtractor": "UGC Script Extractor",
    "UGCScriptVariation": "UGC Script Variation Generator",
    "UGCScriptVariationSelector": "UGC Variation Selector",
    "UGCVoiceGenerator": "UGC Voice Generator",
    "UGCAvatarGenerator": "UGC Avatar Generator",
    "UGCAvatarStatusChecker": "UGC Avatar Status Checker",
    "UGCAvatarDownloader": "UGC Avatar Downloader",
    "UGCTextInput": "UGC Text Input",
}
