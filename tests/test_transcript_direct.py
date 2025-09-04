#!/usr/bin/env python3
"""
Direct test of YouTube Transcript API for the specific video
"""
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
import sys

def test_transcript_direct(video_id):
    """Test transcript fetching directly"""
    print(f"🔍 Testing direct transcript fetch for video: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    
    try:
        # Initialize the API
        ytt_api = YouTubeTranscriptApi()
        
        # Try to get the transcript
        transcript = ytt_api.fetch(video_id)
        
        if transcript:
            print(f"✅ Transcript found! {len(transcript)} entries")
            
            # Convert to raw data (list of dictionaries)
            transcript_data = transcript.to_raw_data()
            
            # Convert to text
            transcript_text = " ".join([entry['text'] for entry in transcript_data])
            print(f"📝 Transcript length: {len(transcript_text)} characters")
            
            # Show first few entries
            print(f"\n📋 First 5 transcript entries:")
            for i, entry in enumerate(transcript_data[:5]):
                start_time = entry.get('start', 0)
                duration = entry.get('duration', 0)
                text = entry.get('text', '')
                print(f"  {i+1}. [{start_time:.1f}s] {text}")
            
            # Show preview of full text
            print(f"\n📖 Full transcript preview:")
            print(f"{transcript_text[:500]}...")
            
            return transcript_text
        else:
            print("❌ No transcript entries found")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        
        # Try to get available transcript languages
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            print(f"\n🌐 Available transcript languages:")
            for transcript in transcript_list:
                print(f"  - {transcript.language} ({transcript.language_code})")
                if transcript.is_generated:
                    print(f"    (auto-generated)")
                if transcript.is_translatable:
                    print(f"    (translatable)")
        except Exception as lang_error:
            print(f"❌ Could not get available languages: {lang_error}")
        
        return None

def main():
    video_id = "7Un6mV2YQ54"
    
    print("🚀 Direct YouTube Transcript API Test")
    print("=" * 50)
    
    result = test_transcript_direct(video_id)
    
    print("\n" + "=" * 50)
    if result:
        print("✅ Transcript test completed successfully!")
    else:
        print("❌ Transcript test failed.")

if __name__ == "__main__":
    main()