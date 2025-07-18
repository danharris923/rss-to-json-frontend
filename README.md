# RSS-to-JSON Frontend Deployment System

A modern, serverless RSS-to-JSON frontend deployment system that automatically fetches RSS feeds hourly, converts them to JSON, and displays them in a React-based frontend. The system is self-contained, GitHub-hosted, and requires zero backend infrastructure.

## 🚀 Features

- **Serverless Architecture**: No ongoing server costs or maintenance
- **Automation**: Hourly RSS feed updates via GitHub Actions
- **Modern Frontend**: React 18 with mobile-first responsive design
- **Static Hosting**: Deploy to GitHub Pages or Vercel
- **Error Handling**: Graceful degradation at all levels
- **Zero Configuration**: Works out of the box with minimal setup

## 🏗️ Architecture

```
RSS Feed → Python Script → JSON File → React Frontend → Static Hosting
    ↓            ↓             ↓           ↓             ↓
  Hourly     feedparser    GitHub      Tailwind    GitHub Pages
  Cron       Error         Actions       CSS         or Vercel
            Handling      Automation   Components
```

## 📁 Project Structure

```
clickandsave/
├── public/
│   ├── index.html          # React app entry point
│   ├── favicon.ico         # Site favicon
│   └── feed.json           # RSS feed data (auto-generated)
├── src/
│   ├── components/
│   │   ├── FeedDisplay.js   # Main feed display component
│   │   ├── FeedItem.js      # Individual feed item component
│   │   └── LoadingSpinner.js # Loading state component
│   ├── App.js               # Main React app
│   ├── App.css              # App styling
│   └── index.js             # React entry point
├── scripts/
│   └── rss_to_json.py       # RSS fetcher script
├── .github/workflows/
│   ├── rss-update.yml       # RSS feed update automation
│   └── deploy-pages.yml     # GitHub Pages deployment
├── tests/
│   ├── test_rss_fetcher.py  # Unit tests for RSS fetcher
│   ├── test_plan.md         # Manual testing checklist
│   └── sample_feeds/        # Test RSS feed samples
├── package.json             # Node.js dependencies
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 14+ and npm
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/clickandsave.git
   cd clickandsave
   ```

2. **Install dependencies**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   npm install
   ```

3. **Configure RSS feed URL**
   ```bash
   # Edit the RSS feed URL in scripts/rss_to_json.py
   # Change DEFAULT_FEED_URL to your desired RSS feed
   ```

4. **Test the RSS fetcher**
   ```bash
   python scripts/rss_to_json.py
   ```

5. **Start the development server**
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`.

## 📊 Usage

### RSS Feed Updates

The system automatically fetches RSS feeds every hour via GitHub Actions. To manually update:

```bash
# Manually run the RSS fetcher
python scripts/rss_to_json.py --url https://your-rss-feed.com/feed.xml

# Or use a custom output location
python scripts/rss_to_json.py --url https://feed.com/rss --output custom/path/feed.json
```

### React Development

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Analyze bundle size
npm run analyze
```

## 🚀 Deployment

### GitHub Pages

1. **Configure repository settings**
   - Enable GitHub Actions in your repository
   - Set up GitHub Pages to use Actions for deployment

2. **Update package.json**
   ```json
   {
     "homepage": "https://your-username.github.io/clickandsave"
   }
   ```

3. **Deploy**
   ```bash
   npm run deploy
   ```

### Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel --prod
   ```

### Automatic Deployment

The system includes GitHub Actions workflows for automatic deployment:

- **RSS Updates**: `.github/workflows/rss-update.yml` - Updates feed data hourly
- **Site Deployment**: `.github/workflows/deploy-pages.yml` - Deploys to GitHub Pages on push

## 🔧 Configuration

### RSS Feed Configuration

Edit `scripts/rss_to_json.py` to customize:

