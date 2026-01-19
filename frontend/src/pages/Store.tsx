import './Store.css';

const Store = () => {
  return (
    <div className="store-page">
      <div className="container">
        {/* Hero Section */}
        <div className="page-hero">
          <div className="hero-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
          </div>
          <h1 className="page-title">Catholic Store</h1>
          <p className="page-subtitle">
            Carefully curated Catholic items to support your faith journey
          </p>
        </div>

        {/* Coming Soon Card */}
        <div className="coming-soon-card">
          <div className="card-content">
            <div className="coming-soon-badge">Opening Soon</div>
            <h2 className="card-heading">Our Affiliate Storefront</h2>
            <p className="card-text">
              We are preparing a curated selection of Catholic books, devotional items, 
              and religious goods from trusted vendors. All items are carefully chosen 
              to support your spiritual growth.
            </p>
            
            {/* Preview Categories */}
            <div className="category-preview">
              <div className="category-item">
                <div className="category-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                    <path d="M12 6v6" />
                    <path d="M9 9h6" />
                  </svg>
                </div>
                <span>Catholic Books</span>
              </div>
              <div className="category-item">
                <div className="category-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                </div>
                <span>Rosaries</span>
              </div>
              <div className="category-item">
                <div className="category-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <circle cx="12" cy="12" r="4" />
                  </svg>
                </div>
                <span>Sacred Art</span>
              </div>
              <div className="category-item">
                <div className="category-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </div>
                <span>Medals & Scapulars</span>
              </div>
            </div>

            <p className="card-text-small">
              As an affiliate storefront, purchases help support Catholic Voices & Prayers 
              at no additional cost to you.
            </p>
          </div>
          
          {/* Decorative Element */}
          <div className="decorative-element">
            <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="0.5">
              <path d="M12 2v20M2 12h20" />
            </svg>
          </div>
        </div>

        {/* Support Note */}
        <div className="support-note">
          <div className="support-icon">♥</div>
          <p className="support-text">
            Until our store launches, the best way to support us is by subscribing 
            to our YouTube channel and sharing our content with others.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Store;
