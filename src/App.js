import React from 'react';
import FeedDisplay from './components/FeedDisplay';
import './App.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg max-w-md mx-auto">
              <h2 className="text-xl font-bold mb-2">Something went wrong</h2>
              <p className="text-sm mb-4">
                We encountered an error while loading the application.
              </p>
              <button 
                onClick={() => window.location.reload()}
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <div className="App min-h-screen bg-gray-50">
        <FeedDisplay />
      </div>
    </ErrorBoundary>
  );
}

export default App;