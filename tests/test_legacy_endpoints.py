#!/usr/bin/env python3
"""
Test script for legacy API endpoints
"""
import requests
import json

def test_legacy_endpoints():
    """Test the legacy API endpoints that should work"""
    
    print('=== Testing Legacy API Endpoints ===')
    print()
    
    base_url = "http://127.0.0.1:8002"
    test_video_id = "7Un6mV2YQ54"
    
    # Test 1: Health Check
    print('1. Testing Root Endpoint...')
    try:
        response = requests.get(f'{base_url}/')
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ Root endpoint working')
            print(f'   Response: {response.json()}')
        else:
            print('   ❌ Root endpoint failed')
    except Exception as e:
        print(f'   ❌ Error: {e}')
    
    print()
    
    # Test 2: Transcribe (using legacy endpoint)
    print('2. Testing Transcribe Endpoint...')
    try:
        payload = {'video_id': test_video_id}
        response = requests.post(f'{base_url}/transcribe/', json=payload, timeout=30)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            transcript_len = len(data.get('transcript', ''))
            print(f'   ✅ Transcription successful! Transcript length: {transcript_len} characters')
            print(f'   📹 Video: {data.get("title", "Unknown")}')
        else:
            print(f'   ❌ Transcription failed: {response.text[:200]}')
    except Exception as e:
        print(f'   ❌ Error: {e}')

    print()

    # Test 3: Process Video
    print('3. Testing Process Video Endpoint (Force Regenerate)...')
    try:
        payload = {'video_id': test_video_id, 'force_regenerate': True}
        print('   🔄 Processing... This may take 1-3 minutes...')
        response = requests.post(f'{base_url}/process-video/', json=payload, timeout=300)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            content_pieces = data.get('content_pieces', [])
            ideas = data.get('ideas', [])
            print(f'   ✅ Processing successful!')
            print(f'   💡 Ideas: {len(ideas)}, Content pieces: {len(content_pieces)}')

            # Show content pieces
            for i, piece in enumerate(content_pieces[:3], 1):
                title = piece.get('title', 'No title')
                content_type = piece.get('content_type', 'unknown')
                content_id = piece.get('content_id', 'No ID')
                print(f'     {i}. [{content_type.upper()}] {title} (ID: {content_id})')

            if len(content_pieces) > 3:
                print(f'     ... and {len(content_pieces) - 3} more pieces')
        else:
            print(f'   ❌ Processing failed: {response.text[:200]}')
    except Exception as e:
        print(f'   ❌ Error: {e}')

    print()
    print('=== Test Complete ===')

if __name__ == "__main__":
    test_legacy_endpoints()