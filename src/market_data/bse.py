# # """
# # BSE Bhavcopy downloader and parser
# # """
# # import requests
# # import pandas as pd
# # from datetime import datetime, timedelta
# # from pathlib import Path
# # from typing import Optional
# # from loguru import logger
# # import zipfile
# # import io
# # import time
# # import json
# # from .base import MarketDataDownloader
# # from .holidays import get_last_trading_day


# # class BSEDownloader(MarketDataDownloader):
# #     """BSE bhavcopy downloader"""
    
# #     # BSE URLs
# #     BHAVCOPY_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.zip"
# #     BHAVCOPY_API_URL = "https://api.bseindia.com/BseIndiaAPI/api/GetBhavcopydata/w?flag=0"
# #     BHAVCOPY_DOWNLOAD_URL = "https://www.bseindia.com/download/BhavCopy/Equity/{filename}"
    
# #     def __init__(self, data_dir: Path):
# #         super().__init__(data_dir / "bse")
# #         self.session = requests.Session()
# #         self.session.headers.update({
# #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
# #             'Accept': 'application/json, text/plain, */*',
# #             'Accept-Language': 'en-US,en;q=0.9',
# #             'Referer': 'https://www.bseindia.com/',
# #             'DNT': '1',
# #             'Connection': 'keep-alive',
# #         })
    
# #     def get_exchange_name(self) -> str:
# #         return "BSE"
    
# #     def download_bhavcopy(self, date: datetime) -> Optional[Path]:
# #         """
# #         Download BSE bhavcopy for a specific date
# #         """
# #         try:
# #             # Get valid trading day
# #             valid_date = get_last_trading_day(date)
            
# #             if valid_date != date:
# #                 logger.info(f"Target date {date.strftime('%Y-%m-%d')} is holiday/weekend. Fetching {valid_date.strftime('%Y-%m-%d')}")
            
# #             date_str = valid_date.strftime("%d%m%Y")
            
# #             # Method 1: Try the API endpoint first (gets the actual file name)
# #             logger.debug(f"Trying BSE API for {valid_date.strftime('%Y-%m-%d')}")
            
# #             api_response = self.session.get(
# #                 self.BHAVCOPY_API_URL,
# #                 headers={
# #                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
# #                     'Accept': 'application/json, text/plain, */*',
# #                     'Referer': 'https://www.bseindia.com/',
# #                 },
# #                 timeout=30
# #             )
            
# #             if api_response.status_code == 200:
# #                 try:
# #                     api_data = api_response.json()
                    
# #                     # Look for the zip file in the response
# #                     if 'dsZip' in api_data and api_data['dsZip']:
# #                         zip_info = api_data['dsZip'][0]
# #                         filename = zip_info.get('FilePath', '')
                        
# #                         if filename:
# #                             download_url = self.BHAVCOPY_DOWNLOAD_URL.format(filename=filename)
# #                             logger.debug(f"Downloading BSE bhavcopy from API: {download_url}")
                            
# #                             response = self.session.get(
# #                                 download_url,
# #                                 headers={
# #                                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
# #                                     'Accept': 'application/zip, application/octet-stream, */*',
# #                                     'Referer': 'https://www.bseindia.com/',
# #                                 },
# #                                 timeout=60
# #                             )
                            
# #                             if response.status_code == 200:
# #                                 return self._save_bse_file(response, valid_date)
# #                 except json.JSONDecodeError:
# #                     logger.debug("BSE API returned non-JSON response, trying direct download")
            
# #             # Method 2: Try direct download with date pattern
# #             logger.debug(f"Trying BSE direct download for {valid_date.strftime('%Y-%m-%d')}")
            
# #             # Try different URL patterns
# #             url_patterns = [
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.zip",
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.zip",
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.csv",
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/{date_str}.zip",
# #             ]
            
# #             for url in url_patterns:
# #                 logger.debug(f"Trying: {url}")
# #                 response = self.session.get(
# #                     url,
# #                     headers={
# #                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
# #                         'Accept': 'application/zip, application/octet-stream, */*',
# #                         'Referer': 'https://www.bseindia.com/',
# #                     },
# #                     timeout=30
# #                 )
                
# #                 if response.status_code == 200:
# #                     return self._save_bse_file(response, valid_date)
                
# #                 # Check if response is HTML (error page)
# #                 if response.status_code == 200 and 'html' in response.headers.get('content-type', '').lower():
# #                     logger.debug(f"URL {url} returned HTML, skipping")
# #                     continue
            
# #             logger.warning(f"BSE bhavcopy not found for {valid_date.strftime('%Y-%m-%d')}")
# #             return None
            
# #         except Exception as e:
# #             logger.error(f"Error downloading BSE bhavcopy for {date.strftime('%Y-%m-%d')}: {e}")
# #             return None
    
# #     def _save_bse_file(self, response, date: datetime) -> Optional[Path]:
# #         """
# #         Save BSE file (zip or csv) and extract if needed
# #         """
# #         try:
# #             date_str = date.strftime("%d%m%Y")
# #             content_type = response.headers.get('content-type', '').lower()
            
# #             # Check if it's a zip file
# #             if 'zip' in content_type or response.content[:4] == b'PK\x03\x04':
# #                 # Save and extract zip
# #                 zip_path = self.data_dir / f"EQ{date_str}.zip"
# #                 with open(zip_path, 'wb') as f:
# #                     f.write(response.content)
                
# #                 # Extract CSV from zip
# #                 try:
# #                     with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
# #                         csv_files = [f for f in zf.namelist() if f.endswith('.csv')]
# #                         if not csv_files:
# #                             logger.warning(f"No CSV found in BSE zip for {date.strftime('%Y-%m-%d')}")
# #                             return None
                        
# #                         csv_filename = csv_files[0]
# #                         csv_path = self.data_dir / csv_filename
                        
# #                         with open(csv_path, 'wb') as f:
# #                             f.write(zf.read(csv_filename))
                        
# #                         logger.debug(f"BSE bhavcopy saved to {csv_path}")
# #                         return csv_path
                        
# #                 except zipfile.BadZipFile:
# #                     logger.warning(f"Bad zip file for BSE {date.strftime('%Y-%m-%d')}")
# #                     return None
            
# #             # If it's a CSV directly
# #             elif 'csv' in content_type or response.text.startswith('SC_CODE'):
# #                 csv_path = self.data_dir / f"EQ{date_str}.csv"
# #                 with open(csv_path, 'w', encoding='utf-8') as f:
# #                     f.write(response.text)
# #                 return csv_path
            
# #             else:
# #                 logger.warning(f"Unknown content type for BSE {date.strftime('%Y-%m-%d')}: {content_type}")
# #                 return None
                
# #         except Exception as e:
# #             logger.error(f"Error saving BSE file: {e}")
# #             return None
    
