#!/usr/bin/env python3
"""
Test script for the Repurpose API with a specific YouTube video
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8002"
VIDEO_ID = "7Un6mV2YQ54"  # From https://www.youtube.com/watch?v=7Un6mV2YQ54

def test_root_endpoint():
    """Test the root endpoint"""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_transcribe_endpoint():
    """Test the transcribe endpoint"""
    print(f"\n🎯 Testing transcribe endpoint with video ID: {VIDEO_ID}")
    try:
        payload = {"video_id": VIDEO_ID}
        response = requests.post(f"{BASE_URL}/transcribe/", json=payload)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Video ID: {data.get('youtube_video_id')}")
            print(f"Title: {data.get('title')}")
            print(f"Status: {data.get('status')}")
            transcript = data.get('transcript', '')
            print(f"Transcript length: {len(transcript)} characters")
            if transcript:
                print(f"Transcript preview: {transcript[:200]}...")
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_process_video_endpoint():
    """Test the process-video endpoint"""
    print(f"\n🚀 Testing process-video endpoint with video ID: {VIDEO_ID}")
    try:
        payload = {"video_id": VIDEO_ID, "force_regenerate": False}
        response = requests.post(f"{BASE_URL}/process-video/", json=payload)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Database ID: {data.get('id')}")
            print(f"Video ID: {data.get('youtube_video_id')}")
            print(f"Title: {data.get('title')}")
            print(f"Status: {data.get('status')}")
            
            ideas = data.get('ideas', [])
            content_pieces = data.get('content_pieces', [])
            
            print(f"Generated ideas: {len(ideas)}")
            print(f"Generated content pieces: {len(content_pieces)}")
            
            if ideas:
                print("\n📝 Content Ideas:")
                for i, idea in enumerate(ideas[:3], 1):  # Show first 3 ideas
                    print(f"  {i}. Type: {idea.get('suggested_content_type')}")
                    print(f"     Title: {idea.get('suggested_title')}")
                    print(f"     Snippet: {idea.get('relevant_transcript_snippet', '')[:100]}...")
            
            if content_pieces:
                print("\n🎬 Generated Content:")
                for i, piece in enumerate(content_pieces[:3], 1):  # Show first 3 pieces
                    content_type = piece.get('content_type', 'Unknown')
                    title = piece.get('title', 'No title')
                    print(f"  {i}. Type: {content_type}")
                    print(f"     Title: {title}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting API tests for YouTube Repurpose API")
    print(f"Testing with video: https://www.youtube.com/watch?v={VIDEO_ID}")
    print("=" * 60)
    
    # Test root endpoint first
    if not test_root_endpoint():
        print("❌ Root endpoint failed. Exiting.")
        return
    
    # Test transcribe endpoint
    transcript_result = test_transcribe_endpoint()
    if not transcript_result:
        print("❌ Transcribe endpoint failed. Skipping process-video test.")
        return
    
    # Wait a moment between requests
    time.sleep(1)
    
    # Test process-video endpoint
    process_result = test_process_video_endpoint()
    
    print("\n" + "=" * 60)
    if transcript_result and process_result:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    main()