import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Prayers.css';

const API = process.env.REACT_APP_BACKEND_URL;

const PrayersHome = () => {
  const [library, setLibrary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLibrary();
  }, []);

  const fetchLibrary = async () => {
    try {
      const response = await fetch(`${API}/api/prayer-library`);
      if (response.ok) {
        const data = await response.json();
        setLibrary(data);
      }
    } catch (error) {
      console.error('Error fetching prayer library:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryConfig = {
    'fulton-sheen': {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      ),
      link: '/prayers/fulton-sheen',
      color: 'fulton-sheen'
    },
    saints: {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="8" r="5" />
          <path d="M12 13v8M8 17h8" />
          <path d="M7 3l2 2M17 3l-2 2" />
        </svg>
      ),
      link: '/prayers/saints',
      color: 'saints'
    },
    teachings: {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
        </svg>
      ),
      link: '/teachings',
      color: 'teachings'
    },
    rosary: {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="5" r="2" />
          <circle cx="12" cy="10" r="1.5" />
          <circle cx="12" cy="14" r="1.5" />
          <circle cx="12" cy="18" r="1.5" />
          <path d="M12 7v11" />
        </svg>
      ),
      link: '/prayers/rosary',
      color: 'rosary'
    },
    novenas: {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2L12 6M12 18L12 22M6 12L2 12M22 12L18 12" />
          <circle cx="12" cy="12" r="6" />
          <path d="M12 9v3l2 2" />
        </svg>
      ),
      link: '/prayers/novenas',
      color: 'novenas'
    },
    devotions: {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
          <path d="M12 6v6l4 2" />
        </svg>
      ),
      link: '/prayers/devotions',
      color: 'devotions'
    }
  };

  return (
    <div className="prayers-page" data-testid="prayers-home">
      <SEO 
        title="Prayers"
        description="Timeless Catholic prayers, guided by sacred tradition. Rosaries, Novenas, and devotions featuring Bishop Fulton J. Sheen."
        keywords="Catholic prayers, Rosary, Novenas, Divine Mercy, Fulton Sheen, traditional prayers, Catholic devotions"
      />

      {/* Hero */}
      <section className="prayers-hero">
        <div className="container">
          <h1 className="prayers-title">Catholic Voices & Prayers</h1>
          <p className="prayers-subtitle">
            Timeless Catholic content, guided by sacred tradition.
          </p>
        </div>
      </section>

      {/* Featured: Bishop Fulton J. Sheen */}
      <section className="prayers-featured">
        <div className="container">
          <Link 
            to="/prayers/fulton-sheen" 
            className="featured-card featured-sheen" 
            data-testid="fulton-sheen-featured"
            style={{
              backgroundImage: `linear-gradient(to right, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,0.85) 100%), url('https://customer-assets.emergentagent.com/job_catholic-voices-4/artifacts/h4sernpl_Yousuf-Karsh-Archbishop-Fulton-Sheen-1952_color_16x9.jpg')`
            }}
          >
            <div className="featured-content-overlay">
              <span className="featured-label">Featured</span>
              <h2 className="featured-title">Pray with Bishop Fulton J. Sheen</h2>
              <p className="featured-description">
                Experience the profound spiritual wisdom of the Venerable Archbishop
              </p>
              <span className="featured-cta">
                Explore Content
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </span>
            </div>
          </Link>
        </div>
      </section>

      {/* Content Categories */}
      <section className="prayers-categories">
        <div className="container">
          <h2 className="section-title">Content Library</h2>
          
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading content...</span>
            </div>
          ) : (
            <div className="categories-grid">
              {/* Lives of the Saints */}
              <Link to="/prayers/saints" className="category-card" data-testid="category-saints">
                <div className="category-icon saints-icon">
                  {categoryConfig.saints.icon}
                </div>
                <div className="category-content">
                  <h3 className="category-title">Lives of the Saints</h3>
                  <p className="category-description">
                    Daily saint reflections and feast day celebrations
                  </p>
                  <span className="category-count">
                    {library?.categories?.saints?.count || 0} videos
                  </span>
                </div>
                <svg className="category-arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </Link>

              {/* Catholic Teachings */}
              <Link to="/teachings" className="category-card" data-testid="category-teachings">
                <div className="category-icon teachings-icon">
                  {categoryConfig.teachings.icon}
                </div>
                <div className="category-content">
                  <h3 className="category-title">Catholic Teachings</h3>
                  <p className="category-description">
                    Faith formation, doctrine, and spiritual guidance
                  </p>
                  <span className="category-count">
                    {library?.categories?.teachings?.count || 0} videos
                  </span>
                </div>
                <svg className="category-arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </Link>

              {/* Prayers & Devotions */}
              <Link to="/prayers/devotions" className="category-card" data-testid="category-devotions">
                <div className="category-icon devotions-icon">
                  {categoryConfig.devotions.icon}
                </div>
                <div className="category-content">
                  <h3 className="category-title">Prayers & Devotions</h3>
                  <p className="category-description">
                    Chaplets, litanies, and traditional Catholic prayers
                  </p>
                  <span className="category-count">
                    {library?.categories?.devotions?.count || 0} videos
                  </span>
                </div>
                <svg className="category-arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 18l6-6-6-6" />
                </svg>
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* Daily Prayer Encouragement */}
      <section className="prayers-daily">
        <div className="container">
          <div className="daily-card">
            <div className="daily-content">
              <h3 className="daily-title">Begin Your Day with Prayer</h3>
              <p className="daily-text">
                "Prayer is the raising of one's mind and heart to God or the requesting of good things from God."
              </p>
              <span className="daily-attribution">— Catechism of the Catholic Church</span>
            </div>
          </div>
        </div>
      </section>

      {/* Subscribe CTA */}
      <section className="prayers-subscribe">
        <div className="container">
          <div className="subscribe-content">
            <h3>Never Miss a Prayer</h3>
            <p>Subscribe to Catholic Voices and Prayers on YouTube for daily devotions</p>
            <a 
              href="https://www.youtube.com/@CatholicVoicesPrayers?sub_confirmation=1"
              target="_blank"
              rel="noopener noreferrer"
              className="subscribe-btn"
              data-testid="subscribe-btn"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              Subscribe on YouTube
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PrayersHome;
