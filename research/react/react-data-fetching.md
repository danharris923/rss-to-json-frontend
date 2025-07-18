# React Data Fetching Guide

## Modern React Patterns (2024)

### Basic Component Structure
```javascript
function Video({ video }) {
  return (
    <div>
      <Thumbnail video={video} />
      <h3>{video.title}</h3>
    </div>
  );
}
```

### Hooks Usage
```javascript
function SearchableVideoList({ videos }) {
  const [searchText, setSearchText] = useState('');
  const foundVideos = filterVideos(videos, searchText);
  // Component logic
}
```

## Data Fetching with useEffect (React 18 Compatible)

### Basic Pattern with Cleanup
```javascript
import React, { useState, useEffect } from 'react';

function FeedDisplay() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;
    
    const fetchData = async () => {
      try {
        const response = await fetch('/feed.json');
        
        if (!response.ok) {
          throw new Error(`HTTP error: Status ${response.status}`);
        }
        
        const jsonData = await response.json();
        
        // Only update state if component is still mounted
        if (!ignore) {
          setData(jsonData);
          setError(null);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message);
          setData(null);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    fetchData();
    
    // Cleanup function
    return () => {
      ignore = true;
    };
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {data && data.map(item => (
        <div key={item.id}>
          <h3>{item.title}</h3>
          <p>{item.description}</p>
        </div>
      ))}
    </div>
  );
}
```

### Alternative: IIFE Pattern
```javascript
useEffect(() => {
  (async () => {
    setLoading(true);
    try {
      const response = await fetch('/feed.json');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  })();
}, []);
```

## Custom Hook Pattern

### useFetch Hook
```javascript
const useFetch = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;
    
    (async () => {
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const result = await response.json();
        if (!ignore) setData(result);
      } catch (err) {
        if (!ignore) setError(err);
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    
    return () => { ignore = true; };
  }, [url]);

  return { data, loading, error };
};

// Usage
function MyComponent() {
  const { data, loading, error } = useFetch('/feed.json');
  // ... render logic
}
```

## useEffect Best Practices

### Purpose
- Synchronize components with external systems
- Run side effects after rendering
- Handle interactions that aren't tied to specific events

### Basic Structure
```javascript
useEffect(() => {
  // Effect logic
  return () => {
    // Cleanup function
  };
}, [dependencies]);
```

### Types of Effects
- Effects that run after every render
- Effects with empty dependency array (run only on mount)
- Effects with specific dependencies

### Key Points
- Only use for synchronizing with external systems
- Implement cleanup functions to prevent memory leaks
- Specify all variables used inside the Effect in dependencies
- Empty array `[]` means "run only on mount"

### Common Use Cases
- Controlling non-React widgets
- Subscribing to events
- Triggering animations
- Fetching data
- Sending analytics

## Error Handling Patterns

### Basic Error Handling
```javascript
try {
  const response = await fetch('/feed.json');
  
  if (!response.ok) {
    throw new Error(`HTTP error: Status ${response.status}`);
  }
  
  const jsonData = await response.json();
  setData(jsonData);
} catch (err) {
  setError(err.message);
}
```

### Specific Error Types
```javascript
catch (err) {
  if (err.name === 'AbortError') {
    console.log('Fetch aborted');
  } else {
    setError(err.message);
  }
}
```

## Loading States

### Simple Loading
```javascript
if (loading) return <div>Loading...</div>;
```

### Skeleton Loading
```javascript
if (loading) return (
  <div className="skeleton">
    <div className="skeleton-title"></div>
    <div className="skeleton-text"></div>
  </div>
);
```

## Modern Alternatives (2024)

### TanStack Query (React Query)
```javascript
import { useQuery } from '@tanstack/react-query';

function MyComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['feed'],
    queryFn: async () => {
      const response = await fetch('/feed.json');
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  
  return <div>{/* Render data */}</div>;
}
```

## Best Practices for 2024

1. **Always include cleanup functions** to prevent memory leaks
2. **Handle loading and error states** explicitly
3. **Check response.ok** before parsing JSON
4. **Consider using modern libraries** like TanStack Query or SWR
5. **Use dependency arrays correctly** to control when effects run
6. **Don't rush to add Effects** - consider direct state updates first