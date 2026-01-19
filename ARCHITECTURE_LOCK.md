# 🔒 ARCHITECTURE LOCK - Catholic Voices & Prayers Website

**CRITICAL: DO NOT MODIFY THIS ARCHITECTURE WITHOUT EXPLICIT USER INSTRUCTION**

---

## ⚠️ LOCKED PROJECT DEFINITION

### THIS PROJECT IS:
✅ **A responsive desktop-first website**
✅ **Accessible via web browsers on all devices**
✅ **Built with Vite + React + TypeScript + React Router**
✅ **Deployed as a traditional website**

### THIS PROJECT IS NOT:
❌ **NOT a mobile app**
❌ **NOT built with Expo or React Native**
❌ **NOT deployed to app stores**
❌ **NOT using native mobile components**
❌ **NOT using app-style UI patterns (tabs, bottom navigation, swipe gestures)**

---

## 🎯 LOCKED CONTENT HIERARCHY

### PRIMARY CONTENT LAYER (Sacred & Permanent)

**Long-Form Videos ONLY (Duration > 3 minutes)**

**Characteristics:**
- ✅ Videos over 180 seconds (3 minutes)
- ✅ Authoritative prayer and teaching content
- ✅ Stable, evergreen, not date-driven
- ✅ Featured in main navigation
- ✅ Displayed in prayer libraries and indexes
- ✅ Source for "Featured Prayer" sections

**Must Appear In:**
- Homepage featured prayer section
- /prayers page (main prayer library)
- Prayer category listings
- Search results (primary)
- "Browse All Prayers" sections

**Must NOT Be Mixed With:**
- Shorts content
- Daily devotional sections
- Date-driven content

---

### SECONDARY CONTENT LAYER (Daily & Supplemental)

**YouTube Shorts ONLY (Duration ≤ 3 minutes)**

**Characteristics:**
- ✅ Videos 180 seconds or less (3 minutes)
- ✅ Brief daily reflections
- ✅ Date-driven, liturgical calendar content
- ✅ Supplements long-form content
- ✅ Never replaces primary content

**Approved Uses ONLY:**
- "Today's Reflection" on homepage
- Feast Day pages
- Saint of the Day pages
- Daily devotional highlights
- Calendar-driven sections

**Strictly PROHIBITED From:**
- Primary prayer libraries
- Main /prayers index
- Long-form content listings
- Featured prayer sections (unless explicitly marked as "Short Reflection")
- Category lists (Rosary, Novenas, Traditional Prayers, etc.)

---

## 🏗️ LOCKED DESIGN ARCHITECTURE

### Desktop-First Responsive Design

**Design Hierarchy:**
1. **Desktop (1200px+):** PRIMARY design reference
2. **Tablet (768px-1199px):** Adapted from desktop
3. **Mobile (<768px):** Responsive adaptation, NOT mobile app UI

**Required Patterns:**
- ✅ Horizontal navigation bar in header
- ✅ Traditional website footer
- ✅ Generous spacing for desktop reading
- ✅ Large typography for prayer text (1.5rem desktop)
- ✅ CSS Grid/Flexbox layouts
- ✅ Standard HTML5 semantic elements

**Prohibited Patterns:**
- ❌ Bottom tab navigation
- ❌ Stack navigation (mobile app style)
- ❌ Native mobile gestures
- ❌ App-style swipe interactions
- ❌ Full-screen modals without context
- ❌ Hamburger-only navigation on desktop

---

## 📺 LOCKED CONTENT SOURCE

### YouTube as Single Source of Truth

**Content Authority:**
- ✅ YouTube channel "Catholic Voices & Prayers" is the ONLY content source
- ✅ Channel Uploads playlist is authoritative
- ✅ Video metadata (title, description, duration) determines classification
- ✅ Content automatically refreshed from YouTube API

**Classification Rules:**
- Duration > 180 seconds = Long-form (primary)
- Duration ≤ 180 seconds = Short (secondary)
- isShort flag stored in database
- Manual feast day mappings can override but not reclassify

**Prohibited Actions:**
- ❌ Creating content not sourced from YouTube
- ❌ Reclassifying Shorts as long-form
- ❌ Promoting Shorts to primary content layer
- ❌ Removing duration-based classification

---

## 🚫 PROHIBITED CHANGES

### DO NOT Under Any Circumstances:

**1. Reintroduce Mobile App Patterns:**
- ❌ Expo framework
- ❌ React Native components
- ❌ expo-router
- ❌ Native mobile navigation
- ❌ App-style UI components
- ❌ SafeAreaView, TouchableOpacity, etc.

