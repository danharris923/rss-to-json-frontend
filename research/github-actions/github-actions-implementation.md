# GitHub Actions Implementation Guide

## Python Setup with GitHub Actions

### Setup-Python Action (v5 - Latest 2024)
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'  # Enables dependency caching
```

## Complete RSS Feed Automation Workflow

### Basic Implementation
```yaml
name: RSS Feed Update
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
  workflow_dispatch:     # Manual trigger

jobs:
  update-feed:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install feedparser
        
    - name: Run RSS parser
      run: python scripts/rss_to_json.py
      
    - name: Check for changes
      id: verify-changed-files
      run: |
        if [ -n "$(git status --porcelain)" ]; then
          echo "changed=true" >> $GITHUB_OUTPUT
        else
          echo "changed=false" >> $GITHUB_OUTPUT
        fi
        
    - name: Commit and push if changed
      if: steps.verify-changed-files.outputs.changed == 'true'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add public/feed.json
        git commit -m "Update RSS feed data [skip ci]"
        git push
```

### Advanced Implementation with Error Handling
```yaml
name: RSS Feed Automation

on:
  schedule:
    - cron: '5 * * * *'  # 5 minutes past every hour
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  update-rss-feed:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
        cache: 'pip'
        
    - name: Cache dependencies
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-feedparser
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install feedparser
        
    - name: Run RSS feed parser
      id: parse
      run: |
        python scripts/rss_to_json.py
        echo "status=$?" >> $GITHUB_OUTPUT
        
    - name: Log parsing results
      run: |
        echo "Parse status: ${{ steps.parse.outputs.status }}"
        if [ -f public/feed.json ]; then
          echo "Feed file created successfully"
          echo "File size: $(stat -c%s public/feed.json) bytes"
        else
          echo "Warning: feed.json not found"
        fi
        
    - name: Commit changes
      uses: stefanzweifel/git-auto-commit-action@v5
      with:
        commit_message: '📰 Update RSS feed content'
        file_pattern: 'public/feed.json'
        commit_user_name: github-actions[bot]
        commit_user_email: github-actions[bot]@users.noreply.github.com
        skip_dirty_check: false
```

## Git Operations in GitHub Actions

### Method 1: Direct Git Commands
```yaml
- name: Configure Git
  run: |
    git config user.name "GitHub Actions Bot"
    git config user.email "actions@github.com"

- name: Commit and Push
  run: |
    git add .
    git diff --quiet && git diff --staged --quiet || (
      git commit -m "Automated update"
      git push
    )
```

### Method 2: Using git-auto-commit-action
```yaml
- name: Commit changes
  uses: stefanzweifel/git-auto-commit-action@v5
  with:
    commit_message: 'Update RSS feed'
    file_pattern: '*.json'
    commit_author: GitHub Actions <actions@github.com>
```

### Method 3: Conditional Commit
```yaml
- name: Check for changes
  id: check_changes
  run: |
    if [[ -n $(git status -s) ]]; then
      echo "changes=true" >> $GITHUB_OUTPUT
    else
      echo "changes=false" >> $GITHUB_OUTPUT
    fi

- name: Commit if changed
  if: steps.check_changes.outputs.changes == 'true'
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
    git add -A
    git commit -m "Auto-update feed data"
    git push
```

## Environment Variables and Secrets

### Using Environment Variables
```yaml
env:
  FEED_URL: https://example.com/feed.xml
  
steps:
  - name: Parse feed
    run: python parse.py --url "$FEED_URL"
```

### Using Secrets
```yaml
- name: Parse protected feed
  env:
    FEED_API_KEY: ${{ secrets.FEED_API_KEY }}
  run: python parse.py --api-key "$FEED_API_KEY"
```

## Best Practices for 2024

1. **Use Latest Action Versions**
   - `actions/checkout@v4`
   - `actions/setup-python@v5`
   - `actions/cache@v4`

2. **Permissions**
   ```yaml
   permissions:
     contents: write  # For pushing commits
     pull-requests: write  # If creating PRs
   ```

3. **Skip CI to Avoid Loops**
   - Add `[skip ci]` to commit messages
   - Or use `skip_trigger: true` in some actions

4. **Error Handling**
   ```yaml
   - name: Parse feed
     id: parse
     continue-on-error: true
     run: python parse.py
     
   - name: Handle failure
     if: steps.parse.outcome == 'failure'
     run: echo "Parse failed, using fallback"
   ```

5. **Debugging**
   ```yaml
   - name: Debug info
     run: |
       echo "Event: ${{ github.event_name }}"
       echo "Ref: ${{ github.ref }}"
       echo "SHA: ${{ github.sha }}"
   ```

## Complete Production Example
```yaml
name: Hourly RSS Feed Update

on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
    inputs:
      debug_enabled:
        description: 'Enable debug logging'
        required: false
        default: 'false'

jobs:
  update-feed:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
        cache: 'pip'
        
    - name: Install dependencies
      run: |
        pip install feedparser
        
    - name: Parse RSS feeds
      env:
        DEBUG: ${{ github.event.inputs.debug_enabled }}
      run: python scripts/rss_to_json.py
      
    - name: Verify output
      run: |
        if [ ! -f public/feed.json ]; then
          echo "Error: feed.json not created"
          exit 1
        fi
        
    - name: Commit changes
      run: |
        git config --global user.name 'github-actions[bot]'
        git config --global user.email 'github-actions[bot]@users.noreply.github.com'
        git add public/feed.json
        git diff --quiet --cached || git commit -m "Update RSS feed [skip ci]"
        git push
```