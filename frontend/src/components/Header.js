import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    document.body.style.overflow = mobileMenuOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [mobileMenuOpen]);

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/prayers', label: 'Prayers' },
    { path: '/daily-saint', label: 'Saint of the Day' },
    { path: '/mass-map', label: 'Mass Map' },
    { path: '/store', label: 'Store' },
    { path: '/about', label: 'About' },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className={`header ${scrolled ? 'header-scrolled' : ''}`} data-testid="header">
      <div className="header-container">
        <Link to="/" className="logo-link" data-testid="logo-link">
          <div className="logo-text">
            <span className="logo-main">Catholic Voices</span>
            <span className="logo-sub">& Prayers</span>
          </div>
        </Link>
        
        <nav className="nav-desktop">
          {navItems.map((item) => (
            <Link 
              key={item.path}
              to={item.path} 
              className={`nav-link ${isActive(item.path) ? 'nav-link-active' : ''}`}
              data-testid={`nav-link-${item.path.replace('/', '') || 'home'}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <button 
          className={`menu-toggle ${mobileMenuOpen ? 'menu-open' : ''}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
          data-testid="menu-toggle"
        >
          <span className="menu-bar"></span>
          <span className="menu-bar"></span>
        </button>
      </div>

      <div className={`nav-mobile ${mobileMenuOpen ? 'nav-mobile-open' : ''}`}>
        <nav className="nav-mobile-inner">
          {navItems.map((item) => (
            <Link 
              key={item.path}
              to={item.path} 
              className={`nav-mobile-link ${isActive(item.path) ? 'nav-mobile-link-active' : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      {mobileMenuOpen && (
        <div className="nav-mobile-overlay" onClick={() => setMobileMenuOpen(false)} />
      )}
    </header>
  );
};

export default Header;
