# Catholic Voices & Prayers - Product Requirements Document

## Original Problem Statement
Build a desktop-first, SEO-driven, reverent Catholic website called "Catholic Voices and Prayers" with:
- Traditional Catholic design inspired by PelicanPlus.com
- Daily Saints system with YouTube API integration
- Interactive Mass Map with location finder
- Prayers page with categorized content
- Affiliate store for Catholic products
- Custom branding with user-provided logos
- **Admin Management**: Protected admin area to manage mass locations
- **User Suggestions**: Public form for users to suggest new locations or edits

## Tech Stack
- **Frontend**: React (CRA), React Router, Leaflet.js, react-helmet-async
- **Backend**: FastAPI, Motor (async MongoDB), APScheduler, JWT (python-jose), bcrypt (passlib)
- **Database**: MongoDB
- **Email**: Resend API (for suggestion notifications)
- **Design**: Desktop-first, responsive, PelicanPlus-inspired

## Core Features

### 1. Daily Saints System ✅ COMPLETE
- YouTube Data API integration for "Daily Lives of the Saints" playlist
- APScheduler job runs daily at 3:15 PM CST
- Automatically fetches YouTube Shorts (≤ 3 min) published after 3:00 PM CST
- Archives all saints for browsing
- Social sharing buttons (Facebook, X/Twitter, Copy link)

### 2. Mass Map ✅ COMPLETE
- **413 total locations** across US and Canada
- Interactive Leaflet map with OpenStreetMap tiles
- **"Find Nearby" Geolocation Feature** - Uses browser GPS to find masses near user
- **Favorites Feature** - Save preferred locations to localStorage
- Filter by affiliation (SSPX, Diocesan, Eastern Catholic, Ordinariate, ICKSP, FSSP)
- Filter by state/province
- Search by city, state, or parish name
- Location detail view with address, website link, directions

### 3. Admin Management ✅ COMPLETE (January 21, 2026)
- **JWT Authentication** - Secure admin login with token-based auth
  - Username: `admin` / Password: `changeme`
- **Admin Dashboard** - Overview with stats and quick actions
  - Total locations count
  - Pending suggestions count
  - Affiliation breakdown
- **Location Management** - Full CRUD operations
  - Paginated list with search/filter
  - Edit location details
  - Create new locations
  - Soft delete locations
- **Suggestion Review** - Review and act on user submissions
  - Pending/Approved/Rejected tabs
  - Approve to apply changes or create location
  - Reject to dismiss
  - View submission details
- **Protected Routes** - AuthContext with token verification
  - `/admin/login` - Login page
  - `/admin/dashboard` - Dashboard (protected)
  - `/admin/locations` - Location management (protected)
  - `/admin/locations/:id` - Edit location (protected)
  - `/admin/locations/new` - Add location (protected)
  - `/admin/suggestions` - Review suggestions (protected)

### 4. User Suggestion System ✅ COMPLETE (January 21, 2026)
- **Public Suggestion Form** - Modal on Mass Map page
  - "Suggest a Location" button in filters section
  - "Suggest Edit" button in location detail view
- **Quick Report Issue** - Simplified form for reporting problems
  - "Report Issue" button in map popup and detail view
  - Issue type dropdown (Incorrect Info, Wrong Address, Wrong Times, Location Closed, Other)
  - Description field and optional email
- **Submission Fields**:
  - User info: Name, Email (required)
  - Location: Name, Affiliation, Rite, Address, City, State
  - Mass info: Times, Website, Phone, Notes
  - Reason for suggestion
- **Anti-spam** - Honeypot field
- **Email Notifications** - Sends notification to admin when new suggestion submitted
  - Requires Resend API key configuration (currently empty)

### 5. Prayers Page ✅ REBUILT (January 21, 2026)
- **Complete Prayer Library Architecture**:
  - `/prayers` - Main hub with featured Fulton Sheen banner and category navigation
  - `/prayers/saints` - Lives of the Saints videos
  - `/prayers/teachings` - Catholic Teachings videos
  - `/prayers/devotions` - Prayers & Devotions videos
  - `/prayers/fulton-sheen` - Featured Bishop Sheen section
  - `/prayers/video/:id` - Individual prayer video page with YouTube embed
- **YouTube Integration**: Connected to "Catholic Voices & Prayers" channel (UCRRPmmYLLHxRJlsKjJER1Ig), 200+ videos categorized
- **Featured Banner**: Bishop Fulton J. Sheen banner with full-bleed image and floating text overlay ✅ (January 21, 2026)
- **Design**: Reverent, PelicanPlus-style with calm typography and devotional spacing

### 6. Store Page ✅ COMPLETE
- Affiliate product listings
- Categories for Catholic products

### 7. Static Pages ✅ COMPLETE
- Home page with hero section
- About page
- SSPX Explained page (expanded with Q&A and quotes)

## API Endpoints

### Public Endpoints
- `GET /api/saints/today` - Current saint of the day
- `GET /api/saints/archive` - All past saints
- `GET /api/mass-locations` - All locations with filters
- `GET /api/mass-locations/stats` - Statistics
- `GET /api/mass-locations/filters` - Available filter options
- `GET /api/mass-locations/search` - Search (supports lat/lng/radius)
- `POST /api/suggestions` - Submit suggestion

