# Manual Testing Plan for RSS-to-JSON Frontend System

## Overview
This document outlines the manual testing procedures for the RSS-to-JSON frontend deployment system. It covers all components: RSS fetcher, GitHub Actions, React frontend, and deployment.

## Pre-Testing Setup

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Node.js 14+ installed
- [ ] Git repository set up
- [ ] GitHub Actions enabled on repository

### Environment Setup
```bash
# Python environment
pip install -r requirements.txt

# Node.js environment
npm install

# Create test output directory
mkdir -p test_output
```

## Component Testing

### 1. RSS Fetcher Script Tests

#### Test 1.1: Valid RSS Feed
```bash
python scripts/rss_to_json.py --url https://rss.cnn.com/rss/edition.rss --output test_output/valid_feed.json
```

**Expected Results:**
- [ ] Script runs without errors
- [ ] JSON file created in test_output/
- [ ] File contains valid JSON structure
- [ ] Entries array has at least 1 item
- [ ] Each entry has title, link, and published fields
- [ ] Console shows "Successfully wrote X entries"

#### Test 1.2: Malformed RSS Feed
```bash
python scripts/rss_to_json.py --url https://httpbin.org/xml --output test_output/malformed_feed.json
```

**Expected Results:**
- [ ] Script shows warning about malformed feed
- [ ] Script either succeeds with data or fails gracefully
- [ ] Error message is informative
- [ ] No crash or unhandled exceptions

#### Test 1.3: Non-existent URL
```bash
python scripts/rss_to_json.py --url https://nonexistent.example.com/feed.xml --output test_output/nonexistent.json
```

**Expected Results:**
- [ ] Script exits with error code 1
- [ ] Error message displayed to stderr
- [ ] No output file created
- [ ] Error message is user-friendly

#### Test 1.4: Invalid URL Format
```bash
python scripts/rss_to_json.py --url "not-a-url" --output test_output/invalid_url.json
```

**Expected Results:**
- [ ] Script exits with error code 1
- [ ] Error message about invalid URL format
- [ ] No output file created

#### Test 1.5: Network Timeout
```bash
python scripts/rss_to_json.py --url https://httpbin.org/delay/30 --output test_output/timeout.json
```

**Expected Results:**
- [ ] Script handles timeout gracefully
- [ ] Error message about network timeout
- [ ] No output file created

### 2. GitHub Actions Workflow Tests

#### Test 2.1: Manual Workflow Trigger
1. Navigate to repository Actions tab
2. Select "RSS Feed Update" workflow
3. Click "Run workflow"
4. Enable debug logging

**Expected Results:**
- [ ] Workflow starts successfully
- [ ] Python environment set up correctly
- [ ] RSS fetcher runs without errors
- [ ] feed.json file updated in repository
- [ ] Git commit created if changes detected
- [ ] Workflow completes successfully

#### Test 2.2: No Changes Scenario
1. Run workflow twice in succession
2. Check second run behavior

**Expected Results:**
- [ ] First run creates/updates feed.json
- [ ] Second run detects no changes
- [ ] No unnecessary commits created
- [ ] Workflow still completes successfully

#### Test 2.3: Workflow Failure Handling
1. Temporarily break RSS URL in workflow
2. Run workflow

**Expected Results:**
- [ ] Workflow fails gracefully
- [ ] Error message clearly displayed
- [ ] No partial commits created
- [ ] Repository remains in clean state

### 3. React Frontend Tests

#### Test 3.1: Local Development Server
```bash
npm start
```

**Expected Results:**
- [ ] Development server starts on port 3000
- [ ] App loads without JavaScript errors
- [ ] Feed data displays correctly
- [ ] Loading spinner shows initially
- [ ] Error handling works for missing feed.json

#### Test 3.2: Production Build
```bash
npm run build
npm run serve
```

**Expected Results:**
- [ ] Build completes without errors
- [ ] Built files created in build/ directory
- [ ] App serves correctly from build directory
- [ ] All functionality works in production build

#### Test 3.3: Mobile Responsiveness
Test on various screen sizes:
- [ ] Mobile (320px - 768px)
- [ ] Tablet (768px - 1024px)
- [ ] Desktop (1024px+)

**Expected Results:**
- [ ] Layout adapts correctly to screen size
- [ ] Text remains readable
- [ ] Cards stack properly on mobile
- [ ] Touch targets are appropriate size
- [ ] No horizontal scrolling on mobile

#### Test 3.4: Feed Data Display
1. Ensure feed.json exists with sample data
2. Load application

