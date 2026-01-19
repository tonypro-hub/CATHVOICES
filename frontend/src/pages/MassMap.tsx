import { useState, useEffect, useCallback, useRef } from 'react';
import './MassMap.css';

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

const MassMap = () => {
  const [locations, setLocations] = useState<MassLocation[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<MassLocation | null>(null);
  const [filters, setFilters] = useState<FilterOptions | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Filter state
  const [activeAffiliation, setActiveAffiliation] = useState<string>('');
  const [activeRite, setActiveRite] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchInput, setSearchInput] = useState<string>('');
  
  // Map state
  const [mapCenter, setMapCenter] = useState({ lat: 39.8283, lng: -98.5795 }); // Center of US
  const [mapZoom, setMapZoom] = useState(4);
  const mapRef = useRef<HTMLDivElement>(null);
  const [hoveredLocation, setHoveredLocation] = useState<string | null>(null);

  // Fetch initial data
  useEffect(() => {
    fetchFilters();
    fetchStats();
    fetchLocations();
  }, []);

  // Fetch locations when filters change
  useEffect(() => {
    fetchLocations();
  }, [activeAffiliation, activeRite, searchQuery]);

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
    setSearchQuery('');
    setSearchInput('');
    setSelectedLocation(null);
  };

  const selectLocation = (location: MassLocation) => {
    setSelectedLocation(location);
    setMapCenter({ lat: location.latitude, lng: location.longitude });
    setMapZoom(12);
  };

  const getMarkerColor = (affiliation: string) => {
    return AFFILIATION_COLORS[affiliation] || '#6b7280';
  };

  // Calculate marker position on map
  const getMarkerPosition = (lat: number, lng: number) => {
    // Simple equirectangular projection for US
    // Map bounds: roughly lat 25-50, lng -125 to -65
    const mapWidth = mapRef.current?.clientWidth || 800;
    const mapHeight = mapRef.current?.clientHeight || 500;
    
    const minLat = 24;
    const maxLat = 50;
    const minLng = -125;
    const maxLng = -65;
    
    const x = ((lng - minLng) / (maxLng - minLng)) * mapWidth;
    const y = ((maxLat - lat) / (maxLat - minLat)) * mapHeight;
    
    return { x, y };
  };

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
                placeholder="Search by city, state, or ZIP code..."
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

          {/* Filter Chips */}
          <div className="filter-section">
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
                  </button>
                ))}
              </div>
            </div>

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

            {(activeAffiliation || activeRite || searchQuery) && (
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
            {/* Interactive Map */}
            <div className="map-container">
              <div className="map-wrapper" ref={mapRef}>
                {/* US Map Background */}
                <div className="map-background">
                  <img 
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Map_of_USA_with_state_names.svg/1200px-Map_of_USA_with_state_names.svg.png" 
                    alt="US Map"
                    className="us-map-img"
                  />
                </div>
                
                {/* Markers */}
                <div className="markers-layer">
                  {locations.map((loc) => {
                    const pos = getMarkerPosition(loc.latitude, loc.longitude);
                    return (
                      <button
                        key={loc.id}
                        className={`map-marker ${
                          selectedLocation?.id === loc.id ? 'marker-selected' : ''
                        } ${
                          hoveredLocation === loc.id ? 'marker-hovered' : ''
                        }`}
                        style={{
                          left: `${pos.x}px`,
                          top: `${pos.y}px`,
                          backgroundColor: getMarkerColor(loc.affiliation)
                        }}
                        onClick={() => selectLocation(loc)}
                        onMouseEnter={() => setHoveredLocation(loc.id)}
                        onMouseLeave={() => setHoveredLocation(null)}
                        title={loc.name}
                      >
                        <span className="marker-pulse" />
                      </button>
                    );
                  })}
                </div>

                {/* Location Count */}
                <div className="map-stats">
                  <span className="stats-count">{locations.length}</span>
                  <span className="stats-label">locations</span>
                </div>
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
            </div>

            {/* Location List / Detail Panel */}
            <div className="locations-panel">
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
                        <p className="info-primary">{selectedLocation.street}</p>
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

                    {selectedLocation.notes && (
                      <div className="info-row">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <path d="M12 16v-4M12 8h.01" />
                        </svg>
                        <p className="info-note">{selectedLocation.notes}</p>
                      </div>
                    )}
                  </div>

                  <div className="detail-actions">
                    {selectedLocation.mass_schedule_url && (
                      <a 
                        href={selectedLocation.mass_schedule_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="action-btn action-primary"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                        Mass Schedule
                      </a>
                    )}
                    {selectedLocation.website_url && (
                      <a 
                        href={selectedLocation.website_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="action-btn"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10" />
                          <line x1="2" y1="12" x2="22" y2="12" />
                          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                        </svg>
                        Website
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
                      Directions
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
                          className={`location-card ${
                            hoveredLocation === loc.id ? 'card-hovered' : ''
                          }`}
                          onClick={() => selectLocation(loc)}
                          onMouseEnter={() => setHoveredLocation(loc.id)}
                          onMouseLeave={() => setHoveredLocation(null)}
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
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-number">{stats.total}</span>
                <span className="stat-label">Total Locations</span>
              </div>
              {Object.entries(stats.by_affiliation).map(([name, count]) => (
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
              This map is a curated directory of reverent Catholic Mass locations. It includes 
              Diocesan Traditional Latin Mass communities, FSSP, ICKSP, Ordinariate parishes, 
              SSPX chapels, and all Eastern Catholic parishes in full communion with Rome.
            </p>
            <p>
              <strong>Note:</strong> This directory does not include sedevacantist groups. 
              All listings are verified for communion with the Holy See.
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
