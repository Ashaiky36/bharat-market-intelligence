"""
Configuration settings for the IPO scraper
"""
import os
from pathlib import Path
from datetime import datetime, timedelta

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# API Configuration
CHITTORGARH_API_URL = "https://webnodejs.chittorgarh.com/cloud/report/data-read/25/1/8/2026/2026-27/0/all/0"
CHITTORGARH_BASE_URL = "https://www.chittorgarh.com"

# Headers for impersonating Chrome browser
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,en-IN;q=0.8,de-AT;q=0.7,de;q=0.6",
    "dnt": "1",
    "origin": CHITTORGARH_BASE_URL,
    "priority": "u=1, i",
    "referer": f"{CHITTORGARH_BASE_URL}/",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
}

# Financial data configuration
RETURN_PERIODS = [2, 5, 10, 15, 30]  # days
YFINANCE_MAX_RETRIES = 3
YFINANCE_RETRY_DELAY = 1  # seconds

# Output CSV filename
OUTPUT_CSV = DATA_DIR / f"ipo_metadata_{datetime.now().strftime('%Y%m%d')}.csv"