**Expected Results:**
- [ ] Feed entries display correctly
- [ ] Titles are clickable links
- [ ] External links open in new tabs
- [ ] Published dates format correctly
- [ ] No broken layouts or missing content

#### Test 3.5: Error States
1. Remove feed.json file
2. Reload application

**Expected Results:**
- [ ] Error message displays clearly
- [ ] No JavaScript console errors
- [ ] User-friendly error message
- [ ] Option to retry/reload

#### Test 3.6: Empty Feed State
1. Replace feed.json with empty entries array
2. Reload application

**Expected Results:**
- [ ] "No posts available" message displays
- [ ] Layout remains intact
- [ ] No JavaScript errors

### 4. Deployment Tests

#### Test 4.1: GitHub Pages Deployment
```bash
npm run deploy
```

**Expected Results:**
- [ ] Build process completes successfully
- [ ] gh-pages branch created/updated
- [ ] Site accessible at GitHub Pages URL
- [ ] All functionality works on deployed site
- [ ] Feed data loads correctly

#### Test 4.2: Vercel Deployment (Optional)
```bash
npm run deploy:vercel
```

**Expected Results:**
- [ ] Vercel deployment completes
- [ ] Site accessible at Vercel URL
- [ ] All functionality works
- [ ] Feed updates work correctly

### 5. Integration Tests

#### Test 5.1: End-to-End Workflow
1. Update RSS feed URL in script
2. Run GitHub Actions workflow
3. Verify site updates

**Expected Results:**
- [ ] RSS fetcher gets new feed data
- [ ] GitHub Actions commits changes
- [ ] Site deployment updates automatically
- [ ] New feed data appears on site

#### Test 5.2: Performance Tests
1. Load site with network throttling
2. Test with large feed (100+ entries)

**Expected Results:**
- [ ] Site loads within 3 seconds on 3G
- [ ] Large feeds render without lag
- [ ] No memory leaks during usage
- [ ] Smooth scrolling and interactions

## Edge Case Testing

### Edge Case 1: RSS Feed with Special Characters
Test with feeds containing:
- [ ] Unicode characters
- [ ] HTML entities
- [ ] Special symbols
- [ ] Non-Latin scripts

### Edge Case 2: RSS Feed with Missing Fields
Test with feeds missing:
- [ ] Publication dates
- [ ] Descriptions
- [ ] Author information
- [ ] Categories

### Edge Case 3: Very Large RSS Feeds
Test with:
- [ ] Feeds with 500+ entries
- [ ] Entries with very long titles
- [ ] Large description content
- [ ] Multiple images per entry

### Edge Case 4: Network Conditions
Test under:
- [ ] Slow network connections
- [ ] Intermittent connectivity
- [ ] High latency conditions
- [ ] Offline scenarios

## Browser Compatibility Testing

Test on the following browsers:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Accessibility Testing

- [ ] Screen reader compatibility
- [ ] Keyboard navigation
- [ ] Color contrast compliance
- [ ] Focus indicators
- [ ] Alt text for images
- [ ] Semantic HTML structure

## Security Testing

- [ ] No XSS vulnerabilities
- [ ] Safe external link handling
- [ ] No sensitive data exposure
- [ ] Secure HTTPS usage
- [ ] Content Security Policy compliance

## Performance Testing

### Metrics to Monitor:
- [ ] First Contentful Paint < 2s
- [ ] Largest Contentful Paint < 3s
- [ ] Time to Interactive < 3s
- [ ] Cumulative Layout Shift < 0.1
- [ ] First Input Delay < 100ms

### Tools:
- [ ] Chrome DevTools Lighthouse
- [ ] WebPageTest
- [ ] GTmetrix
- [ ] Browser dev tools performance tab

## Test Environment Cleanup

After testing:
- [ ] Remove test output files
- [ ] Reset any configuration changes
- [ ] Clean up test branches
- [ ] Document any issues found
- [ ] Create GitHub issues for bugs

## Test Report Template

```
## Test Execution Report

**Date:** [Date]
**Tester:** [Name]
**Environment:** [Browser/OS]

### Tests Passed: X/Y
### Tests Failed: X/Y
### Tests Skipped: X/Y

### Issues Found:
1. [Issue description]
2. [Issue description]

### Recommendations:
1. [Recommendation]
2. [Recommendation]

### Next Steps:
- [ ] Fix identified issues
- [ ] Retest failed cases
- [ ] Deploy to production
```

## Automation Recommendations

For future testing efficiency:
- [ ] Set up automated visual regression testing
- [ ] Create end-to-end test suite with Cypress
- [ ] Implement performance monitoring
- [ ] Add accessibility testing to CI/CD
- [ ] Set up cross-browser testing automation