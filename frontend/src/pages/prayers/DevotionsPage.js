import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const DevotionsPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDevotions();
  }, []);

  const fetchDevotions = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/devotions`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching devotions:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prayers-page" data-testid="devotions-page">
      <SEO 
        title="Prayers & Devotions"
        description="Traditional Catholic prayers including Divine Mercy Chaplet, Litanies, Stations of the Cross, and daily prayers."
        keywords="Catholic devotions, Divine Mercy Chaplet, Litany, Stations of the Cross, Morning prayers, Evening prayers, Angelus"
      />

      {/* Hero */}
      <section className="prayers-hero">
        <div className="container">
          <Link to="/prayers" className="prayers-back">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Prayers
          </Link>
          <h1 className="prayers-title">Prayers & Devotions</h1>
          <p className="prayers-subtitle">
            Chaplets, litanies, and traditional Catholic prayers
          </p>
        </div>
      </section>

      {/* Devotion Videos */}
      <section className="prayer-videos-section">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading devotions...</span>
            </div>
          ) : data?.devotions?.length > 0 ? (
            <>
              {data.devotions.map(devotion => (
                <div key={devotion.name} className="devotion-section">
                  <h2 className="devotion-title">{devotion.name}</h2>
                  <div className="videos-grid">
                    {devotion.videos.map(video => (
                      <Link 
                        to={`/prayers/video/${video.videoId}`} 
                        key={video.videoId}
                        className="video-card"
                        data-testid={`devotion-video-${video.videoId}`}
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
                </div>
              ))}
            </>
          ) : data?.videos?.length > 0 ? (
            <div className="videos-grid">
              {data.videos.map(video => (
                <Link 
                  to={`/prayers/video/${video.videoId}`} 
                  key={video.videoId}
                  className="video-card"
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
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
                <path d="M12 6v6l4 2" />
              </svg>
              <h3>Devotions Coming Soon</h3>
              <p>We're preparing traditional prayers and devotions for you.</p>
              <Link to="/prayers" className="btn-primary">
                Back to Prayers
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default DevotionsPage;