# #     def parse_bhavcopy(self, file_path: Path) -> pd.DataFrame:
# #         """
# #         Parse BSE bhavcopy CSV
# #         """
# #         try:
# #             # First, determine the format by reading the file
# #             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
# #                 first_lines = [f.readline() for _ in range(5)]
            
# #             # Try different encodings and parsers
# #             df = None
# #             for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
# #                 try:
# #                     df = pd.read_csv(
# #                         file_path,
# #                         encoding=encoding,
# #                         skipinitialspace=True,
# #                         on_bad_lines='skip',
# #                         engine='python'  # More forgiving parser
# #                     )
# #                     if not df.empty:
# #                         break
# #                 except Exception:
# #                     continue
            
# #             if df is None or df.empty:
# #                 logger.warning(f"Could not parse BSE file {file_path.name}")
# #                 return pd.DataFrame()
            
# #             # Clean column names
# #             df.columns = df.columns.str.strip().str.upper()
            
# #             # Try to identify columns
# #             column_map = {}
            
# #             # Common BSE column names
# #             col_mappings = {
# #                 'SC_CODE': ['SC_CODE', 'CODE', 'SECURITYCODE', 'SC_CD'],
# #                 'SC_NAME': ['SC_NAME', 'NAME', 'SECURITYNAME'],
# #                 'OPEN': ['OPEN', 'OPENINGPRICE'],
# #                 'HIGH': ['HIGH', 'HIGHPRICE'],
# #                 'LOW': ['LOW', 'LOWPRICE'],
# #                 'CLOSE': ['CLOSE', 'CLOSINGPRICE', 'LAST'],
# #                 'VOLUME': ['NO_OF_SHRS', 'VOLUME', 'SHARES', 'TOTTRDQTY'],
# #                 'PREVCLOSE': ['PREVCLOSE', 'PREVIOUSCLOSE'],
# #                 'ISIN': ['ISIN']
# #             }
            
# #             for target, variants in col_mappings.items():
# #                 for variant in variants:
# #                     if variant in df.columns:
# #                         column_map[target] = variant
# #                         break
            
# #             # Check if we have minimum required columns
# #             required = ['CLOSE', 'SC_NAME']
# #             if 'SC_CODE' not in column_map and 'SC_NAME' not in column_map:
# #                 logger.warning(f"Could not identify symbol/name column in BSE file {file_path.name}")
# #                 return pd.DataFrame()
            
# #             # Build result
# #             result = pd.DataFrame()
            
# #             # Date from filename
# #             date_str = file_path.stem
# #             # Remove common prefixes/suffixes
# #             for prefix in ['EQ', 'BSE_EQ_BHAVCOPY_', 'BHAVCOPY_']:
# #                 if date_str.startswith(prefix):
# #                     date_str = date_str[len(prefix):]
# #             for suffix in ['_CSV', '_ZIP']:
# #                 if date_str.endswith(suffix):
# #                     date_str = date_str[:-len(suffix)]
            
# #             try:
# #                 # Try different date formats
# #                 for fmt in ['%d%m%Y', '%d%m%y', '%Y%m%d']:
# #                     try:
# #                         result['date'] = pd.to_datetime(date_str, format=fmt)
# #                         break
# #                     except ValueError:
# #                         continue
# #                 else:
# #                     # If all fail, use current date
# #                     result['date'] = pd.Timestamp.now()
# #             except:
# #                 result['date'] = pd.Timestamp.now()
            
# #             result['exchange'] = 'BSE'
# #             result['symbol'] = df[column_map.get('SC_NAME', df.columns[0])].astype(str).str.strip()
# #             result['security_id'] = df[column_map.get('SC_CODE', df.columns[0])].astype(str).str.strip()
            
# #             # Numeric fields
# #             for field in ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'PREVCLOSE']:
# #                 col_name = column_map.get(field)
# #                 if col_name and col_name in df.columns:
# #                     result[field.lower()] = pd.to_numeric(df[col_name], errors='coerce')
# #                 else:
# #                     result[field.lower()] = 0
            
# #             # ISIN
# #             if 'ISIN' in column_map:
# #                 result['isin'] = df[column_map['ISIN']].astype(str).str.strip()
# #             else:
# #                 result['isin'] = ''
            
# #             # Clean data
# #             for col in ['open', 'high', 'low', 'close', 'volume']:
# #                 if col in result.columns:
# #                     result[col] = pd.to_numeric(result[col], errors='coerce')
            
# #             # Remove rows with invalid close price
# #             result = result[result['close'].notna()]
# #             result = result[result['close'] > 0]
            
# #             logger.debug(f"Parsed {len(result)} BSE securities from {file_path.name}")
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"Error parsing BSE bhavcopy {file_path}: {e}")
# #             return pd.DataFrame()

# # # src/market_data/bse.py

# # """
# # BSE Bhavcopy downloader and parser
# # """
# # import requests
# # import pandas as pd
# # from datetime import datetime, timedelta
# # from pathlib import Path
# # from typing import Optional
# # from loguru import logger
# # import zipfile
# # import io
# # import time
# # import json
# # from .base import MarketDataDownloader
# # from .holidays import get_last_trading_day


# # class BSEDownloader(MarketDataDownloader):
# #     """BSE bhavcopy downloader"""
    
# #     def __init__(self, data_dir: Path):
# #         super().__init__(data_dir / "bse")
# #         self.session = requests.Session()
# #         self.session.headers.update({
# #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
# #             'Accept': 'application/json, text/plain, */*',
# #             'Accept-Language': 'en-US,en;q=0.9',
# #             'Referer': 'https://www.bseindia.com/',
# #             'DNT': '1',
# #         })
    
# #     def get_exchange_name(self) -> str:
# #         return "BSE"
    
# #     def download_bhavcopy(self, date: datetime) -> Optional[Path]:
# #         """
# #         Download BSE bhavcopy for a specific date
# #         """
# #         try:
# #             # Get valid trading day
# #             valid_date = get_last_trading_day(date)
            
# #             if valid_date != date:
# #                 logger.info(f"Target date {date.strftime('%Y-%m-%d')} is holiday/weekend. Fetching {valid_date.strftime('%Y-%m-%d')}")
            
# #             # Check if file already exists
# #             date_str = valid_date.strftime("%d%m%Y")
# #             csv_path = self.data_dir / f"EQ{date_str}.csv"
            
# #             if csv_path.exists():
# #                 logger.debug(f"BSE file already exists: {csv_path}")
# #                 return csv_path
            
# #             # Method 1: Try direct download with the working format
# #             logger.debug(f"Downloading BSE bhavcopy for {valid_date.strftime('%Y-%m-%d')}")
            
# #             # Try different URL patterns based on actual working BSE URLs
# #             url_patterns = [
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.zip",
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.zip",
# #                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.csv",
# #             ]
            
# #             for url in url_patterns:
# #                 try:
# #                     response = self.session.get(url, timeout=60, stream=True)
                    
# #                     if response.status_code == 200:
# #                         # Check content type
# #                         content_type = response.headers.get('content-type', '').lower()
                        
