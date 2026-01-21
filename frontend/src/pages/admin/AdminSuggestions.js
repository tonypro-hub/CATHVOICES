import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './AdminSuggestions.css';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminSuggestions = () => {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchSuggestions();
  }, [statusFilter]);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ status: statusFilter, limit: '50' });
      const response = await fetch(`${API}/api/admin/suggestions?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.status === 401) {
        logout();
        navigate('/admin/login');
        return;
      }

      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id, action) => {
    setProcessing(true);
    try {
      const response = await fetch(`${API}/api/admin/suggestions/${id}?action=${action}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        fetchSuggestions();
        setSelectedSuggestion(null);
      }
    } catch (error) {
      console.error('Error processing suggestion:', error);
    } finally {
      setProcessing(false);
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
            <h1>User Suggestions</h1>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-container">
          {/* Status Tabs */}
          <div className="status-tabs">
            {['pending', 'approved', 'rejected'].map(status => (
              <button
                key={status}
                className={`status-tab ${statusFilter === status ? 'active' : ''}`}
                onClick={() => setStatusFilter(status)}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>

          {/* Suggestions List */}
          {loading ? (
            <div className="loading-state">Loading suggestions...</div>
          ) : suggestions.length === 0 ? (
            <div className="empty-state">
              <p>No {statusFilter} suggestions</p>
            </div>
          ) : (
            <div className="suggestions-list">
              {suggestions.map(suggestion => (
                <div key={suggestion.id} className="suggestion-card">
                  <div className="suggestion-header">
                    <span className={`suggestion-type type-${suggestion.suggestion_type}`}>
                      {suggestion.suggestion_type === 'new' ? 'New Location' : 'Edit Request'}
                    </span>
                    <span className="suggestion-date">{formatDate(suggestion.created_at)}</span>
                  </div>

                  <h3 className="suggestion-name">{suggestion.name || 'Unnamed Location'}</h3>
                  
                  <p className="suggestion-location">
                    {suggestion.city}, {suggestion.state} {suggestion.country}
                  </p>

                  <p className="suggestion-from">
                    From: {suggestion.user_name || 'Anonymous'} ({suggestion.user_email})
                  </p>

                  {suggestion.reason && (
                    <p className="suggestion-reason">
                      <strong>Reason:</strong> {suggestion.reason}
                    </p>
                  )}

                  <div className="suggestion-actions">
                    <button 
                      className="view-btn"
                      onClick={() => setSelectedSuggestion(suggestion)}
                    >
                      View Details
                    </button>
                    
                    {statusFilter === 'pending' && (
                      <>
                        <button 
                          className="approve-btn"
                          onClick={() => handleAction(suggestion.id, 'approve')}
                          disabled={processing}
                        >
                          Approve
                        </button>
                        <button 
                          className="reject-btn"
                          onClick={() => handleAction(suggestion.id, 'reject')}
                          disabled={processing}
                        >
                          Reject
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Detail Modal */}
      {selectedSuggestion && (
        <div className="modal-overlay" onClick={() => setSelectedSuggestion(null)}>
          <div className="modal-content modal-large" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Suggestion Details</h3>
              <button className="modal-close" onClick={() => setSelectedSuggestion(null)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Type</label>
                  <span>{selectedSuggestion.suggestion_type === 'new' ? 'New Location' : 'Edit Request'}</span>
                </div>
                <div className="detail-item">
                  <label>Status</label>
                  <span className={`status-badge status-${selectedSuggestion.status}`}>
                    {selectedSuggestion.status}
                  </span>
                </div>
                <div className="detail-item">
                  <label>Name</label>
                  <span>{selectedSuggestion.name}</span>
                </div>
                <div className="detail-item">
                  <label>Affiliation</label>
                  <span>{selectedSuggestion.affiliation || 'Not specified'}</span>
                </div>
                <div className="detail-item">
                  <label>Street</label>
                  <span>{selectedSuggestion.street || 'Not provided'}</span>
                </div>
                <div className="detail-item">
                  <label>City, State</label>
                  <span>{selectedSuggestion.city}, {selectedSuggestion.state}</span>
                </div>
                <div className="detail-item">
                  <label>Website</label>
                  <span>{selectedSuggestion.website_url || 'Not provided'}</span>
                </div>
                <div className="detail-item">
                  <label>Phone</label>
                  <span>{selectedSuggestion.phone || 'Not provided'}</span>
                </div>
                <div className="detail-item full-width">
                  <label>Mass Schedule</label>
                  <span>{selectedSuggestion.mass_schedule || 'Not provided'}</span>
                </div>
                <div className="detail-item full-width">
                  <label>Notes</label>
                  <span>{selectedSuggestion.notes || 'None'}</span>
                </div>
                <div className="detail-item full-width">
                  <label>Reason for Suggestion</label>
                  <span>{selectedSuggestion.reason || 'Not provided'}</span>
                </div>
              </div>

              <div className="submitter-info">
                <h4>Submitted By</h4>
                <p><strong>Name:</strong> {selectedSuggestion.user_name || 'Anonymous'}</p>
                <p><strong>Email:</strong> {selectedSuggestion.user_email}</p>
                <p><strong>Date:</strong> {formatDate(selectedSuggestion.created_at)}</p>
              </div>
            </div>

            {selectedSuggestion.status === 'pending' && (
              <div className="modal-footer">
                <button 
                  className="admin-btn admin-btn-secondary"
                  onClick={() => setSelectedSuggestion(null)}
                >
                  Close
                </button>
                <button 
                  className="admin-btn reject-btn"
                  onClick={() => handleAction(selectedSuggestion.id, 'reject')}
                  disabled={processing}
                >
                  Reject
                </button>
                <button 
                  className="admin-btn approve-btn"
                  onClick={() => handleAction(selectedSuggestion.id, 'approve')}
                  disabled={processing}
                >
                  Approve & Apply
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminSuggestions;
