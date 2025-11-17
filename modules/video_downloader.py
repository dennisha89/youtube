"""
Video Downloader Module
Downloads videos from YouTube and other platforms using yt-dlp
"""

import os
import yt_dlp
from pathlib import Path
import config

class VideoDownloader:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or config.DOWNLOADS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def download(self, url, filename=None):
        """
        Download a video from URL

        Args:
            url (str): Video URL
            filename (str): Optional custom filename

        Returns:
            str: Path to downloaded video
        """
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(self.output_dir, filename or '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                print(f"✓ Video downloaded: {video_path}")
                return video_path
        except Exception as e:
            print(f"✗ Error downloading video: {str(e)}")
            raise

    def get_video_info(self, url):
        """
        Get video metadata without downloading

        Args:
            url (str): Video URL

        Returns:
            dict: Video metadata
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'description': info.get('description'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                }
        except Exception as e:
            print(f"✗ Error getting video info: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    downloader = VideoDownloader()

    # Test with a video URL
    # url = "https://www.youtube.com/watch?v=VIDEO_ID"
    # downloader.download(url)

    print("Video downloader module ready!")
    print(f"Download directory: {downloader.output_dir}")
