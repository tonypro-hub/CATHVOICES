# Catholic Voices & Prayers - Mobile App

A beautiful, reverent mobile-first Catholic prayer and devotional app built with Expo, React Native, FastAPI, and MongoDB.

## 🎨 Features Implemented (Phase 1)

### ✅ Global Site Foundation
- **Brand Identity**: Deep burgundy (#8B0000) and gold (#D4AF37) color scheme
- **Logo Integration**: Jerusalem Cross logo on all pages (white version on dark backgrounds)
- **Consistent Navigation**: Stack-based navigation optimized for mobile
- **Typography**: Large, readable fonts optimized for prayer reading
- **Social Media Links**: All 5 platforms integrated (YouTube, Instagram, TikTok, Twitter/X, Facebook)

### ✅ YouTube Content Integration
- **Dynamic Video Fetching**: Automatically fetches long-form videos from YouTube Channel
- **Video Caching**: Videos cached in MongoDB to reduce API calls
- **Embedded Player**: YouTube videos embedded using WebView (works on iOS, Android, and Web)
- **18 Videos Cached**: Bishop Fulton Sheen Rosary series and novenas

### ✅ Prayers Section
- **Prayer List**: Beautiful card-based list of all prayers
- **Prayer Detail Pages**: 
  - YouTube video at top
  - Full prayer text with reverent typography
  - Copy to clipboard functionality
  - Category labels
- **5 Sample Prayers**:
  - The Holy Rosary
  - Holy Cloak of St. Joseph 30-Day Novena
  - The Our Father
  - The Hail Mary
  - Glory Be (Doxology)

### ✅ About Page
- Mission statement
- Features overview
- Social media integration with clickable links

## 🛠 Tech Stack

### Frontend (Mobile)
- **Expo SDK 54** - Cross-platform mobile framework
- **React Native** - Native mobile components
- **Expo Router** - File-based routing
- **TypeScript** - Type safety
- **React Navigation** - Native stack navigation
- **Axios** - HTTP client
- **React Native WebView** - YouTube video embedding
- **@react-native-clipboard/clipboard** - Copy functionality

### Backend
- **FastAPI** - Modern Python web framework
- **Motor** - Async MongoDB driver
- **YouTube Data API v3** - Video fetching
- **Pydantic** - Data validation

### Database
- **MongoDB** - NoSQL database
- Collections: `prayers`, `videos`

## 📁 Project Structure

```
app/
├── backend/
│   ├── server.py          # FastAPI server with YouTube integration
│   ├── .env               # Environment variables (YouTube API key)
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── _layout.tsx    # Root navigation layout
│   │   ├── index.tsx      # Home screen
│   │   ├── about.tsx      # About page
│   │   └── prayers/
│   │       ├── index.tsx  # Prayers list
│   │       └── [id].tsx   # Prayer detail (dynamic route)
│   ├── assets/
│   │   └── images/
│   │       └── brand/     # Logo variations
│   ├── package.json
│   └── .env
└── add_prayer.py          # Utility script to add prayers
```

## 🚀 API Endpoints

### YouTube Integration
- `GET /api/videos/refresh` - Fetch and cache videos from YouTube
- `GET /api/videos` - Get all cached videos
- `GET /api/videos/{videoId}` - Get specific video

### Prayers CRUD
- `GET /api/prayers` - Get all prayers
- `GET /api/prayers/{id}` - Get specific prayer
- `POST /api/prayers` - Create new prayer
- `DELETE /api/prayers/{id}` - Delete prayer

## 📱 Mobile-First Design

### Brand Colors
```typescript
{
  burgundy: '#8B0000',  // Primary brand color
  gold: '#D4AF37',      // Accent color
  cream: '#F5F5DC',     // Text on dark backgrounds
  dark: '#1A1A1A',      // Background
  white: '#FFFFFF'      // Logo and text
}
```

### Typography
- **Prayer Text**: 18px, line-height 32px, letter-spacing 0.3
- **Headings**: 28px bold for prayer titles
- **Body**: 16px for descriptions and body text

### Navigation
- Stack-based navigation (linear flow)
- Burgundy header with cream text
- Back button navigation on all sub-pages

## 🎯 How to Add More Prayers

### Method 1: Using the Python Script
```bash
python /app/add_prayer.py
```

### Method 2: Using curl
```bash
curl -X POST "http://localhost:8001/api/prayers" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prayer Name",
    "videoId": "YouTube_Video_ID",
    "prayerText": "Full prayer text here...",
    "category": "Category Name"
  }'
```

### Method 3: Direct Database Insert
Connect to MongoDB and insert into the `prayers` collection.

## 📊 Current Status

### ✅ Completed
- [x] Global design system and branding
- [x] YouTube API integration (18 videos cached)
- [x] Prayer CRUD operations (5 sample prayers)
- [x] Mobile navigation (Home → Prayers → Detail → About)
- [x] Copy to clipboard functionality
- [x] Social media integration
- [x] Responsive mobile design
- [x] Backend API (100% tested and working)

### 🔄 Future Enhancements (Not in Phase 1)
- [ ] Feast days calendar
- [ ] Saints directory
- [ ] User accounts and favorites
- [ ] Audio-only prayers
- [ ] Daily prayer reminders
- [ ] E-commerce for prayer books
- [ ] Community forums

## 🔑 Environment Variables

### Backend (.env)
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
YOUTUBE_API_KEY="AIzaSyDIgXbeKLC1ga678hpxsMQsKG8Q9mUmJDg"
YOUTUBE_CHANNEL_ID="UCRRPmmYLLHxRJlsKjJER1Ig"
```

### Frontend (.env)
```
EXPO_TUNNEL_SUBDOMAIN=mass-locator
EXPO_PACKAGER_HOSTNAME=https://mass-locator.preview.emergentagent.com
EXPO_PUBLIC_BACKEND_URL=https://mass-locator.preview.emergentagent.com
```

## 🌐 Social Media Links

- **YouTube**: https://www.youtube.com/@CatholicVoicesPrayers
- **Instagram**: https://www.instagram.com/catholic_voices/
- **TikTok**: https://www.tiktok.com/@catholicvoicesprayers
- **Twitter/X**: https://x.com/CatholicVoices1
- **Facebook**: https://www.facebook.com/p/Catholic-Voices-Prayers-61558676517811/

## 📝 Testing Results

### Backend Testing: ✅ 100% Pass Rate
- ✅ YouTube video refresh API
- ✅ Get cached videos API
- ✅ Get video by ID API
- ✅ Get all prayers API
- ✅ Get prayer by ID API
- ✅ Create prayer API
- ✅ Delete prayer API
- ✅ Root endpoint

All 8 backend endpoints tested and working perfectly.

## 🎨 Design Philosophy

This app follows Catholic design principles:
- **Reverent**: Respectful, contemplative design
- **Minimal**: No clutter or distractions
- **Timeless**: Classic colors and typography
- **Readable**: Large text optimized for prayer
- **Accessible**: Mobile-first, easy to navigate

## 📞 Support

For questions about adding content or modifying the app, refer to:
- Backend API docs: `GET /api/` 
- Frontend structure: `/app/frontend/app/`
- Utility scripts: `/app/add_prayer.py`

---

**May this app bring peace and spiritual growth to all who use it.** ✟
