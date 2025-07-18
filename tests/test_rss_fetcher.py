#!/usr/bin/env python3
"""
Unit tests for RSS fetcher script.
Run with: python -m pytest tests/test_rss_fetcher.py -v
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import tempfile
from pathlib import Path

# Add the scripts directory to the path so we can import the RSS fetcher
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from rss_to_json import parse_rss_feed, main
except ImportError as e:
    print(f"Error importing RSS fetcher: {e}")
    sys.exit(1)


class TestRSSFetcher(unittest.TestCase):
    """Test cases for RSS fetcher functionality."""
    
    def test_valid_feed_parsing(self):
        """Test parsing a valid RSS feed."""
        with patch('feedparser.parse') as mock_parse:
            # Mock a valid feed
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [
                {
                    'title': 'Test Post 1',
                    'link': 'https://example.com/post1',
                    'published': '2024-01-17T10:00:00Z'
                },
                {
                    'title': 'Test Post 2',
                    'link': 'https://example.com/post2',
                    'published': '2024-01-17T09:00:00Z'
                }
            ]
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/feed.xml')
            
            # Check that we got entries
            self.assertIn('entries', result)
            self.assertEqual(len(result['entries']), 2)
            
            # Check entry structure
            entry = result['entries'][0]
            self.assertEqual(entry['title'], 'Test Post 1')
            self.assertEqual(entry['link'], 'https://example.com/post1')
            self.assertEqual(entry['published'], '2024-01-17T10:00:00Z')
    
    def test_empty_feed_handling(self):
        """Test handling of empty RSS feed."""
        with patch('feedparser.parse') as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = []
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/empty-feed.xml')
            
            # Should return an error for empty feed
            self.assertIn('error', result)
            self.assertIn('No entries found', result['error'])
    
    def test_malformed_feed_handling(self):
        """Test handling of malformed RSS feed."""
        with patch('feedparser.parse') as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = True
            mock_feed.bozo_exception = Exception("XML parsing error")
            mock_feed.entries = []
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/malformed-feed.xml')
            
            # Should return an error for malformed feed with no entries
            self.assertIn('error', result)
    
    def test_http_error_handling(self):
        """Test handling of HTTP errors."""
        with patch('feedparser.parse') as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.status = 404
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/nonexistent-feed.xml')
            
            # Should return HTTP error
            self.assertIn('error', result)
            self.assertIn('404', result['error'])
    
    def test_missing_required_fields(self):
        """Test handling of entries with missing required fields."""
        with patch('feedparser.parse') as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [
                {
                    'title': 'Valid Post',
                    'link': 'https://example.com/valid',
                    'published': '2024-01-17T10:00:00Z'
                },
                {
                    'title': 'Missing Link Post',
                    # Missing 'link' field
                    'published': '2024-01-17T09:00:00Z'
                },
                {
                    'link': 'https://example.com/missing-title',
                    # Missing 'title' field  
                    'published': '2024-01-17T08:00:00Z'
                }
            ]
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/partial-feed.xml')
            
            # Should only return valid entries
            self.assertIn('entries', result)
            self.assertEqual(len(result['entries']), 1)
            self.assertEqual(result['entries'][0]['title'], 'Valid Post')
    
    def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch('feedparser.parse') as mock_parse:
            mock_parse.side_effect = Exception("Network error")
            
            result = parse_rss_feed('https://example.com/network-error.xml')
            
            # Should return network error
            self.assertIn('error', result)
            self.assertIn('Network error', result['error'])
    
    def test_malformed_feed_with_valid_entries(self):
        """Test malformed feed that still has valid entries."""
        with patch('feedparser.parse') as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = True
            mock_feed.bozo_exception = Exception("XML parsing error")
            mock_feed.entries = [
                {
                    'title': 'Valid Post Despite Malformed XML',
                    'link': 'https://example.com/valid-post',
                    'published': '2024-01-17T10:00:00Z'
                }
            ]
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/malformed-with-entries.xml')
            
            # Should return entries despite malformed XML
            self.assertIn('entries', result)
            self.assertEqual(len(result['entries']), 1)
    
    def test_date_parsing_edge_cases(self):
        """Test date parsing edge cases."""
        with patch('feedparser.parse') as mock_parse:
            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [
                {
                    'title': 'Post with published_parsed',
                    'link': 'https://example.com/post1',
                    'published': '2024-01-17T10:00:00Z',
                    'published_parsed': None  # This should fallback to published
                },
                {
                    'title': 'Post without published',
                    'link': 'https://example.com/post2',
                    # No published field
                }
            ]
            mock_parse.return_value = mock_feed
            
            result = parse_rss_feed('https://example.com/date-edge-cases.xml')
            
            # Should handle both cases gracefully
            self.assertIn('entries', result)
            self.assertEqual(len(result['entries']), 2)
            
            # First entry should have published date
            self.assertEqual(result['entries'][0]['published'], '2024-01-17T10:00:00Z')
            
            # Second entry should have empty published date
            self.assertEqual(result['entries'][1]['published'], '')


class TestMainFunction(unittest.TestCase):
    """Test cases for the main CLI function."""
    
    def test_main_with_valid_args(self):
        """Test main function with valid arguments."""
        with patch('sys.argv', ['rss_to_json.py', '--url', 'https://example.com/feed.xml']):
            with patch('rss_to_json.parse_rss_feed') as mock_parse:
                mock_parse.return_value = {
                    'entries': [
                        {
                            'title': 'Test Post',
                            'link': 'https://example.com/post',
                            'published': '2024-01-17T10:00:00Z'
                        }
                    ]
                }
                
                with patch('builtins.open', mock_open()) as mock_file:
                    with patch('pathlib.Path.mkdir'):
                        with patch('sys.exit') as mock_exit:
                            main()
                            
                            # Should not exit with error
                            mock_exit.assert_not_called()
                            
                            # Should write to file
                            mock_file.assert_called_once()
    
    def test_main_with_invalid_url(self):
        """Test main function with invalid URL."""
        with patch('sys.argv', ['rss_to_json.py', '--url', 'invalid-url']):
            with patch('sys.exit') as mock_exit:
                main()
                
                # Should exit with error code 1
                mock_exit.assert_called_once_with(1)
    
    def test_main_with_parse_error(self):
        """Test main function when parsing fails."""
        with patch('sys.argv', ['rss_to_json.py', '--url', 'https://example.com/feed.xml']):
            with patch('rss_to_json.parse_rss_feed') as mock_parse:
                mock_parse.return_value = {'error': 'Parse failed'}
                
                with patch('sys.exit') as mock_exit:
                    main()
                    
                    # Should exit with error code 1
                    mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)