# #                         # If it's HTML, it's an error page
# #                         if 'html' in content_type or response.text.startswith('<!DOCTYPE'):
# #                             logger.debug(f"URL {url} returned HTML, skipping")
# #                             continue
                        
# #                         # Save the file
# #                         if 'zip' in content_type or url.endswith('.zip'):
# #                             return self._save_zip_file(response, valid_date)
# #                         else:
# #                             return self._save_csv_file(response, valid_date)
                            
# #                 except Exception as e:
# #                     logger.debug(f"Failed to download from {url}: {e}")
# #                     continue
            
# #             # Method 2: Try BSE API
# #             logger.debug("Trying BSE API...")
# #             try:
# #                 api_url = "https://api.bseindia.com/BseIndiaAPI/api/GetBhavcopydata/w?flag=0"
# #                 api_response = self.session.get(api_url, timeout=30)
                
# #                 if api_response.status_code == 200:
# #                     data = api_response.json()
                    
# #                     # Look for the zip file
# #                     if 'dsZip' in data and data['dsZip']:
# #                         zip_info = data['dsZip'][0]
# #                         filename = zip_info.get('FilePath', '')
                        
# #                         if filename and 'ZIP' in filename.upper():
# #                             download_url = f"https://www.bseindia.com/download/BhavCopy/Equity/{filename}"
# #                             response = self.session.get(download_url, timeout=60)
                            
# #                             if response.status_code == 200:
# #                                 return self._save_zip_file(response, valid_date)
# #             except Exception as e:
# #                 logger.debug(f"BSE API failed: {e}")
            
# #             logger.warning(f"BSE bhavcopy not found for {valid_date.strftime('%Y-%m-%d')}")
# #             return None
            
# #         except Exception as e:
# #             logger.error(f"Error downloading BSE bhavcopy for {date.strftime('%Y-%m-%d')}: {e}")
# #             return None
    
# #     def _save_zip_file(self, response, date: datetime) -> Optional[Path]:
# #         """Save and extract zip file"""
# #         try:
# #             date_str = date.strftime("%d%m%Y")
            
# #             # Save zip
# #             zip_path = self.data_dir / f"EQ{date_str}.zip"
# #             with open(zip_path, 'wb') as f:
# #                 f.write(response.content)
            
# #             # Extract CSV
# #             try:
# #                 with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
# #                     # Find the first CSV file
# #                     csv_files = [f for f in zf.namelist() if f.endswith('.csv') or f.endswith('.CSV')]
                    
# #                     if not csv_files:
# #                         logger.warning(f"No CSV found in BSE zip for {date.strftime('%Y-%m-%d')}")
# #                         return None
                    
# #                     # Use the first CSV found
# #                     csv_filename = csv_files[0]
# #                     csv_path = self.data_dir / csv_filename
                    
# #                     # Extract CSV
# #                     with open(csv_path, 'wb') as f:
# #                         f.write(zf.read(csv_filename))
                    
# #                     logger.debug(f"BSE bhavcopy saved to {csv_path}")
# #                     return csv_path
                    
# #             except zipfile.BadZipFile:
# #                 # Try to read as CSV directly
# #                 csv_path = self.data_dir / f"EQ{date_str}.csv"
# #                 try:
# #                     content = response.content.decode('utf-8')
# #                     with open(csv_path, 'w', encoding='utf-8') as f:
# #                         f.write(content)
# #                     return csv_path
# #                 except:
# #                     return None
                    
# #         except Exception as e:
# #             logger.error(f"Error saving BSE file: {e}")
# #             return None
    
# #     def _save_csv_file(self, response, date: datetime) -> Optional[Path]:
# #         """Save CSV file"""
# #         try:
# #             date_str = date.strftime("%d%m%Y")
# #             csv_path = self.data_dir / f"EQ{date_str}.csv"
            
# #             # Try to decode and save
# #             try:
# #                 content = response.content.decode('utf-8')
# #             except:
# #                 content = response.content.decode('latin-1')
            
# #             with open(csv_path, 'w', encoding='utf-8') as f:
# #                 f.write(content)
            
# #             logger.debug(f"BSE bhavcopy saved to {csv_path}")
# #             return csv_path
            
# #         except Exception as e:
# #             logger.error(f"Error saving CSV: {e}")
# #             return None
    
# #     def parse_bhavcopy(self, file_path: Path) -> pd.DataFrame:
# #         """
# #         Parse BSE bhavcopy CSV
# #         """
# #         try:
# #             # Try different encodings
# #             df = None
# #             for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
# #                 try:
# #                     # Try reading with different parameters
# #                     df = pd.read_csv(
# #                         file_path,
# #                         encoding=encoding,
# #                         skipinitialspace=True,
# #                         on_bad_lines='skip',
# #                         engine='python'
# #                     )
# #                     if not df.empty and len(df.columns) > 1:
# #                         break
# #                 except Exception:
# #                     continue
            
# #             if df is None or df.empty:
# #                 logger.warning(f"Could not parse BSE file {file_path.name}")
# #                 return pd.DataFrame()
            
# #             # Clean column names
# #             df.columns = df.columns.str.strip().str.upper()
            
# #             # Try to identify columns by looking for typical BSE column names
# #             # Map common column names
# #             col_mapping = {}
            
# #             # Common BSE column name patterns
# #             patterns = {
# #                 'SC_CODE': ['SC_CODE', 'CODE', 'SECURITYCODE', 'SC_CD', 'SEC_CODE'],
# #                 'SC_NAME': ['SC_NAME', 'NAME', 'SECURITYNAME', 'SEC_NAME'],
# #                 'OPEN': ['OPEN', 'OPENING', 'OPEN_PRICE'],
# #                 'HIGH': ['HIGH', 'HIGH_PRICE'],
# #                 'LOW': ['LOW', 'LOW_PRICE'],
# #                 'CLOSE': ['CLOSE', 'CLOSING', 'CLOSE_PRICE', 'LAST'],
# #                 'VOLUME': ['NO_OF_SHRS', 'VOLUME', 'SHARES', 'TOTTRDQTY', 'TRADED_QTY'],
# #                 'PREVCLOSE': ['PREVCLOSE', 'PREV_CLOSE', 'PREVIOUS_CLOSE'],
# #                 'ISIN': ['ISIN']
# #             }
            
# #             for target, variants in patterns.items():
# #                 for variant in variants:
# #                     if variant in df.columns:
# #                         col_mapping[target] = variant
# #                         break
            
# #             # If we can't identify columns, try to use position-based mapping
# #             if 'CLOSE' not in col_mapping or ('SC_CODE' not in col_mapping and 'SC_NAME' not in col_mapping):
# #                 logger.debug(f"Using position-based mapping for {file_path.name}")
                
