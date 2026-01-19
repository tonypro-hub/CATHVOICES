import './MassMap.css';

const MassMap = () => {
  return (
    <div className="mass-map-page">
      {/* Hero */}
      <section className="mass-hero">
        <div className="container">
          <div className="hero-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
          </div>
          <h1 className="mass-title">Mass Map</h1>
          <p className="mass-subtitle">
            Find reverent Traditional Latin Masses and devout Novus Ordo celebrations across the United States
          </p>
        </div>
      </section>

      {/* Coming Soon Card */}
      <section className="section mass-content">
        <div className="container container-narrow">
          <div className="coming-card">
            <span className="coming-badge">Coming Soon</span>
            <h2 className="coming-title">U.S. Reverent Mass Directory</h2>
            <p className="coming-desc">
              We are building a comprehensive directory of reverent Catholic Masses 
              throughout the United States. Our goal is to help you find:
            </p>
            <ul className="coming-list">
              <li>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Traditional Latin Masses (TLM)
              </li>
              <li>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Reverent Novus Ordo Masses
              </li>
              <li>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Ad Orientem celebrations
              </li>
              <li>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Masses with sacred music and chant
              </li>
            </ul>
            <p className="coming-note">
              Our team is carefully curating this list to ensure quality and accuracy. 
              Please check back soon for updates.
            </p>
          </div>

          {/* Contact */}
          <div className="contact-note">
            <p>
              Want to suggest a reverent Mass location? Contact us through our social media channels.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default MassMap;
