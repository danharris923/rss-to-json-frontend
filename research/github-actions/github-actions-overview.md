# GitHub Actions Documentation Research

## Overview
GitHub Actions is a continuous integration and continuous delivery (CI/CD) platform that allows you to automate your build, test, and deployment pipeline.

## Workflow Syntax

### Basic Structure
```yaml
name: Workflow Name
on: 
  # Triggers
jobs:
  job_id:
    runs-on: runner-type
    steps:
      - uses: actions/checkout@v4
      - run: command-to-execute
```

### Key Components

#### 1. Triggers (`on`)
- **push**: Triggered on code push
- **pull_request**: Triggered on PR events
- **schedule**: Cron-based scheduling
- **workflow_dispatch**: Manual trigger

#### 2. Jobs
- Defined with unique `job_id`
- Specify `runs-on` for runner environment
- Support conditional execution with `if`

#### 3. Steps
- Use pre-built actions with `uses`
- Run shell commands with `run`
- Support environment variables

## Scheduled Workflows (Cron)

### Cron Syntax
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12 or JAN-DEC)
│ │ │ │ ┌───────────── day of the week (0 - 6 or SUN-SAT)
│ │ │ │ │
* * * * *
```

### Hourly Schedule Examples
```yaml
on:
  schedule:
    - cron: '0 * * * *'    # Every hour on the hour
    - cron: '30 * * * *'   # Every hour at :30
    - cron: '0 */2 * * *'  # Every 2 hours
    - cron: '15 */4 * * *' # Every 4 hours at :15
```

### Important Notes
- Uses UTC timezone
- Minimum interval: 5 minutes
- Only runs on default branch
- Disabled after 60 days of inactivity (public repos)

## Complete Hourly Workflow Example
```yaml
name: Hourly RSS Update
on:
  schedule:
    # Run every hour at 5 minutes past
    - cron: '5 * * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  update-feed:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install feedparser
      
      - name: Run RSS fetcher
        run: python scripts/rss_to_json.py
      
      - name: Check for changes
        id: check
        run: |
          git diff --exit-code public/feed.json || echo "changed=true" >> $GITHUB_OUTPUT
      
      - name: Commit changes
        if: steps.check.outputs.changed == 'true'
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add public/feed.json
          git commit -m "Update RSS feed data"
          git push
```

## Runner Options
- **GitHub-hosted runners**: Ubuntu, Windows, macOS
- **Self-hosted runners**: Custom environments

## Security Features
- Secrets management
- OpenID Connect
- Artifact attestations

## Best Practices
1. Use reusable workflows
2. Implement proper secret management
3. Leverage caching for performance
4. Monitor workflow execution times
5. Use specific action versions (e.g., `@v4`)
6. Add `workflow_dispatch` for manual testing