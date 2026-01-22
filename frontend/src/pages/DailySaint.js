import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import SEO from '../components/SEO';
import './DailySaint.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DailySaint = () => {
  const { id } = useParams();
  const [saint, setSaint] = useState(null);
  const [playlistSaints, setPlaylistSaints] = useState([]);
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchSaintById(id);
    } else {
      fetchTodaysSaint();
    }
    fetchPlaylistSaints();
  }, [id]);

  const fetchTodaysSaint = async () => {
    try {
      const response = await axios.get(`${API}/saints/today`);
      setSaint(response.data);
    } catch (err) {
      console.error('Error fetching today\'s saint:', err);
      setError('Unable to load today\'s saint. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSaintById = async (saintId) => {
    try {
      const response = await axios.get(`${API}/saints/${saintId}`);
      setSaint(response.data);
    } catch (err) {
      console.error('Error fetching saint:', err);
      setError('Unable to load this saint. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPlaylistSaints = async () => {
    try {
      const response = await axios.get(`${API}/saints/playlist?limit=6`);
      setPlaylistSaints(response.data.saints || []);
      setPlaylistUrl(response.data.playlistUrl || '');
    } catch (err) {
      console.error('Error fetching playlist saints:', err);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Filter out current saint from playlist
  const previousSaints = playlistSaints.filter(s => s.videoId !== saint?.videoId).slice(0, 6);

  if (loading) {
    return (
      <div className="saints-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading today's saint...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="saints-page">
        <div className="error-container">
          <h2>Unable to Load</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="saints-page" data-testid="daily-saint-page">
      <SEO 
        title={saint?.saintName ? `${saint.saintName} - Saint of the Day` : 'Saint of the Day'}
        description={saint?.description || `Learn about today's saint and watch the daily video on the life of ${saint?.saintName || 'the saint'}.`}
        keywords={`${saint?.saintName || 'saint'}, saint of the day, Catholic saints, daily saints, lives of the saints`}
        image={saint?.thumbnail}
        type="article"
      />

      {/* Hero Section */}
      <section className="saints-hero">
        <div className="container">
          <h1 className="saints-title">Saint of the Day</h1>
          <p className="saints-subtitle">
            Daily reflections on the lives of the saints
          </p>
        </div>
      </section>

      {/* Today's Saint - Featured */}
      <section className="saints-featured">
        <div className="container">
          <div className="featured-saint-card">
            <div className="featured-video-container">
              {saint?.videoId ? (
                <iframe
                  src={`https://www.youtube.com/embed/${saint.videoId}`}
                  title={saint.saintName}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="featured-video"
                  data-testid="saint-video"
                />
              ) : (
                <div className="featured-placeholder">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <circle cx="12" cy="8" r="4"/>
                    <path d="M12 2v2"/>
                    <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
                  </svg>
                  <p>Today's saint video will be available shortly.</p>
                </div>
              )}
            </div>
            
            <div className="featured-info">
              <span className="featured-label">Today's Saint</span>
              <h2 className="featured-name" data-testid="saint-name">{saint?.saintName}</h2>
              <p className="featured-date">{formatDate(saint?.feastDate)}</p>
              
              {saint?.description && (
                <p className="featured-description">{saint.description}</p>
              )}

              <div className="featured-actions">
                {saint?.youtubeUrl && (
                  <a 
                    href={saint.youtubeUrl} 
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
                )}
                <a 
                  href="https://www.youtube.com/@CatholicVoicesPrayers?sub_confirmation=1" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="btn-subscribe"
                >
                  Subscribe to Channel
                </a>
              </div>

              {/* Social Sharing */}
              <div className="featured-share">
                <span className="share-label">Share:</span>
                <div className="share-buttons">
                  <a 
                    href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="share-btn"
                    aria-label="Share on Facebook"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </a>
                  <a 
                    href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`Today's Saint: ${saint?.saintName || 'Saint of the Day'}`)}&url=${encodeURIComponent(window.location.href)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="share-btn"
                    aria-label="Share on X/Twitter"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                  </a>
                  <button 
                    onClick={() => {
                      if (navigator.share) {
                        navigator.share({
                          title: `Saint of the Day: ${saint?.saintName}`,
                          url: window.location.href
                        });
                      } else {
                        navigator.clipboard.writeText(window.location.href);
                        alert('Link copied to clipboard!');
                      }
                    }}
                    className="share-btn"
                    aria-label="Copy link"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Previous Saints from Playlist */}
      {previousSaints.length > 0 && (
        <section className="saints-previous">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">Lives of the Saints</h2>
              <a 
                href={playlistUrl || "https://www.youtube.com/playlist?list=PLSFbA-IaB3xprRODsXjEiXMV6QF9iGXol"} 
                target="_blank"
                rel="noopener noreferrer"
                className="view-all-btn" 
                data-testid="saints-playlist-link"
              >
                View All 268 Saints
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </a>
            </div>
            
            <div className="saints-grid">
              {previousSaints.map(prevSaint => (
                <a 
                  href={prevSaint.youtubeUrl || `https://www.youtube.com/watch?v=${prevSaint.videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  key={prevSaint.videoId}
                  className="saint-card"
                  data-testid={`saint-card-${prevSaint.videoId}`}
                >
                  <div className="saint-thumbnail">
                    <img 
                      src={prevSaint.thumbnail || `https://i.ytimg.com/vi/${prevSaint.videoId}/maxresdefault.jpg`} 
                      alt={prevSaint.saintName || prevSaint.title} 
                      loading="lazy" 
                    />
                    <div className="saint-overlay">
                      <div className="play-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                          <polygon points="10 8 16 12 10 16 10 8"/>
                        </svg>
                      </div>
                    </div>
                    {prevSaint.durationFormatted && (
                      <span className="saint-date-badge">{prevSaint.durationFormatted}</span>
                    )}
                  </div>
                  <div className="saint-info">
                    <h3 className="saint-name">{prevSaint.saintName || prevSaint.title}</h3>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Internal Links */}
      <section className="saints-links">
        <div className="container">
          <h3>Continue Your Journey</h3>
          <div className="links-grid">
            <Link to="/prayers" className="link-card">
              <span className="link-text">Prayers & Devotions</span>
            </Link>
            <Link to="/teachings" className="link-card">
              <span className="link-text">Catholic Teachings</span>
            </Link>
            <Link to="/mass-map" className="link-card">
              <span className="link-text">Find a Mass</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DailySaint;
