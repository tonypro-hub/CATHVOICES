import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MassMap.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Fix Leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const AFFILIATION_COLORS = {
  'Diocesan': '#2563eb',
  'FSSP': '#059669',
  'ICKSP': '#7c3aed',
  'Ordinariate': '#dc2626',
  'SSPX': '#d97706',
  'Eastern Catholic': '#0891b2'
};

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
  'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
  'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

const createMarkerIcon = (color, isSelected = false) => {
  const size = isSelected ? 16 : 12;
  const svgIcon = `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 1}" fill="${color}" stroke="white" stroke-width="2"/>
    </svg>
  `;
  return L.divIcon({
    html: svgIcon,
    className: `custom-marker ${isSelected ? 'selected' : ''}`,
    iconSize: [size, size],
    iconAnchor: [size/2, size/2],
  });
};

const createUserLocationIcon = () => {
  const svgIcon = `
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="8" fill="#3b82f6" stroke="white" stroke-width="3"/>
      <circle cx="12" cy="12" r="3" fill="white"/>
    </svg>
  `;
  return L.divIcon({
    html: svgIcon,
    className: 'user-location-marker',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const MapController = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1 });
  }, [center, zoom, map]);
  return null;
};

const MassMap = () => {
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [filters, setFilters] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [activeAffiliation, setActiveAffiliation] = useState('');
  const [activeRite, setActiveRite] = useState('');
  const [activeState, setActiveState] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchInput, setSearchInput] = useState('');
  
  const [mapCenter, setMapCenter] = useState([39.8283, -98.5795]);
  const [mapZoom, setMapZoom] = useState(4);
  
  const [showMobileList, setShowMobileList] = useState(false);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  
  // Geolocation state
  const [userLocation, setUserLocation] = useState(null);
  const [nearbyMode, setNearbyMode] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState(null);
  const [nearbyRadius, setNearbyRadius] = useState(50);

  useEffect(() => {
    fetchFilters();
    fetchStats();
    fetchLocations();
  }, []);

  useEffect(() => {
    if (nearbyMode && userLocation) {
      fetchNearbyLocations();
    } else {
      fetchLocations();
    }
  }, [activeAffiliation, activeRite, activeState, searchQuery, nearbyMode, userLocation, nearbyRadius]);

  const fetchFilters = async () => {
    try {
      const response = await fetch(`${API}/mass-locations/filters`);
      if (response.ok) setFilters(await response.json());
    } catch (error) {
      console.error('Error fetching filters:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API}/mass-locations/stats`);
      if (response.ok) setStats(await response.json());
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchLocations = async () => {
    try {
      setLoading(true);
      let url = `${API}/mass-locations?`;
      const params = new URLSearchParams();
      
      if (activeAffiliation) params.append('affiliation', activeAffiliation);
      if (activeRite) params.append('rite', activeRite);
      if (activeState) params.append('state', activeState);
      if (searchQuery) {
        url = `${API}/mass-locations/search?`;
        params.append('q', searchQuery);
      }
      
      const response = await fetch(url + params.toString());
      if (response.ok) setLocations(await response.json());
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNearbyLocations = async () => {
    if (!userLocation) return;
    
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.append('lat', userLocation.lat);
      params.append('lng', userLocation.lng);
      params.append('radius_miles', nearbyRadius);
      
      if (activeAffiliation) params.append('affiliation', activeAffiliation);
      if (activeRite) params.append('rite', activeRite);
      
      const response = await fetch(`${API}/mass-locations/search?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setLocations(data);
      }
    } catch (error) {
      console.error('Error fetching nearby locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const findNearbyMasses = () => {
    if (!navigator.geolocation) {
      setGeoError('Geolocation is not supported by your browser');
      return;
    }
    
    setGeoLoading(true);
    setGeoError(null);
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lng: longitude });
        setMapCenter([latitude, longitude]);
        setMapZoom(9);
        setNearbyMode(true);
        setGeoLoading(false);
        setActiveState(''); // Clear state filter when using nearby
        setSearchQuery('');
        setSearchInput('');
      },
      (error) => {
        setGeoLoading(false);
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setGeoError('Location access denied. Please enable location services.');
            break;
          case error.POSITION_UNAVAILABLE:
            setGeoError('Location information unavailable.');
            break;
          case error.TIMEOUT:
            setGeoError('Location request timed out.');
            break;
          default:
            setGeoError('An error occurred getting your location.');
        }
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
  };

  const clearNearbyMode = () => {
    setNearbyMode(false);
    setUserLocation(null);
    setGeoError(null);
    setMapCenter([39.8283, -98.5795]);
    setMapZoom(4);
    fetchLocations();
  };

  const handleSearch = useCallback((e) => {
    e.preventDefault();
    setSearchQuery(searchInput);
  }, [searchInput]);

  const clearFilters = () => {
    setActiveAffiliation('');
    setActiveRite('');
    setActiveState('');
    setSearchQuery('');
    setSearchInput('');
    setSelectedLocation(null);
    setNearbyMode(false);
    setUserLocation(null);
    setGeoError(null);
    setMapCenter([39.8283, -98.5795]);
    setMapZoom(4);
  };

  const selectLocation = (location) => {
    setSelectedLocation(location);
    setMapCenter([location.latitude, location.longitude]);
    setMapZoom(13);
    setShowMobileList(false);
  };

  const getMarkerColor = (affiliation) => AFFILIATION_COLORS[affiliation] || '#6b7280';

  const filterCounts = useMemo(() => {
    const counts = {};
    locations.forEach(loc => {
      counts[loc.affiliation] = (counts[loc.affiliation] || 0) + 1;
      counts[loc.state] = (counts[loc.state] || 0) + 1;
    });
    return counts;
  }, [locations]);

  return (
    <div className="mass-map-page" data-testid="mass-map-page">
      {/* Hero */}
      <section className="map-hero">
        <div className="container">
          <h1 className="map-title">Reverent Catholic Mass Map</h1>
          <p className="map-subtitle">
            Find Traditional Latin Masses, Eastern Catholic parishes, and reverent liturgies across the United States
          </p>
        </div>
      </section>

      {/* Search & Filters */}
      <section className="map-controls">
        <div className="container">
          <form className="search-form" onSubmit={handleSearch}>
            <div className="search-input-wrapper">
              <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <input
                type="text"
                placeholder="Search by city, state, or parish name..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="search-input"
                data-testid="map-search-input"
                disabled={nearbyMode}
              />
              {searchInput && (
                <button type="button" className="clear-search" onClick={() => { setSearchInput(''); setSearchQuery(''); }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
            <button type="submit" className="search-btn" disabled={nearbyMode}>Search</button>
            
            {!nearbyMode ? (
              <button 
                type="button" 
                className="nearby-btn"
                onClick={findNearbyMasses}
                disabled={geoLoading}
                data-testid="find-nearby-btn"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
                </svg>
                {geoLoading ? 'Finding...' : 'Find Nearby'}
              </button>
            ) : (
              <button 
                type="button" 
                className="nearby-btn nearby-btn-active"
                onClick={clearNearbyMode}
                data-testid="clear-nearby-btn"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
                Exit Nearby
              </button>
            )}
          </form>
          
          {/* Nearby Mode Controls */}
          {nearbyMode && (
            <div className="nearby-controls" data-testid="nearby-controls">
              <div className="nearby-info">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <span>Showing masses within <strong>{nearbyRadius} miles</strong> of your location</span>
              </div>
              <div className="radius-selector">
                <label>Radius:</label>
                <select 
                  value={nearbyRadius} 
                  onChange={(e) => setNearbyRadius(Number(e.target.value))}
                  className="radius-select"
                  data-testid="radius-select"
                >
                  <option value={10}>10 miles</option>
                  <option value={25}>25 miles</option>
                  <option value={50}>50 miles</option>
                  <option value={100}>100 miles</option>
                  <option value={200}>200 miles</option>
                </select>
              </div>
            </div>
          )}
          
          {/* Geolocation Error */}
          {geoError && (
            <div className="geo-error" data-testid="geo-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 8v4M12 16h.01" />
              </svg>
              <span>{geoError}</span>
            </div>
          )}

          <button className="mobile-filter-toggle" onClick={() => setShowMobileFilters(!showMobileFilters)}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            Filters
            {(activeAffiliation || activeRite || activeState) && (
              <span className="filter-badge">{[activeAffiliation, activeRite, activeState].filter(Boolean).length}</span>
            )}
          </button>

          <div className={`filter-section ${showMobileFilters ? 'show-mobile' : ''}`}>
            <div className="filter-group">
              <span className="filter-label">Affiliation:</span>
              <div className="filter-chips">
                <button className={`filter-chip ${!activeAffiliation ? 'filter-chip-active' : ''}`} onClick={() => setActiveAffiliation('')}>All</button>
                {filters?.affiliations.map((aff) => (
                  <button
                    key={aff}
                    className={`filter-chip ${activeAffiliation === aff ? 'filter-chip-active' : ''}`}
                    onClick={() => setActiveAffiliation(aff)}
                  >
                    <span className="chip-dot" style={{ backgroundColor: getMarkerColor(aff) }} />
                    {aff}
                    {stats?.by_affiliation[aff] && <span className="chip-count">({stats.by_affiliation[aff]})</span>}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <span className="filter-label">State:</span>
              <select className="state-select" value={activeState} onChange={(e) => setActiveState(e.target.value)}>
                <option value="">All States</option>
                {US_STATES.map(state => (
                  <option key={state} value={state}>{state} {filterCounts[state] ? `(${filterCounts[state]})` : ''}</option>
                ))}
              </select>
            </div>

            {(activeAffiliation || activeRite || activeState || searchQuery) && (
              <button className="clear-filters" onClick={clearFilters}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
                Clear All Filters
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Map & List */}
      <section className="map-content">
        <div className="container">
          <div className="map-layout">
            <div className="map-container">
              <MapContainer center={mapCenter} zoom={mapZoom} className="leaflet-map" scrollWheelZoom={true} zoomControl={true}>
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapController center={mapCenter} zoom={mapZoom} />
                
                {locations.map((loc) => (
                  <Marker
                    key={loc.id}
                    position={[loc.latitude, loc.longitude]}
                    icon={createMarkerIcon(getMarkerColor(loc.affiliation), selectedLocation?.id === loc.id)}
                    eventHandlers={{ click: () => selectLocation(loc) }}
                  >
                    <Popup>
                      <div className="marker-popup">
                        <h4>{loc.name}</h4>
                        <p className="popup-location">{loc.city}, {loc.state}</p>
                        <p className="popup-affiliation" style={{ color: getMarkerColor(loc.affiliation) }}>
                          {loc.affiliation} • {loc.rite}
                        </p>
                        <button className="popup-details-btn" onClick={() => selectLocation(loc)}>View Details →</button>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>

              <div className="map-stats-badge">
                <span className="stats-count">{locations.length}</span>
                <span className="stats-label">locations</span>
              </div>

              <div className="map-legend">
                <span className="legend-title">Legend</span>
                <div className="legend-items">
                  {Object.entries(AFFILIATION_COLORS).map(([name, color]) => (
                    <div key={name} className="legend-item">
                      <span className="legend-dot" style={{ backgroundColor: color }} />
                      <span className="legend-name">{name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <button className="mobile-list-toggle" onClick={() => setShowMobileList(!showMobileList)}>
              {showMobileList ? 'Hide List' : 'Show List'} ({locations.length})
            </button>

            <div className={`locations-panel ${showMobileList ? 'show-mobile' : ''}`}>
              {selectedLocation ? (
                <div className="location-detail">
                  <button className="back-to-list" onClick={() => setSelectedLocation(null)}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M19 12H5M12 19l-7-7 7-7" />
                    </svg>
                    Back to List
                  </button>

                  <div className="detail-header">
                    <span className="detail-badge" style={{ backgroundColor: getMarkerColor(selectedLocation.affiliation) }}>
                      {selectedLocation.affiliation}
                    </span>
                    <h2 className="detail-name">{selectedLocation.name}</h2>
                    <p className="detail-type">{selectedLocation.entity_type} • {selectedLocation.rite} Rite</p>
                  </div>

                  <div className="detail-info">
                    <div className="info-row">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                        <circle cx="12" cy="10" r="3" />
                      </svg>
                      <div>
                        <p className="info-primary">{selectedLocation.street || 'Address not available'}</p>
                        <p className="info-secondary">{selectedLocation.city}, {selectedLocation.state} {selectedLocation.zip_code}</p>
                      </div>
                    </div>

                    {selectedLocation.notes && (
                      <div className="info-row info-notes">
                        <p className="info-note">{selectedLocation.notes}</p>
                      </div>
                    )}
                  </div>

                  <div className="detail-actions">
                    {selectedLocation.website_url && (
                      <a href={selectedLocation.website_url} target="_blank" rel="noopener noreferrer" className="action-btn action-primary">
                        Parish Website
                      </a>
                    )}
                    <a 
                      href={`https://www.google.com/maps/dir/?api=1&destination=${selectedLocation.latitude},${selectedLocation.longitude}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="action-btn"
                    >
                      Get Directions
                    </a>
                  </div>
                </div>
              ) : (
                <div className="locations-list">
                  <div className="list-header">
                    <h3>Locations</h3>
                    <span className="list-count">{locations.length} found</span>
                  </div>
                  
                  {loading ? (
                    <div className="loading-state">
                      <div className="loading-spinner" />
                      <span>Loading locations...</span>
                    </div>
                  ) : locations.length > 0 ? (
                    <div className="list-scroll">
                      {locations.map((loc) => (
                        <button key={loc.id} className="location-card" onClick={() => selectLocation(loc)}>
                          <div className="card-indicator" style={{ backgroundColor: getMarkerColor(loc.affiliation) }} />
                          <div className="card-content">
                            <h4 className="card-name">{loc.name}</h4>
                            <p className="card-location">{loc.city}, {loc.state}</p>
                            <div className="card-tags">
                              <span className="card-tag">{loc.affiliation}</span>
                              <span className="card-tag">{loc.rite}</span>
                            </div>
                          </div>
                          <svg className="card-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M9 18l6-6-6-6" />
                          </svg>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <p>No locations found</p>
                      <span>Try adjusting your filters</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      {stats && (
        <section className="map-stats-section">
          <div className="container">
            <h3 className="stats-title">Directory Statistics</h3>
            <div className="stats-grid">
              <div className="stat-card stat-card-total">
                <span className="stat-number">{stats.total}</span>
                <span className="stat-label">Total Locations</span>
              </div>
              {Object.entries(stats.by_affiliation).sort((a, b) => b[1] - a[1]).map(([name, count]) => (
                <div key={name} className="stat-card">
                  <span className="stat-number" style={{ color: getMarkerColor(name) }}>{count}</span>
                  <span className="stat-label">{name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Disclaimer */}
      <section className="map-disclaimer" data-testid="map-disclaimer">
        <div className="container container-narrow">
          <div className="disclaimer-box">
            <h4>About This Directory</h4>
            <p>
              This map is a curated directory of reverent Catholic Mass locations in the United States. 
              It includes Diocesan Traditional Latin Mass communities, FSSP and ICKSP parishes, 
              Ordinariate communities, SSPX chapels, and all Eastern Catholic parishes.
            </p>
            <p>
              This directory does not include sedevacantist groups. All listings are reviewed for 
              Catholic sacramental validity.
            </p>
            <p className="disclaimer-link">
              <Link to="/sspx-explained" className="sspx-info-link">
                Read more about SSPX Masses and the Sunday Obligation →
              </Link>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default MassMap;
