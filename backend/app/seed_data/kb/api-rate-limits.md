# API Errors & Rate Limits

- HTTP 429 responses mean the account exceeded its plan's requests-per-minute limit. Free tier: 60 rpm, Pro: 600 rpm, Enterprise: custom.
- Recommend exponential backoff starting at 1s, doubling up to 30s, for automatic retries.
- HTTP 500/502/503 spikes are usually transient; check the status page first before escalating to engineering.
- Persistent timeouts on a specific endpoint for more than 15 minutes should be escalated to the on-call engineer immediately.
- API keys can be rotated from Settings > Developer > API Keys; rotating a key immediately invalidates the old one, so warn customers before they do it in production.
