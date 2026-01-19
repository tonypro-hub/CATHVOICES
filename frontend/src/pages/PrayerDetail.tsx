import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import './PrayerDetail.css';

interface ContentItem {
  id: string;
  videoId: string;
  title: string;
  description: string;
  category: string;
  prayerText: string | null;
  hasPrayerText: boolean;
}

const PrayerDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [content, setContent] = useState<ContentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (id) {
      fetchContent(id);
    }
  }, [id]);

  const fetchContent = async (videoId: string) => {
    try {
      const response = await axios.get(`/api/content/${videoId}`);
      setContent(response.data);
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = () => {
    if (content && content.prayerText) {
      navigator.clipboard.writeText(content.prayerText);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    }
  };

  if (loading) {
    return (
      <div className="detail-page">
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="detail-page">
        <div className="container">
          <div className="error-state">
            <h2>Content not found</h2>
            <Link to="/prayers" className="btn-primary">Back to Prayers</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="detail-page">
      {/* Breadcrumb */}
      <nav className="breadcrumb">
        <div className="container">
          <Link to="/" className="breadcrumb-link">Home</Link>
          <span className="breadcrumb-separator">/</span>
          <Link to="/prayers" className="breadcrumb-link">Prayers</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">{content.category}</span>
        </div>
      </nav>

      {/* Video Section */}
      <section className="video-section">
        <div className="video-container">
          <div className="video-wrapper">
            <iframe
              src={`https://www.youtube.com/embed/${content.videoId}?rel=0&modestbranding=1`}
              title={content.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="content-section">
        <div className="content-container">
          {/* Header */}
          <header className="detail-header">
            <span className="detail-category">{content.category}</span>
            <h1 className="detail-title">{content.title}</h1>
          </header>

          {/* Description */}
          {content.description && (
            <div className="detail-description">
              <p>{content.description}</p>
            </div>
          )}

          {/* Prayer Text */}
          {content.hasPrayerText && content.prayerText && (
            <div className="prayer-text-container">
              {/* Divider */}
              <hr className="divider" />
              
              {/* Copy Button */}
              <div className="copy-row">
                <h2 className="prayer-text-heading">Prayer Text</h2>
                <button 
                  onClick={handleCopyText} 
                  className="copy-btn"
                  aria-label="Copy prayer text"
                >
                  {copied ? (
                    <>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      Copied
                    </>
                  ) : (
                    <>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                      </svg>
                      Copy Text
                    </>
                  )}
                </button>
              </div>

              {/* Prayer Text */}
              <div className="prayer-text prose">
                {content.prayerText}
              </div>

              {/* Closing */}
              <div className="prayer-closing">
                <span className="closing-amen">Amen.</span>
              </div>
            </div>
          )}

          {/* Back Link */}
          <div className="back-section">
            <Link to="/prayers" className="back-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              Back to All Prayers
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PrayerDetail;
