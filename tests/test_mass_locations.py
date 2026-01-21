"""
Mass Locations API Tests
Tests for the Mass Map feature including:
- GET /api/mass-locations - List all locations with filters
- GET /api/mass-locations/stats - Statistics by affiliation and rite
- GET /api/mass-locations/filters - Available filter options
- GET /api/mass-locations/search - Search by text or proximity
- GET /api/mass-locations/{id} - Get specific location
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestMassLocationsAPI:
    """Mass Locations endpoint tests"""
    
    def test_get_all_locations(self):
        """Test GET /api/mass-locations returns all locations"""
        response = requests.get(f"{BASE_URL}/api/mass-locations")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify location structure
        loc = data[0]
        assert "id" in loc
        assert "name" in loc
        assert "affiliation" in loc
        assert "city" in loc
        assert "state" in loc
        assert "latitude" in loc
        assert "longitude" in loc
    
    def test_get_locations_count(self):
        """Test that we have 266 total locations"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?limit=500")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 266, f"Expected 266 locations, got {len(data)}"
    
    def test_filter_by_affiliation_sspx(self):
        """Test filtering by SSPX affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=SSPX")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 119, f"Expected 119 SSPX locations, got {len(data)}"
        
        # Verify all returned locations are SSPX
        for loc in data:
            assert loc["affiliation"] == "SSPX"
    
    def test_filter_by_affiliation_eastern_catholic(self):
        """Test filtering by Eastern Catholic affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=Eastern%20Catholic")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 104, f"Expected 104 Eastern Catholic locations, got {len(data)}"
        
        for loc in data:
            assert loc["affiliation"] == "Eastern Catholic"
    
    def test_filter_by_affiliation_ordinariate(self):
        """Test filtering by Ordinariate affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=Ordinariate")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 39, f"Expected 39 Ordinariate locations, got {len(data)}"
        
        for loc in data:
            assert loc["affiliation"] == "Ordinariate"
    
    def test_filter_by_affiliation_fssp(self):
        """Test filtering by FSSP affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=FSSP")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2, f"Expected 2 FSSP locations, got {len(data)}"
        
        for loc in data:
            assert loc["affiliation"] == "FSSP"
    
    def test_filter_by_affiliation_icksp(self):
        """Test filtering by ICKSP affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=ICKSP")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1, f"Expected 1 ICKSP location, got {len(data)}"
        
        for loc in data:
            assert loc["affiliation"] == "ICKSP"
    
    def test_filter_by_affiliation_diocesan(self):
        """Test filtering by Diocesan affiliation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?affiliation=Diocesan")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1, f"Expected 1 Diocesan location, got {len(data)}"
        
        for loc in data:
            assert loc["affiliation"] == "Diocesan"
    
    def test_filter_by_state(self):
        """Test filtering by state"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?state=TX")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        for loc in data:
            assert loc["state"] == "TX"
    
    def test_filter_by_state_california(self):
        """Test filtering by California"""
        response = requests.get(f"{BASE_URL}/api/mass-locations?state=CA")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        for loc in data:
            assert loc["state"] == "CA"


class TestMassLocationsStats:
    """Mass Locations stats endpoint tests"""
    
    def test_get_stats(self):
        """Test GET /api/mass-locations/stats returns correct statistics"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total" in data
        assert "by_affiliation" in data
        assert "by_rite" in data
    
    def test_stats_total_count(self):
        """Test that stats show 266 total locations"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 266, f"Expected 266 total, got {data['total']}"
    
    def test_stats_affiliation_counts(self):
        """Test affiliation counts match expected values"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        
        data = response.json()
        by_aff = data["by_affiliation"]
        
        assert by_aff.get("SSPX") == 119, f"Expected SSPX=119, got {by_aff.get('SSPX')}"
        assert by_aff.get("Eastern Catholic") == 104, f"Expected Eastern Catholic=104, got {by_aff.get('Eastern Catholic')}"
        assert by_aff.get("Ordinariate") == 39, f"Expected Ordinariate=39, got {by_aff.get('Ordinariate')}"
        assert by_aff.get("FSSP") == 2, f"Expected FSSP=2, got {by_aff.get('FSSP')}"
        assert by_aff.get("ICKSP") == 1, f"Expected ICKSP=1, got {by_aff.get('ICKSP')}"
        assert by_aff.get("Diocesan") == 1, f"Expected Diocesan=1, got {by_aff.get('Diocesan')}"
    
    def test_stats_rite_counts(self):
        """Test rite counts are present"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/stats")
        assert response.status_code == 200
        
        data = response.json()
        by_rite = data["by_rite"]
        
        assert "Latin" in by_rite
        assert "Byzantine" in by_rite
        assert by_rite["Latin"] == 162


class TestMassLocationsFilters:
    """Mass Locations filters endpoint tests"""
    
    def test_get_filters(self):
        """Test GET /api/mass-locations/filters returns filter options"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/filters")
        assert response.status_code == 200
        
        data = response.json()
        assert "affiliations" in data
        assert "rites" in data
        assert "liturgies" in data
        assert "states" in data
    
    def test_filters_affiliations(self):
        """Test all 6 affiliations are present"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/filters")
        assert response.status_code == 200
        
        data = response.json()
        affiliations = data["affiliations"]
        
        expected = ["Diocesan", "Eastern Catholic", "FSSP", "ICKSP", "Ordinariate", "SSPX"]
        assert affiliations == expected, f"Expected {expected}, got {affiliations}"
    
    def test_filters_states_count(self):
        """Test 49 states are covered"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/filters")
        assert response.status_code == 200
        
        data = response.json()
        states = data["states"]
        
        assert len(states) == 49, f"Expected 49 states, got {len(states)}"


class TestMassLocationsSearch:
    """Mass Locations search endpoint tests"""
    
    def test_search_by_city(self):
        """Test search by city name"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=Chicago")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        # At least one result should have Chicago in city
        cities = [loc["city"] for loc in data]
        assert "Chicago" in cities
    
    def test_search_by_state_abbreviation(self):
        """Test search by state abbreviation"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=TX")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
        
        for loc in data:
            assert loc["state"] == "TX"
    
    def test_search_by_parish_name(self):
        """Test search by parish name"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=St.%20Mary")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0
    
    def test_search_with_affiliation_filter(self):
        """Test search with affiliation filter"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=TX&affiliation=SSPX")
        assert response.status_code == 200
        
        data = response.json()
        for loc in data:
            assert loc["affiliation"] == "SSPX"
            assert loc["state"] == "TX"
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/search?q=ZZZZNONEXISTENT")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 0


class TestMassLocationDetail:
    """Mass Location detail endpoint tests"""
    
    def test_get_location_by_id(self):
        """Test GET /api/mass-locations/{id} returns location details"""
        # First get a location ID
        response = requests.get(f"{BASE_URL}/api/mass-locations?limit=1")
        assert response.status_code == 200
        
        locations = response.json()
        assert len(locations) > 0
        
        location_id = locations[0]["id"]
        
        # Now get the specific location
        response = requests.get(f"{BASE_URL}/api/mass-locations/{location_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == location_id
        assert "name" in data
        assert "affiliation" in data
        assert "latitude" in data
        assert "longitude" in data
    
    def test_get_location_not_found(self):
        """Test GET /api/mass-locations/{id} with invalid ID returns 404"""
        response = requests.get(f"{BASE_URL}/api/mass-locations/invalid-id-12345")
        assert response.status_code == 404


class TestHealthAndRoot:
    """Basic API health tests"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data or "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
