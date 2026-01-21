import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import SEO from '../components/SEO';
import './SaintsArchive.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SaintsArchive = () => {
  const [saints, setSaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 24;

  useEffect(() => {
    fetchSaints();
  }, []);

  const fetchSaints = async (newOffset = 0) => {
    try {
      if (newOffset === 0) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      const response = await axios.get(`${API}/saints/archive`, {
        params: { limit, offset: newOffset }
      });

      if (newOffset === 0) {
        setSaints(response.data.saints);
      } else {
        setSaints(prev => [...prev, ...response.data.saints]);
      }

      setTotal(response.data.total);
      setHasMore(response.data.hasMore);
      setOffset(newOffset + limit);
    } catch (err) {
      console.error('Error fetching saints archive:', err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const groupByMonth = (saints) => {
    const groups = {};
    
    saints.forEach(saint => {
      const date = new Date(saint.feastDate + 'T00:00:00');
      const monthKey = date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      
      if (!groups[monthKey]) {
        groups[monthKey] = [];
      }
      groups[monthKey].push(saint);
    });
    
    return groups;
  };

  if (loading) {
    return (
      <div className="saints-archive-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading saints archive...</p>
        </div>
      </div>
    );
  }

  const groupedSaints = groupByMonth(saints);

  return (
    <div className="saints-archive-page" data-testid="saints-archive-page">
      {/* Hero Section */}
      <section className="archive-hero">
        <div className="container">
          <Link to="/daily-saint" className="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Today's Saint
          </Link>
          <h1 className="archive-title">Saints Archive</h1>
          <p className="archive-subtitle">
            Browse our complete collection of {total} daily saints from the Daily Lives of the Saints series.
          </p>
        </div>
      </section>

      {/* Archive Grid */}
      <section className="section archive-content">
        <div className="container">
          {saints.length === 0 ? (
            <div className="empty-archive">
              <div className="empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M12 2v2"/>
                  <path d="M12 12c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z"/>
                </svg>
              </div>
              <h2>No Saints Yet</h2>
              <p>The saints archive is being built. Check back soon!</p>
              <Link to="/daily-saint" className="btn-primary">
                View Today's Saint
              </Link>
            </div>
          ) : (
            <>
              {Object.entries(groupedSaints).map(([monthYear, monthSaints]) => (
                <div key={monthYear} className="archive-month-group">
                  <h2 className="month-header">{monthYear}</h2>
                  <div className="saints-grid">
                    {monthSaints.map((saint) => (
                      <Link 
                        key={saint.id} 
                        to={`/saints/${saint.id}`}
                        className="saint-card"
                        data-testid={`saint-card-${saint.id}`}
                      >
                        <div className="saint-card-image">
                          <img src={saint.thumbnail} alt={saint.saintName} />
                          <div className="saint-card-overlay">
                            <div className="play-icon">
                              <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                                <polygon points="10 8 16 12 10 16 10 8"/>
                              </svg>
                            </div>
                          </div>
                        </div>
                        <div className="saint-card-content">
                          <span className="saint-card-date">{formatDate(saint.feastDate)}</span>
                          <h3 className="saint-card-name">{saint.saintName}</h3>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              ))}

              {hasMore && (
                <div className="load-more-container">
                  <button 
                    onClick={() => fetchSaints(offset)}
                    disabled={loadingMore}
                    className="btn-secondary load-more-btn"
                  >
                    {loadingMore ? (
                      <>
                        <span className="loading-spinner-small"></span>
                        Loading...
                      </>
                    ) : (
                      `Load More Saints (${saints.length} of ${total})`
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="section archive-cta-section" data-testid="archive-cta">
        <div className="container container-narrow">
          <div className="archive-cta-card">
            <h2>Never Miss a Saint</h2>
            <p>Subscribe to our YouTube channel to receive daily saint videos.</p>
            <a 
              href="https://www.youtube.com/@CatholicVoicesPrayers?sub_confirmation=1" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-primary"
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

export default SaintsArchive;
