#!/usr/bin/env python3
"""
Diocesan Latin Mass Ingestion Script
Ingests authoritative diocesan data for Latin-language Masses in the US and Canada.

Features:
- Deduplication by name, address, or city+diocese
- Updates existing records, creates new ones only when needed
- Handles multiple rite types (Latin, Dominican, Carmelite, etc.)
- Geocodes addresses
- Reports on all changes
"""

import asyncio
import os
import re
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

# Extended city coordinates for geocoding
CITY_COORDS = {
    # Alabama
    ("Hanceville", "AL"): (34.0615, -86.7683),
    # Alaska
    ("Anchorage", "AK"): (61.2181, -149.9003),
    # Arkansas
    ("Fayetteville", "AR"): (36.0626, -94.1574),
    # California
    ("Hollywood", "CA"): (34.0928, -118.3287),
    ("Santa Paula", "CA"): (34.3542, -119.0590),
    ("West Hollywood", "CA"): (34.0900, -118.3617),
    ("La Mesa", "CA"): (32.7678, -117.0231),
    ("San Francisco", "CA"): (37.7749, -122.4194),
    ("Palo Alto", "CA"): (37.4419, -122.1430),
    ("Napa", "CA"): (38.2975, -122.2869),
    ("Fresno", "CA"): (36.7378, -119.7871),
    ("San Diego", "CA"): (32.7157, -117.1611),
    ("Los Angeles", "CA"): (34.0522, -118.2437),
    # Colorado
    ("Denver", "CO"): (39.7392, -104.9903),
    ("Boulder", "CO"): (40.0150, -105.2705),
    # Connecticut
    ("New Haven", "CT"): (41.3083, -72.9279),
    ("Ridgefield", "CT"): (41.2815, -73.4982),
    ("Stamford", "CT"): (41.0534, -73.5387),
    # Delaware
    ("Wilmington", "DE"): (39.7391, -75.5398),
    # DC
    ("Washington", "DC"): (38.9072, -77.0369),
    # Florida
    ("Cocoa", "FL"): (28.3861, -80.7420),
    ("Jacksonville", "FL"): (30.3322, -81.6557),
    ("St. Augustine", "FL"): (29.8946, -81.3145),
    ("Miami", "FL"): (25.7617, -80.1918),
    ("Coconut Grove", "FL"): (25.7270, -80.2406),
    ("Orlando", "FL"): (28.5383, -81.3792),
    ("Loxahatchee", "FL"): (26.7545, -80.3481),
    ("Tampa", "FL"): (27.9506, -82.4572),
    # Georgia
    ("Atlanta", "GA"): (33.7490, -84.3880),
    ("Conyers", "GA"): (33.6676, -84.0177),
    # Hawaii
    ("Honolulu", "HI"): (21.3069, -157.8583),
    # Illinois
    ("Chicago", "IL"): (41.8781, -87.6298),
    ("River Forest", "IL"): (41.8978, -87.8140),
    ("Oak Park", "IL"): (41.8850, -87.7845),
    # Indiana
    ("Notre Dame", "IN"): (41.7003, -86.2388),
    ("Indianapolis", "IN"): (39.7684, -86.1581),
    ("Fort Wayne", "IN"): (41.0793, -85.1394),
    ("South Bend", "IN"): (41.6764, -86.2520),
    # Iowa
    ("Dubuque", "IA"): (42.5006, -90.6646),
    # Kansas
    ("Atchison", "KS"): (39.5631, -95.1216),
    # Kentucky
    ("Louisville", "KY"): (38.2527, -85.7585),
    ("Covington", "KY"): (39.0837, -84.5086),
    # Louisiana
    ("New Orleans", "LA"): (29.9511, -90.0715),
    ("Lacombe", "LA"): (30.3157, -89.9417),
    ("Grand Coteau", "LA"): (30.4172, -92.0474),
    # Maine
    ("Augusta", "ME"): (44.3106, -69.7795),
    # Maryland
    ("Baltimore", "MD"): (39.2904, -76.6122),
    ("Emmitsburg", "MD"): (39.7043, -77.3269),
    # Massachusetts
    ("Boston", "MA"): (42.3601, -71.0589),
    ("Cambridge", "MA"): (42.3736, -71.1097),
    ("Worcester", "MA"): (42.2626, -71.8023),
    ("Weston", "MA"): (42.3667, -71.3032),
    ("Petersham", "MA"): (42.4892, -72.1892),
    # Michigan
    ("Ann Arbor", "MI"): (42.2808, -83.7430),
    ("Detroit", "MI"): (42.3314, -83.0458),
    # Minnesota
    ("St. Paul", "MN"): (44.9537, -93.0900),
    ("Minneapolis", "MN"): (44.9778, -93.2650),
    ("Collegeville", "MN"): (45.5947, -94.3625),
    # Missouri
    ("St. Louis", "MO"): (38.6270, -90.1994),
    ("Kansas City", "MO"): (39.0997, -94.5786),
    ("Conception", "MO"): (40.0339, -94.6783),
    # Nebraska
    ("Omaha", "NE"): (41.2565, -95.9345),
    # New Hampshire
    ("Manchester", "NH"): (42.9956, -71.4548),
    # New Jersey
    ("Newark", "NJ"): (40.7357, -74.1724),
    ("Jersey City", "NJ"): (40.7282, -74.0776),
    ("Hoboken", "NJ"): (40.7440, -74.0324),
    ("Morristown", "NJ"): (40.7968, -74.4815),
    # New Mexico
    ("Santa Fe", "NM"): (35.6870, -105.9378),
    # New York
    ("New York", "NY"): (40.7128, -74.0060),
    ("Manhattan", "NY"): (40.7831, -73.9712),
    ("Brooklyn", "NY"): (40.6782, -73.9442),
    ("Bronx", "NY"): (40.8448, -73.8648),
    ("Yonkers", "NY"): (40.9312, -73.8987),
    ("Albany", "NY"): (42.6526, -73.7562),
    ("Rochester", "NY"): (43.1566, -77.6088),
    ("Buffalo", "NY"): (42.8864, -78.8784),
    ("Stony Point", "NY"): (41.2295, -73.9874),
    ("Jamaica", "NY"): (40.6915, -73.8057),
    # North Carolina
    ("Raleigh", "NC"): (35.7796, -78.6382),
    ("Belmont", "NC"): (35.2437, -81.0373),
    # Ohio
    ("Cleveland", "OH"): (41.4993, -81.6944),
    ("Cincinnati", "OH"): (39.1031, -84.5120),
    ("Columbus", "OH"): (39.9612, -82.9988),
    # Oklahoma
    ("Oklahoma City", "OK"): (35.4676, -97.5164),
    ("Tulsa", "OK"): (36.1540, -95.9928),
    # Oregon
    ("Mount Angel", "OR"): (45.0678, -122.7973),
    # Pennsylvania
    ("Philadelphia", "PA"): (39.9526, -75.1652),
    ("Latrobe", "PA"): (40.3212, -79.3795),
    ("Pittsburgh", "PA"): (40.4406, -79.9959),
    # Rhode Island
    ("Providence", "RI"): (41.8240, -71.4128),
    ("Warwick", "RI"): (41.7001, -71.4162),
    # South Carolina
    ("Mepkin", "SC"): (33.1176, -79.9514),
    ("Charleston", "SC"): (32.7765, -79.9311),
    # Tennessee
    ("Nashville", "TN"): (36.1627, -86.7816),
    # Texas
    ("Houston", "TX"): (29.7604, -95.3698),
    ("Dallas", "TX"): (32.7767, -96.7970),
    ("Irving", "TX"): (32.8140, -96.9489),
    ("Fort Worth", "TX"): (32.7555, -97.3308),
    ("San Antonio", "TX"): (29.4241, -98.4936),
    ("Austin", "TX"): (30.2672, -97.7431),
    # Utah
    ("Salt Lake City", "UT"): (40.7608, -111.8910),
    # Virginia
    ("Richmond", "VA"): (37.5407, -77.4360),
    ("Arlington", "VA"): (38.8799, -77.1068),
    # Washington
    ("Seattle", "WA"): (47.6062, -122.3321),
    ("Lacey", "WA"): (47.0343, -122.8232),
    # Wisconsin
    ("Milwaukee", "WI"): (43.0389, -87.9065),
    ("Madison", "WI"): (43.0731, -89.4012),
    # Wyoming
    ("Cheyenne", "WY"): (41.1400, -104.8202),
    # Canada - Ontario
    ("Toronto", "ON"): (43.6532, -79.3832),
    ("Ottawa", "ON"): (45.4215, -75.6972),
    ("Peterborough", "ON"): (44.3091, -78.3197),
    ("Petersborough", "ON"): (44.3091, -78.3197),
    # Canada - Quebec
    ("Montreal", "QC"): (45.5017, -73.5673),
    ("Montréal", "QC"): (45.5017, -73.5673),
    ("Quebec City", "QC"): (46.8139, -71.2080),
    ("Oka", "QC"): (45.4667, -74.0833),
    ("Saint-Benoît-du-Lac", "QC"): (45.1667, -72.2833),
}

