import { Link } from 'react-router-dom';
import { storeCategories, AFFILIATE_DISCLOSURE_SHORT } from '../data/products';
import './Store.css';

// Category icons as SVG components
const CategoryIcon = ({ type }: { type: string }) => {
  switch (type) {
    case 'book':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      );
    case 'rosary':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="6" r="2" />
          <circle cx="12" cy="12" r="2" />
          <circle cx="12" cy="18" r="2" />
          <circle cx="6" cy="9" r="2" />
          <circle cx="18" cy="9" r="2" />
          <path d="M12 8v2M12 14v2M8 7.5L10 10M14 10l2-2.5" />
        </svg>
      );
    case 'card':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <path d="M12 8v4M10 12h4" />
          <line x1="7" y1="16" x2="17" y2="16" />
        </svg>
      );
    case 'devotional':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      );
    case 'gift':
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="8" width="18" height="13" rx="1" />
          <path d="M12 8v13" />
          <path d="M3 12h18" />
          <path d="M12 8c-2-2-5-2.5-5 0s3 3 5 3 5-.5 5-3-3-2-5 0" />
        </svg>
      );
    default:
      return (
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" />
        </svg>
      );
  }
};

const Store = () => {
  return (
    <div className="store-page">
      <div className="container">
        {/* Hero Section */}
        <div className="store-hero">
          <h1 className="store-title">Catholic Store</h1>
          <p className="store-subtitle">
            Carefully selected items to support your prayer life and spiritual journey
          </p>
        </div>

        {/* Categories Grid */}
        <div className="categories-grid">
          {storeCategories.map((category) => (
            <Link 
              key={category.id} 
              to={`/store/${category.id}`} 
              className="category-card"
            >
              <div className="category-icon">
                <CategoryIcon type={category.icon} />
              </div>
              <h2 className="category-name">{category.name}</h2>
              <p className="category-description">{category.description}</p>
              <span className="category-count">
                {category.products.length} {category.products.length === 1 ? 'item' : 'items'}
              </span>
              <span className="category-link">
                Browse
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </span>
            </Link>
          ))}
        </div>

        {/* Affiliate Disclosure */}
        <div className="affiliate-disclosure">
          <div className="disclosure-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
          </div>
          <p className="disclosure-text">{AFFILIATE_DISCLOSURE_SHORT}</p>
        </div>

        {/* Support Message */}
        <div className="store-support">
          <div className="support-cross">✝</div>
          <p className="support-text">
            Every purchase through our store helps support Catholic Voices & Prayers, 
            allowing us to continue creating prayer content for the faithful.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Store;
