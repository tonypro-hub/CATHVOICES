"""
Test suite for new features:
- Mass Map with 309 locations (ICKSP: 27, FSSP: 19)
- Favorites feature (localStorage - frontend only)
- Find Nearby geolocation (frontend only)
- SEO meta tags
- Social sharing buttons (frontend only)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMassLocationsStats:
    """Test Mass Locations stats endpoint - verify 309 total locations"""
    
    def test_stats_returns_309_total(self):
        """Verify total count is 309"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 309, f"Expected 309 total, got {data['total']}"
    
    def test_stats_icksp_count(self):
        """Verify ICKSP count is 27"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["by_affiliation"]["ICKSP"] == 27, f"Expected 27 ICKSP, got {data['by_affiliation'].get('ICKSP')}"
    
    def test_stats_fssp_count(self):
        """Verify FSSP count is 19"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["by_affiliation"]["FSSP"] == 19, f"Expected 19 FSSP, got {data['by_affiliation'].get('FSSP')}"
    
    def test_stats_sspx_count(self):
        """Verify SSPX count is 119"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["by_affiliation"]["SSPX"] == 119, f"Expected 119 SSPX, got {data['by_affiliation'].get('SSPX')}"
    
    def test_stats_eastern_catholic_count(self):
        """Verify Eastern Catholic count is 104"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["by_affiliation"]["Eastern Catholic"] == 104, f"Expected 104 Eastern Catholic, got {data['by_affiliation'].get('Eastern Catholic')}"
    
    def test_stats_ordinariate_count(self):
        """Verify Ordinariate count is 39"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["by_affiliation"]["Ordinariate"] == 39, f"Expected 39 Ordinariate, got {data['by_affiliation'].get('Ordinariate')}"


class TestMassLocationsFiltering:
    """Test Mass Locations filtering by affiliation"""
    
    def test_filter_icksp_returns_27(self):
        """Filter by ICKSP should return 27 locations"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=ICKSP")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 27, f"Expected 27 ICKSP locations, got {len(data)}"
    
    def test_filter_fssp_returns_19(self):
        """Filter by FSSP should return 19 locations"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=FSSP")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 19, f"Expected 19 FSSP locations, got {len(data)}"
    
    def test_icksp_locations_have_correct_affiliation(self):
        """All ICKSP filtered locations should have ICKSP affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=ICKSP")
        assert response.status_code == 200
        data = response.json()
        for loc in data:
            assert loc["affiliation"] == "ICKSP", f"Location {loc['name']} has wrong affiliation: {loc['affiliation']}"
    
    def test_fssp_locations_have_correct_affiliation(self):
        """All FSSP filtered locations should have FSSP affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=FSSP")
        assert response.status_code == 200
        data = response.json()
        for loc in data:
            assert loc["affiliation"] == "FSSP", f"Location {loc['name']} has wrong affiliation: {loc['affiliation']}"


class TestMassLocationsSearch:
    """Test Mass Locations search functionality"""
    
    def test_search_by_city(self):
        """Search by city name should return results"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=Chicago")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0, "Expected at least one result for Chicago"
    
    def test_search_by_state(self):
        """Search by state should return results"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=TX")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0, "Expected at least one result for TX"
    
    def test_nearby_search_with_coordinates(self):
        """Search with lat/lng should return nearby locations with distance"""
        # Chicago coordinates
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?lat=41.8781&lng=-87.6298&radius_miles=50")
        assert response.status_code == 200
        data = response.json()
        # Should return locations with distance_miles field
        if len(data) > 0:
            assert "distance_miles" in data[0], "Nearby search should include distance_miles"


class TestDailySaint:
    """Test Daily Saint endpoint"""
    
    def test_today_saint_returns_data(self):
        """Today's saint endpoint should return saint data"""
        response = requests.get(f"{BASE_URL}/api/saints/today")
        assert response.status_code == 200
        data = response.json()
        assert "saintName" in data, "Response should include saintName"
        assert "videoId" in data, "Response should include videoId"
        assert "feastDate" in data, "Response should include feastDate"
    
    def test_today_saint_has_youtube_url(self):
        """Today's saint should have YouTube URL"""
        response = requests.get(f"{BASE_URL}/api/saints/today")
        assert response.status_code == 200
        data = response.json()
        assert "youtubeUrl" in data, "Response should include youtubeUrl"
        assert "youtube.com" in data["youtubeUrl"], "YouTube URL should be valid"


class TestMassLocationsFilters:
    """Test Mass Locations filters endpoint"""
    
    def test_filters_returns_affiliations(self):
        """Filters endpoint should return affiliations list"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/filters")
        assert response.status_code == 200
        data = response.json()
        assert "affiliations" in data, "Response should include affiliations"
        assert "ICKSP" in data["affiliations"], "ICKSP should be in affiliations"
        assert "FSSP" in data["affiliations"], "FSSP should be in affiliations"
    
    def test_filters_returns_states(self):
        """Filters endpoint should return states list"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/filters")
        assert response.status_code == 200
        data = response.json()
        assert "states" in data, "Response should include states"
        assert len(data["states"]) > 0, "Should have at least one state"


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_returns_healthy(self):
        """Health endpoint should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy", "Status should be healthy"
        assert data["database"] == "connected", "Database should be connected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