# #                 # If we have exactly the right number of columns, map by position
# #                 if len(df.columns) >= 7:
# #                     # Typical BSE column order: SC_CODE, SC_NAME, SC_GROUP, SC_TYPE, OPEN, HIGH, LOW, CLOSE, ...
# #                     col_mapping = {
# #                         'SC_CODE': df.columns[0],
# #                         'SC_NAME': df.columns[1],
# #                         'OPEN': df.columns[4] if len(df.columns) > 4 else df.columns[0],
# #                         'HIGH': df.columns[5] if len(df.columns) > 5 else df.columns[0],
# #                         'LOW': df.columns[6] if len(df.columns) > 6 else df.columns[0],
# #                         'CLOSE': df.columns[7] if len(df.columns) > 7 else df.columns[0],
# #                     }
# #                     if len(df.columns) > 8:
# #                         col_mapping['VOLUME'] = df.columns[8]
            
# #             # Build result
# #             result = pd.DataFrame()
            
# #             # Date from filename or use today
# #             try:
# #                 # Try to extract date from filename
# #                 date_str = file_path.stem
# #                 # Remove common prefixes
# #                 for prefix in ['EQ', 'BSE_EQ_BHAVCOPY_', 'BHAVCOPY_']:
# #                     if date_str.startswith(prefix):
# #                         date_str = date_str[len(prefix):]
# #                 # Remove common suffixes
# #                 for suffix in ['_CSV', '_ZIP']:
# #                     if date_str.endswith(suffix):
# #                         date_str = date_str[:-len(suffix)]
                
# #                 # Try to parse date
# #                 for fmt in ['%d%m%Y', '%d%m%y', '%Y%m%d']:
# #                     try:
# #                         result['date'] = pd.to_datetime(date_str[:8], format=fmt)
# #                         break
# #                     except:
# #                         continue
# #                 else:
# #                     result['date'] = pd.Timestamp.now().normalize()
# #             except:
# #                 result['date'] = pd.Timestamp.now().normalize()
            
# #             result['exchange'] = 'BSE'
            
# #             # Symbol/Name
# #             if 'SC_NAME' in col_mapping:
# #                 result['symbol'] = df[col_mapping['SC_NAME']].astype(str).str.strip()
# #             else:
# #                 # Use code as symbol if name not available
# #                 if 'SC_CODE' in col_mapping:
# #                     result['symbol'] = df[col_mapping['SC_CODE']].astype(str).str.strip()
# #                 else:
# #                     result['symbol'] = df.iloc[:, 0].astype(str).str.strip()
            
# #             # Security ID
# #             if 'SC_CODE' in col_mapping:
# #                 result['security_id'] = df[col_mapping['SC_CODE']].astype(str).str.strip()
# #             else:
# #                 result['security_id'] = result['symbol']
            
# #             # Prices
# #             for field in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
# #                 col_name = col_mapping.get(field)
# #                 if col_name and col_name in df.columns:
# #                     result[field.lower()] = pd.to_numeric(df[col_name], errors='coerce')
# #                 else:
# #                     result[field.lower()] = 0.0
            
# #             # Volume
# #             if 'VOLUME' in col_mapping:
# #                 result['volume'] = pd.to_numeric(df[col_mapping['VOLUME']], errors='coerce').fillna(0).astype(int)
# #             else:
# #                 result['volume'] = 0
            
# #             # Previous close
# #             if 'PREVCLOSE' in col_mapping:
# #                 result['previous_close'] = pd.to_numeric(df[col_mapping['PREVCLOSE']], errors='coerce')
# #             else:
# #                 result['previous_close'] = None
            
# #             # ISIN
# #             if 'ISIN' in col_mapping:
# #                 result['isin'] = df[col_mapping['ISIN']].astype(str).str.strip()
# #             else:
# #                 result['isin'] = ''
            
# #             # Clean data - remove rows with invalid close price
# #             result = result[result['close'].notna()]
# #             result = result[result['close'] > 0]
            
# #             # Remove duplicates
# #             result = result.drop_duplicates(subset=['symbol'], keep='first')
            
# #             logger.debug(f"Parsed {len(result)} BSE securities from {file_path.name}")
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"Error parsing BSE bhavcopy {file_path}: {e}")
# #             return pd.DataFrame()

# # src/market_data/bse.py

# """
# BSE Bhavcopy downloader and parser
# """
# import requests
# import pandas as pd
# from datetime import datetime, timedelta
# from pathlib import Path
# from typing import Optional
# from loguru import logger
# import zipfile
# import io
# import time
# import json
# from .base import MarketDataDownloader
# from .holidays import get_last_trading_day


# class BSEDownloader(MarketDataDownloader):
#     """BSE bhavcopy downloader"""
    
#     def __init__(self, data_dir: Path):
#         super().__init__(data_dir / "bse")
#         self.session = requests.Session()
#         self.session.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
#             'Accept': 'application/json, text/plain, */*',
#             'Accept-Language': 'en-US,en;q=0.9',
#             'Referer': 'https://www.bseindia.com/',
#             'DNT': '1',
#         })
    
#     def get_exchange_name(self) -> str:
#         return "BSE"
    
#     def _validate_bse_file(self, file_path: Path) -> bool:
#         """
#         Validate if the BSE file is a valid CSV with data
        
#         Args:
#             file_path: Path to the file
            
#         Returns:
#             True if valid, False otherwise
#         """
#         try:
#             # Check file size - if too small, it's likely an error page
#             if file_path.stat().st_size < 1000:  # Less than 1KB is suspicious
#                 logger.debug(f"File too small: {file_path.name} ({file_path.stat().st_size} bytes)")
#                 return False
            
#             # Try to read first few lines
#             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                 first_lines = [f.readline() for _ in range(5)]
            
#             # Check if it's HTML (error page)
#             for line in first_lines:
#                 if '<html' in line.lower() or '<!DOCTYPE' in line.upper():
#                     logger.debug(f"File appears to be HTML (error page): {file_path.name}")
#                     return False
            
#             # Try to parse as CSV
#             try:
#                 df = pd.read_csv(file_path, nrows=5, on_bad_lines='skip')
#                 # Check if we have any data columns
#                 if len(df.columns) > 1 and len(df) > 0:
#                     return True
#                 else:
#                     logger.debug(f"File has no valid CSV structure: {file_path.name}")
#                     return False
#             except Exception:
#                 return False
                
#         except Exception as e:
#             logger.debug(f"Validation failed for {file_path.name}: {e}")
#             return False
    
#     def download_bhavcopy(self, date: datetime, force: bool = False) -> Optional[Path]:
#         """
#         Download BSE bhavcopy for a specific date
        
#         Args:
#             date: Date to download
#             force: If True, re-download even if file exists
#         """
#         try:
#             # Get valid trading day
#             valid_date = get_last_trading_day(date)
            
#             if valid_date != date:
#                 logger.info(f"Target date {date.strftime('%Y-%m-%d')} is holiday/weekend. Fetching {valid_date.strftime('%Y-%m-%d')}")
            
