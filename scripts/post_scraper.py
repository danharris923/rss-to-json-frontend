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
            # Gaming platforms
            'epicgames.com',
            'store.epicgames.com',
            'steam.com',
            'store.steampowered.com',
            'gog.com',
            'playstation.com',
            'xbox.com',
            'nintendo.com',
            'ubisoft.com',
            'ea.com',
            'origin.com',
            'battle.net',
            'blizzard.com',
            # Restaurant/food chains
            'swisschalet.com',
            'harveys.ca',
            'kfc.ca',
            'mcdonalds.ca',
            'timhortons.ca',
            'starbucks.ca',
            'subway.ca',
            'pizzahut.ca',
            'dominos.ca',
            'ubereats.com',
            'doordash.com',
            'skipthedishes.com',
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
            full_content = self._extract_content(soup)
            post_data = {
                'url': post_url,
                'title': self._extract_title(soup),
                'content': full_content,
                'content_summary': self._summarize_content(full_content),
                'og_image': self._extract_og_image(soup),
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
                # Remove ad blocks and other clutter from content
                for ad in element.select('.adthrive-ad, .ad, .advertisement, .ad-banner, .promo-box'):
                    ad.decompose()
                
                # Remove social media buttons, share buttons, etc.
                for clutter in element.select('.social-share, .share-buttons, .related-posts, .tags, .categories'):
                    clutter.decompose()
                
                content = element.get_text(strip=True)
                if len(content) > 50:  # Only return if we found substantial content
                    return content  # Return full content now
        
        # Fallback: try to find the main content area
        main_content = soup.find('main') or soup.find('div', {'id': 'main'})
        if main_content:
            content = main_content.get_text(strip=True)
            if len(content) > 50:
                return content
        
        return "No content found"
    
    def _summarize_content(self, content: str) -> str:
        """
        Summarize content by extracting key deal information and removing fluff.
        
        Args:
            content (str): Full post content
            
        Returns:
            str: Summarized content focusing on deal details
        """
        if not content or content == "No content found":
            return "No content to summarize"
        
        # Remove common fluff words and phrases
        fluff_patterns = [
            r'\b(the|and|or|but|if|then|also|very|really|quite|just|only|even|still|now|today|here|there|this|that|these|those|some|any|all|each|every|no|not|can|could|will|would|should|may|might|must|shall|do|does|did|have|has|had|be|is|are|was|were|been|being|get|got|getting|make|made|making|take|took|taking|give|gave|giving|go|goes|went|going|come|came|coming|see|saw|seeing|know|knew|known|knowing|think|thought|thinking|say|said|saying|tell|told|telling|use|used|using|find|found|finding|work|worked|working|call|called|calling|try|tried|trying|ask|asked|asking|need|needed|needing|want|wanted|wanting|turn|turned|turning|put|putting|seem|seemed|seeming|look|looked|looking|feel|felt|feeling|leave|left|leaving|move|moved|moving|live|lived|living|believe|believed|believing|hold|held|holding|bring|brought|bringing|happen|happened|happening|write|wrote|written|writing|provide|provided|providing|sit|sat|sitting|stand|stood|standing|lose|lost|losing|pay|paid|paying|meet|met|meeting|include|included|including|continue|continued|continuing|set|setting|learn|learned|learning|change|changed|changing|lead|led|leading|understand|understood|understanding|watch|watched|watching|follow|followed|following|stop|stopped|stopping|create|created|creating|speak|spoke|spoken|speaking|read|reading|allow|allowed|allowing|add|added|adding|spend|spent|spending|grow|grew|grown|growing|open|opened|opening|walk|walked|walking|win|won|winning|offer|offered|offering|remember|remembered|remembering|love|loved|loving|consider|considered|considering|appear|appeared|appearing|buy|bought|buying|wait|waited|waiting|serve|served|serving|die|died|dying|send|sent|sending|expect|expected|expecting|build|built|building|stay|stayed|staying|fall|fell|fallen|falling|cut|cutting|reach|reached|reaching|kill|killed|killing|remain|remained|remaining|suggest|suggested|suggesting|raise|raised|raising|pass|passed|passing|sell|sold|selling|require|required|requiring|report|reported|reporting|decide|decided|deciding|pull|pulled|pulling)\b',
            r'\b(um|uh|hmm|well|like|you know|i mean|basically|literally|actually|honestly|obviously|clearly|definitely|certainly|probably|maybe|perhaps|anyway|however|therefore|furthermore|moreover|nevertheless|meanwhile|otherwise|instead|besides|although|though|unless|until|while|since|because|if|when|where|what|why|how|who|which|whom|whose)\b',
            r'\b(amazing|awesome|incredible|fantastic|great|good|nice|cool|sweet|wow|omg|lol|haha|yes|no|ok|okay|sure|right|exactly|absolutely|totally|completely|perfectly|simply|easily|quickly|slowly|carefully|gently|softly|loudly|clearly|obviously|definitely|certainly|probably|maybe|perhaps|possibly|likely|unlikely|hopefully|unfortunately|luckily|surprisingly|interestingly|importantly|basically|essentially|generally|specifically|particularly|especially|mainly|mostly|usually|normally|typically|often|sometimes|rarely|never|always|already|still|yet|again|once|twice|three times|first|second|third|last|next|previous|final|initial|original|new|old|young|small|large|big|little|long|short|high|low|fast|slow|hot|cold|warm|cool|wet|dry|clean|dirty|easy|hard|difficult|simple|complex|light|dark|bright|heavy|empty|full|open|closed|free|busy|quiet|loud|safe|dangerous|happy|sad|angry|excited|tired|hungry|thirsty|sick|healthy|rich|poor|strong|weak|smart|stupid|funny|serious|beautiful|ugly|interesting|boring|important|useful|useless|necessary|unnecessary|possible|impossible|correct|wrong|true|false|real|fake|public|private|local|global|national|international|popular|common|rare|special|normal|strange|different|same|similar|equal|better|worse|best|worst|more|less|most|least|enough|too much|too little|too many|too few)\b',
        ]
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Find sentences that contain deal-related keywords
        deal_keywords = [
            'deal', 'discount', 'sale', 'offer', 'promo', 'coupon', 'code', 'save', 'free', 'off',
            'price', 'cost', 'buy', 'get', 'click', 'link', 'here', 'view', 'shop', 'store',
            'amazon', 'walmart', 'bestbuy', 'canadian tire', 'epic games', 'steam', 'playstation',
            'xbox', 'nintendo', 'apple', 'microsoft', 'google', 'samsung', 'sony', 'lg',
            'percent', '%', '$', 'dollar', 'cad', 'usd', 'shipping', 'delivery', 'order',
            'limited time', 'expires', 'until', 'while supplies last', 'today only'
        ]
        
        important_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            # Check if sentence contains deal keywords
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in deal_keywords):
                # Clean the sentence of fluff
                cleaned_sentence = sentence
                for pattern in fluff_patterns:
                    cleaned_sentence = re.sub(pattern, '', cleaned_sentence, flags=re.IGNORECASE)
                
                # Remove extra spaces
                cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence).strip()
                
                if len(cleaned_sentence) > 20:  # Only keep substantial sentences
                    important_sentences.append(cleaned_sentence)
        
        # If no important sentences found, take first few sentences
        if not important_sentences:
            important_sentences = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        # Combine important sentences
        summary = '. '.join(important_sentences[:5])  # Max 5 sentences
        
        # Final cleanup
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # Limit length
        if len(summary) > 500:
            summary = summary[:500] + '...'
        
        return summary if summary else "Unable to summarize content"
    
    def _extract_og_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract OpenGraph image URL from the post."""
        # Try OpenGraph meta tag first
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Try Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # Try generic meta image
        meta_image = soup.find('meta', attrs={'name': 'image'})
        if meta_image and meta_image.get('content'):
            return meta_image['content']
        
        # Try to find featured image in content
        content_areas = soup.select('.entry-content, .post-content, .blog-content')
        for area in content_areas:
            img = area.find('img')
            if img and img.get('src'):
                return img['src']
        
        # Fallback to any img tag
        img = soup.find('img')
        if img and img.get('src'):
            return img['src']
        
        return None
    
    def _extract_merchant_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all merchant links from the post."""
        merchant_links = []
        
        # Focus ONLY on the main blog post content, not navigation or sidebars
        content_areas = []
        
        # Try SmartCanucks-specific content selectors first
        smartcanucks_selectors = [
            '.blog-content',
            '.col-md-6.col-sm-7',
            '.entry-content',
            '.post-content',
            '.content',
            'article .content',
            'main article',
            '.single-post-content',
            '.post-body'
        ]
        
        for selector in smartcanucks_selectors:
            elements = soup.select(selector)
            if elements:
                content_areas.extend(elements)
                break  # Use the first successful match to avoid duplicates
        
        # If no content areas found, fallback but be more selective
        if not content_areas:
            # Try to find the main content by looking for text content
            for element in soup.find_all(['article', 'main', 'div']):
                if element.get_text(strip=True) and len(element.get_text(strip=True)) > 100:
                    content_areas = [element]
                    break
        
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
                
                # Skip internal SmartCanucks links, navigation, and social media
                skip_patterns = [
                    'smartcanucks.ca', 'facebook.com', 'twitter.com', 'instagram.com', 
                    'pinterest.com', 'youtube.com', 'tiktok.com', 'linkedin.com',
                    '#', 'mailto:', 'tel:', 'javascript:', 'void(0)',
                    '/deals/', '/coupons/', '/flyers/', '/forum/', '/stores/',
                    'amazon.smartcanucks.ca', 'deals.smartcanucks.ca', 
                    'coupons.smartcanucks.ca', 'flyers.smartcanucks.ca',
                    'forum.smartcanucks.ca', 'hotcanadadeals.ca'
                ]
                if any(skip in href.lower() for skip in skip_patterns):
                    continue
                
                # Get link text early for filtering
                link_text = link.get_text(strip=True)
                
                # Also skip if the link text suggests it's navigation
                navigation_text = [
                    'home', 'blog', 'deals', 'coupons', 'flyers', 'forum', 'stores',
                    'contact', 'about', 'privacy', 'terms', 'subscribe', 'newsletter',
                    'follow us', 'share', 'comment', 'reply', 'more posts'
                ]
                if any(nav in link_text.lower() for nav in navigation_text):
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Check if this is a deal link using intelligent detection
                if self._is_deal_link(full_url, link):
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
    
    def _is_deal_link(self, url: str, link_element) -> bool:
        """Intelligent detection of deal links based on context and content."""
        try:
            # Get link text and surrounding context
            link_text = link_element.get_text(strip=True).lower()
            
            # Check if link has deal-related text patterns
            deal_text_patterns = [
                'click here', 'view offer', 'get deal', 'shop now', 'buy now',
                'order now', 'purchase', 'download', 'get it', 'grab it',
                'check it out', 'see deal', 'view deal', 'get this',
                'epic games', 'steam', 'amazon', 'walmart', 'best buy',
                'get free', 'download free', 'claim', 'redeem',
                'visit', 'go to', 'check out', 'see more', 'learn more',
                'promo code', 'coupon', 'discount', 'save', 'sale'
            ]
            
            # Check link text
            if any(pattern in link_text for pattern in deal_text_patterns):
                return True
            
            # Check if link is in a deal context (look at parent elements)
            parent = link_element.parent
            if parent:
                parent_text = parent.get_text(strip=True).lower()
                
                # Look for deal context in parent text
                deal_context_patterns = [
                    'deal', 'offer', 'promo', 'sale', 'discount', 'free',
                    'save', 'coupon', 'code', 'epic games', 'steam',
                    'amazon', 'walmart', 'click here', 'view'
                ]
                
                if any(pattern in parent_text for pattern in deal_context_patterns):
                    return True
            
            # Check URL for deal patterns
            url_lower = url.lower()
            deal_url_patterns = [
                'deal', 'offer', 'promo', 'sale', 'discount', 'coupon',
                'free', 'epicgames.com', 'steam', 'amazon', 'walmart',
                'product', 'item', 'buy', 'shop', 'store'
            ]
            
            if any(pattern in url_lower for pattern in deal_url_patterns):
                return True
            
            # Check if URL is from known merchant domains
            domain = urlparse(url).netloc.lower().replace('www.', '')
            if any(merchant in domain for merchant in self.merchant_domains):
                return True
            
            # Check if link has special attributes that indicate it's a deal link
            link_attrs = link_element.attrs
            if 'data-deal' in link_attrs or 'data-offer' in link_attrs:
                return True
                
            # Prioritize external links that might be deals
            if domain != 'smartcanucks.ca' and domain != 'hotcanadadeals.ca' and len(link_text) > 5:
                # If it's an external link with substantial text, it's likely a deal
                return True
            
            return False
            
        except Exception as e:
            # If there's any error, be conservative and return False
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