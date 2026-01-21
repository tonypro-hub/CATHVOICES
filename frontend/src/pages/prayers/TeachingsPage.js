import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const TeachingsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeachings();
  }, []);

  const fetchTeachings = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/teachings`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching teachings:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prayers-page" data-testid="teachings-page">
      <SEO 
        title="Catholic Teachings | Catholic Voices and Prayers"
        description="Faith formation, doctrine, and spiritual guidance. Learn more about the teachings of the Catholic Church."
        keywords="Catholic Teachings, Faith Formation, Catholic Doctrine, Spiritual Guidance, Catholic Education"
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
          <h1 className="prayers-title">Catholic Teachings</h1>
          <p className="prayers-subtitle">
            Faith formation, doctrine, and spiritual guidance
          </p>
        </div>
      </section>

      {/* Teachings Videos */}
      <section className="prayer-videos-section">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading teachings...</span>
            </div>
          ) : data?.videos?.length > 0 ? (
            <div className="videos-grid">
              {data.videos.map(video => (
                <Link 
                  to={`/prayers/video/${video.videoId}`} 
                  key={video.videoId}
                  className="video-card"
                  data-testid={`teaching-video-${video.videoId}`}
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
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
              <h3>Teachings Coming Soon</h3>
              <p>We're preparing Catholic teachings for you.</p>
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

export default TeachingsPage;
