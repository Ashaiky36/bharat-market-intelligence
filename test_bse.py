# test_bse.py
from datetime import datetime
from src.market_data.bse import BSEDownloader
from pathlib import Path

# Test a specific date
date = datetime(2026, 8, 7)  # A trading day
downloader = BSEDownloader(Path("data/bhavcopy"))

file_path = downloader.download_bhavcopy(date)
if file_path:
    print(f"Downloaded: {file_path}")
    df = downloader.parse_bhavcopy(file_path)
    print(f"Parsed {len(df)} records")
else:
    print("Failed to download")