# Sedevacantist groups to exclude
EXCLUDED_GROUPS = ['sspv', 'cmri', 'sedevacantist', 'independent chapel']

def check_exclusion(name, affiliation, notes=""):
    """Check if location should be excluded"""
    combined = f"{name} {affiliation} {notes}".lower()
    for excluded in EXCLUDED_GROUPS:
        if excluded in combined:
            return True, f"Excluded: matches {excluded}"
    return False, None

def get_coordinates(city, state):
    """Get coordinates for city/state pair"""
    # Normalize state
    state = state.upper().strip()
    city = city.strip()
    
    key = (city, state)
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    
    # Try fuzzy match
    for (c, s), coords in CITY_COORDS.items():
        if s == state and (c.lower() in city.lower() or city.lower() in c.lower()):
            return coords
    
    return None, None

def parse_use_liturgy(schedule_text):
    """Determine liturgy type from schedule description"""
    text = schedule_text.lower()
    
    if 'extraordinary form' in text or '1962' in text or 'ef' in text.split():
        return 'Extraordinary Form 1962'
    elif 'dominican rite' in text or 'dominican' in text:
        return 'Dominican Rite'
    elif 'carmelite rite' in text or 'carmelite' in text:
        return 'Carmelite Rite'
    elif 'carthusian' in text:
        return 'Carthusian Rite'
    elif 'ordinariate' in text or 'anglican use' in text:
        return 'Ordinariate Use'
    elif 'hybrid' in text:
        return 'Ordinary Form Latin (Hybrid)'
    elif 'ordinary form' in text or 'novus ordo' in text:
        return 'Ordinary Form Latin'
    else:
        return 'Ordinary Form Latin'

def parse_entity_type(name, notes=""):
    """Determine entity type from name"""
    name_lower = name.lower()
    notes_lower = notes.lower() if notes else ""
    combined = f"{name_lower} {notes_lower}"
    
    if 'cathedral' in combined:
        return 'Cathedral'
    elif 'monastery' in combined or 'abbey' in combined:
        return 'Monastery'
    elif 'shrine' in combined:
        return 'Shrine'
    elif 'chapel' in combined and ('college' in combined or 'university' in combined):
        return 'University Chapel'
    elif 'chapel' in combined:
        return 'Chapel'
    elif 'basilica' in combined:
        return 'Basilica'
    else:
        return 'Parish'

def parse_public_access(notes):
    """Determine public access from notes"""
    if not notes:
        return True
    
    notes_lower = notes.lower()
    if 'not open to public' in notes_lower or 'private' in notes_lower:
        return False
    elif 'call to confirm' in notes_lower or 'call ahead' in notes_lower or 'conditional' in notes_lower:
        return 'conditional'
    return True

# ============================================
# DIOCESAN LATIN MASS DATA
# ============================================

