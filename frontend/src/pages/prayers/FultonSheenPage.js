import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const FultonSheenPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFultonSheen();
  }, []);

  const fetchFultonSheen = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/fulton-sheen`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching Fulton Sheen prayers:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prayers-page fulton-sheen-page" data-testid="fulton-sheen-page">
      <SEO 
        title="Praying with Bishop Fulton J. Sheen | Prayers"
        description="Experience the profound spiritual guidance of the Venerable Archbishop Fulton J. Sheen through guided prayers, rosaries, and reflections."
        keywords="Fulton Sheen prayers, Bishop Sheen Rosary, Archbishop Sheen, Catholic prayers, Sheen devotions"
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
          <h1 className="prayers-title">Praying with Bishop Fulton J. Sheen</h1>
          <p className="prayers-subtitle">
            Guided prayers and reflections with the Venerable Archbishop
          </p>
        </div>
      </section>

      {/* Introduction */}
      <section className="fulton-sheen-intro">
        <div className="container">
          <div className="intro-content">
            <h2>A Voice of Faith</h2>
            <p>
              Archbishop Fulton J. Sheen was one of the most influential Catholic voices of the 20th century. 
              His profound spiritual insight and gift for communication continue to guide souls toward Christ. 
              Experience the depth of his prayer life through these guided devotions.
            </p>
          </div>
        </div>
      </section>

      {/* Fulton Sheen Videos */}
      <section className="prayer-videos-section">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading prayers...</span>
            </div>
          ) : data?.videos?.length > 0 ? (
            <>
              {/* Rosaries */}
              {data.rosaries?.length > 0 && (
                <div className="mystery-section">
                  <h2 className="mystery-title">Rosaries</h2>
                  <div className="videos-grid">
                    {data.rosaries.map(video => (
                      <Link 
                        to={`/prayers/video/${video.videoId}`} 
                        key={video.videoId}
                        className="video-card"
                        data-testid={`sheen-rosary-${video.videoId}`}
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

              {/* Novenas & Devotions */}
              {data.novenas_devotions?.length > 0 && (
                <div className="mystery-section">
                  <h2 className="mystery-title">Novenas & Devotions</h2>
                  <div className="videos-grid">
                    {data.novenas_devotions.map(video => (
                      <Link 
                        to={`/prayers/video/${video.videoId}`} 
                        key={video.videoId}
                        className="video-card"
                        data-testid={`sheen-devotion-${video.videoId}`}
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

              {/* All Videos (fallback if no categorized content) */}
              {(!data.rosaries?.length && !data.novenas_devotions?.length) && (
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
              )}
            </>
          ) : (
            <div className="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              <h3>Bishop Sheen Prayers Coming Soon</h3>
              <p>We're preparing guided prayers featuring Bishop Fulton J. Sheen.</p>
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

export default FultonSheenPage;
