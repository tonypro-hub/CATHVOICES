import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Prayers from './pages/Prayers';
import PrayerDetail from './pages/PrayerDetail';
import SaintsFeasts from './pages/SaintsFeasts';
import Daily from './pages/Daily';
import DailySaint from './pages/DailySaint';
import SaintsArchive from './pages/SaintsArchive';
import MassMap from './pages/MassMap';
import SspxExplained from './pages/SspxExplained';
import Store from './pages/Store';
import StoreCategory from './pages/StoreCategory';
import About from './pages/About';
import './styles/variables.css';
import './styles/global.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            {/* Core Pages */}
            <Route path="/" element={<Home />} />
            <Route path="/prayers" element={<Prayers />} />
            <Route path="/prayers/:id" element={<PrayerDetail />} />
            
            {/* Saints & Feasts */}
            <Route path="/saints-feasts" element={<SaintsFeasts />} />
            <Route path="/saints-feasts/saints" element={<SaintsFeasts />} />
            <Route path="/saints-feasts/calendar" element={<SaintsFeasts />} />
            
            {/* Daily Saint System */}
            <Route path="/daily-saint" element={<DailySaint />} />
            <Route path="/saints-archive" element={<SaintsArchive />} />
            <Route path="/saints/:id" element={<DailySaint />} />
            
            {/* Daily */}
            <Route path="/daily" element={<Daily />} />
            <Route path="/daily/saint" element={<Daily />} />
            <Route path="/daily/feast" element={<Daily />} />
            
            {/* Store */}
            <Route path="/store" element={<Store />} />
            <Route path="/store/:categoryId" element={<StoreCategory />} />
            
            {/* Additional Pages */}
            <Route path="/mass-map" element={<MassMap />} />
            <Route path="/sspx-explained" element={<SspxExplained />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
