import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = mobileMenuOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [mobileMenuOpen]);

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/prayers', label: 'Prayers' },
    { path: '/saints-feasts', label: 'Saints & Feasts' },
    { path: '/daily', label: 'Daily' },
    { path: '/mass-map', label: 'Mass Map' },
    { path: '/store', label: 'Store' },
    { path: '/about', label: 'About' },
  ];

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className={`header ${scrolled ? 'header-scrolled' : ''}`}>
      <div className="header-container">
        {/* Logo */}
        <Link to="/" className="logo-link">
          <img src="/logo.png" alt="Catholic Voices & Prayers" className="logo-image" />
        </Link>
        
        {/* Desktop Navigation */}
        <nav className="nav-desktop">
          {navItems.map((item) => (
            <Link 
              key={item.path}
              to={item.path} 
              className={`nav-link ${isActive(item.path) ? 'nav-link-active' : ''}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Mobile Menu Toggle */}
        <button 
          className={`menu-toggle ${mobileMenuOpen ? 'menu-open' : ''}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
          aria-expanded={mobileMenuOpen}
        >
          <span className="menu-bar"></span>
          <span className="menu-bar"></span>
        </button>
      </div>

      {/* Mobile Navigation */}
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

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div 
          className="nav-mobile-overlay" 
          onClick={() => setMobileMenuOpen(false)} 
        />
      )}
    </header>
  );
};

export default Header;