#             # Check if file already exists and is valid
#             date_str = valid_date.strftime("%d%m%Y")
#             csv_path = self.data_dir / f"EQ{date_str}.csv"
            
#             if csv_path.exists() and not force:
#                 if self._validate_bse_file(csv_path):
#                     logger.debug(f"BSE file already exists and is valid: {csv_path}")
#                     return csv_path
#                 else:
#                     logger.warning(f"Existing BSE file is corrupt, re-downloading: {csv_path.name}")
#                     # Delete corrupt file
#                     csv_path.unlink()
            
#             # Try different URL patterns
#             logger.debug(f"Downloading BSE bhavcopy for {valid_date.strftime('%Y-%m-%d')}")
            
#             # Correct BSE URL patterns (updated with working URLs)
#             url_patterns = [
#                 # Primary BSE download URL
#                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.zip",
#                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.zip",
#                 # Alternative patterns
#                 f"https://www.bseindia.com/download/BhavCopy/Equity/{date_str}.zip",
#                 f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.csv",
#             ]
            
#             for url in url_patterns:
#                 try:
#                     logger.debug(f"Trying URL: {url}")
#                     response = self.session.get(url, timeout=60, stream=True)
                    
#                     if response.status_code == 200:
#                         # Check content type
#                         content_type = response.headers.get('content-type', '').lower()
#                         content_length = response.headers.get('content-length', '0')
                        
#                         # If content is too small, it's likely an error
#                         if content_length and int(content_length) < 1000:
#                             logger.debug(f"Content too small ({content_length} bytes), skipping")
#                             continue
                        
#                         # Check first few bytes to detect HTML
#                         first_bytes = response.content[:100]
#                         if b'<html' in first_bytes.lower() or b'<!DOCTYPE' in first_bytes:
#                             logger.debug(f"URL {url} returned HTML, skipping")
#                             continue
                        
#                         # Save the file
#                         if 'zip' in content_type or url.endswith('.zip'):
#                             file_path = self._save_zip_file(response, valid_date)
#                         else:
#                             file_path = self._save_csv_file(response, valid_date)
                        
#                         # Validate the downloaded file
#                         if file_path and self._validate_bse_file(file_path):
#                             logger.debug(f"Successfully downloaded valid BSE file: {file_path.name}")
#                             return file_path
#                         elif file_path:
#                             logger.warning(f"Downloaded file is invalid, removing: {file_path.name}")
#                             file_path.unlink()
                            
#                 except Exception as e:
#                     logger.debug(f"Failed to download from {url}: {e}")
#                     continue
            
#             # Method 2: Try BSE API to get the correct file name
#             logger.debug("Trying BSE API...")
#             try:
#                 api_url = "https://api.bseindia.com/BseIndiaAPI/api/GetBhavcopydata/w?flag=0"
#                 api_response = self.session.get(api_url, timeout=30)
                
#                 if api_response.status_code == 200:
#                     data = api_response.json()
                    
#                     # Look for the zip file in dsEqnew (new format)
#                     zip_files = []
                    
#                     if 'dsEqnew' in data:
#                         for item in data['dsEqnew']:
#                             if 'FilePath' in item and 'ZIP' in item['FilePath'].upper():
#                                 zip_files.append(item)
                    
#                     # Also check dsZip (old format)
#                     if 'dsZip' in data:
#                         for item in data['dsZip']:
#                             if 'FilePath' in item and 'ZIP' in item['FilePath'].upper():
#                                 zip_files.append(item)
                    
#                     # Also check DSAddEqDeri (another format)
#                     if 'DSAddEqDeri' in data:
#                         for item in data['DSAddEqDeri']:
#                             if 'BhavCopyFileName' in item:
#                                 filename = item['BhavCopyFileName']
#                                 if '.csv' in filename.lower():
#                                     zip_files.append({'FilePath': filename})
                    
#                     for zip_info in zip_files:
#                         filename = zip_info.get('FilePath', '')
#                         if filename:
#                             download_url = f"https://www.bseindia.com/download/BhavCopy/Equity/{filename}"
#                             logger.debug(f"Downloading from API: {download_url}")
                            
#                             response = self.session.get(download_url, timeout=60)
                            
#                             if response.status_code == 200:
#                                 if filename.endswith('.zip') or filename.endswith('.ZIP'):
#                                     file_path = self._save_zip_file(response, valid_date)
#                                 else:
#                                     file_path = self._save_csv_file(response, valid_date)
                                
#                                 if file_path and self._validate_bse_file(file_path):
#                                     return file_path
                                    
#             except Exception as e:
#                 logger.debug(f"BSE API failed: {e}")
            
#             # Method 3: Try direct BSE data portal
#             try:
#                 # Try the new BSE data portal URL
#                 portal_url = f"https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx?flag=0"
#                 logger.debug(f"Trying BSE portal: {portal_url}")
                
#                 # This might redirect to the actual file
#                 response = self.session.get(portal_url, timeout=30)
                
#                 # Look for the actual download link in the response
#                 if response.status_code == 200 and 'href' in response.text:
#                     import re
#                     # Find zip file links
#                     zip_links = re.findall(r'href=[\'"]?([^\'" >]+\.zip)', response.text, re.IGNORECASE)
#                     for link in zip_links:
#                         if 'EQ' in link and date_str in link:
#                             download_url = f"https://www.bseindia.com/{link}"
#                             response = self.session.get(download_url, timeout=60)
#                             if response.status_code == 200:
#                                 file_path = self._save_zip_file(response, valid_date)
#                                 if file_path and self._validate_bse_file(file_path):
#                                     return file_path
#             except Exception as e:
#                 logger.debug(f"BSE portal method failed: {e}")
            
#             logger.warning(f"BSE bhavcopy not found for {valid_date.strftime('%Y-%m-%d')} after trying all methods")
#             return None
            
#         except Exception as e:
#             logger.error(f"Error downloading BSE bhavcopy for {date.strftime('%Y-%m-%d')}: {e}")
#             return None
    
#     def _save_zip_file(self, response, date: datetime) -> Optional[Path]:
#         """Save and extract zip file"""
#         try:
#             date_str = date.strftime("%d%m%Y")
            
#             # Save zip
#             zip_path = self.data_dir / f"EQ{date_str}.zip"
#             with open(zip_path, 'wb') as f:
#                 f.write(response.content)
            
#             # Extract CSV
#             try:
#                 with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
#                     # Find the first CSV file
#                     csv_files = [f for f in zf.namelist() if f.endswith('.csv') or f.endswith('.CSV')]
                    
#                     if not csv_files:
#                         logger.warning(f"No CSV found in BSE zip for {date.strftime('%Y-%m-%d')}")
#                         return None
                    
#                     # Use the first CSV found
#                     csv_filename = csv_files[0]
#                     csv_path = self.data_dir / csv_filename
                    
#                     # Extract CSV
#                     with open(csv_path, 'wb') as f:
#                         f.write(zf.read(csv_filename))
                    