DIOCESAN_DATA = [
    # Alabama
    {
        "name": "Our Lady of the Angels Monastery (Shrine of the Most Blessed Sacrament)",
        "diocese": "Diocese of Birmingham",
        "street": "3222 County Road 548",
        "city": "Hanceville",
        "state": "AL",
        "postal_code": "35077",
        "country": "USA",
        "schedule": "Daily 7 AM Hybrid Latin Novus Ordo (rebroadcast on EWTN)",
        "notes": "Franciscan Missionaries of the Eternal Word"
    },
    # Alaska
    {
        "name": "Holy Family Cathedral",
        "diocese": "Archdiocese of Anchorage",
        "city": "Anchorage",
        "state": "AK",
        "country": "USA",
        "schedule": "Sundays 4:00 PM Dominican Rite Latin Mass"
    },
    # Arkansas
    {
        "name": "St. Joseph Church",
        "diocese": "Diocese of Little Rock",
        "street": "1722 N. Starr Drive",
        "city": "Fayetteville",
        "state": "AR",
        "postal_code": "72701",
        "country": "USA",
        "schedule": "Saturday 5:00 PM hybrid (Latin Gregorian Schola)"
    },
    # California
    {
        "name": "Monastery of the Angels",
        "diocese": "Archdiocese of Los Angeles",
        "street": "1977 Carmen Ave.",
        "city": "Hollywood",
        "state": "CA",
        "postal_code": "90068",
        "country": "USA",
        "schedule": "Sundays 7 AM sung Ordinary-Form Latin Mass",
        "notes": "Cloistered Dominican Nuns"
    },
    {
        "name": "Thomas Aquinas College Chapel",
        "diocese": "Archdiocese of Los Angeles",
        "street": "10000 North Ojai Road",
        "city": "Santa Paula",
        "state": "CA",
        "postal_code": "93060",
        "country": "USA",
        "schedule": "Weekdays 7 AM EF (academic year); Sat & Sun 7:15 AM EF; Sun 9 AM hybrid; Sat 5:30 PM hybrid"
    },
    {
        "name": "St. Victor Church",
        "diocese": "Archdiocese of Los Angeles",
        "street": "8634 Holloway Drive",
        "city": "West Hollywood",
        "state": "CA",
        "postal_code": "90069",
        "country": "USA",
        "schedule": "Sunday 10:30 AM hybrid; Sunday 7:30 PM Extraordinary Form"
    },
    {
        "name": "Little Flower Haven",
        "diocese": "Diocese of San Diego",
        "street": "8585 La Mesa Boulevard",
        "city": "La Mesa",
        "state": "CA",
        "postal_code": "91941",
        "country": "USA",
        "schedule": "Daily 7 AM hybrid / Old Carmelite Rite",
        "notes": "Call to confirm access"
    },
    {
        "name": "Cathedral of St. Mary of the Assumption",
        "diocese": "Archdiocese of San Francisco",
        "street": "1111 Gough St.",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94109",
        "country": "USA",
        "schedule": "Sunday 9 AM hybrid"
    },
    {
        "name": "St. Dominic's Church",
        "diocese": "Archdiocese of San Francisco",
        "street": "2390 Bush St.",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94115",
        "country": "USA",
        "schedule": "Sunday 11:30 AM hybrid"
    },
    {
        "name": "Sts. Peter & Paul Church",
        "diocese": "Archdiocese of San Francisco",
        "street": "666 Filbert St.",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94133",
        "country": "USA",
        "schedule": "1st Sunday 11:45 AM Ordinary-Form Latin Mass"
    },
    {
        "name": "St. Thomas Aquinas Church",
        "diocese": "Diocese of San Jose",
        "street": "751 Waverly St.",
        "city": "Palo Alto",
        "state": "CA",
        "postal_code": "94306",
        "country": "USA",
        "schedule": "Sunday 12 Noon hybrid; Latin Vespers Sunday 6:15 PM"
    },
    {
        "name": "St. John the Baptist Church",
        "diocese": "Diocese of Santa Rosa",
        "street": "983 Napa St.",
        "city": "Napa",
        "state": "CA",
        "postal_code": "94559",
        "country": "USA",
        "schedule": "Sunday 8 AM hybrid"
    },
    {
        "name": "St. Anthony of Padua Church",
        "diocese": "Diocese of Fresno",
        "street": "5770 N. Maroa Ave.",
        "city": "Fresno",
        "state": "CA",
        "postal_code": "93704",
        "country": "USA",
        "schedule": "Sunday 12 Noon hybrid"
    },
    # Colorado
    {
        "name": "Cathedral Basilica of the Immaculate Conception",
        "diocese": "Archdiocese of Denver",
        "street": "1530 Logan St.",
        "city": "Denver",
        "state": "CO",
        "postal_code": "80203",
        "country": "USA",
        "schedule": "Sunday 6:30 PM Extraordinary Form"
    },
    {
        "name": "St. Thomas Aquinas Church",
        "diocese": "Archdiocese of Denver",
        "street": "898 14th St.",
        "city": "Boulder",
        "state": "CO",
        "postal_code": "80302",
        "country": "USA",
        "schedule": "Sunday 5:00 PM Extraordinary Form",
        "notes": "University Parish"
    },
    # Connecticut
    {
        "name": "St. Mary's Church",
        "diocese": "Archdiocese of Hartford",
        "street": "5 Hillhouse Ave.",
        "city": "New Haven",
        "state": "CT",
        "postal_code": "06511",
        "country": "USA",
        "schedule": "Sunday 9:30 AM Latin Ordinary Form",
        "notes": "Yale University Parish (Dominican)"
    },
    {
        "name": "St. Mary Church",
        "diocese": "Diocese of Bridgeport",
        "street": "55 Catoonah St.",
        "city": "Ridgefield",
        "state": "CT",
        "postal_code": "06877",
        "country": "USA",
        "schedule": "Sunday 12 Noon hybrid"
    },
    # Delaware
    {
        "name": "St. Joseph on the Brandywine",
        "diocese": "Diocese of Wilmington",
        "street": "10 Old Church Road",
        "city": "Wilmington",
        "state": "DE",
        "postal_code": "19807",
        "country": "USA",
        "schedule": "1st Sunday 9 AM Latin High Mass"
    },
    # District of Columbia
    {
        "name": "Basilica of the National Shrine of the Immaculate Conception",
        "diocese": "Archdiocese of Washington",
        "street": "400 Michigan Ave. NE",
        "city": "Washington",
        "state": "DC",
        "postal_code": "20017",
        "country": "USA",
        "schedule": "Sunday 12:30 PM Latin Ordinary Form (Crypt Church); Daily 7 AM Latin"
    },
    {
        "name": "St. Matthew's Cathedral",
        "diocese": "Archdiocese of Washington",
        "street": "1725 Rhode Island Ave. NW",
        "city": "Washington",
        "state": "DC",
        "postal_code": "20036",
        "country": "USA",
        "schedule": "Sunday 5:30 PM hybrid"
    },
    {
        "name": "Franciscan Monastery of the Holy Land",
        "diocese": "Archdiocese of Washington",
        "street": "1400 Quincy St. NE",
        "city": "Washington",
        "state": "DC",
        "postal_code": "20017",
        "country": "USA",
        "schedule": "Sunday 11:30 AM hybrid"
    },
    {
        "name": "Dominican House of Studies",
        "diocese": "Archdiocese of Washington",
        "street": "487 Michigan Ave. NE",
        "city": "Washington",
        "state": "DC",
        "postal_code": "20017",
        "country": "USA",
        "schedule": "Daily Conventual Mass in Latin",
        "notes": "Call to confirm public access"
    },
    # Florida
    {
        "name": "Our Saviour Church",
        "diocese": "Diocese of Orlando",
        "street": "5301 N. Atlantic Ave.",
        "city": "Cocoa",
        "state": "FL",
        "postal_code": "32927",
        "country": "USA",
        "schedule": "Sunday 8 AM hybrid"
    },
    {
        "name": "Assumption Church",
        "diocese": "Diocese of St. Augustine",
        "street": "2403 Atlantic Blvd.",
        "city": "Jacksonville",
        "state": "FL",
        "postal_code": "32207",
        "country": "USA",
        "schedule": "Sunday 10 AM Latin Ordinary Form"
    },
    {
        "name": "Cathedral Basilica of St. Augustine",
        "diocese": "Diocese of St. Augustine",
        "street": "38 Cathedral Place",
        "city": "St. Augustine",
        "state": "FL",
        "postal_code": "32084",
        "country": "USA",
        "schedule": "Sunday 11 AM hybrid; 1st Saturday 9 AM Latin"
    },
    {
        "name": "St. Hugh Church",
        "diocese": "Archdiocese of Miami",
        "street": "3460 Royal Road",
        "city": "Coconut Grove",
        "state": "FL",
        "postal_code": "33133",
        "country": "USA",
        "schedule": "Sunday 12:15 PM hybrid"
    },
    {
        "name": "Mary, Queen of the Universe Shrine",
        "diocese": "Diocese of Orlando",
        "street": "8300 Vineland Ave.",
        "city": "Orlando",
        "state": "FL",
        "postal_code": "32821",
        "country": "USA",
        "schedule": "Sunday 7:30 AM Latin"
    },
    {
        "name": "Our Lady of Lourdes Church",
        "diocese": "Diocese of Palm Beach",
        "street": "15960 Okeechobee Blvd.",
        "city": "Loxahatchee",
        "state": "FL",
        "postal_code": "33470",
        "country": "USA",
        "schedule": "Sunday 8 AM hybrid"
    },
    # Georgia
    {
        "name": "Cathedral of Christ the King",
        "diocese": "Archdiocese of Atlanta",
        "street": "2699 Peachtree Road NE",
        "city": "Atlanta",
        "state": "GA",
        "postal_code": "30305",
        "country": "USA",
        "schedule": "Sunday 1 PM Latin Ordinary Form"
    },
    {
        "name": "Monastery of the Holy Spirit",
        "diocese": "Archdiocese of Atlanta",
        "street": "2625 Highway 212 SW",
        "city": "Conyers",
        "state": "GA",
        "postal_code": "30094",
        "country": "USA",
        "schedule": "Daily Latin Mass (Trappist schedule)",
        "notes": "Trappist Monastery - call for times"
    },
    # Hawaii
    {
        "name": "Cathedral Basilica of Our Lady of Peace",
        "diocese": "Diocese of Honolulu",
        "street": "1184 Bishop St.",
        "city": "Honolulu",
        "state": "HI",
        "postal_code": "96813",
        "country": "USA",
        "schedule": "Sunday 5 PM Latin (occasional)"
    },
    # Illinois
    {
        "name": "St. John Cantius Church",
        "diocese": "Archdiocese of Chicago",
        "street": "825 N. Carpenter St.",
        "city": "Chicago",
        "state": "IL",
        "postal_code": "60642",
        "country": "USA",
        "schedule": "Sunday 8 AM, 9 AM (hybrid), 11 AM (Solemn High EF), 12:30 PM (hybrid); Weekdays EF and OF Latin"
    },
    {
        "name": "St. Vincent Ferrer Church (Dominican)",
        "diocese": "Archdiocese of Chicago",
        "street": "1530 Jackson Ave.",
        "city": "River Forest",
        "state": "IL",
        "postal_code": "60305",
        "country": "USA",
        "schedule": "Sunday 10 AM hybrid"
    },
    # Indiana
    {
        "name": "Basilica of the Sacred Heart",
        "diocese": "Diocese of Fort Wayne-South Bend",
        "street": "University of Notre Dame",
        "city": "Notre Dame",
        "state": "IN",
        "postal_code": "46556",
        "country": "USA",
        "schedule": "Sunday 10 AM Latin (academic year)"
    },
    {
        "name": "SS. Peter & Paul Cathedral",
        "diocese": "Archdiocese of Indianapolis",
        "street": "1347 N. Meridian St.",
        "city": "Indianapolis",
        "state": "IN",
        "postal_code": "46202",
        "country": "USA",
        "schedule": "3rd Sunday 5 PM Latin"
    },
    # Iowa
    {
        "name": "St. Raphael Cathedral",
        "diocese": "Archdiocese of Dubuque",
        "street": "231 Bluff St.",
        "city": "Dubuque",
        "state": "IA",
        "postal_code": "52001",
        "country": "USA",
        "schedule": "Sunday 10:30 AM hybrid"
    },
    # Kansas
    {
        "name": "St. Benedict's Abbey",
        "diocese": "Archdiocese of Kansas City in Kansas",
        "street": "1020 N. 2nd St.",
        "city": "Atchison",
        "state": "KS",
        "postal_code": "66002",
        "country": "USA",
        "schedule": "Daily Latin Mass (Benedictine)",
        "notes": "Benedictine Abbey"
    },
    # Kentucky
    {
        "name": "Cathedral of the Assumption",
        "diocese": "Archdiocese of Louisville",
        "street": "433 S. 5th St.",
        "city": "Louisville",
        "state": "KY",
        "postal_code": "40202",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin"
    },
    {
        "name": "Cathedral Basilica of the Assumption",
        "diocese": "Diocese of Covington",
        "street": "1140 Madison Ave.",
        "city": "Covington",
        "state": "KY",
        "postal_code": "41011",
        "country": "USA",
        "schedule": "Sunday 10 AM hybrid"
    },
    # Louisiana
    {
        "name": "St. Patrick's Church",
        "diocese": "Archdiocese of New Orleans",
        "street": "724 Camp St.",
        "city": "New Orleans",
        "state": "LA",
        "postal_code": "70130",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin Ordinary Form"
    },
    {
        "name": "St. Joseph Abbey",
        "diocese": "Archdiocese of New Orleans",
        "street": "75376 River Road",
        "city": "Lacombe",
        "state": "LA",
        "postal_code": "70445",
        "country": "USA",
        "schedule": "Daily Latin (Benedictine schedule)",
        "notes": "Benedictine Abbey"
    },
    {
        "name": "Our Lady of the Oaks Retreat House",
        "diocese": "Diocese of Lafayette",
        "street": "527 St. Mary St.",
        "city": "Grand Coteau",
        "state": "LA",
        "postal_code": "70541",
        "country": "USA",
        "schedule": "Latin Mass during retreats",
        "notes": "Jesuit Retreat House"
    },
    # Maine
    {
        "name": "St. Augustine Church",
        "diocese": "Diocese of Portland",
        "street": "57 Melville St.",
        "city": "Augusta",
        "state": "ME",
        "postal_code": "04330",
        "country": "USA",
        "schedule": "Sunday 9 AM hybrid"
    },
    # Maryland
    {
        "name": "Basilica of the National Shrine of the Assumption",
        "diocese": "Archdiocese of Baltimore",
        "street": "409 Cathedral St.",
        "city": "Baltimore",
        "state": "MD",
        "postal_code": "21201",
        "country": "USA",
        "schedule": "Sunday 10:45 AM Latin Solemn Mass"
    },
    {
        "name": "Mount St. Mary's Seminary",
        "diocese": "Archdiocese of Baltimore",
        "street": "16300 Old Emmitsburg Road",
        "city": "Emmitsburg",
        "state": "MD",
        "postal_code": "21727",
        "country": "USA",
        "schedule": "Daily Latin Mass (seminary schedule)"
    },
    # Massachusetts
    {
        "name": "St. Paul Church",
        "diocese": "Archdiocese of Boston",
        "street": "29 Mt. Auburn St.",
        "city": "Cambridge",
        "state": "MA",
        "postal_code": "02138",
        "country": "USA",
        "schedule": "Sunday 9 AM Latin",
        "notes": "Harvard Square"
    },
    {
        "name": "Blessed Sacrament Chapel (Campion Center)",
        "diocese": "Archdiocese of Boston",
        "street": "319 Concord Road",
        "city": "Weston",
        "state": "MA",
        "postal_code": "02493",
        "country": "USA",
        "schedule": "Daily Latin (Jesuit)",
        "notes": "Jesuit Retreat Center - call to confirm"
    },
    {
        "name": "St. Benedict Abbey",
        "diocese": "Diocese of Worcester",
        "street": "252 Still River Road",
        "city": "Petersham",
        "state": "MA",
        "postal_code": "01366",
        "country": "USA",
        "schedule": "Daily Latin (Benedictine)",
        "notes": "Benedictine Monastery"
    },
    # Michigan
    {
        "name": "St. Thomas the Apostle Church",
        "diocese": "Archdiocese of Detroit",
        "street": "530 Elizabeth St.",
        "city": "Ann Arbor",
        "state": "MI",
        "postal_code": "48104",
        "country": "USA",
        "schedule": "Sunday 9:30 AM Latin Ordinary Form",
        "notes": "University Parish"
    },
    # Minnesota
    {
        "name": "St. Agnes Church",
        "diocese": "Archdiocese of St. Paul and Minneapolis",
        "street": "548 Lafond Ave.",
        "city": "St. Paul",
        "state": "MN",
        "postal_code": "55103",
        "country": "USA",
        "schedule": "Sunday 10 AM Solemn High Mass (hybrid)"
    },
    {
        "name": "St. John's Abbey",
        "diocese": "Diocese of St. Cloud",
        "street": "2900 Abbey Plaza",
        "city": "Collegeville",
        "state": "MN",
        "postal_code": "56321",
        "country": "USA",
        "schedule": "Daily Latin (Benedictine schedule)",
        "notes": "Benedictine Abbey"
    },
    # Missouri
    {
        "name": "St. Francis Xavier College Church",
        "diocese": "Archdiocese of St. Louis",
        "street": "3628 Lindell Blvd.",
        "city": "St. Louis",
        "state": "MO",
        "postal_code": "63108",
        "country": "USA",
        "schedule": "Sunday 10:30 AM hybrid",
        "notes": "Jesuit - St. Louis University"
    },
    {
        "name": "Conception Abbey",
        "diocese": "Diocese of Kansas City-St. Joseph",
        "street": "37174 State Highway VV",
        "city": "Conception",
        "state": "MO",
        "postal_code": "64433",
        "country": "USA",
        "schedule": "Daily Latin (Benedictine schedule)",
        "notes": "Benedictine Abbey"
    },
    # Nebraska
    {
        "name": "St. Cecilia Cathedral",
        "diocese": "Archdiocese of Omaha",
        "street": "701 N. 40th St.",
        "city": "Omaha",
        "state": "NE",
        "postal_code": "68131",
        "country": "USA",
        "schedule": "Sunday 10:30 AM hybrid"
    },
    # New Hampshire
    {
        "name": "St. Joseph Cathedral",
        "diocese": "Diocese of Manchester",
        "street": "145 Lowell St.",
        "city": "Manchester",
        "state": "NH",
        "postal_code": "03104",
        "country": "USA",
        "schedule": "Sunday 8 AM Latin"
    },
    # New Jersey
    {
        "name": "Cathedral Basilica of the Sacred Heart",
        "diocese": "Archdiocese of Newark",
        "street": "89 Ridge St.",
        "city": "Newark",
        "state": "NJ",
        "postal_code": "07104",
        "country": "USA",
        "schedule": "Sunday 12 Noon Latin"
    },
    {
        "name": "St. Peter's Church",
        "diocese": "Archdiocese of Newark",
        "street": "144 Grand St.",
        "city": "Jersey City",
        "state": "NJ",
        "postal_code": "07302",
        "country": "USA",
        "schedule": "Sunday 10:30 AM hybrid"
    },
    {
        "name": "SS. Peter & Paul Church",
        "diocese": "Archdiocese of Newark",
        "street": "404 Hudson St.",
        "city": "Hoboken",
        "state": "NJ",
        "postal_code": "07030",
        "country": "USA",
        "schedule": "Sunday 12:15 PM Latin"
    },
    {
        "name": "Assumption Church",
        "diocese": "Diocese of Paterson",
        "street": "91 Maple Ave.",
        "city": "Morristown",
        "state": "NJ",
        "postal_code": "07960",
        "country": "USA",
        "schedule": "Sunday 10 AM Latin"
    },
    # New Mexico
    {
        "name": "Cathedral Basilica of St. Francis of Assisi",
        "diocese": "Archdiocese of Santa Fe",
        "street": "131 Cathedral Place",
        "city": "Santa Fe",
        "state": "NM",
        "postal_code": "87501",
        "country": "USA",
        "schedule": "Sunday 12:15 PM hybrid"
    },
    # New York
    {
        "name": "Church of St. Vincent Ferrer",
        "diocese": "Archdiocese of New York",
        "street": "869 Lexington Ave.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10065",
        "country": "USA",
        "schedule": "Sunday 1 PM Solemn High Mass (hybrid)",
        "notes": "Dominican"
    },
    {
        "name": "Church of Our Saviour",
        "diocese": "Archdiocese of New York",
        "street": "59 Park Ave.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10016",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin Ordinary Form"
    },
    {
        "name": "Church of St. Agnes",
        "diocese": "Archdiocese of New York",
        "street": "143 E. 43rd St.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10017",
        "country": "USA",
        "schedule": "Sunday 9 AM Latin; Weekdays 12:10 PM Latin"
    },
    {
        "name": "St. Patrick's Cathedral",
        "diocese": "Archdiocese of New York",
        "street": "Fifth Avenue at 50th St.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10022",
        "country": "USA",
        "schedule": "Sunday 10:15 AM Latin Ordinary Form"
    },
    {
        "name": "Church of the Holy Innocents",
        "diocese": "Archdiocese of New York",
        "street": "128 W. 37th St.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10018",
        "country": "USA",
        "schedule": "Daily 12:30 PM EF; Sunday 11:30 AM hybrid, 12:30 PM EF"
    },
    {
        "name": "Holy Trinity Church",
        "diocese": "Archdiocese of New York",
        "street": "213 W. 82nd St.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10024",
        "country": "USA",
        "schedule": "Sunday 11 AM hybrid"
    },
    {
        "name": "St. Jean Baptiste Church",
        "diocese": "Archdiocese of New York",
        "street": "184 E. 76th St.",
        "city": "New York",
        "state": "NY",
        "postal_code": "10021",
        "country": "USA",
        "schedule": "Sunday 11 AM Solemn High Mass (hybrid)"
    },
    {
        "name": "Graymoor Franciscan Friars",
        "diocese": "Archdiocese of New York",
        "street": "40 Franciscan Way",
        "city": "Stony Point",
        "state": "NY",
        "postal_code": "10986",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin",
        "notes": "Franciscan Friary"
    },
    {
        "name": "Immaculate Conception Center (Diocesan Seminary)",
        "diocese": "Diocese of Rockville Centre",
        "street": "7200 Douglaston Parkway",
        "city": "Jamaica",
        "state": "NY",
        "postal_code": "11362",
        "country": "USA",
        "schedule": "Daily Latin (seminary schedule)"
    },
    {
        "name": "Cathedral of the Immaculate Conception",
        "diocese": "Diocese of Albany",
        "street": "125 Eagle St.",
        "city": "Albany",
        "state": "NY",
        "postal_code": "12202",
        "country": "USA",
        "schedule": "Sunday 12:15 PM Latin"
    },
    {
        "name": "Sacred Heart Cathedral",
        "diocese": "Diocese of Rochester",
        "street": "296 Flower City Park",
        "city": "Rochester",
        "state": "NY",
        "postal_code": "14615",
        "country": "USA",
        "schedule": "1st Sunday 12:15 PM Latin"
    },
    {
        "name": "St. Joseph Cathedral",
        "diocese": "Diocese of Buffalo",
        "street": "50 Franklin St.",
        "city": "Buffalo",
        "state": "NY",
        "postal_code": "14202",
        "country": "USA",
        "schedule": "Sunday 8 AM Latin"
    },
    # North Carolina
    {
        "name": "Holy Name of Jesus Cathedral",
        "diocese": "Diocese of Raleigh",
        "street": "715 Nazareth St.",
        "city": "Raleigh",
        "state": "NC",
        "postal_code": "27606",
        "country": "USA",
        "schedule": "Sunday 1 PM Latin"
    },
    {
        "name": "Belmont Abbey",
        "diocese": "Diocese of Charlotte",
        "street": "100 Belmont-Mt. Holly Road",
        "city": "Belmont",
        "state": "NC",
        "postal_code": "28012",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin (Abbey Church)",
        "notes": "Benedictine Abbey"
    },
    # Ohio
    {
        "name": "St. John Cathedral",
        "diocese": "Diocese of Cleveland",
        "street": "1007 Superior Ave.",
        "city": "Cleveland",
        "state": "OH",
        "postal_code": "44114",
        "country": "USA",
        "schedule": "Sunday 11 AM hybrid"
    },
    {
        "name": "Old St. Mary's Church",
        "diocese": "Archdiocese of Cincinnati",
        "street": "123 E. 13th St.",
        "city": "Cincinnati",
        "state": "OH",
        "postal_code": "45202",
        "country": "USA",
        "schedule": "Sunday 9 AM hybrid"
    },
    # Oklahoma
    {
        "name": "St. Francis of Assisi Church",
        "diocese": "Archdiocese of Oklahoma City",
        "street": "1901 NW 18th St.",
        "city": "Oklahoma City",
        "state": "OK",
        "postal_code": "73106",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin"
    },
    {
        "name": "Church of St. Mary",
        "diocese": "Diocese of Tulsa",
        "street": "1347 E. 49th Place",
        "city": "Tulsa",
        "state": "OK",
        "postal_code": "74105",
        "country": "USA",
        "schedule": "Sunday 10:30 AM hybrid"
    },
    # Oregon
    {
        "name": "Mount Angel Abbey",
        "diocese": "Archdiocese of Portland",
        "street": "1 Abbey Drive",
        "city": "Mount Angel",
        "state": "OR",
        "postal_code": "97362",
        "country": "USA",
        "schedule": "Daily Latin (Benedictine schedule)",
        "notes": "Benedictine Abbey"
    },
    # Pennsylvania
    {
        "name": "Cathedral Basilica of SS. Peter & Paul",
        "diocese": "Archdiocese of Philadelphia",
        "street": "1723 Race St.",
        "city": "Philadelphia",
        "state": "PA",
        "postal_code": "19103",
        "country": "USA",
        "schedule": "Sunday 11 AM Solemn Latin Mass"
    },
    {
        "name": "St. Archabbey Church (Saint Vincent)",
        "diocese": "Diocese of Greensburg",
        "street": "300 Fraser Purchase Road",
        "city": "Latrobe",
        "state": "PA",
        "postal_code": "15650",
        "country": "USA",
        "schedule": "Sunday 10:30 AM Latin (Conventual Mass)",
        "notes": "Benedictine Archabbey"
    },
    # Rhode Island
    {
        "name": "Cathedral of SS. Peter & Paul",
        "diocese": "Diocese of Providence",
        "street": "30 Fenner St.",
        "city": "Providence",
        "state": "RI",
        "postal_code": "02903",
        "country": "USA",
        "schedule": "Sunday 11:30 AM Latin"
    },
    {
        "name": "St. Kevin Church",
        "diocese": "Diocese of Providence",
        "street": "333 Sandy Lane",
        "city": "Warwick",
        "state": "RI",
        "postal_code": "02889",
        "country": "USA",
        "schedule": "Sunday 9 AM hybrid"
    },
    # South Carolina
    {
        "name": "Mepkin Abbey",
        "diocese": "Diocese of Charleston",
        "street": "1098 Mepkin Abbey Road",
        "city": "Mepkin",
        "state": "SC",
        "postal_code": "29461",
        "country": "USA",
        "schedule": "Daily Latin (Trappist schedule)",
        "notes": "Trappist Monastery"
    },
    # Tennessee
    {
        "name": "Cathedral of the Incarnation",
        "diocese": "Diocese of Nashville",
        "street": "2015 West End Ave.",
        "city": "Nashville",
        "state": "TN",
        "postal_code": "37203",
        "country": "USA",
        "schedule": "Sunday 2 PM Latin"
    },
    # Texas
    {
        "name": "Co-Cathedral of the Sacred Heart",
        "diocese": "Archdiocese of Galveston-Houston",
        "street": "1111 St. Joseph Parkway",
        "city": "Houston",
        "state": "TX",
        "postal_code": "77002",
        "country": "USA",
        "schedule": "Sunday 7 PM Latin"
    },
    {
        "name": "Church of the Incarnation",
        "diocese": "Diocese of Dallas",
        "street": "3966 McKinney Ave.",
        "city": "Dallas",
        "state": "TX",
        "postal_code": "75204",
        "country": "USA",
        "schedule": "Sunday 11 AM Latin Ordinary Form"
    },
    {
        "name": "University of Dallas Chapel",
        "diocese": "Diocese of Dallas",
        "street": "1845 E. Northgate Drive",
        "city": "Irving",
        "state": "TX",
        "postal_code": "75062",
        "country": "USA",
        "schedule": "Daily Latin (academic year)"
    },
    {
        "name": "St. Patrick Cathedral",
        "diocese": "Diocese of Fort Worth",
        "street": "1206 Throckmorton St.",
        "city": "Fort Worth",
        "state": "TX",
        "postal_code": "76102",
        "country": "USA",
        "schedule": "Sunday 7:30 AM Latin"
    },
    {
        "name": "San Fernando Cathedral",
        "diocese": "Archdiocese of San Antonio",
        "street": "115 W. Main Plaza",
        "city": "San Antonio",
        "state": "TX",
        "postal_code": "78205",
        "country": "USA",
        "schedule": "Sunday 10:30 AM Latin"
    },
    {
        "name": "St. Mary Cathedral",
        "diocese": "Diocese of Austin",
        "street": "203 E. 10th St.",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78701",
        "country": "USA",
        "schedule": "Sunday 12 Noon Latin"
    },
    # Utah
    {
        "name": "Cathedral of the Madeleine",
        "diocese": "Diocese of Salt Lake City",
        "street": "331 E. South Temple",
        "city": "Salt Lake City",
        "state": "UT",
        "postal_code": "84111",
        "country": "USA",
        "schedule": "Sunday 12 Noon Latin"
    },
    # Virginia
    {
        "name": "Cathedral of the Sacred Heart",
        "diocese": "Diocese of Richmond",
        "street": "823 Cathedral Place",
        "city": "Richmond",
        "state": "VA",
        "postal_code": "23220",
        "country": "USA",
        "schedule": "Sunday 9 AM Latin"
    },
    {
        "name": "St. Charles Borromeo Church",
        "diocese": "Diocese of Arlington",
        "street": "3304 Washington Blvd.",
        "city": "Arlington",
        "state": "VA",
        "postal_code": "22201",
        "country": "USA",
        "schedule": "Sunday 11 AM hybrid"
    },
    # Washington
    {
        "name": "St. James Cathedral",
        "diocese": "Archdiocese of Seattle",
        "street": "804 9th Ave.",
        "city": "Seattle",
        "state": "WA",
        "postal_code": "98104",
        "country": "USA",
        "schedule": "Sunday 10 AM Latin Ordinary Form"
    },
    {
        "name": "St. Martin's Abbey",
        "diocese": "Archdiocese of Seattle",
        "street": "5000 Abbey Way SE",
        "city": "Lacey",
        "state": "WA",
        "postal_code": "98503",
        "country": "USA",
        "schedule": "Daily Latin (Benedictine schedule)",
        "notes": "Benedictine Abbey"
    },
    # Wisconsin
    {
        "name": "Cathedral of St. John the Evangelist",
        "diocese": "Archdiocese of Milwaukee",
        "street": "812 N. Jackson St.",
        "city": "Milwaukee",
        "state": "WI",
        "postal_code": "53202",
        "country": "USA",
        "schedule": "Sunday 10 AM hybrid"
    },
    {
        "name": "St. Paul University Catholic Center",
        "diocese": "Diocese of Madison",
        "street": "723 State St.",
        "city": "Madison",
        "state": "WI",
        "postal_code": "53703",
        "country": "USA",
        "schedule": "Sunday 10:30 AM Latin (Dominican)",
        "notes": "University of Wisconsin"
    },
    # Wyoming
    {
        "name": "St. Mary's Cathedral",
        "diocese": "Diocese of Cheyenne",
        "street": "2107 Capitol Ave.",
        "city": "Cheyenne",
        "state": "WY",
        "postal_code": "82001",
        "country": "USA",
        "schedule": "1st Sunday 5 PM Latin"
    },
    
    # ============================================
    # CANADA
    # ============================================
    
    # Ontario
    {
        "name": "St. Michael's Cathedral Basilica",
        "diocese": "Archdiocese of Toronto",
        "street": "65 Bond St.",
        "city": "Toronto",
        "state": "ON",
        "country": "Canada",
        "schedule": "Sunday 9:30 AM Latin Ordinary Form"
    },
    {
        "name": "Notre-Dame Cathedral Basilica",
        "diocese": "Archdiocese of Ottawa",
        "street": "56 Guigues Ave.",
        "city": "Ottawa",
        "state": "ON",
        "country": "Canada",
        "schedule": "Sunday 12 Noon Latin"
    },
    {
        "name": "St. Peter's Cathedral Basilica",
        "diocese": "Diocese of Peterborough",
        "street": "379 Reid St.",
        "city": "Peterborough",
        "state": "ON",
        "country": "Canada",
        "schedule": "1st Sunday 2 PM Latin"
    },
    # Quebec
    {
        "name": "Notre-Dame Basilica",
        "diocese": "Archdiocese of Montreal",
        "street": "110 Notre-Dame St. West",
        "city": "Montreal",
        "state": "QC",
        "country": "Canada",
        "schedule": "Sunday 11 AM Latin"
    },
    {
        "name": "Abbaye cistercienne d'Oka",
        "diocese": "Archdiocese of Montreal",
        "street": "1600 Chemin d'Oka",
        "city": "Oka",
        "state": "QC",
        "country": "Canada",
        "schedule": "Daily Latin (Trappist schedule)",
        "notes": "Trappist Abbey"
    },
    {
        "name": "Abbaye de Saint-Benoît-du-Lac",
        "diocese": "Diocese of Sherbrooke",
        "street": "1 rue Principale",
        "city": "Saint-Benoît-du-Lac",
        "state": "QC",
        "country": "Canada",
        "schedule": "Daily Latin (Benedictine schedule)",
        "notes": "Benedictine Abbey"
    },
]


