import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './PrayerDetail.css';

interface Prayer {
  id: string;
  title: string;
  videoId: string;
  prayerText: string;
  category: string;
}

const PrayerDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [prayer, setPrayer] = useState<Prayer | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (id) {
      fetchPrayer(id);
    }
  }, [id]);

  const fetchPrayer = async (prayerId: string) => {
    try {
      const response = await axios.get(`/api/prayers/${prayerId}`);
      setPrayer(response.data);
    } catch (error) {
      console.error('Error fetching prayer:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = () => {
    if (prayer) {
      navigator.clipboard.writeText(prayer.prayerText);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    }
  };

  if (loading) {
    return (
      <div className="prayer-page">
        <div className="prayer-container">
          <div className="loading-state">Loading prayer...</div>
        </div>
      </div>
    );
  }

  if (!prayer) {
    return (
      <div className="prayer-page">
        <div className="prayer-container">
          <div className="error-state">Prayer not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="prayer-page">
      {/* Video Section */}
      <div className="video-section">
        <div className="video-wrapper">
          <iframe
            src={`https://www.youtube.com/embed/${prayer.videoId}?rel=0&modestbranding=1`}
            title={prayer.title}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="video-iframe"
          ></iframe>
        </div>
      </div>

      {/* Prayer Content */}
      <div className="prayer-content">
        <div className="prayer-container">
          {/* Prayer Header */}
          <div className="prayer-header">
            <div className="prayer-category">{prayer.category}</div>
            <h1 className="prayer-title">{prayer.title}</h1>
          </div>

          {/* Copy Button */}
          <div className="copy-section">
            <button 
              onClick={handleCopyText} 
              className="copy-button"
              aria-label="Copy prayer text"
            >
              {copied ? (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  <span>Copy Prayer Text</span>
                </>
              )}
            </button>
          </div>

          {/* Prayer Text */}
          <div className="prayer-text-section">
            <div className="prayer-text">{prayer.prayerText}</div>
          </div>

          {/* Closing */}
          <div className="prayer-closing">
            <div className="closing-symbol">✝</div>
            <p className="closing-text">Amen</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrayerDetail;
