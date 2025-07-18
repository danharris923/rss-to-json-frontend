# Project Planning: RSS-to-JSON Frontend Deployment

## Project Overview
A modern, serverless React-based frontend that displays blog/news content scraped hourly from third-party WordPress RSS feeds. The content is converted to JSON, committed to the repository, and displayed without requiring backend infrastructure.

## Architecture

### Core Components
1. **RSS Fetcher** - Python script that fetches RSS feeds and converts to JSON
2. **GitHub Actions** - Automated workflow that runs hourly to update content
3. **React Frontend** - Displays the JSON content in a modern UI
4. **Static Hosting** - GitHub Pages or Vercel deployment

### Technology Stack
- **Backend**: Python with feedparser
- **CI/CD**: GitHub Actions
- **Frontend**: React with Tailwind CSS
- **Hosting**: GitHub Pages / Vercel
- **Data Format**: JSON

## File Structure
```
/
├── public/
│   └── feed.json            # Output from RSS fetcher
├── scripts/
│   └── rss_to_json.py       # RSS fetcher script
├── src/
│   ├── components/
│   │   └── FeedDisplay.js   # React component for feed display
│   └── App.js               # Main React app
├── .github/
│   └── workflows/
│       └── rss-update.yml   # GitHub Action workflow
├── tests/
│   ├── test_rss_fetcher.py  # Unit tests for RSS fetcher
│   └── test_plan.md         # Manual testing checklist
├── package.json
├── .env.example
└── README.md
```

## Naming Conventions
- **Python files**: snake_case (e.g., `rss_to_json.py`)
- **React components**: PascalCase (e.g., `FeedDisplay.js`)
- **Test files**: test_*.py for Python, *.test.js for React
- **Environment variables**: UPPERCASE_WITH_UNDERSCORES

## Architecture Patterns
- **Modular Design**: Each component is self-contained and reusable
- **Error Handling**: Graceful degradation for missing/invalid data
- **Relative Paths**: All file references use relative paths for portability
- **Validation**: Input validation at every layer
- **Testing**: Unit tests for all core functionality

## Constraints
- No backend servers or databases
- Must work with static hosting
- GitHub Actions free tier limits (workflow runs)
- RSS feed availability and format variations
- Browser CORS restrictions for direct RSS fetching

## Development Workflow
1. Local development with mock data
2. Test RSS fetcher with various feed formats
3. Validate GitHub Action workflow locally
4. Deploy to staging environment
5. Production deployment after QA

## Success Metrics
- Zero server costs
- Automatic hourly updates
- < 3 second page load time
- Mobile-responsive design
- 99% uptime (dependent on GitHub/hosting platform)