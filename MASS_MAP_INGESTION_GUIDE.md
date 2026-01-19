# Mass Map Data Ingestion Guide
## Catholic Voices & Prayers - Reverent Catholic Mass Map

**Mode: DATA INGESTION**  
**Status: ACTIVE**  
**Last Updated: January 2025**

---

## Overview

This guide documents the data ingestion system for the Reverent Catholic Mass Map. The system is designed to systematically expand from sample data to real national coverage using **authoritative directories only**.

---

## 1. Authoritative Data Sources

### APPROVED Sources Only

| Source | Affiliation | URL | Data Format |
|--------|-------------|-----|-------------|
| Latin Mass Directory | Diocesan | latinmassdir.org | Web directory |
| FSSP Official | FSSP | fssp.org/where-to-find-us | Structured |
| ICKSP Official | ICKSP | institute-christ-king.org/locations | Structured |
| Ordinariate Parish Finder | Ordinariate | ordinariate.net/parish-finder | Structured |
| SSPX Chapel Finder | SSPX | sspx.org/en/mass-and-confession-schedule | Structured |
| Byzantine Metropolia Pittsburgh | Eastern Catholic | archpitt.org/parishes | Directory |
| Ukrainian Archeparchy Philadelphia | Eastern Catholic | ukrarcheparchy.us/parishes | Directory |
| Eparchy of St. Maron (Maronite) | Eastern Catholic | stmaron.org/parishes | Directory |
| Melkite Eparchy of Newton | Eastern Catholic | melkite.org/parishes | Directory |
| Eparchy of Parma (Ruthenian) | Eastern Catholic | parma.org/parishes | Directory |
| Chaldean Eparchy St. Thomas | Eastern Catholic | chaldeandiocese.org/parishes | Directory |

### PROHIBITED Sources

❌ Unverified user submissions  
❌ Social media posts  
❌ Unofficial directories or aggregators  
❌ Sedevacantist websites (CMRI, SSPV, etc.)  
❌ Scraped data without manual verification  

---

## 2. API Endpoints

### Ingestion Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/mass-locations/ingest/bulk` | POST | Bulk JSON import |
| `/api/mass-locations/ingest/csv` | POST | CSV import |
| `/api/mass-locations/ingest/template` | GET | Get CSV template |
| `/api/mass-locations/ingest/sources` | GET | List authoritative sources |
| `/api/mass-locations/ingest/status` | GET | Database statistics |
| `/api/mass-locations/ingest/validate` | POST | Validate single location |

---

## 3. Bulk JSON Import

### Endpoint
```
POST /api/mass-locations/ingest/bulk
```

### Request Body
```json
{
  "locations": [
    {
      "name": "St. Example Parish",
      "entity_type": "Parish",
      "jurisdiction": "Society",
      "affiliation": "FSSP",
      "rite": "Latin",
      "use_or_liturgy": "1962 Roman Missal",
      "street": "123 Main Street",
      "city": "Example City",
      "state": "PA",
      "zip_code": "19000",
      "latitude": 40.1234,
      "longitude": -75.5678,
      "website_url": "https://example.com",
      "mass_schedule_url": "https://example.com/schedule",
      "phone": "555-123-4567",
      "notes": "Optional notes"
    }
  ],
  "source_name": "FSSP Official Directory",
  "source_url": "https://fssp.org/where-to-find-us",
  "dry_run": true
}
```

### Response
```json
{
  "total_processed": 50,
  "inserted": 45,
  "skipped_duplicate": 3,
  "skipped_excluded": 0,
  "errors": 2,
  "error_details": [
    {"index": 12, "name": "Example", "error": "Missing required fields"}
  ],
  "dry_run": true
}
```

### Dry Run Mode
Set `"dry_run": true` to validate data without inserting. Always use dry run first!

---

## 4. CSV Import

### Endpoint
```
POST /api/mass-locations/ingest/csv
```

### Query Parameters
```
source_name: "FSSP Directory"
source_url: "https://fssp.org"
affiliation: "FSSP"
rite: "Latin"
use_or_liturgy: "1962 Roman Missal"
dry_run: true
```

### CSV Format
```csv
name,street,city,state,zip_code,latitude,longitude,website,phone,notes
"St. Mary Mother of God","727 5th St NW","Washington","DC","20001","38.9006","-77.0211","https://example.com","202-555-0100","FSSP apostolate"
```

### Required Columns
- `name`
- `city`
- `state`

### Optional Columns
- `street` or `address`
- `zip_code` or `zip`
- `latitude` or `lat`
- `longitude` or `lng` or `lon`
- `website` or `website_url`
- `phone`
- `notes` or `description`

---

## 5. Validation Endpoint

### Endpoint
```
POST /api/mass-locations/ingest/validate
```

### Request
```json
{
  "name": "Test Parish",
  "city": "Philadelphia",
  "state": "PA",
  "affiliation": "FSSP",
  "latitude": 39.9526,
  "longitude": -75.1652
}
```

### Response
```json
{
  "valid": true,
  "excluded": false,
  "issues": [
    "Warning: No phone number provided"
  ],
  "location": { ... }
}
```

---

## 6. Deduplication Rules

The system uses **aggressive deduplication** to prevent duplicate entries:

### Level 1: Exact Match
- Same name + city + state (case-insensitive)
- **Result:** Skipped as duplicate

### Level 2: Geographic Proximity
- Locations within 0.5 miles of each other
- With similar names (2+ common significant words)
- **Result:** Flagged as potential duplicate

