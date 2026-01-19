# MASS MAP ARCHITECTURE LOCK
## Catholic Voices & Prayers - Reverent Catholic Mass Map

**Status: LOCKED**  
**Lock Date: January 2025**  
**Document Version: 1.0**

---

## ⚠️ CRITICAL: DO NOT MODIFY WITHOUT EXPLICIT USER INSTRUCTION

This document defines the **final, locked architecture** for the Reverent Catholic Mass Map feature. All architectural decisions documented here are **non-negotiable** and must not be changed, reinterpreted, or circumvented by any future development work.

---

## 1. DATABASE SCHEMA (LOCKED)

The `mass_locations` collection schema is **final**. Do not add, remove, or rename fields.

```javascript
{
  // Identity
  location_id: UUID,
  name: String,
  entity_type: String,      // Parish, Oratory, Chapel, Mission
  jurisdiction: String,     // Diocese, Eparchy, Ordinariate, Society
  affiliation: String,      // Diocesan, FSSP, ICKSP, Ordinariate, SSPX, Eastern Catholic
  rite: String,             // Latin, Byzantine, Maronite, Melkite, Ukrainian, Ruthenian, Chaldean
  use_or_liturgy: String,   // 1962 Roman Missal, Ordinariate Use, Divine Liturgy
  
  // Address & Geo
  street: String,
  city: String,
  state: String,
  zip_code: String,
  country: String,
  latitude: Float,
  longitude: Float,
  
  // Sacraments & Info
  mass_schedule_url: String (optional),
  confession_url: String (optional),
  adoration_url: String (optional),
  livestream_url: String (optional),
  website_url: String (optional),
  phone: String (optional),
  notes: String (optional),
  
  // Data Governance
  source_name: String,
  source_url: String,
  last_verified_date: DateTime,
  verification_method: String,
  exclude_flag: Boolean,
  exclude_reason: String,
  
  // Timestamps
  created_at: DateTime,
  updated_at: DateTime
}
```

---

## 2. INCLUSION RULES (LOCKED)

The following groups are **permanently included** in the Mass Map:

| Group | Affiliation Value | Notes |
|-------|-------------------|-------|
| Diocesan Traditional Latin Mass | `Diocesan` | 1962 Roman Missal communities under diocesan authority |
| FSSP | `FSSP` | Priestly Fraternity of St. Peter |
| ICKSP | `ICKSP` | Institute of Christ the King Sovereign Priest |
| Ordinariate | `Ordinariate` | Personal Ordinariate of the Chair of St. Peter |
| SSPX | `SSPX` | Society of St. Pius X - **EXPLICITLY INCLUDED** |
| Eastern Catholic Churches | `Eastern Catholic` | All sui iuris Eastern Catholic Churches in communion with Rome |

### Eastern Catholic Rites (LOCKED)
- Byzantine
- Maronite
- Melkite
- Ukrainian
- Ruthenian
- Chaldean
- (Additional Eastern rites may be added as data becomes available)

---

## 3. EXCLUSION RULES (LOCKED - NON-NEGOTIABLE)

The following groups are **permanently excluded** and must **NEVER** appear on the public map:

| Excluded Group | Reason |
|----------------|--------|
| CMRI | Sedevacantist |
| SSPV | Sedevacantist |
| SSPX-MC (SSPX Marian Corps) | Sedevacantist |
| Any group identifying as "Sedevacantist" | Not in communion with Rome |
| Any group identifying as "Vacantist" | Not in communion with Rome |
| Any group using "Non una cum" | Sedevacantist position |

### Exclusion Implementation
```python
EXCLUDED_GROUPS = [
    'cmri', 'sspv', 'sspx-mc', 'sspx marian corps',
    'sedevacantist', 'vacantist', 'non una cum'
]
```

- Exclusion check runs on: `name`, `affiliation`, `notes` fields
- Excluded locations are stored with `exclude_flag = true`
- Excluded locations are **never returned** by public API endpoints
- This exclusion logic must **never** be disabled or bypassed

---

## 4. AFFILIATION CATEGORIES (LOCKED)

The following affiliation values are **final**:

1. `Diocesan` - Traditional Latin Mass under diocesan authority
2. `FSSP` - Priestly Fraternity of St. Peter
3. `ICKSP` - Institute of Christ the King Sovereign Priest
4. `Ordinariate` - Personal Ordinariate of the Chair of St. Peter
5. `SSPX` - Society of St. Pius X
6. `Eastern Catholic` - All Eastern Catholic Churches

