"""YouTube Transcript Service"""
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional, Any

def get_transcript(video_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch transcript for a YouTube video"""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return transcript.to_raw_data() if transcript else None
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None

def get_transcript_text(video_id: str) -> Optional[str]:
    """Get transcript as concatenated text"""
    transcript = get_transcript(video_id)
    if transcript:
        return " ".join([entry['text'] for entry in transcript])
    return None