### Level 3: Address Normalization
- Street addresses are normalized
- Common variations are matched (St./Street, Ave./Avenue)

---

## 7. Exclusion Rules

The following are **automatically excluded** (non-negotiable):

| Excluded Term | Type |
|---------------|------|
| CMRI | Sedevacantist |
| SSPV | Sedevacantist |
| SSPX-MC | Sedevacantist |
| Sedevacantist | Self-identified |
| Vacantist | Self-identified |
| Non una cum | Sedevacantist position |

Exclusion check runs on: `name`, `affiliation`, `notes` fields

Excluded locations are stored with `exclude_flag: true` but never displayed publicly.

---

## 8. Ingestion Workflow

### Step 1: Gather Data
1. Visit authoritative source
2. Export or manually compile location data
3. Ensure coordinates are included

### Step 2: Format Data
```bash
# Get CSV template
curl http://localhost:8001/api/mass-locations/ingest/template
```

### Step 3: Validate (Dry Run)
```bash
# Dry run to check for issues
curl -X POST "http://localhost:8001/api/mass-locations/ingest/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [...],
    "source_name": "Source Name",
    "source_url": "https://source.url",
    "dry_run": true
  }'
```

### Step 4: Review Report
- Check `skipped_duplicate` count
- Review `error_details` for issues
- Fix any validation errors

### Step 5: Import
```bash
# Actual import (dry_run: false)
curl -X POST "http://localhost:8001/api/mass-locations/ingest/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [...],
    "source_name": "Source Name",
    "source_url": "https://source.url",
    "dry_run": false
  }'
```

### Step 6: Verify
```bash
# Check database status
curl http://localhost:8001/api/mass-locations/ingest/status
```

---

## 9. Data Quality Requirements

### Required Fields
- ✅ `name` - Official parish/chapel name
- ✅ `city` - City name
- ✅ `state` - 2-letter state code
- ✅ `affiliation` - One of: Diocesan, FSSP, ICKSP, Ordinariate, SSPX, Eastern Catholic

### Strongly Recommended
- ✅ `latitude` / `longitude` - For accurate mapping and deduplication
- ✅ `street` - Full street address
- ✅ `zip_code` - 5-digit ZIP
- ✅ `website_url` - Official website

### Optional
- `mass_schedule_url`
- `confession_url`
- `adoration_url`
- `phone`
- `notes`

### Coordinate Validation
- US mainland latitude: 24° to 50°
- US mainland longitude: -125° to -65°
- Alaska/Hawaii require special handling

---

## 10. Sample Import Scripts

### Python Example
```python
import requests
import json

locations = [
    {
        "name": "St. Mary Mother of God",
        "affiliation": "FSSP",
        "rite": "Latin",
        "use_or_liturgy": "1962 Roman Missal",
        "street": "727 5th St NW",
        "city": "Washington",
        "state": "DC",
        "zip_code": "20001",
        "latitude": 38.9006,
        "longitude": -77.0211,
        "website_url": "https://www.stmarymotherof god.org"
    }
]

# Dry run first
response = requests.post(
    "http://localhost:8001/api/mass-locations/ingest/bulk",
    json={
        "locations": locations,
        "source_name": "FSSP Official Directory",
        "source_url": "https://fssp.org",
        "dry_run": True
    }
)

print(json.dumps(response.json(), indent=2))

# If successful, run actual import
if response.json()["errors"] == 0:
    response = requests.post(
        "http://localhost:8001/api/mass-locations/ingest/bulk",
        json={
            "locations": locations,
            "source_name": "FSSP Official Directory",
            "source_url": "https://fssp.org",
            "dry_run": False
        }
    )
    print("Imported:", response.json()["inserted"])
```

---

## 11. Current Database Status

Check status at any time:
```bash
curl http://localhost:8001/api/mass-locations/ingest/status
```

Returns:
- Total records
- Active vs excluded locations
- Breakdown by source
- Breakdown by affiliation
- State coverage
- Recent additions

---

## 12. Priority Ingestion Order

Recommended order for data ingestion:

### Phase 1: Official Directories (High Confidence)
1. FSSP Official Directory
2. ICKSP Official Directory
3. Ordinariate Parish Finder
4. SSPX Official Chapel Listings

### Phase 2: Eastern Catholic Eparchies
5. Byzantine Catholic (Pittsburgh, Parma)
6. Ukrainian Catholic
7. Maronite Catholic
8. Melkite Catholic
9. Ruthenian Catholic
10. Chaldean Catholic

### Phase 3: Diocesan TLM
11. Latin Mass Directory (with verification)
12. Individual diocesan websites

---

## 13. Maintenance

### Periodic Tasks
- Re-verify coordinates quarterly
- Update URLs for broken links
- Check for new locations from official sources
- Remove closed parishes

### Data Governance Fields
- `last_verified_date` - When location was last verified
- `verification_method` - How it was verified
- `source_name` - Original data source
- `source_url` - URL of original source

---

## Important Notes

⚠️ **Do not modify the database schema**  
⚠️ **Do not alter exclusion rules**  
⚠️ **Do not change affiliation categories**  
⚠️ **Always use dry run before actual import**  
⚠️ **Only use authoritative sources**

---

*This document is part of the Mass Map Data Ingestion Mode.*
*Architecture is locked per MASS_MAP_ARCHITECTURE_LOCK.md*