#                     logger.debug(f"BSE bhavcopy saved to {csv_path}")
#                     return csv_path
                    
#             except zipfile.BadZipFile:
#                 # Try to read as CSV directly
#                 csv_path = self.data_dir / f"EQ{date_str}.csv"
#                 try:
#                     content = response.content.decode('utf-8')
#                     with open(csv_path, 'w', encoding='utf-8') as f:
#                         f.write(content)
#                     return csv_path
#                 except:
#                     return None
                    
#         except Exception as e:
#             logger.error(f"Error saving BSE file: {e}")
#             return None
    
#     def _save_csv_file(self, response, date: datetime) -> Optional[Path]:
#         """Save CSV file"""
#         try:
#             date_str = date.strftime("%d%m%Y")
#             csv_path = self.data_dir / f"EQ{date_str}.csv"
            
#             # Try to decode and save
#             try:
#                 content = response.content.decode('utf-8')
#             except:
#                 content = response.content.decode('latin-1')
            
#             with open(csv_path, 'w', encoding='utf-8') as f:
#                 f.write(content)
            
#             logger.debug(f"BSE bhavcopy saved to {csv_path}")
#             return csv_path
            
#         except Exception as e:
#             logger.error(f"Error saving CSV: {e}")
#             return None
    
#     def parse_bhavcopy(self, file_path: Path) -> pd.DataFrame:
#         """
#         Parse BSE bhavcopy CSV
#         """
#         try:
#             # First validate the file
#             if not self._validate_bse_file(file_path):
#                 logger.warning(f"Invalid BSE file: {file_path.name}")
#                 return pd.DataFrame()
            
#             # Try different encodings
#             df = None
#             for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
#                 try:
#                     # Try reading with different parameters
#                     df = pd.read_csv(
#                         file_path,
#                         encoding=encoding,
#                         skipinitialspace=True,
#                         on_bad_lines='skip',
#                         engine='python'
#                     )
#                     if not df.empty and len(df.columns) > 1:
#                         break
#                 except Exception:
#                     continue
            
#             if df is None or df.empty:
#                 logger.warning(f"Could not parse BSE file {file_path.name}")
#                 return pd.DataFrame()
            
#             # Clean column names
#             df.columns = df.columns.str.strip().str.upper()
            
#             # Try to identify columns by looking for typical BSE column names
#             col_mapping = {}
            
#             # Common BSE column name patterns
#             patterns = {
#                 'SC_CODE': ['SC_CODE', 'CODE', 'SECURITYCODE', 'SC_CD', 'SEC_CODE'],
#                 'SC_NAME': ['SC_NAME', 'NAME', 'SECURITYNAME', 'SEC_NAME'],
#                 'OPEN': ['OPEN', 'OPENING', 'OPEN_PRICE'],
#                 'HIGH': ['HIGH', 'HIGH_PRICE'],
#                 'LOW': ['LOW', 'LOW_PRICE'],
#                 'CLOSE': ['CLOSE', 'CLOSING', 'CLOSE_PRICE', 'LAST'],
#                 'VOLUME': ['NO_OF_SHRS', 'VOLUME', 'SHARES', 'TOTTRDQTY', 'TRADED_QTY'],
#                 'PREVCLOSE': ['PREVCLOSE', 'PREV_CLOSE', 'PREVIOUS_CLOSE'],
#                 'ISIN': ['ISIN']
#             }
            
#             for target, variants in patterns.items():
#                 for variant in variants:
#                     if variant in df.columns:
#                         col_mapping[target] = variant
#                         break
            
#             # If we can't identify columns, try to use position-based mapping
#             if 'CLOSE' not in col_mapping or ('SC_CODE' not in col_mapping and 'SC_NAME' not in col_mapping):
#                 logger.debug(f"Using position-based mapping for {file_path.name}")
                
#                 # If we have exactly the right number of columns, map by position
#                 if len(df.columns) >= 7:
#                     # Typical BSE column order: SC_CODE, SC_NAME, SC_GROUP, SC_TYPE, OPEN, HIGH, LOW, CLOSE, ...
#                     col_mapping = {
#                         'SC_CODE': df.columns[0],
#                         'SC_NAME': df.columns[1],
#                         'OPEN': df.columns[4] if len(df.columns) > 4 else df.columns[0],
#                         'HIGH': df.columns[5] if len(df.columns) > 5 else df.columns[0],
#                         'LOW': df.columns[6] if len(df.columns) > 6 else df.columns[0],
#                         'CLOSE': df.columns[7] if len(df.columns) > 7 else df.columns[0],
#                     }
#                     if len(df.columns) > 8:
#                         col_mapping['VOLUME'] = df.columns[8]
            
#             # Build result
#             result = pd.DataFrame()
            
#             # Date from filename or use today
#             try:
#                 # Try to extract date from filename
#                 date_str = file_path.stem
#                 # Remove common prefixes
#                 for prefix in ['EQ', 'BSE_EQ_BHAVCOPY_', 'BHAVCOPY_']:
#                     if date_str.startswith(prefix):
#                         date_str = date_str[len(prefix):]
#                 # Remove common suffixes
#                 for suffix in ['_CSV', '_ZIP']:
#                     if date_str.endswith(suffix):
#                         date_str = date_str[:-len(suffix)]
                
#                 # Try to parse date
#                 for fmt in ['%d%m%Y', '%d%m%y', '%Y%m%d']:
#                     try:
#                         result['date'] = pd.to_datetime(date_str[:8], format=fmt)
#                         break
#                     except:
#                         continue
#                 else:
#                     result['date'] = pd.Timestamp.now().normalize()
#             except:
#                 result['date'] = pd.Timestamp.now().normalize()
            
#             result['exchange'] = 'BSE'
            
#             # Symbol/Name
#             if 'SC_NAME' in col_mapping:
#                 result['symbol'] = df[col_mapping['SC_NAME']].astype(str).str.strip()
#             else:
#                 # Use code as symbol if name not available
#                 if 'SC_CODE' in col_mapping:
#                     result['symbol'] = df[col_mapping['SC_CODE']].astype(str).str.strip()
#                 else:
#                     result['symbol'] = df.iloc[:, 0].astype(str).str.strip()
            
#             # Security ID
#             if 'SC_CODE' in col_mapping:
#                 result['security_id'] = df[col_mapping['SC_CODE']].astype(str).str.strip()
#             else:
#                 result['security_id'] = result['symbol']
            
#             # Prices
#             for field in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
#                 col_name = col_mapping.get(field)
#                 if col_name and col_name in df.columns:
#                     result[field.lower()] = pd.to_numeric(df[col_name], errors='coerce')
#                 else:
#                     result[field.lower()] = 0.0
            
#             # Volume
#             if 'VOLUME' in col_mapping:
#                 result['volume'] = pd.to_numeric(df[col_mapping['VOLUME']], errors='coerce').fillna(0).astype(int)
#             else:
#                 result['volume'] = 0
            
