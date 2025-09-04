#!/usr/bin/env python3
"""
Test script for the content editing functionality
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8002"
VIDEO_ID = "7Un6mV2YQ54"  # Sourdough bread video

def test_get_content_pieces():
    """First, get the generated content pieces to identify what we can edit"""
    print("🔍 Getting content pieces from processed video...")
    
    try:
        payload = {"video_id": VIDEO_ID, "force_regenerate": False}
        response = requests.post(f"{BASE_URL}/process-video/", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            content_pieces = data.get('content_pieces', [])
            
            print(f"✅ Found {len(content_pieces)} content pieces:")
            print("="*80)
            
            for i, piece in enumerate(content_pieces, 1):
                content_id = piece.get('content_id', 'Unknown')
                content_type = piece.get('content_type', 'Unknown')
                title = piece.get('title', 'No title')
                
                print(f"{i}. ID: {content_id}")
                print(f"   Type: {content_type}")
                print(f"   Title: {title}")
                
                if content_type == 'reel':
                    caption = piece.get('caption', '')
                    print(f"   Caption ({len(caption)} chars): {caption[:100]}...")
                elif content_type == 'tweet':
                    tweet_text = piece.get('tweet_text', '')
                    print(f"   Tweet ({len(tweet_text)} chars): {tweet_text[:100]}...")
                elif content_type == 'image_carousel':
                    caption = piece.get('caption', '')
                    slides = piece.get('slides', [])
                    print(f"   Caption ({len(caption)} chars): {caption[:100]}...")
                    print(f"   Slides: {len(slides)}")
                
                print("-" * 40)
            
            return content_pieces
        else:
            print(f"❌ Failed to get content pieces: {response.status_code}")
            print(response.text)
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_edit_content_piece(content_piece_id: str, content_type: str, edit_prompt: str):
    """Test editing a specific content piece"""
    print(f"\\n✏️  Testing content editing...")
    print(f"Content ID: {content_piece_id}")
    print(f"Content Type: {content_type}")
    print(f"Edit Prompt: {edit_prompt}")
    print("="*80)
    
    try:
        payload = {
            "video_id": VIDEO_ID,
            "content_piece_id": content_piece_id,
            "edit_prompt": edit_prompt,
            "content_type": content_type
        }
        
        print("🚀 Sending edit request...")
        response = requests.post(f"{BASE_URL}/edit-content/", json=payload)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Content edited successfully!")
                
                original = data.get('original_content', {})
                edited = data.get('edited_content', {})
                changes = data.get('changes_made', [])
                
                print(f"\\n📝 Changes Made:")
                for change in changes:
                    print(f"  - {change}")
                
                print(f"\\n📋 Before & After Comparison:")
                
                if content_type == 'reel':
                    orig_caption = original.get('caption', '')
                    edit_caption = edited.get('caption', '')
                    print(f"Caption (Original, {len(orig_caption)} chars):")
                    print(f"  {orig_caption}")
                    print(f"Caption (Edited, {len(edit_caption)} chars):")
                    print(f"  {edit_caption}")
                    
                elif content_type == 'tweet':
                    orig_text = original.get('tweet_text', '')
                    edit_text = edited.get('tweet_text', '')
                    print(f"Tweet Text (Original, {len(orig_text)} chars):")
                    print(f"  {orig_text}")
                    print(f"Tweet Text (Edited, {len(edit_text)} chars):")
                    print(f"  {edit_text}")
                    
                elif content_type == 'image_carousel':
                    orig_caption = original.get('caption', '')
                    edit_caption = edited.get('caption', '')
                    print(f"Caption (Original, {len(orig_caption)} chars):")
                    print(f"  {orig_caption}")
                    print(f"Caption (Edited, {len(edit_caption)} chars):")
                    print(f"  {edit_caption}")
                
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
    """Main test function"""
    print("🧪 Content Editing API Test")
    print("This test demonstrates LLM-powered diff-based content editing")
    print("="*80)
    
    # Step 1: Get existing content pieces
    content_pieces = test_get_content_pieces()
    
    if not content_pieces:
        print("❌ No content pieces found. Please run process-video first.")
        return
    
    # Step 2: Test editing different types of content
    test_cases = [
        {
            "description": "Make caption shorter and more engaging",
            "edit_prompt": "Make the caption shorter and more engaging. Keep it under 200 characters and add more emojis.",
            "filter_type": "reel"
        },
        {
            "description": "Add a call-to-action to tweet",
            "edit_prompt": "Add a strong call-to-action at the end asking people to DM for help with their business.",
            "filter_type": "tweet"
        },
        {
            "description": "Make carousel caption more business-focused",
            "edit_prompt": "Rewrite the caption to be more business-focused, emphasizing how sourdough principles apply to e-commerce success.",
            "filter_type": "image_carousel"
        }
    ]
    
    for test_case in test_cases:
        # Find a content piece of the right type
        target_piece = None
        for piece in content_pieces:
            if piece.get('content_type') == test_case['filter_type']:
                target_piece = piece
                break
        
        if target_piece:
            print(f"\\n🎯 Test Case: {test_case['description']}")
            success = test_edit_content_piece(
                target_piece.get('content_id'),
                target_piece.get('content_type'),
                test_case['edit_prompt']
            )
            
            if success:
                print("✅ Edit test passed!")
            else:
                print("❌ Edit test failed!")
            
            time.sleep(2)  # Brief pause between tests
        else:
            print(f"\\n⚠️  No {test_case['filter_type']} content found to test")
    
    print("\\n" + "="*80)
    print("🎉 Content editing tests completed!")
    print("\\nThe API now supports:")
    print("• Natural language editing prompts")
    print("• Diff-based content modification")
    print("• Validation of edited content")
    print("• Change tracking and comparison")
    print("• Database persistence of edits")

if __name__ == "__main__":
    main()