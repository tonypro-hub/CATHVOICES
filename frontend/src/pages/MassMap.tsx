import './MassMap.css';

const MassMap = () => {
  return (
    <div className="mass-map-page">
      <div className="container">
        {/* Hero Section */}
        <div className="page-hero">
          <div className="hero-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
              <path d="M12 7v6" />
              <path d="M9 10h6" />
            </svg>
          </div>
          <h1 className="page-title">Mass Map</h1>
          <p className="page-subtitle">
            Find reverent Traditional Latin Masses and devout Novus Ordo celebrations across the United States
          </p>
        </div>

        {/* Coming Soon Card */}
        <div className="coming-soon-card">
          <div className="card-content">
            <div className="coming-soon-badge">Coming Soon</div>
            <h2 className="card-heading">U.S. Reverent Mass Directory</h2>
            <p className="card-text">
              We are building a comprehensive directory of reverent Catholic Masses 
              throughout the United States. Our goal is to help you find:
            </p>
            <ul className="feature-list">
              <li>
                <span className="feature-icon">✝</span>
                <span>Traditional Latin Masses (TLM)</span>
              </li>
              <li>
                <span className="feature-icon">✝</span>
                <span>Reverent Novus Ordo Masses</span>
              </li>
              <li>
                <span className="feature-icon">✝</span>
                <span>Ad Orientem celebrations</span>
              </li>
              <li>
                <span className="feature-icon">✝</span>
                <span>Masses with sacred music and chant</span>
              </li>
            </ul>
            <p className="card-text-small">
              Our team is carefully curating this list to ensure quality and accuracy. 
              Please check back soon for updates.
            </p>
          </div>
          
          {/* Decorative Element */}
          <div className="decorative-cross">
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="0.5">
              <path d="M12 2v20M2 12h20" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </div>
        </div>

        {/* Notify Section */}
        <div className="notify-section">
          <p className="notify-text">
            Want to suggest a reverent Mass location? Contact us through our social media channels.
          </p>
        </div>
      </div>
    </div>
  );
};

export default MassMap;
