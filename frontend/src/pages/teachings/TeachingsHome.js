import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Teachings.css';

const API = process.env.REACT_APP_BACKEND_URL;

const TeachingsHome = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeachings();
  }, []);

  const fetchTeachings = async () => {
    try {
      const response = await fetch(`${API}/api/teachings`);
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
    <div className="teachings-page" data-testid="teachings-home">
      <SEO 
        title="Catholic Teachings | Catholic Voices and Prayers"
        description="Clear answers to the Faith, rooted in Sacred Tradition. Explore Catholic doctrine, apologetics, and spiritual guidance."
        keywords="Catholic Teachings, Catholic Apologetics, Catholic Doctrine, Faith Formation, Catholic Education"
      />

      {/* Hero */}
      <section className="teachings-hero">
        <div className="container">
          <h1 className="teachings-title">Catholic Teachings</h1>
          <p className="teachings-subtitle">
            Clear answers to the Faith, rooted in Sacred Tradition.
          </p>
          {data && (
            <p className="teachings-count">{data.totalVideos} teachings available</p>
          )}
        </div>
      </section>

      {/* Categories */}
      <section className="teachings-categories">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading teachings library...</span>
            </div>
          ) : data?.categories?.length > 0 ? (
            <div className="categories-list">
              {data.categories.map(category => (
                <div key={category.id} className="category-section" data-testid={`category-${category.id}`}>
                  <div className="category-header">
                    <div className="category-info">
                      <h2 className="category-title">{category.name}</h2>
                      <p className="category-description">{category.description}</p>
                    </div>
                    <Link 
                      to={`/teachings/${category.id}`} 
                      className="view-all-btn"
                      data-testid={`view-all-${category.id}`}
                    >
                      View All ({category.count})
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                      </svg>
                    </Link>
                  </div>
                  
                  <div className="shorts-grid">
                    {category.preview.map(video => (
                      <Link 
                        to={`/teachings/video/${video.videoId}`}
                        key={video.videoId}
                        className="short-card"
                        data-testid={`video-${video.videoId}`}
                      >
                        <div className="short-thumbnail">
                          <img src={video.thumbnail} alt={video.title} loading="lazy" />
                          <div className="short-overlay">
                            <div className="play-icon">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                                <polygon points="10 8 16 12 10 16 10 8"/>
                              </svg>
                            </div>
                          </div>
                          <span className="short-duration">{video.durationFormatted}</span>
                        </div>
                        <div className="short-info">
                          <h3 className="short-title">{video.title}</h3>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
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
            </div>
          )}
        </div>
      </section>

      {/* Internal Links */}
      <section className="teachings-links">
        <div className="container">
          <h3>Continue Your Journey</h3>
          <div className="links-grid">
            <Link to="/prayers" className="link-card">
              <span className="link-icon">🙏</span>
              <span className="link-text">Prayers & Devotions</span>
            </Link>
            <Link to="/prayers/saints" className="link-card">
              <span className="link-icon">✝️</span>
              <span className="link-text">Lives of the Saints</span>
            </Link>
            <Link to="/mass-map" className="link-card">
              <span className="link-icon">⛪</span>
              <span className="link-text">Find a Mass</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default TeachingsHome;
