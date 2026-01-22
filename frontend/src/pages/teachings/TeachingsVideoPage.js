import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Teachings.css';

const API = process.env.REACT_APP_BACKEND_URL;

const TeachingsVideoPage = () => {
  const { videoId } = useParams();
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoId]);

  const fetchVideo = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/api/teachings/video/${videoId}`);
      if (response.ok) {
        const result = await response.json();
        setVideo(result);
      }
    } catch (error) {
      console.error('Error fetching video:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="teachings-page">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner" />
            <span>Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="teachings-page">
        <div className="container">
          <div className="empty-state">
            <h3>Video not found</h3>
            <Link to="/teachings" className="btn-primary">Back to Teachings</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="teachings-page teachings-video-page" data-testid={`video-page-${videoId}`}>
      <SEO 
        title={`${video.title} | Catholic Voices and Prayers`}
        description={video.description?.slice(0, 160) || 'Catholic teaching from Catholic Voices and Prayers.'}
        keywords={`Catholic Teachings, ${video.categoryName}, Catholic Apologetics`}
      />

      <div className="container">
        {/* Breadcrumb */}
        <nav className="video-breadcrumb">
          <Link to="/teachings">Teachings</Link>
          <span className="breadcrumb-sep">/</span>
          <Link to={`/teachings/${video.categoryId}`}>{video.categoryName}</Link>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">{video.title?.slice(0, 40)}...</span>
        </nav>

        <div className="video-layout">
          {/* Main Video */}
          <div className="video-main">
            <div className="video-embed-container video-embed-short">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}?rel=0`}
                title={video.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>

            <div className="video-details">
              <h1 className="video-page-title">{video.title}</h1>
              
              <div className="video-meta">
                <span className="video-category-badge">{video.categoryName}</span>
                <span className="video-duration-badge">{video.durationFormatted}</span>
              </div>

              {video.description && (
                <div className="video-description">
                  <h3>Description</h3>
                  <p>{video.description}</p>
                </div>
              )}

              <div className="video-actions">
                <a 
                  href={`https://www.youtube.com/watch?v=${videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-youtube"
                  data-testid="watch-youtube-btn"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                  Watch on YouTube
                </a>
                <a 
                  href="https://www.youtube.com/@CatholicVoicesandPrayers?sub_confirmation=1"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-subscribe"
                  data-testid="subscribe-btn"
                >
                  Subscribe to Channel
                </a>
              </div>
            </div>
          </div>

          {/* Related Videos */}
          {video.related?.length > 0 && (
            <aside className="video-sidebar">
              <h3 className="sidebar-title">More in {video.categoryName}</h3>
              <div className="related-videos">
                {video.related.map(related => (
                  <Link 
                    to={`/teachings/video/${related.videoId}`}
                    key={related.videoId}
                    className="related-card"
                    data-testid={`related-${related.videoId}`}
                  >
                    <div className="related-thumbnail">
                      <img src={related.thumbnail} alt={related.title} loading="lazy" />
                      <span className="related-duration">{related.durationFormatted}</span>
                    </div>
                    <div className="related-info">
                      <h4 className="related-title">{related.title}</h4>
                    </div>
                  </Link>
                ))}
              </div>
              
              <Link 
                to={`/teachings/${video.categoryId}`}
                className="view-all-related"
              >
                View all in {video.categoryName}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Link>
            </aside>
          )}
        </div>

        {/* Internal Links */}
        <section className="video-internal-links">
          <h3>Continue Your Journey</h3>
          <div className="links-grid">
            <Link to="/prayers" className="link-card">
              <span className="link-text">Prayers & Devotions</span>
            </Link>
            <Link to="/prayers/saints" className="link-card">
              <span className="link-text">Lives of the Saints</span>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
};

export default TeachingsVideoPage;