**Do not:**
- Add new affiliation categories
- Rename existing categories
- Merge or split categories
- Remove any category

---

## 5. RITE CATEGORIES (LOCKED)

The following rite values are **final**:

1. `Latin` - Roman Rite
2. `Byzantine` - Byzantine Rite
3. `Maronite` - Maronite Rite
4. `Melkite` - Melkite Greek Catholic
5. `Ukrainian` - Ukrainian Greek Catholic
6. `Ruthenian` - Ruthenian Byzantine Catholic
7. `Chaldean` - Chaldean Catholic

**Do not:**
- Rename existing rites
- Remove any rite
- Merge rites

---

## 6. LITURGY/USE CATEGORIES (LOCKED)

1. `1962 Roman Missal` - Traditional Latin Mass
2. `Ordinariate Use` - Divine Worship missal
3. `Divine Liturgy` - Eastern Catholic liturgies

---

## 7. UI/UX ARCHITECTURE (LOCKED)

### Design Principles (FINAL)
- **Desktop-first**, responsive for mobile
- Clean, reverent, non-commercial aesthetic
- Hallow-inspired design language
- No aggressive calls to action
- No advertisements

### Prohibited UI Patterns
- ❌ Bottom navigation bars
- ❌ Tab-based navigation
- ❌ App-style interfaces
- ❌ Floating action buttons
- ❌ Push notification prompts
- ❌ Pop-ups or modals (except location detail)
- ❌ Social sharing widgets
- ❌ User accounts or login

### Required UI Elements
- ✅ Search by city/state/ZIP
- ✅ Filter by affiliation
- ✅ Filter by rite
- ✅ Visual map with color-coded markers
- ✅ Location list panel
- ✅ Location detail view
- ✅ Legend showing marker colors
- ✅ Statistics display
- ✅ Disclaimer about exclusions

---

## 8. API ENDPOINTS (LOCKED)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/mass-locations` | GET | List locations with filters |
| `/api/mass-locations/search` | GET | Text search |
| `/api/mass-locations/nearby` | GET | Proximity search |
| `/api/mass-locations/filters` | GET | Available filter options |
| `/api/mass-locations/stats` | GET | Statistics |
| `/api/mass-locations/{id}` | GET | Single location |
| `/api/mass-locations` | POST | Create (admin) |
| `/api/mass-locations/{id}` | PUT | Update (admin) |
| `/api/mass-locations/{id}` | DELETE | Delete (admin) |
| `/api/mass-locations/submit` | POST | User submission |
| `/api/mass-locations/seed` | POST | Seed data |

---

## 9. MARKER COLOR SCHEME (LOCKED)

| Affiliation | Color | Hex Code |
|-------------|-------|----------|
| Diocesan | Blue | `#2563eb` |
| FSSP | Green | `#059669` |
| ICKSP | Purple | `#7c3aed` |
| Ordinariate | Red | `#dc2626` |
| SSPX | Amber | `#d97706` |
| Eastern Catholic | Cyan | `#0891b2` |

---

## 10. PERMITTED FUTURE WORK

The following work is **allowed** without architectural changes:

### ✅ Allowed
- Adding new verified locations to the database
- Updating existing location data (addresses, URLs, schedules)
- Improving data accuracy and verification
- Performance optimization (caching, indexing)
- Bug fixes that don't alter architecture
- Adding additional Eastern Catholic rites (within Eastern Catholic affiliation)
- Improving mobile responsiveness
- Accessibility improvements
- Loading performance optimization

### ❌ Not Allowed Without Explicit Instruction
- Changing database schema
- Adding or removing affiliation categories
- Adding or removing rite categories
- Modifying exclusion rules
- Changing SSPX inclusion status
- Changing Eastern Catholic inclusion status
- Converting to app-style UI
- Adding user authentication
- Adding social features
- Changing marker colors
- Restructuring API endpoints

---

## 11. VERIFICATION CHECKLIST

Before any Mass Map changes, verify:

- [ ] Database schema unchanged
- [ ] Exclusion rules intact
- [ ] SSPX still included
- [ ] Eastern Catholic still included
- [ ] All 6 affiliations present
- [ ] All 7+ rites present
- [ ] No app-style UI patterns
- [ ] Desktop-first design maintained
- [ ] Color scheme unchanged
- [ ] API endpoints unchanged

---

## 12. CONTACT FOR CHANGES

Any proposed changes to locked architecture must be:
1. Explicitly requested by the user
2. Documented as an architecture update
3. This document updated to reflect changes

---

**This architecture is FINAL unless explicitly instructed otherwise by the user.**
