#!/usr/bin/env python3
"""
RSS to JSON converter script
Usage: python rss_to_json.py [--url RSS_URL] [--output OUTPUT_FILE]
"""

import feedparser
import json
import argparse
import sys
import time
from pathlib import Path
from urllib.error import URLError
from datetime import datetime

# Default RSS feed URL - using a reliable feed for testing
DEFAULT_FEED_URL = "https://rss.cnn.com/rss/edition.rss"


def parse_rss_feed(feed_url):
    """
    Parse RSS feed with comprehensive error handling.
    
    Args:
        feed_url (str): URL of the RSS feed to parse
        
    Returns:
        dict: Result with 'entries' key on success or 'error' key on failure
    """
    try:
        print(f"Fetching RSS feed from: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        # Check for bozo errors (malformed feeds)
        if feed.bozo:
            print(f"Warning: Feed is malformed - {feed.bozo_exception}")
            # Continue processing despite malformation as per PRP requirements
            
        # Check HTTP status if available
        if hasattr(feed, 'status'):
            if feed.status == 404:
                return {'error': 'Feed not found (404)', 'status': 404}
            elif feed.status == 403:
                return {'error': 'Access forbidden (403)', 'status': 403}
            elif feed.status == 500:
                return {'error': 'Server error (500)', 'status': 500}
            elif feed.status != 200:
                return {'error': f'HTTP error {feed.status}', 'status': feed.status}
                
        # Check for entries
        if not feed.entries:
            return {'error': 'No entries found in feed', 'entries': []}
            
        # Process entries with validation
        entries = []
        for entry in feed.entries:
            # Validate required fields (title and link)
            if entry.get('title') and entry.get('link'):
                # Convert published date to ISO format if available
                published_iso = ''
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', entry.published_parsed)
                    except:
                        published_iso = entry.get('published', '')
                else:
                    published_iso = entry.get('published', '')
                
                entries.append({
                    'title': entry.title.strip(),
                    'link': entry.link.strip(),
                    'published': published_iso
                })
            else:
                print(f"Warning: Skipping entry without title or link: {entry.get('title', 'No title')}")
                
        # Validate we have at least one valid entry
        if not entries:
            return {'error': 'No valid entries found (missing title or link)', 'entries': []}
            
        print(f"Successfully parsed {len(entries)} valid entries")
        return {'entries': entries}
        
    except URLError as e:
        return {'error': f'URL Error: {str(e)}'}
    except Exception as e:
        return {'error': f'Failed to parse feed: {str(e)}'}


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(description='Convert RSS feed to JSON')
    parser.add_argument('--url', default=DEFAULT_FEED_URL, 
                        help='RSS feed URL to parse')
    parser.add_argument('--output', default='public/feed.json',
                        help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Validate URL format
    if not args.url.startswith(('http://', 'https://')):
        print(f"Error: Invalid URL format: {args.url}", file=sys.stderr)
        sys.exit(1)
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse the feed
    result = parse_rss_feed(args.url)
    
    if 'error' in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Add metadata to output
    output_data = {
        'feed_url': args.url,
        'updated': datetime.now().isoformat() + 'Z',
        'entries': result['entries']
    }
    
    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully wrote {len(result['entries'])} entries to {output_path}")
        
        # Log sample entry for verification
        if result['entries']:
            sample = result['entries'][0]
            print(f"Sample entry: {sample['title'][:50]}...")
            
    except Exception as e:
        print(f"Error writing output file: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()