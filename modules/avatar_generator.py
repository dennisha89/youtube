"""
Avatar Generator Module
Generates AI avatar videos using HeyGen and D-ID APIs
"""

import os
import time
import requests
import config

class AvatarGenerator:
    def __init__(self, service='heygen'):
        """
        Initialize Avatar Generator

        Args:
            service (str): 'heygen' or 'did'
        """
        self.service = service
        self.output_dir = config.VARIATIONS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        if service == 'heygen':
            self.api_key = config.HEYGEN_API_KEY
            self.base_url = "https://api.heygen.com/v1"
        elif service == 'did':
            self.api_key = config.DID_API_KEY
            self.base_url = "https://api.d-id.com"
        else:
            raise ValueError("Service must be 'heygen' or 'did'")

    # ==================== HeyGen Methods ====================

    def heygen_list_avatars(self):
        """Get list of available HeyGen avatars"""
        if not self.api_key:
            print("⚠ HeyGen API key not set")
            return []

        try:
            headers = {
                "X-Api-Key": self.api_key
            }
            response = requests.get(f"{self.base_url}/avatars", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Error fetching avatars: {str(e)}")
            return []

    def heygen_create_video(self, script, avatar_id=None, voice_id=None, background=None):
        """
        Create video using HeyGen

        Args:
            script (str): Script text
            avatar_id (str): Avatar ID from HeyGen
            voice_id (str): Voice ID from HeyGen
            background (str): Background setting

        Returns:
            dict: Video creation response with video_id
        """
        if not self.api_key:
            print("⚠ HeyGen API key not set. Cannot create video.")
            return None

        print(f"Creating HeyGen video...")

        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        # Default avatar and voice if not specified
        if avatar_id is None:
            avatar_id = "josh_lite3_20230714"  # Default HeyGen avatar
        if voice_id is None:
            voice_id = "1bd001e7e50f421d891986aad5158bc8"  # Default HeyGen voice

        data = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id
                },
                "background": {
                    "type": "color",
                    "value": background or "#FFFFFF"
                }
            }],
            "dimension": {
                "width": 1920,
                "height": 1080
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/video/generate",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Video creation initiated: {result.get('video_id')}")
            return result
        except Exception as e:
            print(f"✗ Error creating video: {str(e)}")
            raise

    def heygen_check_status(self, video_id):
        """
        Check HeyGen video generation status

        Args:
            video_id (str): Video ID from creation

        Returns:
            dict: Status response
        """
        if not self.api_key:
            return None

        headers = {
            "X-Api-Key": self.api_key
        }

        try:
            response = requests.get(
                f"{self.base_url}/video_status.get?video_id={video_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Error checking status: {str(e)}")
            return None

    def heygen_download_video(self, video_id, output_filename=None):
        """
        Download generated HeyGen video

        Args:
            video_id (str): Video ID
            output_filename (str): Output filename

        Returns:
            str: Path to downloaded video
        """
        print(f"Checking video status for {video_id}...")

        # Poll for completion
        max_attempts = 60  # 10 minutes max
        attempt = 0

        while attempt < max_attempts:
            status_response = self.heygen_check_status(video_id)

            if status_response:
                status = status_response.get('status')
                print(f"Status: {status}")

                if status == 'completed':
                    video_url = status_response.get('video_url')
                    if video_url:
                        return self._download_from_url(video_url, output_filename or f"heygen_{video_id}.mp4")
                elif status == 'failed':
                    print(f"✗ Video generation failed")
                    return None

            time.sleep(10)
            attempt += 1

        print("⚠ Timeout waiting for video")
        return None

    # ==================== D-ID Methods ====================

    def did_create_video(self, script, presenter_id=None, voice_id=None, audio_url=None):
        """
        Create video using D-ID

        Args:
            script (str): Script text (if not using audio_url)
            presenter_id (str): D-ID presenter/avatar ID
            voice_id (str): D-ID voice ID
            audio_url (str): Optional pre-generated audio URL

        Returns:
            dict: Video creation response
        """
        if not self.api_key:
            print("⚠ D-ID API key not set. Cannot create video.")
            return None

        print(f"Creating D-ID video...")

        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default presenter
        if presenter_id is None:
            presenter_id = "amy-jcwCkr1grs"  # Default D-ID presenter

        data = {
            "source_url": f"https://d-id-public-bucket.s3.amazonaws.com/alice.jpg",  # Placeholder
            "script": {}
        }

        if audio_url:
            data["script"]["audio_url"] = audio_url
        else:
            data["script"]["type"] = "text"
            data["script"]["input"] = script
            if voice_id:
                data["script"]["voice_id"] = voice_id

        try:
            response = requests.post(
                f"{self.base_url}/talks",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ D-ID video creation initiated: {result.get('id')}")
            return result
        except Exception as e:
            print(f"✗ Error creating D-ID video: {str(e)}")
            raise

    # ==================== Helper Methods ====================

    def _download_from_url(self, url, filename):
        """Download video from URL"""
        output_path = os.path.join(self.output_dir, filename)

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✓ Video downloaded: {output_path}")
            return output_path
        except Exception as e:
            print(f"✗ Error downloading video: {str(e)}")
            return None

    def create_variations(self, scripts, service_params=None):
        """
        Create multiple avatar video variations

        Args:
            scripts (list): List of script variations
            service_params (dict): Service-specific parameters

        Returns:
            list: List of video creation jobs
        """
        if service_params is None:
            service_params = {}

        jobs = []

        for i, script_data in enumerate(scripts, 1):
            script_text = script_data.get('script', script_data)

            print(f"\nCreating variation {i}...")

            if self.service == 'heygen':
                result = self.heygen_create_video(
                    script=script_text,
                    **service_params
                )
            elif self.service == 'did':
                result = self.did_create_video(
                    script=script_text,
                    **service_params
                )

            if result:
                jobs.append({
                    'variation_number': i,
                    'video_id': result.get('video_id') or result.get('id'),
                    'service': self.service,
                    'result': result
                })

        return jobs

if __name__ == "__main__":
    # Example usage
    print("Avatar generator ready!")
    print("Supported services: heygen, did")
