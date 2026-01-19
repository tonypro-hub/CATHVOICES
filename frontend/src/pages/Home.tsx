import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';
import './Home.css';

interface Prayer {
  id: string;
  title: string;
  videoId: string;
  category: string;
}

const Home = () => {
  const [prayers, setPrayers] = useState<Prayer[]>([]);

  useEffect(() => {
    fetchPrayers();
  }, []);

  const fetchPrayers = async () => {
    try {
      const response = await axios.get('/api/prayers');
      setPrayers(response.data);
    } catch (error) {
      console.error('Error fetching prayers:', error);
    }
  };

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container hero-container">
          <div className="hero-content">
            <h1 className="hero-title">Find God's Peace in Prayer</h1>
            <p className="hero-subtitle">
              Join millions praying with Bishop Fulton Sheen on Catholic Voices & Prayers
            </p>
            <Link to="/prayers" className="cta-button primary-cta">
              Start Praying
            </Link>
          </div>
          <div className="hero-image">
            <img src="/assets/brand/banner.jpg" alt="Catholic Prayer" className="hero-img" />
          </div>
        </div>
      </section>

      {/* Three Feature Cards */}
      <section className="features-section">
        <div className="container">
          <div className="feature-cards">
            <div className="feature-card">
              <img src="/assets/brand/logo-white.png" alt="Find Peace" className="feature-image" />
              <h3 className="feature-title">Find Peace</h3>
              <p className="feature-description">
                Let God bring you His peace with the Rosary, novenas, and traditional Catholic prayers.
              </p>
            </div>
            <div className="feature-card">
              <img src="/assets/brand/logo-white.png" alt="Transform Prayer Life" className="feature-image" />
              <h3 className="feature-title">Transform Your Prayer Life</h3>
              <p className="feature-description">
                Choose from traditional Catholic prayers with video guidance to lead you closer to Christ.
              </p>
            </div>
            <div className="feature-card">
              <img src="/assets/brand/logo-white.png" alt="Build a Habit" className="feature-image" />
              <h3 className="feature-title">Build a Habit</h3>
              <p className="feature-description">
                Build a real habit of prayer every day with beautiful videos and full prayer texts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Scripture Quote */}
      <section className="scripture-section">
        <div className="container scripture-container">
          <p className="scripture-reference">Matthew 6:6</p>
          <blockquote className="scripture-quote">
            "But when you pray, go into your room, close the door and pray to your Father, who is unseen."
          </blockquote>
        </div>
      </section>

      {/* Prayers Grid Section */}
      <section className="prayers-grid-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Traditional Catholic Prayers</h2>
            <Link to="/prayers" className="see-all-link">See All</Link>
          </div>
          <div className="horizontal-scroll">
            {prayers.map((prayer) => (
              <Link to={`/prayers/${prayer.id}`} key={prayer.id} className="prayer-card-horizontal">
                <div className="card-image-placeholder">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M23 7l-7 5 7 5V7z"/>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                  </svg>
                </div>
                <h3 className="card-title">{prayer.title}</h3>
                <p className="card-category">{prayer.category}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta-section">
        <div className="container cta-container">
          <div className="cta-icon">✝</div>
          <h2 className="cta-title">Start your prayer journey today!</h2>
          <Link to="/prayers" className="cta-button secondary-cta">
            Explore Prayers
          </Link>
        </div>
      </section>

      {/* Categories Section */}
      <section className="categories-section">
        <div className="container">
          <h2 className="section-title-center">Explore by Category</h2>
          <div className="categories-grid">
            <Link to="/prayers" className="category-card">
              <div className="category-image-placeholder burgundy-bg">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
              </div>
              <h3 className="category-title">The Rosary</h3>
              <p className="category-description">Joyful, Sorrowful & Glorious Mysteries</p>
            </Link>
            <Link to="/prayers" className="category-card">
              <div className="category-image-placeholder gold-bg">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
              <h3 className="category-title">Novenas</h3>
              <p className="category-description">Nine days of powerful prayer</p>
            </Link>
            <Link to="/prayers" className="category-card">
              <div className="category-image-placeholder cream-bg">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <h3 className="category-title">Traditional Prayers</h3>
              <p className="category-description">Our Father, Hail Mary, Glory Be</p>
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="final-cta">
        <div className="container final-cta-container">
          <p className="prayers-count">Prayers Prayed with Catholic Voices & Prayers</p>
          <Link to="/prayers" className="cta-button primary-cta large-cta">
            Begin Your Prayer Journey
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
