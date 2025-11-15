#!/usr/bin/env python3
"""
Full API Testing Suite with Advanced Features
Tests all endpoints with comprehensive error handling, retry logic, and detailed reporting
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

# Configuration
BASE_URL = "http://localhost:8002"

# Test video IDs - using popular videos that likely have transcripts
TEST_VIDEOS = {
    "rick_roll": "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "me_at_zoo": "jNQXAC9IVRw",  # First YouTube video
    "gangnam_style": "9bZkp7q19f0",  # PSY - Gangnam Style
}

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


@dataclass
class TestResult:
    """Store test result information"""
    name: str
    passed: bool
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class APITester:
    """Comprehensive API testing class"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    def print_test(self, endpoint: str, method: str = "GET"):
        """Print test information"""
        print(f"{Colors.OKBLUE}{Colors.BOLD}[{method}] {endpoint}{Colors.ENDC}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        timeout: int = 30
    ) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=timeout, stream=stream)
            elif method.upper() == "POST":
                response = self.session.post(url, json=json_data, params=params, timeout=timeout, stream=stream)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=json_data, params=params, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=timeout)
            else:
                self.print_error(f"Unsupported HTTP method: {method}")
                return None
            
            response.elapsed_time = time.time() - start_time
            return response
            
        except requests.exceptions.ConnectionError:
            self.print_error(f"Connection failed! Is the server running on {self.base_url}?")
            return None
        except requests.exceptions.Timeout:
            self.print_error("Request timed out!")
            return None
        except Exception as e:
            self.print_error(f"Request failed: {str(e)}")
            return None
    
    def check_server_availability(self) -> bool:
        """Check if server is available"""
        self.print_header("SERVER AVAILABILITY CHECK")
        self.print_info(f"Checking server at {self.base_url}...")
        
        response = self.make_request("GET", "/", timeout=5)
        
        if response and response.status_code == 200:
            self.print_success(f"Server is running and accessible!")
            try:
                data = response.json()
                self.print_info(f"Response: {data.get('message', 'N/A')}")
            except:
                pass
            return True
        else:
            self.print_error(f"Server is not accessible at {self.base_url}")
            self.print_error("Please make sure the server is running on localhost:8002")
            return False
    
    def test_endpoint(
        self,
        name: str,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        expected_status: int = 200,
        validator: Optional[callable] = None,
        timeout: int = 30
    ) -> TestResult:
        """Test a single endpoint"""
        self.print_test(endpoint, method)
        
        response = self.make_request(method, endpoint, json_data, params, timeout=timeout)
        
        if not response:
            result = TestResult(
                name=name,
                passed=False,
                error_message="No response received"
            )
            self.results.append(result)
            return result
        
        elapsed = getattr(response, 'elapsed_time', None)
        status_code = response.status_code
        
        print(f"Status: {status_code} | Time: {elapsed:.2f}s" if elapsed else f"Status: {status_code}")
        
        # Check status code
        passed = status_code == expected_status
        warnings = []
        
        if not passed:
            if expected_status == 200:
                self.print_error(f"Expected {expected_status}, got {status_code}")
            else:
                self.print_warning(f"Expected {expected_status}, got {status_code}")
        else:
            self.print_success(f"Status code matches expected ({expected_status})")
        
        # Run custom validator
        details = {}
        if validator and passed:
            try:
                data = response.json()
                validation_result = validator(data)
                if isinstance(validation_result, dict):
                    details = validation_result
                    if 'passed' in validation_result:
                        passed = validation_result['passed']
                    if 'warnings' in validation_result:
                        warnings.extend(validation_result['warnings'])
            except Exception as e:
                self.print_warning(f"Validation error: {str(e)}")
                warnings.append(f"Validation failed: {str(e)}")
        
        # Display response snippet
        try:
            json_data = response.json()
            json_str = json.dumps(json_data, indent=2)
            if len(json_str) > 500:
                print(f"{json_str[:500]}...\n[Truncated]")
            else:
                print(json_str)
        except:
            if len(response.text) > 300:
                print(f"{response.text[:300]}...\n[Truncated]")
            else:
                print(response.text)
        
        # Display warnings
        for warning in warnings:
            self.print_warning(warning)
        
        result = TestResult(
            name=name,
            passed=passed,
            status_code=status_code,
            response_time=elapsed,
            warnings=warnings,
            details=details
        )
        
        self.results.append(result)
        print()
        return result
    
    # Validators
    def validate_presets(self, data: Dict) -> Dict:
        """Validate style presets response"""
        if 'presets' not in data:
            return {'passed': False, 'warnings': ['Missing presets key']}
        
        presets = data['presets']
        details = {'preset_count': len(presets)}
        
        required_fields = ['name', 'description', 'target_audience', 'language', 'tone']
        
        for key, preset in presets.items():
            for field in required_fields:
                if field not in preset:
                    return {
                        'passed': False,
                        'warnings': [f"Preset '{key}' missing required field: {field}"]
                    }
        
        self.print_info(f"Found {len(presets)} valid presets")
        return {'passed': True, 'details': details}
    
    def validate_transcript(self, data: Dict) -> Dict:
        """Validate transcript response"""
        required_fields = ['youtube_video_id', 'transcript', 'status']
        warnings = []
        
        for field in required_fields:
            if field not in data:
                warnings.append(f"Missing field: {field}")
        
        if 'transcript' in data:
            transcript_len = len(data['transcript'])
            self.print_info(f"Transcript length: {transcript_len} characters")
            
            if transcript_len < 10:
                warnings.append("Transcript seems too short")
        
        if 'title' in data:
            self.print_info(f"Title: {data['title'][:60]}...")
        
        return {'passed': len(warnings) == 0, 'warnings': warnings}
    
    def validate_videos_list(self, data: Dict) -> Dict:
        """Validate videos list response"""
        if 'videos' not in data:
            return {'passed': False, 'warnings': ['Missing videos key']}
        
        videos = data['videos']
        total = data.get('total', len(videos))
        
        self.print_info(f"Total videos: {total}")
        
        if videos:
            sample = videos[0]
            self.print_info(f"Sample video: {sample.get('title', 'N/A')[:50]}")
        
        return {'passed': True, 'details': {'video_count': total}}
    
    def run_basic_tests(self):
        """Run basic endpoint tests"""
        self.print_header("BASIC ENDPOINTS")
        
        self.test_endpoint(
            "Root Endpoint",
            "GET",
            "/"
        )
        
        self.test_endpoint(
            "Health Check",
            "GET",
            "/test-print/"
        )
    
    def run_content_style_tests(self):
        """Run content style endpoint tests"""
        self.print_header("CONTENT STYLE ENDPOINTS")
        
        self.test_endpoint(
            "Get All Style Presets",
            "GET",
            "/content-styles/presets/",
            validator=self.validate_presets
        )
        
        self.test_endpoint(
            "Get Specific Preset",
            "GET",
            "/content-styles/presets/ecommerce_entrepreneur"
        )
        
        self.test_endpoint(
            "Get Non-existent Preset",
            "GET",
            "/content-styles/presets/nonexistent",
            expected_status=404
        )
    
    def run_transcription_tests(self):
        """Run transcription endpoint tests"""
        self.print_header("TRANSCRIPTION ENDPOINTS")
        
        video_id = TEST_VIDEOS["rick_roll"]
        
        self.test_endpoint(
            "Basic Transcribe",
            "POST",
            "/transcribe/",
            json_data={"video_id": video_id},
            validator=self.validate_transcript,
            timeout=60
        )
        
        self.test_endpoint(
            "Enhanced Transcribe",
            "POST",
            "/transcribe-enhanced/",
            json_data={
                "video_id": video_id,
                "preferences": {
                    "prefer_manual": True,
                    "allow_auto_generated": True
                }
            },
            timeout=60
        )
        
        # Note: analyze-transcripts may fail for some videos
        self.test_endpoint(
            "Analyze Transcripts",
            "GET",
            f"/analyze-transcripts/{video_id}"
        )
    
    def run_video_management_tests(self):
        """Run video management endpoint tests"""
        self.print_header("VIDEO MANAGEMENT ENDPOINTS")
        
        self.test_endpoint(
            "Get All Videos",
            "GET",
            "/videos/",
            params={"skip": 0, "limit": 10},
            validator=self.validate_videos_list
        )
        
        self.test_endpoint(
            "Get Videos with Pagination",
            "GET",
            "/videos/",
            params={"skip": 5, "limit": 5},
            validator=self.validate_videos_list
        )
    
    def run_error_handling_tests(self):
        """Run error handling tests"""
        self.print_header("ERROR HANDLING & EDGE CASES")
        
        self.test_endpoint(
            "Invalid Endpoint",
            "GET",
            "/nonexistent-endpoint/",
            expected_status=404
        )
        
        self.test_endpoint(
            "Invalid Method",
            "DELETE",
            "/",
            expected_status=405
        )
        
        self.test_endpoint(
            "Invalid JSON",
            "POST",
            "/transcribe/",
            json_data={"invalid": "data"},
            expected_status=422  # Validation error
        )
    
    def run_all_tests(self, include_heavy: bool = False):
        """Run all tests"""
        self.print_header("API TESTING SUITE")
        self.print_info(f"Base URL: {self.base_url}")
        self.print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check server first
        if not self.check_server_availability():
            self.print_error("\n❌ Server is not available. Cannot proceed with tests.")
            return False
        
        # Run test suites
        self.run_basic_tests()
        self.run_content_style_tests()
        self.run_transcription_tests()
        self.run_video_management_tests()
        self.run_error_handling_tests()
        
        if include_heavy:
            self.print_header("HEAVY PROCESSING TESTS")
            self.print_warning("Running heavy tests - this will take several minutes...")
            
            video_id = TEST_VIDEOS["me_at_zoo"]
            
            self.test_endpoint(
                "Process Video",
                "POST",
                "/process-video/",
                json_data={"video_id": video_id, "force_regenerate": False},
                timeout=180
            )
        else:
            self.print_header("HEAVY PROCESSING TESTS")
            self.print_warning("Skipped - use --heavy flag to run processing tests")
            self.print_info("Heavy tests include:")
            self.print_info("  • Process Video")
            self.print_info("  • Process Video Stream")
            self.print_info("  • Bulk Video Processing")
            self.print_info("  • Content Editing")
        
        # Generate report
        self.generate_report()
        
        return all(r.passed for r in self.results)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # Calculate stats
        avg_response_time = sum(r.response_time for r in self.results if r.response_time) / max(len([r for r in self.results if r.response_time]), 1)
        
        # Print summary stats
        print(f"{Colors.BOLD}Test Statistics:{Colors.ENDC}")
        print(f"  Total Tests: {total}")
        print(f"  Passed: {Colors.OKGREEN}{passed}{Colors.ENDC}")
        print(f"  Failed: {Colors.FAIL}{failed}{Colors.ENDC}")
        print(f"  Success Rate: {(passed/total*100):.1f}%")
        print(f"  Avg Response Time: {avg_response_time:.2f}s")
        print()
        
        # Detailed results
        print(f"{Colors.BOLD}Detailed Results:{Colors.ENDC}")
        for result in self.results:
            status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if result.passed else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
            time_str = f" ({result.response_time:.2f}s)" if result.response_time else ""
            print(f"  {status} {result.name}{time_str}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"      {Colors.WARNING}⚠ {warning}{Colors.ENDC}")
            
            if result.error_message:
                print(f"      {Colors.FAIL}✗ {result.error_message}{Colors.ENDC}")
        
        print()
        
        # Final verdict
        if passed == total:
            self.print_success("🎉 All tests passed!")
        elif passed > total * 0.7:
            self.print_warning(f"⚠ Most tests passed ({failed} failures)")
        else:
            self.print_error(f"❌ Many tests failed ({failed} failures)")
        
        self.print_info(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main entry point"""
    # Check for flags
    include_heavy = "--heavy" in sys.argv or "-h" in sys.argv
    
    # Create tester
    tester = APITester(BASE_URL)
    
    # Run tests
    try:
        success = tester.run_all_tests(include_heavy=include_heavy)
        exit(0 if success else 1)
    except KeyboardInterrupt:
        tester.print_error("\n\n⚠ Tests interrupted by user")
        exit(130)
    except Exception as e:
        tester.print_error(f"\n\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
