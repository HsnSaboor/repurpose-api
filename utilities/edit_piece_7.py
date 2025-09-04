#!/usr/bin/env python3
"""
Simple content editor for piece #7
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002"
VIDEO_ID = "7Un6mV2YQ54"

def get_content_pieces_via_api():
    """Get content pieces via the API"""
    try:
        payload = {"video_id": VIDEO_ID, "force_regenerate": False}
        response = requests.post(f"{BASE_URL}/process-video/", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            content_pieces = data.get('content_pieces', [])
            
            print(f"✅ Found {len(content_pieces)} content pieces via API:")
            print("=" * 80)
            
            for i, piece in enumerate(content_pieces, 1):
                content_id = piece.get('content_id', 'Unknown')
                content_type = piece.get('content_type', 'Unknown')
                title = piece.get('title', 'No title')
                
                print(f"{i}. ID: {content_id}")
                print(f"   Type: {content_type}")
                print(f"   Title: {title}")
                
                if content_type == 'tweet':
                    tweet_text = piece.get('tweet_text', '')
                    print(f"   Tweet ({len(tweet_text)} chars): {tweet_text}")
                
                print("-" * 40)
            
            return content_pieces
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def edit_piece_7(content_pieces):
    """Edit piece #7 (Sourdough Discard tweet)"""
    if len(content_pieces) < 7:
        print(f"❌ Piece #7 not found (only {len(content_pieces)} pieces available)")
        return
    
    piece_7 = content_pieces[6]  # 0-indexed
    content_id = piece_7.get('content_id')
    content_type = piece_7.get('content_type')
    title = piece_7.get('title')
    
    print(f"\\n🎯 Editing Piece #7:")
    print(f"Content ID: {content_id}")
    print(f"Content Type: {content_type}")
    print(f"Title: {title}")
    print("=" * 80)
    
    # Original tweet content
    original_tweet = piece_7.get('tweet_text', '')
    print(f"📝 Original Tweet ({len(original_tweet)} chars):")
    print(f"{original_tweet}")
    print("-" * 40)
    
    # Edit prompt
    edit_prompt = "Make this tweet more actionable and add a clear call-to-action. Add relevant emojis and keep it under 240 characters."
    
    try:
        payload = {
            "video_id": VIDEO_ID,
            "content_piece_id": content_id,
            "edit_prompt": edit_prompt,
            "content_type": content_type
        }
        
        print(f"🚀 Sending edit request...")
        print(f"Edit Prompt: {edit_prompt}")
        print("-" * 40)
        
        response = requests.post(f"{BASE_URL}/edit-content/", json=payload)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Content edited successfully!")
                
                original = data.get('original_content', {})
                edited = data.get('edited_content', {})
                changes = data.get('changes_made', [])
                
                print(f"\\n📊 Changes Made:")
                for change in changes:
                    print(f"  - {change}")
                
                print(f"\\n📋 Before & After Comparison:")
                
                orig_text = original.get('tweet_text', '')
                edit_text = edited.get('tweet_text', '')
                
                print(f"\\n📝 BEFORE ({len(orig_text)} chars):")
                print(f"{orig_text}")
                
                print(f"\\n✨ AFTER ({len(edit_text)} chars):")
                print(f"{edit_text}")
                
                print(f"\\n🎉 Successfully edited piece #7!")
                return True
            else:
                print(f"❌ Edit failed: {data.get('error_message')}")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Content Editing Test for Piece #7")
    print("Editing: 'Sourdough Discard: Waste nahi, Opportunity hai!' (tweet)")
    print("=" * 80)
    
    # Step 1: Get content pieces
    content_pieces = get_content_pieces_via_api()
    
    if not content_pieces:
        print("❌ No content pieces found. Make sure the server is running and video is processed.")
        return
    
    # Step 2: Edit piece #7
    success = edit_piece_7(content_pieces)
    
    print("\\n" + "=" * 80)
    if success:
        print("🎉 Content editing test completed successfully!")
    else:
        print("❌ Content editing test failed.")

if __name__ == "__main__":
    main()