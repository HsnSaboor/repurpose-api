import scrapetube
import requests
from datetime import datetime

def get_channel_videos(username, max_videos=100):
    # scrapetube supports channel_username parameter directly
    videos_gen = scrapetube.get_channel(channel_username=username, content_type="videos", limit=max_videos)
    
    videos = []
    for video in videos_gen:
        # video is a dict with video details
        video_id = video.get('videoId')
        # Extract the actual title text from the nested structure
        title_data = video.get('title', {})
        if isinstance(title_data, dict) and 'runs' in title_data:
            # Extract text from the first run in the array
            title = title_data['runs'][0]['text'] if title_data['runs'] else 'Untitled'
        else:
            title = title_data if isinstance(title_data, str) else 'Untitled'
        
        # Views and duration are nested in 'lengthText' and 'viewCountText' inside 'video' or 'videoRenderer'
        # scrapetube returns raw data, so we extract them carefully
        
        # Extract view count text
        view_count_text = video.get('viewCountText', {}).get('simpleText', 'N/A')
        # Extract published time text
        published_time = video.get('publishedTimeText', {}).get('simpleText', 'N/A')
        # Extract duration
        duration = video.get('lengthText', {}).get('simpleText', 'N/A')
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        videos.append({
            'video_id': video_id,
            'title': title,
            'views': view_count_text,
            'url': url,
            'date_posted': published_time,
            'duration': duration
        })
    return videos

if __name__ == "__main__":
    username = input("Enter YouTube channel username (without @): ").strip()
    videos = get_channel_videos(username, max_videos=100)
    for v in videos:
        print(f"ID: {v['video_id']}")
        print(f"Title: {v['title']}")
        print(f"Views: {v['views']}")
        print(f"URL: {v['url']}")
        print(f"Date Posted: {v['date_posted']}")
        print(f"Duration: {v['duration']}")
        print("-" * 40)
