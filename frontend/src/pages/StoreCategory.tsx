import { useParams, Link } from 'react-router-dom';
import { getCategoryById, AFFILIATE_DISCLOSURE } from '../data/products';
import './Store.css';

const StoreCategory = () => {
  const { categoryId } = useParams<{ categoryId: string }>();
  const category = categoryId ? getCategoryById(categoryId) : undefined;

  if (!category) {
    return (
      <div className="category-page">
        <div className="container">
          <div className="error-state" style={{ textAlign: 'center', padding: '6rem 0' }}>
            <h2>Category not found</h2>
            <Link to="/store" className="btn-primary" style={{ marginTop: '1.5rem', display: 'inline-block' }}>Back to Store</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="category-page">
      {/* Breadcrumb */}
      <nav className="store-breadcrumb">
        <div className="container">
          <Link to="/">Home</Link>
          <span className="bc-sep">/</span>
          <Link to="/store">Store</Link>
          <span className="bc-sep">/</span>
          <span>{category.name}</span>
        </div>
      </nav>

      {/* Hero */}
      <section className="category-hero">
        <h1 className="category-hero-title">{category.name}</h1>
        <p className="category-hero-desc">{category.description}</p>
      </section>

      {/* Products */}
      <section className="products-section">
        <div className="container">
          <div className="products-grid">
            {category.products.map((product) => (
              <article key={product.id} className="product-card">
                <div className="product-image">
                  <img src={product.image} alt={product.name} loading="lazy" />
                </div>
                <div className="product-info">
                  <h2 className="product-name">{product.name}</h2>
                  <p className="product-desc">{product.description}</p>
                  <div className="product-footer">
                    {product.price && <span className="product-price">{product.price}</span>}
                    <a 
                      href={product.affiliateUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="product-btn"
                    >
                      View Product
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" y1="14" x2="21" y2="3" />
                      </svg>
                    </a>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Disclosure */}
          <div className="full-disclosure">
            <h3>Affiliate Disclosure</h3>
            <p>{AFFILIATE_DISCLOSURE}</p>
          </div>

          {/* Back */}
          <Link to="/store" className="back-to-store">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Back to All Categories
          </Link>
        </div>
      </section>
    </div>
  );
};

export default StoreCategory;
