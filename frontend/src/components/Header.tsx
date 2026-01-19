import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (mobileMenuOpen && !target.closest('.nav') && !target.closest('.mobile-menu-toggle')) {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [mobileMenuOpen]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
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
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <header className="header">
      <div className="container header-content">
        <Link to="/" className="logo-link">
          <img 
            src="/assets/brand/logo-white.png" 
            alt="Catholic Voices and Prayers" 
            className="logo"
          />
        </Link>
        
        {/* Hamburger Menu Button */}
        <button 
          className={`mobile-menu-toggle ${mobileMenuOpen ? 'menu-open' : ''}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
          aria-expanded={mobileMenuOpen}
        >
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>
        
        {/* Navigation */}
        <nav className={`nav ${mobileMenuOpen ? 'nav-open' : ''}`}>
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

        {/* Mobile Menu Overlay */}
        {mobileMenuOpen && <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)} />}
      </div>
    </header>
  );
};

export default Header;
