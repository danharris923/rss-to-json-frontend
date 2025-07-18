import React from 'react';

const FeedItem = ({ item }) => {
  // Format the published date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return dateString;
    }
  };

  // Get merchant info for styling
  const getMerchantInfo = (merchant) => {
    const merchantColors = {
      'amazon': 'bg-orange-100 text-orange-800',
      'walmart': 'bg-blue-100 text-blue-800',
      'bestbuy': 'bg-yellow-100 text-yellow-800',
      'adidas': 'bg-black text-white',
      'staples': 'bg-red-100 text-red-800',
      'apple': 'bg-gray-100 text-gray-800',
    };
    
    return {
      color: merchantColors[merchant] || 'bg-gray-100 text-gray-800',
      name: merchant ? merchant.charAt(0).toUpperCase() + merchant.slice(1) : 'Deal'
    };
  };

  const merchantInfo = getMerchantInfo(item.merchant);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300 border border-gray-200">
      
      {/* Merchant Badge */}
      {item.merchant && (
        <div className="flex justify-between items-center mb-3">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${merchantInfo.color}`}>
            {merchantInfo.name}
          </span>
          {item.affiliate_processed && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              ✓ Affiliate
            </span>
          )}
        </div>
      )}
      
      <h3 className="text-xl font-semibold mb-3 line-clamp-2 leading-tight">
        <a 
          href={item.link} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-gray-800 hover:text-blue-600 transition-colors duration-200 no-underline"
        >
          {item.title}
        </a>
      </h3>
      
      {/* Show link type and source */}
      {item.link_type && (
        <p className="text-sm text-gray-600 mb-2 capitalize">
          {item.link_type.replace('_', ' ')}
        </p>
      )}
      
      {item.published && (
        <p className="text-sm text-gray-500 mb-4 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
          {formatDate(item.published)}
        </p>
      )}
      
      <a 
        href={item.link} 
        target="_blank" 
        rel="noopener noreferrer"
        className="inline-flex items-center text-blue-500 hover:text-blue-700 font-medium transition-colors duration-200"
      >
        Shop Now
        <svg className="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </a>
    </div>
  );
};

export default FeedItem;