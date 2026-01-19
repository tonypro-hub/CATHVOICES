import { Link } from 'react-router-dom';
import './SaintsFeasts.css';

const SaintsFeasts = () => {
  return (
    <div className="saints-feasts-page">
      <div className="container">
        {/* Hero Section */}
        <div className="page-hero">
          <h1 className="page-title">Saints & Feasts</h1>
          <p className="page-subtitle">
            Discover the lives of the saints and the rich tapestry of the liturgical calendar
          </p>
        </div>

        {/* Navigation Cards */}
        <div className="section-cards">
          <Link to="/saints-feasts/saints" className="section-card">
            <div className="card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="8" r="4" />
                <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" />
                <path d="M12 2v2" />
                <path d="M9 4l3-2 3 2" />
              </svg>
            </div>
            <h2 className="card-title">Saints Index</h2>
            <p className="card-description">
              Browse our collection of saints, learn about their lives, and find prayers 
              dedicated to their intercession.
            </p>
            <span className="card-link">
              Explore Saints
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          </Link>

          <Link to="/saints-feasts/calendar" className="section-card">
            <div className="card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <line x1="3" y1="10" x2="21" y2="10" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <path d="M12 14v4" />
                <path d="M10 16h4" />
              </svg>
            </div>
            <h2 className="card-title">Feast Day Calendar</h2>
            <p className="card-description">
              Navigate the liturgical year with our comprehensive feast day calendar, 
              honoring the mysteries of our faith.
            </p>
            <span className="card-link">
              View Calendar
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          </Link>
        </div>

        {/* Coming Soon Notice */}
        <div className="coming-soon-notice">
          <div className="notice-icon">✝</div>
          <p className="notice-text">
            We are continually expanding our collection of saints and feast day resources. 
            Check back often for new content.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SaintsFeasts;
