import { Link } from 'react-router-dom';
import './About.css';

const About = () => {
  return (
    <div className="about-page" data-testid="about-page">
      {/* Hero */}
      <section className="about-hero">
        <div className="container">
          <h1 className="about-title">About Catholic Voices & Prayers</h1>
          <p className="about-subtitle">
            A digital sanctuary for the faithful, dedicated to preserving and sharing 
            the richness of Catholic tradition
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section about-mission">
        <div className="container container-narrow">
          <div className="mission-content">
            <span className="section-label">Our Mission</span>
            <h2>Bringing Catholics Closer to Christ</h2>
            <p>
              Catholic Voices & Prayers exists to serve Catholics worldwide by providing free access 
              to traditional prayers, devotions, and spiritual resources. In a world of endless 
              distraction, we offer a place of peace and reverence.
            </p>
            <p>
              Founded by a small group of faithful Catholics, our mission is simple: to help souls 
              grow in holiness through the time-tested prayers and traditions of the Church. We believe 
              that the ancient liturgy and traditional devotions speak to the heart in a way that 
              transcends time.
            </p>
          </div>
        </div>
      </section>

      {/* What We Offer */}
      <section className="section about-offerings">
        <div className="container">
          <div className="section-header">
            <span className="section-label">What We Offer</span>
            <h2 className="section-title">Resources for Your Faith Journey</h2>
          </div>
          
          <div className="offerings-grid">
            <div className="offering-card">
              <div className="offering-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <polygon points="10 8 16 12 10 16 10 8"/>
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                </svg>
              </div>
              <h3>Prayer Videos</h3>
              <p>
                Guided prayers and devotions on YouTube, including the Holy Rosary, 
                Chaplets, Litanies, and Novenas.
              </p>
            </div>
            
            <div className="offering-card">
              <div className="offering-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M12 2v2"/>
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
                </svg>
              </div>
              <h3>Daily Saints</h3>
              <p>
                Learn about the lives of the saints each day through our "Daily Lives of the Saints" 
                YouTube Shorts series.
              </p>
            </div>
            
            <div className="offering-card">
              <div className="offering-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <h3>Mass Map</h3>
              <p>
                Find reverent Catholic Masses near you, including Traditional Latin Mass, 
                Eastern Catholic, and Ordinariate communities.
              </p>
            </div>
            
            <div className="offering-card">
              <div className="offering-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <h3>Prayer Texts</h3>
              <p>
                Traditional prayer texts to accompany our videos, so you can pray along 
                or use for personal devotion.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="section section-cream about-values">
        <div className="container container-narrow">
          <div className="section-header">
            <span className="section-label">Our Values</span>
            <h2 className="section-title">What Guides Us</h2>
          </div>
          
          <div className="values-list">
            <div className="value-item">
              <div className="value-number">01</div>
              <div className="value-content">
                <h3>Sacred Tradition</h3>
                <p>
                  We honor the timeless traditions of the Catholic Church, believing that 
                  what nourished souls for centuries continues to have power today.
                </p>
              </div>
            </div>
            
            <div className="value-item">
              <div className="value-number">02</div>
              <div className="value-content">
                <h3>Reverence</h3>
                <p>
                  Everything we create is made with reverence for God and respect for 
                  the sacred nature of prayer and worship.
                </p>
              </div>
            </div>
            
            <div className="value-item">
              <div className="value-number">03</div>
              <div className="value-content">
                <h3>Accessibility</h3>
                <p>
                  We believe spiritual resources should be freely available to all. 
                  Our content is free and always will be.
                </p>
              </div>
            </div>
            
            <div className="value-item">
              <div className="value-number">04</div>
              <div className="value-content">
                <h3>Unity</h3>
                <p>
                  We serve Catholics of all liturgical preferences who share a love 
                  for reverent worship and authentic Catholic tradition.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* YouTube */}
      <section className="section about-youtube">
        <div className="container">
          <div className="youtube-card">
            <div className="youtube-content">
              <svg className="youtube-logo" width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              <h2>Join Our Community on YouTube</h2>
              <p>
                Subscribe to Catholic Voices & Prayers for daily prayers, saint stories, 
                and devotional content to enrich your spiritual life.
              </p>
              <a 
                href="https://www.youtube.com/@CatholicVoicesPrayers?sub_confirmation=1" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="btn-primary youtube-btn"
              >
                Subscribe on YouTube
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-lg about-cta" data-testid="about-cta">
        <div className="container container-narrow">
          <div className="cta-content">
            <h2>Begin Your Prayer Journey</h2>
            <p>
              Explore our library of traditional prayers and devotions, 
              or find a reverent Mass near you.
            </p>
            <div className="cta-buttons">
              <Link to="/prayers" className="btn-primary">Explore Prayers</Link>
              <Link to="/mass-map" className="btn-secondary">Find a Mass</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
