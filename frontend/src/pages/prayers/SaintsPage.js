import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const SaintsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSaints();
  }, []);

  const fetchSaints = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/saints`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching saints:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prayers-page" data-testid="saints-page">
      <SEO 
        title="Lives of the Saints | Catholic Voices and Prayers"
        description="Daily saint reflections and feast day celebrations. Learn about the holy men and women of our Catholic faith."
        keywords="Catholic Saints, Lives of Saints, Feast Days, Saint Biographies, Catholic Martyrs"
      />

      {/* Hero */}
      <section className="prayers-hero">
        <div className="container">
          <Link to="/prayers" className="prayers-back">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Library
          </Link>
          <h1 className="prayers-title">Lives of the Saints</h1>
          <p className="prayers-subtitle">
            Daily reflections on the holy men and women of our faith
          </p>
        </div>
      </section>

      {/* Saints Videos */}
      <section className="prayer-videos-section">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading saints...</span>
            </div>
          ) : data?.videos?.length > 0 ? (
            <div className="videos-grid">
              {data.videos.map(video => (
                <Link 
                  to={`/prayers/video/${video.videoId}`} 
                  key={video.videoId}
                  className="video-card"
                  data-testid={`saint-video-${video.videoId}`}
                >
                  <div className="video-thumbnail">
                    <img src={video.thumbnail} alt={video.title} />
                    <span className="video-duration">{video.durationFormatted}</span>
                    <div className="video-play-overlay">
                      <div className="video-play-btn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                          <polygon points="10 8 16 12 10 16 10 8"/>
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div className="video-info">
                    <h3 className="video-title">{video.title}</h3>
                    {video.isFultonSheen && (
                      <span className="video-badge">With Bishop Sheen</span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="8" r="5" />
                <path d="M12 13v8M8 17h8" />
              </svg>
              <h3>Saints Content Coming Soon</h3>
              <p>We're preparing stories of the saints for you.</p>
              <Link to="/prayers" className="btn-primary">
                Back to Library
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default SaintsPage;