**2. Alter Content Hierarchy:**
- ❌ Display Shorts in primary prayer libraries
- ❌ Feature Shorts as "Prayer of the Day" (only "Short Reflection of the Day")
- ❌ Mix Shorts into category listings
- ❌ Reclassify content based on popularity vs. duration

**3. Change Design Philosophy:**
- ❌ Mobile-first design approach
- ❌ App-style layouts
- ❌ Bottom navigation
- ❌ Swipe-based interactions
- ❌ Full-screen takeover patterns

---

## ✅ ALLOWED CHANGES

### Changes That DO NOT Require Explicit Permission:

**Content & Data:**
- Adding new prayers (with proper classification)
- Adding prayer text to videos
- Creating feast day mappings
- Updating video metadata from YouTube
- Adding manual category overrides

**Design Refinements:**
- Typography adjustments (maintaining readability)
- Color scheme refinements (maintaining burgundy/gold/black)
- Spacing improvements
- Accessibility enhancements
- Performance optimizations

**Feature Additions:**
- New prayer-related features that respect hierarchy
- Enhanced search functionality
- Filtering and sorting options
- User preferences (without accounts)
- Print-friendly views

### Changes That REQUIRE Explicit Permission:

**Structural Changes:**
- Modifying content hierarchy
- Changing primary vs. secondary classification
- Altering desktop-first approach
- Adding user accounts/authentication
- Introducing e-commerce
- Adding community features

**Technology Stack:**
- Changing from Vite to another bundler
- Switching from React to another framework
- Removing React Router
- Adding native mobile capabilities

---

## 📋 VERIFICATION CHECKLIST

### Before Making Any Changes, Verify:

**Content Hierarchy:**
- [ ] Are long-form videos still primary content?
- [ ] Are Shorts still secondary only?
- [ ] Is duration (180s) still the classification boundary?
- [ ] Are Shorts excluded from prayer libraries?

**Design Architecture:**
- [ ] Is this still a desktop-first website?
- [ ] Are we using standard HTML/CSS/JavaScript?
- [ ] Is navigation still horizontal header-based?
- [ ] Are mobile patterns avoided?

**Content Source:**
- [ ] Is YouTube still the single source?
- [ ] Are we respecting the Uploads playlist?
- [ ] Is duration-based classification intact?

---

## 🔓 OVERRIDE PROTOCOL

### If User Requests Architecture Changes:

**Required Actions:**
1. ✅ Confirm the requested change explicitly
2. ✅ Document WHY the architecture is being modified
3. ✅ Update this ARCHITECTURE_LOCK.md file
4. ✅ Update PROJECT_SPECIFICATION.md accordingly
5. ✅ Test thoroughly to ensure integrity

**Do NOT:**
- ❌ Interpret vague requests as architecture changes
- ❌ "Improve" the architecture without permission
- ❌ Reintroduce previously rejected patterns
- ❌ Make "temporary" architecture changes

---

## 📊 CURRENT LOCKED STATE

**Last Verified:** January 2025

**Project Type:** ✅ Responsive Desktop Website  
**Framework:** ✅ Vite + React + TypeScript  
**Routing:** ✅ React Router v6  
**Content Source:** ✅ YouTube Channel Uploads  
**Primary Content:** ✅ Long-form videos (>3 min)  
**Secondary Content:** ✅ Shorts (≤3 min)  
**Design Approach:** ✅ Desktop-first responsive  
**Navigation Style:** ✅ Traditional header/footer  

---

## 🎯 SUMMARY

This is a **desktop-first responsive website** for Catholic prayer content.

**Content Hierarchy:**
1. Long-form videos (>3 min) = Primary
2. Shorts (≤3 min) = Secondary (daily/feast days only)

**Design Philosophy:**
- Desktop-first, not mobile-first
- Traditional website, not mobile app
- Contemplative, not interactive

**Source of Truth:**
- YouTube channel uploads
- Duration-based classification
- Manual feast day mapping

**DO NOT change this architecture without explicit user instruction.**

---

## 📍 RELATED ARCHITECTURE LOCKS

### Mass Map Feature
See **`/app/MASS_MAP_ARCHITECTURE_LOCK.md`** for the locked architecture of the Reverent Catholic Mass Map feature, including:
- Database schema (locked)
- Inclusion rules (Diocesan, FSSP, ICKSP, Ordinariate, SSPX, Eastern Catholic)
- Exclusion rules (sedevacantist groups - non-negotiable)
- Affiliation and rite categories (locked)
- UI/UX requirements (desktop-first, no app-style patterns)
- API endpoints (locked)
- Marker color scheme (locked)

**The Mass Map architecture is FINAL and must not be modified without explicit user instruction.**

---

*This document serves as the authoritative reference for all development decisions.*
*Any code changes that contradict this document should be rejected.*
