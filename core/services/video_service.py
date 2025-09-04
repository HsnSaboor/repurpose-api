"""Video Metadata Service using scrapetube"""
import scrapetube
import yt_dlp
from typing import Dict, List, Optional

def get_channel_videos(channel_id: str, limit: int = 100) -> Optional[List[Dict]]:
    """Get videos from a YouTube channel"""
    try:
        videos = scrapetube.get_channel(channel_id=channel_id, limit=limit)
        return list(videos)
    except Exception as e:
        print(f"Error fetching videos for channel {channel_id}: {e}")
        return None

def get_video_metadata(video_id: str) -> Optional[Dict]:
    """Get metadata for a specific video"""
    try:
        videos = scrapetube.get_videos(video_ids=[video_id])
        if videos:
            return next(videos, None)
        return None
    except Exception as e:
        print(f"Error fetching metadata for video {video_id}: {e}")
        return None

def get_video_title(video_id: str) -> Optional[str]:
    """Get title for a specific video using yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get('title', 'Unknown Title')
    except Exception as e:
        print(f"Error fetching title for video {video_id}: {e}")
        return "Unknown Title"