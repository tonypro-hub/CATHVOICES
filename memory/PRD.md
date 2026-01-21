# Catholic Voices & Prayers - Product Requirements Document

## Original Problem Statement
Build a desktop-first, SEO-driven, reverent Catholic website called "Catholic Voices and Prayers" with:
- Traditional Catholic design inspired by PelicanPlus.com
- Daily Saints system with YouTube API integration
- Interactive Mass Map with location finder
- Prayers page with categorized content
- Affiliate store for Catholic products
- Custom branding with user-provided logos

## Tech Stack
- **Frontend**: React (CRA), React Router, Leaflet.js
- **Backend**: FastAPI, Motor (async MongoDB), APScheduler
- **Database**: MongoDB
- **Design**: Desktop-first, responsive, PelicanPlus-inspired

## Core Features

### 1. Daily Saints System ✅ COMPLETE
- YouTube Data API integration for "Daily Lives of the Saints" playlist
- APScheduler job runs daily at 3:15 PM CST
- Automatically fetches YouTube Shorts (≤ 3 min) published after 3:00 PM CST
- Archives all saints for browsing
- API Endpoints:
  - `GET /api/saints/today` - Current saint of the day
  - `GET /api/saints/archive` - All past saints
  - `POST /api/saints/refresh` - Manual trigger

### 2. Mass Map ✅ COMPLETE (January 21, 2026)
- **309 total locations** across 49+ US states
- Interactive Leaflet map with OpenStreetMap tiles
- **"Find Nearby" Geolocation Feature** - Uses browser GPS to find masses near user
  - Adjustable radius (10, 25, 50, 100, 200 miles)
  - Shows distance in miles for each location
  - User location marker on map
- **Favorites Feature** - Save preferred locations to localStorage (no login required)
  - Heart icon toggle on cards, popups, and detail view
  - "My Favorites" filter shows saved locations
  - Persists across browser sessions
- Filter by affiliation:
  - SSPX: 119 locations
  - Eastern Catholic: 104 locations
  - Ordinariate: 39 locations
  - ICKSP: 27 locations (from web scraper)
  - FSSP: 19 locations (from web scraper)
  - Diocesan: 1 location
- Filter by state (49 states covered)
- Search by city, state, or parish name
- Location detail view with address, website link, directions
- Excludes sedevacantist groups (CMRI, SSPV, etc.)
- **Web Scraper** - Manual script to fetch locations from ICKSP and FSSP websites
- API Endpoints:
  - `GET /api/mass-locations` - All locations with filters
  - `GET /api/mass-locations/stats` - Statistics
  - `GET /api/mass-locations/filters` - Available filter options
  - `GET /api/mass-locations/search` - Search endpoint (supports lat/lng/radius)
  - `GET /api/mass-locations/{id}` - Location detail
  - `POST /api/mass-locations/scrape` - Trigger web scraper (manual)

### 3. Prayers Page ✅ COMPLETE
- Categorized prayer content
- API Endpoints:
  - `GET /api/prayers` - All prayers
  - `POST /api/prayers` - Create prayer
  - `GET /api/prayers/{id}` - Get specific prayer

### 4. Store Page ✅ COMPLETE
- Affiliate product listings
- Categories for Catholic products
- API Endpoints:
  - `GET /api/store/products` - All products

### 5. Static Pages ✅ COMPLETE
- Home page with hero section
- About page
- SSPX Explained page

## Branding ✅ COMPLETE
- Custom dark red logo in header
- Custom white logo in footer
- "Made with Emergent" badge removed

## Database Schema

### `daily_saints`
```json
{
  "id": "uuid",
  "videoId": "string",
  "saintName": "string",
  "feastDate": "YYYY-MM-DD",
  "description": "string",
  "thumbnail": "url",
  "youtubeUrl": "url",
  "publishedAt": "ISO datetime",
  "isActive": "boolean"
}
```

### `mass_locations`
```json
{
  "id": "uuid",
  "name": "string",
  "entity_type": "Parish|Chapel|Community|Cathedral",
  "affiliation": "SSPX|Eastern Catholic|Ordinariate|FSSP|ICKSP|Diocesan",
  "rite": "Latin|Byzantine|Ukrainian|Melkite|Chaldean|Maronite",
  "use_or_liturgy": "1962 Roman Missal|Divine Liturgy|Ordinariate Use",
  "street": "string",
  "city": "string",
  "state": "string (2-letter)",
  "zip_code": "string",
  "country": "USA",
  "latitude": "float",
  "longitude": "float",
  "website_url": "url (optional)",
  "notes": "string (optional)",
  "exclude_flag": "boolean",
  "created_at": "ISO datetime"
}
```

## Completed Milestones
- [x] Backend API structure with FastAPI
- [x] MongoDB integration
- [x] Daily Saints automation with YouTube API
- [x] APScheduler for daily updates
- [x] Frontend React app with all pages
- [x] PelicanPlus design implementation
- [x] Custom logo integration
- [x] Mass Map with 309 locations
- [x] All affiliate types covered (SSPX, Eastern Catholic, Ordinariate, ICKSP, FSSP)
- [x] Testing completed (18+ tests passing)
- [x] **"Find Nearby" geolocation feature** - GPS-based mass finder
- [x] **Favorites feature** - localStorage-based saved locations
- [x] **Dynamic SEO** - Page-specific meta tags with react-helmet-async
- [x] **Social sharing buttons** - Facebook, X/Twitter, Copy link on Daily Saint
- [x] **Web Scraper** - ICKSP and FSSP location scraper (manual trigger)

## Future Tasks (Backlog)
1. **P1**: Web scraper to find additional mass locations
2. **P2**: Dynamic SEO (page-specific titles/meta descriptions)
3. **P2**: Social sharing buttons on Daily Saint pages
4. **P3**: User authentication for saved locations
5. **P3**: Email notifications for daily saints

## 3rd Party Integrations
- **YouTube Data API v3**: Daily Saints feature (API key in backend/.env)
- **OpenStreetMap/Leaflet**: Mass Map tiles (no API key required)

## File Structure
```
/app/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── .env               # Environment variables (MONGO_URL, YOUTUBE_API_KEY)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Header, Footer, etc.
│   │   ├── pages/         # Home, DailySaint, MassMap, etc.
│   │   └── styles/        # CSS files
│   └── .env               # REACT_APP_BACKEND_URL
├── scripts/
│   └── add_locations.py   # Location import script
└── tests/
    └── test_mass_locations.py  # Backend API tests
```

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial testing
- `/app/test_reports/iteration_2.json` - Mass Map testing (26 tests passed)
