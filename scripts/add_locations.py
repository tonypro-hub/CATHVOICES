#!/usr/bin/env python3
"""
Script to add mass locations from extracted Excel data to MongoDB.
Uses a simple geocoding approach with city/state coordinates.
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# US City coordinates lookup (approximate city centers)
# This covers cities mentioned in the Excel data
CITY_COORDINATES = {
    # Texas
    ("Arlington", "TX"): (32.7357, -97.1081),
    ("Fort Worth", "TX"): (32.7555, -97.3308),
    ("Katy", "TX"): (29.7858, -95.8245),
    ("Spring", "TX"): (30.0799, -95.4172),
    ("Carthage", "TX"): (32.1576, -94.3374),
    ("North Richland Hills", "TX"): (32.8343, -97.2286),
    ("Austin", "TX"): (30.2672, -97.7431),
    ("Houston", "TX"): (29.7604, -95.3698),
    ("Irving", "TX"): (32.8140, -96.9489),
    ("El Paso", "TX"): (31.7619, -106.4850),
    
    # Alabama
    ("Mobile", "AL"): (30.6954, -88.0399),
    ("Birmingham", "AL"): (33.5207, -86.8025),
    
    # California
    ("Santa Ana", "CA"): (33.7455, -117.8677),
    ("San Jose", "CA"): (37.3382, -121.8863),
    ("Arcadia", "CA"): (34.1397, -118.0353),
    ("San Diego", "CA"): (32.7157, -117.1611),
    ("Sacramento", "CA"): (38.5816, -121.4944),
    ("Bakersfield", "CA"): (35.3733, -119.0187),
    ("North Hollywood", "CA"): (34.1870, -118.3813),
    ("Placentia", "CA"): (33.8722, -117.8703),
    ("Fresno", "CA"): (36.7378, -119.7871),
    ("San Francisco", "CA"): (37.7749, -122.4194),
    
    # Florida
    ("Pinecrest", "FL"): (25.6650, -80.3079),
    ("St. Augustine", "FL"): (29.8946, -81.3145),
    ("Jacksonville", "FL"): (30.3322, -81.6557),
    ("Tampa", "FL"): (27.9506, -82.4572),
    
    # Georgia
    ("Savannah", "GA"): (32.0809, -81.0912),
    ("Atlanta", "GA"): (33.7490, -84.3880),
    
    # Indiana
    ("Indianapolis", "IN"): (39.7684, -86.1581),
    
    # Maryland
    ("Catonsville", "MD"): (39.2721, -76.7319),
    ("Upper Marlboro", "MD"): (38.8154, -76.7497),
    ("Baltimore", "MD"): (39.2904, -76.6122),
    
    # Massachusetts
    ("Chestnut Hill", "MA"): (42.3188, -71.1653),
    ("Boston", "MA"): (42.3601, -71.0589),
    ("Brockton", "MA"): (42.0834, -71.0184),
    
    # Minnesota
    ("Collegeville", "MN"): (45.5947, -94.3625),
    ("Browerville", "MN"): (46.0697, -94.8614),
    ("St. Paul", "MN"): (44.9537, -93.0900),
    ("Duluth", "MN"): (46.7867, -92.1005),
    
    # Missouri
    ("Republic", "MO"): (37.1200, -93.4802),
    ("St. Louis", "MO"): (38.6270, -90.1994),
    
    # Nebraska
    ("Omaha", "NE"): (41.2565, -95.9345),
    
    # New York
    ("Henrietta", "NY"): (43.0548, -77.6339),
    ("Albany", "NY"): (42.6526, -73.7562),
    ("Syracuse", "NY"): (43.0481, -76.1474),
    ("Brooklyn", "NY"): (40.6782, -73.9442),
    ("Binghamton", "NY"): (42.0987, -75.9180),
    ("New York", "NY"): (40.7128, -74.0060),
    ("Rochester", "NY"): (43.1566, -77.6088),
    
    # North Carolina
    ("Jacksonville", "NC"): (34.7541, -77.4302),
    ("Charlotte", "NC"): (35.2271, -80.8431),
    ("Raleigh", "NC"): (35.7796, -78.6382),
    
    # Pennsylvania
    ("Bridgeport", "PA"): (40.1043, -75.3449),
    ("Philadelphia", "PA"): (39.9526, -75.1652),
    ("Scranton", "PA"): (41.4090, -75.6624),
    ("Aliquippa", "PA"): (40.6173, -80.2545),
    ("Ambridge", "PA"): (40.5890, -80.2251),
    ("Uniontown", "PA"): (39.8998, -79.7164),
    ("Greensburg", "PA"): (40.3015, -79.5389),
    ("Pittsburgh", "PA"): (40.4406, -79.9959),
    ("Bethlehem", "PA"): (40.6259, -75.3705),
    ("Olyphant", "PA"): (41.4684, -75.6021),
    ("Warrington", "PA"): (40.2439, -75.1343),
    ("Allentown", "PA"): (40.6084, -75.4902),
    ("Avella", "PA"): (40.2601, -80.4617),
    ("Beaver", "PA"): (40.6951, -80.3045),
    ("Beaverdale", "PA"): (40.3245, -78.6997),
    ("Braddock", "PA"): (40.4037, -79.8684),
    ("Bradenville", "PA"): (40.3284, -79.3192),
    ("Brownsville", "PA"): (40.0237, -79.8839),
    ("Canonsburg", "PA"): (40.2626, -80.1873),
    ("Clairton", "PA"): (40.2923, -79.8820),
    ("Clarence", "PA"): (41.0634, -77.8586),
    ("Clymer", "PA"): (40.6726, -79.0114),
    ("Donora", "PA"): (40.1726, -79.8578),
    ("DuBois", "PA"): (41.1192, -78.7600),
    ("Ernest", "PA"): (40.6762, -79.1747),
    ("Gibsonia", "PA"): (40.6326, -79.9667),
    ("Girard", "PA"): (42.0034, -80.3181),
    ("Hannastown", "PA"): (40.3465, -79.4936),
    ("Hawk Run", "PA"): (40.9270, -78.2164),
    ("Herminie", "PA"): (40.2626, -79.7167),
    ("Hermitage", "PA"): (41.2334, -80.4489),
    ("Homer City", "PA"): (40.5415, -79.1603),
    ("Johnstown", "PA"): (40.3267, -78.9197),
    ("Leisenring", "PA"): (39.9684, -79.6278),
    ("Lyndora", "PA"): (40.8584, -79.9206),
    ("McKeesport", "PA"): (40.3476, -79.8642),
    ("Monessen", "PA"): (40.1526, -79.8878),
    ("Munhall", "PA"): (40.3923, -79.9001),
    ("Nanty Glo", "PA"): (40.4731, -78.8336),
    ("New Salem", "PA"): (39.9312, -79.7953),
    ("North Huntingdon", "PA"): (40.3284, -79.7278),
    ("Northern Cambria", "PA"): (40.6584, -78.7764),
    ("Perryopolis", "PA"): (40.0865, -79.7503),
    ("Scottdale", "PA"): (40.1001, -79.5867),
    ("Sheffield", "PA"): (41.6959, -79.0350),
    ("State College", "PA"): (40.7934, -77.8600),
    ("Latrobe", "PA"): (40.3212, -79.3795),
    ("Windber", "PA"): (40.2398, -78.8342),
    
    # South Carolina
    ("Charleston", "SC"): (32.7765, -79.9311),
    ("Greenville", "SC"): (34.8526, -82.3940),
    
    # Virginia
    ("Potomac Falls", "VA"): (39.0457, -77.3983),
    ("Norfolk", "VA"): (36.8508, -76.2859),
    ("Richmond", "VA"): (37.5407, -77.4360),
    ("Virginia Beach", "VA"): (36.8529, -75.9780),
    
    # Idaho
    ("Post Falls", "ID"): (47.7182, -116.9516),
    ("New Plymouth", "ID"): (43.9696, -116.8185),
    ("St. Maries", "ID"): (47.3143, -116.5624),
    ("Boise", "ID"): (43.6150, -116.2023),
    ("Pocatello", "ID"): (42.8713, -112.4455),
    
    # Ohio
    ("Mingo Junction", "OH"): (40.3220, -80.6098),
    ("Cleveland", "OH"): (41.4993, -81.6944),
    ("Parma", "OH"): (41.4048, -81.7229),
    ("Cincinnati", "OH"): (39.1031, -84.5120),
    ("Columbus", "OH"): (39.9612, -82.9988),
    ("Boardman", "OH"): (41.0245, -80.6626),
    ("Campbell", "OH"): (41.0784, -80.5992),
    ("Pleasant City", "OH"): (39.9037, -81.5579),
    ("Toronto", "OH"): (40.4640, -80.6009),
    ("Youngstown", "OH"): (41.0998, -80.6495),
    
    # West Virginia
    ("Morgantown", "WV"): (39.6295, -79.9559),
    ("Weirton", "WV"): (40.4189, -80.5895),
    ("Charleston", "WV"): (38.3498, -81.6326),
    
    # New Jersey
    ("Whippany", "NJ"): (40.8226, -74.4193),
    ("Woodland Park", "NJ"): (40.8898, -74.1946),
    ("Trenton", "NJ"): (40.2206, -74.7597),
    
    # Arizona
    ("Phoenix", "AZ"): (33.4484, -112.0740),
    ("Tucson", "AZ"): (32.2226, -110.9747),
    
    # Michigan
    ("Warren", "MI"): (42.4901, -83.0270),
    ("Troy", "MI"): (42.6064, -83.1498),
    ("Detroit", "MI"): (42.3314, -83.0458),
    ("West Bloomfield", "MI"): (42.5656, -83.3855),
    ("Oak Park", "MI"): (42.4598, -83.1827),
    ("Grand Rapids", "MI"): (42.9634, -85.6681),
    
    # New Hampshire
    ("Manchester", "NH"): (42.9956, -71.4548),
    
    # Connecticut
    ("Ridgefield", "CT"): (41.2815, -73.4982),
    ("Orange", "CT"): (41.2787, -73.0257),
    ("Hartford", "CT"): (41.7658, -72.6734),
    ("Stamford", "CT"): (41.0534, -73.5387),
    
    # Illinois
    ("Chicago", "IL"): (41.8781, -87.6298),
    
    # Kentucky
    ("Louisville", "KY"): (38.2527, -85.7585),
    
    # Louisiana
    ("New Orleans", "LA"): (29.9511, -90.0715),
    ("Baton Rouge", "LA"): (30.4515, -91.1871),
    
    # Nevada
    ("Las Vegas", "NV"): (36.1699, -115.1398),
    ("Reno", "NV"): (39.5296, -119.8138),
    
    # Wisconsin
    ("Milwaukee", "WI"): (43.0389, -87.9065),
    ("Green Bay", "WI"): (44.5192, -88.0198),
    
    # Oregon
    ("Portland", "OR"): (45.5152, -122.6784),
    ("Eugene", "OR"): (44.0521, -123.0868),
    
    # Utah
    ("Salt Lake City", "UT"): (40.7608, -111.8910),
    
    # Oklahoma
    ("Oklahoma City", "OK"): (35.4676, -97.5164),
    ("Tulsa", "OK"): (36.1540, -95.9928),
    ("Lawton", "OK"): (34.6036, -98.3959),
    
    # Arkansas
    ("Little Rock", "AR"): (34.7465, -92.2896),
    
    # Iowa
    ("Des Moines", "IA"): (41.5868, -93.6250),
    
    # Kansas
    ("Wichita", "KS"): (37.6872, -97.3301),
    ("St. Marys", "KS"): (39.1942, -96.0711),
    
    # Maine
    ("Portland", "ME"): (43.6591, -70.2568),
    
    # Montana
    ("Billings", "MT"): (45.7833, -108.5007),
    ("Helena", "MT"): (46.5927, -112.0361),
    
    # North Dakota
    ("Fargo", "ND"): (46.8772, -96.7898),
    
    # South Dakota
    ("Sioux Falls", "SD"): (43.5446, -96.7311),
    
    # Tennessee
    ("Knoxville", "TN"): (35.9606, -83.9207),
    
    # Washington
    ("Tacoma", "WA"): (47.2529, -122.4443),
    ("Spokane", "WA"): (47.6588, -117.4260),
    ("Seattle", "WA"): (47.6062, -122.3321),
    
    # Wyoming
    ("Cheyenne", "WY"): (41.1400, -104.8202),
    
    # Hawaii
    ("Honolulu", "HI"): (21.3069, -157.8583),
    
    # Alaska
    ("Anchorage", "AK"): (61.2181, -149.9003),
    
    # Colorado
    ("Denver", "CO"): (39.7392, -104.9903),
    ("Colorado Springs", "CO"): (38.8339, -104.8214),
    
    # New Mexico
    ("Albuquerque", "NM"): (35.0844, -106.6504),
    
    # Mississippi
    ("Jackson", "MS"): (32.2988, -90.1848),
    
    # Delaware
    ("Wilmington", "DE"): (39.7391, -75.5398),
}

# Locations data extracted from the Excel file
LOCATIONS_DATA = [
    # Ordinariate locations
    {"name": "St. Peter the Rock Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "street": "1408 North Davis Drive", "city": "Arlington", "state": "TX"},
    {"name": "St. Timothy Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Fort Worth", "state": "TX"},
    {"name": "St. Margaret Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Katy", "state": "TX"},
    {"name": "St. Gregory the Great Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Mobile", "state": "AL"},
    {"name": "St. John Henry Newman Church (Santa Ana)", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Santa Ana", "state": "CA"},
    {"name": "San Agustin Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Pinecrest", "state": "FL"},
    {"name": "St. James Mission", "entity_type": "Mission", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "St. Augustine", "state": "FL"},
    {"name": "Our Lady of Mount Carmel Community (Savannah)", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Savannah", "state": "GA"},
    {"name": "St. Joseph of Arimathea Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Indianapolis", "state": "IN"},
    {"name": "St. Timothy Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Catonsville", "state": "MD"},
    {"name": "St. Gregory the Great Church (Boston)", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Chestnut Hill", "state": "MA"},
    {"name": "St. Bede the Venerable Society", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Collegeville", "state": "MN"},
    {"name": "St. George Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Republic", "state": "MO"},
    {"name": "St. Barnabas Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Omaha", "state": "NE"},
    {"name": "St. Alban Fellowship", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Henrietta", "state": "NY"},
    {"name": "Our Lady of Good Counsel Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Jacksonville", "state": "NC"},
    {"name": "Our Lady of Mount Carmel Church (Philadelphia)", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Bridgeport", "state": "PA"},
    {"name": "St. Michael the Archangel Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Philadelphia", "state": "PA"},
    {"name": "St. Thomas More Parish", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Scranton", "state": "PA"},
    {"name": "Corpus Christi Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Charleston", "state": "SC"},
    {"name": "St. Anselm Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Greenville", "state": "SC"},
    {"name": "St. John Fisher Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Potomac Falls", "state": "VA"},
    {"name": "St. Thomas the Apostle Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Austin", "state": "TX"},
    {"name": "St. Mary the Virgin Church", "entity_type": "Parish", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Arlington", "state": "TX"},
    {"name": "Our Lady of Hope Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Louisville", "state": "KY"},
    {"name": "St. Alban Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Rochester", "state": "NY"},
    {"name": "All Saints Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Denver", "state": "CO"},
    {"name": "St. Edmund of Canterbury Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "San Diego", "state": "CA"},
    {"name": "Our Lady of Walsingham Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Seattle", "state": "WA"},
    {"name": "St. Gregory the Great Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Portland", "state": "OR"},
    {"name": "Holy Trinity Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Phoenix", "state": "AZ"},
    {"name": "St. John Henry Newman Community", "entity_type": "Community", "affiliation": "Ordinariate", "rite": "Latin", "use_or_liturgy": "Ordinariate Use", "city": "Las Vegas", "state": "NV"},
    
    # SSPX locations
    {"name": "Immaculate Conception Church", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "495 Lincoln Street", "city": "Post Falls", "state": "ID"},
    {"name": "Our Lady Help of Christians Church", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "1565 S. White Road", "city": "San Jose", "state": "CA"},
    {"name": "Our Lady of the Sun Church", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "El Paso", "state": "TX"},
    {"name": "Our Lady of Guadalupe Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "221 W. Elm Street", "city": "New Plymouth", "state": "ID"},
    {"name": "St. Joseph's Mission", "entity_type": "Mission", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "81525 State Hwy 3", "city": "St. Maries", "state": "ID"},
    {"name": "SSPX Boise Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Boise", "state": "ID"},
    {"name": "SSPX Pocatello Mission", "entity_type": "Mission", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Pocatello", "state": "ID"},
    {"name": "St. Michael the Archangel Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "24001 Aldine Westfield Road", "city": "Spring", "state": "TX"},
    {"name": "Jesus and Mary Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Carthage", "state": "TX"},
    {"name": "SSPX Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "North Richland Hills", "state": "TX"},
    {"name": "St. Pius X Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "7604 S. Osborne Rd", "city": "Upper Marlboro", "state": "MD"},
    {"name": "St. Ignatius Retreat House", "entity_type": "Retreat", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "street": "209 Tackora Trail", "city": "Ridgefield", "state": "CT"},
    {"name": "Our Lady of Guadalupe Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Browerville", "state": "MN"},
    {"name": "Immaculate Conception Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Arcadia", "state": "CA"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "San Diego", "state": "CA"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Sacramento", "state": "CA"},
    {"name": "St. Therese of Lisieux Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Bakersfield", "state": "CA"},
    {"name": "Our Lady of Sorrows Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Tucson", "state": "AZ"},
    {"name": "St. Vincent Ferrer Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Orange", "state": "CT"},
    {"name": "Our Lady Star of the Sea Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Jacksonville", "state": "FL"},
    {"name": "Holy Family Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Tampa", "state": "FL"},
    {"name": "St. John the Baptist Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Chicago", "state": "IL"},
    {"name": "Our Lady of Sorrows Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Indianapolis", "state": "IN"},
    {"name": "St. Mary's Academy and Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "St. Marys", "state": "KS"},
    {"name": "Queen of All Saints Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Louisville", "state": "KY"},
    {"name": "St. Theresa Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "New Orleans", "state": "LA"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Boston", "state": "MA"},
    {"name": "Our Lady of the Rosary Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Detroit", "state": "MI"},
    {"name": "St. Vincent de Paul Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "St. Paul", "state": "MN"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "St. Louis", "state": "MO"},
    {"name": "Holy Cross Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Omaha", "state": "NE"},
    {"name": "St. Jude Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Las Vegas", "state": "NV"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Albany", "state": "NY"},
    {"name": "St. Thomas Aquinas Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Syracuse", "state": "NY"},
    {"name": "Our Lady of Lourdes Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Cincinnati", "state": "OH"},
    {"name": "St. Isidore Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Columbus", "state": "OH"},
    {"name": "Our Lady of Czestochowa Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Philadelphia", "state": "PA"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Pittsburgh", "state": "PA"},
    {"name": "Our Lady Help of Christians Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Charleston", "state": "SC"},
    {"name": "Our Lady of Assumption Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Norfolk", "state": "VA"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Richmond", "state": "VA"},
    {"name": "Immaculate Heart of Mary Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Milwaukee", "state": "WI"},
    {"name": "St. Mary's Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Green Bay", "state": "WI"},
    {"name": "Holy Family Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Portland", "state": "OR"},
    {"name": "St. Patrick Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Salt Lake City", "state": "UT"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Oklahoma City", "state": "OK"},
    {"name": "Our Lady of Sorrows Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Birmingham", "state": "AL"},
    {"name": "St. Michael Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Little Rock", "state": "AR"},
    {"name": "St. Isidore Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Des Moines", "state": "IA"},
    {"name": "St. Joan of Arc Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Wichita", "state": "KS"},
    {"name": "St. Thomas More Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Baton Rouge", "state": "LA"},
    {"name": "Our Lady of Perpetual Help Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Portland", "state": "ME"},
    {"name": "St. Athanasius Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Grand Rapids", "state": "MI"},
    {"name": "St. John Vianney Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Duluth", "state": "MN"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Billings", "state": "MT"},
    {"name": "St. Michael Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Charlotte", "state": "NC"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Fargo", "state": "ND"},
    {"name": "Our Lady of the Mountains Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Reno", "state": "NV"},
    {"name": "St. Anne Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Manchester", "state": "NH"},
    {"name": "St. Pius V Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Allentown", "state": "PA"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Sioux Falls", "state": "SD"},
    {"name": "Immaculate Heart Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Knoxville", "state": "TN"},
    {"name": "Our Lady of Guadalupe Chapel (Tacoma)", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Tacoma", "state": "WA"},
    {"name": "St. Patrick Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Charleston", "state": "WV"},
    {"name": "St. Theresa Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Cheyenne", "state": "WY"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Honolulu", "state": "HI"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Anchorage", "state": "AK"},
    {"name": "St. Pius X Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Tulsa", "state": "OK"},
    {"name": "Our Lady of Fatima Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Sacramento", "state": "CA"},
    {"name": "St. Thomas More Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Fresno", "state": "CA"},
    {"name": "Queen of All Saints Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "San Francisco", "state": "CA"},
    {"name": "Our Lady of Good Counsel Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Spokane", "state": "WA"},
    {"name": "St. Patrick Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Portland", "state": "OR"},
    {"name": "Holy Family Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Eugene", "state": "OR"},
    {"name": "St. Bernadette Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Albuquerque", "state": "NM"},
    {"name": "Our Lady of Sorrows Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Colorado Springs", "state": "CO"},
    {"name": "St. Francis de Sales Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Salt Lake City", "state": "UT"},
    {"name": "Our Lady of Perpetual Help Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Boise", "state": "ID"},
    {"name": "St. Anthony Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Helena", "state": "MT"},
    {"name": "St. Athanasius Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Jackson", "state": "MS"},
    {"name": "St. Joseph Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Mobile", "state": "AL"},
    {"name": "Our Lady of Victory Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Raleigh", "state": "NC"},
    {"name": "St. John Fisher Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Virginia Beach", "state": "VA"},
    {"name": "Immaculate Heart of Mary Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Baltimore", "state": "MD"},
    {"name": "St. Augustine Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Wilmington", "state": "DE"},
    {"name": "Our Lady of Lourdes Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Trenton", "state": "NJ"},
    {"name": "St. Thomas More Chapel", "entity_type": "Chapel", "affiliation": "SSPX", "rite": "Latin", "use_or_liturgy": "1962 Roman Missal", "city": "Hartford", "state": "CT"},
    
    # Eastern Catholic - Byzantine
    {"name": "St. George Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Aliquippa", "state": "PA"},
    {"name": "St. Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Ambridge", "state": "PA"},
    {"name": "St. John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Uniontown", "state": "PA"},
    {"name": "St. Nicholas of Myra Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Greensburg", "state": "PA"},
    {"name": "St. John the Baptist Byzantine Catholic Church (Mingo Junction)", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Mingo Junction", "state": "OH"},
    {"name": "Holy Protection of the Mother of God Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Morgantown", "state": "WV"},
    {"name": "Assumption of the Mother of God Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Weirton", "state": "WV"},
    {"name": "St. Michael Ruthenian Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Binghamton", "state": "NY"},
    {"name": "St. Mary Byzantine Catholic Church (Ruthenian)", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Cleveland", "state": "OH"},
    {"name": "Holy Spirit Byzantine Catholic Church (Ruthenian)", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Parma", "state": "OH"},
    {"name": "St. Stephen Byzantine Catholic Cathedral", "entity_type": "Cathedral", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "city": "Phoenix", "state": "AZ"},
    
    # Byzantine Catholic Churches with addresses from the Excel
    {"name": "Saint John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "176 Cross Creek Road", "city": "Avella", "state": "PA"},
    {"name": "Saint Nicholas of Myra Byzantine Catholic Chapel", "entity_type": "Chapel", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "5400 Tuscarawas Road", "city": "Beaver", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "Stewart Street", "city": "Beaverdale", "state": "PA"},
    {"name": "Saints Peter & Paul Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "431 George Street", "city": "Braddock", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "112 St. Mary's Way", "city": "Bradenville", "state": "PA"},
    {"name": "Saint Nicholas Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "302 3rd Avenue", "city": "Brownsville", "state": "PA"},
    {"name": "Saint Michael Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "166 East College Street", "city": "Canonsburg", "state": "PA"},
    {"name": "Ascension of Our Lord Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "318 Park Avenue", "city": "Clairton", "state": "PA"},
    {"name": "Dormition of the Mother of God Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "104 Byzantine Lane", "city": "Clarence", "state": "PA"},
    {"name": "Saint Anne Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "48 Franklin Street", "city": "Clymer", "state": "PA"},
    {"name": "Saint Michael the Archangel Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "511 Murray Avenue", "city": "Donora", "state": "PA"},
    {"name": "Nativity of the Mother of God Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "200 McCullough Street", "city": "DuBois", "state": "PA"},
    {"name": "Saint Jude Thaddeus Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "320 Main Street", "city": "Ernest", "state": "PA"},
    {"name": "Saint Andrew the Apostle Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "235 Logan Road", "city": "Gibsonia", "state": "PA"},
    {"name": "Saints Cyril and Methodius Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1022 Tilden Drive", "city": "Girard", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "Pollins Avenue", "city": "Hannastown", "state": "PA"},
    {"name": "St. John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "24 Fulton Street", "city": "Hawk Run", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "5 2nd Street", "city": "Herminie", "state": "PA"},
    {"name": "Saint Michael Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "2230 Highland Road", "city": "Hermitage", "state": "PA"},
    {"name": "Saint Mary's Holy Protection Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "279 Yellow Creek Street", "city": "Homer City", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "411 Power Street", "city": "Johnstown", "state": "PA"},
    {"name": "Saint Stephen Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "3120 West Crawford Avenue", "city": "Leisenring", "state": "PA"},
    {"name": "Saint John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "105 Kohler Avenue", "city": "Lyndora", "state": "PA"},
    {"name": "Saint Nicholas of Myra Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "410 West 6th Avenue", "city": "McKeesport", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church of the Assumption", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "125 McKee Avenue", "city": "Monessen", "state": "PA"},
    {"name": "Saint John the Baptist Byzantine Catholic Cathedral", "entity_type": "Cathedral", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "210 Greentree Road", "city": "Munhall", "state": "PA"},
    {"name": "Saint Nicholas of Myra Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1191 2nd Street", "city": "Nanty Glo", "state": "PA"},
    {"name": "Saint Mary Assumption Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "12 Center Street Extension", "city": "New Salem", "state": "PA"},
    {"name": "Saint Stephen Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "90 Bethel Road", "city": "North Huntingdon", "state": "PA"},
    {"name": "Saint John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "719 Chestnut Avenue", "city": "Northern Cambria", "state": "PA"},
    {"name": "Saint Nicholas Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "102 Railroad Street", "city": "Perryopolis", "state": "PA"},
    {"name": "Saint Pius X Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "2336 Brownsville Road", "city": "Pittsburgh", "state": "PA"},
    {"name": "Saint John Chrysostom Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "506 Saline Street", "city": "Pittsburgh", "state": "PA"},
    {"name": "Saint John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1720 Jane Street", "city": "Pittsburgh", "state": "PA"},
    {"name": "Holy Spirit Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "4815 Fifth Avenue", "city": "Pittsburgh", "state": "PA"},
    {"name": "Saint John the Baptist Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "525 Porter Avenue", "city": "Scottdale", "state": "PA"},
    {"name": "Saint Michael the Archangel Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "407 School Street", "city": "Sheffield", "state": "PA"},
    {"name": "State College Byzantine Catholic Community", "entity_type": "Community", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1606 Norma St", "city": "State College", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "4480 Route 981", "city": "Latrobe", "state": "PA"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "803 Somerset Avenue", "city": "Windber", "state": "PA"},
    {"name": "Saint Nicholas of Myra Byzantine Catholic Mission", "entity_type": "Mission", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "2435 South Carrollton Avenue", "city": "New Orleans", "state": "LA"},
    {"name": "Infant Jesus of Prague Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "7754 South Avenue", "city": "Boardman", "state": "OH"},
    {"name": "Saint Michael Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "463 Robinson Road", "city": "Campbell", "state": "OH"},
    {"name": "Saint Michael Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "408 Walnut Street", "city": "Pleasant City", "state": "OH"},
    {"name": "Saint Joseph Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "814 North 5th Street", "city": "Toronto", "state": "OH"},
    {"name": "Saint Nicholas Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1898 Wilson Avenue", "city": "Youngstown", "state": "OH"},
    {"name": "Saint Mary Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "356 South Belle Vista Avenue", "city": "Youngstown", "state": "OH"},
    {"name": "Byzantine Catholic Mission Holy Family Church", "entity_type": "Mission", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1010 NW 82nd St", "city": "Lawton", "state": "OK"},
    {"name": "The Byzantine Catholic Community of Austin", "entity_type": "Community", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1610 E 11th St", "city": "Austin", "state": "TX"},
    {"name": "Saint John Chrysostom Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "5402 Acorn Street", "city": "Houston", "state": "TX"},
    {"name": "Saint Basil the Great Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Byzantine", "use_or_liturgy": "Divine Liturgy", "street": "1118 East Union Bower Road", "city": "Irving", "state": "TX"},
    
    # Ukrainian Catholic
    {"name": "St. Nicholas Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Philadelphia", "state": "PA"},
    {"name": "St. John the Baptist Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Whippany", "state": "NJ"},
    {"name": "St. Josaphat Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Bethlehem", "state": "PA"},
    {"name": "Sts. Cyril and Methodius Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Olyphant", "state": "PA"},
    {"name": "St. Anne Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Warrington", "state": "PA"},
    {"name": "St. George Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "New York", "state": "NY"},
    {"name": "Cathedral of St. Vladimir", "entity_type": "Cathedral", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Stamford", "state": "CT"},
    {"name": "St. Michael Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Hartford", "state": "CT"},
    {"name": "St. Nicholas Ukrainian Catholic Cathedral", "entity_type": "Cathedral", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Chicago", "state": "IL"},
    {"name": "Ss. Volodymyr and Olha Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Chicago", "state": "IL"},
    {"name": "St. Joseph Ukrainian Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Ukrainian", "use_or_liturgy": "Divine Liturgy", "city": "Chicago", "state": "IL"},
    
    # Melkite Catholic
    {"name": "St. Ann Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Woodland Park", "state": "NJ"},
    {"name": "Virgin Mary Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Brooklyn", "state": "NY"},
    {"name": "St. John Chrysostom Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Atlanta", "state": "GA"},
    {"name": "St. George Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Birmingham", "state": "AL"},
    {"name": "St. John of the Desert Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Phoenix", "state": "AZ"},
    {"name": "St. Anne Melkite Co-Cathedral", "entity_type": "Co-Cathedral", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "North Hollywood", "state": "CA"},
    {"name": "Holy Cross Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Placentia", "state": "CA"},
    {"name": "St. George Melkite Catholic Church (Sacramento)", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Sacramento", "state": "CA"},
    {"name": "Our Lady of Redemption Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Warren", "state": "MI"},
    {"name": "Our Lady of the Cedars Melkite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Melkite", "use_or_liturgy": "Divine Liturgy", "city": "Manchester", "state": "NH"},
    
    # Chaldean Catholic
    {"name": "St. Joseph Chaldean Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Chaldean", "use_or_liturgy": "Divine Liturgy", "city": "Troy", "state": "MI"},
    {"name": "Sacred Heart Chaldean Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Chaldean", "use_or_liturgy": "Divine Liturgy", "city": "Detroit", "state": "MI"},
    {"name": "St. Thomas the Apostle Chaldean Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Chaldean", "use_or_liturgy": "Divine Liturgy", "city": "West Bloomfield", "state": "MI"},
    {"name": "Mar Addai Chaldean Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Chaldean", "use_or_liturgy": "Divine Liturgy", "city": "Oak Park", "state": "MI"},
    {"name": "St. George Chaldean Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Chaldean", "use_or_liturgy": "Divine Liturgy", "city": "Chicago", "state": "IL"},
    {"name": "Our Lady of Chaldeans Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Chaldean", "use_or_liturgy": "Divine Liturgy", "city": "Phoenix", "state": "AZ"},
    
    # Other Eastern Catholic
    {"name": "St. Theresa Maronite Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Maronite", "use_or_liturgy": "Divine Liturgy", "city": "Brockton", "state": "MA"},
    {"name": "St. Mary Romanian Byzantine Catholic Church", "entity_type": "Parish", "affiliation": "Eastern Catholic", "rite": "Romanian", "use_or_liturgy": "Divine Liturgy", "city": "Cleveland", "state": "OH"},
    {"name": "Our Lady of Nareg Armenian Catholic Cathedral", "entity_type": "Cathedral", "affiliation": "Eastern Catholic", "rite": "Armenian", "use_or_liturgy": "Divine Liturgy", "city": "New York", "state": "NY"},
    {"name": "St. Mary Queen of Peace Syro-Malankara Cathedral", "entity_type": "Cathedral", "affiliation": "Eastern Catholic", "rite": "Syro-Malankara", "use_or_liturgy": "Divine Liturgy", "city": "Elmont", "state": "NY"},
]

# Sedevacantist groups to exclude
EXCLUDED_GROUPS = [
    'cmri', 'sspv', 'sspx-mc', 'sspx marian corps',
    'sedevacantist', 'vacantist', 'non una cum'
]

def check_exclusion(name: str, affiliation: str, notes: str = "") -> tuple:
    """Check if location should be excluded based on sedevacantist affiliation"""
    combined_text = f"{name} {affiliation} {notes}".lower()
    for excluded in EXCLUDED_GROUPS:
        if excluded in combined_text:
            return True, f"Matches excluded group: {excluded}"
    return False, None

def get_coordinates(city: str, state: str) -> tuple:
    """Get coordinates for a city/state pair"""
    key = (city, state)
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]
    
    # Try fuzzy matching for city names with slight variations
    for (c, s), coords in CITY_COORDINATES.items():
        if s == state and (c.lower() in city.lower() or city.lower() in c.lower()):
            return coords
    
    return None, None

async def add_locations():
    """Add all locations from the Excel data to MongoDB"""
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'catholic_voices')]
    
    inserted_count = 0
    skipped_count = 0
    no_coords_count = 0
    
    for loc_data in LOCATIONS_DATA:
        name = loc_data.get('name', '')
        city = loc_data.get('city', '')
        state = loc_data.get('state', '')
        
        # Check for duplicates
        existing = await db.mass_locations.find_one({
            "name": name,
            "city": city,
            "state": state
        })
        
        if existing:
            print(f"SKIP (exists): {name}, {city}, {state}")
            skipped_count += 1
            continue
        
        # Get coordinates
        lat, lng = get_coordinates(city, state)
        
        if lat is None or lng is None:
            print(f"NO COORDS: {name}, {city}, {state}")
            no_coords_count += 1
            continue
        
        # Check for exclusion
        exclude_flag, exclude_reason = check_exclusion(
            name,
            loc_data.get('affiliation', ''),
            loc_data.get('notes', '')
        )
        
        # Create location document
        location_doc = {
            "id": str(uuid.uuid4()),
            "location_id": str(uuid.uuid4()),
            "name": name,
            "entity_type": loc_data.get('entity_type', 'Parish'),
            "jurisdiction": loc_data.get('jurisdiction', 'Diocese'),
            "affiliation": loc_data.get('affiliation', ''),
            "rite": loc_data.get('rite', 'Latin'),
            "use_or_liturgy": loc_data.get('use_or_liturgy', ''),
            "street": loc_data.get('street', ''),
            "city": city,
            "state": state,
            "zip_code": loc_data.get('zip_code', ''),
            "country": loc_data.get('country', 'USA'),
            "latitude": lat,
            "longitude": lng,
            "mass_schedule_url": loc_data.get('mass_schedule_url'),
            "website_url": loc_data.get('website_url'),
            "phone": loc_data.get('phone'),
            "notes": loc_data.get('notes'),
            "exclude_flag": exclude_flag,
            "exclude_reason": exclude_reason,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.mass_locations.insert_one(location_doc)
        print(f"INSERT: {name}, {city}, {state}")
        inserted_count += 1
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Inserted: {inserted_count}")
    print(f"Skipped (already exists): {skipped_count}")
    print(f"Skipped (no coordinates): {no_coords_count}")
    print(f"Total processed: {len(LOCATIONS_DATA)}")
    
    # Get final count
    total = await db.mass_locations.count_documents({"exclude_flag": {"$ne": True}})
    print(f"\nTotal locations in database: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_locations())
