import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './PrayerVideo.css';

const API = process.env.REACT_APP_BACKEND_URL;

const PrayerVideoPage = () => {
  const { videoId } = useParams();
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVideo();
  }, [videoId]);

  const fetchVideo = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library/video/${videoId}`);
      if (response.ok) {
        const data = await response.json();
        setVideo(data);
      }
    } catch (error) {
      console.error('Error fetching prayer video:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLink = (category) => {
    const links = {
      'rosary': '/prayers/rosary',
      'novenas': '/prayers/novenas',
      'devotions': '/prayers/devotions',
      'fulton-sheen': '/prayers/fulton-sheen'
    };
    return links[category] || '/prayers';
  };

  const getCategoryName = (category) => {
    const names = {
      'rosary': 'Rosaries',
      'novenas': 'Novenas',
      'devotions': 'Devotions',
      'fulton-sheen': 'Bishop Sheen'
    };
    return names[category] || 'Prayers';
  };

  if (loading) {
    return (
      <div className="prayer-video-page">
        <div className="loading-container">
          <div className="loading-spinner" />
          <span>Loading prayer...</span>
        </div>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="prayer-video-page">
        <div className="container">
          <div className="error-state">
            <h2>Prayer Not Found</h2>
            <p>The prayer you're looking for doesn't exist.</p>
            <Link to="/prayers" className="btn-primary">Browse All Prayers</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="prayer-video-page" data-testid="prayer-video-page">
      <SEO 
        title={`${video.title} | Catholic Voices and Prayers`}
        description={video.description?.substring(0, 160) || `Pray along with ${video.title}`}
        keywords={`${video.title}, Catholic prayer, ${video.category}`}
      />

      {/* Hero */}
      <section className="video-hero">
        <div className="container">
          <div className="video-breadcrumb">
            <Link to="/prayers">Prayers</Link>
            <span>/</span>
            <Link to={getCategoryLink(video.category)}>{getCategoryName(video.category)}</Link>
          </div>
          <h1 className="video-page-title">{video.title}</h1>
          {video.isFultonSheen && (
            <span className="sheen-badge">With Bishop Fulton J. Sheen</span>
          )}
        </div>
      </section>

      {/* Video Player */}
      <section className="video-player-section">
        <div className="container">
          <div className="video-container">
            <iframe
              src={`https://www.youtube.com/embed/${video.videoId}?rel=0`}
              title={video.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="video-iframe"
              data-testid="prayer-video-player"
            />
          </div>
        </div>
      </section>

      {/* Video Info & Actions */}
      <section className="video-info-section">
        <div className="container">
          <div className="video-details">
            <div className="video-description">
              {video.description && (
                <>
                  <h3>About This Prayer</h3>
                  <p>{video.description}</p>
                </>
              )}
            </div>

            <div className="video-actions">
              <h3>Join in Prayer</h3>
              <div className="actions-grid">
                <a 
                  href={`https://www.youtube.com/watch?v=${video.videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="action-btn action-youtube"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                  </svg>
                  Watch on YouTube
                </a>
                <a 
                  href="https://www.youtube.com/@CatholicVoicesPrayers?sub_confirmation=1"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="action-btn action-subscribe"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                  </svg>
                  Subscribe for Daily Prayers
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Related Prayers */}
      {video.related?.length > 0 && (
        <section className="related-prayers-section">
          <div className="container">
            <h3 className="related-title">Continue Praying</h3>
            <div className="related-grid">
              {video.related.map(related => (
                <Link 
                  to={`/prayers/video/${related.videoId}`} 
                  key={related.videoId}
                  className="related-card"
                >
                  <div className="related-thumbnail">
                    <img src={related.thumbnail} alt={related.title} />
                    <span className="related-duration">{related.durationFormatted}</span>
                  </div>
                  <div className="related-info">
                    <h4>{related.title}</h4>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default PrayerVideoPage;
