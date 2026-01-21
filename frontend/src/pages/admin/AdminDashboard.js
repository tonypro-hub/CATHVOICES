import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './AdminDashboard.css';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [pendingSuggestions, setPendingSuggestions] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch location stats
      const statsRes = await fetch(`${API}/api/mass-locations/stats`);
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }

      // Fetch pending suggestions count
      const suggestionsRes = await fetch(`${API}/api/admin/suggestions?status=pending&limit=1`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (suggestionsRes.ok) {
        const data = await suggestionsRes.json();
        setPendingSuggestions(data.total);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-header-content">
          <h1>Admin Dashboard</h1>
          <div className="admin-actions">
            <Link to="/" className="admin-btn admin-btn-secondary">View Site</Link>
            <button onClick={handleLogout} className="admin-btn admin-btn-outline">Logout</button>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-container">
          {/* Quick Stats */}
          <section className="dashboard-stats">
            <div className="stat-card">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
              </div>
              <div className="stat-content">
                <span className="stat-value">{stats?.total || 0}</span>
                <span className="stat-label">Total Locations</span>
              </div>
            </div>

            <div className="stat-card stat-card-warning">
              <div className="stat-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" />
                </svg>
              </div>
              <div className="stat-content">
                <span className="stat-value">{pendingSuggestions}</span>
                <span className="stat-label">Pending Suggestions</span>
              </div>
            </div>

            {stats?.by_affiliation && Object.entries(stats.by_affiliation).slice(0, 4).map(([key, value]) => (
              <div className="stat-card stat-card-small" key={key}>
                <span className="stat-value-small">{value}</span>
                <span className="stat-label-small">{key}</span>
              </div>
            ))}
          </section>

          {/* Quick Actions */}
          <section className="dashboard-actions">
            <h2>Quick Actions</h2>
            <div className="action-cards">
              <Link to="/admin/locations" className="action-card">
                <div className="action-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                </div>
                <h3>Manage Locations</h3>
                <p>View, edit, and add mass locations</p>
              </Link>

              <Link to="/admin/suggestions" className="action-card">
                <div className="action-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <h3>Review Suggestions</h3>
                <p>{pendingSuggestions > 0 ? `${pendingSuggestions} pending` : 'No pending suggestions'}</p>
                {pendingSuggestions > 0 && <span className="action-badge">{pendingSuggestions}</span>}
              </Link>

              <Link to="/admin/locations/new" className="action-card">
                <div className="action-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 8v8M8 12h8" />
                  </svg>
                </div>
                <h3>Add Location</h3>
                <p>Create a new mass location</p>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
