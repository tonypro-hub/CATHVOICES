import { useEffect, useState, useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import SEO from '../../components/SEO';
import './Teachings.css';

const API = process.env.REACT_APP_BACKEND_URL;

const TeachingsCategoryPage = () => {
  const { categoryId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);

  const fetchCategory = useCallback(async (pageNum = 1, append = false) => {
    try {
      if (pageNum === 1) setLoading(true);
      else setLoadingMore(true);
      
      const response = await fetch(`${API}/api/teachings/category/${categoryId}?page=${pageNum}&limit=24`);
      if (response.ok) {
        const result = await response.json();
        if (append && data) {
          setData({
            ...result,
            videos: [...data.videos, ...result.videos]
          });
        } else {
          setData(result);
        }
        setPage(pageNum);
      }
    } catch (error) {
      console.error('Error fetching category:', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [categoryId, data]);

  useEffect(() => {
    fetchCategory(1, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categoryId]);

  const loadMore = () => {
    if (data?.hasMore && !loadingMore) {
      fetchCategory(page + 1, true);
    }
  };

  return (
    <div className="teachings-page" data-testid={`category-page-${categoryId}`}>
      <SEO 
        title={`${data?.name || 'Catholic Teachings'} | Catholic Voices and Prayers`}
        description={data?.description || 'Catholic teachings and apologetics.'}
        keywords={`Catholic Teachings, ${data?.name || ''}, Catholic Apologetics, Faith Formation`}
      />

      {/* Hero */}
      <section className="teachings-hero teachings-hero-compact">
        <div className="container">
          <Link to="/teachings" className="teachings-back">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Teachings
          </Link>
          <h1 className="teachings-title">{data?.name || 'Loading...'}</h1>
          <p className="teachings-subtitle">{data?.description || ''}</p>
          {data && (
            <p className="teachings-count">{data.count} teachings in this category</p>
          )}
        </div>
      </section>

      {/* Videos Grid */}
      <section className="teachings-videos">
        <div className="container">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner" />
              <span>Loading teachings...</span>
            </div>
          ) : data?.videos?.length > 0 ? (
            <>
              <div className="shorts-grid shorts-grid-full">
                {data.videos.map(video => (
                  <Link 
                    to={`/teachings/video/${video.videoId}`}
                    key={video.videoId}
                    className="short-card"
                    data-testid={`video-${video.videoId}`}
                  >
                    <div className="short-thumbnail">
                      <img src={video.thumbnail} alt={video.title} loading="lazy" />
                      <div className="short-overlay">
                        <div className="play-icon">
                          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                            <polygon points="10 8 16 12 10 16 10 8"/>
                          </svg>
                        </div>
                      </div>
                      <span className="short-duration">{video.durationFormatted}</span>
                    </div>
                    <div className="short-info">
                      <h3 className="short-title">{video.title}</h3>
                    </div>
                  </Link>
                ))}
              </div>
              
              {data.hasMore && (
                <div className="load-more-container">
                  <button 
                    onClick={loadMore} 
                    className="load-more-btn"
                    disabled={loadingMore}
                    data-testid="load-more-btn"
                  >
                    {loadingMore ? (
                      <>
                        <div className="loading-spinner-small" />
                        Loading...
                      </>
                    ) : (
                      <>
                        Load More
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M12 5v14M5 12l7 7 7-7"/>
                        </svg>
                      </>
                    )}
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <h3>No teachings found</h3>
              <p>Check back soon for more content.</p>
              <Link to="/teachings" className="btn-primary">
                Back to Teachings
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default TeachingsCategoryPage;
