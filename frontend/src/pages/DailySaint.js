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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id) {
      fetchSaintById(id);
    } else {
      fetchTodaysSaint();
    }
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

  if (loading) {
    return (
      <div className="daily-saint-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading today's saint...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="daily-saint-page">
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
    <div className="daily-saint-page" data-testid="daily-saint-page">
      {/* Hero Section */}
      <section className="saint-hero">
        <div className="saint-hero-background"></div>
        <div className="container saint-hero-content">
          <span className="saint-label">Saint of the Day</span>
          <h1 className="saint-hero-title" data-testid="saint-name">{saint?.saintName || 'Loading...'}</h1>
          <p className="saint-date">
            {saint?.feastDate ? formatDate(saint.feastDate) : ''}
          </p>
          {saint?.notice && (
            <div className="saint-notice">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{saint.notice}</span>
            </div>
          )}
        </div>
      </section>

      {/* Video Section */}
      <section className="section saint-video-section">
        <div className="container">
          {saint?.videoId ? (
            <div className="saint-video-container">
              <div className="saint-video-wrapper">
                <iframe
                  src={`https://www.youtube.com/embed/${saint.videoId}`}
                  title={saint.saintName}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="saint-video"
                  data-testid="saint-video"
                ></iframe>
              </div>
            </div>
          ) : (
            <div className="saint-placeholder">
              <div className="placeholder-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M12 2v2"/>
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
                </svg>
              </div>
              <p>Today's saint video will be available shortly.</p>
            </div>
          )}
        </div>
      </section>

      {/* Description Section */}
      {saint?.description && (
        <section className="section saint-description-section">
          <div className="container container-narrow">
            <div className="saint-description-card">
              <h2>About {saint.saintName}</h2>
              <p className="saint-description-text">
                {saint.description}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Actions Section */}
      <section className="section saint-actions-section">
        <div className="container">
          <div className="saint-actions">
            {saint?.youtubeUrl && (
              <a 
                href={saint.youtubeUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn-primary"
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
              className="btn-secondary"
            >
              Subscribe to Channel
            </a>
          </div>
        </div>
      </section>

      {/* Social Sharing */}
      <section className="section saint-share-section">
        <div className="container container-narrow">
          <div className="share-card">
            <h3>Share Today's Saint</h3>
            <div className="share-buttons">
              <a 
                href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="share-btn share-facebook"
                aria-label="Share on Facebook"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a 
                href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`Today's Saint: ${saint?.saintName || 'Saint of the Day'}`)}&url=${encodeURIComponent(window.location.href)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="share-btn share-twitter"
                aria-label="Share on X/Twitter"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
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
                className="share-btn share-copy"
                aria-label="Copy link"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Archive Link */}
      <section className="section saint-archive-link">
        <div className="container container-narrow">
          <Link to="/saints-archive" className="archive-cta" data-testid="saints-archive-link">
            <div className="archive-cta-content">
              <h3>View All Saints</h3>
              <p>Browse our complete archive of daily saints</p>
            </div>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default DailySaint;
