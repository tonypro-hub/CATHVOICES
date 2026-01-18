#!/usr/bin/env python3
"""
Simple script to add prayers to the Catholic Voices & Prayers app
Usage: python add_prayer.py
"""

import requests
import json

API_URL = "http://localhost:8001/api/prayers"

def add_prayer():
    print("\n=== Add New Prayer ===\n")
    
    title = input("Prayer Title: ")
    video_id = input("YouTube Video ID: ")
    category = input("Category (e.g., Traditional Prayers, Novenas, The Rosary): ")
    
    print("\nEnter the prayer text (press Ctrl+D or Ctrl+Z when done):")
    print("---")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    prayer_text = '\n'.join(lines)
    
    # Create prayer
    payload = {
        "title": title,
        "videoId": video_id,
        "prayerText": prayer_text,
        "category": category
    }
    
    response = requests.post(API_URL, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Prayer added successfully!")
        print(f"  ID: {result['id']}")
        print(f"  Title: {result['title']}")
        print(f"  Category: {result['category']}")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    add_prayer()
