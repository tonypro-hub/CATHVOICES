import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Prayers from './pages/Prayers';
import PrayerDetail from './pages/PrayerDetail';
import DailySaint from './pages/DailySaint';
import SaintsArchive from './pages/SaintsArchive';
import MassMap from './pages/MassMap';
import SspxExplained from './pages/SspxExplained';
import Store from './pages/Store';
import About from './pages/About';
import './styles/variables.css';
import './styles/global.css';

function App() {
  return (
    <HelmetProvider>
      <BrowserRouter>
        <div className="app">
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/prayers" element={<Prayers />} />
              <Route path="/prayers/:id" element={<PrayerDetail />} />
              <Route path="/daily-saint" element={<DailySaint />} />
              <Route path="/saints-archive" element={<SaintsArchive />} />
              <Route path="/saints/:id" element={<DailySaint />} />
              <Route path="/mass-map" element={<MassMap />} />
              <Route path="/sspx-explained" element={<SspxExplained />} />
              <Route path="/store" element={<Store />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </HelmetProvider>
  );
}

export default App;
