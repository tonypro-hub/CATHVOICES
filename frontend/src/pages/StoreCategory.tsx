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
          <Link to="/store" className="back-to-store">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Back to Store
          </Link>
          <div className="empty-category">
            <div className="empty-icon">✝</div>
            <p className="empty-text">Category not found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="category-page">
      <div className="container">
        {/* Breadcrumb */}
        <nav className="breadcrumb">
          <Link to="/">Home</Link>
          <span className="breadcrumb-separator">/</span>
          <Link to="/store">Store</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">{category.name}</span>
        </nav>

        {/* Category Header */}
        <header className="category-header">
          <h1 className="category-page-title">{category.name}</h1>
          <p className="category-page-description">{category.description}</p>
        </header>

        {/* Products Grid */}
        {category.products.length > 0 ? (
          <div className="products-grid">
            {category.products.map((product) => (
              <article key={product.id} className="product-card">
                <div className="product-image-container">
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className="product-image"
                    loading="lazy"
                  />
                </div>
                <div className="product-info">
                  <h2 className="product-name">{product.name}</h2>
                  <p className="product-description">{product.description}</p>
                  <div className="product-footer">
                    {product.price && (
                      <span className="product-price">{product.price}</span>
                    )}
                    <a 
                      href={product.affiliateUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="product-button"
                    >
                      View Product
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
        ) : (
          <div className="empty-category">
            <div className="empty-icon">✝</div>
            <p className="empty-text">Products coming soon</p>
          </div>
        )}

        {/* Affiliate Disclosure */}
        <div className="full-disclosure">
          <h3 className="disclosure-heading">Affiliate Disclosure</h3>
          <p>{AFFILIATE_DISCLOSURE}</p>
        </div>

        {/* Back to Store */}
        <Link to="/store" className="back-to-store">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to All Categories
        </Link>
      </div>
    </div>
  );
};

export default StoreCategory;