```python
# Change the default RSS feed URL
DEFAULT_FEED_URL = "https://your-feed.com/rss"

# Customize the output format
def parse_rss_feed(feed_url):
    # Add custom parsing logic here
    pass
```

### React Configuration

Edit `src/components/FeedDisplay.js` to customize:

```javascript
// Customize the feed display
const FeedDisplay = () => {
  // Add custom display logic here
};
```

### GitHub Actions Configuration

Edit `.github/workflows/rss-update.yml` to customize:

```yaml
on:
  schedule:
    # Change the cron schedule (currently every hour)
    - cron: '5 * * * *'
```

## 🧪 Testing

### Unit Tests

```bash
# Run Python unit tests
python -m pytest tests/test_rss_fetcher.py -v

# Run React tests
npm test
```

### Manual Testing

Follow the manual testing checklist in `tests/test_plan.md`:

1. **RSS Fetcher Tests**
   - Valid RSS feeds
   - Malformed feeds
   - Network errors
   - Empty feeds

2. **Frontend Tests**
   - Component rendering
   - Mobile responsiveness
   - Error states
   - Loading states

3. **Integration Tests**
   - End-to-end workflow
   - Deployment testing
   - Performance testing

### Test Data

Sample RSS feeds for testing are available in `tests/sample_feeds/`:

- `valid_feed.xml` - Well-formed RSS feed
- `malformed_feed.xml` - Malformed XML for error testing
- `empty_feed.xml` - Empty feed for edge case testing
- `partial_feed.xml` - Feed with missing fields

## 🔍 Troubleshooting

### Common Issues

1. **RSS fetcher fails**
   ```bash
   # Check if the feed URL is accessible
   curl -I https://your-feed.com/rss
   
   # Test with a known working feed
   python scripts/rss_to_json.py --url https://rss.cnn.com/rss/edition.rss
   ```

2. **React app won't load feed data**
   - Ensure `public/feed.json` exists
   - Check browser console for errors
   - Verify the feed JSON structure

3. **GitHub Actions workflow fails**
   - Check the Actions tab in your repository
   - Verify Python and Node.js versions
   - Ensure repository permissions allow Actions to write

4. **Deployment issues**
   - For GitHub Pages: Check repository settings
   - For Vercel: Verify build output directory
   - Ensure all dependencies are listed in package.json

### Debug Mode

Enable debug logging:

```bash
# For RSS fetcher
python scripts/rss_to_json.py --url https://feed.com/rss --debug

# For GitHub Actions
# Use the workflow_dispatch trigger with debug enabled
```

## 📈 Performance

### Optimization Features

- **Caching**: Feed data cached for 5 minutes
- **Lazy Loading**: Components load efficiently
- **Bundle Size**: Optimized React build
- **Mobile First**: Responsive design for all devices
- **Static Assets**: Served from CDN

### Performance Metrics

Target metrics:
- First Contentful Paint: < 2s
- Largest Contentful Paint: < 3s
- Time to Interactive: < 3s
- Cumulative Layout Shift: < 0.1

## 🛡️ Security

### Security Features

- **HTTPS Only**: All requests over secure connections
- **CSP Headers**: Content Security Policy implemented
- **XSS Protection**: Safe handling of external content
- **No Secrets**: No sensitive data in client-side code

### Best Practices

- External links open in new tabs with `noopener noreferrer`
- HTML content is sanitized before display
- No user input processing on the frontend
- Regular dependency updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test` and `python -m pytest tests/`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [React](https://reactjs.org/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
- RSS parsing with [feedparser](https://pythonhosted.org/feedparser/)
- Automated with [GitHub Actions](https://github.com/features/actions)
- Hosted on [GitHub Pages](https://pages.github.com/) / [Vercel](https://vercel.com/)

## 📞 Support

- Create an issue for bug reports
- Start a discussion for feature requests
- Check the [troubleshooting section](#troubleshooting) for common issues

---

**Made with ❤️ for the RSS community**