#             # Previous close
#             if 'PREVCLOSE' in col_mapping:
#                 result['previous_close'] = pd.to_numeric(df[col_mapping['PREVCLOSE']], errors='coerce')
#             else:
#                 result['previous_close'] = None
            
#             # ISIN
#             if 'ISIN' in col_mapping:
#                 result['isin'] = df[col_mapping['ISIN']].astype(str).str.strip()
#             else:
#                 result['isin'] = ''
            
#             # Clean data - remove rows with invalid close price
#             result = result[result['close'].notna()]
#             result = result[result['close'] > 0]
            
#             # Remove duplicates
#             result = result.drop_duplicates(subset=['symbol'], keep='first')
            
#             logger.debug(f"Parsed {len(result)} BSE securities from {file_path.name}")
#             return result
            
#         except Exception as e:
#             logger.error(f"Error parsing BSE bhavcopy {file_path}: {e}")
#             return pd.DataFrame()

# src/market_data/bse.py

"""
BSE Bhavcopy downloader and parser
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
import json
import re
from .base import MarketDataDownloader
from .holidays import get_last_trading_day


class BSEDownloader(MarketDataDownloader):
    """BSE bhavcopy downloader"""
    
    def __init__(self, data_dir: Path):
        super().__init__(data_dir / "bse")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.bseindia.com/',
            'DNT': '1',
        })
    
    def get_exchange_name(self) -> str:
        return "BSE"
    
    def _validate_bse_file(self, file_path: Path) -> bool:
        """
        Validate if the BSE file is a valid CSV with data
        """
        try:
            if not file_path.exists():
                return False
                
            # Check file size
            if file_path.stat().st_size < 1000:
                logger.debug(f"File too small: {file_path.name} ({file_path.stat().st_size} bytes)")
                return False
            
            # Try to read first few lines
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline() for _ in range(5)]
            
            # Check if it's HTML (error page)
            for line in first_lines:
                if '<html' in line.lower() or '<!DOCTYPE' in line.upper():
                    logger.debug(f"File appears to be HTML: {file_path.name}")
                    return False
            
            # Try to parse as CSV
            try:
                df = pd.read_csv(file_path, nrows=5, on_bad_lines='skip')
                if len(df.columns) > 1 and len(df) > 0:
                    # Check if it has typical BSE columns
                    columns_upper = [col.upper() for col in df.columns]
                    expected_cols = ['SC_CODE', 'SC_NAME', 'CLOSE', 'OPEN', 'HIGH', 'LOW']
                    found_cols = [col for col in expected_cols if any(col in c for c in columns_upper)]
                    if len(found_cols) >= 2:  # At least have code/name and close
                        return True
                    else:
                        logger.debug(f"File missing expected BSE columns: {found_cols}")
                        return False
                else:
                    return False
            except Exception as e:
                logger.debug(f"CSV parse failed: {e}")
                return False
                
        except Exception as e:
            logger.debug(f"Validation failed for {file_path.name}: {e}")
            return False
    
    def download_bhavcopy(self, date: datetime, force: bool = False) -> Optional[Path]:
        """
        Download BSE bhavcopy for a specific date
        """
        try:
            # Get valid trading day
            valid_date = get_last_trading_day(date)
            
            if valid_date != date:
                logger.info(f"Target date {date.strftime('%Y-%m-%d')} is holiday/weekend. Fetching {valid_date.strftime('%Y-%m-%d')}")
            
            # Check if file already exists and is valid
            date_str = valid_date.strftime("%d%m%Y")
            csv_path = self.data_dir / f"EQ{date_str}.csv"
            
            if csv_path.exists() and not force:
                if self._validate_bse_file(csv_path):
                    logger.debug(f"BSE file already exists and is valid: {csv_path}")
                    return csv_path
                else:
                    logger.warning(f"Existing BSE file is corrupt, re-downloading: {csv_path.name}")
                    csv_path.unlink()
            
            # Try BSE API first to get the correct file name
            logger.debug(f"Downloading BSE bhavcopy for {valid_date.strftime('%Y-%m-%d')}")
            
            # Method 1: Get file info from API
            try:
                api_url = "https://api.bseindia.com/BseIndiaAPI/api/GetBhavcopydata/w?flag=0"
                api_response = self.session.get(api_url, timeout=30)
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    
                    # Look for the equity zip file
                    zip_filename = None
                    
                    # Check dsEqnew (new format)
                    if 'dsEqnew' in data:
                        for item in data['dsEqnew']:
                            if 'FilePath' in item and 'ZIP' in item['FilePath'].upper():
                                if 'EQ' in item['FilePath'].upper() and 'BHAVCOPY' in item['FilePath'].upper():
                                    zip_filename = item['FilePath']
                                    break
                    
                    # If not found, check dsZip (old format)
                    if not zip_filename and 'dsZip' in data:
                        for item in data['dsZip']:
                            if 'FilePath' in item and 'ZIP' in item['FilePath'].upper():
                                if 'EQ' in item['FilePath'].upper():
                                    zip_filename = item['FilePath']
                                    break
                    
                    if zip_filename:
                        download_url = f"https://www.bseindia.com/download/BhavCopy/Equity/{zip_filename}"
                        logger.debug(f"Downloading from API: {download_url}")
                        
                        response = self.session.get(download_url, timeout=60)
                        
                        if response.status_code == 200:
                            return self._save_and_extract_zip(response, valid_date, zip_filename)
                            
            except Exception as e:
                logger.debug(f"BSE API method failed: {e}")
            
            # Method 2: Try direct download with known patterns
            url_patterns = [
                f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.zip",
                f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}.zip",
                f"https://www.bseindia.com/download/BhavCopy/Equity/{date_str}.zip",
            ]
            
            for url in url_patterns:
                try:
                    logger.debug(f"Trying URL: {url}")
                    response = self.session.get(url, timeout=60, stream=True)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        
                        # Check for HTML
                        first_bytes = response.content[:200]
                        if b'<html' in first_bytes.lower() or b'<!DOCTYPE' in first_bytes:
                            logger.debug(f"URL returned HTML, skipping")
                            continue
                        
                        if 'zip' in content_type or url.endswith('.zip'):
                            # Try to extract filename from URL
                            filename = url.split('/')[-1]
                            return self._save_and_extract_zip(response, valid_date, filename)
                            
                except Exception as e:
                    logger.debug(f"Failed to download from {url}: {e}")
                    continue
            
            logger.warning(f"BSE bhavcopy not found for {valid_date.strftime('%Y-%m-%d')}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading BSE bhavcopy for {date.strftime('%Y-%m-%d')}: {e}")
            return None
    
    def _save_and_extract_zip(self, response, date: datetime, zip_filename: str) -> Optional[Path]:
        """
        Save and extract zip file, returning the path to the extracted CSV
        """
        try:
            date_str = date.strftime("%d%m%Y")
            
            # Save zip file with original name
            zip_path = self.data_dir / zip_filename
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            logger.debug(f"Saved zip: {zip_path}")
            
            # Extract CSV
            try:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                    # Find CSV files in the zip
                    csv_files = [f for f in zf.namelist() if f.lower().endswith('.csv')]
                    
                    if not csv_files:
                        logger.warning(f"No CSV found in zip: {zip_filename}")
                        return None
                    
                    # Get the first CSV file
                    csv_filename = csv_files[0]
                    
                    # Extract CSV content
                    csv_content = zf.read(csv_filename)
                    
                    # Save as EQ{date}.csv
                    csv_path = self.data_dir / f"EQ{date_str}.csv"
                    with open(csv_path, 'wb') as f:
                        f.write(csv_content)
                    
                    logger.debug(f"Extracted CSV to: {csv_path}")
                    
                    # Validate the extracted file
                    if self._validate_bse_file(csv_path):
                        logger.debug(f"Successfully extracted valid BSE CSV: {csv_path.name}")
                        return csv_path
                    else:
                        logger.warning(f"Extracted CSV is invalid: {csv_path.name}")
                        csv_path.unlink()
                        return None
                    
            except zipfile.BadZipFile:
                logger.error(f"Bad zip file: {zip_filename}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting zip: {e}")
            return None
    
    def parse_bhavcopy(self, file_path: Path) -> pd.DataFrame:
        """
        Parse BSE bhavcopy CSV
        """
        try:
            # First validate the file
            if not self._validate_bse_file(file_path):
                logger.warning(f"Invalid BSE file: {file_path.name}")
                return pd.DataFrame()
            
            # Try different encodings
            df = None
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        skipinitialspace=True,
                        on_bad_lines='skip',
                        engine='python'
                    )
                    if not df.empty and len(df.columns) > 1:
                        break
                except Exception:
                    continue
            
            if df is None or df.empty:
                logger.warning(f"Could not parse BSE file {file_path.name}")
                return pd.DataFrame()
            
            # Clean column names
            df.columns = df.columns.str.strip().str.upper()
            
            # Map columns
            col_mapping = {}
            
            # Common BSE column names
            patterns = {
                'SC_CODE': ['SC_CODE', 'CODE', 'SECURITYCODE', 'SC_CD', 'SEC_CODE'],
                'SC_NAME': ['SC_NAME', 'NAME', 'SECURITYNAME', 'SEC_NAME'],
                'OPEN': ['OPEN', 'OPENING', 'OPEN_PRICE'],
                'HIGH': ['HIGH', 'HIGH_PRICE'],
                'LOW': ['LOW', 'LOW_PRICE'],
                'CLOSE': ['CLOSE', 'CLOSING', 'CLOSE_PRICE', 'LAST'],
                'VOLUME': ['NO_OF_SHRS', 'VOLUME', 'SHARES', 'TOTTRDQTY', 'TRADED_QTY'],
                'PREVCLOSE': ['PREVCLOSE', 'PREV_CLOSE', 'PREVIOUS_CLOSE'],
                'ISIN': ['ISIN']
            }
            
            for target, variants in patterns.items():
                for variant in variants:
                    if variant in df.columns:
                        col_mapping[target] = variant
                        break
            
            # If we can't identify columns, use position-based mapping
            if 'CLOSE' not in col_mapping or ('SC_CODE' not in col_mapping and 'SC_NAME' not in col_mapping):
                logger.debug(f"Using position-based mapping for {file_path.name}")
                
                if len(df.columns) >= 7:
                    col_mapping = {
                        'SC_CODE': df.columns[0],
                        'SC_NAME': df.columns[1],
                        'OPEN': df.columns[4] if len(df.columns) > 4 else df.columns[0],
                        'HIGH': df.columns[5] if len(df.columns) > 5 else df.columns[0],
                        'LOW': df.columns[6] if len(df.columns) > 6 else df.columns[0],
                        'CLOSE': df.columns[7] if len(df.columns) > 7 else df.columns[0],
                    }
                    if len(df.columns) > 8:
                        col_mapping['VOLUME'] = df.columns[8]
            
            # Build result
            result = pd.DataFrame()
            
            # Date from filename
            try:
                date_str = file_path.stem
                # Remove common prefixes
                for prefix in ['EQ', 'BSE_EQ_BHAVCOPY_', 'BHAVCOPY_']:
                    if date_str.startswith(prefix):
                        date_str = date_str[len(prefix):]
                # Remove common suffixes
                for suffix in ['_CSV', '_ZIP']:
                    if date_str.endswith(suffix):
                        date_str = date_str[:-len(suffix)]
                
                # Try to parse date
                for fmt in ['%d%m%Y', '%d%m%y', '%Y%m%d']:
                    try:
                        result['date'] = pd.to_datetime(date_str[:8], format=fmt)
                        break
                    except:
                        continue
                else:
                    result['date'] = pd.Timestamp.now().normalize()
            except:
                result['date'] = pd.Timestamp.now().normalize()
            
            result['exchange'] = 'BSE'
            
            # Symbol
            if 'SC_NAME' in col_mapping:
                result['symbol'] = df[col_mapping['SC_NAME']].astype(str).str.strip()
            elif 'SC_CODE' in col_mapping:
                result['symbol'] = df[col_mapping['SC_CODE']].astype(str).str.strip()
            else:
                result['symbol'] = df.iloc[:, 0].astype(str).str.strip()
            
            # Security ID
            if 'SC_CODE' in col_mapping:
                result['security_id'] = df[col_mapping['SC_CODE']].astype(str).str.strip()
            else:
                result['security_id'] = result['symbol']
            
            # Prices
            for field in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
                col_name = col_mapping.get(field)
                if col_name and col_name in df.columns:
                    result[field.lower()] = pd.to_numeric(df[col_name], errors='coerce')
                else:
                    result[field.lower()] = 0.0
            
            # Volume
            if 'VOLUME' in col_mapping:
                result['volume'] = pd.to_numeric(df[col_mapping['VOLUME']], errors='coerce').fillna(0).astype(int)
            else:
                result['volume'] = 0
            
            # Previous close
            if 'PREVCLOSE' in col_mapping:
                result['previous_close'] = pd.to_numeric(df[col_mapping['PREVCLOSE']], errors='coerce')
            else:
                result['previous_close'] = None
            
            # ISIN
            if 'ISIN' in col_mapping:
                result['isin'] = df[col_mapping['ISIN']].astype(str).str.strip()
            else:
                result['isin'] = ''
            
            # Clean data
            result = result[result['close'].notna()]
            result = result[result['close'] > 0]
            
            # Remove duplicates
            result = result.drop_duplicates(subset=['symbol'], keep='first')
            
            logger.debug(f"Parsed {len(result)} BSE securities from {file_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing BSE bhavcopy {file_path}: {e}")
            return pd.DataFrame()