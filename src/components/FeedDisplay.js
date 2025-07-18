import React, { useState, useEffect } from 'react';
import FeedItem from './FeedItem';
import LoadingSpinner from './LoadingSpinner';

const FeedDisplay = () => {
  const [feedData, setFeedData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    let ignore = false;
    
    const fetchFeed = async () => {
      try {
        const response = await fetch('/feed.json');
        if (!response.ok) {
          throw new Error(`Failed to fetch feed: ${response.status}`);
        }
        const data = await response.json();
        
        if (!ignore) {
          // Always show SmartCanucks blog posts 
          let entries = [];
          
          if (data.blog_posts && data.blog_posts.length > 0) {
            entries = data.blog_posts;
          }
          // Legacy fallback to RSS entries
          else if (data.rss_entries && data.rss_entries.length > 0) {
            entries = data.rss_entries;
          }
          // Legacy fallback
          else if (data.entries && data.entries.length > 0) {
            entries = data.entries;
          }
          
          setFeedData(entries);
          setLastUpdated(data.scraped_at || data.updated);
          setError(null);
          setLoading(false);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message);
          setFeedData([]);
          setLoading(false);
        }
      }
    };

    fetchFeed();
    
    // Cleanup function to prevent memory leaks in React 18
    return () => { ignore = true; };
  }, []);

  // Loading state
  if (loading) return <LoadingSpinner />;
  
  // Error state
  if (error) return (
    <div className="text-center py-8">
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mx-auto max-w-md">
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="font-bold">Feed failed to load</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    </div>
  );
  
  // No posts state
  if (!feedData || feedData.length === 0) return (
    <div className="text-center py-8">
      <div className="bg-gray-100 border border-gray-300 text-gray-700 px-4 py-3 rounded mx-auto max-w-md">
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="font-bold">No posts available</p>
            <p className="text-sm">Please check back later for updates.</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
          SmartCanucks Affiliate Deals
        </h1>
        <p className="text-gray-600">
          Latest Canadian deals with affiliate links
        </p>
        {lastUpdated && (
          <p className="text-sm text-gray-500 mt-2">
            Last updated: {new Date(lastUpdated).toLocaleString()}
          </p>
        )}
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {feedData.map((item, index) => (
          <FeedItem key={`${item.link}-${index}`} item={item} />
        ))}
      </div>
      
      <footer className="text-center mt-8 text-gray-500 text-sm">
        <p>Showing {feedData.length} {feedData.length === 1 ? 'post' : 'posts'}</p>
        <p className="mt-2">
          <a 
            href="https://github.com/your-username/your-repo" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-500 hover:text-blue-700 transition-colors"
          >
            View on GitHub
          </a>
        </p>
      </footer>
    </div>
  );
};

export default FeedDisplay;