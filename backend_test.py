#!/usr/bin/env python3
"""
Backend API Testing for Catholic Voices & Prayers
Tests all API endpoints for functionality and data integrity
"""

import requests
import sys
import json
from datetime import datetime

class CatholicVoicesAPITester:
    def __init__(self, base_url="https://catholic-voices-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.results = {}

    def run_test(self, name, method, endpoint, expected_status=200, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    self.results[name] = {
                        'status': 'PASSED',
                        'status_code': response.status_code,
                        'response_size': len(str(response_data)),
                        'has_data': bool(response_data)
                    }
                    
                    # Log key response info
                    if isinstance(response_data, dict):
                        if 'saints' in response_data:
                            print(f"   📊 Found {len(response_data['saints'])} saints")
                        elif 'saintName' in response_data:
                            print(f"   🎯 Saint: {response_data['saintName']}")
                        elif isinstance(response_data, list):
                            print(f"   📊 Found {len(response_data)} items")
                        elif 'total' in response_data:
                            print(f"   📊 Total items: {response_data['total']}")
                            
                except Exception as e:
                    print(f"   ⚠️  Response not JSON: {str(e)[:100]}")
                    self.results[name] = {
                        'status': 'PASSED',
                        'status_code': response.status_code,
                        'response_size': len(response.text),
                        'has_data': bool(response.text)
                    }
                    
                return True, response_data if 'response_data' in locals() else response.text

            else:
                self.tests_passed += 1 if response.status_code in [404, 500] and 'error expected' in name.lower() else 0
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'url': url,
                    'response': response.text[:500]
                })
                
                self.results[name] = {
                    'status': 'FAILED',
                    'status_code': response.status_code,
                    'expected_status': expected_status,
                    'error': response.text[:200]
                }
                
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout after {timeout}s")
            self.failed_tests.append({
                'name': name,
                'error': 'Timeout',
                'url': url
            })
            self.results[name] = {'status': 'FAILED', 'error': 'Timeout'}
            return False, {}
            
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': str(e),
                'url': url
            })
            self.results[name] = {'status': 'FAILED', 'error': str(e)}
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "health")

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "")

    def test_todays_saint(self):
        """Test today's saint endpoint"""
        success, data = self.run_test("Today's Saint", "GET", "saints/today")
        
        if success and data:
            # Validate saint data structure
            required_fields = ['saintName', 'feastDate', 'videoId']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ Saint data structure valid")
                
            # Check if it's St. Fabian as expected
            if 'Fabian' in data.get('saintName', ''):
                print(f"   🎯 Correct saint for today: {data['saintName']}")
            else:
                print(f"   ℹ️  Current saint: {data.get('saintName', 'Unknown')}")
                
        return success, data

    def test_saints_archive(self):
        """Test saints archive endpoint"""
        success, data = self.run_test("Saints Archive", "GET", "saints/archive")
        
        if success and data:
            saints_count = len(data.get('saints', []))
            total = data.get('total', 0)
            has_more = data.get('hasMore', False)
            
            print(f"   📊 Archive: {saints_count} saints loaded, {total} total, hasMore: {has_more}")
            
        return success, data

    def test_mass_locations(self):
        """Test mass locations endpoint"""
        success, data = self.run_test("Mass Locations", "GET", "mass-locations")
        
        if success and data:
            locations_count = len(data) if isinstance(data, list) else 0
            print(f"   📊 Found {locations_count} mass locations")
            
            # Check for expected affiliations
            if locations_count > 0:
                affiliations = set(loc.get('affiliation', '') for loc in data)
                print(f"   🏛️  Affiliations: {', '.join(sorted(affiliations))}")
                
        return success, data

    def test_mass_location_filters(self):
        """Test mass location filters endpoint"""
        success, data = self.run_test("Mass Location Filters", "GET", "mass-locations/filters")
        
        if success and data:
            affiliations = len(data.get('affiliations', []))
            states = len(data.get('states', []))
            print(f"   📊 Filters: {affiliations} affiliations, {states} states")
            
        return success, data

    def test_mass_location_stats(self):
        """Test mass location stats endpoint"""
        success, data = self.run_test("Mass Location Stats", "GET", "mass-locations/stats")
        
        if success and data:
            total = data.get('total', 0)
            by_affiliation = data.get('by_affiliation', {})
            print(f"   📊 Stats: {total} total locations")
            print(f"   📊 By affiliation: {dict(list(by_affiliation.items())[:3])}...")
            
        return success, data

    def test_mass_location_search(self):
        """Test mass location search endpoint"""
        success, data = self.run_test("Mass Location Search", "GET", "mass-locations/search?q=Chicago")
        
        if success and data:
            results_count = len(data) if isinstance(data, list) else 0
            print(f"   🔍 Search 'Chicago': {results_count} results")
            
        return success, data

    def test_content_endpoint(self):
        """Test content/videos endpoint"""
        success, data = self.run_test("Content/Videos", "GET", "content")
        
        if success and data:
            content_count = len(data) if isinstance(data, list) else 0
            print(f"   📺 Found {content_count} content items")
            
        return success, data

    def test_prayers_endpoint(self):
        """Test prayers endpoint"""
        success, data = self.run_test("Prayers", "GET", "prayers")
        
        if success and data:
            prayers_count = len(data) if isinstance(data, list) else 0
            print(f"   🙏 Found {prayers_count} prayers")
            
        return success, data

    def test_seed_mass_locations(self):
        """Test seeding mass locations"""
        success, data = self.run_test("Seed Mass Locations", "POST", "mass-locations/seed")
        
        if success and data:
            inserted = data.get('inserted', 0)
            print(f"   🌱 Seeded {inserted} new locations")
            
        return success, data

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Catholic Voices & Prayers API Tests")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 60)

        # Core API tests
        self.test_health_check()
        self.test_root_endpoint()
        
        # Saints API tests
        self.test_todays_saint()
        self.test_saints_archive()
        
        # Mass locations API tests
        self.test_mass_locations()
        self.test_mass_location_filters()
        self.test_mass_location_stats()
        self.test_mass_location_search()
        
        # Content API tests
        self.test_content_endpoint()
        self.test_prayers_endpoint()
        
        # Seed data test
        self.test_seed_mass_locations()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Tests Failed: {len(self.failed_tests)}")
        
        if self.failed_tests:
            print("\n🚨 FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   • {test['name']}: {test.get('error', 'Status code mismatch')}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        # Determine overall status
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend APIs are working well!")
            return 0
        elif success_rate >= 70:
            print("⚠️  GOOD: Most APIs working, some issues to address")
            return 1
        else:
            print("🚨 CRITICAL: Major API issues detected")
            return 2

def main():
    """Main test execution"""
    tester = CatholicVoicesAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())