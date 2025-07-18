#!/usr/bin/env python3
"""
Multi-blade scraper: RSS + Post Content + Affiliate Processing
Combines all scraping layers for maximum link extraction.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import argparse

from rss_to_json import parse_rss_feed
from post_scraper import PostScraper
from affiliate_processor import AffiliateProcessor

class MultiBladeScrap:
    """Multi-layered scraper for comprehensive link extraction."""
    
    def __init__(self, max_posts=10, post_delay=(1, 3)):
        self.post_scraper = PostScraper(delay_range=post_delay)
        self.affiliate_processor = AffiliateProcessor()
        self.max_posts = max_posts
        
    def scrape_feed_comprehensive(self, feed_url: str) -> Dict:
        """
        Comprehensive scraping: RSS -> Post Content -> Affiliate Processing
        
        Args:
            feed_url (str): RSS feed URL
            
        Returns:
            dict: Comprehensive scraped data
        """
        print(f"[*] Starting multi-blade scraping for: {feed_url}")
        
        # BLADE 1: RSS Feed Scraping
        print("\n[1] BLADE 1: RSS Feed Scraping")
        rss_result = parse_rss_feed(feed_url)
        
        if 'error' in rss_result:
            return {'error': f"RSS scraping failed: {rss_result['error']}"}
        
        rss_entries = rss_result.get('entries', [])
        print(f"   [+] Found {len(rss_entries)} RSS entries")
        
        # BLADE 2: Post Content Scraping
        print(f"\n[2] BLADE 2: Post Content Scraping (max {self.max_posts} posts)")
        
        # Extract post URLs for scraping
        post_urls = [entry['link'] for entry in rss_entries[:self.max_posts]]
        scraped_posts = self.post_scraper.scrape_posts_batch(post_urls)
        
        # Count total merchant links found
        total_merchant_links = sum(len(post.get('merchant_links', [])) for post in scraped_posts)
        print(f"   [+] Scraped {len(scraped_posts)} posts")
        print(f"   [+] Found {total_merchant_links} merchant links")
        
        # BLADE 3: Affiliate Processing
        print(f"\n[3] BLADE 3: Affiliate Processing")
        
        # Collect all merchant links for affiliate processing
        all_merchant_links = []
        for post in scraped_posts:
            for link in post.get('merchant_links', []):
                all_merchant_links.append({
                    'title': f"{post.get('title', 'No title')} - {link['text']}",
                    'link': link['url'],
                    'merchant': link['merchant'],
                    'link_type': link['link_type'],
                    'source_post': post['url'],
                    'published': '',  # Will be filled from RSS if available
                })
        
        # Process merchant links through affiliate system
        processed_links = []
        for link_data in all_merchant_links:
            processed_entry = self.affiliate_processor.process_rss_entry(link_data.copy())
            processed_links.append(processed_entry)
        
        # Get affiliate processing stats
        affiliate_stats = self.affiliate_processor.get_stats()
        print(f"   [+] Processed {affiliate_stats['processed']} links with affiliate tags")
        print(f"   [+] Skipped {affiliate_stats['skipped']} links")
        print(f"   [+] Success rate: {affiliate_stats['success_rate']:.1f}%")
        
        # BLADE 4: Combine and Structure Results
        print(f"\n[4] BLADE 4: Combining Results")
        
        # Combine RSS entries with their scraped content
        enhanced_entries = []
        for i, rss_entry in enumerate(rss_entries):
            enhanced_entry = rss_entry.copy()
            
            # Add scraped content if available
            if i < len(scraped_posts):
                post_data = scraped_posts[i]
                enhanced_entry['scraped_content'] = {
                    'title': post_data.get('title', ''),
                    'content_preview': post_data.get('content', '')[:200] + '...' if post_data.get('content') else '',
                    'content_summary': post_data.get('content_summary', ''),
                    'og_image': post_data.get('og_image'),
                    'merchant_links_count': len(post_data.get('merchant_links', [])),
                    'deal_info': post_data.get('deal_info', {}),
                    'scraped_at': post_data.get('scraped_at'),
                }
            
            enhanced_entries.append(enhanced_entry)
        
        # Create comprehensive result
        result = {
            'feed_url': feed_url,
            'scraped_at': datetime.now().isoformat() + 'Z',
            'scraping_stats': {
                'rss_entries': len(rss_entries),
                'posts_scraped': len(scraped_posts),
                'merchant_links_found': total_merchant_links,
                'affiliate_links_processed': affiliate_stats['processed'],
                'affiliate_success_rate': affiliate_stats['success_rate'],
            },
            'blog_posts': enhanced_entries,  # SmartCanucks blog posts
            'product_links': processed_links,  # Extracted clean/affiliate product links
            'processing_summary': {
                'total_blog_posts': len(enhanced_entries),
                'total_product_links': len(processed_links),
                'affiliate_processed': affiliate_stats['processed'],
                'unique_merchants': len(set(link.get('merchant', 'unknown') for link in processed_links)),
            }
        }
        
        print(f"   [+] Combined {len(enhanced_entries)} RSS entries with scraped content")
        print(f"   [+] Generated {len(processed_links)} affiliate-ready merchant links")
        
        return result
    
    def save_results(self, results: Dict, output_path: str):
        """Save comprehensive results to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Results saved to: {output_file}")
        
        # Print summary
        stats = results.get('scraping_stats', {})
        print(f"\n[*] FINAL SUMMARY:")
        print(f"   - RSS Entries: {stats.get('rss_entries', 0)}")
        print(f"   - Posts Scraped: {stats.get('posts_scraped', 0)}")
        print(f"   - Merchant Links: {stats.get('merchant_links_found', 0)}")
        print(f"   - Affiliate Processed: {stats.get('affiliate_links_processed', 0)}")
        print(f"   - Success Rate: {stats.get('affiliate_success_rate', 0):.1f}%")

def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(description='Multi-blade RSS + Post + Affiliate scraper')
    parser.add_argument('--url', default='https://smartcanucks.ca/feed/', 
                        help='RSS feed URL to scrape')
    parser.add_argument('--output', default='build/comprehensive_feed.json',
                        help='Output JSON file path')
    parser.add_argument('--max-posts', type=int, default=10,
                        help='Maximum number of posts to scrape')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Delay between post requests (seconds)')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = MultiBladeScrap(
        max_posts=args.max_posts,
        post_delay=(args.delay, args.delay + 1)
    )
    
    # Run comprehensive scraping
    results = scraper.scrape_feed_comprehensive(args.url)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Save results
    scraper.save_results(results, args.output)
    
    print(f"\n[*] Multi-blade scraping complete!")

if __name__ == "__main__":
    main()