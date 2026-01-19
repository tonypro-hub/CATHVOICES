import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Prayers.css';

interface ContentItem {
  id: string;
  videoId: string;
  title: string;
  description: string;
  thumbnail: string;
  category: string;
  duration: string;
  publishedAt: string;
  hasPrayerText: boolean;
}

const Prayers = () => {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/content');
      setContent(response.data);
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="prayers-page">
        <div className="container">
          <div className="loading">Loading content...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="prayers-page">
      <div className="container">
        <div className="prayers-header">
          <h1 className="prayers-title">All Videos & Prayers</h1>
          <p className="prayers-subtitle">{content.length} videos from Catholic Voices & Prayers</p>
        </div>

        <div className="prayers-grid">
          {content.map((item) => (
            <Link to={`/prayers/${item.videoId}`} key={item.videoId} className="prayer-card">
              <div className="prayer-card-thumbnail">
                <img src={item.thumbnail} alt={item.title} className="thumbnail-img" />
                <div className="play-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polygon points="10 8 16 12 10 16 10 8"/>
                  </svg>
                </div>
              </div>
              <div className="prayer-card-content">
                <span className="prayer-category">{item.category}</span>
                <h3 className="prayer-card-title">{item.title}</h3>
                {item.hasPrayerText && (
                  <span className="has-prayer-badge">Prayer Text Available</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Prayers;
