import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Daily.css';

interface Short {
  videoId: string;
  title: string;
  thumbnailUrl: string;
  thumbnail: string;
  publishedAt: string;
  category: string;
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
      {/* Hero */}
      <section className="daily-hero">
        <div className="container">
          <span className="daily-date">{formattedDate}</span>
          <h1 className="daily-title">Daily Devotions</h1>
          <p className="daily-subtitle">
            Brief moments of prayer and reflection to carry with you throughout the day
          </p>
        </div>
      </section>

      {/* Quick Links */}
      <section className="section daily-links">
        <div className="container">
          <div className="links-grid">
            <Link to="/daily/saint" className="link-card">
              <div className="link-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" />
                </svg>
              </div>
              <div className="link-content">
                <h3>Today's Saint</h3>
                <p>Learn about the saint celebrated today</p>
              </div>
              <svg className="link-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 18l6-6-6-6" />
              </svg>
            </Link>

            <Link to="/daily/feast" className="link-card">
              <div className="link-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="3" y="4" width="18" height="18" rx="2" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                  <path d="M12 14v4" />
                  <path d="M10 16h4" />
                </svg>
              </div>
              <div className="link-content">
                <h3>Today's Feast</h3>
                <p>Explore today's liturgical celebration</p>
              </div>
              <svg className="link-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 18l6-6-6-6" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Reflections Grid */}
      <section className="section reflections">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Daily Reflections</h2>
          </div>

          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <span>Loading reflections...</span>
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
                  <div className="short-media">
                    <img
                      src={short.thumbnail || short.thumbnailUrl}
                      alt={short.title}
                    />
                    <div className="short-play">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="10 8 16 12 10 16 10 8" />
                      </svg>
                    </div>
                  </div>
                  <div className="short-info">
                    <h3>{short.title}</h3>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>Daily reflections coming soon</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Daily;
