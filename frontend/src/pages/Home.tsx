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
  const [evergreenContent, setEvergreenContent] = useState<ContentItem[]>([]);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      // Fetch daily Short (secondary content)
      try {
        const dailyResponse = await axios.get('/api/shorts/daily');
        setDailyShort(dailyResponse.data);
      } catch (error) {
        console.log('No daily Short available');
      }

      // Fetch evergreen long-form content (primary)
      const contentResponse = await axios.get('/api/content'); // Excludes Shorts by default
      const longFormVideos = contentResponse.data;
      setEvergreenContent(longFormVideos);
      
      // Set first long-form video as featured
      if (longFormVideos.length > 0) {
        setFeaturedPrayer(longFormVideos[0]);
      }
    } catch (error) {
      console.error('Error fetching content:', error);
    }
  };

  // Get unique categories from evergreen content
  const categories = Array.from(new Set(evergreenContent.map(p => p.category)));

  return (
    <div className="home">
      {/* Hero Section - Mission Statement */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-symbol">✝</div>
          <h1 className="hero-title">Catholic Voices & Prayers</h1>
          <p className="hero-mission">
            A sacred space for traditional Catholic prayer and devotion,<br />
            guided by the wisdom of Bishop Fulton Sheen and the voices of faithful Catholics.
          </p>
          <p className="hero-invitation">
            Enter into prayer. Draw closer to Christ.
          </p>
        </div>
      </section>

      {/* DAILY CONTENT SECTION (Secondary - Powered by Shorts) */}
      {dailyShort && (
        <section className="daily-section">
          <div className="content-container">
            <div className="section-label daily-label">Today's Reflection</div>
            <div className="daily-content">
              <div className="daily-video">
                <Link to={`/prayers/${dailyShort.videoId}`} className="daily-thumbnail-link">
                  <img 
                    src={dailyShort.thumbnail}
                    alt={dailyShort.title}
                    className="daily-thumbnail"
                  />
                  <div className="play-overlay">
                    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polygon points="10 8 16 12 10 16 10 8"/>
                    </svg>
                  </div>
                  <div className="short-badge">Short Reflection</div>
                </Link>
              </div>
              <div className="daily-text">
                <span className="daily-category">{dailyShort.category}</span>
                <h2 className="daily-title">{dailyShort.title}</h2>
                <p className="daily-description">
                  {dailyShort.description ? dailyShort.description.slice(0, 200) + '...' : 'A brief daily reflection to guide your prayer.'}
                </p>
                <Link to={`/prayers/${dailyShort.videoId}`} className="text-link">
                  Watch Now →
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Divider */}
      <div className="section-divider">
        <div className="divider-line"></div>
      </div>

      {/* FEATURED PRAYER SECTION (Primary - Evergreen Long-Form) */}
      {featuredPrayer && (
        <section className="featured-section">
          <div className="content-container">
            <div className="section-label">Featured Prayer</div>
            <div className="featured-content">
              <div className="featured-text">
                <h2 className="featured-title">{featuredPrayer.title}</h2>
                <p className="featured-excerpt">
                  {featuredPrayer.description ? featuredPrayer.description.slice(0, 280) + '...' : 
                   (featuredPrayer.prayerText ? featuredPrayer.prayerText.slice(0, 280) + '...' : '')}
                </p>
                <Link to={`/prayers/${featuredPrayer.videoId}`} className="text-link">
                  Pray Now →
                </Link>
              </div>
              <div className="featured-media">
                <Link to={`/prayers/${featuredPrayer.videoId}`} className="video-thumbnail">
                  <img 
                    src={featuredPrayer.thumbnail || `https://img.youtube.com/vi/${featuredPrayer.videoId}/maxresdefault.jpg`}
                    alt={featuredPrayer.title}
                    className="thumbnail-image"
                  />
                  <div className="play-overlay">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polygon points="10 8 16 12 10 16 10 8"/>
                    </svg>
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Divider */}
      <div className="section-divider">
        <div className="divider-line"></div>
      </div>

      {/* EVERGREEN PRAYER CATEGORIES (Primary - Long-Form Only) */}
      <section className="categories-section">
        <div className="content-container">
          <h2 className="section-heading">Traditional Catholic Prayers</h2>
          <p className="section-subheading">
            Explore our collection of prayers, organized by tradition and devotion.
          </p>
          
          <div className="categories-list">
            {categories.map((category, index) => {
              const categoryContent = evergreenContent.filter(p => p.category === category);
              return (
                <div key={index} className="category-item">
                  <div className="category-header">
                    <h3 className="category-name">{category}</h3>
                    <span className="category-count">{categoryContent.length} {categoryContent.length === 1 ? 'video' : 'videos'}</span>
                  </div>
                  <div className="category-prayers">
                    {categoryContent.slice(0, 3).map(content => (
                      <Link 
                        key={content.videoId} 
                        to={`/prayers/${content.videoId}`} 
                        className="prayer-link"
                      >
                        {content.title}
                      </Link>
                    ))}
                  </div>
                  <Link to="/prayers" className="category-link">
                    View all →
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="section-divider">
        <div className="divider-line"></div>
      </div>

      {/* INVITATION TO EXPLORE */}
      <section className="invitation-section">
        <div className="content-container">
          <div className="invitation-content">
            <div className="invitation-symbol">✝</div>
            <h2 className="invitation-title">
              Come and pray with us
            </h2>
            <p className="invitation-text">
              Whether you seek the comfort of the Rosary, the power of novenas,<br />
              or the beauty of traditional prayers, you will find a home here.
            </p>
            <div className="invitation-actions">
              <Link to="/prayers" className="primary-link">
                Browse All Prayers
              </Link>
              <Link to="/about" className="secondary-link">
                Learn More About Us
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* FINAL BLESSING */}
      <section className="blessing-section">
        <div className="content-container">
          <p className="blessing-text">
            "Pray without ceasing." — 1 Thessalonians 5:17
          </p>
        </div>
      </section>
    </div>
  );
};

export default Home;
