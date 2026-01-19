import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Daily.css';

interface Short {
  videoId: string;
  title: string;
  thumbnailUrl: string;
  publishedAt: string;
}

const Daily = () => {
  const [shorts, setShorts] = useState<Short[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchShorts();
  }, []);

  const fetchShorts = async () => {
    try {
      const response = await fetch('/api/shorts?limit=12');
      if (response.ok) {
        const data = await response.json();
        setShorts(data);
      }
    } catch (error) {
      console.error('Error fetching shorts:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get today's date formatted
  const today = new Date();
  const dateOptions: Intl.DateTimeFormatOptions = { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  };
  const formattedDate = today.toLocaleDateString('en-US', dateOptions);

  return (
    <div className="daily-page">
      <div className="container">
        {/* Hero Section */}
        <div className="daily-hero">
          <p className="daily-date">{formattedDate}</p>
          <h1 className="daily-title">Daily Devotions</h1>
          <p className="daily-subtitle">
            Start each day with faith through today's saint, feast, and reflections
          </p>
        </div>

        {/* Quick Links */}
        <div className="daily-quick-links">
          <Link to="/daily/saint" className="quick-link-card">
            <div className="quick-link-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="8" r="4" />
                <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" />
                <circle cx="12" cy="5" r="1" fill="currentColor" />
              </svg>
            </div>
            <div className="quick-link-content">
              <h3>Today's Saint</h3>
              <p>Learn about the saint celebrated today</p>
            </div>
            <svg className="quick-link-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </Link>

          <Link to="/daily/feast" className="quick-link-card">
            <div className="quick-link-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <line x1="3" y1="10" x2="21" y2="10" />
                <path d="M12 14v4" />
                <path d="M10 16h4" />
              </svg>
            </div>
            <div className="quick-link-content">
              <h3>Today's Feast</h3>
              <p>Explore today's liturgical celebration</p>
            </div>
            <svg className="quick-link-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </Link>
        </div>

        {/* Daily Reflections (Shorts) */}
        <section className="daily-reflections">
          <h2 className="section-title">Daily Reflections</h2>
          <p className="section-description">
            Short moments of prayer and reflection to carry with you throughout the day
          </p>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading reflections...</p>
            </div>
          ) : shorts.length > 0 ? (
            <div className="shorts-grid">
              {shorts.map((short) => (
                <a
                  key={short.videoId}
                  href={`https://www.youtube.com/shorts/${short.videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="short-card"
                >
                  <div className="short-thumbnail-container">
                    <img
                      src={short.thumbnailUrl}
                      alt={short.title}
                      className="short-thumbnail"
                    />
                    <div className="short-play-icon">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                    <div className="short-duration">SHORT</div>
                  </div>
                  <h3 className="short-title">{short.title}</h3>
                </a>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">✝</div>
              <p>Daily reflections coming soon</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Daily;
