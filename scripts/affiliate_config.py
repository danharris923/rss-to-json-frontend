#!/usr/bin/env python3
"""
Affiliate link configuration and URL rewriting system.
Configure your affiliate tags and link patterns here.
"""

# Your affiliate tags - Use environment variables for production
# These can be set in Vercel environment variables
import os

AFFILIATE_TAGS = {
    # Amazon affiliate tag
    'amazon.ca': os.environ.get('AMAZON_CA_TAG', 'yourtag-20'),
    'amazon.com': os.environ.get('AMAZON_COM_TAG', 'yourtag-20'),
    
    # Other affiliate networks
    'walmart.ca': os.environ.get('WALMART_CA_TAG', 'your-walmart-id'),
    'bestbuy.ca': os.environ.get('BESTBUY_CA_TAG', 'your-bestbuy-id'),
    'canadiantire.ca': os.environ.get('CANADIANTIRE_CA_TAG', 'your-ct-id'),
    'staples.ca': os.environ.get('STAPLES_CA_TAG', 'your-staples-id'),
    'thebay.com': os.environ.get('THEBAY_COM_TAG', 'your-bay-id'),
    'sportchek.ca': os.environ.get('SPORTCHEK_CA_TAG', 'your-sportchek-id'),
    'marks.com': os.environ.get('MARKS_COM_TAG', 'your-marks-id'),
    'well.ca': os.environ.get('WELL_CA_TAG', 'your-well-id'),
    'chapters.indigo.ca': os.environ.get('INDIGO_CA_TAG', 'your-indigo-id'),
    'costco.ca': os.environ.get('COSTCO_CA_TAG', 'your-costco-id'),
    
    # Fashion/retail
    'gap.ca': os.environ.get('GAP_CA_TAG', 'your-gap-id'),
    'oldnavy.ca': os.environ.get('OLDNAVY_CA_TAG', 'your-oldnavy-id'),
    'bananarepublic.ca': os.environ.get('BANANAREPUBLIC_CA_TAG', 'your-br-id'),
    'lululemon.com': os.environ.get('LULULEMON_COM_TAG', 'your-lulu-id'),
    'nike.com': os.environ.get('NIKE_COM_TAG', 'your-nike-id'),
    'adidas.ca': os.environ.get('ADIDAS_CA_TAG', 'your-adidas-id'),
    
    # Electronics/tech
    'newegg.ca': os.environ.get('NEWEGG_CA_TAG', 'your-newegg-id'),
    'memoryexpress.com': os.environ.get('MEMORYEXPRESS_COM_TAG', 'your-memex-id'),
    'microsoft.com': os.environ.get('MICROSOFT_COM_TAG', 'your-microsoft-id'),
    'apple.com': os.environ.get('APPLE_COM_TAG', 'your-apple-id'),
}

# URL patterns that should be rewritten through your affiliate system
AFFILIATE_URL_PATTERNS = {
    # Amazon - add your associate tag to product URLs
    'amazon.ca': {
        'pattern': r'(https?://(?:www\.)?amazon\.ca/[^?\s]+)',
        'rewrite': r'\1?tag={affiliate_tag}',
    },
    'amazon.com': {
        'pattern': r'(https?://(?:www\.)?amazon\.com/[^?\s]+)',
        'rewrite': r'\1?tag={affiliate_tag}',
    },
    
    # Other affiliate networks - customize based on their URL structure
    'walmart.ca': {
        'pattern': r'(https?://(?:www\.)?walmart\.ca/[^?\s]+)',
        'rewrite': r'\1?affiliate={affiliate_tag}',
    },
    
    # Add more patterns as needed for other merchants
}

# Default affiliate redirect system
DEFAULT_AFFILIATE_SYSTEM = {
    'enabled': True,
    'redirect_domain': 'your-domain.com',  # Your domain for link tracking
    'redirect_path': '/go/',  # Path for redirect links
    'track_clicks': True,
    'add_utm_params': True,
}

# UTM parameters for tracking
UTM_PARAMS = {
    'utm_source': 'rss_feed',
    'utm_medium': 'affiliate',
    'utm_campaign': 'smartcanucks_deals',
    'utm_content': 'rss_item',
}

def get_affiliate_tag(domain):
    """Get affiliate tag for a specific domain."""
    for affiliate_domain, tag in AFFILIATE_TAGS.items():
        if affiliate_domain in domain.lower():
            return tag
    return None

def should_affiliate_link(url):
    """Check if a URL should be converted to an affiliate link."""
    domain = url.lower()
    return any(affiliate_domain in domain for affiliate_domain in AFFILIATE_TAGS.keys())

def get_utm_string():
    """Generate UTM parameter string."""
    return '&'.join([f'{key}={value}' for key, value in UTM_PARAMS.items()])