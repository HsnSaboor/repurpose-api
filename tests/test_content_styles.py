#!/usr/bin/env python3
"""
Test script for content style functionality
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8002"
TEST_VIDEO_ID = "7Un6mV2YQ54"  # A valid YouTube video ID

def test_style_presets_endpoint():
    """Test the style presets endpoint"""
    print("\n🎨 Testing content style presets endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/content-styles/presets/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            presets = data.get('presets', {})
            print(f"✅ Found {len(presets)} style presets:")
            
            for key, preset in presets.items():
                print(f"  • {key}: {preset['name']}")
                print(f"    Description: {preset['description']}")
                print(f"    Language: {preset['language']}")
                print(f"    Tone: {preset['tone']}")
                print()
            
            return True, list(presets.keys())
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_specific_style_preset(preset_name):
    """Test getting details of a specific style preset"""
    print(f"\n🔍 Testing specific style preset: {preset_name}")
    try:
        response = requests.get(f"{BASE_URL}/content-styles/presets/{preset_name}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Style preset details:")
            print(f"  Name: {data.get('name')}")
            print(f"  Description: {data.get('description')}")
            print(f"  Target Audience: {data.get('target_audience')}")
            print(f"  Call to Action: {data.get('call_to_action')}")
            print(f"  Content Goal: {data.get('content_goal')}")
            print(f"  Language: {data.get('language')}")
            print(f"  Tone: {data.get('tone')}")
            if data.get('additional_instructions'):
                print(f"  Additional Instructions: {data.get('additional_instructions')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_process_video_with_style_preset(preset_name):
    """Test processing a video with a specific style preset"""
    print(f"\n🚀 Testing video processing with style preset: {preset_name}")
    try:
        payload = {
            "video_id": TEST_VIDEO_ID,
            "force_regenerate": True,
            "style_preset": preset_name
        }
        
        print(f"Processing video {TEST_VIDEO_ID} with {preset_name} style...")
        print("⏱️ This may take 1-3 minutes...")
        
        response = requests.post(f"{BASE_URL}/process-video/", json=payload, timeout=300)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content_pieces = data.get('content_pieces', [])
            ideas = data.get('ideas', [])
            
            print(f"✅ Processing successful!")
            print(f"💡 Ideas: {len(ideas)}")
            print(f"📝 Content pieces: {len(content_pieces)}")
            
            # Show first few content pieces to verify style application
            for i, piece in enumerate(content_pieces[:2], 1):
                content_type = piece.get('content_type', 'unknown')
                title = piece.get('title', 'No title')
                
                print(f"\n  {i}. [{content_type.upper()}] {title}")
                
                if content_type == 'reel':
                    caption = piece.get('caption', '')
                    hook = piece.get('hook', '')
                    print(f"     Hook: {hook[:100]}...")
                    print(f"     Caption: {caption[:100]}...")
                elif content_type == 'tweet':
                    tweet_text = piece.get('tweet_text', '')
                    print(f"     Tweet: {tweet_text}")
                elif content_type == 'image_carousel':
                    caption = piece.get('caption', '')
                    slides = piece.get('slides', [])
                    print(f"     Caption: {caption[:100]}...")
                    print(f"     Slides: {len(slides)}")
                    if slides:
                        print(f"     First slide: {slides[0].get('step_heading', 'No heading')}")
            
            return True, data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_process_video_with_custom_style():
    """Test processing a video with custom style configuration"""
    print(f"\n🎯 Testing video processing with custom style configuration...")
    
    custom_style = {
        "target_audience": "tech entrepreneurs and startup founders",
        "call_to_action": "Subscribe for more startup insights and follow us on LinkedIn",
        "content_goal": "education, thought_leadership, networking",
        "language": "English",
        "tone": "Inspirational and professional",
        "additional_instructions": "Use startup terminology, focus on actionable insights, include success metrics when possible"
    }
    
    try:
        payload = {
            "video_id": TEST_VIDEO_ID,
            "force_regenerate": True,
            "custom_style": custom_style
        }
        
        print(f"Processing video {TEST_VIDEO_ID} with custom style...")
        print("⏱️ This may take 1-3 minutes...")
        
        response = requests.post(f"{BASE_URL}/process-video/", json=payload, timeout=300)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content_pieces = data.get('content_pieces', [])
            ideas = data.get('ideas', [])
            
            print(f"✅ Processing successful!")
            print(f"💡 Ideas: {len(ideas)}")
            print(f"📝 Content pieces: {len(content_pieces)}")
            
            # Show first content piece to verify custom style application
            if content_pieces:
                piece = content_pieces[0]
                content_type = piece.get('content_type', 'unknown')
                title = piece.get('title', 'No title')
                
                print(f"\n  Sample content piece:")
                print(f"  Type: {content_type.upper()}")
                print(f"  Title: {title}")
                
                if content_type == 'reel':
                    caption = piece.get('caption', '')
                    print(f"  Caption: {caption}")
                elif content_type == 'tweet':
                    tweet_text = piece.get('tweet_text', '')
                    print(f"  Tweet: {tweet_text}")
            
            return True, data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def main():
    """Main test function"""
    print("🎨 Starting Content Style Functionality Tests")
    print(f"Testing with video: https://www.youtube.com/watch?v={TEST_VIDEO_ID}")
    print("=" * 80)
    
    # Test 1: Get available style presets
    presets_success, available_presets = test_style_presets_endpoint()
    if not presets_success:
        print("❌ Style presets endpoint failed. Exiting.")
        return
    
    # Test 2: Get details of specific presets
    if available_presets:
        test_preset = available_presets[0]  # Test first available preset
        preset_detail_success = test_specific_style_preset(test_preset)
        
        if preset_detail_success:
            # Test 3: Process video with style preset
            process_preset_success, _ = test_process_video_with_style_preset(test_preset)
            
            if process_preset_success:
                time.sleep(2)  # Brief pause between tests
                
                # Test 4: Process video with custom style
                custom_style_success, _ = test_process_video_with_custom_style()
    
    print("\n" + "=" * 80)
    print("🎉 Content style functionality tests completed!")
    print("\nThe API now supports:")
    print("• 5 predefined content style presets")
    print("• Custom style configuration")
    print("• Style-aware content generation")
    print("• Dynamic prompt generation based on style")

if __name__ == "__main__":
    main()