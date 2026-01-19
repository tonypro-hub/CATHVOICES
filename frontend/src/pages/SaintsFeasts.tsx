import { Link } from 'react-router-dom';
import './SaintsFeasts.css';

const SaintsFeasts = () => {
  return (
    <div className="saints-page">
      {/* Hero */}
      <section className="saints-hero">
        <div className="container">
          <h1 className="saints-title">Saints & Feast Days</h1>
          <p className="saints-subtitle">
            Discover the lives of holy men and women and the rich tapestry of the liturgical calendar
          </p>
        </div>
      </section>

      {/* Navigation Cards */}
      <section className="section saints-nav">
        <div className="container">
          <div className="nav-cards">
            <Link to="/saints-feasts/saints" className="nav-card">
              <div className="nav-card-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" />
                  <path d="M12 2v2" />
                </svg>
              </div>
              <h2 className="nav-card-title">Saints Index</h2>
              <p className="nav-card-desc">
                Browse our collection of saints, learn about their lives, and find prayers 
                dedicated to their intercession.
              </p>
              <span className="nav-card-link">
                Explore Saints
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </span>
            </Link>

            <Link to="/saints-feasts/calendar" className="nav-card">
              <div className="nav-card-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="3" y="4" width="18" height="18" rx="2" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                </svg>
              </div>
              <h2 className="nav-card-title">Feast Day Calendar</h2>
              <p className="nav-card-desc">
                Navigate the liturgical year with our comprehensive feast day calendar, 
                honoring the mysteries of our faith.
              </p>
              <span className="nav-card-link">
                View Calendar
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* Coming Soon */}
      <section className="section-sm coming-soon">
        <div className="container container-narrow">
          <div className="coming-soon-card">
            <p>
              We are continually expanding our collection of saints and feast day resources. 
              Check back often for new content.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SaintsFeasts;
