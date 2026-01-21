import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const NovenasPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNovenas();
  }, []);

  const fetchNovenas = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/novenas`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching novenas:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prayers-page" data-testid="novenas-page">
      <SEO 
        title="Novenas | Prayers"
        description="Nine-day prayers of devotion to saints and sacred mysteries. Pray novenas to your favorite saints."
        keywords="Catholic Novenas, Novena prayers, 9 day prayers, Saint Novenas, Marian Novenas"
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
          <h1 className="prayers-title">Novenas</h1>
          <p className="prayers-subtitle">
            Nine-day prayers of devotion to saints and sacred mysteries
          </p>
        </div>
      </section>

      {/* Novena Videos */}
      <section className="prayer-videos-section">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading novenas...</span>
            </div>
          ) : data?.novenas?.length > 0 ? (
            <>
              {data.novenas.map(novena => (
                <div key={novena.name} className="novena-section">
                  <h2 className="novena-title">{novena.name}</h2>
                  <div className="videos-grid">
                    {novena.days.map(video => (
                      <Link 
                        to={`/prayers/video/${video.videoId}`} 
                        key={video.videoId}
                        className="video-card"
                        data-testid={`novena-video-${video.videoId}`}
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
                          {video.novenaDay && (
                            <span className="video-meta">Day {video.novenaDay}</span>
                          )}
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
          ) : (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2L12 6M12 18L12 22M6 12L2 12M22 12L18 12" />
                <circle cx="12" cy="12" r="6" />
              </svg>
              <h3>Novenas Coming Soon</h3>
              <p>We're preparing nine-day devotional prayers for you.</p>
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

export default NovenasPage;
