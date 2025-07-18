import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="relative">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <div className="absolute top-0 left-0 rounded-full h-12 w-12 border-t-2 border-blue-200 animate-pulse"></div>
      </div>
      <p className="ml-4 text-gray-600 text-lg">Loading feed...</p>
    </div>
  );
};

export default LoadingSpinner;