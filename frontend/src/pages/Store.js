import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import './Store.css';

const SAMPLE_PRODUCTS = [
  {
    id: 1,
    name: 'Traditional Latin Missal',
    description: 'A comprehensive missal with both Latin and English texts for the Traditional Roman Rite.',
    price: 45.99,
    category: 'Books',
    image: 'https://m.media-amazon.com/images/I/51qA7y9t8qL._SY580_.jpg',
    affiliateUrl: 'https://www.amazon.com/dp/1930278276'
  },
  {
    id: 2,
    name: 'Brown Scapular',
    description: 'Authentic Brown Scapular of Our Lady of Mt. Carmel, blessed and ready for enrollment.',
    price: 8.99,
    category: 'Sacramentals',
    image: 'https://m.media-amazon.com/images/I/61oG6hfuQGL._AC_SX679_.jpg',
    affiliateUrl: 'https://www.amazon.com/dp/B07F8GWQLS'
  },
  {
    id: 3,
    name: 'Crystal Rosary Beads',
    description: 'Beautiful handcrafted crystal rosary beads with silver crucifix.',
    price: 24.99,
    category: 'Rosaries',
    image: 'https://m.media-amazon.com/images/I/71z6NLSE7jL._AC_SX679_.jpg',
    affiliateUrl: 'https://www.amazon.com/dp/B075DKM3WC'
  },
  {
    id: 4,
    name: 'Douay-Rheims Bible',
    description: 'The traditional Catholic Bible in the historic Douay-Rheims translation.',
    price: 34.99,
    category: 'Books',
    image: 'https://m.media-amazon.com/images/I/71s1FApZd1L._SY466_.jpg',
    affiliateUrl: 'https://www.amazon.com/dp/1930278241'
  },
  {
    id: 5,
    name: 'Miraculous Medal',
    description: 'Sterling silver Miraculous Medal on a delicate chain.',
    price: 19.99,
    category: 'Sacramentals',
    image: 'https://m.media-amazon.com/images/I/61xQTfXVURL._AC_SY695_.jpg',
    affiliateUrl: 'https://www.amazon.com/dp/B00DGI1JUS'
  },
  {
    id: 6,
    name: 'Wooden Rosary Case',
    description: 'Elegant handcrafted wooden case to protect your rosary.',
    price: 14.99,
    category: 'Accessories',
    image: 'https://m.media-amazon.com/images/I/81n3B3w9+LL._AC_SX679_.jpg',
    affiliateUrl: 'https://www.amazon.com/dp/B07QXVVN8J'
  }
];

const Store = () => {
  return (
    <div className="store-page" data-testid="store-page">
      <SEO 
        title="Catholic Store - Sacred Items"
        description="Shop carefully curated Catholic items including missals, rosaries, scapulars, and sacred art to support your prayer life and spiritual journey."
        keywords="Catholic store, rosary, missal, scapular, Catholic gifts, religious items, Traditional Latin Mass missal"
      />
      {/* Hero */}
      <section className="store-hero">
        <div className="container">
          <span className="store-label">Catholic Store</span>
          <h1 className="store-title">Sacred Items for Your Faith</h1>
          <p className="store-subtitle">
            Carefully curated Catholic items to support your prayer life and spiritual journey
          </p>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="store-notice">
        <div className="container">
          <div className="notice-banner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <p>
              <strong>Affiliate Disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases. 
              This helps support our ministry at no additional cost to you.
            </p>
          </div>
        </div>
      </section>

      {/* Products Grid */}
      <section className="section store-products">
        <div className="container">
          <div className="products-grid">
            {SAMPLE_PRODUCTS.map((product) => (
              <div key={product.id} className="product-card" data-testid={`product-${product.id}`}>
                <div className="product-image">
                  <img src={product.image} alt={product.name} />
                  <span className="product-category">{product.category}</span>
                </div>
                <div className="product-info">
                  <h3 className="product-name">{product.name}</h3>
                  <p className="product-description">{product.description}</p>
                  <div className="product-footer">
                    <span className="product-price">${product.price.toFixed(2)}</span>
                    <a 
                      href={product.affiliateUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="product-btn"
                    >
                      View on Amazon
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="section store-categories">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Browse by Category</h2>
          </div>
          <div className="categories-grid">
            {['Books', 'Rosaries', 'Sacramentals', 'Accessories'].map((category) => (
              <div key={category} className="category-card">
                <div className="category-icon">
                  {category === 'Books' && (
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                    </svg>
                  )}
                  {category === 'Rosaries' && (
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <circle cx="12" cy="12" r="3"/>
                      <circle cx="12" cy="5" r="2"/>
                      <circle cx="17" cy="9" r="2"/>
                      <circle cx="17" cy="15" r="2"/>
                      <circle cx="12" cy="19" r="2"/>
                      <circle cx="7" cy="15" r="2"/>
                      <circle cx="7" cy="9" r="2"/>
                    </svg>
                  )}
                  {category === 'Sacramentals' && (
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                      <path d="M2 17l10 5 10-5"/>
                      <path d="M2 12l10 5 10-5"/>
                    </svg>
                  )}
                  {category === 'Accessories' && (
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <rect x="3" y="8" width="18" height="13" rx="2"/>
                      <path d="M12 8v13"/>
                      <path d="M3 12h18"/>
                    </svg>
                  )}
                </div>
                <h3 className="category-name">{category}</h3>
                <span className="category-count">
                  {SAMPLE_PRODUCTS.filter(p => p.category === category).length} items
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-lg store-cta" data-testid="store-cta">
        <div className="container container-narrow">
          <div className="cta-card">
            <h2>Looking for Something Specific?</h2>
            <p>Our store is a small curated selection. For a wider range of Catholic items, visit our trusted partners.</p>
            <div className="cta-buttons">
              <Link to="/prayers" className="btn-primary">Explore Our Prayers</Link>
              <Link to="/about" className="btn-secondary">Learn About Us</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Store;
