import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';
import './Home.css';

interface Prayer {
  id: string;
  title: string;
  videoId: string;
  category: string;
  prayerText: string;
}

const Home = () => {
  const [featuredPrayer, setFeaturedPrayer] = useState<Prayer | null>(null);
  const [prayers, setPrayers] = useState<Prayer[]>([]);

  useEffect(() => {
    fetchPrayers();
  }, []);

  const fetchPrayers = async () => {
    try {
      const response = await axios.get('/api/content');
      const allContent = response.data;
      setPrayers(allContent);
      // Set first item as featured
      if (allContent.length > 0) {
        setFeaturedPrayer(allContent[0]);
      }
    } catch (error) {
      console.error('Error fetching content:', error);
    }
  };

  // Get unique categories
  const categories = Array.from(new Set(prayers.map(p => p.category)));

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

      {/* Featured Prayer Section */}
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
                  Watch Now →
                </Link>
              </div>
              <div className="featured-media">
                <div className="video-thumbnail">
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
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Daily Feast / Saint Section */}
      <section className="daily-section">
        <div className="content-container">
          <div className="section-label">Today's Devotion</div>
          <div className="daily-content">
            <h2 className="daily-title">The Holy Rosary</h2>
            <p className="daily-description">
              Join Bishop Fulton J. Sheen in praying the mysteries of the Rosary.<br />
              Contemplate the Joyful, Sorrowful, and Glorious moments of our salvation.
            </p>
            <Link to="/prayers" className="text-link">
              Watch & Pray →
            </Link>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="section-divider">
        <div className="divider-line"></div>
      </div>

      {/* Prayer Categories Section */}
      <section className="categories-section">
        <div className="content-container">
          <h2 className="section-heading">Traditional Catholic Prayers</h2>
          <p className="section-subheading">
            Explore our collection of prayers, organized by tradition and devotion.
          </p>
          
          <div className="categories-list">
            {categories.map((category, index) => {
              const categoryPrayers = prayers.filter(p => p.category === category);
              return (
                <div key={index} className="category-item">
                  <div className="category-header">
                    <h3 className="category-name">{category}</h3>
                    <span className="category-count">{categoryPrayers.length} {categoryPrayers.length === 1 ? 'prayer' : 'prayers'}</span>
                  </div>
                  <div className="category-prayers">
                    {categoryPrayers.slice(0, 3).map(prayer => (
                      <Link 
                        key={prayer.videoId} 
                        to={`/prayers/${prayer.videoId}`} 
                        className="prayer-link"
                      >
                        {prayer.title}
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

      {/* Invitation to Explore */}
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

      {/* Final Blessing */}
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
