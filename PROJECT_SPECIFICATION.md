# Catholic Voices & Prayers - Project Specification

## ⚠️ ARCHITECTURE LOCK - READ FIRST

**🔒 This project's architecture is LOCKED to prevent unintended changes.**

**Before making ANY structural changes, consult: `/app/ARCHITECTURE_LOCK.md`**

Key Locked Rules:
- ✅ This IS a responsive desktop website (NOT a mobile app)
- ✅ Long-form videos (>3 min) are PRIMARY content
- ✅ Shorts (≤3 min) are SECONDARY content only
- ✅ YouTube is the single source of truth
- ❌ DO NOT reintroduce app-style UI patterns
- ❌ DO NOT mix Shorts into primary prayer libraries

---

## ⚠️ CRITICAL PROJECT TYPE DEFINITION

**THIS IS A RESPONSIVE DESKTOP WEBSITE - NOT A MOBILE APP**

### Project Type: DESKTOP-FIRST RESPONSIVE WEBSITE

- **Primary Platform:** Desktop web browsers (Chrome, Firefox, Safari, Edge)
- **Secondary Platform:** Mobile web browsers (responsive design)
- **Technology:** Vite + React + TypeScript + React Router
- **Deployment:** Web hosting (NOT app stores)
- **Access Method:** Web URL in browser (NOT native app installation)

---

## 🚫 PROHIBITED PATTERNS

**DO NOT** reintroduce these mobile app patterns:

- ❌ Expo / React Native framework
- ❌ Native mobile components (View, Text, TouchableOpacity, etc.)
- ❌ Bottom tab navigation bars
- ❌ Stack navigation (mobile app style)
- ❌ App-style UI patterns
- ❌ Native mobile gestures
- ❌ App store deployment considerations
- ❌ PWA (Progressive Web App) patterns unless explicitly requested

---

## ✅ REQUIRED PATTERNS

**ALWAYS USE** these web patterns:

- ✅ Standard HTML5 semantic elements (div, nav, header, footer, section)
- ✅ Traditional website navigation (horizontal nav bar in header)
- ✅ Desktop-first CSS with responsive breakpoints
- ✅ React Router for web routing
- ✅ Standard web forms and inputs
- ✅ CSS Grid / Flexbox for layouts
- ✅ Web-standard interactions (hover states, click events)
- ✅ Browser-based functionality

---

## 🎨 Design Approach

### Desktop-First Responsive Design

1. **Desktop (1200px+):** Primary design target
   - Full-width layouts
   - Multi-column grids
   - Horizontal navigation bar
   - Large typography and imagery
   - Hover effects and interactions

2. **Tablet (768px - 1199px):** Adapted layout
   - Reduced columns
   - Adjusted spacing
   - Maintained horizontal nav or simplified version

3. **Mobile (< 768px):** Responsive adaptation
   - Single column layouts
   - Hamburger menu navigation
   - Touch-friendly buttons (44px+)
   - Stacked content

**Important:** Mobile view is a responsive adaptation, NOT a mobile app UI.

---

## 📁 Technology Stack

### Frontend
- **Framework:** React 19
- **Build Tool:** Vite 7.x
- **Routing:** React Router v6
- **Language:** TypeScript
- **Styling:** CSS3 with CSS Variables
- **State:** React Hooks (useState, useEffect)

### Backend
- **Framework:** FastAPI (Python)
- **Database:** MongoDB
- **API:** RESTful JSON endpoints
- **External:** YouTube Data API v3

### Development
- **Dev Server:** Vite dev server (port 3000)
- **Hot Reload:** Vite HMR
- **Process Manager:** Supervisor

---

## 🎨 Brand & Design System

### Color Scheme: Black/Burgundy/Gold
- **Black:** #000000 (primary backgrounds)
- **Dark Black:** #0a0a0a (card backgrounds)
- **Burgundy:** #8B0000 (accents, borders, highlights)
- **Gold:** #D4AF37 (CTAs, text highlights, icons)
- **Cream:** #F5F5DC (body text on dark backgrounds)
- **White:** #FFFFFF (headings, logo)

### Typography
- **Primary Font:** System sans-serif stack
- **Prayer Text Font:** Georgia, Times New Roman (serif)
- **Headings:** 2rem - 4rem (desktop), responsive scaling
- **Body Text:** 1rem - 1.25rem, line-height 1.6-1.8
- **Prayer Text:** 1.25rem, line-height 2 (extra spacing for readability)

### Layout Inspiration
- **Design Reference:** Hallow.com layout structure
- **Pattern:** Hero section, feature cards, horizontal scrolling content, category grids, large CTAs

---

## 📄 Page Structure

### Current Pages
1. **Home (/):** Hero, features, prayers preview, categories, CTAs
2. **Prayers (/prayers):** Grid of all prayers with categories
3. **Prayer Detail (/prayers/:id):** YouTube video + full prayer text + copy button
4. **About (/about):** Mission, features, social media links

### Navigation Structure
```
Header (Sticky)
├── Logo (left)
└── Navigation (right)
    ├── Home
    ├── Prayers
    └── About

Footer
├── Description
├── Social Media Links
└── Copyright
```

---

## 🔗 API Integration

### YouTube Data API
- **Purpose:** Fetch long-form prayer videos from channel
- **Channel ID:** UCRRPmmYLLHxRJlsKjJER1Ig
- **Caching:** Videos cached in MongoDB
- **Endpoint:** /api/videos/refresh

### Prayer Management
- **Endpoints:**
  - GET /api/prayers - List all prayers
  - GET /api/prayers/:id - Get single prayer
  - POST /api/prayers - Create prayer
  - DELETE /api/prayers/:id - Delete prayer

---

## 🚀 Development Commands

```bash
# Start frontend (Vite dev server)
cd /app/frontend
npm run dev

# Start backend (FastAPI)
cd /app/backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Supervisor commands
sudo supervisorctl status
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
```

---

## 📝 Future Development Guidelines

When making changes or adding features:

1. **Always use web-standard technologies** (HTML, CSS, JavaScript/TypeScript)
2. **Maintain desktop-first responsive approach** (design for desktop, adapt to mobile)
3. **Use semantic HTML5 elements** (not React Native components)
4. **Keep traditional website navigation patterns** (header nav, not app tabs)
5. **Preserve Black/Burgundy/Gold color scheme**
6. **Follow Hallow.com-inspired layout patterns**
7. **Test on desktop browsers first**, then verify mobile responsiveness

---

## ⚡ Performance Considerations

- **Vite HMR:** Hot module replacement for fast development
- **Code Splitting:** React Router automatically splits routes
- **Image Optimization:** Use appropriate image formats and sizes
- **API Caching:** YouTube videos cached in MongoDB to reduce API calls
- **CSS Variables:** Centralized theme management

---

## 🎯 Project Goals

1. **Present Catholic prayer content** in a beautiful, reverent web experience
2. **Use YouTube videos** as primary content engine
3. **Maintain strict brand consistency** (Black/Burgundy/Gold)
4. **Optimize for desktop browsing** with mobile responsiveness
5. **Enable easy content expansion** (more prayers, categories, features)

---

## 📞 Support & Maintenance

- **Preview URL:** https://mass-locator.preview.emergentagent.com
- **Tech Stack:** Vite + React + FastAPI + MongoDB
- **Project Type:** DESKTOP WEBSITE (responsive)

---

**Last Updated:** January 2025
**Project Status:** Active Development
**Architecture:** Locked as Responsive Desktop Website ✅
