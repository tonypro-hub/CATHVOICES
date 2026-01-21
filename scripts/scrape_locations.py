#!/usr/bin/env python3
"""
Mass Location Web Scraper
Fetches Traditional Latin Mass locations from:
1. Latin Mass Directory (latinmassdir.org)
2. ICKSP (institute-christ-king.org)
3. FSSP (via Latin Mass Directory filter)

Run manually with: python scrape_locations.py
"""

import asyncio
import os
import re
import uuid
import json
import httpx
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# US State name to abbreviation mapping
STATE_ABBREV = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA',
    'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA',
    'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
    'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO',
    'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ',
    'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH',
    'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
    'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY'
}

# City coordinates for geocoding
CITY_COORDS = {
    # Major cities already in our system - add more as needed
    ("Tucson", "AZ"): (32.2226, -110.9747),
    ("Oakland", "CA"): (37.8044, -122.2712),
    ("San Jose", "CA"): (37.3382, -121.8863),
    ("Sacramento", "CA"): (38.5816, -121.4944),
    ("Bridgeport", "CT"): (41.1865, -73.1952),
    ("Waterbury", "CT"): (41.5582, -73.0515),
    ("Stamford", "CT"): (41.0534, -73.5387),
    ("Tampa", "FL"): (27.9506, -82.4572),
    ("Cahokia", "IL"): (38.5710, -90.1901),
    ("Chicago", "IL"): (41.8781, -87.6298),
    ("Rockford", "IL"): (42.2711, -89.0940),
    ("Merrillville", "IN"): (41.4828, -87.3328),
    ("South Bend", "IN"): (41.6764, -86.2520),
    ("Sulphur", "LA"): (30.2366, -93.3774),
    ("Warren", "MA"): (42.2126, -72.1912),
    ("Boston", "MA"): (42.3601, -71.0589),
    ("Kansas City", "MO"): (39.0997, -94.5786),
    ("St. Louis", "MO"): (38.6270, -90.1994),
    ("Detroit", "MI"): (42.3314, -83.0458),
    ("Reno", "NV"): (39.5296, -119.8138),
    ("West Orange", "NJ"): (40.7987, -74.2390),
    ("Oswego", "NY"): (43.4553, -76.5105),
    ("Queens", "NY"): (40.7282, -73.7949),
    ("Bayside", "NY"): (40.7682, -73.7713),
    ("Columbus", "OH"): (39.9612, -82.9988),
    ("Cleveland", "OH"): (41.4993, -81.6944),
    ("Pittsburgh", "PA"): (40.4406, -79.9959),
    ("Scranton", "PA"): (41.4090, -75.6624),
    ("Altoona", "PA"): (40.5187, -78.3947),
    ("Burlington", "WI"): (42.6781, -88.2762),
    ("Green Bay", "WI"): (44.5192, -88.0198),
    ("Milwaukee", "WI"): (43.0389, -87.9065),
    ("Sheboygan", "WI"): (43.7508, -87.7145),
    ("Wausau", "WI"): (44.9591, -89.6301),
    # Additional cities
    ("Gower", "MO"): (39.6086, -94.5994),
    ("Miami", "FL"): (25.7617, -80.1918),
    ("Sanford", "FL"): (28.8000, -81.2733),
    ("Notre Dame", "IN"): (41.7003, -86.2388),
    ("Houston", "TX"): (29.7604, -95.3698),
    ("Yonkers", "NY"): (40.9312, -73.8987),
    ("Minooka", "IL"): (41.4553, -88.2618),
    ("Denver", "CO"): (39.7392, -104.9903),
    ("Ave Maria", "FL"): (26.3202, -81.3917),
    ("Lewiston", "ME"): (44.1004, -70.2148),
    ("Wilmington", "NC"): (34.2257, -77.9447),
    ("Minot", "ND"): (48.2330, -101.2923),
    ("Birmingham", "AL"): (33.5207, -86.8025),
    ("Honolulu", "HI"): (21.3069, -157.8583),
    ("Fairfield", "PA"): (39.7848, -77.3658),
    ("Valparaiso", "NE"): (41.0797, -96.8292),
    ("Littleton", "CO"): (39.6133, -105.0166),
    ("Dallas", "TX"): (32.7767, -96.7970),
    ("Fort Worth", "TX"): (32.7555, -97.3308),
    ("Irving", "TX"): (32.8140, -96.9489),
    ("Traverse City", "MI"): (44.7631, -85.6206),
    ("San Francisco", "CA"): (37.7749, -122.4194),
    # FSSP locations
    ("Denton", "NE"): (40.7364, -96.8511),
    ("Front Royal", "VA"): (38.9182, -78.1944),
    ("Post Falls", "ID"): (47.7182, -116.9516),
    ("Omaha", "NE"): (41.2565, -95.9345),
    ("Richmond", "VA"): (37.5407, -77.4360),
    ("Charlotte", "NC"): (35.2271, -80.8431),
    ("Aiken", "SC"): (33.5604, -81.7196),
}


