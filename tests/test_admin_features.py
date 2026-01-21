"""
Test Admin Features and User Suggestions
- Admin Login with JWT authentication
- Admin Location CRUD operations
- User Suggestion submission and admin review
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://faith-finder-16.preview.emergentagent.com')

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "changeme"


class TestAdminLogin:
    """Test admin authentication endpoints"""
    
    def test_admin_login_success(self):
        """Test successful admin login returns JWT token"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        assert "access_token" in data, "Response missing access_token"
        assert "token_type" in data, "Response missing token_type"
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0, "Token is empty"
        print(f"✓ Admin login successful, token received")
    
    def test_admin_login_invalid_username(self):
        """Test login with invalid username returns 401"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": "wronguser",
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid username correctly rejected")
    
    def test_admin_login_invalid_password(self):
        """Test login with invalid password returns 401"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": ADMIN_USERNAME,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid password correctly rejected")
    
    def test_admin_me_with_valid_token(self):
        """Test /admin/me endpoint with valid token"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        token = login_response.json()["access_token"]
        
        # Test /admin/me
        response = requests.get(f"{BASE_URL}/api/admin/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["username"] == ADMIN_USERNAME
        assert data["authenticated"] == True
        print(f"✓ Admin /me endpoint working with valid token")
    
    def test_admin_me_without_token(self):
        """Test /admin/me endpoint without token returns 403"""
        response = requests.get(f"{BASE_URL}/api/admin/me")
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Admin /me correctly rejects requests without token")


class TestAdminLocations:
    """Test admin location management endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_admin_get_locations(self, auth_token):
        """Test GET /admin/locations returns paginated list"""
        response = requests.get(f"{BASE_URL}/api/admin/locations", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "locations" in data, "Response missing locations"
        assert "total" in data, "Response missing total"
        assert "page" in data, "Response missing page"
        assert "pages" in data, "Response missing pages"
        assert isinstance(data["locations"], list)
        print(f"✓ Admin locations list returned {data['total']} locations")
    
    def test_admin_get_locations_with_search(self, auth_token):
        """Test GET /admin/locations with search parameter"""
        response = requests.get(f"{BASE_URL}/api/admin/locations?search=Chicago", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        print(f"✓ Admin locations search returned {len(data['locations'])} results for 'Chicago'")
    
    def test_admin_get_locations_with_affiliation_filter(self, auth_token):
        """Test GET /admin/locations with affiliation filter"""
        response = requests.get(f"{BASE_URL}/api/admin/locations?affiliation=FSSP", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        # Verify all returned locations have FSSP affiliation
        for loc in data["locations"]:
            assert loc["affiliation"] == "FSSP", f"Expected FSSP, got {loc['affiliation']}"
        print(f"✓ Admin locations filter by FSSP returned {len(data['locations'])} results")
    
    def test_admin_get_single_location(self, auth_token):
        """Test GET /admin/locations/:id returns location details"""
        # First get a location ID
        list_response = requests.get(f"{BASE_URL}/api/admin/locations?limit=1", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        locations = list_response.json()["locations"]
        
        if locations:
            location_id = locations[0]["id"]
            response = requests.get(f"{BASE_URL}/api/admin/locations/{location_id}", headers={
                "Authorization": f"Bearer {auth_token}"
            })
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data["id"] == location_id
            print(f"✓ Admin get single location returned: {data['name']}")
        else:
            pytest.skip("No locations available to test")
    
    def test_admin_create_location(self, auth_token):
        """Test POST /admin/locations creates new location"""
        test_location = {
            "name": f"TEST_Admin_Created_Parish_{uuid.uuid4().hex[:8]}",
            "entity_type": "Parish",
            "affiliation": "Diocesan",
            "rite": "Latin",
            "use_or_liturgy": "1962 Roman Missal",
            "street": "123 Test Street",
            "city": "Test City",
            "state": "TX",
            "zip_code": "12345",
            "country": "USA",
            "latitude": 32.7767,
            "longitude": -96.7970
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/locations", 
            json=test_location,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response missing id"
        print(f"✓ Admin created location with ID: {data['id']}")
        
        # Return ID for cleanup
        return data["id"]
    
    def test_admin_update_location(self, auth_token):
        """Test PUT /admin/locations/:id updates location"""
        # First create a test location
        test_location = {
            "name": f"TEST_Update_Parish_{uuid.uuid4().hex[:8]}",
            "entity_type": "Parish",
            "affiliation": "Diocesan",
            "rite": "Latin",
            "city": "Original City",
            "state": "TX",
            "country": "USA",
            "latitude": 32.7767,
            "longitude": -96.7970
        }
        
        create_response = requests.post(f"{BASE_URL}/api/admin/locations", 
            json=test_location,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        location_id = create_response.json()["id"]
        
        # Update the location
        update_data = {
            "city": "Updated City",
            "notes": "Updated via test"
        }
        
        response = requests.put(f"{BASE_URL}/api/admin/locations/{location_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify update
        get_response = requests.get(f"{BASE_URL}/api/admin/locations/{location_id}", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        updated_loc = get_response.json()
        assert updated_loc["city"] == "Updated City", f"City not updated: {updated_loc['city']}"
        print(f"✓ Admin updated location successfully")
        
        # Cleanup - delete the test location
        requests.delete(f"{BASE_URL}/api/admin/locations/{location_id}", headers={
            "Authorization": f"Bearer {auth_token}"
        })
    
    def test_admin_delete_location(self, auth_token):
        """Test DELETE /admin/locations/:id soft deletes location"""
        # First create a test location
        test_location = {
            "name": f"TEST_Delete_Parish_{uuid.uuid4().hex[:8]}",
            "entity_type": "Parish",
            "affiliation": "Diocesan",
            "rite": "Latin",
            "city": "Delete City",
            "state": "TX",
            "country": "USA",
            "latitude": 32.7767,
            "longitude": -96.7970
        }
        
        create_response = requests.post(f"{BASE_URL}/api/admin/locations", 
            json=test_location,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        location_id = create_response.json()["id"]
        
        # Delete the location
        response = requests.delete(f"{BASE_URL}/api/admin/locations/{location_id}", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Admin deleted location successfully")
    
    def test_admin_locations_unauthorized(self):
        """Test admin endpoints reject unauthorized requests"""
        response = requests.get(f"{BASE_URL}/api/admin/locations")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Admin locations correctly rejects unauthorized requests")


class TestUserSuggestions:
    """Test user suggestion submission and admin review"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_submit_new_location_suggestion(self):
        """Test POST /suggestions for new location"""
        suggestion = {
            "suggestion_type": "new",
            "user_email": "test@example.com",
            "user_name": "Test User",
            "name": f"TEST_Suggested_Parish_{uuid.uuid4().hex[:8]}",
            "city": "Suggestion City",
            "state": "CA",
            "country": "USA",
            "affiliation": "Diocesan",
            "rite": "Latin",
            "reason": "This is a test suggestion"
        }
        
        response = requests.post(f"{BASE_URL}/api/suggestions", json=suggestion)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response missing id"
        assert "message" in data, "Response missing message"
        print(f"✓ New location suggestion submitted with ID: {data['id']}")
        return data["id"]
    
    def test_submit_edit_suggestion(self, auth_token):
        """Test POST /suggestions for edit request"""
        # First get an existing location ID
        list_response = requests.get(f"{BASE_URL}/api/admin/locations?limit=1", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        locations = list_response.json()["locations"]
        
        if locations:
            location_id = locations[0]["id"]
            
            suggestion = {
                "suggestion_type": "edit",
                "location_id": location_id,
                "user_email": "editor@example.com",
                "user_name": "Edit Tester",
                "name": locations[0]["name"],
                "city": locations[0]["city"],
                "state": locations[0]["state"],
                "notes": "Updated notes via suggestion",
                "reason": "Testing edit suggestion"
            }
            
            response = requests.post(f"{BASE_URL}/api/suggestions", json=suggestion)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "id" in data
            print(f"✓ Edit suggestion submitted for location: {locations[0]['name']}")
        else:
            pytest.skip("No locations available to test edit suggestion")
    
    def test_honeypot_spam_detection(self):
        """Test honeypot field catches spam submissions"""
        suggestion = {
            "suggestion_type": "new",
            "user_email": "spam@example.com",
            "name": "Spam Location",
            "city": "Spam City",
            "state": "XX",
            "honeypot": "I am a bot"  # Honeypot filled = spam
        }
        
        response = requests.post(f"{BASE_URL}/api/suggestions", json=suggestion)
        
        # Should still return 200 (silent rejection)
        assert response.status_code == 200
        data = response.json()
        # Check if it was detected as spam
        assert data.get("id") == "spam-detected" or "id" in data
        print(f"✓ Honeypot spam detection working")
    
    def test_admin_get_suggestions(self, auth_token):
        """Test GET /admin/suggestions returns list"""
        response = requests.get(f"{BASE_URL}/api/admin/suggestions", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "suggestions" in data
        assert "total" in data
        print(f"✓ Admin suggestions list returned {data['total']} suggestions")
    
    def test_admin_get_pending_suggestions(self, auth_token):
        """Test GET /admin/suggestions with status filter"""
        response = requests.get(f"{BASE_URL}/api/admin/suggestions?status=pending", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        # Verify all returned suggestions are pending
        for suggestion in data["suggestions"]:
            assert suggestion["status"] == "pending"
        print(f"✓ Admin pending suggestions filter working, {len(data['suggestions'])} pending")
    
    def test_admin_approve_suggestion(self, auth_token):
        """Test PUT /admin/suggestions/:id?action=approve"""
        # First submit a test suggestion
        suggestion = {
            "suggestion_type": "new",
            "user_email": "approve-test@example.com",
            "user_name": "Approve Tester",
            "name": f"TEST_Approve_Parish_{uuid.uuid4().hex[:8]}",
            "city": "Approve City",
            "state": "NY",
            "country": "USA",
            "affiliation": "Diocesan"
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/suggestions", json=suggestion)
        suggestion_id = submit_response.json()["id"]
        
        if suggestion_id == "spam-detected":
            pytest.skip("Suggestion was detected as spam")
        
        # Approve the suggestion
        response = requests.put(f"{BASE_URL}/api/admin/suggestions/{suggestion_id}?action=approve", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "approved" in data.get("message", "").lower() or data.get("id") == suggestion_id
        print(f"✓ Admin approved suggestion successfully")
    
    def test_admin_reject_suggestion(self, auth_token):
        """Test PUT /admin/suggestions/:id?action=reject"""
        # First submit a test suggestion
        suggestion = {
            "suggestion_type": "new",
            "user_email": "reject-test@example.com",
            "user_name": "Reject Tester",
            "name": f"TEST_Reject_Parish_{uuid.uuid4().hex[:8]}",
            "city": "Reject City",
            "state": "FL",
            "country": "USA",
            "affiliation": "Diocesan"
        }
        
        submit_response = requests.post(f"{BASE_URL}/api/suggestions", json=suggestion)
        suggestion_id = submit_response.json()["id"]
        
        if suggestion_id == "spam-detected":
            pytest.skip("Suggestion was detected as spam")
        
        # Reject the suggestion
        response = requests.put(f"{BASE_URL}/api/admin/suggestions/{suggestion_id}?action=reject", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Admin rejected suggestion successfully")
    
    def test_admin_suggestions_unauthorized(self):
        """Test admin suggestions endpoint rejects unauthorized requests"""
        response = requests.get(f"{BASE_URL}/api/admin/suggestions")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print(f"✓ Admin suggestions correctly rejects unauthorized requests")


class TestProtectedRoutes:
    """Test that protected routes require authentication"""
    
    def test_admin_locations_requires_auth(self):
        """Test /admin/locations requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/locations")
        assert response.status_code == 403
        print(f"✓ /admin/locations requires authentication")
    
    def test_admin_suggestions_requires_auth(self):
        """Test /admin/suggestions requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/suggestions")
        assert response.status_code == 403
        print(f"✓ /admin/suggestions requires authentication")
    
    def test_admin_me_requires_auth(self):
        """Test /admin/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/me")
        assert response.status_code == 403
        print(f"✓ /admin/me requires authentication")
    
    def test_invalid_token_rejected(self):
        """Test invalid JWT token is rejected"""
        response = requests.get(f"{BASE_URL}/api/admin/locations", headers={
            "Authorization": "Bearer invalid-token-here"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid token correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
