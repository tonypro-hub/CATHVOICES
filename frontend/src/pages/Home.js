import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';
import SEO from '../components/SEO';
import './Home.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const [featuredContent, setFeaturedContent] = useState([]);
  const [todaysSaint, setTodaysSaint] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContent();
    fetchTodaysSaint();
  }, []);

  const fetchContent = async () => {
    try {
      const response = await axios.get(`${API}/content`);
      setFeaturedContent(response.data.slice(0, 6));
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTodaysSaint = async () => {
    try {
      const response = await axios.get(`${API}/saints/today`);
      setTodaysSaint(response.data);
    } catch (error) {
      console.error('Error fetching today\'s saint:', error);
    }
  };

  const formatSaintDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  };

  return (
    <div className="home" data-testid="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background">
          <div className="hero-gradient"></div>
        </div>
        <div className="container hero-container">
          <div className="hero-content">
            <span className="hero-label">Welcome to</span>
            <h1 className="hero-title">
              <span className="hero-title-line">Catholic</span>
              <span className="hero-title-line">Voices & Prayers</span>
            </h1>
            <p className="hero-subtitle">
              A digital home for traditional Catholic prayer, devotion, and spiritual formation — 
              guided by the wisdom of the Church and the voices of faithful Catholics.
            </p>
            <div className="hero-actions">
              <Link to="/prayers" className="btn-primary" data-testid="hero-prayers-btn">
                Begin Praying
              </Link>
              <Link to="/mass-map" className="btn-outline-white" data-testid="hero-mass-btn">
                Find a Mass
              </Link>
            </div>
          </div>
        </div>
        
        {/* Scrolling Feature Ribbon */}
        <div className="feature-ribbon">
          <div className="ribbon-track">
            {['Traditional Prayers', 'Daily Devotions', 'Mass Directory', 'Saints & Feasts', 'Prayer Videos', 'The Rosary'].map((item, i) => (
              <div className="ribbon-item" key={i}>
                <span className="ribbon-icon">✝️</span>
                <span>{item}</span>
              </div>
            ))}
            {['Traditional Prayers', 'Daily Devotions', 'Mass Directory', 'Saints & Feasts', 'Prayer Videos', 'The Rosary'].map((item, i) => (
              <div className="ribbon-item" key={`dup-${i}`}>
                <span className="ribbon-icon">✝️</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="section about-section">
        <div className="container container-narrow">
          <div className="about-content">
            <span className="section-label">Our Mission</span>
            <h2 className="about-title">A Digital Home for Catholics Everywhere</h2>
            <p className="about-text">
              Catholic Voices & Prayers was born out of a deep love for Sacred Tradition. 
              We created a space where the faithful can discover traditional prayers, 
              connect with reverent liturgies, and grow in their spiritual life — 
              free from the distractions of the modern world.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Saint of the Day */}
      {todaysSaint && todaysSaint.videoId && (
        <section className="section saint-spotlight-section" data-testid="saint-spotlight">
          <div className="container">
            <div className="saint-spotlight">
              <div className="saint-spotlight-content">
                <span className="section-label">Saint of the Day</span>
                <h2 className="saint-spotlight-name">{todaysSaint.saintName}</h2>
                <p className="saint-spotlight-date">{formatSaintDate(todaysSaint.feastDate)}</p>
                <p className="saint-spotlight-description">
                  {todaysSaint.description?.split('\n')[0].slice(0, 200)}
                  {todaysSaint.description?.length > 200 ? '...' : ''}
                </p>
                <div className="saint-spotlight-actions">
                  <Link to="/daily-saint" className="btn-primary" data-testid="watch-saint-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                      <polygon points="10 8 16 12 10 16 10 8"/>
                    </svg>
                    Watch Today's Saint
                  </Link>
                  <Link to="/saints-archive" className="btn-secondary">
                    View All Saints
                  </Link>
                </div>
              </div>
              <div className="saint-spotlight-media">
                <Link to="/daily-saint" className="saint-spotlight-thumbnail">
                  <img src={todaysSaint.thumbnail} alt={todaysSaint.saintName} />
                  <div className="saint-play-overlay">
                    <div className="play-button">
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="10 8 16 12 10 16 10 8"/>
                      </svg>
                    </div>
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Feature Cards Grid */}
      <section className="section section-cream features-section">
        <div className="container">
          <div className="section-header">
            <span className="section-label">Explore</span>
            <h2 className="section-title">Discover What We Offer</h2>
          </div>
          
          <div className="features-grid">
            <Link to="/prayers" className="feature-card feature-card-large" data-testid="feature-prayers">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
              <h3 className="feature-title">Prayers & Devotions</h3>
              <p className="feature-description">
                Experience the beauty of traditional Catholic prayers. From the Holy Rosary to ancient litanies, 
                find prayers for every occasion.
              </p>
              <span className="feature-link">
                Explore Prayers
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>

            <Link to="/mass-map" className="feature-card" data-testid="feature-mass">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <h3 className="feature-title">Reverent Mass Map</h3>
              <p className="feature-description">
                Find Traditional Latin Mass, Eastern Catholic, and reverent Novus Ordo liturgies near you.
              </p>
              <span className="feature-link">
                Find a Mass
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>

            <Link to="/daily-saint" className="feature-card" data-testid="feature-saints">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M12 2v2"/>
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
                </svg>
              </div>
              <h3 className="feature-title">Saints & Feast Days</h3>
              <p className="feature-description">
                Discover the lives of holy men and women who have gone before us marked with the sign of faith.
              </p>
              <span className="feature-link">
                Explore Saints
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>

            <Link to="/store" className="feature-card" data-testid="feature-store">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <rect x="3" y="8" width="18" height="13" rx="1"/>
                  <path d="M12 8v13M3 12h18"/>
                </svg>
              </div>
              <h3 className="feature-title">Catholic Store</h3>
              <p className="feature-description">
                Carefully selected items to support your prayer life and spiritual journey.
              </p>
              <span className="feature-link">
                Browse Store
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* Mass Map Highlight Section */}
      <section className="section section-dark mass-highlight">
        <div className="container">
          <div className="mass-highlight-grid">
            <div className="mass-highlight-content">
              <span className="section-label">Featured</span>
              <h2 className="mass-highlight-title">Reverent Catholic Mass Map</h2>
              <p className="mass-highlight-text">
                Our comprehensive directory helps you find Traditional Latin Mass (TLM), 
                Eastern Catholic Divine Liturgies, Anglican Ordinariate communities, 
                and reverent Novus Ordo parishes across the United States.
              </p>
              <ul className="mass-highlight-list">
                <li>FSSP, ICKSP, Diocesan TLM locations</li>
                <li>Byzantine, Maronite, and other Eastern Rites</li>
                <li>Anglican Ordinariate communities</li>
                <li>Verified locations nationwide</li>
              </ul>
              <div className="mass-highlight-actions">
                <Link to="/mass-map" className="btn-white">
                  Explore the Map
                </Link>
                <Link to="/sspx-explained" className="btn-outline-white">
                  Learn About SSPX
                </Link>
              </div>
            </div>
            <div className="mass-highlight-image">
              <div className="map-preview">
                <svg viewBox="0 0 100 60" className="map-icon">
                  <rect x="5" y="5" width="90" height="50" rx="4" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" strokeWidth="1"/>
                  <circle cx="30" cy="25" r="4" fill="var(--color-accent-primary)"/>
                  <circle cx="50" cy="35" r="4" fill="var(--color-accent-primary)"/>
                  <circle cx="70" cy="20" r="4" fill="var(--color-accent-primary)"/>
                  <circle cx="45" cy="18" r="3" fill="var(--color-accent-gold)"/>
                  <circle cx="65" cy="40" r="3" fill="var(--color-accent-gold)"/>
                </svg>
                <span className="map-preview-text">Interactive Map</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Prayer Content Grid */}
      {featuredContent.length > 0 && (
        <section className="section content-section">
          <div className="container">
            <div className="section-header">
              <span className="section-label">Prayer Content</span>
              <h2 className="section-title">Featured Prayers & Devotions</h2>
              <p className="section-subtitle">
                Guided prayers and devotional content to deepen your spiritual life
              </p>
            </div>
            
            <div className="content-grid">
              {featuredContent.map((item) => (
                <Link 
                  key={item.videoId} 
                  to={`/prayers/${item.videoId}`} 
                  className="content-card"
                >
                  <div className="content-card-image">
                    <img src={item.thumbnail} alt={item.title} />
                    <div className="content-card-overlay">
                      <div className="play-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                          <polygon points="10 8 16 12 10 16 10 8"/>
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div className="content-card-body">
                    <span className="content-card-category">{item.category}</span>
                    <h3 className="content-card-title">{item.title}</h3>
                  </div>
                </Link>
              ))}
            </div>
            
            <div className="section-footer">
              <Link to="/prayers" className="btn-secondary">
                View All Prayers
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Scripture Quote Section */}
      <section className="section-lg scripture-section">
        <div className="container container-narrow">
          <blockquote className="scripture-quote">
            <div className="scripture-mark">“</div>
            <p className="scripture-text">Pray without ceasing.</p>
            <cite className="scripture-cite">— 1 Thessalonians 5:17</cite>
          </blockquote>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-lg cta-section" data-testid="cta-section">
        <div className="container container-narrow">
          <div className="cta-content">
            <h2 className="cta-title">Begin Your Prayer Journey</h2>
            <p className="cta-text">
              Whether you seek the comfort of the Rosary, the power of novenas, 
              or the beauty of traditional prayers — you will find a home here.
            </p>
            <div className="cta-actions">
              <Link to="/prayers" className="btn-primary">Explore Prayers</Link>
              <Link to="/about" className="btn-secondary">Learn More</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
