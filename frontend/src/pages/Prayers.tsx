import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Prayers.css';

interface Prayer {
  id: string;
  title: string;
  videoId: string;
  category: string;
}

const Prayers = () => {
  const [prayers, setPrayers] = useState<Prayer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrayers();
  }, []);

  const fetchPrayers = async () => {
    try {
      const response = await axios.get('/api/prayers');
      setPrayers(response.data);
    } catch (error) {
      console.error('Error fetching prayers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="prayers-page">
        <div className="container">
          <div className="loading">Loading prayers...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="prayers-page">
      <div className="container">
        <div className="prayers-header">
          <h1 className="prayers-title">Traditional Catholic Prayers</h1>
          <p className="prayers-subtitle">Select a prayer to watch the video and read along</p>
        </div>

        <div className="prayers-grid">
          {prayers.map((prayer) => (
            <Link to={`/prayers/${prayer.id}`} key={prayer.id} className="prayer-card">
              <div className="prayer-card-header">
                <div className="prayer-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M23 7l-7 5 7 5V7z"/>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                  </svg>
                </div>
                <span className="prayer-category">{prayer.category}</span>
              </div>
              <h3 className="prayer-card-title">{prayer.title}</h3>
              <div className="prayer-card-arrow">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Prayers;
