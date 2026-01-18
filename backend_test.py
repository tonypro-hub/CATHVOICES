#!/usr/bin/env python3
"""
Catholic Voices & Prayers API Backend Testing Suite
Tests all backend endpoints for YouTube integration and Prayers CRUD operations
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://faith-voices-1.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        self.created_prayer_id = None
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Catholic Voices and Prayers API" in data.get("message", ""):
                    self.log_test("Root Endpoint", True, "API root endpoint responding correctly", data)
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_get_prayers(self):
        """Test GET /api/prayers - should return all prayers"""
        try:
            response = requests.get(f"{self.base_url}/prayers", headers=self.headers, timeout=10)
            if response.status_code == 200:
                prayers = response.json()
                if isinstance(prayers, list):
                    self.log_test("GET Prayers", True, f"Retrieved {len(prayers)} prayers", {"count": len(prayers)})
                    
                    # Validate prayer structure if prayers exist
                    if prayers:
                        sample_prayer = prayers[0]
                        required_fields = ["id", "title", "videoId", "prayerText", "category", "createdAt"]
                        missing_fields = [field for field in required_fields if field not in sample_prayer]
                        
                        if not missing_fields:
                            self.log_test("Prayer Structure Validation", True, "Prayer objects have all required fields")
                        else:
                            self.log_test("Prayer Structure Validation", False, f"Missing fields: {missing_fields}")
                    
                    return True, prayers
                else:
                    self.log_test("GET Prayers", False, f"Expected list, got: {type(prayers)}")
                    return False, []
            else:
                self.log_test("GET Prayers", False, f"HTTP {response.status_code}: {response.text}")
                return False, []
        except Exception as e:
            self.log_test("GET Prayers", False, f"Request error: {str(e)}")
            return False, []
    
    def test_create_prayer(self):
        """Test POST /api/prayers - create a new prayer"""
        test_prayer = {
            "title": "Test Prayer for API Testing",
            "videoId": "test_video_123",
            "prayerText": "This is a test prayer created during API testing. Please ignore.",
            "category": "Testing"
        }
        
        try:
            response = requests.post(f"{self.base_url}/prayers", 
                                   headers=self.headers, 
                                   json=test_prayer, 
                                   timeout=10)
            
            if response.status_code == 200:
                created_prayer = response.json()
                if "id" in created_prayer and created_prayer["title"] == test_prayer["title"]:
                    self.created_prayer_id = created_prayer["id"]
                    self.log_test("POST Prayer", True, f"Prayer created with ID: {self.created_prayer_id}", created_prayer)
                    return True, created_prayer
                else:
                    self.log_test("POST Prayer", False, f"Invalid response structure: {created_prayer}")
                    return False, None
            else:
                self.log_test("POST Prayer", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("POST Prayer", False, f"Request error: {str(e)}")
            return False, None
    
    def test_get_prayer_by_id(self, prayer_id):
        """Test GET /api/prayers/{id} - get specific prayer"""
        try:
            response = requests.get(f"{self.base_url}/prayers/{prayer_id}", 
                                  headers=self.headers, 
                                  timeout=10)
            
            if response.status_code == 200:
                prayer = response.json()
                if prayer.get("id") == prayer_id:
                    self.log_test("GET Prayer by ID", True, f"Retrieved prayer: {prayer['title']}", prayer)
                    return True, prayer
                else:
                    self.log_test("GET Prayer by ID", False, f"ID mismatch: expected {prayer_id}, got {prayer.get('id')}")
                    return False, None
            elif response.status_code == 404:
                self.log_test("GET Prayer by ID", False, f"Prayer not found: {prayer_id}")
                return False, None
            else:
                self.log_test("GET Prayer by ID", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("GET Prayer by ID", False, f"Request error: {str(e)}")
            return False, None
    
    def test_delete_prayer(self, prayer_id):
        """Test DELETE /api/prayers/{id} - delete prayer"""
        try:
            response = requests.delete(f"{self.base_url}/prayers/{prayer_id}", 
                                     headers=self.headers, 
                                     timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "deleted successfully" in result.get("message", ""):
                    self.log_test("DELETE Prayer", True, f"Prayer {prayer_id} deleted successfully", result)
                    return True
                else:
                    self.log_test("DELETE Prayer", False, f"Unexpected response: {result}")
                    return False
            elif response.status_code == 404:
                self.log_test("DELETE Prayer", False, f"Prayer not found for deletion: {prayer_id}")
                return False
            else:
                self.log_test("DELETE Prayer", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("DELETE Prayer", False, f"Request error: {str(e)}")
            return False
    
    def test_get_videos(self):
        """Test GET /api/videos - get cached videos"""
        try:
            response = requests.get(f"{self.base_url}/videos", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                videos = response.json()
                if isinstance(videos, list):
                    self.log_test("GET Videos", True, f"Retrieved {len(videos)} cached videos", {"count": len(videos)})
                    
                    # Validate video structure if videos exist
                    if videos:
                        sample_video = videos[0]
                        required_fields = ["id", "videoId", "title", "description", "thumbnail", "duration", "publishedAt", "cachedAt"]
                        missing_fields = [field for field in required_fields if field not in sample_video]
                        
                        if not missing_fields:
                            self.log_test("Video Structure Validation", True, "Video objects have all required fields")
                        else:
                            self.log_test("Video Structure Validation", False, f"Missing fields: {missing_fields}")
                    
                    return True, videos
                else:
                    self.log_test("GET Videos", False, f"Expected list, got: {type(videos)}")
                    return False, []
            else:
                self.log_test("GET Videos", False, f"HTTP {response.status_code}: {response.text}")
                return False, []
        except Exception as e:
            self.log_test("GET Videos", False, f"Request error: {str(e)}")
            return False, []
    
    def test_refresh_videos(self):
        """Test GET /api/videos/refresh - refresh videos from YouTube"""
        try:
            print("⏳ Testing YouTube API integration (this may take a moment)...")
            response = requests.get(f"{self.base_url}/videos/refresh", 
                                  headers=self.headers, 
                                  timeout=30)  # Longer timeout for YouTube API
            
            if response.status_code == 200:
                result = response.json()
                if "Successfully cached" in result.get("message", ""):
                    count = result.get("count", 0)
                    self.log_test("Refresh Videos", True, f"YouTube integration working - cached {count} videos", result)
                    return True, result
                else:
                    self.log_test("Refresh Videos", False, f"Unexpected response: {result}")
                    return False, None
            else:
                self.log_test("Refresh Videos", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Refresh Videos", False, f"Request error: {str(e)}")
            return False, None
    
    def test_get_video_by_id(self, video_id):
        """Test GET /api/videos/{videoId} - get specific video"""
        try:
            response = requests.get(f"{self.base_url}/videos/{video_id}", 
                                  headers=self.headers, 
                                  timeout=10)
            
            if response.status_code == 200:
                video = response.json()
                if video.get("videoId") == video_id:
                    self.log_test("GET Video by ID", True, f"Retrieved video: {video['title']}", video)
                    return True, video
                else:
                    self.log_test("GET Video by ID", False, f"VideoId mismatch: expected {video_id}, got {video.get('videoId')}")
                    return False, None
            elif response.status_code == 404:
                self.log_test("GET Video by ID", False, f"Video not found: {video_id}")
                return False, None
            else:
                self.log_test("GET Video by ID", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("GET Video by ID", False, f"Request error: {str(e)}")
            return False, None
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Catholic Voices & Prayers API Backend Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test 1: Root endpoint
        if not self.test_root_endpoint():
            print("❌ Root endpoint failed - stopping tests")
            return self.generate_summary()
        
        # Test 2: Get existing prayers
        prayers_success, existing_prayers = self.test_get_prayers()
        
        # Test 3: Create new prayer
        create_success, created_prayer = self.test_create_prayer()
        
        # Test 4: Get prayer by ID (using created prayer)
        if create_success and self.created_prayer_id:
            self.test_get_prayer_by_id(self.created_prayer_id)
        elif existing_prayers:
            # Test with existing prayer if creation failed
            existing_id = existing_prayers[0]["id"]
            self.test_get_prayer_by_id(existing_id)
        
        # Test 5: Get videos (cached)
        videos_success, existing_videos = self.test_get_videos()
        
        # Test 6: Refresh videos from YouTube
        refresh_success, refresh_result = self.test_refresh_videos()
        
        # Test 7: Get video by ID (if we have videos)
        if existing_videos:
            test_video_id = existing_videos[0]["videoId"]
            self.test_get_video_by_id(test_video_id)
        elif refresh_success:
            # Try to get videos again after refresh
            time.sleep(1)  # Brief pause
            videos_success, new_videos = self.test_get_videos()
            if new_videos:
                test_video_id = new_videos[0]["videoId"]
                self.test_get_video_by_id(test_video_id)
        
        # Test 8: Delete created prayer (cleanup)
        if create_success and self.created_prayer_id:
            self.test_delete_prayer(self.created_prayer_id)
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}: {result['message']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = APITester()
    summary = tester.run_all_tests()
    
    # Save results to file
    with open("/app/test_results_backend.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/test_results_backend.json")
    
    # Exit with appropriate code
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()