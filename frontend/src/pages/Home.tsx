import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="container hero-content">
          <div className="hero-text">
            <h1 className="hero-title">Welcome to Catholic Voices & Prayers</h1>
            <p className="hero-description">
              Discover a reverent collection of traditional Catholic prayers and devotions,
              beautifully presented with video guidance and full prayer texts.
            </p>
            <div className="hero-actions">
              <Link to="/prayers" className="btn btn-primary">
                Explore Prayers
              </Link>
              <Link to="/about" className="btn btn-secondary">
                Learn More
              </Link>
            </div>
          </div>
          <div className="hero-image">
            <img src="/assets/brand/logo-white.png" alt="Catholic Voices Logo" className="hero-logo" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 className="section-title">What We Offer</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 7l-7 5 7 5V7z"/>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                </svg>
              </div>
              <h3 className="feature-title">Video Guidance</h3>
              <p className="feature-description">
                Watch and listen to each prayer beautifully recited by Bishop Fulton Sheen and other Catholic voices.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
              </div>
              <h3 className="feature-title">Full Prayer Texts</h3>
              <p className="feature-description">
                Read along with large, reverent typography optimized for contemplative prayer and meditation.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </div>
              <h3 className="feature-title">Easy Sharing</h3>
              <p className="feature-description">
                Copy prayer texts to your clipboard and share them with family and friends.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta">
        <div className="container cta-content">
          <div className="cta-cross">✝</div>
          <h2 className="cta-title">Begin Your Prayer Journey</h2>
          <p className="cta-description">
            Explore our collection of traditional Catholic prayers, from the Holy Rosary to powerful novenas.
          </p>
          <Link to="/prayers" className="btn btn-primary btn-large">
            View All Prayers
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
