import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './PrayerDetail.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PrayerDetail = () => {
  const { id } = useParams();
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchContent();
  }, [id]);

  const fetchContent = async () => {
    try {
      const response = await axios.get(`${API}/content/${id}`);
      setContent(response.data);
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyPrayerText = () => {
    if (content?.prayerText) {
      navigator.clipboard.writeText(content.prayerText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <div className="prayer-detail-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading prayer...</p>
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="prayer-detail-page">
        <div className="error-container">
          <h2>Prayer Not Found</h2>
          <p>The prayer you're looking for doesn't exist.</p>
          <Link to="/prayers" className="btn-primary">Browse All Prayers</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="prayer-detail-page" data-testid="prayer-detail-page">
      {/* Hero */}
      <section className="prayer-hero">
        <div className="container">
          <Link to="/prayers" className="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            All Prayers
          </Link>
          <span className="prayer-category">{content.category}</span>
          <h1 className="prayer-title">{content.title}</h1>
        </div>
      </section>

      {/* Video */}
      <section className="section prayer-video-section">
        <div className="container">
          <div className="video-container">
            <iframe
              src={`https://www.youtube.com/embed/${content.videoId}`}
              title={content.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="prayer-video"
              data-testid="prayer-video"
            ></iframe>
          </div>
        </div>
      </section>

      {/* Prayer Text */}
      {content.prayerText && (
        <section className="section prayer-text-section">
          <div className="container container-narrow">
            <div className="prayer-text-card">
              <div className="prayer-text-header">
                <h2>Prayer Text</h2>
                <button 
                  className="copy-btn" 
                  onClick={copyPrayerText}
                  data-testid="copy-prayer-btn"
                >
                  {copied ? (
                    <>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      Copied!
                    </>
                  ) : (
                    <>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                      </svg>
                      Copy Prayer
                    </>
                  )}
                </button>
              </div>
              <div className="prayer-text-content">
                {content.prayerText}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Actions */}
      <section className="section prayer-actions-section">
        <div className="container">
          <div className="prayer-actions">
            <a 
              href={`https://www.youtube.com/watch?v=${content.videoId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
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
              className="btn-secondary"
            >
              Subscribe
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PrayerDetail;