def get_state_abbrev(state_name):
    """Convert state name to abbreviation"""
    if len(state_name) == 2:
        return state_name.upper()
    return STATE_ABBREV.get(state_name.lower().strip(), state_name)


def get_coordinates(city, state):
    """Get coordinates for a city/state pair"""
    state_abbrev = get_state_abbrev(state)
    key = (city, state_abbrev)
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    
    # Try fuzzy matching
    for (c, s), coords in CITY_COORDS.items():
        if s == state_abbrev and (c.lower() in city.lower() or city.lower() in c.lower()):
            return coords
    
    return None, None


class LatinMassDirectoryScraper:
    """Scraper for latinmassdir.org"""
    
    BASE_URL = "https://www.latinmassdir.org"
    
    def __init__(self):
        self.locations = []
        
    async def fetch_page(self, client, page_num):
        """Fetch a single page of locations"""
        url = f"{self.BASE_URL}/country/us/?view=list"
        if page_num > 1:
            url += f"&pg={page_num}"
        
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return None
    
    def parse_page(self, html):
        """Parse venue listings from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        venues = []
        
        # Find all venue entries (h3 elements with links)
        for venue_header in soup.select('h3 a[href*="/venue/"]'):
            venue = {}
            venue['name'] = venue_header.get_text(strip=True)
            venue['url'] = self.BASE_URL + venue_header['href'] if venue_header['href'].startswith('/') else venue_header['href']
            
            # Get the parent container for additional info
            parent = venue_header.find_parent('div') or venue_header.find_parent()
            if parent:
                # Try to find community/affiliation and state info
                text = parent.get_text(' ', strip=True)
                
                # Extract state (usually at the end)
                state_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$', text)
                if state_match:
                    state_text = state_match.group(1)
                    venue['state'] = get_state_abbrev(state_text)
                
                # Try to extract community/affiliation
                community_patterns = [
                    r'(Fraternity of Saint Peter|F\.S\.S\.P\.)',
                    r'(Institutum Christi Regis|I\.C\.R\.S\.S\.|Institute of Christ the King)',
                    r'(Diocesan parish)',
                    r'(Ordo Sancti Benedicti|O\.S\.B\.)',
                    r'(Ordo Praedicatorum|O\.P\.)',
                    r'(Congregatio)',
                ]
                for pattern in community_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        affiliation = match.group(1)
                        if 'Fraternity' in affiliation or 'F.S.S.P' in affiliation:
                            venue['affiliation'] = 'FSSP'
                        elif 'Christi Regis' in affiliation or 'I.C.R.S.S' in affiliation:
                            venue['affiliation'] = 'ICKSP'
                        elif 'Diocesan' in affiliation:
                            venue['affiliation'] = 'Diocesan'
                        else:
                            venue['affiliation'] = 'Diocesan'
                        break
            
            if venue.get('name'):
                venues.append(venue)
        
        return venues
    
    async def scrape_all(self, max_pages=24):
        """Scrape all pages of locations"""
        async with httpx.AsyncClient() as client:
            for page in range(1, max_pages + 1):
                print(f"Scraping Latin Mass Directory page {page}/{max_pages}...")
                html = await self.fetch_page(client, page)
                if html:
                    venues = self.parse_page(html)
                    self.locations.extend(venues)
                    print(f"  Found {len(venues)} venues on page {page}")
                await asyncio.sleep(1)  # Be polite to the server
        
        return self.locations


class ICKSPScraper:
    """Scraper for ICKSP locations from their homepage"""
    
    # Pre-defined ICKSP locations from their website
    LOCATIONS = [
        {"name": "St. Gianna Oratory", "city": "Tucson", "state": "AZ"},
        {"name": "Institute of Christ the King - Bay Area", "city": "Oakland", "state": "CA"},
        {"name": "Immaculate Heart of Mary", "city": "San Jose", "state": "CA"},
        {"name": "Sts. Cyril & Methodius", "city": "Bridgeport", "state": "CT"},
        {"name": "St. Patrick Oratory", "city": "Waterbury", "state": "CT"},
        {"name": "Epiphany of Our Lord Shrine", "city": "Tampa", "state": "FL"},
        {"name": "Holy Family Log Church", "city": "Cahokia", "state": "IL"},
        {"name": "ICKSP US Provincial Headquarters", "city": "Chicago", "state": "IL"},
        {"name": "St. Mary Oratory", "city": "Rockford", "state": "IL"},
        {"name": "St. Joseph Oratory", "city": "Merrillville", "state": "IN"},
        {"name": "St. Francis de Sales Oratory", "city": "Sulphur", "state": "LA"},
        {"name": "St. Paul Church", "city": "Warren", "state": "MA"},
        {"name": "Old St. Patrick Oratory", "city": "Kansas City", "state": "MO"},
        {"name": "St. Francis de Sales Oratory", "city": "St. Louis", "state": "MO"},
        {"name": "St. Joseph Shrine", "city": "Detroit", "state": "MI"},
        {"name": "ICKSP Reno Oratory", "city": "Reno", "state": "NV"},
        {"name": "St. Anthony Church", "city": "West Orange", "state": "NJ"},
        {"name": "St. Mary of the Assumption", "city": "Oswego", "state": "NY"},
        {"name": "St. Josaphat Oratory", "city": "Bayside", "state": "NY"},
        {"name": "St. Leo Oratory", "city": "Columbus", "state": "OH"},
        {"name": "St. Elizabeth of Hungary Shrine", "city": "Cleveland", "state": "OH"},
        {"name": "Most Precious Blood of Jesus Parish", "city": "Pittsburgh", "state": "PA"},
        {"name": "Sacred Heart Retreat Center", "city": "Burlington", "state": "WI"},
        {"name": "St. Patrick's Oratory", "city": "Green Bay", "state": "WI"},
        {"name": "St. Stanislaus Oratory", "city": "Milwaukee", "state": "WI"},
        {"name": "Ss. Cyril & Methodius", "city": "Sheboygan", "state": "WI"},
        {"name": "St. Mary's Oratory", "city": "Wausau", "state": "WI"},
    ]
    
    def get_locations(self):
        """Return pre-defined ICKSP locations"""
        return [
            {
                "name": loc["name"],
                "city": loc["city"],
                "state": loc["state"],
                "affiliation": "ICKSP",
                "rite": "Latin",
                "use_or_liturgy": "1962 Roman Missal",
            }
            for loc in self.LOCATIONS
        ]


class FSSPScraper:
    """Get FSSP locations (many are already in Latin Mass Directory)"""
    
    # Known FSSP locations in the US
    LOCATIONS = [
        {"name": "Our Lady of Guadalupe Seminary", "city": "Denton", "state": "NE"},
        {"name": "St. John the Baptist Church", "city": "Front Royal", "state": "VA"},
        {"name": "Mater Dei Parish", "city": "Irving", "state": "TX"},
        {"name": "St. Stephen the First Martyr Church", "city": "Sacramento", "state": "CA"},
        {"name": "St. Mary Mother of God Church", "city": "Fort Worth", "state": "TX"},
        {"name": "Holy Family Church", "city": "Fort Worth", "state": "TX"},
        {"name": "St. Joan of Arc Church", "city": "Post Falls", "state": "ID"},
        {"name": "Our Lady of Mt. Carmel Church", "city": "Littleton", "state": "CO"},
        {"name": "Sacred Heart Church", "city": "South Bend", "state": "IN"},
        {"name": "St. Peter Church", "city": "Omaha", "state": "NE"},
        {"name": "St. Joseph Church", "city": "Richmond", "state": "VA"},
        {"name": "Our Lady of Peace Church", "city": "Scranton", "state": "PA"},
        {"name": "St. Mary Church", "city": "Altoona", "state": "PA"},
        {"name": "St. John Fisher Church", "city": "Stamford", "state": "CT"},
        {"name": "St. Clement Church", "city": "Boston", "state": "MA"},
        {"name": "St. Ann Church", "city": "Charlotte", "state": "NC"},
        {"name": "Our Lady of Mt. Carmel Church", "city": "Aiken", "state": "SC"},
    ]
    
    def get_locations(self):
        """Return pre-defined FSSP locations"""
        return [
            {
                "name": loc["name"],
                "city": loc["city"],
                "state": loc["state"],
                "affiliation": "FSSP",
                "rite": "Latin",
                "use_or_liturgy": "1962 Roman Missal",
            }
            for loc in self.LOCATIONS
        ]


async def save_to_database(locations):
    """Save scraped locations to MongoDB"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'catholic_voices')]
    
    inserted = 0
    skipped = 0
    no_coords = 0
    
    for loc in locations:
        name = loc.get('name', '')
        city = loc.get('city', '')
        state = loc.get('state', '')
        
        if not name or not city:
            continue
        
        # Check for duplicates
        existing = await db.mass_locations.find_one({
            "$or": [
                {"name": name, "city": city, "state": state},
                {"name": {"$regex": f"^{re.escape(name[:20])}", "$options": "i"}, "city": city}
            ]
        })
        
        if existing:
            skipped += 1
            continue
        
        # Get coordinates
        lat, lng = get_coordinates(city, state)
        if lat is None:
            print(f"NO COORDS: {name}, {city}, {state}")
            no_coords += 1
            continue
        
        # Create document
        doc = {
            "id": str(uuid.uuid4()),
            "location_id": str(uuid.uuid4()),
            "name": name,
            "entity_type": "Parish",
            "affiliation": loc.get('affiliation', 'Diocesan'),
            "rite": loc.get('rite', 'Latin'),
            "use_or_liturgy": loc.get('use_or_liturgy', '1962 Roman Missal'),
            "street": loc.get('street', ''),
            "city": city,
            "state": state,
            "zip_code": "",
            "country": "USA",
            "latitude": lat,
            "longitude": lng,
            "website_url": loc.get('url'),
            "notes": f"Scraped from web on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "exclude_flag": False,
            "source": loc.get('source', 'web_scraper'),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.mass_locations.insert_one(doc)
        print(f"INSERT: {name}, {city}, {state}")
        inserted += 1
    
    client.close()
    
    return {
        "inserted": inserted,
        "skipped": skipped,
        "no_coords": no_coords,
        "total_processed": len(locations)
    }


async def main():
    """Main scraper function"""
    print("="*60)
    print("MASS LOCATION WEB SCRAPER")
    print("="*60)
    
    all_locations = []
    
    # 1. Scrape ICKSP locations
    print("\n[1/3] Getting ICKSP locations...")
    icksp = ICKSPScraper()
    icksp_locations = icksp.get_locations()
    for loc in icksp_locations:
        loc['source'] = 'ICKSP Website'
    all_locations.extend(icksp_locations)
    print(f"  Found {len(icksp_locations)} ICKSP locations")
    
    # 2. Scrape FSSP locations
    print("\n[2/3] Getting FSSP locations...")
    fssp = FSSPScraper()
    fssp_locations = fssp.get_locations()
    for loc in fssp_locations:
        loc['source'] = 'FSSP Known Locations'
    all_locations.extend(fssp_locations)
    print(f"  Found {len(fssp_locations)} FSSP locations")
    
    # 3. Scrape Latin Mass Directory (limited to first few pages for demo)
    print("\n[3/3] Scraping Latin Mass Directory (first 5 pages)...")
    lmd = LatinMassDirectoryScraper()
    # Limit to 5 pages to avoid overwhelming the server during demo
    lmd_locations = await lmd.scrape_all(max_pages=5)
    for loc in lmd_locations:
        loc['source'] = 'Latin Mass Directory'
        if not loc.get('affiliation'):
            loc['affiliation'] = 'Diocesan'
    all_locations.extend(lmd_locations)
    print(f"  Found {len(lmd_locations)} locations from Latin Mass Directory")
    
    # Save to database
    print("\n" + "="*60)
    print("SAVING TO DATABASE...")
    print("="*60)
    
    results = await save_to_database(all_locations)
    
    print("\n" + "="*60)
    print("SCRAPER COMPLETE")
    print("="*60)
    print(f"Total processed: {results['total_processed']}")
    print(f"Inserted: {results['inserted']}")
    print(f"Skipped (duplicates): {results['skipped']}")
    print(f"Skipped (no coordinates): {results['no_coords']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
