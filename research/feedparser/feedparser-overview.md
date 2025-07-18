# Feedparser Documentation Research

## Overview
- **Current Version**: 6.0.11 (latest on readthedocs), 5.2.0 (pythonhosted)
- **Python Requirement**: >=3.6
- **License**: BSD-2-Clause
- **Maintainer**: Kurt McKee

## Installation
```bash
pip install feedparser
```

## Supported Feed Formats
- RSS 0.9x
- RSS 1.0
- RSS 2.0
- CDF
- Atom 0.3
- Atom 1.0

## Basic Usage Pattern
```python
import feedparser

# Parse a feed from URL
feed = feedparser.parse('http://example.com/feed.xml')

# Parse a feed from file
feed = feedparser.parse('path/to/feed.xml')

# Parse a feed from string
feed = feedparser.parse(feed_string)

# Access feed metadata
print(feed.feed.title)
print(feed.feed.link)
print(feed.feed.description)

# Access feed entries
for entry in feed.entries:
    print(entry.title)
    print(entry.link)
    print(entry.published)
    print(entry.get('published_parsed'))  # structured time
```

## Key Features

### 1. Basic Features
- RSS/Atom feed parsing
- Common element extraction
- Existence testing for elements

### 2. Advanced Features
- Date parsing (automatic conversion to Python datetime)
- HTML sanitization
- Content normalization
- Namespace handling
- Link resolution
- Feed type detection
- Character encoding detection
- Error detection

### 3. HTTP Features
- ETag support
- Last-Modified headers
- User-Agent configuration
- HTTP redirect handling
- Authentication for password-protected feeds

## Data Structure
The parsed feed returns a dictionary-like object with:
- `feed` - Contains feed-level metadata
- `entries` - List of feed items/posts
- `bozo` - Boolean indicating if feed has errors
- `bozo_exception` - The exception if bozo is True

## Error Handling
```python
feed = feedparser.parse(url)
if feed.bozo:
    # Feed has errors but may still have data
    print(f"Feed error: {feed.bozo_exception}")
    # Can still access entries if partially parsed
```

## Common Patterns

### Checking for Required Fields
```python
for entry in feed.entries:
    title = entry.get('title', 'No title')
    link = entry.get('link', '')
    published = entry.get('published', '')
```

### Date Handling
```python
# Published date as string
published_string = entry.published

# Published date as struct_time
published_parsed = entry.published_parsed
```

## Documentation Links
- Main Documentation: https://feedparser.readthedocs.io/en/latest/
- PyPI Page: https://pypi.org/project/feedparser/
- Legacy Documentation: https://pythonhosted.org/feedparser/