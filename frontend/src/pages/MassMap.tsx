import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MassMap.css';

// Fix Leaflet default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Types
interface MassLocation {
  id: string;
  location_id: string;
  name: string;
  entity_type: string;
  jurisdiction: string;
  affiliation: string;
  rite: string;
  use_or_liturgy: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  latitude: number;
  longitude: number;
  mass_schedule_url?: string;
  confession_url?: string;
  adoration_url?: string;
  livestream_url?: string;
  website_url?: string;
  phone?: string;
  notes?: string;
  distance_miles?: number;
}

interface FilterOptions {
  affiliations: string[];
  rites: string[];
  liturgies: string[];
  states: string[];
}

interface Stats {
  total: number;
  by_affiliation: Record<string, number>;
  by_rite: Record<string, number>;
}

// Affiliation colors for markers
const AFFILIATION_COLORS: Record<string, string> = {
  'Diocesan': '#2563eb',       // Blue
  'FSSP': '#059669',           // Green
  'ICKSP': '#7c3aed',          // Purple
  'Ordinariate': '#dc2626',    // Red
  'SSPX': '#d97706',           // Amber
  'Eastern Catholic': '#0891b2' // Cyan
};

// US States for filter
const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
  'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
  'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

// Create custom marker icons
const createMarkerIcon = (color: string, isSelected: boolean = false) => {
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

// Map controller component for flying to location
const MapController = ({ center, zoom }: { center: [number, number]; zoom: number }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1 });
  }, [center, zoom, map]);
  return null;
};

