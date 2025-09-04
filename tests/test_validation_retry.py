#!/usr/bin/env python3
"""
Test script specifically for validation retry mechanism
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002"
VIDEO_ID = "7Un6mV2YQ54"  # From https://www.youtube.com/watch?v=7Un6mV2YQ54

def test_process_video_with_force_regenerate():
    """Test the process-video endpoint with force regeneration to trigger validation retry"""
    print(f"\n🔄 Testing process-video endpoint with FORCE REGENERATION")
    print(f"Video ID: {VIDEO_ID}")
    print("This should trigger the validation retry mechanism if validation errors occur")
    print("="*80)
    
    try:
        payload = {
            "video_id": VIDEO_ID, 
            "force_regenerate": True  # This forces regeneration even if content exists
        }
        
        print("🚀 Sending request with force_regenerate=True...")
        response = requests.post(f"{BASE_URL}/process-video/", json=payload)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Request completed!")
            print(f"Database ID: {data.get('id')}")
            print(f"Video ID: {data.get('youtube_video_id')}")
            print(f"Title: {data.get('title')}")
            print(f"Status: {data.get('status')}")
            
            ideas = data.get('ideas', [])
            content_pieces = data.get('content_pieces', [])
            
            print(f"\\n📊 Results:")
            print(f"Generated ideas: {len(ideas)}")
            print(f"Generated content pieces: {len(content_pieces)}")
            
            if ideas:
                print(f"\\n💡 Content Ideas:")
                for i, idea in enumerate(ideas[:3], 1):  # Show first 3 ideas
                    print(f"  {i}. Type: {idea.get('suggested_content_type')}")
                    print(f"     Title: {idea.get('suggested_title')}")
                    print(f"     Snippet: {idea.get('relevant_transcript_snippet', '')[:100]}...")
            
            if content_pieces:
                print(f"\\n🎬 Generated Content:")
                for i, piece in enumerate(content_pieces, 1):
                    content_type = piece.get('content_type', 'Unknown')
                    title = piece.get('title', 'No title')
                    caption = piece.get('caption', '')
                    print(f"  {i}. Type: {content_type}")
                    print(f"     Title: {title}")
                    if caption:
                        caption_len = len(caption)
                        status_emoji = "✅" if caption_len <= 300 else "❌"
                        print(f"     Caption ({caption_len} chars): {status_emoji} {caption[:100]}...")
            
            # Check if validation retry was successful
            success_count = len(content_pieces)
            total_attempts = len(ideas)
            if total_attempts > 0:
                success_rate = (success_count / total_attempts) * 100
                print(f"\\n📈 Success Rate: {success_count}/{total_attempts} ({success_rate:.1f}%)")
                if success_rate > 0:
                    print("🎉 Validation retry mechanism appears to be working!")
                else:
                    print("⚠️  No content pieces generated - check server logs for validation retry attempts")
            
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
    print("🧪 Validation Retry Mechanism Test")
    print("This test will force regeneration of content to trigger validation retry")
    print("Watch the server logs to see validation retry attempts in action")
    print("="*80)
    
    result = test_process_video_with_force_regenerate()
    
    print("\\n" + "="*80)
    if result:
        print("✅ Test completed! Check server logs for validation retry activity.")
        print("   Look for messages like:")
        print("   - 'Initial validation failed...'")
        print("   - 'Attempting to fix validation errors...'")
        print("   - 'Successfully fixed validation errors...'")
        print("   - 'Successfully recovered content piece...'")
    else:
        print("❌ Test failed.")

if __name__ == "__main__":
    main()