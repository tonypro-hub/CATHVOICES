import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import SEO from '../components/SEO';
import './Prayers.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Prayers = () => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/content`);
      setContent(response.data);
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...Array.from(new Set(content.map(item => item.category)))];
  
  const filteredContent = selectedCategory === 'all' 
    ? content 
    : content.filter(item => item.category === selectedCategory);

  return (
    <div className="prayers-page" data-testid="prayers-page">
      {/* Hero */}
      <section className="prayers-hero">
        <div className="container">
          <h1 className="prayers-title">Prayers & Devotions</h1>
          <p className="prayers-subtitle">
            A collection of traditional Catholic prayers to guide your spiritual journey
          </p>
        </div>
      </section>

      {/* Filters */}
      <section className="prayers-filters">
        <div className="container">
          <div className="filter-tabs">
            {categories.map((category) => (
              <button
                key={category}
                className={`filter-tab ${selectedCategory === category ? 'filter-tab-active' : ''}`}
                onClick={() => setSelectedCategory(category)}
                data-testid={`filter-${category}`}
              >
                {category === 'all' ? 'All Prayers' : category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Content Grid */}
      <section className="prayers-content">
        <div className="container">
          {loading ? (
            <div className="loading">
              <div className="loading-spinner"></div>
              <span>Loading prayers...</span>
            </div>
          ) : (
            <>
              <p className="results-count">
                {filteredContent.length} {filteredContent.length === 1 ? 'prayer' : 'prayers'}
                {selectedCategory !== 'all' && ` in ${selectedCategory}`}
              </p>
              <div className="content-grid">
                {filteredContent.map((item) => (
                  <Link 
                    to={`/prayers/${item.videoId}`} 
                    key={item.videoId} 
                    className="content-card"
                    data-testid={`prayer-card-${item.videoId}`}
                  >
                    <div className="content-card-media">
                      <img src={item.thumbnail} alt={item.title} />
                      <div className="play-icon">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
                          <polygon points="10 8 16 12 10 16 10 8"/>
                        </svg>
                      </div>
                      {item.hasPrayerText && (
                        <span className="text-badge">Prayer Text</span>
                      )}
                    </div>
                    <div className="content-card-body">
                      <span className="content-category">{item.category}</span>
                      <h3 className="content-title">{item.title}</h3>
                    </div>
                  </Link>
                ))}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
};

export default Prayers;
