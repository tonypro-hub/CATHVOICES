import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './AdminLocations.css';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminLocations = () => {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [affiliation, setAffiliation] = useState('');
  const [deleteModal, setDeleteModal] = useState(null);
  
  // Bulk upload state
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [bulkUploading, setBulkUploading] = useState(false);
  const [bulkUploadResult, setBulkUploadResult] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const affiliations = ['SSPX', 'Diocesan', 'Eastern Catholic', 'Ordinariate', 'ICKSP', 'FSSP'];

  useEffect(() => {
    fetchLocations();
  }, [page, search, affiliation]);

  const fetchLocations = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '25',
        ...(search && { search }),
        ...(affiliation && { affiliation })
      });

      const response = await fetch(`${API}/api/admin/locations?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.status === 401) {
        logout();
        navigate('/admin/login');
        return;
      }

      const data = await response.json();
      setLocations(data.locations || []);
      setTotalPages(data.pages || 1);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`${API}/api/admin/locations/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        setDeleteModal(null);
        fetchLocations();
      }
    } catch (error) {
      console.error('Error deleting location:', error);
    }
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-header-content">
          <div className="header-left">
            <Link to="/admin/dashboard" className="back-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
            </Link>
            <h1>Manage Locations</h1>
          </div>
          <div className="admin-actions">
            <Link to="/admin/locations/new" className="admin-btn admin-btn-primary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
              Add Location
            </Link>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-container">
          {/* Filters */}
          <div className="filters-bar">
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                placeholder="Search by name, city, or state..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="search-input"
              />
              <button type="submit" className="search-btn">Search</button>
            </form>

            <select 
              value={affiliation} 
              onChange={(e) => { setAffiliation(e.target.value); setPage(1); }}
              className="filter-select"
            >
              <option value="">All Affiliations</option>
              {affiliations.map(aff => (
                <option key={aff} value={aff}>{aff}</option>
              ))}
            </select>

            <span className="results-count">{total} locations</span>
          </div>

          {/* Locations Table */}
          <div className="table-container">
            {loading ? (
              <div className="loading-state">Loading locations...</div>
            ) : (
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Location</th>
                    <th>Affiliation</th>
                    <th>Rite</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {locations.map((loc) => (
                    <tr key={loc.id}>
                      <td>
                        <div className="location-name">{loc.name}</div>
                        {loc.entity_type && (
                          <span className="entity-type">{loc.entity_type}</span>
                        )}
                      </td>
                      <td>
                        <div className="location-address">
                          {loc.city}, {loc.state}
                          {loc.country === 'Canada' && ' (Canada)'}
                        </div>
                        {loc.street && (
                          <span className="street-address">{loc.street}</span>
                        )}
                      </td>
                      <td>
                        <span className={`affiliation-badge affiliation-${loc.affiliation?.toLowerCase().replace(/\s+/g, '-')}`}>
                          {loc.affiliation}
                        </span>
                      </td>
                      <td>{loc.rite}</td>
                      <td>
                        <div className="action-btns">
                          <Link 
                            to={`/admin/locations/${loc.id}`} 
                            className="action-btn edit-btn"
                            title="Edit"
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                          </Link>
                          <button 
                            onClick={() => setDeleteModal(loc)}
                            className="action-btn delete-btn"
                            title="Delete"
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="page-btn"
              >
                Previous
              </button>
              <span className="page-info">Page {page} of {totalPages}</span>
              <button 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="page-btn"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Delete Confirmation Modal */}
      {deleteModal && (
        <div className="modal-overlay" onClick={() => setDeleteModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Delete Location</h3>
            <p>Are you sure you want to delete <strong>{deleteModal.name}</strong>?</p>
            <p className="modal-warning">This action cannot be undone.</p>
            <div className="modal-actions">
              <button onClick={() => setDeleteModal(null)} className="admin-btn admin-btn-secondary">
                Cancel
              </button>
              <button onClick={() => handleDelete(deleteModal.id)} className="admin-btn admin-btn-danger">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminLocations;