const MassMap = () => {
  const [locations, setLocations] = useState<MassLocation[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<MassLocation | null>(null);
  const [filters, setFilters] = useState<FilterOptions | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Filter state
  const [activeAffiliation, setActiveAffiliation] = useState<string>('');
  const [activeRite, setActiveRite] = useState<string>('');
  const [activeState, setActiveState] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchInput, setSearchInput] = useState<string>('');
  
  // Map state
  const [mapCenter, setMapCenter] = useState<[number, number]>([39.8283, -98.5795]); // Center of US
  const [mapZoom, setMapZoom] = useState(4);
  
  // Mobile panel state
  const [showMobileList, setShowMobileList] = useState(false);
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchFilters();
    fetchStats();
    fetchLocations();
  }, []);

  // Fetch locations when filters change
  useEffect(() => {
    fetchLocations();
  }, [activeAffiliation, activeRite, activeState, searchQuery]);

  const fetchFilters = async () => {
    try {
      const response = await fetch('/api/mass-locations/filters');
      if (response.ok) {
        const data = await response.json();
        setFilters(data);
      }
    } catch (error) {
      console.error('Error fetching filters:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/mass-locations/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchLocations = async () => {
    try {
      setLoading(true);
      let url = '/api/mass-locations?';
      const params = new URLSearchParams();
      
      if (activeAffiliation) params.append('affiliation', activeAffiliation);
      if (activeRite) params.append('rite', activeRite);
      if (activeState) params.append('state', activeState);
      if (searchQuery) {
        url = '/api/mass-locations/search?';
        params.append('q', searchQuery);
      }
      
      const response = await fetch(url + params.toString());
      if (response.ok) {
        const data = await response.json();
        setLocations(data);
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = useCallback((e: React.FormEvent) => {
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
    setMapCenter([39.8283, -98.5795]);
    setMapZoom(4);
  };

  const selectLocation = (location: MassLocation) => {
    setSelectedLocation(location);
    setMapCenter([location.latitude, location.longitude]);
    setMapZoom(13);
    setShowMobileList(false);
  };

  const getMarkerColor = (affiliation: string) => {
    return AFFILIATION_COLORS[affiliation] || '#6b7280';
  };

  // Get unique states from locations
  const _availableStates = useMemo(() => {
    const states = new Set(locations.map(loc => loc.state));
    return US_STATES.filter(state => states.has(state));
  }, [locations]);
  void _availableStates; // Suppress unused variable warning

  // Filter counts
  const filterCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    locations.forEach(loc => {
      counts[loc.affiliation] = (counts[loc.affiliation] || 0) + 1;
      counts[loc.rite] = (counts[loc.rite] || 0) + 1;
      counts[loc.state] = (counts[loc.state] || 0) + 1;
    });
    return counts;
  }, [locations]);

  return (
    <div className="mass-map-page">
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
          {/* Search Bar */}
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
              />
              {searchInput && (
                <button 
                  type="button" 
                  className="clear-search" 
                  onClick={() => { setSearchInput(''); setSearchQuery(''); }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
            <button type="submit" className="search-btn">Search</button>
          </form>

          {/* Mobile Filter Toggle */}
          <button 
            className="mobile-filter-toggle"
            onClick={() => setShowMobileFilters(!showMobileFilters)}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            Filters
            {(activeAffiliation || activeRite || activeState) && (
              <span className="filter-badge">
                {[activeAffiliation, activeRite, activeState].filter(Boolean).length}
              </span>
            )}
          </button>

          {/* Filter Chips */}
          <div className={`filter-section ${showMobileFilters ? 'show-mobile' : ''}`}>
            {/* Affiliation Filter */}
            <div className="filter-group">
              <span className="filter-label">Affiliation:</span>
              <div className="filter-chips">
                <button
                  className={`filter-chip ${!activeAffiliation ? 'filter-chip-active' : ''}`}
                  onClick={() => setActiveAffiliation('')}
                >
                  All
                </button>
                {filters?.affiliations.map((aff) => (
                  <button
                    key={aff}
                    className={`filter-chip ${activeAffiliation === aff ? 'filter-chip-active' : ''}`}
                    onClick={() => setActiveAffiliation(aff)}
                    style={{
                      '--chip-color': getMarkerColor(aff)
                    } as React.CSSProperties}
                  >
                    <span 
                      className="chip-dot" 
                      style={{ backgroundColor: getMarkerColor(aff) }}
                    />
                    {aff}
                    {stats?.by_affiliation[aff] && (
                      <span className="chip-count">({stats.by_affiliation[aff]})</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Rite Filter */}
            <div className="filter-group">
              <span className="filter-label">Rite:</span>
              <div className="filter-chips">
                <button
                  className={`filter-chip ${!activeRite ? 'filter-chip-active' : ''}`}
                  onClick={() => setActiveRite('')}
                >
                  All Rites
                </button>
                {filters?.rites.map((rite) => (
                  <button
                    key={rite}
                    className={`filter-chip ${activeRite === rite ? 'filter-chip-active' : ''}`}
                    onClick={() => setActiveRite(rite)}
                  >
                    {rite}
                  </button>
                ))}
              </div>
            </div>

            {/* State Filter */}
            <div className="filter-group">
              <span className="filter-label">State:</span>
              <select 
                className="state-select"
                value={activeState}
                onChange={(e) => setActiveState(e.target.value)}
              >
                <option value="">All States</option>
                {US_STATES.map(state => (
                  <option key={state} value={state}>
                    {state} {filterCounts[state] ? `(${filterCounts[state]})` : ''}
                  </option>
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
            {/* Interactive Leaflet Map */}
            <div className="map-container">
              <MapContainer
                center={mapCenter}
                zoom={mapZoom}
                className="leaflet-map"
                scrollWheelZoom={true}
                zoomControl={true}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapController center={mapCenter} zoom={mapZoom} />
                
                {locations.map((loc) => (
                  <Marker
                    key={loc.id}
                    position={[loc.latitude, loc.longitude]}
                    icon={createMarkerIcon(getMarkerColor(loc.affiliation), selectedLocation?.id === loc.id)}
                    eventHandlers={{
                      click: () => selectLocation(loc),
                    }}
                  >
                    <Popup>
                      <div className="marker-popup">
                        <h4>{loc.name}</h4>
                        <p className="popup-location">{loc.city}, {loc.state}</p>
                        <p className="popup-affiliation" style={{ color: getMarkerColor(loc.affiliation) }}>
                          {loc.affiliation} • {loc.rite}
                        </p>
                        {loc.notes && <p className="popup-notes">{loc.notes}</p>}
                        <button 
                          className="popup-details-btn"
                          onClick={() => selectLocation(loc)}
                        >
                          View Details →
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>

              {/* Location Count Badge */}
              <div className="map-stats-badge">
                <span className="stats-count">{locations.length}</span>
                <span className="stats-label">locations</span>
              </div>

              {/* Legend */}
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

              {/* Zoom Controls Info */}
              <div className="zoom-info">
                <span>Use scroll or +/- to zoom</span>
              </div>
            </div>

            {/* Mobile List Toggle */}
            <button 
              className="mobile-list-toggle"
              onClick={() => setShowMobileList(!showMobileList)}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="8" y1="6" x2="21" y2="6" />
                <line x1="8" y1="12" x2="21" y2="12" />
                <line x1="8" y1="18" x2="21" y2="18" />
                <line x1="3" y1="6" x2="3.01" y2="6" />
                <line x1="3" y1="12" x2="3.01" y2="12" />
                <line x1="3" y1="18" x2="3.01" y2="18" />
              </svg>
              {showMobileList ? 'Hide List' : 'Show List'} ({locations.length})
            </button>

            {/* Location List / Detail Panel */}
            <div className={`locations-panel ${showMobileList ? 'show-mobile' : ''}`}>
              {selectedLocation ? (
                // Detail View
                <div className="location-detail">
                  <button 
                    className="back-to-list" 
                    onClick={() => setSelectedLocation(null)}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M19 12H5M12 19l-7-7 7-7" />
                    </svg>
                    Back to List
                  </button>

                  <div className="detail-header">
                    <span 
                      className="detail-badge" 
                      style={{ backgroundColor: getMarkerColor(selectedLocation.affiliation) }}
                    >
                      {selectedLocation.affiliation}
                    </span>
                    <h2 className="detail-name">{selectedLocation.name}</h2>
                    <p className="detail-type">
                      {selectedLocation.entity_type} • {selectedLocation.rite} Rite
                    </p>
                  </div>

                  <div className="detail-info">
                    <div className="info-row">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                        <circle cx="12" cy="10" r="3" />
                      </svg>
                      <div>
                        <p className="info-primary">{selectedLocation.street || 'Address not available'}</p>
                        <p className="info-secondary">
                          {selectedLocation.city}, {selectedLocation.state} {selectedLocation.zip_code}
                        </p>
                      </div>
                    </div>

                    <div className="info-row">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5z" />
                        <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
                      </svg>
                      <div>
                        <p className="info-primary">{selectedLocation.use_or_liturgy}</p>
                        <p className="info-secondary">{selectedLocation.jurisdiction}</p>
                      </div>
                    </div>

                    {selectedLocation.phone && (
                      <div className="info-row">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                        </svg>
                        <a href={`tel:${selectedLocation.phone}`} className="info-link">
                          {selectedLocation.phone}
                        </a>
                      </div>
                    )}

                    {selectedLocation.notes && (
                      <div className="info-row info-notes">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                          <line x1="9" y1="4" x2="9" y2="10" />
                        </svg>
                        <div>
                          <p className="info-label">Mass Schedule Notes</p>
                          <p className="info-note">{selectedLocation.notes}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="detail-actions">
                    {selectedLocation.website_url && (
                      <a 
                        href={selectedLocation.website_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="action-btn action-primary"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <line x1="2" y1="12" x2="22" y2="12" />
                          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                        </svg>
                        Parish Website
                      </a>
                    )}
                    {selectedLocation.mass_schedule_url && (
                      <a 
                        href={selectedLocation.mass_schedule_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="action-btn"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                        Mass Schedule
                      </a>
                    )}
                    <a 
                      href={`https://www.google.com/maps/dir/?api=1&destination=${selectedLocation.latitude},${selectedLocation.longitude}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="action-btn"
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polygon points="3 11 22 2 13 21 11 13 3 11" />
                      </svg>
                      Get Directions
                    </a>
                  </div>
                </div>
              ) : (
                // List View
                <div className="locations-list">
                  <div className="list-header">
                    <h3>Locations</h3>
                    <span className="list-count">{locations.length} found</span>
                  </div>
                  
                  {loading ? (
                    <div className="loading-state">
                      <div className="spinner" />
                      <span>Loading locations...</span>
                    </div>
                  ) : locations.length > 0 ? (
                    <div className="list-scroll">
                      {locations.map((loc) => (
                        <button
                          key={loc.id}
                          className="location-card"
                          onClick={() => selectLocation(loc)}
                        >
                          <div 
                            className="card-indicator" 
                            style={{ backgroundColor: getMarkerColor(loc.affiliation) }} 
                          />
                          <div className="card-content">
                            <h4 className="card-name">{loc.name}</h4>
                            <p className="card-location">
                              {loc.city}, {loc.state}
                            </p>
                            <div className="card-tags">
                              <span className="card-tag">{loc.affiliation}</span>
                              <span className="card-tag">{loc.rite}</span>
                            </div>
                            {loc.notes && (
                              <p className="card-schedule">{loc.notes.substring(0, 60)}...</p>
                            )}
                          </div>
                          <svg className="card-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M9 18l6-6-6-6" />
                          </svg>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                        <circle cx="12" cy="10" r="3" />
                      </svg>
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

      {/* Statistics */}
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
                  <span 
                    className="stat-number" 
                    style={{ color: getMarkerColor(name) }}
                  >
                    {count}
                  </span>
                  <span className="stat-label">{name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Disclaimer */}
      <section className="map-disclaimer">
        <div className="container container-narrow">
          <div className="disclaimer-box">
            <h4>About This Directory</h4>
            <p>
              This map is a curated directory of reverent Catholic Mass locations in the United States. 
              It includes Diocesan Traditional Latin Mass communities (1962 Roman Missal), parishes of 
              the FSSP and ICKSP, Ordinariate of the Chair of Saint Peter communities, SSPX chapels, 
              and all Eastern Catholic parishes in full communion with Rome.
            </p>
            <p>
              This directory does not include sedevacantist groups. All listings are reviewed for 
              Catholic sacramental validity and communion with the Church.
            </p>
            <p>
              Some locations listed, such as those of the Society of Saint Pius X (SSPX), exist in a 
              canonically irregular situation. While irregular, their Masses are valid and may fulfill 
              the Sunday obligation under specific conditions.
            </p>
            <p className="disclaimer-link">
              <Link to="/sspx-explained" className="sspx-info-link">
                Read more about SSPX Masses and the Sunday Obligation →
              </Link>
            </p>
            <p className="disclaimer-contact">
              To suggest a location or report an error, please contact us through our social media channels.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default MassMap;
