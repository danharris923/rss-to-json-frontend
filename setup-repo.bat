@echo off
echo Setting up RSS-to-JSON Frontend Repository...
echo.

echo Step 1: Remove old origin
git remote remove origin

echo Step 2: Add new origin (replace YOUR_USERNAME with your GitHub username)
set /p username="Enter your GitHub username: "
git remote add origin https://github.com/%username%/rss-to-json-frontend.git

echo Step 3: Push to new repository
git push -u origin main

echo.
echo ✅ Repository setup complete!
echo.
echo Next steps:
echo 1. Enable GitHub Actions in your repository settings
echo 2. Enable GitHub Pages (Settings → Pages → Source: GitHub Actions)
echo 3. Your RSS feed will update automatically every hour!
echo.
echo Repository URL: https://github.com/%username%/rss-to-json-frontend
echo Live site will be: https://%username%.github.io/rss-to-json-frontend
echo.
pause