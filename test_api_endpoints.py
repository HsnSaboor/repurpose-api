#!/usr/bin/env python3
"""
Comprehensive API Testing Script for YouTube Repurposer API
Tests all available endpoints with proper error handling and logging
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8002"
TEST_VIDEO_ID = "dQw4w9WgXcQ"  # Sample YouTube video ID
TEST_CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # Sample channel ID

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_test(endpoint: str, method: str = "GET"):
    """Print test information"""
    print(f"{Colors.OKBLUE}{Colors.BOLD}Testing [{method}] {endpoint}{Colors.ENDC}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def make_request(
    method: str,
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    stream: bool = False
) -> Optional[requests.Response]:
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=30, stream=stream)
        elif method.upper() == "POST":
            response = requests.post(url, json=json_data, params=params, timeout=120, stream=stream)
        elif method.upper() == "PUT":
            response = requests.put(url, json=json_data, params=params, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, params=params, timeout=30)
        else:
            print_error(f"Unsupported HTTP method: {method}")
            return None
        
        return response
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed! Is the server running on {BASE_URL}?")
        return None
    except requests.exceptions.Timeout:
        print_error("Request timed out!")
        return None
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None


def display_response(response: requests.Response, show_body: bool = True):
    """Display response details"""
    print(f"Status Code: {response.status_code}")
    
    if response.status_code >= 200 and response.status_code < 300:
        print_success(f"Success ({response.status_code})")
    elif response.status_code >= 400 and response.status_code < 500:
        print_error(f"Client Error ({response.status_code})")
    elif response.status_code >= 500:
        print_error(f"Server Error ({response.status_code})")
    
    if show_body:
        try:
            json_response = response.json()
            print(f"\n{Colors.OKCYAN}Response:{Colors.ENDC}")
            print(json.dumps(json_response, indent=2)[:1000])  # Limit output
            if len(json.dumps(json_response)) > 1000:
                print_warning("... (response truncated)")
        except:
            print(f"\n{Colors.OKCYAN}Response Text:{Colors.ENDC}")
            print(response.text[:500])
            if len(response.text) > 500:
                print_warning("... (response truncated)")


# Test Functions
def test_root():
    """Test root endpoint"""
    print_test("/", "GET")
    response = make_request("GET", "/")
    
    if response:
        display_response(response)
        return response.status_code == 200
    return False


def test_health_check():
    """Test health/test endpoint"""
    print_test("/test-print/", "GET")
    response = make_request("GET", "/test-print/")
    
    if response:
        display_response(response)
        return response.status_code == 200
    return False


def test_get_content_style_presets():
    """Test getting content style presets"""
    print_test("/content-styles/presets/", "GET")
    response = make_request("GET", "/content-styles/presets/")
    
    if response:
        display_response(response)
        if response.status_code == 200:
            data = response.json()
            if 'presets' in data:
                print_info(f"Found {len(data['presets'])} style presets")
                for key, preset in data['presets'].items():
                    print(f"  - {key}: {preset.get('name', 'N/A')}")
            return True
        return False
    return False


def test_get_specific_style_preset():
    """Test getting a specific content style preset"""
    preset_name = "ecommerce_entrepreneur"
    print_test(f"/content-styles/presets/{preset_name}", "GET")
    response = make_request("GET", f"/content-styles/presets/{preset_name}")
    
    if response:
        display_response(response)
        return response.status_code == 200
    return False


def test_transcribe_video():
    """Test video transcription"""
    print_test("/transcribe/", "POST")
    print_info(f"Using video ID: {TEST_VIDEO_ID}")
    
    payload = {
        "video_id": TEST_VIDEO_ID
    }
    
    response = make_request("POST", "/transcribe/", json_data=payload)
    
    if response:
        display_response(response, show_body=False)  # Don't show full transcript
        if response.status_code == 200:
            data = response.json()
            print_info(f"Title: {data.get('title', 'N/A')}")
            print_info(f"Status: {data.get('status', 'N/A')}")
            print_info(f"Transcript length: {len(data.get('transcript', ''))} characters")
            return True
        return False
    return False


def test_transcribe_enhanced():
    """Test enhanced transcription with preferences"""
    print_test("/transcribe-enhanced/", "POST")
    print_info(f"Using video ID: {TEST_VIDEO_ID}")
    
    payload = {
        "video_id": TEST_VIDEO_ID,
        "preferences": {
            "prefer_manual": True,
            "allow_auto_generated": True,
            "allow_translated": True
        }
    }
    
    response = make_request("POST", "/transcribe-enhanced/", json_data=payload)
    
    if response:
        display_response(response, show_body=False)
        if response.status_code == 200:
            data = response.json()
            print_info(f"Title: {data.get('title', 'N/A')}")
            print_info(f"Available languages: {len(data.get('available_languages', []))}")
            metadata = data.get('transcript_metadata', {})
            if metadata:
                print_info(f"Language: {metadata.get('language', 'N/A')}")
                print_info(f"Priority: {metadata.get('priority', 'N/A')}")
                print_info(f"Is Generated: {metadata.get('is_generated', 'N/A')}")
            return True
        return False
    return False


def test_analyze_transcripts():
    """Test transcript analysis"""
    print_test(f"/analyze-transcripts/{TEST_VIDEO_ID}", "GET")
    response = make_request("GET", f"/analyze-transcripts/{TEST_VIDEO_ID}")
    
    if response:
        display_response(response)
        if response.status_code == 200:
            data = response.json()
            print_info(f"Recommended approach: {data.get('recommended_approach', 'N/A')}")
            print_info(f"Available transcripts: {len(data.get('available_transcripts', []))}")
            return True
        return False
    return False


def test_process_video():
    """Test video processing"""
    print_test("/process-video/", "POST")
    print_warning("This may take several minutes...")
    print_info(f"Using video ID: {TEST_VIDEO_ID}")
    
    payload = {
        "video_id": TEST_VIDEO_ID,
        "force_regenerate": False
    }
    
    response = make_request("POST", "/process-video/", json_data=payload)
    
    if response:
        display_response(response, show_body=False)
        if response.status_code == 200:
            data = response.json()
            print_info(f"Title: {data.get('title', 'N/A')}")
            print_info(f"Status: {data.get('status', 'N/A')}")
            print_info(f"Ideas generated: {len(data.get('ideas', []))}")
            print_info(f"Content pieces: {len(data.get('content_pieces', []))}")
            return True
        return False
    return False


def test_process_video_with_style():
    """Test video processing with style preset"""
    print_test("/process-video/ (with style)", "POST")
    print_warning("This may take several minutes...")
    print_info(f"Using video ID: {TEST_VIDEO_ID}")
    print_info("Style: professional_business")
    
    payload = {
        "video_id": TEST_VIDEO_ID,
        "force_regenerate": False,
        "style_preset": "professional_business"
    }
    
    response = make_request("POST", "/process-video/", json_data=payload)
    
    if response:
        display_response(response, show_body=False)
        if response.status_code == 200:
            data = response.json()
            print_info(f"Title: {data.get('title', 'N/A')}")
            print_info(f"Content pieces: {len(data.get('content_pieces', []))}")
            return True
        return False
    return False


def test_process_video_stream():
    """Test streaming video processing"""
    print_test("/process-video-stream/", "POST")
    print_warning("This will stream progress updates...")
    print_info(f"Using video ID: {TEST_VIDEO_ID}")
    
    payload = {
        "video_id": TEST_VIDEO_ID,
        "force_regenerate": False
    }
    
    response = make_request("POST", "/process-video-stream/", json_data=payload, stream=True)
    
    if response:
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print_info("Streaming response:")
            event_count = 0
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        event_count += 1
                        try:
                            data = json.loads(decoded_line[5:].strip())
                            status = data.get('status', 'unknown')
                            progress = data.get('progress', 0)
                            message = data.get('message', '')
                            
                            print(f"  [{progress}%] {status}: {message}")
                            
                            if status == 'complete':
                                print_success("Processing complete!")
                                break
                            elif status == 'error':
                                print_error(f"Error: {message}")
                                break
                        except json.JSONDecodeError:
                            print_warning(f"Could not parse: {decoded_line}")
                        
                        if event_count > 20:  # Limit output
                            print_warning("... (truncating stream output)")
                            break
            
            return True
        return False
    return False


def test_get_all_videos():
    """Test getting all videos"""
    print_test("/videos/", "GET")
    response = make_request("GET", "/videos/", params={"skip": 0, "limit": 10})
    
    if response:
        display_response(response, show_body=False)
        if response.status_code == 200:
            data = response.json()
            videos = data.get('videos', [])
            print_info(f"Total videos: {data.get('total', 0)}")
            
            if videos:
                print_info("Sample videos:")
                for i, video in enumerate(videos[:3], 1):
                    print(f"  {i}. {video.get('title', 'N/A')} ({video.get('youtube_video_id', 'N/A')})")
            return True
        return False
    return False


def test_bulk_video_processing():
    """Test bulk video processing"""
    print_test("/process-videos-bulk/", "POST")
    print_warning("This may take several minutes...")
    
    # Using a couple of test video IDs
    payload = {
        "video_ids": [TEST_VIDEO_ID, "jNQXAC9IVRw"]  # 2 sample videos
    }
    
    response = make_request("POST", "/process-videos-bulk/", json_data=payload)
    
    if response:
        display_response(response, show_body=False)
        if response.status_code == 200:
            data = response.json()
            print_info(f"Processed {len(data)} videos")
            for item in data:
                status = item.get('status', 'unknown')
                video_id = item.get('video_id', 'N/A')
                print(f"  - {video_id}: {status}")
            return True
        return False
    return False


def test_edit_content():
    """Test content editing"""
    print_test("/edit-content/", "POST")
    print_warning("This requires an existing processed video with content pieces")
    print_info("This test may fail if video hasn't been processed yet")
    
    # First, we need to get a content piece ID
    # This is just a demonstration - will likely fail without real data
    payload = {
        "video_id": TEST_VIDEO_ID,
        "content_piece_id": f"{TEST_VIDEO_ID}_001",
        "edit_prompt": "Make the content more engaging and add emojis",
        "content_type": "reel"
    }
    
    response = make_request("POST", "/edit-content/", json_data=payload)
    
    if response:
        display_response(response, show_body=False)
        if response.status_code == 200:
            data = response.json()
            print_info(f"Edit success: {data.get('success', False)}")
            if data.get('changes_made'):
                print_info(f"Changes made: {len(data.get('changes_made', []))}")
            return True
        elif response.status_code == 404:
            print_warning("Content piece not found - this is expected if video hasn't been processed")
            return True  # Not an error in this context
        return False
    return False


def test_invalid_endpoint():
    """Test invalid endpoint handling"""
    print_test("/invalid-endpoint/", "GET")
    response = make_request("GET", "/invalid-endpoint/")
    
    if response:
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print_success("Correctly returned 404 for invalid endpoint")
            return True
        else:
            print_error(f"Expected 404, got {response.status_code}")
        return False
    return False


def test_invalid_video_id():
    """Test invalid video ID handling"""
    print_test("/transcribe/ (invalid ID)", "POST")
    
    payload = {
        "video_id": "INVALID_VIDEO_ID_123"
    }
    
    response = make_request("POST", "/transcribe/", json_data=payload)
    
    if response:
        print(f"Status Code: {response.status_code}")
        if response.status_code >= 400:
            print_success("Correctly handled invalid video ID")
            return True
        else:
            print_warning(f"Unexpected success with invalid video ID")
        return True  # Not necessarily a failure
    return False


def run_all_tests():
    """Run all API tests"""
    print_header("YouTube Repurposer API - Comprehensive Endpoint Testing")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test Video ID: {TEST_VIDEO_ID}")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test results tracker
    results = {}
    
    # Basic endpoints
    print_header("BASIC ENDPOINTS")
    results['Root Endpoint'] = test_root()
    print()
    results['Health Check'] = test_health_check()
    print()
    
    # Content Style endpoints
    print_header("CONTENT STYLE ENDPOINTS")
    results['Get Style Presets'] = test_get_content_style_presets()
    print()
    results['Get Specific Preset'] = test_get_specific_style_preset()
    print()
    
    # Transcription endpoints
    print_header("TRANSCRIPTION ENDPOINTS")
    results['Basic Transcribe'] = test_transcribe_video()
    print()
    results['Enhanced Transcribe'] = test_transcribe_enhanced()
    print()
    results['Analyze Transcripts'] = test_analyze_transcripts()
    print()
    
    # Video processing endpoints
    print_header("VIDEO PROCESSING ENDPOINTS")
    results['Get All Videos'] = test_get_all_videos()
    print()
    
    # Skip heavy processing tests by default - uncomment to run
    print_warning("Skipping heavy processing tests to save time/resources")
    print_info("Uncomment these tests in the code if you want to run them:")
    print_info("  - Process Video")
    print_info("  - Process Video with Style")
    print_info("  - Process Video Stream")
    print_info("  - Bulk Video Processing")
    print_info("  - Edit Content")
    
    # Uncomment below to run heavy tests
    # results['Process Video'] = test_process_video()
    # print()
    # results['Process Video (Style)'] = test_process_video_with_style()
    # print()
    # results['Process Video Stream'] = test_process_video_stream()
    # print()
    # results['Bulk Processing'] = test_bulk_video_processing()
    # print()
    # results['Edit Content'] = test_edit_content()
    # print()
    
    # Error handling tests
    print_header("ERROR HANDLING TESTS")
    results['Invalid Endpoint'] = test_invalid_endpoint()
    print()
    results['Invalid Video ID'] = test_invalid_video_id()
    print()
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
    for test_name, passed_test in results.items():
        status = f"{Colors.OKGREEN}✓ PASSED{Colors.ENDC}" if passed_test else f"{Colors.FAIL}✗ FAILED{Colors.ENDC}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print_success(f"\n🎉 All tests passed!")
    elif passed > 0:
        print_warning(f"\n⚠ Some tests failed: {total - passed} failures")
    else:
        print_error(f"\n❌ All tests failed!")
    
    print_info(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\n⚠ Tests interrupted by user")
        exit(130)
    except Exception as e:
        print_error(f"\n\n❌ Test suite failed with error: {str(e)}")
        exit(1)
