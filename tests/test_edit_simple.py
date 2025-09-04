#!/usr/bin/env python3
"""
Simple test for editing content piece #7
"""
import requests
import json

# Based on the logs, piece #7 should have ID: 7Un6mV2YQ54_007
VIDEO_ID = "7Un6mV2YQ54"
CONTENT_PIECE_ID = f"{VIDEO_ID}_007"  # Piece #7
BASE_URL = "http://127.0.0.1:8002"

def test_edit_content():
    """Test editing content piece #7"""
    
    # Edit request for piece #7 (Sourdough Discard tweet)
    payload = {
        "video_id": VIDEO_ID,
        "content_piece_id": CONTENT_PIECE_ID,
        "edit_prompt": "Make this tweet more actionable and engaging. Add emojis and a clear call-to-action asking people to DM for business tips. Keep it under 240 characters.",
        "content_type": "tweet"
    }
    
    print("🎯 Testing Content Edit API")
    print(f"Video ID: {VIDEO_ID}")
    print(f"Content Piece ID: {CONTENT_PIECE_ID}")
    print(f"Content Type: tweet") 
    print(f"Edit Prompt: {payload['edit_prompt']}")
    print("=" * 80)
    
    try:
        print("🚀 Sending edit request...")
        response = requests.post(f"{BASE_URL}/edit-content/", json=payload, timeout=60)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Edit successful!")
                
                original = data.get('original_content', {})
                edited = data.get('edited_content', {})
                changes = data.get('changes_made', [])
                
                print(f"\\n📊 Changes Made:")
                for change in changes:
                    print(f"  - {change}")
                
                print(f"\\n📋 Content Comparison:")
                
                orig_tweet = original.get('tweet_text', 'N/A')
                edit_tweet = edited.get('tweet_text', 'N/A')
                
                print(f"\\n📝 ORIGINAL ({len(orig_tweet)} chars):")
                print(f"'{orig_tweet}'")
                
                print(f"\\n✨ EDITED ({len(edit_tweet)} chars):")
                print(f"'{edit_tweet}'")
                
                print(f"\\n🎉 Successfully edited piece #7!")
                
            else:
                print(f"❌ Edit failed: {data.get('error_message', 'Unknown error')}")
        
        elif response.status_code == 404:
            print("❌ Content piece not found. Available content piece IDs might be different.")
            print("💡 Try running the video processing first or check the actual content piece IDs.")
            
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The LLM might be taking longer to process.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the server is running on http://127.0.0.1:8002")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_edit_content()