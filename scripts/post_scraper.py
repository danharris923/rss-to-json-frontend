#!/usr/bin/env python3
"""
WordPress post content scraper for extracting merchant links.
Scrapes individual SmartCanucks posts to find actual product links.
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
import random
from typing import List, Dict, Optional
import logging

class PostScraper:
    """Scrape WordPress posts to extract merchant product links."""
    
    def __init__(self, delay_range=(1, 3), timeout=10):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.delay_range = delay_range
        self.timeout = timeout
        
        # Merchant domains to look for (including shortlinks)
        self.merchant_domains = {
            'amazon.ca', 'amazon.com', 'amzn.to',  # Amazon shortlinks
            'walmart.ca', 'walmart.com',
            'bestbuy.ca', 'bestbuy.com',
            'canadiantire.ca',
            'staples.ca',
            'thebay.com',
            'sportchek.ca',
            'marks.com',
            'well.ca',
            'chapters.indigo.ca',
            'costco.ca',
            'gap.ca',
            'oldnavy.ca',
            'bananarepublic.ca',
            'lululemon.com',
            'nike.com',
            'adidas.ca',
            'newegg.ca',
            'memoryexpress.com',
            'microsoft.com',
            'apple.com',
            'homedepot.ca',
            'lowes.ca',
            'canadianfreestuff.com',
            'rakuten.ca',
            'groupon.ca',
        }
    
    def scrape_post(self, post_url: str) -> Dict:
        """
        Scrape a single WordPress post for merchant links.
        
        Args:
            post_url (str): URL of the WordPress post
            
        Returns:
            dict: Scraped data including merchant links
        """
        try:
            # Random delay to be respectful
            if self.delay_range:
                time.sleep(random.uniform(*self.delay_range))
            
            print(f"Scraping post: {post_url}")
            
            # Fetch the post content
            response = self.session.get(post_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract post metadata
            post_data = {
                'url': post_url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'merchant_links': self._extract_merchant_links(soup, post_url),
                'deal_info': self._extract_deal_info(soup),
                'scraped_at': time.time(),
            }
            
            print(f"Found {len(post_data['merchant_links'])} merchant links")
            return post_data
            
        except Exception as e:
            print(f"Error scraping post {post_url}: {e}")
            return {
                'url': post_url,
                'error': str(e),
                'scraped_at': time.time(),
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract post title."""
        # Try multiple selectors for WordPress titles
        title_selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1.title',
            '.entry-header h1',
            '.post-header h1',
            'title',
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "No title found"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main post content."""
        # Try SmartCanucks-specific selectors first
        smartcanucks_selectors = [
            '.blog-content',
            '.col-md-6.col-sm-7',
        ]
        
        # Then try standard WordPress selectors
        wordpress_selectors = [
            '.entry-content',
            '.post-content',
            '.content',
            'article .content',
            '.post-body',
            'main article',
            '.post',
            'article',
            '#content',
            '.single-post-content',
        ]
        
        all_selectors = smartcanucks_selectors + wordpress_selectors
        
        for selector in all_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove ad blocks from content
                for ad in element.select('.adthrive-ad'):
                    ad.decompose()
                
                content = element.get_text(strip=True)
                if len(content) > 50:  # Only return if we found substantial content
                    return content[:1000]  # Limit content length
        
        # Fallback: try to find the main content area
        main_content = soup.find('main') or soup.find('div', {'id': 'main'})
        if main_content:
            content = main_content.get_text(strip=True)
            if len(content) > 50:
                return content[:1000]
        
        return "No content found"
    
    def _extract_merchant_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all merchant links from the post."""
        merchant_links = []
        
        # Focus on SmartCanucks content areas first
        smartcanucks_areas = soup.select('.blog-content, .col-md-6.col-sm-7')
        
        # Then try standard WordPress content areas
        wordpress_areas = soup.select('.entry-content, .post-content, .content, article, main, .post')
        
        content_areas = smartcanucks_areas + wordpress_areas
        if not content_areas:
            content_areas = [soup]  # Fallback to entire page
        
        for content_area in content_areas:
            # Remove ad blocks first
            for ad in content_area.select('.adthrive-ad'):
                ad.decompose()
            
            # Find all links in the content area
            all_links = content_area.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '').strip()
                if not href:
                    continue
                
                # Skip internal SmartCanucks links, footer links, etc.
                skip_patterns = [
                    'smartcanucks.ca', 'facebook.com', 'twitter.com', 'instagram.com', 
                    'pinterest.com', 'youtube.com', '#', 'mailto:', 'tel:', 'javascript:'
                ]
                if any(skip in href.lower() for skip in skip_patterns):
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Check if this is a merchant link (including amzn.to shortlinks)
                if self._is_merchant_link(full_url):
                    link_text = link.get_text(strip=True)
                    
                    # Skip if link text is too generic or empty
                    if not link_text or len(link_text) < 2:
                        continue
                    
                    link_data = {
                        'url': full_url,
                        'text': link_text,
                        'merchant': self._identify_merchant(full_url),
                        'link_type': self._classify_link_type(full_url),
                    }
                    
                    # Avoid duplicates
                    if not any(existing['url'] == full_url for existing in merchant_links):
                        merchant_links.append(link_data)
        
        return merchant_links
    
    def _is_merchant_link(self, url: str) -> bool:
        """Check if URL is a merchant link we want to process."""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            domain = domain.replace('www.', '')
            
            # Check if domain matches any merchant domain
            return any(merchant in domain for merchant in self.merchant_domains)
        except:
            return False
    
    def _identify_merchant(self, url: str) -> str:
        """Identify which merchant this link belongs to."""
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            
            # Special handling for Amazon shortlinks
            if 'amzn.to' in domain:
                return 'amazon'
            
            # Direct domain matches
            for merchant_domain in self.merchant_domains:
                if merchant_domain in domain:
                    return merchant_domain.replace('.ca', '').replace('.com', '')
            
            return 'unknown'
        except:
            return 'unknown'
    
    def _classify_link_type(self, url: str) -> str:
        """Classify the type of merchant link."""
        url_lower = url.lower()
        
        # Amazon shortlinks
        if 'amzn.to' in url_lower:
            return 'amazon_product'
        
        # Amazon product patterns
        elif 'amazon' in url_lower:
            if '/dp/' in url_lower or '/gp/product/' in url_lower:
                return 'amazon_product'
            elif '/deal/' in url_lower or '/gp/deal/' in url_lower:
                return 'amazon_deal'
            else:
                return 'amazon_other'
        
        # Walmart patterns
        elif 'walmart' in url_lower:
            if '/ip/' in url_lower:
                return 'walmart_product'
            else:
                return 'walmart_other'
        
        # Best Buy patterns
        elif 'bestbuy' in url_lower:
            if '/product/' in url_lower:
                return 'bestbuy_product'
            else:
                return 'bestbuy_other'
        
        # Generic patterns
        elif any(keyword in url_lower for keyword in ['product', 'item', 'deal']):
            return 'product_page'
        
        return 'merchant_page'
    
    def _extract_deal_info(self, soup: BeautifulSoup) -> Dict:
        """Extract deal-specific information from the post."""
        deal_info = {
            'discount_percentage': None,
            'original_price': None,
            'sale_price': None,
            'coupon_code': None,
            'expiry_date': None,
        }
        
        # Extract text for analysis
        text = soup.get_text().lower()
        
        # Look for discount percentages
        discount_matches = re.findall(r'(\d+)%\s*off', text)
        if discount_matches:
            deal_info['discount_percentage'] = max(map(int, discount_matches))
        
        # Look for prices
        price_matches = re.findall(r'\$(\d+(?:\.\d{2})?)', text)
        if price_matches:
            prices = [float(p) for p in price_matches]
            if len(prices) >= 2:
                deal_info['original_price'] = max(prices)
                deal_info['sale_price'] = min(prices)
        
        # Look for coupon codes
        coupon_matches = re.findall(r'code[:\s]+([A-Z0-9]+)', text)
        if coupon_matches:
            deal_info['coupon_code'] = coupon_matches[0]
        
        # Look for expiry dates
        expiry_matches = re.findall(r'until\s+(\w+\s+\d+)', text)
        if expiry_matches:
            deal_info['expiry_date'] = expiry_matches[0]
        
        return deal_info
    
    def scrape_posts_batch(self, post_urls: List[str], max_posts: Optional[int] = None) -> List[Dict]:
        """
        Scrape multiple posts in batch.
        
        Args:
            post_urls (List[str]): List of post URLs to scrape
            max_posts (Optional[int]): Maximum number of posts to scrape
            
        Returns:
            List[Dict]: List of scraped post data
        """
        if max_posts:
            post_urls = post_urls[:max_posts]
        
        scraped_posts = []
        
        for i, post_url in enumerate(post_urls, 1):
            print(f"Scraping post {i}/{len(post_urls)}")
            
            post_data = self.scrape_post(post_url)
            scraped_posts.append(post_data)
            
            # Progress update
            if i % 5 == 0:
                total_links = sum(len(post.get('merchant_links', [])) for post in scraped_posts)
                print(f"Progress: {i}/{len(post_urls)} posts, {total_links} merchant links found")
        
        return scraped_posts

# Example usage and testing
if __name__ == "__main__":
    # Test with a SmartCanucks Amazon deals post
    scraper = PostScraper()
    
    # Amazon deals post URL
    test_url = "https://smartcanucks.ca/amazon-canada-deals-save-57-on-cordless-table-lamps-rechargeable-49-on-womens-yoga-pants-more/"
    
    result = scraper.scrape_post(test_url)
    
    print(f"\nPost Title: {result.get('title', 'N/A')}")
    print(f"Content Preview: {result.get('content', 'N/A')[:200]}...")
    print(f"Merchant Links Found: {len(result.get('merchant_links', []))}")
    
    for link in result.get('merchant_links', []):
        print(f"  - {link['merchant']}: {link['text'][:50]}...")
        print(f"    URL: {link['url']}")
        print(f"    Type: {link['link_type']}")
        print("    ---")