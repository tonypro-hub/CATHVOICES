import { Link } from 'react-router-dom';
import { storeCategories, AFFILIATE_DISCLOSURE_SHORT } from '../data/products';
import './Store.css';

// Category icons
const CategoryIcon = ({ type }: { type: string }) => {
  const icons: Record<string, JSX.Element> = {
    book: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      </svg>
    ),
    rosary: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="6" r="2" />
        <circle cx="12" cy="12" r="2" />
        <circle cx="12" cy="18" r="2" />
        <path d="M12 8v2M12 14v2" />
      </svg>
    ),
    card: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="4" width="18" height="16" rx="2" />
        <path d="M12 8v4M10 12h4" />
      </svg>
    ),
    devotional: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
    gift: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="8" width="18" height="13" rx="1" />
        <path d="M12 8v13M3 12h18" />
      </svg>
    ),
  };
  return icons[type] || icons.book;
};

const Store = () => {
  return (
    <div className="store-page">
      {/* Hero */}
      <section className="store-hero">
        <div className="container">
          <h1 className="store-title">Catholic Store</h1>
          <p className="store-subtitle">
            Carefully selected items to support your prayer life and spiritual journey
          </p>
        </div>
      </section>

      {/* Categories */}
      <section className="section store-categories">
        <div className="container">
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
                <p className="category-desc">{category.description}</p>
                <span className="category-count">
                  {category.products.length} {category.products.length === 1 ? 'item' : 'items'}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Disclosure */}
      <section className="section-sm store-disclosure">
        <div className="container container-narrow">
          <div className="disclosure-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4M12 8h.01" />
            </svg>
            <p>{AFFILIATE_DISCLOSURE_SHORT}</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Store;
