#!/usr/bin/env python3
"""
Link resolver for affiliate processing.
Resolves redirects and extracts clean URLs before affiliate processing.
"""

import requests
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urllib.error import URLError
import time

class LinkResolver:
    """Resolve affiliate links and extract clean URLs."""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def resolve_url(self, url):
        """
        Resolve a URL to its final destination, following redirects.
        
        Args:
            url (str): URL to resolve
            
        Returns:
            str: Final resolved URL or original URL if resolution fails
        """
        try:
            # First check if it's already a direct product URL
            if self._is_direct_product_url(url):
                return self._clean_url(url)
            
            # Follow redirects to get final URL
            response = self.session.head(url, allow_redirects=True, timeout=self.timeout)
            final_url = response.url
            
            # Clean the final URL
            return self._clean_url(final_url)
            
        except Exception as e:
            print(f"Warning: Could not resolve URL {url}: {e}")
            return url
    
    def _is_direct_product_url(self, url):
        """Check if URL is already a direct product URL."""
        direct_patterns = [
            r'amazon\.(ca|com)/.*/(dp|gp/product)/[A-Z0-9]{10}',
            r'walmart\.ca/.*ip/.*',
            r'bestbuy\.ca/.*product/.*',
            r'canadiantire\.ca/.*product/.*',
            r'staples\.ca/.*product/.*',
            r'thebay\.com/.*product/.*',
            r'sportchek\.ca/.*product/.*',
            r'marks\.com/.*product/.*',
            r'well\.ca/.*product/.*',
            r'chapters\.indigo\.ca/.*product/.*',
            r'costco\.ca/.*product/.*',
        ]
        
        for pattern in direct_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def _clean_url(self, url):
        """
        Clean URL by removing tracking parameters and affiliate codes.
        
        Args:
            url (str): URL to clean
            
        Returns:
            str: Cleaned URL
        """
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Parameters to remove (common tracking and affiliate parameters)
            remove_params = {
                # General tracking
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
                'gclid', 'fbclid', 'msclkid', 'dclid', 'gbraid', 'wbraid',
                
                # Amazon
                'tag', 'linkCode', 'linkId', 'ref_', 'pf_rd_p', 'pf_rd_r',
                'pf_rd_s', 'pf_rd_t', 'pf_rd_i', 'pf_rd_m', 'pd_rd_r',
                'pd_rd_w', 'pd_rd_wg', 'psc', 'refRID', 'th', 'psc',
                
                # Walmart
                'athbdg', 'athznb', 'athiid', 'athstid', 'athena_met',
                'adid', 'wmlspartner', 'sourceid', 'affillinktype',
                'veh', 'wmlspartner', 'selectedSellerId',
                
                # Best Buy
                'ref', 'loc', 'acampID', 'irclickid', 'irgwc',
                'mpid', 'intl',
                
                # Canadian Tire
                'cid', 'utm_', 'gclid', 'referrer',
                
                # Generic affiliate
                'aff', 'affiliate', 'partner', 'promo', 'coupon',
                'discount', 'offer', 'ref', 'source', 'medium', 'campaign',
                
                # Social media
                'igshid', 'fbclid', 'share', 'shared',
                
                # Email marketing
                'email', 'em', 'newsletter', 'mkt_tok', 'trk',
                
                # Other tracking
                'mc_cid', 'mc_eid', '_ga', '_gid', '_gac', 'gclsrc',
            }
            
            # Remove unwanted parameters
            cleaned_params = {}
            for key, value in query_params.items():
                # Remove if key matches remove_params or starts with tracking prefixes
                if (key.lower() not in remove_params and 
                    not key.lower().startswith(('utm_', 'ga_', 'gclid', 'fbclid', 'msclkid', '_'))):
                    cleaned_params[key] = value
            
            # Rebuild URL
            if cleaned_params:
                new_query = urlencode(cleaned_params, doseq=True)
                cleaned_parsed = parsed._replace(query=new_query)
            else:
                cleaned_parsed = parsed._replace(query='')
            
            return urlunparse(cleaned_parsed)
            
        except Exception as e:
            print(f"Warning: Could not clean URL {url}: {e}")
            return url
    
    def extract_product_info(self, url):
        """
        Extract product information from URL.
        
        Args:
            url (str): Product URL
            
        Returns:
            dict: Product information
        """
        domain = urlparse(url).netloc.lower()
        
        # Amazon product info
        if 'amazon' in domain:
            asin_match = re.search(r'/(dp|gp/product)/([A-Z0-9]{10})', url)
            if asin_match:
                return {
                    'merchant': 'amazon',
                    'product_id': asin_match.group(2),
                    'url_type': 'product'
                }
        
        # Walmart product info
        elif 'walmart' in domain:
            product_match = re.search(r'/ip/[^/]+/(\d+)', url)
            if product_match:
                return {
                    'merchant': 'walmart',
                    'product_id': product_match.group(1),
                    'url_type': 'product'
                }
        
        # Best Buy product info
        elif 'bestbuy' in domain:
            product_match = re.search(r'/product/[^/]+/(\d+)', url)
            if product_match:
                return {
                    'merchant': 'bestbuy',
                    'product_id': product_match.group(1),
                    'url_type': 'product'
                }
        
        # Default info
        return {
            'merchant': domain.replace('www.', '').replace('.ca', '').replace('.com', ''),
            'product_id': None,
            'url_type': 'unknown'
        }

# Example usage and testing
if __name__ == "__main__":
    resolver = LinkResolver()
    
    # Test URLs
    test_urls = [
        'https://www.amazon.ca/dp/B08N5WRWNW?tag=oldtag-20&ref=something',
        'https://www.walmart.ca/en/ip/some-product/123456?utm_source=google&utm_medium=cpc',
        'https://smartcanucks.ca/go/amazon/B08N5WRWNW',
        'https://example.com/redirect?url=https://www.amazon.ca/dp/B08N5WRWNW',
    ]
    
    for url in test_urls:
        print(f"Original: {url}")
        resolved = resolver.resolve_url(url)
        print(f"Resolved: {resolved}")
        info = resolver.extract_product_info(resolved)
        print(f"Info: {info}")
        print("---")