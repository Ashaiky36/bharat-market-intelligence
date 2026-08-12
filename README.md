# IPO Metadata Scraper for Chittorgarh

A robust web scraper that extracts IPO metadata from Chittorgarh using `curl_cffi` to bypass Cloudflare and other WAF protections.

## Features

- 🚀 Bypasses WAF protection using TLS fingerprint impersonation
- 📊 Fetches IPO data from hidden JSON APIs
- 💹 Enriches data with historical prices using yfinance
- 📈 Calculates returns for multiple time periods (2d, 5d, 10d, 15d, 1m)
- 📁 Exports data to CSV format
- 📊 Generates HTML reports with summary statistics

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ipo_scraper