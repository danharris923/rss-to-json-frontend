#!/usr/bin/env python3
"""
Affiliate link processor for RSS feeds.
Processes and rewrites links to include affiliate tags.
"""

import re
import urllib.parse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from affiliate_config import (
    AFFILIATE_TAGS, 
    AFFILIATE_URL_PATTERNS, 
    DEFAULT_AFFILIATE_SYSTEM,
    UTM_PARAMS,
    get_affiliate_tag,
    should_affiliate_link,
    get_utm_string
)
from link_resolver import LinkResolver

class AffiliateProcessor:
    """Process and rewrite affiliate links in RSS feed content."""
    
    def __init__(self, config=None):
        self.config = config or DEFAULT_AFFILIATE_SYSTEM
        self.processed_count = 0
        self.skipped_count = 0
        self.resolver = LinkResolver()
    
    def process_rss_entry(self, entry):
        """Process a single RSS entry and rewrite affiliate links."""
        original_link = entry.get('link', '')
        
        # First resolve the link to get the clean final URL
        resolved_link = self.resolver.resolve_url(original_link)
        
        # Then process the resolved link for affiliate tags
        processed_link = self.process_link(resolved_link)
        entry['link'] = processed_link
        
        # Track if we processed this link
        if processed_link != original_link:
            self.processed_count += 1
            entry['affiliate_processed'] = True
            entry['original_link'] = original_link  # Keep original for debugging
            entry['resolved_link'] = resolved_link  # Keep resolved for debugging
        else:
            self.skipped_count += 1
            entry['affiliate_processed'] = False
        
        return entry
    
    def process_link(self, url):
        """Process a single URL: resolve → clean → add affiliate tags if available."""
        if not url or not self.config.get('enabled', True):
            return url
        
        try:
            # Step 1: Resolve the URL to get the final destination
            resolved_url = self.resolver.resolve_url(url)
            
            # Step 2: Parse the resolved URL
            parsed = urlparse(resolved_url)
            domain = parsed.netloc.lower()
            
            # Step 3: Check if this domain should be processed
            if not should_affiliate_link(resolved_url):
                return resolved_url  # Return clean resolved URL
            
            # Step 4: Get affiliate tag for this domain
            affiliate_tag = get_affiliate_tag(domain)
            
            # Step 5: If no affiliate tag available, return clean URL
            if not affiliate_tag:
                return resolved_url  # Clean URL, no affiliate tag
            
            # Step 6: Add affiliate tag to clean URL
            return self._add_affiliate_tag(resolved_url, domain, affiliate_tag)
            
        except Exception as e:
            print(f"Error processing affiliate link {url}: {e}")
            return url
    
    def _apply_affiliate_patterns(self, url, domain):
        """Apply specific affiliate URL patterns."""
        for affiliate_domain, pattern_config in AFFILIATE_URL_PATTERNS.items():
            if affiliate_domain in domain:
                pattern = pattern_config['pattern']
                rewrite = pattern_config['rewrite']
                affiliate_tag = get_affiliate_tag(domain)
                
                if affiliate_tag:
                    # Apply the pattern replacement
                    new_url = re.sub(pattern, rewrite.format(affiliate_tag=affiliate_tag), url)
                    if new_url != url:
                        return self._add_utm_params(new_url)
        
        return url
    
    def _add_affiliate_tag(self, url, domain, affiliate_tag):
        """Add affiliate tag to clean URL based on merchant."""
        try:
            # Parse URL components
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Add affiliate tag based on domain
            if 'amazon' in domain:
                query_params['tag'] = [affiliate_tag]
            elif 'walmart' in domain:
                query_params['affiliate'] = [affiliate_tag]
            elif 'bestbuy' in domain:
                query_params['ref'] = [affiliate_tag]
            elif 'staples' in domain:
                query_params['aff'] = [affiliate_tag]
            elif 'adidas' in domain:
                query_params['aff'] = [affiliate_tag]
            else:
                # Generic affiliate parameter
                query_params['aff'] = [affiliate_tag]
            
            # Rebuild URL with affiliate parameters
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            new_url = urlunparse(new_parsed)
            
            return self._add_utm_params(new_url)
            
        except Exception as e:
            print(f"Error adding affiliate tag to {url}: {e}")
            return url
    
    def _add_utm_params(self, url):
        """Add UTM tracking parameters to URL."""
        if not self.config.get('add_utm_params', True):
            return url
        
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Add UTM parameters
            for key, value in UTM_PARAMS.items():
                if key not in query_params:
                    query_params[key] = [value]
            
            # Rebuild URL
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            return urlunparse(new_parsed)
            
        except Exception as e:
            print(f"Error adding UTM params to {url}: {e}")
            return url
    
    def create_redirect_link(self, original_url, title=""):
        """Create a redirect link through your own domain for tracking."""
        if not self.config.get('enabled', True):
            return original_url
        
        redirect_domain = self.config.get('redirect_domain')
        redirect_path = self.config.get('redirect_path', '/go/')
        
        if not redirect_domain:
            return original_url
        
        # Create tracking parameters
        tracking_params = {
            'url': original_url,
            'source': 'rss_feed',
            'title': title[:100] if title else '',  # Limit title length
        }
        
        # Add UTM parameters
        tracking_params.update(UTM_PARAMS)
        
        # Build redirect URL
        redirect_url = f"https://{redirect_domain}{redirect_path}?{urlencode(tracking_params)}"
        return redirect_url
    
    def get_stats(self):
        """Get processing statistics."""
        return {
            'processed': self.processed_count,
            'skipped': self.skipped_count,
            'total': self.processed_count + self.skipped_count,
            'success_rate': self.processed_count / (self.processed_count + self.skipped_count) * 100 if (self.processed_count + self.skipped_count) > 0 else 0
        }

def process_feed_entries(entries, config=None):
    """Process a list of RSS feed entries and add affiliate links."""
    processor = AffiliateProcessor(config)
    
    processed_entries = []
    for entry in entries:
        processed_entry = processor.process_rss_entry(entry.copy())
        processed_entries.append(processed_entry)
    
    # Print statistics
    stats = processor.get_stats()
    print(f"Affiliate processing complete:")
    print(f"  - Processed: {stats['processed']} links")
    print(f"  - Skipped: {stats['skipped']} links")
    print(f"  - Success rate: {stats['success_rate']:.1f}%")
    
    return processed_entries

# Example usage and testing
if __name__ == "__main__":
    # Test affiliate processing
    test_entries = [
        {
            'title': 'Test Amazon Deal',
            'link': 'https://www.amazon.ca/dp/B08N5WRWNW',
            'published': '2024-01-01T00:00:00Z'
        },
        {
            'title': 'Test Walmart Deal',
            'link': 'https://www.walmart.ca/en/ip/some-product/123456',
            'published': '2024-01-01T00:00:00Z'
        },
        {
            'title': 'Test Regular Link',
            'link': 'https://example.com/some-page',
            'published': '2024-01-01T00:00:00Z'
        }
    ]
    
    print("Testing affiliate processing...")
    processed = process_feed_entries(test_entries)
    
    for entry in processed:
        print(f"Title: {entry['title']}")
        print(f"Original vs Processed: {entry['link']}")
        print(f"Affiliate processed: {entry['affiliate_processed']}")
        print("---")