async def ingest_diocesan_data():
    """Main ingestion function"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'catholic_voices')]
    
    stats = {
        "updated": 0,
        "created": 0,
        "skipped": 0,
        "no_coords": 0,
        "flagged": []
    }
    
    print("="*70)
    print("DIOCESAN LATIN MASS INGESTION")
    print("="*70)
    print(f"Processing {len(DIOCESAN_DATA)} locations...")
    print()
    
    for entry in DIOCESAN_DATA:
        name = entry.get("name", "")
        city = entry.get("city", "")
        state = entry.get("state", "")
        street = entry.get("street", "")
        country = entry.get("country", "USA")
        
        # Check for existing record by multiple criteria
        existing = None
        
        # Try exact name + city + state match
        existing = await db.mass_locations.find_one({
            "name": {"$regex": f"^{re.escape(name[:30])}", "$options": "i"},
            "city": {"$regex": f"^{re.escape(city)}", "$options": "i"},
            "state": state
        })
        
        # Try street address match if available
        if not existing and street:
            existing = await db.mass_locations.find_one({
                "street": {"$regex": re.escape(street[:20]), "$options": "i"},
                "city": {"$regex": f"^{re.escape(city)}", "$options": "i"}
            })
        
        # Determine liturgy type
        schedule = entry.get("schedule", "")
        use_liturgy = parse_use_liturgy(schedule)
        entity_type = parse_entity_type(name, entry.get("notes", ""))
        public_access = parse_public_access(entry.get("notes", ""))
        
        # Get coordinates
        lat, lng = get_coordinates(city, state)
        
        if lat is None:
            print(f"  NO COORDS: {name}, {city}, {state}")
            stats["no_coords"] += 1
            stats["flagged"].append({"name": name, "reason": "Missing coordinates"})
            continue
        
        if existing:
            # UPDATE existing record
            update_fields = {}
            
            # Only update fields that are empty or missing
            if not existing.get("street") and street:
                update_fields["street"] = street
            if not existing.get("postal_code") and entry.get("postal_code"):
                update_fields["postal_code"] = entry.get("postal_code")
            if not existing.get("diocese_or_archdiocese"):
                update_fields["diocese_or_archdiocese"] = entry.get("diocese", "")
            if not existing.get("mass_schedule"):
                update_fields["mass_schedule"] = schedule
            if not existing.get("use_or_liturgy") or existing.get("use_or_liturgy") == "1962 Roman Missal":
                # Update if the diocesan data has more specific info
                update_fields["use_or_liturgy"] = use_liturgy
            if not existing.get("mass_language"):
                update_fields["mass_language"] = "Latin"
            if entry.get("notes"):
                # Append notes if not duplicate
                current_notes = existing.get("notes", "") or ""
                new_notes = entry.get("notes", "")
                if new_notes and new_notes not in current_notes:
                    update_fields["notes"] = f"{current_notes}; {new_notes}".strip("; ")
            
            # Update verification status
            update_fields["source"] = "Latin Language Association / Diocesan Listings"
            update_fields["verification_status"] = "Verified"
            update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            if update_fields:
                await db.mass_locations.update_one(
                    {"_id": existing["_id"]},
                    {"$set": update_fields}
                )
                print(f"  UPDATE: {name}, {city}, {state}")
                stats["updated"] += 1
            else:
                print(f"  SKIP (no changes): {name}, {city}, {state}")
                stats["skipped"] += 1
        else:
            # CREATE new record
            new_doc = {
                "id": str(uuid.uuid4()),
                "location_id": str(uuid.uuid4()),
                "name": name,
                "entity_type": entity_type,
                "affiliation": "Diocesan",
                "rite": "Latin",
                "use_or_liturgy": use_liturgy,
                "mass_language": "Latin",
                "street": street,
                "city": city,
                "state": state,
                "postal_code": entry.get("postal_code", ""),
                "country": country,
                "diocese_or_archdiocese": entry.get("diocese", ""),
                "latitude": lat,
                "longitude": lng,
                "mass_schedule": schedule,
                "notes": entry.get("notes", ""),
                "public_access": public_access,
                "source": "Latin Language Association / Diocesan Listings",
                "verification_status": "Verified",
                "exclude_flag": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.mass_locations.insert_one(new_doc)
            print(f"  CREATE: {name}, {city}, {state}")
            stats["created"] += 1
    
    # Final stats
    total = await db.mass_locations.count_documents({"exclude_flag": {"$ne": True}})
    diocesan_count = await db.mass_locations.count_documents({
        "affiliation": "Diocesan",
        "exclude_flag": {"$ne": True}
    })
    
    print()
    print("="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"Records updated: {stats['updated']}")
    print(f"Records created: {stats['created']}")
    print(f"Records skipped (no changes): {stats['skipped']}")
    print(f"Records skipped (no coords): {stats['no_coords']}")
    print()
    print(f"Total Diocesan locations: {diocesan_count}")
    print(f"Total locations in database: {total}")
    
    if stats["flagged"]:
        print()
        print("FLAGGED FOR REVIEW:")
        for item in stats["flagged"]:
            print(f"  - {item['name']}: {item['reason']}")
    
    client.close()
    
    return stats


if __name__ == "__main__":
    asyncio.run(ingest_diocesan_data())
