#!/usr/bin/env python3
"""
Comprehensive API Testing Script for YouTube Repurposer API
Tests all endpoints with video ID: 7Un6mV2YQ54
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://127.0.0.1:8002"
VIDEO_ID = "7Un6mV2YQ54"  # Test video ID

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_response(response, endpoint_name):
    print(f"\n📊 {endpoint_name} Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    try:
        response_json = response.json()
        print(f"Response Body:\n{json.dumps(response_json, indent=2, ensure_ascii=False)}")
        return response_json
    except Exception as e:
        print(f"Response Text: {response.text}")
        print(f"JSON Parse Error: {e}")
        return None

def test_health_endpoint():
    """Test 1: Health Check Endpoint"""
    print_separator("TEST 1: Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/health/", timeout=10)
        data = print_response(response, "Health Check")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test 2: Root Information Endpoint"""
    print_separator("TEST 2: Root Information Endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        data = print_response(response, "Root Info")
        
        if response.status_code == 200:
            print("✅ Root endpoint passed!")
            return True
        else:
            print("❌ Root endpoint failed!")
            return False
            
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_transcribe_endpoint():
    """Test 3: Video Transcription Endpoint"""
    print_separator("TEST 3: Video Transcription Endpoint")
    
    try:
        payload = {"video_id": VIDEO_ID}
        response = requests.post(
            f"{API_BASE}/api/v1/transcribe/", 
            json=payload, 
            timeout=30
        )
        data = print_response(response, "Transcribe Video")
        
        if response.status_code == 200 and data:
            print("✅ Transcription successful!")
            print(f"📹 Video: {data.get('title', 'Unknown')}")
            print(f"📝 Transcript length: {len(data.get('transcript', ''))} characters")
            return True, data
        else:
            print("❌ Transcription failed!")
            return False, None
            
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return False, None

def test_process_video_endpoint():
    """Test 4: Video Processing Endpoint (Force Regenerate)"""
    print_separator("TEST 4: Video Processing Endpoint (Force Regenerate)")
    
    try:
        payload = {
            "video_id": VIDEO_ID,
            "force_regenerate": True  # Force regenerate as requested
        }
        
        print(f"🔄 Processing video {VIDEO_ID} with force_regenerate=True...")
        print("⏱️ This may take 1-3 minutes for content generation...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/v1/process-video/", 
            json=payload, 
            timeout=300  # 5 minute timeout for content generation
        )
        end_time = time.time()
        
        data = print_response(response, "Process Video")
        
        if response.status_code == 200 and data:
            print("✅ Video processing successful!")
            print(f"⏱️ Processing time: {end_time - start_time:.2f} seconds")
            print(f"📹 Video: {data.get('title', 'Unknown')}")
            print(f"💡 Ideas generated: {len(data.get('ideas', []))}")
            print(f"📝 Content pieces generated: {len(data.get('content_pieces', []))}")
            
            # Print content pieces summary
            content_pieces = data.get('content_pieces', [])
            for i, piece in enumerate(content_pieces, 1):
                content_type = piece.get('content_type', 'unknown')
                title = piece.get('title', 'No title')
                content_id = piece.get('content_id', 'No ID')
                print(f"  {i}. [{content_type.upper()}] {title} (ID: {content_id})")
            
            return True, data
        else:
            print("❌ Video processing failed!")
            return False, None
            
    except Exception as e:
        print(f"❌ Video processing error: {e}")
        return False, None

def test_edit_content_endpoint(content_pieces):
    """Test 5: Content Editing Endpoint"""
    print_separator("TEST 5: Content Editing Endpoint")
    
    if not content_pieces:
        print("❌ No content pieces available for editing!")
        return False
    
    try:
        # Pick a random content piece (let's pick the first one)
        selected_piece = content_pieces[0]
        content_id = selected_piece.get('content_id')
        content_type = selected_piece.get('content_type')
        
        print(f"🎯 Selected piece for editing:")
        print(f"   ID: {content_id}")
        print(f"   Type: {content_type}")
        print(f"   Title: {selected_piece.get('title', 'No title')}")
        
        # Create an edit request
        edit_payload = {
            "video_id": VIDEO_ID,
            "content_piece_id": content_id,
            "edit_prompt": "Make it more engaging and add relevant emojis",
            "content_type": content_type
        }
        
        print(f"✏️ Edit prompt: {edit_payload['edit_prompt']}")
        print("⏱️ Processing edit request...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/v1/edit-content/", 
            json=edit_payload, 
            timeout=120  # 2 minute timeout for editing
        )
        end_time = time.time()
        
        data = print_response(response, "Edit Content")
        
        if response.status_code == 200 and data:
            success = data.get('success', False)
            if success:
                print("✅ Content editing successful!")
                print(f"⏱️ Edit time: {end_time - start_time:.2f} seconds")
                
                changes = data.get('changes_made', [])
                print(f"🔄 Changes made: {', '.join(changes)}")
                
                # Show before/after comparison
                original = data.get('original_content', {})
                edited = data.get('edited_content', {})
                
                print("\n📝 BEFORE:")
                if content_type == 'reel':
                    print(f"   Caption: {original.get('caption', 'N/A')}")
                elif content_type == 'tweet':
                    print(f"   Text: {original.get('tweet_text', 'N/A')}")
                elif content_type == 'image_carousel':
                    print(f"   Caption: {original.get('caption', 'N/A')}")
                
                print("\n📝 AFTER:")
                if content_type == 'reel':
                    print(f"   Caption: {edited.get('caption', 'N/A')}")
                elif content_type == 'tweet':
                    print(f"   Text: {edited.get('tweet_text', 'N/A')}")
                elif content_type == 'image_carousel':
                    print(f"   Caption: {edited.get('caption', 'N/A')}")
                
                return True
            else:
                error_msg = data.get('error_message', 'Unknown error')
                print(f"❌ Content editing failed: {error_msg}")
                return False
        else:
            print("❌ Content editing request failed!")
            return False
            
    except Exception as e:
        print(f"❌ Content editing error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting Comprehensive API Testing")
    print(f"📍 API Base URL: {API_BASE}")
    print(f"🎥 Test Video ID: {VIDEO_ID}")
    print(f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_endpoint()))
    
    # Test 2: Root Endpoint
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Test 3: Transcribe Video
    transcribe_success, transcribe_data = test_transcribe_endpoint()
    results.append(("Transcribe Video", transcribe_success))
    
    # Test 4: Process Video (with force regenerate)
    process_success, process_data = test_process_video_endpoint()
    results.append(("Process Video", process_success))
    
    # Test 5: Edit Content
    if process_success and process_data:
        content_pieces = process_data.get('content_pieces', [])
        edit_success = test_edit_content_endpoint(content_pieces)
        results.append(("Edit Content", edit_success))
    else:
        print_separator("TEST 5: Content Editing Endpoint - SKIPPED")
        print("❌ Skipping content editing test due to video processing failure")
        results.append(("Edit Content", False))
    
    # Summary
    print_separator("TEST SUMMARY")
    print(f"🕒 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! API is working perfectly!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)