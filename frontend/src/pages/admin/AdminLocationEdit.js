import { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './AdminLocationEdit.css';

const API = process.env.REACT_APP_BACKEND_URL;

const AdminLocationEdit = () => {
  const { id } = useParams();
  const isNew = id === 'new';
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    entity_type: 'Parish',
    affiliation: 'Diocesan',
    rite: 'Latin',
    use_or_liturgy: '',
    street: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'USA',
    latitude: '',
    longitude: '',
    mass_schedule: '',
    website_url: '',
    phone: '',
    notes: '',
    diocese_or_archdiocese: ''
  });

  const affiliations = ['SSPX', 'Diocesan', 'Eastern Catholic', 'Ordinariate', 'ICKSP', 'FSSP'];
  const entityTypes = ['Parish', 'Chapel', 'Cathedral', 'Basilica', 'Monastery', 'Shrine', 'University Chapel', 'Mission'];
  const rites = ['Latin', 'Byzantine', 'Ukrainian', 'Melkite', 'Chaldean', 'Maronite', 'Dominican', 'Carmelite'];

  useEffect(() => {
    if (!isNew) {
      fetchLocation();
    }
  }, [id]);

  const fetchLocation = async () => {
    try {
      const response = await fetch(`${API}/api/admin/locations/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.status === 401) {
        logout();
        navigate('/admin/login');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setFormData({
          name: data.name || '',
          entity_type: data.entity_type || 'Parish',
          affiliation: data.affiliation || 'Diocesan',
          rite: data.rite || 'Latin',
          use_or_liturgy: data.use_or_liturgy || '',
          street: data.street || '',
          city: data.city || '',
          state: data.state || '',
          zip_code: data.zip_code || '',
          country: data.country || 'USA',
          latitude: data.latitude || '',
          longitude: data.longitude || '',
          mass_schedule: data.mass_schedule || '',
          website_url: data.website_url || '',
          phone: data.phone || '',
          notes: data.notes || '',
          diocese_or_archdiocese: data.diocese_or_archdiocese || ''
        });
      }
    } catch (error) {
      setError('Failed to load location');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);

    try {
      const url = isNew 
        ? `${API}/api/admin/locations`
        : `${API}/api/admin/locations/${id}`;

      const response = await fetch(url, {
        method: isNew ? 'POST' : 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          latitude: parseFloat(formData.latitude) || 0,
          longitude: parseFloat(formData.longitude) || 0
        })
      });

      if (response.ok) {
        navigate('/admin/locations');
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to save location');
      }
    } catch (error) {
      setError('An error occurred while saving');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="admin-page"><div className="loading-state">Loading...</div></div>;
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-header-content">
          <div className="header-left">
            <Link to="/admin/locations" className="back-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
            </Link>
            <h1>{isNew ? 'Add Location' : 'Edit Location'}</h1>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-container">
          <form onSubmit={handleSubmit} className="edit-form">
            {error && (
              <div className="form-error">{error}</div>
            )}

            <div className="form-section">
              <h2>Basic Information</h2>
              <div className="form-grid">
                <div className="form-group form-group-full">
                  <label>Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Entity Type</label>
                  <select name="entity_type" value={formData.entity_type} onChange={handleChange}>
                    {entityTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Affiliation *</label>
                  <select name="affiliation" value={formData.affiliation} onChange={handleChange}>
                    {affiliations.map(aff => (
                      <option key={aff} value={aff}>{aff}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Rite</label>
                  <select name="rite" value={formData.rite} onChange={handleChange}>
                    {rites.map(rite => (
                      <option key={rite} value={rite}>{rite}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Use/Liturgy</label>
                  <input
                    type="text"
                    name="use_or_liturgy"
                    value={formData.use_or_liturgy}
                    onChange={handleChange}
                    placeholder="e.g., 1962 Roman Missal"
                  />
                </div>

                <div className="form-group form-group-full">
                  <label>Diocese/Archdiocese</label>
                  <input
                    type="text"
                    name="diocese_or_archdiocese"
                    value={formData.diocese_or_archdiocese}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h2>Address</h2>
              <div className="form-grid">
                <div className="form-group form-group-full">
                  <label>Street Address</label>
                  <input
                    type="text"
                    name="street"
                    value={formData.street}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>City *</label>
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>State/Province *</label>
                  <input
                    type="text"
                    name="state"
                    value={formData.state}
                    onChange={handleChange}
                    required
                    placeholder="e.g., CA, TX, ON"
                  />
                </div>

                <div className="form-group">
                  <label>Postal Code</label>
                  <input
                    type="text"
                    name="zip_code"
                    value={formData.zip_code}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Country</label>
                  <select name="country" value={formData.country} onChange={handleChange}>
                    <option value="USA">USA</option>
                    <option value="Canada">Canada</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="form-section">
              <h2>Coordinates</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label>Latitude *</label>
                  <input
                    type="number"
                    step="any"
                    name="latitude"
                    value={formData.latitude}
                    onChange={handleChange}
                    required={isNew}
                    placeholder="e.g., 40.7128"
                  />
                </div>

                <div className="form-group">
                  <label>Longitude *</label>
                  <input
                    type="number"
                    step="any"
                    name="longitude"
                    value={formData.longitude}
                    onChange={handleChange}
                    required={isNew}
                    placeholder="e.g., -74.0060"
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h2>Contact & Details</h2>
              <div className="form-grid">
                <div className="form-group form-group-full">
                  <label>Mass Schedule</label>
                  <textarea
                    name="mass_schedule"
                    value={formData.mass_schedule}
                    onChange={handleChange}
                    rows="3"
                    placeholder="e.g., Sunday 10 AM Latin High Mass"
                  />
                </div>

                <div className="form-group">
                  <label>Website URL</label>
                  <input
                    type="url"
                    name="website_url"
                    value={formData.website_url}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group form-group-full">
                  <label>Notes</label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    rows="3"
                  />
                </div>
              </div>
            </div>

            <div className="form-actions">
              <Link to="/admin/locations" className="admin-btn admin-btn-secondary">Cancel</Link>
              <button type="submit" className="admin-btn admin-btn-primary" disabled={saving}>
                {saving ? 'Saving...' : (isNew ? 'Create Location' : 'Save Changes')}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default AdminLocationEdit;
