"""
NSE Bhavcopy downloader and parser
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from loguru import logger
import zipfile
import io
import time
from .base import MarketDataDownloader
from .holidays import get_last_trading_day, is_trading_day


class NSEDownloader(MarketDataDownloader):
    """NSE bhavcopy downloader"""
    
    # New UDiFF Format URL
    BHAVCOPY_UDIFF_URL = "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
    # Fallback Old URL
    BHAVCOPY_OLD_URL = "https://archives.nseindia.com/content/historical/EQUITIES/{year}/{month}/cm{old_date_str}bhav.csv.zip"
    
    def __init__(self, data_dir: Path):
        super().__init__(data_dir / "nse")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/all-reports',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session with NSE to get cookies"""
        try:
            logger.debug("Initializing NSE session...")
            
            # First visit the main page to get cookies
            main_response = self.session.get(
                "https://www.nseindia.com",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                },
                timeout=30
            )
            
            # Then visit the reports page
            reports_response = self.session.get(
                "https://www.nseindia.com/all-reports",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                },
                timeout=30
            )
            
            # Get the API endpoint for merged daily reports
            api_response = self.session.get(
                "https://www.nseindia.com/api/merged-daily-reports?key=favCapital",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://www.nseindia.com/all-reports',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                timeout=30
            )
            
            logger.debug("NSE session initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize NSE session: {e}")
    
    def get_exchange_name(self) -> str:
        return "NSE"
    
    def download_bhavcopy(self, date: datetime) -> Optional[Path]:
        """
        Download NSE bhavcopy for a specific date
        """
        try:
            # Get valid trading day (roll back if weekend/holiday)
            valid_date = get_last_trading_day(date)
            
            if valid_date != date:
                logger.info(f"Target date {date.strftime('%Y-%m-%d')} is holiday/weekend. Fetching {valid_date.strftime('%Y-%m-%d')}")
            
            date_str_udiff = valid_date.strftime("%Y%m%d")
            
            # Try UDiFF format first (new format)
            url = self.BHAVCOPY_UDIFF_URL.format(date_str=date_str_udiff)
            
            logger.debug(f"Downloading NSE bhavcopy from {url}")
            
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
            
            response = self.session.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
                    'Accept': 'application/zip, application/octet-stream, */*',
                    'Referer': 'https://www.nseindia.com/all-reports',
                },
                timeout=30
            )
            
            # If UDiFF fails, try old format
            if response.status_code != 200:
                old_date_str = valid_date.strftime("%d%m%Y")
                year = valid_date.strftime("%Y")
                month = valid_date.strftime("%b").upper()
                url = self.BHAVCOPY_OLD_URL.format(year=year, month=month, old_date_str=old_date_str)
                
                logger.debug(f"UDiFF not found. Trying old format: {url}")
                response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"NSE bhavcopy not found for {valid_date.strftime('%Y-%m-%d')} (Status: {response.status_code})")
                return None
            
            # Check if response is actually a zip file
            content_type = response.headers.get('content-type', '')
            if 'html' in content_type.lower() or response.text.startswith('<'):
                logger.warning(f"NSE returned HTML instead of zip for {valid_date.strftime('%Y-%m-%d')}")
                return None
            
            # Save zip file
            zip_path = self.data_dir / f"bhavcopy_{date_str_udiff}.csv.zip"
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract CSV
            try:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                    csv_files = [f for f in zf.namelist() if f.endswith('.csv')]
                    if not csv_files:
                        logger.warning(f"No CSV found in NSE zip for {valid_date.strftime('%Y-%m-%d')}")
                        return None
                    
                    csv_filename = csv_files[0]
                    csv_path = self.data_dir / csv_filename
                    
                    with open(csv_path, 'wb') as f:
                        f.write(zf.read(csv_filename))
                    
                    logger.debug(f"NSE bhavcopy saved to {csv_path}")
                    return csv_path
                    
            except zipfile.BadZipFile:
                logger.warning(f"Bad zip file for NSE {valid_date.strftime('%Y-%m-%d')}")
                return None
            
        except Exception as e:
            logger.error(f"Error downloading NSE bhavcopy for {date.strftime('%Y-%m-%d')}: {e}")
            return None
    
    def parse_bhavcopy(self, file_path: Path) -> pd.DataFrame:
        """
        Parse NSE bhavcopy CSV
        Supports both old format and new UDiFF format
        """
        try:
            # Try to detect the format by reading first few lines
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            
            is_udiff = 'TckrSymb' in first_line or 'TradDt' in first_line
            
            df = pd.read_csv(file_path)
            
            if is_udiff:
                # New UDiFF format
                logger.debug(f"Parsing NSE UDiFF format: {file_path.name}")
                
                # Filter for Equity (EQ)
                if 'Srs' in df.columns:
                    df = df[df['Srs'] == 'EQ']
                
                # Map columns
                result = pd.DataFrame({
                    'date': pd.to_datetime(df.get('TradDt', df.get('Date', pd.Timestamp.now()))),
                    'exchange': 'NSE',
                    'symbol': df.get('TckrSymb', df.get('SYMBOL', '')).astype(str).str.strip(),
                    'security_id': df.get('TckrSymb', df.get('SYMBOL', '')).astype(str).str.strip(),
                    'open': pd.to_numeric(df.get('OpnPric', df.get('OPEN', 0)), errors='coerce'),
                    'high': pd.to_numeric(df.get('HghPric', df.get('HIGH', 0)), errors='coerce'),
                    'low': pd.to_numeric(df.get('LwPric', df.get('LOW', 0)), errors='coerce'),
                    'close': pd.to_numeric(df.get('ClsPric', df.get('CLOSE', 0)), errors='coerce'),
                    'volume': pd.to_numeric(df.get('TtlTrdVol', df.get('TOTTRDQTY', 0)), errors='coerce'),
                    'previous_close': pd.to_numeric(df.get('PrvsClsG', df.get('PREVCLOSE', 0)), errors='coerce'),
                    'isin': df.get('ISIN', '').astype(str).str.strip()
                })
            else:
                # Old format
                logger.debug(f"Parsing NSE old format: {file_path.name}")
                
                # Filter for EQ series
                if 'SERIES' in df.columns:
                    df = df[df['SERIES'] == 'EQ']
                
                # Get date from TIMESTAMP or filename
                if 'TIMESTAMP' in df.columns:
                    date_series = pd.to_datetime(df['TIMESTAMP'])
                else:
                    # Try to get date from filename
                    date_str = file_path.stem
                    # Remove common prefixes
                    for prefix in ['cm', 'bhavcopy_']:
                        if date_str.startswith(prefix):
                            date_str = date_str[len(prefix):]
                    date_str = date_str[:8]  # Take first 8 digits for DDMMYYYY
                    date_series = pd.to_datetime(date_str, format='%d%m%Y')
                
                result = pd.DataFrame({
                    'date': date_series,
                    'exchange': 'NSE',
                    'symbol': df['SYMBOL'].astype(str).str.strip(),
                    'security_id': df['SYMBOL'].astype(str).str.strip(),
                    'open': pd.to_numeric(df['OPEN'], errors='coerce'),
                    'high': pd.to_numeric(df['HIGH'], errors='coerce'),
                    'low': pd.to_numeric(df['LOW'], errors='coerce'),
                    'close': pd.to_numeric(df['CLOSE'], errors='coerce'),
                    'volume': pd.to_numeric(df.get('TOTTRDQTY', 0), errors='coerce'),
                    'previous_close': pd.to_numeric(df.get('PREVCLOSE', 0), errors='coerce'),
                    'isin': df.get('ISIN', '').astype(str).str.strip()
                })
            
            # Clean data
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in result.columns:
                    result[col] = pd.to_numeric(result[col], errors='coerce')
            
            # Remove rows with invalid close price
            result = result[result['close'].notna()]
            result = result[result['close'] > 0]
            
            logger.debug(f"Parsed {len(result)} NSE securities from {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing NSE bhavcopy {file_path}: {e}")
            return pd.DataFrame()