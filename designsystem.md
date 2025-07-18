# Design System

## Colors
- **Primary**: #3B82F6 (Blue)
- **Secondary**: #10B981 (Green)
- **Error**: #EF4444 (Red)
- **Warning**: #F59E0B (Amber)
- **Background**: #FFFFFF (White)
- **Surface**: #F9FAFB (Light Gray)
- **Text Primary**: #111827 (Dark Gray)
- **Text Secondary**: #6B7280 (Medium Gray)

## Typography
- **Font Family**: Inter, system-ui, -apple-system, sans-serif
- **Headings**: 
  - H1: 2.5rem (40px), font-weight: 700
  - H2: 2rem (32px), font-weight: 600
  - H3: 1.5rem (24px), font-weight: 600
- **Body**: 1rem (16px), font-weight: 400
- **Small**: 0.875rem (14px), font-weight: 400

## Spacing
- Base unit: 4px
- Spacing scale: 0, 1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64

## Components

### Cards
```css
.card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### Buttons
```css
.button-primary {
  background: #3B82F6;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: background 0.2s;
}

.button-primary:hover {
  background: #2563EB;
}
```

### Loading States
- Skeleton screens with animated shimmer effect
- Spinner for inline loading
- Progress bars for determinate operations

### Error States
- Red border and text for form errors
- Error message below input fields
- Global error banner for critical errors

## Responsive Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## Accessibility
- WCAG 2.1 AA compliance
- Minimum contrast ratio: 4.5:1 for normal text
- Focus indicators on all interactive elements
- Semantic HTML structure
- ARIA labels where needed