### Admin Endpoints (Protected)
- `POST /api/admin/login` - Login and get JWT token
- `GET /api/admin/me` - Verify token
- `GET /api/admin/locations` - Paginated location list with search/filter
- `GET /api/admin/locations/:id` - Get location for editing
- `POST /api/admin/locations` - Create location
- `PUT /api/admin/locations/:id` - Update location
- `DELETE /api/admin/locations/:id` - Soft delete location
- `GET /api/admin/suggestions` - List suggestions with status filter
- `GET /api/admin/suggestions/:id` - Get suggestion details
- `PUT /api/admin/suggestions/:id?action=approve|reject` - Act on suggestion
- `DELETE /api/admin/suggestions/:id` - Delete suggestion

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
  "location_id": "uuid",
  "name": "string",
  "entity_type": "Parish|Chapel|Community|Cathedral",
  "affiliation": "SSPX|Eastern Catholic|Ordinariate|FSSP|ICKSP|Diocesan",
  "rite": "Latin|Byzantine|Ukrainian|Melkite|Chaldean|Maronite",
  "use_or_liturgy": "1962 Roman Missal|Divine Liturgy|Ordinariate Use",
  "street": "string",
  "city": "string",
  "state": "string (2-letter)",
  "zip_code": "string",
  "country": "USA|Canada",
  "latitude": "float",
  "longitude": "float",
  "website_url": "url (optional)",
  "notes": "string (optional)",
  "exclude_flag": "boolean",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "updated_by": "string"
}
```

### `location_suggestions`
```json
{
  "id": "uuid",
  "suggestion_type": "new|edit",
  "location_id": "uuid (for edits)",
  "user_email": "email",
  "user_name": "string",
  "name": "string",
  "street": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "country": "string",
  "affiliation": "string",
  "rite": "string",
  "mass_schedule": "string",
  "website_url": "string",
  "phone": "string",
  "notes": "string",
  "reason": "string",
  "status": "pending|approved|rejected",
  "created_at": "ISO datetime",
  "reviewed_at": "ISO datetime",
  "reviewed_by": "string"
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
- [x] Mass Map with 413 locations (US + Canada)
- [x] All affiliate types covered (SSPX, Diocesan, Eastern Catholic, Ordinariate, ICKSP, FSSP)
- [x] "Find Nearby" geolocation feature
- [x] Favorites feature (localStorage)
- [x] Dynamic SEO with react-helmet-async
- [x] Social sharing buttons on Daily Saint
- [x] Web Scraper (ICKSP and FSSP)
- [x] Diocesan Data Ingestion (105 Latin Mass locations)
- [x] **Admin Login with JWT authentication** (January 21, 2026)
- [x] **Admin Dashboard with stats and quick actions** (January 21, 2026)
- [x] **Admin Location Management (CRUD)** (January 21, 2026)
- [x] **Admin Suggestion Review (approve/reject)** (January 21, 2026)
- [x] **User Suggestion Form on Mass Map** (January 21, 2026)
- [x] **Protected Routes with AuthContext** (January 21, 2026)

- [x] **Quick Report Issue button on map popup and detail view** (January 21, 2026)
- [x] **Mass Times display in location cards, popups, and detail view** (January 21, 2026)
- [x] **"Mass Times Unknown" indicator with "Submit Times" CTA button** (January 21, 2026)
- [x] **Admin Bulk Upload for Mass Times (CSV import)** (January 21, 2026)
- [x] **Prayer Library rebuilt with YouTube channel integration** (January 21, 2026)
- [x] **Fulton Sheen featured banner with floating text design** (January 21, 2026)

## Future Tasks (Backlog)
1. **P2**: Mass times data integration (API or manual entry)
2. **P2**: Configure Resend API for email notifications (requires API key)
3. **P3**: User authentication for cloud-synced favorites
4. **P3**: Email notifications for daily saints
5. **P3**: Server-side rendering (SSR) for full SEO meta tag support

## 3rd Party Integrations
- **YouTube Data API v3**: Daily Saints feature
- **OpenStreetMap/Leaflet**: Mass Map tiles
- **Resend**: Email notifications (NOT configured - requires API key)

## Admin Credentials
- **Username**: `admin`
- **Password**: `changeme`
- **Access**: `/admin/login`

## Test Reports
- `/app/test_reports/iteration_1.json` - Initial testing
- `/app/test_reports/iteration_2.json` - Mass Map testing
- `/app/test_reports/iteration_3.json` - Web scraping feature
- `/app/test_reports/iteration_4.json` - Admin & Suggestions testing (96% backend, 100% frontend)

## File Structure
```
/app/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── .env               # Environment variables
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Header, Footer, SEO
│   │   ├── context/       # AuthContext.js
│   │   ├── pages/         # Public pages
│   │   │   └── admin/     # Admin pages (Login, Dashboard, Locations, Suggestions)
│   │   └── styles/        # CSS files
│   └── .env               # REACT_APP_BACKEND_URL
├── scripts/
│   ├── add_locations.py
│   ├── scrape_locations.py
│   └── ingest_diocesan_data.py
└── tests/
    └── test_admin_features.py
```
