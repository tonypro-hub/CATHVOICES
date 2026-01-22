import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import DailySaint from './pages/DailySaint';
import SaintsArchive from './pages/SaintsArchive';
import MassMap from './pages/MassMap';
import SspxExplained from './pages/SspxExplained';
import Store from './pages/Store';
import About from './pages/About';
import { AuthProvider, useAuth } from './context/AuthContext';
import AdminLogin from './pages/admin/AdminLogin';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminLocations from './pages/admin/AdminLocations';
import AdminLocationEdit from './pages/admin/AdminLocationEdit';
import AdminSuggestions from './pages/admin/AdminSuggestions';
// New Prayer Pages
import { 
  PrayersHome, 
  RosaryPage, 
  NovenasPage, 
  DevotionsPage, 
  FultonSheenPage,
  SaintsPage,
  TeachingsPage, 
  PrayerVideoPage 
} from './pages/prayers';
// New Teachings Pages
import TeachingsHome from './pages/teachings/TeachingsHome';
import TeachingsCategoryPage from './pages/teachings/TeachingsCategoryPage';
import TeachingsVideoPage from './pages/teachings/TeachingsVideoPage';
import './styles/variables.css';
import './styles/global.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div style={{ padding: '100px', textAlign: 'center' }}>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }
  
  return children;
};

function AppContent() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Admin Routes (no header/footer) */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/dashboard" element={
          <ProtectedRoute><AdminDashboard /></ProtectedRoute>
        } />
        <Route path="/admin/locations" element={
          <ProtectedRoute><AdminLocations /></ProtectedRoute>
        } />
        <Route path="/admin/locations/:id" element={
          <ProtectedRoute><AdminLocationEdit /></ProtectedRoute>
        } />
        <Route path="/admin/suggestions" element={
          <ProtectedRoute><AdminSuggestions /></ProtectedRoute>
        } />
        <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
        
        {/* Public Routes (with header/footer) */}
        <Route path="/*" element={
          <div className="app">
            <Header />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Home />} />
                {/* Prayer Library Routes */}
                <Route path="/prayers" element={<PrayersHome />} />
                <Route path="/prayers/rosary" element={<RosaryPage />} />
                <Route path="/prayers/novenas" element={<NovenasPage />} />
                <Route path="/prayers/devotions" element={<DevotionsPage />} />
                <Route path="/prayers/fulton-sheen" element={<FultonSheenPage />} />
                <Route path="/prayers/saints" element={<SaintsPage />} />
                <Route path="/prayers/teachings" element={<TeachingsPage />} />
                <Route path="/prayers/video/:videoId" element={<PrayerVideoPage />} />
                {/* Catholic Teachings Routes */}
                <Route path="/teachings" element={<TeachingsHome />} />
                <Route path="/teachings/:categoryId" element={<TeachingsCategoryPage />} />
                <Route path="/teachings/video/:videoId" element={<TeachingsVideoPage />} />
                {/* Daily Saints */}
                <Route path="/daily-saint" element={<DailySaint />} />
                <Route path="/saints-archive" element={<SaintsArchive />} />
                <Route path="/saints/:id" element={<DailySaint />} />
                {/* Other Pages */}
                <Route path="/mass-map" element={<MassMap />} />
                <Route path="/sspx-explained" element={<SspxExplained />} />
                <Route path="/store" element={<Store />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </main>
            <Footer />
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  return (
    <HelmetProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
