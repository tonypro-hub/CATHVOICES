import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const RosaryPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRosary();
  }, []);

  const fetchRosary = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/rosary`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching rosary prayers:', error);
    } finally {
      setLoading(false);
    }
  };

  const mysteryOrder = [
    'Joyful Mysteries',
    'Sorrowful Mysteries', 
    'Glorious Mysteries',
    'Luminous Mysteries',
    'Scriptural Rosary',
    'Holy Rosary'
  ];

  return (
    <div className="prayers-page" data-testid="rosary-page">
      <SEO 
        title="Holy Rosary | Prayers"
        description="Pray the Holy Rosary with guided video meditations. Joyful, Sorrowful, Glorious, and Luminous Mysteries."
        keywords="Holy Rosary, Rosary prayers, Joyful Mysteries, Sorrowful Mysteries, Glorious Mysteries, Luminous Mysteries, Catholic Rosary"
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
          <h1 className="prayers-title">The Holy Rosary</h1>
          <p className="prayers-subtitle">
            Pray the sacred mysteries with guided video meditations
          </p>
        </div>
      </section>

      {/* Rosary Videos */}
      <section className="prayer-videos-section">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading rosary prayers...</span>
            </div>
          ) : data?.videos?.length > 0 ? (
            <>
              {/* Group by Mystery Type */}
              {mysteryOrder.map(mystery => {
                const mysteryVideos = data.byMystery?.[mystery] || [];
                if (mysteryVideos.length === 0) return null;
                
                return (
                  <div key={mystery} className="mystery-section">
                    <h2 className="mystery-title">{mystery}</h2>
                    <div className="videos-grid">
                      {mysteryVideos.map(video => (
                        <Link 
                          to={`/prayers/video/${video.videoId}`} 
                          key={video.videoId}
                          className="video-card"
                          data-testid={`rosary-video-${video.videoId}`}
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
                );
              })}
              
              {/* Any ungrouped videos */}
              {data.videos.filter(v => !mysteryOrder.includes(v.mysteryType)).length > 0 && (
                <div className="mystery-section">
                  <h2 className="mystery-title">More Rosary Prayers</h2>
                  <div className="videos-grid">
                    {data.videos
                      .filter(v => !mysteryOrder.includes(v.mysteryType))
                      .map(video => (
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
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="5" r="2" />
                <circle cx="12" cy="10" r="1.5" />
                <circle cx="12" cy="14" r="1.5" />
                <circle cx="12" cy="18" r="1.5" />
              </svg>
              <h3>Rosary Prayers Coming Soon</h3>
              <p>We're preparing guided Rosary meditations for you.</p>
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

export default RosaryPage;
