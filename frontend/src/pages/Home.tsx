import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';
import './Home.css';

interface ContentItem {
  id: string;
  videoId: string;
  title: string;
  description: string;
  thumbnail: string;
  category: string;
  duration: string;
  publishedAt: string;
  isShort: boolean;
  prayerText?: string;
  hasPrayerText: boolean;
}

const Home = () => {
  const [dailyShort, setDailyShort] = useState<ContentItem | null>(null);
  const [featuredPrayer, setFeaturedPrayer] = useState<ContentItem | null>(null);
  const [recentPrayers, setRecentPrayers] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      // Fetch daily Short
      try {
        const dailyResponse = await axios.get('/api/shorts/daily');
        setDailyShort(dailyResponse.data);
      } catch (error) {
        console.log('No daily Short available');
      }

      // Fetch long-form content
      const contentResponse = await axios.get('/api/content');
      const longFormVideos = contentResponse.data;
      
      if (longFormVideos.length > 0) {
        setFeaturedPrayer(longFormVideos[0]);
        setRecentPrayers(longFormVideos.slice(1, 7));
      }
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Find peace in prayer</h1>
          <p className="hero-subtitle">
            A sacred space for traditional Catholic prayer and devotion,
            guided by the wisdom of the Church and the voices of faithful Catholics.
          </p>
          <Link to="/prayers" className="btn-primary">
            Begin Praying
          </Link>
        </div>
      </section>

      {/* Daily Focus Section */}
      {dailyShort && (
        <section className="section daily-focus">
          <div className="container">
            <div className="section-header">
              <span className="section-label">Today's Reflection</span>
              <h2 className="section-title">Daily Devotion</h2>
            </div>
            <div className="daily-card">
              <Link to={`/prayers/${dailyShort.videoId}`} className="daily-media">
                <img 
                  src={dailyShort.thumbnail}
                  alt={dailyShort.title}
                  className="daily-image"
                />
                <div className="play-button">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="10 8 16 12 10 16 10 8"/>
                  </svg>
                </div>
              </Link>
              <div className="daily-info">
                <span className="daily-category">{dailyShort.category}</span>
                <h3 className="daily-title">{dailyShort.title}</h3>
                <p className="daily-description">
                  {dailyShort.description ? dailyShort.description.slice(0, 150) + '...' : 'A brief reflection to guide your prayer today.'}
                </p>
                <Link to={`/prayers/${dailyShort.videoId}`} className="text-link">
                  Watch Now
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Featured Prayer Section */}
      {featuredPrayer && (
        <section className="section featured-prayer">
          <div className="container">
            <div className="featured-grid">
              <div className="featured-content">
                <span className="section-label">Featured Prayer</span>
                <h2 className="featured-title">{featuredPrayer.title}</h2>
                <p className="featured-excerpt">
                  {featuredPrayer.description ? 
                    featuredPrayer.description.slice(0, 200) + '...' : 
                    'Experience the beauty of this traditional Catholic prayer.'}
                </p>
                <div className="featured-actions">
                  <Link to={`/prayers/${featuredPrayer.videoId}`} className="btn-primary">
                    Pray Now
                  </Link>
                  <Link to="/prayers" className="btn-secondary">
                    Browse All
                  </Link>
                </div>
              </div>
              <Link to={`/prayers/${featuredPrayer.videoId}`} className="featured-media">
                <img 
                  src={featuredPrayer.thumbnail}
                  alt={featuredPrayer.title}
                  className="featured-image"
                />
                <div className="play-button play-button-lg">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="10 8 16 12 10 16 10 8"/>
                  </svg>
                </div>
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Content Modules */}
      <section className="section modules">
        <div className="container">
          <div className="modules-grid">
            {/* Prayers Module */}
            <Link to="/prayers" className="module-card">
              <div className="module-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
              <h3 className="module-title">Prayers & Devotions</h3>
              <p className="module-description">Traditional prayers for every occasion</p>
              <span className="module-link">
                Explore
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>

            {/* Saints Module */}
            <Link to="/saints-feasts" className="module-card">
              <div className="module-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M12 2v2"/>
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
                </svg>
              </div>
              <h3 className="module-title">Saints & Feast Days</h3>
              <p className="module-description">Discover the lives of holy men and women</p>
              <span className="module-link">
                Explore
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>

            {/* Daily Module */}
            <Link to="/daily" className="module-card">
              <div className="module-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <h3 className="module-title">Daily Reflections</h3>
              <p className="module-description">Brief moments of prayer for each day</p>
              <span className="module-link">
                Explore
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* Recent Prayers Grid */}
      {recentPrayers.length > 0 && (
        <section className="section recent-prayers">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">Recent Prayers</h2>
              <Link to="/prayers" className="text-link">
                View All
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Link>
            </div>
            <div className="prayers-grid">
              {recentPrayers.map((prayer) => (
                <Link 
                  key={prayer.videoId} 
                  to={`/prayers/${prayer.videoId}`} 
                  className="prayer-card"
                >
                  <div className="prayer-card-media">
                    <img src={prayer.thumbnail} alt={prayer.title} />
                    <div className="play-button play-button-sm">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="10 8 16 12 10 16 10 8"/>
                      </svg>
                    </div>
                  </div>
                  <div className="prayer-card-content">
                    <span className="prayer-card-category">{prayer.category}</span>
                    <h3 className="prayer-card-title">{prayer.title}</h3>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Invitation Section */}
      <section className="section-lg invitation">
        <div className="container container-narrow">
          <div className="invitation-content">
            <h2 className="invitation-title">Begin your prayer journey</h2>
            <p className="invitation-text">
              Whether you seek the comfort of the Rosary, the power of novenas,
              or the beauty of traditional prayers, you will find a home here.
            </p>
            <div className="invitation-actions">
              <Link to="/prayers" className="btn-primary">Explore Prayers</Link>
              <Link to="/about" className="btn-secondary">Learn More</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Scripture Quote */}
      <section className="section scripture">
        <div className="container container-narrow">
          <blockquote className="scripture-quote">
            <p>"Pray without ceasing."</p>
            <cite>— 1 Thessalonians 5:17</cite>
          </blockquote>
        </div>
      </section>
    </div>
  );
};

export default Home;
