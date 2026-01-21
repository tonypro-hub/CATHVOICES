import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import SEO from '../components/SEO';
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
  
  // Favorites state
  const [favorites, setFavorites] = useState(() => {
    const saved = localStorage.getItem('massMapFavorites');
    return saved ? JSON.parse(saved) : [];
  });
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  
  // Geolocation state
  const [userLocation, setUserLocation] = useState(null);
  const [nearbyMode, setNearbyMode] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState(null);
  const [nearbyRadius, setNearbyRadius] = useState(50);
  
  // Suggestion modal state
  const [showSuggestionModal, setShowSuggestionModal] = useState(false);
  const [suggestionType, setSuggestionType] = useState('new');
  const [suggestionSubmitting, setSuggestionSubmitting] = useState(false);
  const [suggestionSuccess, setSuggestionSuccess] = useState(false);
  const [suggestionError, setSuggestionError] = useState('');
  const [suggestionForm, setSuggestionForm] = useState({
    name: '',
    street: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA',
    affiliation: 'Diocesan',
    rite: 'Latin',
    mass_schedule: '',
    website_url: '',
    phone: '',
    notes: '',
    reason: '',
    user_name: '',
    user_email: '',
    honeypot: ''
  });
  
  // Quick report modal state
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportLocation, setReportLocation] = useState(null);
  const [reportSubmitting, setReportSubmitting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);
  const [reportError, setReportError] = useState('');
  const [reportForm, setReportForm] = useState({
    issue_type: 'incorrect_info',
    description: '',
    user_email: ''
  });

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

  // Favorites functions
  const toggleFavorite = (locationId) => {
    setFavorites(prev => {
      const newFavorites = prev.includes(locationId)
        ? prev.filter(id => id !== locationId)
        : [...prev, locationId];
      localStorage.setItem('massMapFavorites', JSON.stringify(newFavorites));
      return newFavorites;
    });
  };

  const isFavorite = (locationId) => favorites.includes(locationId);

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
    setShowFavoritesOnly(false);
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

  // Suggestion handlers
  const openSuggestionModal = (type = 'new', location = null) => {
    setSuggestionType(type);
    setSuggestionSuccess(false);
    setSuggestionError('');
    
    if (type === 'edit' && location) {
      setSuggestionForm({
        name: location.name || '',
        street: location.street || '',
        city: location.city || '',
        state: location.state || '',
        zip_code: location.zip_code || '',
        country: location.country || 'USA',
        affiliation: location.affiliation || 'Diocesan',
        rite: location.rite || 'Latin',
        mass_schedule: '',
        website_url: location.website_url || '',
        phone: location.phone || '',
        notes: location.notes || '',
        reason: '',
        user_name: '',
        user_email: '',
        honeypot: '',
        location_id: location.id
      });
    } else {
      setSuggestionForm({
        name: '',
        street: '',
        city: '',
        state: '',
        zip_code: '',
        country: 'USA',
        affiliation: 'Diocesan',
        rite: 'Latin',
        mass_schedule: '',
        website_url: '',
        phone: '',
        notes: '',
        reason: '',
        user_name: '',
        user_email: '',
        honeypot: ''
      });
    }
    setShowSuggestionModal(true);
  };

  const handleSuggestionChange = (e) => {
    const { name, value } = e.target;
    setSuggestionForm(prev => ({ ...prev, [name]: value }));
  };

  const submitSuggestion = async (e) => {
    e.preventDefault();
    setSuggestionSubmitting(true);
    setSuggestionError('');

    try {
      const payload = {
        suggestion_type: suggestionType,
        location_id: suggestionForm.location_id || null,
        user_email: suggestionForm.user_email,
        user_name: suggestionForm.user_name,
        name: suggestionForm.name,
        street: suggestionForm.street,
        city: suggestionForm.city,
        state: suggestionForm.state,
        zip_code: suggestionForm.zip_code,
        country: suggestionForm.country,
        affiliation: suggestionForm.affiliation,
        rite: suggestionForm.rite,
        mass_schedule: suggestionForm.mass_schedule,
        website_url: suggestionForm.website_url,
        phone: suggestionForm.phone,
        notes: suggestionForm.notes,
        reason: suggestionForm.reason,
        honeypot: suggestionForm.honeypot
      };

      const response = await fetch(`${API}/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setSuggestionSuccess(true);
      } else {
        const data = await response.json();
        setSuggestionError(data.detail || 'Failed to submit suggestion');
      }
    } catch (error) {
      setSuggestionError('An error occurred. Please try again.');
    } finally {
      setSuggestionSubmitting(false);
    }
  };

  const closeSuggestionModal = () => {
    setShowSuggestionModal(false);
    setSuggestionSuccess(false);
    setSuggestionError('');
  };

  // Quick report handlers
  const openReportModal = (location) => {
    setReportLocation(location);
    setReportSuccess(false);
    setReportError('');
    setReportForm({
      issue_type: 'incorrect_info',
      description: '',
      user_email: ''
    });
    setShowReportModal(true);
  };

  const handleReportChange = (e) => {
    const { name, value } = e.target;
    setReportForm(prev => ({ ...prev, [name]: value }));
  };

  const submitReport = async (e) => {
    e.preventDefault();
    setReportSubmitting(true);
    setReportError('');

    try {
      const issueLabels = {
        'incorrect_info': 'Incorrect Information',
        'closed': 'Location Closed/No Longer Exists',
        'wrong_times': 'Wrong Mass Times',
        'wrong_address': 'Wrong Address',
        'other': 'Other Issue'
      };

      const payload = {
        suggestion_type: 'edit',
        location_id: reportLocation.id,
        user_email: reportForm.user_email,
        name: reportLocation.name,
        city: reportLocation.city,
        state: reportLocation.state,
        country: reportLocation.country || 'USA',
        reason: `[${issueLabels[reportForm.issue_type]}] ${reportForm.description}`
      };

      const response = await fetch(`${API}/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setReportSuccess(true);
      } else {
        const data = await response.json();
        setReportError(data.detail || 'Failed to submit report');
      }
    } catch (error) {
      setReportError('An error occurred. Please try again.');
    } finally {
      setReportSubmitting(false);
    }
  };

  const closeReportModal = () => {
    setShowReportModal(false);
    setReportSuccess(false);
    setReportError('');
  };

  // Filter locations based on favorites if enabled
  const displayedLocations = useMemo(() => {
    if (showFavoritesOnly) {
      return locations.filter(loc => favorites.includes(loc.id));
    }
    return locations;
  }, [locations, showFavoritesOnly, favorites]);

  const filterCounts = useMemo(() => {
    const counts = {};
    displayedLocations.forEach(loc => {
      counts[loc.affiliation] = (counts[loc.affiliation] || 0) + 1;
      counts[loc.state] = (counts[loc.state] || 0) + 1;
    });
    return counts;
  }, [displayedLocations]);

  return (
    <div className="mass-map-page" data-testid="mass-map-page">
      <SEO 
        title="Mass Map - Find a Latin Mass Near You"
        description="Find Traditional Latin Masses, Eastern Catholic parishes, SSPX chapels, FSSP parishes, and reverent liturgies across the United States. 266+ locations in 49 states."
        keywords="Latin Mass finder, Traditional Latin Mass, SSPX chapel, FSSP parish, Eastern Catholic, Byzantine Catholic, mass near me, TLM finder"
      />
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

            {/* Favorites Toggle */}
            <button 
              className={`favorites-toggle ${showFavoritesOnly ? 'favorites-toggle-active' : ''}`}
              onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
              data-testid="favorites-toggle"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill={showFavoritesOnly ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
              </svg>
              Favorites {favorites.length > 0 && <span className="favorites-count">({favorites.length})</span>}
            </button>

            {/* Suggest Location Button */}
            <button 
              className="suggest-location-btn"
              onClick={() => openSuggestionModal('new')}
              data-testid="suggest-location-btn"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 8v8M8 12h8" />
              </svg>
              Suggest a Location
            </button>

            {(activeAffiliation || activeRite || activeState || searchQuery || nearbyMode || showFavoritesOnly) && (
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
                
                {/* User location marker */}
                {userLocation && (
                  <Marker
                    position={[userLocation.lat, userLocation.lng]}
                    icon={createUserLocationIcon()}
                    zIndexOffset={1000}
                  >
                    <Popup>
                      <div className="marker-popup user-location-popup">
                        <h4>Your Location</h4>
                        <p className="popup-location">Showing masses within {nearbyRadius} miles</p>
                      </div>
                    </Popup>
                  </Marker>
                )}
                
                {locations.map((loc) => (
                  <Marker
                    key={loc.id}
                    position={[loc.latitude, loc.longitude]}
                    icon={createMarkerIcon(getMarkerColor(loc.affiliation), selectedLocation?.id === loc.id)}
                    eventHandlers={{ click: () => selectLocation(loc) }}
                  >
                    <Popup>
                      <div className="marker-popup">
                        <div className="popup-header">
                          <h4>{loc.name}</h4>
                          <button 
                            className={`popup-favorite-btn ${isFavorite(loc.id) ? 'is-favorite' : ''}`}
                            onClick={(e) => { e.stopPropagation(); toggleFavorite(loc.id); }}
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill={isFavorite(loc.id) ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                            </svg>
                          </button>
                        </div>
                        <p className="popup-location">{loc.city}, {loc.state}</p>
                        <p className="popup-affiliation" style={{ color: getMarkerColor(loc.affiliation) }}>
                          {loc.affiliation} • {loc.rite}
                        </p>
                        {loc.mass_schedule && (
                          <div className="popup-mass-times">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <circle cx="12" cy="12" r="10" />
                              <path d="M12 6v6l4 2" />
                            </svg>
                            <span>{loc.mass_schedule}</span>
                          </div>
                        )}
                        {loc.distance_miles && (
                          <p className="popup-distance">{loc.distance_miles} miles away</p>
                        )}
                        <div className="popup-actions">
                          <button className="popup-details-btn" onClick={() => selectLocation(loc)}>View Details →</button>
                          <button 
                            className="popup-report-btn" 
                            onClick={(e) => { e.stopPropagation(); openReportModal(loc); }}
                            title="Report an issue"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <circle cx="12" cy="12" r="10" />
                              <path d="M12 8v4M12 16h.01" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>

              <div className="map-stats-badge">
                <span className="stats-count">{displayedLocations.length}</span>
                <span className="stats-label">{showFavoritesOnly ? 'favorites' : 'locations'}</span>
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
                    <div className="detail-header-top">
                      <span className="detail-badge" style={{ backgroundColor: getMarkerColor(selectedLocation.affiliation) }}>
                        {selectedLocation.affiliation}
                      </span>
                      <button 
                        className={`detail-favorite-btn ${isFavorite(selectedLocation.id) ? 'is-favorite' : ''}`}
                        onClick={() => toggleFavorite(selectedLocation.id)}
                        data-testid="detail-favorite-btn"
                      >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill={isFavorite(selectedLocation.id) ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                        </svg>
                        {isFavorite(selectedLocation.id) ? 'Saved' : 'Save'}
                      </button>
                    </div>
                    <h2 className="detail-name">{selectedLocation.name}</h2>
                    <p className="detail-type">{selectedLocation.entity_type} • {selectedLocation.rite} Rite</p>
                  </div>

                  <div className="detail-info">
                    {selectedLocation.mass_schedule && (
                      <div className="info-row info-mass-times">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <path d="M12 6v6l4 2" />
                        </svg>
                        <div>
                          <p className="info-label">Mass Times</p>
                          <p className="info-mass-schedule">{selectedLocation.mass_schedule}</p>
                        </div>
                      </div>
                    )}

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
                    <button 
                      className="action-btn action-suggest"
                      onClick={() => openSuggestionModal('edit', selectedLocation)}
                      data-testid="suggest-edit-btn"
                    >
                      Suggest Edit
                    </button>
                    <button 
                      className="action-btn action-report"
                      onClick={() => openReportModal(selectedLocation)}
                      data-testid="report-issue-btn"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 8v4M12 16h.01" />
                      </svg>
                      Report Issue
                    </button>
                  </div>
                </div>
              ) : (
                <div className="locations-list">
                  <div className="list-header">
                    <h3>{showFavoritesOnly ? 'My Favorites' : nearbyMode ? 'Nearby Masses' : 'Locations'}</h3>
                    <span className="list-count">{displayedLocations.length} found</span>
                  </div>
                  
                  {loading ? (
                    <div className="loading-state">
                      <div className="loading-spinner" />
                      <span>Loading locations...</span>
                    </div>
                  ) : displayedLocations.length > 0 ? (
                    <div className="list-scroll">
                      {displayedLocations.map((loc) => (
                        <button key={loc.id} className="location-card" onClick={() => selectLocation(loc)}>
                          <div className="card-indicator" style={{ backgroundColor: getMarkerColor(loc.affiliation) }} />
                          <div className="card-content">
                            <div className="card-header">
                              <h4 className="card-name">{loc.name}</h4>
                              {isFavorite(loc.id) && (
                                <svg className="card-favorite-icon" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2">
                                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                                </svg>
                              )}
                            </div>
                            <p className="card-location">
                              {loc.city}, {loc.state}
                              {loc.distance_miles && (
                                <span className="card-distance"> • {loc.distance_miles} mi</span>
                              )}
                            </p>
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
                      <p>{showFavoritesOnly ? 'No favorites saved yet' : 'No locations found'}</p>
                      <span>{showFavoritesOnly ? 'Click the heart icon on any location to save it' : 'Try adjusting your filters'}</span>
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

      {/* Suggestion Modal */}
      {showSuggestionModal && (
        <div className="suggestion-modal-overlay" onClick={closeSuggestionModal} data-testid="suggestion-modal">
          <div className="suggestion-modal" onClick={e => e.stopPropagation()}>
            <div className="suggestion-modal-header">
              <h3>{suggestionType === 'new' ? 'Suggest a New Location' : 'Suggest an Edit'}</h3>
              <button className="suggestion-close-btn" onClick={closeSuggestionModal}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            {suggestionSuccess ? (
              <div className="suggestion-success">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
                <h4>Thank You!</h4>
                <p>Your suggestion has been submitted. We'll review it soon.</p>
                <button className="btn-primary" onClick={closeSuggestionModal}>Close</button>
              </div>
            ) : (
              <form onSubmit={submitSuggestion} className="suggestion-form">
                {suggestionError && (
                  <div className="suggestion-error">{suggestionError}</div>
                )}

                <div className="suggestion-form-section">
                  <h4>Your Information</h4>
                  <div className="suggestion-form-row">
                    <div className="suggestion-form-group">
                      <label>Your Name</label>
                      <input
                        type="text"
                        name="user_name"
                        value={suggestionForm.user_name}
                        onChange={handleSuggestionChange}
                        placeholder="John Smith"
                      />
                    </div>
                    <div className="suggestion-form-group">
                      <label>Email *</label>
                      <input
                        type="email"
                        name="user_email"
                        value={suggestionForm.user_email}
                        onChange={handleSuggestionChange}
                        required
                        placeholder="john@example.com"
                      />
                    </div>
                  </div>
                </div>

                <div className="suggestion-form-section">
                  <h4>Location Details</h4>
                  <div className="suggestion-form-group">
                    <label>Parish/Chapel Name *</label>
                    <input
                      type="text"
                      name="name"
                      value={suggestionForm.name}
                      onChange={handleSuggestionChange}
                      required
                      placeholder="St. Mary's Church"
                    />
                  </div>

                  <div className="suggestion-form-row">
                    <div className="suggestion-form-group">
                      <label>Affiliation *</label>
                      <select name="affiliation" value={suggestionForm.affiliation} onChange={handleSuggestionChange}>
                        <option value="Diocesan">Diocesan</option>
                        <option value="FSSP">FSSP</option>
                        <option value="ICKSP">ICKSP</option>
                        <option value="SSPX">SSPX</option>
                        <option value="Ordinariate">Ordinariate</option>
                        <option value="Eastern Catholic">Eastern Catholic</option>
                      </select>
                    </div>
                    <div className="suggestion-form-group">
                      <label>Rite</label>
                      <select name="rite" value={suggestionForm.rite} onChange={handleSuggestionChange}>
                        <option value="Latin">Latin</option>
                        <option value="Byzantine">Byzantine</option>
                        <option value="Ukrainian">Ukrainian</option>
                        <option value="Maronite">Maronite</option>
                        <option value="Melkite">Melkite</option>
                        <option value="Chaldean">Chaldean</option>
                      </select>
                    </div>
                  </div>

                  <div className="suggestion-form-group">
                    <label>Street Address</label>
                    <input
                      type="text"
                      name="street"
                      value={suggestionForm.street}
                      onChange={handleSuggestionChange}
                      placeholder="123 Main Street"
                    />
                  </div>

                  <div className="suggestion-form-row">
                    <div className="suggestion-form-group">
                      <label>City *</label>
                      <input
                        type="text"
                        name="city"
                        value={suggestionForm.city}
                        onChange={handleSuggestionChange}
                        required
                        placeholder="City"
                      />
                    </div>
                    <div className="suggestion-form-group">
                      <label>State *</label>
                      <input
                        type="text"
                        name="state"
                        value={suggestionForm.state}
                        onChange={handleSuggestionChange}
                        required
                        placeholder="CA"
                      />
                    </div>
                  </div>
                </div>

                <div className="suggestion-form-section">
                  <h4>Mass Information</h4>
                  <div className="suggestion-form-group">
                    <label>Mass Times</label>
                    <textarea
                      name="mass_schedule"
                      value={suggestionForm.mass_schedule}
                      onChange={handleSuggestionChange}
                      rows="2"
                      placeholder="Sunday: 10 AM High Mass, 12 PM Low Mass"
                    />
                  </div>

                  <div className="suggestion-form-row">
                    <div className="suggestion-form-group">
                      <label>Website</label>
                      <input
                        type="url"
                        name="website_url"
                        value={suggestionForm.website_url}
                        onChange={handleSuggestionChange}
                        placeholder="https://..."
                      />
                    </div>
                    <div className="suggestion-form-group">
                      <label>Phone</label>
                      <input
                        type="tel"
                        name="phone"
                        value={suggestionForm.phone}
                        onChange={handleSuggestionChange}
                        placeholder="(555) 123-4567"
                      />
                    </div>
                  </div>

                  <div className="suggestion-form-group">
                    <label>Additional Notes</label>
                    <textarea
                      name="notes"
                      value={suggestionForm.notes}
                      onChange={handleSuggestionChange}
                      rows="2"
                      placeholder="Any other helpful information..."
                    />
                  </div>
                </div>

                <div className="suggestion-form-section">
                  <div className="suggestion-form-group">
                    <label>{suggestionType === 'new' ? 'Why should this location be added?' : 'What needs to be changed?'}</label>
                    <textarea
                      name="reason"
                      value={suggestionForm.reason}
                      onChange={handleSuggestionChange}
                      rows="2"
                      placeholder={suggestionType === 'new' ? 'e.g., Recently opened Latin Mass community...' : 'e.g., Address is incorrect, new Mass times...'}
                    />
                  </div>
                </div>

                {/* Honeypot field - hidden from users */}
                <input
                  type="text"
                  name="honeypot"
                  value={suggestionForm.honeypot}
                  onChange={handleSuggestionChange}
                  style={{ display: 'none' }}
                  tabIndex="-1"
                  autoComplete="off"
                />

                <div className="suggestion-form-actions">
                  <button type="button" className="btn-secondary" onClick={closeSuggestionModal}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" disabled={suggestionSubmitting}>
                    {suggestionSubmitting ? 'Submitting...' : 'Submit Suggestion'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Quick Report Issue Modal */}
      {showReportModal && reportLocation && (
        <div className="report-modal-overlay" onClick={closeReportModal} data-testid="report-modal">
          <div className="report-modal" onClick={e => e.stopPropagation()}>
            <div className="report-modal-header">
              <h3>Report an Issue</h3>
              <button className="report-close-btn" onClick={closeReportModal}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="report-location-info">
              <strong>{reportLocation.name}</strong>
              <span>{reportLocation.city}, {reportLocation.state}</span>
            </div>

            {reportSuccess ? (
              <div className="report-success">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
                <h4>Thank You!</h4>
                <p>We've received your report and will review it soon.</p>
                <button className="btn-primary" onClick={closeReportModal}>Close</button>
              </div>
            ) : (
              <form onSubmit={submitReport} className="report-form">
                {reportError && (
                  <div className="report-error">{reportError}</div>
                )}

                <div className="report-form-group">
                  <label>What's the issue? *</label>
                  <select 
                    name="issue_type" 
                    value={reportForm.issue_type} 
                    onChange={handleReportChange}
                    required
                  >
                    <option value="incorrect_info">Incorrect Information</option>
                    <option value="wrong_address">Wrong Address</option>
                    <option value="wrong_times">Wrong Mass Times</option>
                    <option value="closed">Location Closed/No Longer Exists</option>
                    <option value="other">Other Issue</option>
                  </select>
                </div>

                <div className="report-form-group">
                  <label>Please describe the issue *</label>
                  <textarea
                    name="description"
                    value={reportForm.description}
                    onChange={handleReportChange}
                    required
                    rows="3"
                    placeholder="What information is incorrect? What should it be changed to?"
                  />
                </div>

                <div className="report-form-group">
                  <label>Your Email (optional)</label>
                  <input
                    type="email"
                    name="user_email"
                    value={reportForm.user_email}
                    onChange={handleReportChange}
                    placeholder="In case we need to follow up"
                  />
                </div>

                <div className="report-form-actions">
                  <button type="button" className="btn-secondary" onClick={closeReportModal}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" disabled={reportSubmitting}>
                    {reportSubmitting ? 'Submitting...' : 'Submit Report'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MassMap;
