# # # # # # # monitor_leap_ipo.py - Updated with better parsing

# # # # # # """
# # # # # # Real-time monitor for LEAP IPO subscription data from NSE API
# # # # # # """
# # # # # # import sys
# # # # # # import json
# # # # # # import time
# # # # # # import csv
# # # # # # import requests
# # # # # # from pathlib import Path
# # # # # # from datetime import datetime
# # # # # # from loguru import logger
# # # # # # import pandas as pd
# # # # # # from typing import Optional, Dict, Any

# # # # # # # Add src to path
# # # # # # sys.path.insert(0, str(Path(__file__).parent))

# # # # # # from src.config import DATA_DIR
# # # # # # from src.utils import setup_logger


# # # # # # class LEAPIPOMonitor:
# # # # # #     """Real-time monitor for LEAP IPO subscription data"""
    
# # # # # #     # NSE API endpoint
# # # # # #     API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
# # # # # #     # Headers to mimic browser
# # # # # #     HEADERS = {
# # # # # #         'accept': '*/*',
# # # # # #         'accept-language': 'en-US,en;q=0.9',
# # # # # #         'dnt': '1',
# # # # # #         'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
# # # # # #         'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
# # # # # #         'sec-ch-ua-mobile': '?0',
# # # # # #         'sec-ch-ua-platform': '"Windows"',
# # # # # #         'sec-fetch-dest': 'empty',
# # # # # #         'sec-fetch-mode': 'cors',
# # # # # #         'sec-fetch-site': 'same-origin',
# # # # # #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
# # # # # #     }
    
# # # # # #     def __init__(self, output_dir: Path = None, interval_seconds: int = 300):
# # # # # #         """
# # # # # #         Initialize the monitor
        
# # # # # #         Args:
# # # # # #             output_dir: Directory to save CSV files
# # # # # #             interval_seconds: Refresh interval in seconds (default: 300 = 5 minutes)
# # # # # #         """
# # # # # #         self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
# # # # # #         self.output_dir.mkdir(parents=True, exist_ok=True)
# # # # # #         self.interval_seconds = interval_seconds
# # # # # #         self.session = requests.Session()
# # # # # #         self.session.headers.update(self.HEADERS)
        
# # # # # #         # CSV file path
# # # # # #         self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
# # # # # #         # Initialize CSV with headers if it doesn't exist
# # # # # #         self._initialize_csv()
        
# # # # # #         logger.info(f"LEAP IPO Monitor initialized")
# # # # # #         logger.info(f"CSV file: {self.csv_path}")
# # # # # #         logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
# # # # # #     def _initialize_csv(self):
# # # # # #         """Initialize CSV file with headers"""
# # # # # #         headers = [
# # # # # #             'timestamp',
# # # # # #             'datetime',
# # # # # #             'category',
# # # # # #             'no_of_share_offered',
# # # # # #             'no_of_shares_bid',
# # # # # #             'subscription_times',
# # # # # #             'total_no_of_share_offered',
# # # # # #             'total_no_of_shares_bid',
# # # # # #             'total_subscription_times',
# # # # # #             'api_response_raw'
# # # # # #         ]
        
# # # # # #         if not self.csv_path.exists():
# # # # # #             with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
# # # # # #                 writer = csv.writer(f)
# # # # # #                 writer.writerow(headers)
# # # # # #             logger.debug(f"Created CSV file: {self.csv_path}")
    
# # # # # #     def _init_session(self):
# # # # # #         """Initialize session with NSE to get cookies"""
# # # # # #         try:
# # # # # #             # First visit main page
# # # # # #             self.session.get("https://www.nseindia.com", timeout=30)
# # # # # #             logger.debug("Session initialized with NSE")
# # # # # #         except Exception as e:
# # # # # #             logger.warning(f"Failed to initialize session: {e}")
    
# # # # # #     def fetch_data(self) -> Optional[Dict[str, Any]]:
# # # # # #         """
# # # # # #         Fetch LEAP IPO data from NSE API
        
# # # # # #         Returns:
# # # # # #             Dictionary with extracted data or None if failed
# # # # # #         """
# # # # # #         try:
# # # # # #             logger.debug("Fetching LEAP IPO data...")
            
# # # # # #             # Get data from API
# # # # # #             response = self.session.get(
# # # # # #                 self.API_URL,
# # # # # #                 timeout=30
# # # # # #             )
            
# # # # # #             if response.status_code != 200:
# # # # # #                 logger.error(f"API returned status {response.status_code}")
# # # # # #                 logger.debug(f"Response: {response.text[:200]}")
# # # # # #                 return None
            
# # # # # #             data = response.json()
            
# # # # # #             # Debug: Print the structure
# # # # # #             logger.debug(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
# # # # # #             # Try different ways to find the data
# # # # # #             items = []
            
# # # # # #             # Method 1: Check if data is in 'data' field
# # # # # #             if 'data' in data and isinstance(data['data'], list):
# # # # # #                 items = data['data']
# # # # # #                 logger.debug(f"Found {len(items)} items in 'data' field")
# # # # # #             # Method 2: Check if data is directly in response (some APIs do this)
# # # # # #             elif isinstance(data, list):
# # # # # #                 items = data
# # # # # #                 logger.debug(f"Found {len(items)} items in root response")
# # # # # #             # Method 3: Check if there's a 'result' field
# # # # # #             elif 'result' in data and isinstance(data['result'], list):
# # # # # #                 items = data['result']
# # # # # #                 logger.debug(f"Found {len(items)} items in 'result' field")
# # # # # #             # Method 4: Check if response is a dict with category keys
# # # # # #             elif isinstance(data, dict):
# # # # # #                 # Look for any field that might contain the IPO data
# # # # # #                 for key, value in data.items():
# # # # # #                     if isinstance(value, list) and len(value) > 0:
# # # # # #                         # Check if first item has 'category' field
# # # # # #                         if isinstance(value[0], dict) and 'category' in value[0]:
# # # # # #                             items = value
# # # # # #                             logger.debug(f"Found {len(items)} items in '{key}' field")
# # # # # #                             break
            
# # # # # #             if not items:
# # # # # #                 logger.warning("No data items found in response")
# # # # # #                 logger.debug(f"Response structure: {json.dumps(data, indent=2)[:500]}")
# # # # # #                 return None
            
# # # # # #             # Extract QIB data
# # # # # #             qib_data = None
# # # # # #             total_offered = 0
# # # # # #             total_bid = 0
            
# # # # # #             for item in items:
# # # # # #                 # Try to get category from various possible field names
# # # # # #                 category = (
# # # # # #                     item.get('category') or 
# # # # # #                     item.get('Category') or 
# # # # # #                     item.get('cat') or 
# # # # # #                     item.get('type') or 
# # # # # #                     ''
# # # # # #                 )
                
# # # # # #                 # Check if this is QIB
# # # # # #                 if 'QIB' in category or 'Qualified Institutional' in category:
# # # # # #                     qib_data = {
# # # # # #                         'category': category,
# # # # # #                         'no_of_share_offered': int(item.get('noOfShareOffered', item.get('noOfShareOffered', 0))),
# # # # # #                         'no_of_shares_bid': int(item.get('noOfSharesBid', item.get('noOfSharesBid', 0))),
# # # # # #                         'subscription_times': float(item.get('noOfTotalMeant', item.get('totalMeant', 0)))
# # # # # #                     }
# # # # # #                     logger.debug(f"Found QIB data: {qib_data}")
                
# # # # # #                 # Track totals
# # # # # #                 total_offered += int(item.get('noOfShareOffered', item.get('noOfShareOffered', 0)))
# # # # # #                 total_bid += int(item.get('noOfSharesBid', item.get('noOfSharesBid', 0)))
            
# # # # # #             # If QIB not found, try to find it by srNo or position
# # # # # #             if not qib_data and items:
# # # # # #                 # QIB is usually the first item or has srNo: 1
# # # # # #                 for item in items:
# # # # # #                     if item.get('srNo') == '1' or item.get('srNo') == 1:
# # # # # #                         qib_data = {
# # # # # #                             'category': item.get('category', 'QIB'),
# # # # # #                             'no_of_share_offered': int(item.get('noOfShareOffered', 0)),
# # # # # #                             'no_of_shares_bid': int(item.get('noOfSharesBid', 0)),
# # # # # #                             'subscription_times': float(item.get('noOfTotalMeant', 0))
# # # # # #                         }
# # # # # #                         logger.debug(f"Found QIB by srNo: {qib_data}")
# # # # # #                         break
            
# # # # # #             if not qib_data:
# # # # # #                 logger.warning("QIB data not found in response")
# # # # # #                 logger.debug(f"Available items: {json.dumps(items, indent=2)[:500]}")
# # # # # #                 return None
            
# # # # # #             # Calculate total subscription times
# # # # # #             total_subscription_times = total_bid / total_offered if total_offered > 0 else 0
            
# # # # # #             result = {
# # # # # #                 'timestamp': datetime.now().isoformat(),
# # # # # #                 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# # # # # #                 'category': qib_data['category'],
# # # # # #                 'no_of_share_offered': qib_data['no_of_share_offered'],
# # # # # #                 'no_of_shares_bid': qib_data['no_of_shares_bid'],
# # # # # #                 'subscription_times': qib_data['subscription_times'],
# # # # # #                 'total_no_of_share_offered': total_offered,
# # # # # #                 'total_no_of_shares_bid': total_bid,
# # # # # #                 'total_subscription_times': total_subscription_times,
# # # # # #                 'api_response_raw': json.dumps(data)
# # # # # #             }
            
# # # # # #             logger.info(f"QIB Subscription: {qib_data['subscription_times']:.2f}x | Total: {total_subscription_times:.2f}x")
# # # # # #             return result
            
# # # # # #         except requests.exceptions.RequestException as e:
# # # # # #             logger.error(f"Network error: {e}")
# # # # # #             return None
# # # # # #         except json.JSONDecodeError as e:
# # # # # #             logger.error(f"JSON parsing error: {e}")
# # # # # #             logger.debug(f"Response: {response.text[:200]}")
# # # # # #             return None
# # # # # #         except Exception as e:
# # # # # #             logger.error(f"Error fetching data: {e}")
# # # # # #             import traceback
# # # # # #             logger.debug(traceback.format_exc())
# # # # # #             return None
    
# # # # # #     def append_to_csv(self, data: Dict[str, Any]):
# # # # # #         """
# # # # # #         Append data to CSV file
        
# # # # # #         Args:
# # # # # #             data: Data dictionary to append
# # # # # #         """
# # # # # #         try:
# # # # # #             with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
# # # # # #                 writer = csv.writer(f)
# # # # # #                 row = [
# # # # # #                     data['timestamp'],
# # # # # #                     data['datetime'],
# # # # # #                     data['category'],
# # # # # #                     data['no_of_share_offered'],
# # # # # #                     data['no_of_shares_bid'],
# # # # # #                     data['subscription_times'],
# # # # # #                     data['total_no_of_share_offered'],
# # # # # #                     data['total_no_of_shares_bid'],
# # # # # #                     data['total_subscription_times'],
# # # # # #                     data['api_response_raw']
# # # # # #                 ]
# # # # # #                 writer.writerow(row)
            
# # # # # #             logger.debug(f"Appended data to CSV: {data['datetime']}")
            
# # # # # #         except Exception as e:
# # # # # #             logger.error(f"Error appending to CSV: {e}")
    
# # # # # #     def run(self):
# # # # # #         """
# # # # # #         Run the monitoring loop
# # # # # #         """
# # # # # #         logger.info("=" * 60)
# # # # # #         logger.info("LEAP IPO Real-time Monitor Started")
# # # # # #         logger.info("=" * 60)
# # # # # #         logger.info(f"Monitoring: LEAP IPO Subscription Data")
# # # # # #         logger.info(f"Output file: {self.csv_path}")
# # # # # #         logger.info(f"Refresh interval: {self.interval_seconds} seconds")
# # # # # #         logger.info("Press Ctrl+C to stop")
# # # # # #         logger.info("=" * 60)
        
# # # # # #         # Initialize session
# # # # # #         self._init_session()
        
# # # # # #         iteration = 0
        
# # # # # #         try:
# # # # # #             while True:
# # # # # #                 iteration += 1
# # # # # #                 logger.debug(f"\n--- Iteration {iteration} ---")
                
# # # # # #                 # Fetch data
# # # # # #                 data = self.fetch_data()
                
# # # # # #                 if data:
# # # # # #                     # Display current subscription
# # # # # #                     logger.info(f"[{data['datetime']}] QIB: {data['subscription_times']:.2f}x | Total: {data['total_subscription_times']:.2f}x")
                    
# # # # # #                     # Append to CSV
# # # # # #                     self.append_to_csv(data)
# # # # # #                 else:
# # # # # #                     logger.warning("Failed to fetch data, retrying...")
                
# # # # # #                 # Wait for next interval
# # # # # #                 if iteration > 0:
# # # # # #                     logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
# # # # # #                     time.sleep(self.interval_seconds)
                    
# # # # # #         except KeyboardInterrupt:
# # # # # #             logger.info("\nMonitoring stopped by user")
# # # # # #             self._print_summary()
# # # # # #         except Exception as e:
# # # # # #             logger.error(f"Unexpected error: {e}")
# # # # # #             self._print_summary()
    
# # # # # #     def _print_summary(self):
# # # # # #         """Print summary of collected data"""
# # # # # #         try:
# # # # # #             if not self.csv_path.exists():
# # # # # #                 logger.info("No data collected")
# # # # # #                 return
            
# # # # # #             df = pd.read_csv(self.csv_path)
            
# # # # # #             if df.empty:
# # # # # #                 logger.info("No data collected")
# # # # # #                 return
            
# # # # # #             logger.info("\n" + "=" * 60)
# # # # # #             logger.info("Monitoring Summary")
# # # # # #             logger.info("=" * 60)
# # # # # #             logger.info(f"Total records: {len(df)}")
# # # # # #             logger.info(f"First record: {df.iloc[0]['datetime']}")
# # # # # #             logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
# # # # # #             # Latest subscription
# # # # # #             latest = df.iloc[-1]
# # # # # #             logger.info(f"\nLatest QIB Subscription: {latest['subscription_times']:.2f}x")
# # # # # #             logger.info(f"Latest Total Subscription: {latest['total_subscription_times']:.2f}x")
            
# # # # # #             # Calculate changes
# # # # # #             if len(df) > 1:
# # # # # #                 first = df.iloc[0]
# # # # # #                 qib_change = latest['subscription_times'] - first['subscription_times']
# # # # # #                 total_change = latest['total_subscription_times'] - first['total_subscription_times']
                
# # # # # #                 logger.info(f"\nChange from first to latest:")
# # # # # #                 logger.info(f"  QIB: {qib_change:+.2f}x")
# # # # # #                 logger.info(f"  Total: {total_change:+.2f}x")
            
# # # # # #             # Max and min
# # # # # #             max_qib = df['subscription_times'].max()
# # # # # #             min_qib = df['subscription_times'].min()
# # # # # #             max_total = df['total_subscription_times'].max()
# # # # # #             min_total = df['total_subscription_times'].min()
            
# # # # # #             logger.info(f"\nQIB Subscription Range:")
# # # # # #             logger.info(f"  Max: {max_qib:.2f}x")
# # # # # #             logger.info(f"  Min: {min_qib:.2f}x")
            
# # # # # #             logger.info(f"\nTotal Subscription Range:")
# # # # # #             logger.info(f"  Max: {max_total:.2f}x")
# # # # # #             logger.info(f"  Min: {min_total:.2f}x")
            
# # # # # #             logger.info(f"\nData saved to: {self.csv_path}")
# # # # # #             logger.info("=" * 60)
            
# # # # # #         except Exception as e:
# # # # # #             logger.error(f"Error generating summary: {e}")
    
# # # # # #     def generate_report(self):
# # # # # #         """Generate a report from collected data"""
# # # # # #         try:
# # # # # #             if not self.csv_path.exists():
# # # # # #                 logger.warning("No data file found")
# # # # # #                 return
            
# # # # # #             df = pd.read_csv(self.csv_path)
            
# # # # # #             if df.empty:
# # # # # #                 logger.warning("No data in file")
# # # # # #                 return
            
# # # # # #             # Convert datetime
# # # # # #             df['datetime'] = pd.to_datetime(df['datetime'])
            
# # # # # #             # Create report
# # # # # #             report = {
# # # # # #                 'total_records': len(df),
# # # # # #                 'start_time': df.iloc[0]['datetime'],
# # # # # #                 'end_time': df.iloc[-1]['datetime'],
# # # # # #                 'duration_hours': (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds() / 3600,
                
# # # # # #                 'qib_final': df.iloc[-1]['subscription_times'],
# # # # # #                 'qib_start': df.iloc[0]['subscription_times'],
# # # # # #                 'qib_change': df.iloc[-1]['subscription_times'] - df.iloc[0]['subscription_times'],
# # # # # #                 'qib_max': df['subscription_times'].max(),
# # # # # #                 'qib_min': df['subscription_times'].min(),
                
# # # # # #                 'total_final': df.iloc[-1]['total_subscription_times'],
# # # # # #                 'total_start': df.iloc[0]['total_subscription_times'],
# # # # # #                 'total_change': df.iloc[-1]['total_subscription_times'] - df.iloc[0]['total_subscription_times'],
# # # # # #                 'total_max': df['total_subscription_times'].max(),
# # # # # #                 'total_min': df['total_subscription_times'].min(),
# # # # # #             }
            
# # # # # #             # Save report
# # # # # #             report_path = self.output_dir / f"leap_ipo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
# # # # # #             with open(report_path, 'w') as f:
# # # # # #                 json.dump(report, f, indent=2, default=str)
            
# # # # # #             logger.success(f"Report generated: {report_path}")
            
# # # # # #             # Print report
# # # # # #             logger.info("\n" + "=" * 60)
# # # # # #             logger.info("LEAP IPO Subscription Report")
# # # # # #             logger.info("=" * 60)
# # # # # #             logger.info(f"Records: {report['total_records']}")
# # # # # #             logger.info(f"Duration: {report['duration_hours']:.2f} hours")
# # # # # #             logger.info(f"QIB Subscription: {report['qib_final']:.2f}x")
# # # # # #             logger.info(f"QIB Change: {report['qib_change']:+.2f}x")
# # # # # #             logger.info(f"Total Subscription: {report['total_final']:.2f}x")
# # # # # #             logger.info(f"Total Change: {report['total_change']:+.2f}x")
# # # # # #             logger.info("=" * 60)
            
# # # # # #             return report
            
# # # # # #         except Exception as e:
# # # # # #             logger.error(f"Error generating report: {e}")
# # # # # #             return None


# # # # # # def main():
# # # # # #     """Main execution function"""
# # # # # #     import argparse
    
# # # # # #     parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
# # # # # #     parser.add_argument('--interval', type=int, default=300, 
# # # # # #                        help='Refresh interval in seconds (default: 300)')
# # # # # #     parser.add_argument('--once', action='store_true',
# # # # # #                        help='Fetch once and exit')
# # # # # #     parser.add_argument('--report', action='store_true',
# # # # # #                        help='Generate report from existing data and exit')
# # # # # #     parser.add_argument('--output', type=str, default=None,
# # # # # #                        help='Output directory for CSV files')
    
# # # # # #     args = parser.parse_args()
    
# # # # # #     # Setup logger
# # # # # #     setup_logger()
    
# # # # # #     # Set output directory
# # # # # #     output_dir = Path(args.output) if args.output else None
    
# # # # # #     # Initialize monitor
# # # # # #     monitor = LEAPIPOMonitor(
# # # # # #         output_dir=output_dir,
# # # # # #         interval_seconds=args.interval
# # # # # #     )
    
# # # # # #     # Handle report generation
# # # # # #     if args.report:
# # # # # #         monitor.generate_report()
# # # # # #         return
    
# # # # # #     # Handle one-time fetch
# # # # # #     if args.once:
# # # # # #         data = monitor.fetch_data()
# # # # # #         if data:
# # # # # #             monitor.append_to_csv(data)
# # # # # #             logger.success("Data fetched and saved")
# # # # # #             print(json.dumps(data, indent=2))
# # # # # #         return
    
# # # # # #     # Run continuous monitoring
# # # # # #     monitor.run()


# # # # # # if __name__ == "__main__":
# # # # # #     main()

# # # # # # monitor_leap_ipo.py - Fixed version

# # # # # """
# # # # # Real-time monitor for LEAP IPO subscription data from NSE API
# # # # # """
# # # # # import sys
# # # # # import json
# # # # # import time
# # # # # import csv
# # # # # import requests
# # # # # from pathlib import Path
# # # # # from datetime import datetime
# # # # # from loguru import logger
# # # # # import pandas as pd
# # # # # from typing import Optional, Dict, Any

# # # # # # Add src to path
# # # # # sys.path.insert(0, str(Path(__file__).parent))

# # # # # from src.config import DATA_DIR
# # # # # from src.utils import setup_logger


# # # # # class LEAPIPOMonitor:
# # # # #     """Real-time monitor for LEAP IPO subscription data"""
    
# # # # #     # NSE API endpoint
# # # # #     API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
# # # # #     # Headers to mimic browser
# # # # #     HEADERS = {
# # # # #         'accept': '*/*',
# # # # #         'accept-language': 'en-US,en;q=0.9',
# # # # #         'dnt': '1',
# # # # #         'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
# # # # #         'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
# # # # #         'sec-ch-ua-mobile': '?0',
# # # # #         'sec-ch-ua-platform': '"Windows"',
# # # # #         'sec-fetch-dest': 'empty',
# # # # #         'sec-fetch-mode': 'cors',
# # # # #         'sec-fetch-site': 'same-origin',
# # # # #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
# # # # #     }
    
# # # # #     def __init__(self, output_dir: Path = None, interval_seconds: int = 300):
# # # # #         """
# # # # #         Initialize the monitor
        
# # # # #         Args:
# # # # #             output_dir: Directory to save CSV files
# # # # #             interval_seconds: Refresh interval in seconds (default: 300 = 5 minutes)
# # # # #         """
# # # # #         self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
# # # # #         self.output_dir.mkdir(parents=True, exist_ok=True)
# # # # #         self.interval_seconds = interval_seconds
# # # # #         self.session = requests.Session()
# # # # #         self.session.headers.update(self.HEADERS)
        
# # # # #         # CSV file path
# # # # #         self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
# # # # #         # Initialize CSV with headers if it doesn't exist
# # # # #         self._initialize_csv()
        
# # # # #         logger.info(f"LEAP IPO Monitor initialized")
# # # # #         logger.info(f"CSV file: {self.csv_path}")
# # # # #         logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
# # # # #     def _initialize_csv(self):
# # # # #         """Initialize CSV file with headers"""
# # # # #         headers = [
# # # # #             'timestamp',
# # # # #             'datetime',
# # # # #             'update_time',
# # # # #             'qib_category',
# # # # #             'qib_no_of_share_offered',
# # # # #             'qib_no_of_shares_bid',
# # # # #             'qib_subscription_times',
# # # # #             'nii_no_of_share_offered',
# # # # #             'nii_no_of_shares_bid',
# # # # #             'nii_subscription_times',
# # # # #             'rii_no_of_share_offered',
# # # # #             'rii_no_of_shares_bid',
# # # # #             'rii_subscription_times',
# # # # #             'total_no_of_share_offered',
# # # # #             'total_no_of_shares_bid',
# # # # #             'total_subscription_times',
# # # # #             'api_response_raw'
# # # # #         ]
        
# # # # #         if not self.csv_path.exists():
# # # # #             with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
# # # # #                 writer = csv.writer(f)
# # # # #                 writer.writerow(headers)
# # # # #             logger.debug(f"Created CSV file: {self.csv_path}")
    
# # # # #     def _init_session(self):
# # # # #         """Initialize session with NSE to get cookies"""
# # # # #         try:
# # # # #             # First visit main page
# # # # #             self.session.get("https://www.nseindia.com", timeout=30)
# # # # #             logger.debug("Session initialized with NSE")
# # # # #         except Exception as e:
# # # # #             logger.warning(f"Failed to initialize session: {e}")
    
# # # # #     def _safe_int_convert(self, value):
# # # # #         """Safely convert string to int, handling empty strings and non-numeric values"""
# # # # #         if not value or value == '' or value == 'null':
# # # # #             return 0
# # # # #         try:
# # # # #             # Remove commas if present
# # # # #             cleaned = str(value).replace(',', '').strip()
# # # # #             return int(float(cleaned)) if cleaned else 0
# # # # #         except (ValueError, TypeError):
# # # # #             return 0
    
# # # # #     def _safe_float_convert(self, value):
# # # # #         """Safely convert string to float, handling empty strings and non-numeric values"""
# # # # #         if not value or value == '' or value == 'null':
# # # # #             return 0.0
# # # # #         try:
# # # # #             cleaned = str(value).replace(',', '').strip()
# # # # #             return float(cleaned) if cleaned else 0.0
# # # # #         except (ValueError, TypeError):
# # # # #             return 0.0
    
# # # # #     def fetch_data(self) -> Optional[Dict[str, Any]]:
# # # # #         """
# # # # #         Fetch LEAP IPO data from NSE API
        
# # # # #         Returns:
# # # # #             Dictionary with extracted data or None if failed
# # # # #         """
# # # # #         try:
# # # # #             logger.debug("Fetching LEAP IPO data...")
            
# # # # #             # Get data from API
# # # # #             response = self.session.get(
# # # # #                 self.API_URL,
# # # # #                 timeout=30
# # # # #             )
            
# # # # #             if response.status_code != 200:
# # # # #                 logger.error(f"API returned status {response.status_code}")
# # # # #                 logger.debug(f"Response: {response.text[:200]}")
# # # # #                 return None
            
# # # # #             data = response.json()
            
# # # # #             # Debug: Print the structure
# # # # #             logger.debug(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
# # # # #             # Get data items - the API uses 'dataList' field
# # # # #             items = data.get('dataList', [])
            
# # # # #             if not items:
# # # # #                 logger.warning("No dataList found in response")
# # # # #                 return None
            
# # # # #             # Skip the first item (it's the header row)
# # # # #             if len(items) > 0 and items[0].get('category') == 'Category':
# # # # #                 items = items[1:]
            
# # # # #             # Extract data by category
# # # # #             qib_data = None
# # # # #             nii_data = None
# # # # #             rii_data = None
# # # # #             total_data = None
            
# # # # #             for item in items:
# # # # #                 category = item.get('category', '')
                
# # # # #                 # Extract QIB data
# # # # #                 if 'Qualified Institutional' in category or category == 'QIBs':
# # # # #                     qib_data = {
# # # # #                         'category': category,
# # # # #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# # # # #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# # # # #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# # # # #                     }
                
# # # # #                 # Extract NII data
# # # # #                 elif 'Non Institutional Investors' in category and 'Bid amount of more than Ten Lakh' in category:
# # # # #                     nii_data = {
# # # # #                         'category': category,
# # # # #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# # # # #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# # # # #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# # # # #                     }
                
# # # # #                 # Extract RII data
# # # # #                 elif 'Retail Individual Investors' in category:
# # # # #                     rii_data = {
# # # # #                         'category': category,
# # # # #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# # # # #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# # # # #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# # # # #                     }
                
# # # # #                 # Extract Total data
# # # # #                 elif category == 'Total':
# # # # #                     total_data = {
# # # # #                         'category': category,
# # # # #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# # # # #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# # # # #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# # # # #                     }
            
# # # # #             # If QIB not found, try to find by srNo
# # # # #             if not qib_data:
# # # # #                 for item in items:
# # # # #                     if item.get('srNo') == '1' or item.get('srNo') == 1:
# # # # #                         qib_data = {
# # # # #                             'category': item.get('category', 'QIB'),
# # # # #                             'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# # # # #                             'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# # # # #                             'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# # # # #                         }
# # # # #                         break
            
# # # # #             if not qib_data:
# # # # #                 logger.warning("QIB data not found in response")
# # # # #                 return None
            
# # # # #             # Get update time
# # # # #             update_time = data.get('updateTime', '')
            
# # # # #             # Calculate totals if not available
# # # # #             if total_data:
# # # # #                 total_offered = total_data['no_of_share_offered']
# # # # #                 total_bid = total_data['no_of_shares_bid']
# # # # #                 total_subscription = total_data['subscription_times']
# # # # #             else:
# # # # #                 # Calculate from individual categories
# # # # #                 total_offered = (
# # # # #                     qib_data.get('no_of_share_offered', 0) +
# # # # #                     (nii_data.get('no_of_share_offered', 0) if nii_data else 0) +
# # # # #                     (rii_data.get('no_of_share_offered', 0) if rii_data else 0)
# # # # #                 )
# # # # #                 total_bid = (
# # # # #                     qib_data.get('no_of_shares_bid', 0) +
# # # # #                     (nii_data.get('no_of_shares_bid', 0) if nii_data else 0) +
# # # # #                     (rii_data.get('no_of_shares_bid', 0) if rii_data else 0)
# # # # #                 )
# # # # #                 total_subscription = total_bid / total_offered if total_offered > 0 else 0
            
# # # # #             result = {
# # # # #                 'timestamp': datetime.now().isoformat(),
# # # # #                 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# # # # #                 'update_time': update_time,
# # # # #                 'qib_category': qib_data['category'],
# # # # #                 'qib_no_of_share_offered': qib_data['no_of_share_offered'],
# # # # #                 'qib_no_of_shares_bid': qib_data['no_of_shares_bid'],
# # # # #                 'qib_subscription_times': qib_data['subscription_times'],
# # # # #                 'nii_no_of_share_offered': nii_data['no_of_share_offered'] if nii_data else 0,
# # # # #                 'nii_no_of_shares_bid': nii_data['no_of_shares_bid'] if nii_data else 0,
# # # # #                 'nii_subscription_times': nii_data['subscription_times'] if nii_data else 0,
# # # # #                 'rii_no_of_share_offered': rii_data['no_of_share_offered'] if rii_data else 0,
# # # # #                 'rii_no_of_shares_bid': rii_data['no_of_shares_bid'] if rii_data else 0,
# # # # #                 'rii_subscription_times': rii_data['subscription_times'] if rii_data else 0,
# # # # #                 'total_no_of_share_offered': total_offered,
# # # # #                 'total_no_of_shares_bid': total_bid,
# # # # #                 'total_subscription_times': total_subscription,
# # # # #                 'api_response_raw': json.dumps(data)
# # # # #             }
            
# # # # #             logger.info(f"QIB: {qib_data['subscription_times']:.2f}x | NII: {(nii_data['subscription_times'] if nii_data else 0):.2f}x | RII: {(rii_data['subscription_times'] if rii_data else 0):.2f}x | Total: {total_subscription:.2f}x")
# # # # #             return result
            
# # # # #         except requests.exceptions.RequestException as e:
# # # # #             logger.error(f"Network error: {e}")
# # # # #             return None
# # # # #         except json.JSONDecodeError as e:
# # # # #             logger.error(f"JSON parsing error: {e}")
# # # # #             logger.debug(f"Response: {response.text[:200]}")
# # # # #             return None
# # # # #         except Exception as e:
# # # # #             logger.error(f"Error fetching data: {e}")
# # # # #             import traceback
# # # # #             logger.debug(traceback.format_exc())
# # # # #             return None
    
# # # # #     def append_to_csv(self, data: Dict[str, Any]):
# # # # #         """
# # # # #         Append data to CSV file
        
# # # # #         Args:
# # # # #             data: Data dictionary to append
# # # # #         """
# # # # #         try:
# # # # #             with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
# # # # #                 writer = csv.writer(f)
# # # # #                 row = [
# # # # #                     data['timestamp'],
# # # # #                     data['datetime'],
# # # # #                     data['update_time'],
# # # # #                     data['qib_category'],
# # # # #                     data['qib_no_of_share_offered'],
# # # # #                     data['qib_no_of_shares_bid'],
# # # # #                     data['qib_subscription_times'],
# # # # #                     data['nii_no_of_share_offered'],
# # # # #                     data['nii_no_of_shares_bid'],
# # # # #                     data['nii_subscription_times'],
# # # # #                     data['rii_no_of_share_offered'],
# # # # #                     data['rii_no_of_shares_bid'],
# # # # #                     data['rii_subscription_times'],
# # # # #                     data['total_no_of_share_offered'],
# # # # #                     data['total_no_of_shares_bid'],
# # # # #                     data['total_subscription_times'],
# # # # #                     data['api_response_raw']
# # # # #                 ]
# # # # #                 writer.writerow(row)
            
# # # # #             logger.debug(f"Appended data to CSV: {data['datetime']}")
            
# # # # #         except Exception as e:
# # # # #             logger.error(f"Error appending to CSV: {e}")
    
# # # # #     def run(self):
# # # # #         """
# # # # #         Run the monitoring loop
# # # # #         """
# # # # #         logger.info("=" * 60)
# # # # #         logger.info("LEAP IPO Real-time Monitor Started")
# # # # #         logger.info("=" * 60)
# # # # #         logger.info(f"Monitoring: LEAP IPO Subscription Data")
# # # # #         logger.info(f"Output file: {self.csv_path}")
# # # # #         logger.info(f"Refresh interval: {self.interval_seconds} seconds")
# # # # #         logger.info("Press Ctrl+C to stop")
# # # # #         logger.info("=" * 60)
        
# # # # #         # Initialize session
# # # # #         self._init_session()
        
# # # # #         iteration = 0
        
# # # # #         try:
# # # # #             while True:
# # # # #                 iteration += 1
# # # # #                 logger.debug(f"\n--- Iteration {iteration} ---")
                
# # # # #                 # Fetch data
# # # # #                 data = self.fetch_data()
                
# # # # #                 if data:
# # # # #                     # Display current subscription
# # # # #                     logger.info(f"[{data['datetime']}] QIB: {data['qib_subscription_times']:.2f}x | Total: {data['total_subscription_times']:.2f}x")
                    
# # # # #                     # Append to CSV
# # # # #                     self.append_to_csv(data)
# # # # #                 else:
# # # # #                     logger.warning("Failed to fetch data, retrying...")
                
# # # # #                 # Wait for next interval
# # # # #                 if iteration > 0:
# # # # #                     logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
# # # # #                     time.sleep(self.interval_seconds)
                    
# # # # #         except KeyboardInterrupt:
# # # # #             logger.info("\nMonitoring stopped by user")
# # # # #             self._print_summary()
# # # # #         except Exception as e:
# # # # #             logger.error(f"Unexpected error: {e}")
# # # # #             self._print_summary()
    
# # # # #     def _print_summary(self):
# # # # #         """Print summary of collected data"""
# # # # #         try:
# # # # #             if not self.csv_path.exists():
# # # # #                 logger.info("No data collected")
# # # # #                 return
            
# # # # #             df = pd.read_csv(self.csv_path)
            
# # # # #             if df.empty:
# # # # #                 logger.info("No data collected")
# # # # #                 return
            
# # # # #             logger.info("\n" + "=" * 60)
# # # # #             logger.info("Monitoring Summary")
# # # # #             logger.info("=" * 60)
# # # # #             logger.info(f"Total records: {len(df)}")
# # # # #             logger.info(f"First record: {df.iloc[0]['datetime']}")
# # # # #             logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
# # # # #             # Latest subscription
# # # # #             latest = df.iloc[-1]
# # # # #             logger.info(f"\nLatest Subscriptions:")
# # # # #             logger.info(f"  QIB: {latest['qib_subscription_times']:.2f}x")
# # # # #             logger.info(f"  Total: {latest['total_subscription_times']:.2f}x")
            
# # # # #             # Calculate changes
# # # # #             if len(df) > 1:
# # # # #                 first = df.iloc[0]
# # # # #                 qib_change = latest['qib_subscription_times'] - first['qib_subscription_times']
# # # # #                 total_change = latest['total_subscription_times'] - first['total_subscription_times']
                
# # # # #                 logger.info(f"\nChange from first to latest:")
# # # # #                 logger.info(f"  QIB: {qib_change:+.2f}x")
# # # # #                 logger.info(f"  Total: {total_change:+.2f}x")
            
# # # # #             # Max and min
# # # # #             max_qib = df['qib_subscription_times'].max()
# # # # #             min_qib = df['qib_subscription_times'].min()
# # # # #             max_total = df['total_subscription_times'].max()
# # # # #             min_total = df['total_subscription_times'].min()
            
# # # # #             logger.info(f"\nQIB Subscription Range:")
# # # # #             logger.info(f"  Max: {max_qib:.2f}x")
# # # # #             logger.info(f"  Min: {min_qib:.2f}x")
            
# # # # #             logger.info(f"\nTotal Subscription Range:")
# # # # #             logger.info(f"  Max: {max_total:.2f}x")
# # # # #             logger.info(f"  Min: {min_total:.2f}x")
            
# # # # #             logger.info(f"\nData saved to: {self.csv_path}")
# # # # #             logger.info("=" * 60)
            
# # # # #         except Exception as e:
# # # # #             logger.error(f"Error generating summary: {e}")
    
# # # # #     def generate_report(self):
# # # # #         """Generate a report from collected data"""
# # # # #         try:
# # # # #             if not self.csv_path.exists():
# # # # #                 logger.warning("No data file found")
# # # # #                 return
            
# # # # #             df = pd.read_csv(self.csv_path)
            
# # # # #             if df.empty:
# # # # #                 logger.warning("No data in file")
# # # # #                 return
            
# # # # #             # Convert datetime
# # # # #             df['datetime'] = pd.to_datetime(df['datetime'])
            
# # # # #             # Create report
# # # # #             report = {
# # # # #                 'total_records': len(df),
# # # # #                 'start_time': df.iloc[0]['datetime'],
# # # # #                 'end_time': df.iloc[-1]['datetime'],
# # # # #                 'duration_hours': (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds() / 3600,
                
# # # # #                 'qib_final': df.iloc[-1]['qib_subscription_times'],
# # # # #                 'qib_start': df.iloc[0]['qib_subscription_times'],
# # # # #                 'qib_change': df.iloc[-1]['qib_subscription_times'] - df.iloc[0]['qib_subscription_times'],
# # # # #                 'qib_max': df['qib_subscription_times'].max(),
# # # # #                 'qib_min': df['qib_subscription_times'].min(),
                
# # # # #                 'total_final': df.iloc[-1]['total_subscription_times'],
# # # # #                 'total_start': df.iloc[0]['total_subscription_times'],
# # # # #                 'total_change': df.iloc[-1]['total_subscription_times'] - df.iloc[0]['total_subscription_times'],
# # # # #                 'total_max': df['total_subscription_times'].max(),
# # # # #                 'total_min': df['total_subscription_times'].min(),
# # # # #             }
            
# # # # #             # Save report
# # # # #             report_path = self.output_dir / f"leap_ipo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
# # # # #             with open(report_path, 'w') as f:
# # # # #                 json.dump(report, f, indent=2, default=str)
            
# # # # #             logger.success(f"Report generated: {report_path}")
            
# # # # #             # Print report
# # # # #             logger.info("\n" + "=" * 60)
# # # # #             logger.info("LEAP IPO Subscription Report")
# # # # #             logger.info("=" * 60)
# # # # #             logger.info(f"Records: {report['total_records']}")
# # # # #             logger.info(f"Duration: {report['duration_hours']:.2f} hours")
# # # # #             logger.info(f"QIB Subscription: {report['qib_final']:.2f}x")
# # # # #             logger.info(f"QIB Change: {report['qib_change']:+.2f}x")
# # # # #             logger.info(f"Total Subscription: {report['total_final']:.2f}x")
# # # # #             logger.info(f"Total Change: {report['total_change']:+.2f}x")
# # # # #             logger.info("=" * 60)
            
# # # # #             return report
            
# # # # #         except Exception as e:
# # # # #             logger.error(f"Error generating report: {e}")
# # # # #             return None


# # # # # def main():
# # # # #     """Main execution function"""
# # # # #     import argparse
    
# # # # #     parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
# # # # #     parser.add_argument('--interval', type=int, default=300, 
# # # # #                        help='Refresh interval in seconds (default: 300)')
# # # # #     parser.add_argument('--once', action='store_true',
# # # # #                        help='Fetch once and exit')
# # # # #     parser.add_argument('--report', action='store_true',
# # # # #                        help='Generate report from existing data and exit')
# # # # #     parser.add_argument('--output', type=str, default=None,
# # # # #                        help='Output directory for CSV files')
    
# # # # #     args = parser.parse_args()
    
# # # # #     # Setup logger
# # # # #     setup_logger()
    
# # # # #     # Set output directory
# # # # #     output_dir = Path(args.output) if args.output else None
    
# # # # #     # Initialize monitor
# # # # #     monitor = LEAPIPOMonitor(
# # # # #         output_dir=output_dir,
# # # # #         interval_seconds=args.interval
# # # # #     )
    
# # # # #     # Handle report generation
# # # # #     if args.report:
# # # # #         monitor.generate_report()
# # # # #         return
    
# # # # #     # Handle one-time fetch
# # # # #     if args.once:
# # # # #         data = monitor.fetch_data()
# # # # #         if data:
# # # # #             monitor.append_to_csv(data)
# # # # #             logger.success("Data fetched and saved")
# # # # #             print(json.dumps(data, indent=2))
# # # # #         return
    
# # # # #     # Run continuous monitoring
# # # # #     monitor.run()


# # # # # if __name__ == "__main__":
# # # # #     main()

# # # # # monitor_leap_ipo.py - Final version with proper columns and counter

# # # # """
# # # # Real-time monitor for LEAP IPO subscription data from NSE API
# # # # """
# # # # import sys
# # # # import json
# # # # import time
# # # # import csv
# # # # import requests
# # # # from pathlib import Path
# # # # from datetime import datetime
# # # # from loguru import logger
# # # # import pandas as pd
# # # # from typing import Optional, Dict, Any

# # # # # Add src to path
# # # # sys.path.insert(0, str(Path(__file__).parent))

# # # # from src.config import DATA_DIR
# # # # from src.utils import setup_logger


# # # # class LEAPIPOMonitor:
# # # #     """Real-time monitor for LEAP IPO subscription data"""
    
# # # #     # NSE API endpoint
# # # #     API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
# # # #     # Headers to mimic browser
# # # #     HEADERS = {
# # # #         'accept': '*/*',
# # # #         'accept-language': 'en-US,en;q=0.9',
# # # #         'dnt': '1',
# # # #         'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
# # # #         'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
# # # #         'sec-ch-ua-mobile': '?0',
# # # #         'sec-ch-ua-platform': '"Windows"',
# # # #         'sec-fetch-dest': 'empty',
# # # #         'sec-fetch-mode': 'cors',
# # # #         'sec-fetch-site': 'same-origin',
# # # #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
# # # #     }
    
# # # #     def __init__(self, output_dir: Path = None, interval_seconds: int = 120):
# # # #         """
# # # #         Initialize the monitor
        
# # # #         Args:
# # # #             output_dir: Directory to save CSV files
# # # #             interval_seconds: Refresh interval in seconds (default: 120 = 2 minutes)
# # # #         """
# # # #         self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
# # # #         self.output_dir.mkdir(parents=True, exist_ok=True)
# # # #         self.interval_seconds = interval_seconds
# # # #         self.session = requests.Session()
# # # #         self.session.headers.update(self.HEADERS)
        
# # # #         # Counter for QIB >= 5x
# # # #         self.qib_above_5_count = 0
# # # #         self.last_qib_value = None
        
# # # #         # CSV file path
# # # #         self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
# # # #         # Initialize CSV with headers if it doesn't exist
# # # #         self._initialize_csv()
        
# # # #         logger.info(f"LEAP IPO Monitor initialized")
# # # #         logger.info(f"CSV file: {self.csv_path}")
# # # #         logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
# # # #     def _initialize_csv(self):
# # # #         """Initialize CSV file with headers"""
# # # #         headers = [
# # # #             'timestamp',
# # # #             'datetime',
# # # #             'update_time',
# # # #             'qib_subscription',
# # # #             'nii_subscription',
# # # #             'rii_subscription',
# # # #             'total_subscription',
# # # #             'qib_above_5x_count'
# # # #         ]
        
# # # #         if not self.csv_path.exists():
# # # #             with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
# # # #                 writer = csv.writer(f)
# # # #                 writer.writerow(headers)
# # # #             logger.debug(f"Created CSV file: {self.csv_path}")
    
# # # #     def _init_session(self):
# # # #         """Initialize session with NSE to get cookies"""
# # # #         try:
# # # #             # First visit main page
# # # #             self.session.get("https://www.nseindia.com", timeout=30)
# # # #             logger.debug("Session initialized with NSE")
# # # #         except Exception as e:
# # # #             logger.warning(f"Failed to initialize session: {e}")
    
# # # #     def _safe_int_convert(self, value):
# # # #         """Safely convert string to int"""
# # # #         if not value or value == '' or value == 'null':
# # # #             return 0
# # # #         try:
# # # #             cleaned = str(value).replace(',', '').strip()
# # # #             return int(float(cleaned)) if cleaned else 0
# # # #         except (ValueError, TypeError):
# # # #             return 0
    
# # # #     def _safe_float_convert(self, value):
# # # #         """Safely convert string to float"""
# # # #         if not value or value == '' or value == 'null':
# # # #             return 0.0
# # # #         try:
# # # #             cleaned = str(value).replace(',', '').strip()
# # # #             return float(cleaned) if cleaned else 0.0
# # # #         except (ValueError, TypeError):
# # # #             return 0.0
    
# # # #     def fetch_data(self) -> Optional[Dict[str, Any]]:
# # # #         """
# # # #         Fetch LEAP IPO data from NSE API
        
# # # #         Returns:
# # # #             Dictionary with extracted data or None if failed
# # # #         """
# # # #         try:
# # # #             logger.debug("Fetching LEAP IPO data...")
            
# # # #             # Get data from API
# # # #             response = self.session.get(
# # # #                 self.API_URL,
# # # #                 timeout=30
# # # #             )
            
# # # #             if response.status_code != 200:
# # # #                 logger.error(f"API returned status {response.status_code}")
# # # #                 return None
            
# # # #             data = response.json()
            
# # # #             # Get data items
# # # #             items = data.get('dataList', [])
            
# # # #             if not items:
# # # #                 logger.warning("No dataList found in response")
# # # #                 return None
            
# # # #             # Skip the header row
# # # #             if len(items) > 0 and items[0].get('category') == 'Category':
# # # #                 items = items[1:]
            
# # # #             # Extract data by category
# # # #             qib_subscription = 0.0
# # # #             nii_subscription = 0.0
# # # #             rii_subscription = 0.0
# # # #             total_subscription = 0.0
            
# # # #             for item in items:
# # # #                 category = item.get('category', '')
                
# # # #                 # Extract QIB data
# # # #                 if 'Qualified Institutional' in category or category == 'QIBs':
# # # #                     qib_subscription = self._safe_float_convert(item.get('noOfTotalMeant', 0))
                
# # # #                 # Extract NII data (the one with "more than Ten Lakh")
# # # #                 elif 'Non Institutional Investors' in category and 'more than Ten Lakh' in category:
# # # #                     nii_subscription = self._safe_float_convert(item.get('noOfTotalMeant', 0))
                
# # # #                 # Extract RII data
# # # #                 elif 'Retail Individual Investors' in category:
# # # #                     rii_subscription = self._safe_float_convert(item.get('noOfTotalMeant', 0))
                
# # # #                 # Extract Total data
# # # #                 elif category == 'Total':
# # # #                     total_subscription = self._safe_float_convert(item.get('noOfTotalMeant', 0))
            
# # # #             # Get update time
# # # #             update_time = data.get('updateTime', '')
            
# # # #             result = {
# # # #                 'timestamp': datetime.now().isoformat(),
# # # #                 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# # # #                 'update_time': update_time,
# # # #                 'qib_subscription': qib_subscription,
# # # #                 'nii_subscription': nii_subscription,
# # # #                 'rii_subscription': rii_subscription,
# # # #                 'total_subscription': total_subscription
# # # #             }
            
# # # #             logger.info(f"QIB: {qib_subscription:.2f}x | NII: {nii_subscription:.2f}x | RII: {rii_subscription:.2f}x | Total: {total_subscription:.2f}x")
# # # #             return result
            
# # # #         except requests.exceptions.RequestException as e:
# # # #             logger.error(f"Network error: {e}")
# # # #             return None
# # # #         except json.JSONDecodeError as e:
# # # #             logger.error(f"JSON parsing error: {e}")
# # # #             return None
# # # #         except Exception as e:
# # # #             logger.error(f"Error fetching data: {e}")
# # # #             return None
    
# # # #     def append_to_csv(self, data: Dict[str, Any]):
# # # #         """
# # # #         Append data to CSV file with counter tracking
        
# # # #         Args:
# # # #             data: Data dictionary to append
# # # #         """
# # # #         try:
# # # #             # Update counter only if QIB value changed
# # # #             current_qib = data['qib_subscription']
            
# # # #             # Check if QIB >= 5 and value changed
# # # #             if current_qib >= 5.0:
# # # #                 if self.last_qib_value is None or current_qib != self.last_qib_value:
# # # #                     self.qib_above_5_count += 1
# # # #                     logger.info(f"🎯 QIB subscription {current_qib:.2f}x >= 5x! Count: {self.qib_above_5_count}")
            
# # # #             # Update last value
# # # #             self.last_qib_value = current_qib
            
# # # #             # Prepare row with clean columns
# # # #             row = [
# # # #                 data['timestamp'],
# # # #                 data['datetime'],
# # # #                 data['update_time'],
# # # #                 round(data['qib_subscription'], 2),
# # # #                 round(data['nii_subscription'], 2),
# # # #                 round(data['rii_subscription'], 2),
# # # #                 round(data['total_subscription'], 2),
# # # #                 self.qib_above_5_count
# # # #             ]
            
# # # #             # Append to CSV
# # # #             with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
# # # #                 writer = csv.writer(f)
# # # #                 writer.writerow(row)
            
# # # #             logger.debug(f"Appended data to CSV: {data['datetime']}")
            
# # # #         except Exception as e:
# # # #             logger.error(f"Error appending to CSV: {e}")
    
# # # #     def run(self):
# # # #         """
# # # #         Run the monitoring loop
# # # #         """
# # # #         logger.info("=" * 60)
# # # #         logger.info("LEAP IPO Real-time Monitor Started")
# # # #         logger.info("=" * 60)
# # # #         logger.info(f"Monitoring: LEAP IPO Subscription Data")
# # # #         logger.info(f"Output file: {self.csv_path}")
# # # #         logger.info(f"Refresh interval: {self.interval_seconds} seconds")
# # # #         logger.info(f"Tracking QIB >= 5x counter")
# # # #         logger.info("Press Ctrl+C to stop")
# # # #         logger.info("=" * 60)
        
# # # #         # Initialize session
# # # #         self._init_session()
        
# # # #         iteration = 0
        
# # # #         try:
# # # #             while True:
# # # #                 iteration += 1
# # # #                 logger.debug(f"\n--- Iteration {iteration} ---")
                
# # # #                 # Fetch data
# # # #                 data = self.fetch_data()
                
# # # #                 if data:
# # # #                     # Display current subscription
# # # #                     logger.info(f"[{data['datetime']}] QIB: {data['qib_subscription']:.2f}x | Total: {data['total_subscription']:.2f}x | 5x Count: {self.qib_above_5_count}")
                    
# # # #                     # Append to CSV
# # # #                     self.append_to_csv(data)
# # # #                 else:
# # # #                     logger.warning("Failed to fetch data, retrying...")
                
# # # #                 # Wait for next interval
# # # #                 if iteration > 0:
# # # #                     logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
# # # #                     time.sleep(self.interval_seconds)
                    
# # # #         except KeyboardInterrupt:
# # # #             logger.info("\nMonitoring stopped by user")
# # # #             self._print_summary()
# # # #         except Exception as e:
# # # #             logger.error(f"Unexpected error: {e}")
# # # #             self._print_summary()
    
# # # #     def _print_summary(self):
# # # #         """Print summary of collected data"""
# # # #         try:
# # # #             if not self.csv_path.exists():
# # # #                 logger.info("No data collected")
# # # #                 return
            
# # # #             df = pd.read_csv(self.csv_path)
            
# # # #             if df.empty:
# # # #                 logger.info("No data collected")
# # # #                 return
            
# # # #             logger.info("\n" + "=" * 60)
# # # #             logger.info("Monitoring Summary")
# # # #             logger.info("=" * 60)
# # # #             logger.info(f"Total records: {len(df)}")
# # # #             logger.info(f"First record: {df.iloc[0]['datetime']}")
# # # #             logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
# # # #             # Latest subscription
# # # #             latest = df.iloc[-1]
# # # #             logger.info(f"\nLatest Subscriptions:")
# # # #             logger.info(f"  QIB: {latest['qib_subscription']:.2f}x")
# # # #             logger.info(f"  NII: {latest['nii_subscription']:.2f}x")
# # # #             logger.info(f"  RII: {latest['rii_subscription']:.2f}x")
# # # #             logger.info(f"  Total: {latest['total_subscription']:.2f}x")
            
# # # #             # Counter
# # # #             logger.info(f"\nQIB >= 5x Counter: {latest['qib_above_5x_count']}")
            
# # # #             # Calculate changes
# # # #             if len(df) > 1:
# # # #                 first = df.iloc[0]
# # # #                 qib_change = latest['qib_subscription'] - first['qib_subscription']
# # # #                 total_change = latest['total_subscription'] - first['total_subscription']
                
# # # #                 logger.info(f"\nChange from first to latest:")
# # # #                 logger.info(f"  QIB: {qib_change:+.2f}x")
# # # #                 logger.info(f"  Total: {total_change:+.2f}x")
            
# # # #             # Max and min
# # # #             max_qib = df['qib_subscription'].max()
# # # #             min_qib = df['qib_subscription'].min()
            
# # # #             logger.info(f"\nQIB Subscription Range:")
# # # #             logger.info(f"  Max: {max_qib:.2f}x")
# # # #             logger.info(f"  Min: {min_qib:.2f}x")
            
# # # #             # Times QIB crossed 5x
# # # #             logger.info(f"\nQIB >= 5x Count: {df['qib_above_5x_count'].max()}")
            
# # # #             logger.info(f"\nData saved to: {self.csv_path}")
# # # #             logger.info("=" * 60)
            
# # # #         except Exception as e:
# # # #             logger.error(f"Error generating summary: {e}")
    
# # # #     def generate_report(self):
# # # #         """Generate a report from collected data"""
# # # #         try:
# # # #             if not self.csv_path.exists():
# # # #                 logger.warning("No data file found")
# # # #                 return
            
# # # #             df = pd.read_csv(self.csv_path)
            
# # # #             if df.empty:
# # # #                 logger.warning("No data in file")
# # # #                 return
            
# # # #             # Convert datetime
# # # #             df['datetime'] = pd.to_datetime(df['datetime'])
            
# # # #             # Create report
# # # #             report = {
# # # #                 'total_records': len(df),
# # # #                 'start_time': df.iloc[0]['datetime'],
# # # #                 'end_time': df.iloc[-1]['datetime'],
# # # #                 'duration_hours': (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds() / 3600,
                
# # # #                 'qib_final': df.iloc[-1]['qib_subscription'],
# # # #                 'qib_start': df.iloc[0]['qib_subscription'],
# # # #                 'qib_change': df.iloc[-1]['qib_subscription'] - df.iloc[0]['qib_subscription'],
# # # #                 'qib_max': df['qib_subscription'].max(),
# # # #                 'qib_min': df['qib_subscription'].min(),
# # # #                 'qib_above_5x_count': df['qib_above_5x_count'].max(),
                
# # # #                 'total_final': df.iloc[-1]['total_subscription'],
# # # #                 'total_start': df.iloc[0]['total_subscription'],
# # # #                 'total_change': df.iloc[-1]['total_subscription'] - df.iloc[0]['total_subscription'],
# # # #                 'total_max': df['total_subscription'].max(),
# # # #                 'total_min': df['total_subscription'].min(),
# # # #             }
            
# # # #             # Save report
# # # #             report_path = self.output_dir / f"leap_ipo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
# # # #             with open(report_path, 'w') as f:
# # # #                 json.dump(report, f, indent=2, default=str)
            
# # # #             logger.success(f"Report generated: {report_path}")
            
# # # #             # Print report
# # # #             logger.info("\n" + "=" * 60)
# # # #             logger.info("LEAP IPO Subscription Report")
# # # #             logger.info("=" * 60)
# # # #             logger.info(f"Records: {report['total_records']}")
# # # #             logger.info(f"Duration: {report['duration_hours']:.2f} hours")
# # # #             logger.info(f"QIB Subscription: {report['qib_final']:.2f}x")
# # # #             logger.info(f"QIB Change: {report['qib_change']:+.2f}x")
# # # #             logger.info(f"Total Subscription: {report['total_final']:.2f}x")
# # # #             logger.info(f"Total Change: {report['total_change']:+.2f}x")
# # # #             logger.info(f"Times QIB >= 5x: {report['qib_above_5x_count']}")
# # # #             logger.info("=" * 60)
            
# # # #             return report
            
# # # #         except Exception as e:
# # # #             logger.error(f"Error generating report: {e}")
# # # #             return None


# # # # def main():
# # # #     """Main execution function"""
# # # #     import argparse
    
# # # #     parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
# # # #     parser.add_argument('--interval', type=int, default=120, 
# # # #                        help='Refresh interval in seconds (default: 120)')
# # # #     parser.add_argument('--once', action='store_true',
# # # #                        help='Fetch once and exit')
# # # #     parser.add_argument('--report', action='store_true',
# # # #                        help='Generate report from existing data and exit')
# # # #     parser.add_argument('--output', type=str, default=None,
# # # #                        help='Output directory for CSV files')
    
# # # #     args = parser.parse_args()
    
# # # #     # Setup logger
# # # #     setup_logger()
    
# # # #     # Set output directory
# # # #     output_dir = Path(args.output) if args.output else None
    
# # # #     # Initialize monitor
# # # #     monitor = LEAPIPOMonitor(
# # # #         output_dir=output_dir,
# # # #         interval_seconds=args.interval
# # # #     )
    
# # # #     # Handle report generation
# # # #     if args.report:
# # # #         monitor.generate_report()
# # # #         return
    
# # # #     # Handle one-time fetch
# # # #     if args.once:
# # # #         data = monitor.fetch_data()
# # # #         if data:
# # # #             monitor.append_to_csv(data)
# # # #             logger.success("Data fetched and saved")
# # # #             print(json.dumps(data, indent=2))
# # # #         return
    
# # # #     # Run continuous monitoring
# # # #     monitor.run()


# # # # if __name__ == "__main__":
# # # #     main()

# # # # monitor_leap_ipo.py - Clean version with minimal columns

# # # """
# # # Real-time monitor for LEAP IPO subscription data from NSE API
# # # """
# # # import sys
# # # import json
# # # import time
# # # import csv
# # # import requests
# # # from pathlib import Path
# # # from datetime import datetime
# # # from loguru import logger
# # # import pandas as pd
# # # from typing import Optional, Dict, Any

# # # # Add src to path
# # # sys.path.insert(0, str(Path(__file__).parent))

# # # from src.config import DATA_DIR
# # # from src.utils import setup_logger


# # # class LEAPIPOMonitor:
# # #     """Real-time monitor for LEAP IPO subscription data"""
    
# # #     # NSE API endpoint
# # #     API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
# # #     # Headers to mimic browser
# # #     HEADERS = {
# # #         'accept': '*/*',
# # #         'accept-language': 'en-US,en;q=0.9',
# # #         'dnt': '1',
# # #         'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
# # #         'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
# # #         'sec-ch-ua-mobile': '?0',
# # #         'sec-ch-ua-platform': '"Windows"',
# # #         'sec-fetch-dest': 'empty',
# # #         'sec-fetch-mode': 'cors',
# # #         'sec-fetch-site': 'same-origin',
# # #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
# # #     }
    
# # #     def __init__(self, output_dir: Path = None, interval_seconds: int = 120):
# # #         """
# # #         Initialize the monitor
        
# # #         Args:
# # #             output_dir: Directory to save CSV files
# # #             interval_seconds: Refresh interval in seconds (default: 120 = 2 minutes)
# # #         """
# # #         self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
# # #         self.output_dir.mkdir(parents=True, exist_ok=True)
# # #         self.interval_seconds = interval_seconds
# # #         self.session = requests.Session()
# # #         self.session.headers.update(self.HEADERS)
        
# # #         # Counter for tracking
# # #         self.last_qib_value = None
# # #         self.counter = 0
# # #         self.last_category_data = {}
        
# # #         # CSV file path
# # #         self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
# # #         # Initialize CSV with headers if it doesn't exist
# # #         self._initialize_csv()
        
# # #         logger.info(f"LEAP IPO Monitor initialized")
# # #         logger.info(f"CSV file: {self.csv_path}")
# # #         logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
# # #     def _initialize_csv(self):
# # #         """Initialize CSV file with headers"""
# # #         headers = [
# # #             'timestamp',
# # #             'datetime',
# # #             'update_time',
# # #             'category',
# # #             'no_of_shares_offered',
# # #             'no_of_shares_bid',
# # #             'no_of_times_total_meant',
# # #             'counter'
# # #         ]
        
# # #         if not self.csv_path.exists():
# # #             with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
# # #                 writer = csv.writer(f)
# # #                 writer.writerow(headers)
# # #             logger.debug(f"Created CSV file: {self.csv_path}")
    
# # #     def _init_session(self):
# # #         """Initialize session with NSE to get cookies"""
# # #         try:
# # #             # First visit main page
# # #             self.session.get("https://www.nseindia.com", timeout=30)
# # #             logger.debug("Session initialized with NSE")
# # #         except Exception as e:
# # #             logger.warning(f"Failed to initialize session: {e}")
    
# # #     def _safe_int_convert(self, value):
# # #         """Safely convert string to int"""
# # #         if not value or value == '' or value == 'null':
# # #             return 0
# # #         try:
# # #             cleaned = str(value).replace(',', '').strip()
# # #             return int(float(cleaned)) if cleaned else 0
# # #         except (ValueError, TypeError):
# # #             return 0
    
# # #     def _safe_float_convert(self, value):
# # #         """Safely convert string to float"""
# # #         if not value or value == '' or value == 'null':
# # #             return 0.0
# # #         try:
# # #             cleaned = str(value).replace(',', '').strip()
# # #             return float(cleaned) if cleaned else 0.0
# # #         except (ValueError, TypeError):
# # #             return 0.0
    
# # #     def fetch_data(self) -> Optional[Dict[str, Any]]:
# # #         """
# # #         Fetch LEAP IPO data from NSE API
        
# # #         Returns:
# # #             Dictionary with extracted data or None if failed
# # #         """
# # #         try:
# # #             logger.debug("Fetching LEAP IPO data...")
            
# # #             # Get data from API
# # #             response = self.session.get(
# # #                 self.API_URL,
# # #                 timeout=30
# # #             )
            
# # #             if response.status_code != 200:
# # #                 logger.error(f"API returned status {response.status_code}")
# # #                 return None
            
# # #             data = response.json()
            
# # #             # Get data items
# # #             items = data.get('dataList', [])
            
# # #             if not items:
# # #                 logger.warning("No dataList found in response")
# # #                 return None
            
# # #             # Skip the header row
# # #             if len(items) > 0 and items[0].get('category') == 'Category':
# # #                 items = items[1:]
            
# # #             # Find QIB data (srNo = 1)
# # #             qib_data = None
# # #             for item in items:
# # #                 if item.get('srNo') == '1' or item.get('srNo') == 1:
# # #                     qib_data = item
# # #                     break
            
# # #             if not qib_data:
# # #                 logger.warning("QIB data not found in response")
# # #                 return None
            
# # #             # Extract QIB data
# # #             category = qib_data.get('category', 'Qualified Institutional Buyers(QIBs)')
# # #             no_of_shares_offered = self._safe_int_convert(qib_data.get('noOfShareOffered', 0))
# # #             no_of_shares_bid = self._safe_int_convert(qib_data.get('noOfSharesBid', 0))
# # #             no_of_times_total_meant = self._safe_float_convert(qib_data.get('noOfTotalMeant', 0))
            
# # #             # Update counter only if value changed and >= 5
# # #             current_value = no_of_times_total_meant
            
# # #             if current_value >= 5.0:
# # #                 if self.last_qib_value is None or current_value != self.last_qib_value:
# # #                     self.counter += 1
# # #                     logger.info(f"🎯 QIB subscription {current_value:.2f}x >= 5x! Count: {self.counter}")
            
# # #             # Update last value
# # #             self.last_qib_value = current_value
            
# # #             # Get update time
# # #             update_time = data.get('updateTime', '')
            
# # #             result = {
# # #                 'timestamp': datetime.now().isoformat(),
# # #                 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# # #                 'update_time': update_time,
# # #                 'category': category,
# # #                 'no_of_shares_offered': no_of_shares_offered,
# # #                 'no_of_shares_bid': no_of_shares_bid,
# # #                 'no_of_times_total_meant': no_of_times_total_meant,
# # #                 'counter': self.counter
# # #             }
            
# # #             logger.info(f"QIB: {no_of_times_total_meant:.2f}x | Shares Offered: {no_of_shares_offered:,} | Bid: {no_of_shares_bid:,} | Counter: {self.counter}")
# # #             return result
            
# # #         except requests.exceptions.RequestException as e:
# # #             logger.error(f"Network error: {e}")
# # #             return None
# # #         except json.JSONDecodeError as e:
# # #             logger.error(f"JSON parsing error: {e}")
# # #             return None
# # #         except Exception as e:
# # #             logger.error(f"Error fetching data: {e}")
# # #             return None
    
# # #     def append_to_csv(self, data: Dict[str, Any]):
# # #         """
# # #         Append data to CSV file
        
# # #         Args:
# # #             data: Data dictionary to append
# # #         """
# # #         try:
# # #             row = [
# # #                 data['timestamp'],
# # #                 data['datetime'],
# # #                 data['update_time'],
# # #                 data['category'],
# # #                 data['no_of_shares_offered'],
# # #                 data['no_of_shares_bid'],
# # #                 data['no_of_times_total_meant'],
# # #                 data['counter']
# # #             ]
            
# # #             # Append to CSV
# # #             with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
# # #                 writer = csv.writer(f)
# # #                 writer.writerow(row)
            
# # #             logger.debug(f"Appended data to CSV: {data['datetime']}")
            
# # #         except Exception as e:
# # #             logger.error(f"Error appending to CSV: {e}")
    
# # #     def run(self):
# # #         """
# # #         Run the monitoring loop
# # #         """
# # #         logger.info("=" * 60)
# # #         logger.info("LEAP IPO Real-time Monitor Started")
# # #         logger.info("=" * 60)
# # #         logger.info(f"Monitoring: LEAP IPO Subscription Data")
# # #         logger.info(f"Output file: {self.csv_path}")
# # #         logger.info(f"Refresh interval: {self.interval_seconds} seconds")
# # #         logger.info(f"Tracking QIB >= 5x counter")
# # #         logger.info("Press Ctrl+C to stop")
# # #         logger.info("=" * 60)
        
# # #         # Initialize session
# # #         self._init_session()
        
# # #         iteration = 0
        
# # #         try:
# # #             while True:
# # #                 iteration += 1
# # #                 logger.debug(f"\n--- Iteration {iteration} ---")
                
# # #                 # Fetch data
# # #                 data = self.fetch_data()
                
# # #                 if data:
# # #                     # Display current subscription
# # #                     logger.info(f"[{data['datetime']}] QIB: {data['no_of_times_total_meant']:.2f}x | Counter: {data['counter']}")
                    
# # #                     # Append to CSV
# # #                     self.append_to_csv(data)
# # #                 else:
# # #                     logger.warning("Failed to fetch data, retrying...")
                
# # #                 # Wait for next interval
# # #                 if iteration > 0:
# # #                     logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
# # #                     time.sleep(self.interval_seconds)
                    
# # #         except KeyboardInterrupt:
# # #             logger.info("\nMonitoring stopped by user")
# # #             self._print_summary()
# # #         except Exception as e:
# # #             logger.error(f"Unexpected error: {e}")
# # #             self._print_summary()
    
# # #     def _print_summary(self):
# # #         """Print summary of collected data"""
# # #         try:
# # #             if not self.csv_path.exists():
# # #                 logger.info("No data collected")
# # #                 return
            
# # #             df = pd.read_csv(self.csv_path)
            
# # #             if df.empty:
# # #                 logger.info("No data collected")
# # #                 return
            
# # #             logger.info("\n" + "=" * 60)
# # #             logger.info("Monitoring Summary")
# # #             logger.info("=" * 60)
# # #             logger.info(f"Total records: {len(df)}")
# # #             logger.info(f"First record: {df.iloc[0]['datetime']}")
# # #             logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
# # #             # Latest data
# # #             latest = df.iloc[-1]
# # #             logger.info(f"\nLatest QIB Data:")
# # #             logger.info(f"  Category: {latest['category']}")
# # #             logger.info(f"  Shares Offered: {latest['no_of_shares_offered']:,.0f}")
# # #             logger.info(f"  Shares Bid: {latest['no_of_shares_bid']:,.0f}")
# # #             logger.info(f"  Subscription: {latest['no_of_times_total_meant']:.2f}x")
# # #             logger.info(f"  Counter (>=5x): {latest['counter']}")
            
# # #             # Calculate changes
# # #             if len(df) > 1:
# # #                 first = df.iloc[0]
# # #                 qib_change = latest['no_of_times_total_meant'] - first['no_of_times_total_meant']
# # #                 bid_change = latest['no_of_shares_bid'] - first['no_of_shares_bid']
                
# # #                 logger.info(f"\nChange from first to latest:")
# # #                 logger.info(f"  Subscription: {qib_change:+.2f}x")
# # #                 logger.info(f"  Shares Bid: {bid_change:+,.0f}")
            
# # #             # Max and min
# # #             max_qib = df['no_of_times_total_meant'].max()
# # #             min_qib = df['no_of_times_total_meant'].min()
            
# # #             logger.info(f"\nQIB Subscription Range:")
# # #             logger.info(f"  Max: {max_qib:.2f}x")
# # #             logger.info(f"  Min: {min_qib:.2f}x")
            
# # #             logger.info(f"\nFinal Counter Value: {df.iloc[-1]['counter']}")
            
# # #             logger.info(f"\nData saved to: {self.csv_path}")
# # #             logger.info("=" * 60)
            
# # #         except Exception as e:
# # #             logger.error(f"Error generating summary: {e}")


# # # def main():
# # #     """Main execution function"""
# # #     import argparse
    
# # #     parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
# # #     parser.add_argument('--interval', type=int, default=120, 
# # #                        help='Refresh interval in seconds (default: 120)')
# # #     parser.add_argument('--once', action='store_true',
# # #                        help='Fetch once and exit')
# # #     parser.add_argument('--output', type=str, default=None,
# # #                        help='Output directory for CSV files')
    
# # #     args = parser.parse_args()
    
# # #     # Setup logger
# # #     setup_logger()
    
# # #     # Set output directory
# # #     output_dir = Path(args.output) if args.output else None
    
# # #     # Initialize monitor
# # #     monitor = LEAPIPOMonitor(
# # #         output_dir=output_dir,
# # #         interval_seconds=args.interval
# # #     )
    
# # #     # Handle one-time fetch
# # #     if args.once:
# # #         data = monitor.fetch_data()
# # #         if data:
# # #             monitor.append_to_csv(data)
# # #             logger.success("Data fetched and saved")
# # #             print(json.dumps(data, indent=2))
# # #         return
    
# # #     # Run continuous monitoring
# # #     monitor.run()


# # # if __name__ == "__main__":
# # #     main()

# # # monitor_leap_ipo.py - Fixed version

# # """
# # Real-time monitor for LEAP IPO subscription data from NSE API
# # """
# # import sys
# # import json
# # import time
# # import csv
# # import requests
# # from pathlib import Path
# # from datetime import datetime
# # from loguru import logger
# # import pandas as pd
# # from typing import Optional, Dict, Any

# # # Add src to path
# # sys.path.insert(0, str(Path(__file__).parent))

# # from src.config import DATA_DIR
# # from src.utils import setup_logger


# # class LEAPIPOMonitor:
# #     """Real-time monitor for LEAP IPO subscription data"""
    
# #     # NSE API endpoint
# #     API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
# #     # Headers to mimic browser
# #     HEADERS = {
# #         'accept': '*/*',
# #         'accept-language': 'en-US,en;q=0.9',
# #         'dnt': '1',
# #         'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
# #         'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
# #         'sec-ch-ua-mobile': '?0',
# #         'sec-ch-ua-platform': '"Windows"',
# #         'sec-fetch-dest': 'empty',
# #         'sec-fetch-mode': 'cors',
# #         'sec-fetch-site': 'same-origin',
# #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
# #     }
    
# #     def __init__(self, output_dir: Path = None, interval_seconds: int = 300):
# #         """
# #         Initialize the monitor
        
# #         Args:
# #             output_dir: Directory to save CSV files
# #             interval_seconds: Refresh interval in seconds (default: 300 = 5 minutes)
# #         """
# #         self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
# #         self.output_dir.mkdir(parents=True, exist_ok=True)
# #         self.interval_seconds = interval_seconds
# #         self.session = requests.Session()
# #         self.session.headers.update(self.HEADERS)
        
# #         # CSV file path
# #         self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
# #         # Initialize CSV with headers if it doesn't exist
# #         self._initialize_csv()
        
# #         logger.info(f"LEAP IPO Monitor initialized")
# #         logger.info(f"CSV file: {self.csv_path}")
# #         logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
# #     def _initialize_csv(self):
# #         """Initialize CSV file with headers"""
# #         headers = [
# #             'timestamp',
# #             'datetime',
# #             'update_time',
# #             'qib_category',
# #             'qib_no_of_share_offered',
# #             'qib_no_of_shares_bid',
# #             'qib_subscription_times',
# #             'nii_no_of_share_offered',
# #             'nii_no_of_shares_bid',
# #             'nii_subscription_times',
# #             'rii_no_of_share_offered',
# #             'rii_no_of_shares_bid',
# #             'rii_subscription_times',
# #             'total_no_of_share_offered',
# #             'total_no_of_shares_bid',
# #             'total_subscription_times',
# #             'api_response_raw'
# #         ]
        
# #         if not self.csv_path.exists():
# #             with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
# #                 writer = csv.writer(f)
# #                 writer.writerow(headers)
# #             logger.debug(f"Created CSV file: {self.csv_path}")
    
# #     def _init_session(self):
# #         """Initialize session with NSE to get cookies"""
# #         try:
# #             # First visit main page
# #             self.session.get("https://www.nseindia.com", timeout=30)
# #             logger.debug("Session initialized with NSE")
# #         except Exception as e:
# #             logger.warning(f"Failed to initialize session: {e}")
    
# #     def _safe_int_convert(self, value):
# #         """Safely convert string to int, handling empty strings and non-numeric values"""
# #         if not value or value == '' or value == 'null':
# #             return 0
# #         try:
# #             # Remove commas if present
# #             cleaned = str(value).replace(',', '').strip()
# #             return int(float(cleaned)) if cleaned else 0
# #         except (ValueError, TypeError):
# #             return 0
    
# #     def _safe_float_convert(self, value):
# #         """Safely convert string to float, handling empty strings and non-numeric values"""
# #         if not value or value == '' or value == 'null':
# #             return 0.0
# #         try:
# #             cleaned = str(value).replace(',', '').strip()
# #             return float(cleaned) if cleaned else 0.0
# #         except (ValueError, TypeError):
# #             return 0.0
    
# #     def fetch_data(self) -> Optional[Dict[str, Any]]:
# #         """
# #         Fetch LEAP IPO data from NSE API
        
# #         Returns:
# #             Dictionary with extracted data or None if failed
# #         """
# #         try:
# #             logger.debug("Fetching LEAP IPO data...")
            
# #             # Get data from API
# #             response = self.session.get(
# #                 self.API_URL,
# #                 timeout=30
# #             )
            
# #             if response.status_code != 200:
# #                 logger.error(f"API returned status {response.status_code}")
# #                 logger.debug(f"Response: {response.text[:200]}")
# #                 return None
            
# #             data = response.json()
            
# #             # Debug: Print the structure
# #             logger.debug(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
# #             # Get data items - the API uses 'dataList' field
# #             items = data.get('dataList', [])
            
# #             if not items:
# #                 logger.warning("No dataList found in response")
# #                 return None
            
# #             # Skip the first item (it's the header row)
# #             if len(items) > 0 and items[0].get('category') == 'Category':
# #                 items = items[1:]
            
# #             # Extract data by category
# #             qib_data = None
# #             nii_data = None
# #             rii_data = None
# #             total_data = None
            
# #             for item in items:
# #                 category = item.get('category', '')
                
# #                 # Extract QIB data
# #                 if 'Qualified Institutional' in category or category == 'QIBs':
# #                     qib_data = {
# #                         'category': category,
# #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# #                     }
                
# #                 # Extract NII data
# #                 elif 'Non Institutional Investors' in category and 'Bid amount of more than Ten Lakh' in category:
# #                     nii_data = {
# #                         'category': category,
# #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# #                     }
                
# #                 # Extract RII data
# #                 elif 'Retail Individual Investors' in category:
# #                     rii_data = {
# #                         'category': category,
# #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# #                     }
                
# #                 # Extract Total data
# #                 elif category == 'Total':
# #                     total_data = {
# #                         'category': category,
# #                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# #                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# #                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# #                     }
            
# #             # If QIB not found, try to find by srNo
# #             if not qib_data:
# #                 for item in items:
# #                     if item.get('srNo') == '1' or item.get('srNo') == 1:
# #                         qib_data = {
# #                             'category': item.get('category', 'QIB'),
# #                             'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
# #                             'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
# #                             'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
# #                         }
# #                         break
            
# #             if not qib_data:
# #                 logger.warning("QIB data not found in response")
# #                 return None
            
# #             # Get update time
# #             update_time = data.get('updateTime', '')
            
# #             # Calculate totals if not available
# #             if total_data:
# #                 total_offered = total_data['no_of_share_offered']
# #                 total_bid = total_data['no_of_shares_bid']
# #                 total_subscription = total_data['subscription_times']
# #             else:
# #                 # Calculate from individual categories
# #                 total_offered = (
# #                     qib_data.get('no_of_share_offered', 0) +
# #                     (nii_data.get('no_of_share_offered', 0) if nii_data else 0) +
# #                     (rii_data.get('no_of_share_offered', 0) if rii_data else 0)
# #                 )
# #                 total_bid = (
# #                     qib_data.get('no_of_shares_bid', 0) +
# #                     (nii_data.get('no_of_shares_bid', 0) if nii_data else 0) +
# #                     (rii_data.get('no_of_shares_bid', 0) if rii_data else 0)
# #                 )
# #                 total_subscription = total_bid / total_offered if total_offered > 0 else 0
            
# #             result = {
# #                 'timestamp': datetime.now().isoformat(),
# #                 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
# #                 'update_time': update_time,
# #                 'qib_category': qib_data['category'],
# #                 'qib_no_of_share_offered': qib_data['no_of_share_offered'],
# #                 'qib_no_of_shares_bid': qib_data['no_of_shares_bid'],
# #                 'qib_subscription_times': qib_data['subscription_times'],
# #                 'nii_no_of_share_offered': nii_data['no_of_share_offered'] if nii_data else 0,
# #                 'nii_no_of_shares_bid': nii_data['no_of_shares_bid'] if nii_data else 0,
# #                 'nii_subscription_times': nii_data['subscription_times'] if nii_data else 0,
# #                 'rii_no_of_share_offered': rii_data['no_of_share_offered'] if rii_data else 0,
# #                 'rii_no_of_shares_bid': rii_data['no_of_shares_bid'] if rii_data else 0,
# #                 'rii_subscription_times': rii_data['subscription_times'] if rii_data else 0,
# #                 'total_no_of_share_offered': total_offered,
# #                 'total_no_of_shares_bid': total_bid,
# #                 'total_subscription_times': total_subscription,
# #                 'api_response_raw': json.dumps(data)
# #             }
            
# #             logger.info(f"QIB: {qib_data['subscription_times']:.2f}x | NII: {(nii_data['subscription_times'] if nii_data else 0):.2f}x | RII: {(rii_data['subscription_times'] if rii_data else 0):.2f}x | Total: {total_subscription:.2f}x")
# #             return result
            
# #         except requests.exceptions.RequestException as e:
# #             logger.error(f"Network error: {e}")
# #             return None
# #         except json.JSONDecodeError as e:
# #             logger.error(f"JSON parsing error: {e}")
# #             logger.debug(f"Response: {response.text[:200]}")
# #             return None
# #         except Exception as e:
# #             logger.error(f"Error fetching data: {e}")
# #             import traceback
# #             logger.debug(traceback.format_exc())
# #             return None
    
# #     def append_to_csv(self, data: Dict[str, Any]):
# #         """
# #         Append data to CSV file
        
# #         Args:
# #             data: Data dictionary to append
# #         """
# #         try:
# #             with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
# #                 writer = csv.writer(f)
# #                 row = [
# #                     data['timestamp'],
# #                     data['datetime'],
# #                     data['update_time'],
# #                     data['qib_category'],
# #                     data['qib_no_of_share_offered'],
# #                     data['qib_no_of_shares_bid'],
# #                     data['qib_subscription_times'],
# #                     data['nii_no_of_share_offered'],
# #                     data['nii_no_of_shares_bid'],
# #                     data['nii_subscription_times'],
# #                     data['rii_no_of_share_offered'],
# #                     data['rii_no_of_shares_bid'],
# #                     data['rii_subscription_times'],
# #                     data['total_no_of_share_offered'],
# #                     data['total_no_of_shares_bid'],
# #                     data['total_subscription_times'],
# #                     data['api_response_raw']
# #                 ]
# #                 writer.writerow(row)
            
# #             logger.debug(f"Appended data to CSV: {data['datetime']}")
            
# #         except Exception as e:
# #             logger.error(f"Error appending to CSV: {e}")
    
# #     def run(self):
# #         """
# #         Run the monitoring loop
# #         """
# #         logger.info("=" * 60)
# #         logger.info("LEAP IPO Real-time Monitor Started")
# #         logger.info("=" * 60)
# #         logger.info(f"Monitoring: LEAP IPO Subscription Data")
# #         logger.info(f"Output file: {self.csv_path}")
# #         logger.info(f"Refresh interval: {self.interval_seconds} seconds")
# #         logger.info("Press Ctrl+C to stop")
# #         logger.info("=" * 60)
        
# #         # Initialize session
# #         self._init_session()
        
# #         iteration = 0
        
# #         try:
# #             while True:
# #                 iteration += 1
# #                 logger.debug(f"\n--- Iteration {iteration} ---")
                
# #                 # Fetch data
# #                 data = self.fetch_data()
                
# #                 if data:
# #                     # Display current subscription
# #                     logger.info(f"[{data['datetime']}] QIB: {data['qib_subscription_times']:.2f}x | Total: {data['total_subscription_times']:.2f}x")
                    
# #                     # Append to CSV
# #                     self.append_to_csv(data)
# #                 else:
# #                     logger.warning("Failed to fetch data, retrying...")
                
# #                 # Wait for next interval
# #                 if iteration > 0:
# #                     logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
# #                     time.sleep(self.interval_seconds)
                    
# #         except KeyboardInterrupt:
# #             logger.info("\nMonitoring stopped by user")
# #             self._print_summary()
# #         except Exception as e:
# #             logger.error(f"Unexpected error: {e}")
# #             self._print_summary()
    
# #     def _print_summary(self):
# #         """Print summary of collected data"""
# #         try:
# #             if not self.csv_path.exists():
# #                 logger.info("No data collected")
# #                 return
            
# #             df = pd.read_csv(self.csv_path)
            
# #             if df.empty:
# #                 logger.info("No data collected")
# #                 return
            
# #             logger.info("\n" + "=" * 60)
# #             logger.info("Monitoring Summary")
# #             logger.info("=" * 60)
# #             logger.info(f"Total records: {len(df)}")
# #             logger.info(f"First record: {df.iloc[0]['datetime']}")
# #             logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
# #             # Latest subscription
# #             latest = df.iloc[-1]
# #             logger.info(f"\nLatest Subscriptions:")
# #             logger.info(f"  QIB: {latest['qib_subscription_times']:.2f}x")
# #             logger.info(f"  Total: {latest['total_subscription_times']:.2f}x")
            
# #             # Calculate changes
# #             if len(df) > 1:
# #                 first = df.iloc[0]
# #                 qib_change = latest['qib_subscription_times'] - first['qib_subscription_times']
# #                 total_change = latest['total_subscription_times'] - first['total_subscription_times']
                
# #                 logger.info(f"\nChange from first to latest:")
# #                 logger.info(f"  QIB: {qib_change:+.2f}x")
# #                 logger.info(f"  Total: {total_change:+.2f}x")
            
# #             # Max and min
# #             max_qib = df['qib_subscription_times'].max()
# #             min_qib = df['qib_subscription_times'].min()
# #             max_total = df['total_subscription_times'].max()
# #             min_total = df['total_subscription_times'].min()
            
# #             logger.info(f"\nQIB Subscription Range:")
# #             logger.info(f"  Max: {max_qib:.2f}x")
# #             logger.info(f"  Min: {min_qib:.2f}x")
            
# #             logger.info(f"\nTotal Subscription Range:")
# #             logger.info(f"  Max: {max_total:.2f}x")
# #             logger.info(f"  Min: {min_total:.2f}x")
            
# #             logger.info(f"\nData saved to: {self.csv_path}")
# #             logger.info("=" * 60)
            
# #         except Exception as e:
# #             logger.error(f"Error generating summary: {e}")
    
# #     def generate_report(self):
# #         """Generate a report from collected data"""
# #         try:
# #             if not self.csv_path.exists():
# #                 logger.warning("No data file found")
# #                 return
            
# #             df = pd.read_csv(self.csv_path)
            
# #             if df.empty:
# #                 logger.warning("No data in file")
# #                 return
            
# #             # Convert datetime
# #             df['datetime'] = pd.to_datetime(df['datetime'])
            
# #             # Create report
# #             report = {
# #                 'total_records': len(df),
# #                 'start_time': df.iloc[0]['datetime'],
# #                 'end_time': df.iloc[-1]['datetime'],
# #                 'duration_hours': (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds() / 3600,
                
# #                 'qib_final': df.iloc[-1]['qib_subscription_times'],
# #                 'qib_start': df.iloc[0]['qib_subscription_times'],
# #                 'qib_change': df.iloc[-1]['qib_subscription_times'] - df.iloc[0]['qib_subscription_times'],
# #                 'qib_max': df['qib_subscription_times'].max(),
# #                 'qib_min': df['qib_subscription_times'].min(),
                
# #                 'total_final': df.iloc[-1]['total_subscription_times'],
# #                 'total_start': df.iloc[0]['total_subscription_times'],
# #                 'total_change': df.iloc[-1]['total_subscription_times'] - df.iloc[0]['total_subscription_times'],
# #                 'total_max': df['total_subscription_times'].max(),
# #                 'total_min': df['total_subscription_times'].min(),
# #             }
            
# #             # Save report
# #             report_path = self.output_dir / f"leap_ipo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
# #             with open(report_path, 'w') as f:
# #                 json.dump(report, f, indent=2, default=str)
            
# #             logger.success(f"Report generated: {report_path}")
            
# #             # Print report
# #             logger.info("\n" + "=" * 60)
# #             logger.info("LEAP IPO Subscription Report")
# #             logger.info("=" * 60)
# #             logger.info(f"Records: {report['total_records']}")
# #             logger.info(f"Duration: {report['duration_hours']:.2f} hours")
# #             logger.info(f"QIB Subscription: {report['qib_final']:.2f}x")
# #             logger.info(f"QIB Change: {report['qib_change']:+.2f}x")
# #             logger.info(f"Total Subscription: {report['total_final']:.2f}x")
# #             logger.info(f"Total Change: {report['total_change']:+.2f}x")
# #             logger.info("=" * 60)
            
# #             return report
            
# #         except Exception as e:
# #             logger.error(f"Error generating report: {e}")
# #             return None


# # def main():
# #     """Main execution function"""
# #     import argparse
    
# #     parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
# #     parser.add_argument('--interval', type=int, default=300, 
# #                        help='Refresh interval in seconds (default: 300)')
# #     parser.add_argument('--once', action='store_true',
# #                        help='Fetch once and exit')
# #     parser.add_argument('--report', action='store_true',
# #                        help='Generate report from existing data and exit')
# #     parser.add_argument('--output', type=str, default=None,
# #                        help='Output directory for CSV files')
    
# #     args = parser.parse_args()
    
# #     # Setup logger
# #     setup_logger()
    
# #     # Set output directory
# #     output_dir = Path(args.output) if args.output else None
    
# #     # Initialize monitor
# #     monitor = LEAPIPOMonitor(
# #         output_dir=output_dir,
# #         interval_seconds=args.interval
# #     )
    
# #     # Handle report generation
# #     if args.report:
# #         monitor.generate_report()
# #         return
    
# #     # Handle one-time fetch
# #     if args.once:
# #         data = monitor.fetch_data()
# #         if data:
# #             monitor.append_to_csv(data)
# #             logger.success("Data fetched and saved")
# #             print(json.dumps(data, indent=2))
# #         return
    
# #     # Run continuous monitoring
# #     monitor.run()


# # if __name__ == "__main__":
# #     main()

# # monitor_leap_ipo.py - Updated with change detection

# """
# Real-time monitor for LEAP IPO subscription data from NSE API
# """
# import sys
# import json
# import time
# import csv
# import requests
# from pathlib import Path
# from datetime import datetime
# from loguru import logger
# import pandas as pd
# from typing import Optional, Dict, Any

# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent))

# from src.config import DATA_DIR
# from src.utils import setup_logger


# class LEAPIPOMonitor:
#     """Real-time monitor for LEAP IPO subscription data"""
    
#     # NSE API endpoint
#     API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
#     # Headers to mimic browser
#     HEADERS = {
#         'accept': '*/*',
#         'accept-language': 'en-US,en;q=0.9',
#         'dnt': '1',
#         'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
#         'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#         'sec-fetch-dest': 'empty',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'same-origin',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
#     }
    
#     def __init__(self, output_dir: Path = None, interval_seconds: int = 300):
#         """
#         Initialize the monitor
        
#         Args:
#             output_dir: Directory to save CSV files
#             interval_seconds: Refresh interval in seconds (default: 300 = 5 minutes)
#         """
#         self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#         self.interval_seconds = interval_seconds
#         self.session = requests.Session()
#         self.session.headers.update(self.HEADERS)
        
#         # CSV file path
#         self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
#         # Last recorded data for change detection
#         self.last_data = None
#         self.last_update_time = None
#         self.last_qib_subscription = None
#         self.last_total_subscription = None
        
#         # Initialize CSV with headers if it doesn't exist
#         self._initialize_csv()
        
#         # Load last record if exists
#         self._load_last_record()
        
#         logger.info(f"LEAP IPO Monitor initialized")
#         logger.info(f"CSV file: {self.csv_path}")
#         logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
#     def _initialize_csv(self):
#         """Initialize CSV file with headers"""
#         headers = [
#             'timestamp',
#             'datetime',
#             'update_time',
#             'qib_category',
#             'qib_no_of_share_offered',
#             'qib_no_of_shares_bid',
#             'qib_subscription_times',
#             'nii_no_of_share_offered',
#             'nii_no_of_shares_bid',
#             'nii_subscription_times',
#             'rii_no_of_share_offered',
#             'rii_no_of_shares_bid',
#             'rii_subscription_times',
#             'total_no_of_share_offered',
#             'total_no_of_shares_bid',
#             'total_subscription_times',
#             'api_response_raw'
#         ]
        
#         if not self.csv_path.exists():
#             with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(headers)
#             logger.debug(f"Created CSV file: {self.csv_path}")
    
#     def _load_last_record(self):
#         """Load the last recorded data for change detection"""
#         try:
#             if not self.csv_path.exists():
#                 return
            
#             df = pd.read_csv(self.csv_path)
            
#             if df.empty:
#                 return
            
#             last_row = df.iloc[-1]
            
#             self.last_update_time = last_row.get('update_time', '')
#             self.last_qib_subscription = float(last_row.get('qib_subscription_times', 0))
#             self.last_total_subscription = float(last_row.get('total_subscription_times', 0))
            
#             logger.debug(f"Loaded last record: update_time={self.last_update_time}, qib={self.last_qib_subscription:.2f}x, total={self.last_total_subscription:.2f}x")
            
#         except Exception as e:
#             logger.debug(f"Could not load last record: {e}")
    
#     def _init_session(self):
#         """Initialize session with NSE to get cookies"""
#         try:
#             # First visit main page
#             self.session.get("https://www.nseindia.com", timeout=30)
#             logger.debug("Session initialized with NSE")
#         except Exception as e:
#             logger.warning(f"Failed to initialize session: {e}")
    
#     def _safe_int_convert(self, value):
#         """Safely convert string to int, handling empty strings and non-numeric values"""
#         if not value or value == '' or value == 'null':
#             return 0
#         try:
#             # Remove commas if present
#             cleaned = str(value).replace(',', '').strip()
#             return int(float(cleaned)) if cleaned else 0
#         except (ValueError, TypeError):
#             return 0
    
#     def _safe_float_convert(self, value):
#         """Safely convert string to float, handling empty strings and non-numeric values"""
#         if not value or value == '' or value == 'null':
#             return 0.0
#         try:
#             cleaned = str(value).replace(',', '').strip()
#             return float(cleaned) if cleaned else 0.0
#         except (ValueError, TypeError):
#             return 0.0
    
#     def _has_data_changed(self, new_data: Dict[str, Any]) -> bool:
#         """
#         Check if the data has changed compared to last recorded data
        
#         Args:
#             new_data: New data dictionary
            
#         Returns:
#             True if data has changed, False otherwise
#         """
#         # Get new values
#         new_update_time = new_data.get('update_time', '')
#         new_qib = new_data.get('qib_subscription_times', 0)
#         new_total = new_data.get('total_subscription_times', 0)
        
#         # Check if update_time is different (most reliable)
#         if self.last_update_time and new_update_time != self.last_update_time:
#             logger.debug(f"Update time changed: {self.last_update_time} -> {new_update_time}")
#             return True
        
#         # Check if QIB subscription changed significantly (more than 0.001x)
#         if self.last_qib_subscription is not None:
#             qib_diff = abs(new_qib - self.last_qib_subscription)
#             if qib_diff > 0.001:  # Only record if change is significant
#                 logger.debug(f"QIB subscription changed: {self.last_qib_subscription:.2f}x -> {new_qib:.2f}x (diff: {qib_diff:.3f}x)")
#                 return True
        
#         # Check if Total subscription changed significantly
#         if self.last_total_subscription is not None:
#             total_diff = abs(new_total - self.last_total_subscription)
#             if total_diff > 0.001:
#                 logger.debug(f"Total subscription changed: {self.last_total_subscription:.2f}x -> {new_total:.2f}x (diff: {total_diff:.3f}x)")
#                 return True
        
#         # Check if it's the first record
#         if self.last_update_time is None:
#             logger.debug("First record, saving...")
#             return True
        
#         # No significant changes detected
#         return False
    
#     def fetch_data(self) -> Optional[Dict[str, Any]]:
#         """
#         Fetch LEAP IPO data from NSE API
        
#         Returns:
#             Dictionary with extracted data or None if failed
#         """
#         try:
#             logger.debug("Fetching LEAP IPO data...")
            
#             # Get data from API
#             response = self.session.get(
#                 self.API_URL,
#                 timeout=30
#             )
            
#             if response.status_code != 200:
#                 logger.error(f"API returned status {response.status_code}")
#                 logger.debug(f"Response: {response.text[:200]}")
#                 return None
            
#             data = response.json()
            
#             # Get data items - the API uses 'dataList' field
#             items = data.get('dataList', [])
            
#             if not items:
#                 logger.warning("No dataList found in response")
#                 return None
            
#             # Skip the first item (it's the header row)
#             if len(items) > 0 and items[0].get('category') == 'Category':
#                 items = items[1:]
            
#             # Extract data by category
#             qib_data = None
#             nii_data = None
#             rii_data = None
#             total_data = None
            
#             for item in items:
#                 category = item.get('category', '')
                
#                 # Extract QIB data
#                 if 'Qualified Institutional' in category or category == 'QIBs':
#                     qib_data = {
#                         'category': category,
#                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
#                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
#                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
#                     }
                
#                 # Extract NII data (the main NII category with the total)
#                 elif 'Non Institutional Investors' in category and 'Bid amount of more than Ten Lakh' in category and 'upto Ten Lakh' not in category:
#                     nii_data = {
#                         'category': category,
#                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
#                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
#                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
#                     }
                
#                 # Extract RII data
#                 elif 'Retail Individual Investors' in category and 'Cut Off' not in category and 'Price bids' not in category:
#                     rii_data = {
#                         'category': category,
#                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
#                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
#                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
#                     }
                
#                 # Extract Total data
#                 elif category == 'Total':
#                     total_data = {
#                         'category': category,
#                         'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
#                         'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
#                         'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
#                     }
            
#             # If QIB not found, try to find by srNo
#             if not qib_data:
#                 for item in items:
#                     if item.get('srNo') == '1' or item.get('srNo') == 1:
#                         qib_data = {
#                             'category': item.get('category', 'QIB'),
#                             'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
#                             'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
#                             'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
#                         }
#                         break
            
#             if not qib_data:
#                 logger.warning("QIB data not found in response")
#                 return None
            
#             # Get update time
#             update_time = data.get('updateTime', '')
            
#             # Calculate totals if not available
#             if total_data:
#                 total_offered = total_data['no_of_share_offered']
#                 total_bid = total_data['no_of_shares_bid']
#                 total_subscription = total_data['subscription_times']
#             else:
#                 # Calculate from individual categories
#                 total_offered = (
#                     qib_data.get('no_of_share_offered', 0) +
#                     (nii_data.get('no_of_share_offered', 0) if nii_data else 0) +
#                     (rii_data.get('no_of_share_offered', 0) if rii_data else 0)
#                 )
#                 total_bid = (
#                     qib_data.get('no_of_shares_bid', 0) +
#                     (nii_data.get('no_of_shares_bid', 0) if nii_data else 0) +
#                     (rii_data.get('no_of_shares_bid', 0) if rii_data else 0)
#                 )
#                 total_subscription = total_bid / total_offered if total_offered > 0 else 0
            
#             result = {
#                 'timestamp': datetime.now().isoformat(),
#                 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                 'update_time': update_time,
#                 'qib_category': qib_data['category'],
#                 'qib_no_of_share_offered': qib_data['no_of_share_offered'],
#                 'qib_no_of_shares_bid': qib_data['no_of_shares_bid'],
#                 'qib_subscription_times': qib_data['subscription_times'],
#                 'nii_no_of_share_offered': nii_data['no_of_share_offered'] if nii_data else 0,
#                 'nii_no_of_shares_bid': nii_data['no_of_shares_bid'] if nii_data else 0,
#                 'nii_subscription_times': nii_data['subscription_times'] if nii_data else 0,
#                 'rii_no_of_share_offered': rii_data['no_of_share_offered'] if rii_data else 0,
#                 'rii_no_of_shares_bid': rii_data['no_of_shares_bid'] if rii_data else 0,
#                 'rii_subscription_times': rii_data['subscription_times'] if rii_data else 0,
#                 'total_no_of_share_offered': total_offered,
#                 'total_no_of_shares_bid': total_bid,
#                 'total_subscription_times': total_subscription,
#                 'api_response_raw': json.dumps(data)
#             }
            
#             logger.info(f"QIB: {qib_data['subscription_times']:.2f}x | NII: {(nii_data['subscription_times'] if nii_data else 0):.2f}x | RII: {(rii_data['subscription_times'] if rii_data else 0):.2f}x | Total: {total_subscription:.2f}x")
#             return result
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Network error: {e}")
#             return None
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing error: {e}")
#             logger.debug(f"Response: {response.text[:200]}")
#             return None
#         except Exception as e:
#             logger.error(f"Error fetching data: {e}")
#             import traceback
#             logger.debug(traceback.format_exc())
#             return None
    
#     def append_to_csv(self, data: Dict[str, Any]):
#         """
#         Append data to CSV file
        
#         Args:
#             data: Data dictionary to append
#         """
#         try:
#             with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 row = [
#                     data['timestamp'],
#                     data['datetime'],
#                     data['update_time'],
#                     data['qib_category'],
#                     data['qib_no_of_share_offered'],
#                     data['qib_no_of_shares_bid'],
#                     data['qib_subscription_times'],
#                     data['nii_no_of_share_offered'],
#                     data['nii_no_of_shares_bid'],
#                     data['nii_subscription_times'],
#                     data['rii_no_of_share_offered'],
#                     data['rii_no_of_shares_bid'],
#                     data['rii_subscription_times'],
#                     data['total_no_of_share_offered'],
#                     data['total_no_of_shares_bid'],
#                     data['total_subscription_times'],
#                     data['api_response_raw']
#                 ]
#                 writer.writerow(row)
            
#             # Update last recorded values
#             self.last_update_time = data['update_time']
#             self.last_qib_subscription = data['qib_subscription_times']
#             self.last_total_subscription = data['total_subscription_times']
            
#             logger.debug(f"Appended data to CSV: {data['datetime']}")
            
#         except Exception as e:
#             logger.error(f"Error appending to CSV: {e}")
    
#     def run(self):
#         """
#         Run the monitoring loop
#         """
#         logger.info("=" * 60)
#         logger.info("LEAP IPO Real-time Monitor Started")
#         logger.info("=" * 60)
#         logger.info(f"Monitoring: LEAP IPO Subscription Data")
#         logger.info(f"Output file: {self.csv_path}")
#         logger.info(f"Refresh interval: {self.interval_seconds} seconds")
#         logger.info("Only appending when data changes (update_time or subscription values)")
#         logger.info("Press Ctrl+C to stop")
#         logger.info("=" * 60)
        
#         # Initialize session
#         self._init_session()
        
#         iteration = 0
#         no_change_count = 0
        
#         try:
#             while True:
#                 iteration += 1
#                 logger.debug(f"\n--- Iteration {iteration} ---")
                
#                 # Fetch data
#                 data = self.fetch_data()
                
#                 if data:
#                     # Check if data has changed
#                     if self._has_data_changed(data):
#                         # Append to CSV
#                         self.append_to_csv(data)
#                         no_change_count = 0
                        
#                         # Display update
#                         logger.success(f"✓ Recorded: [{data['datetime']}] QIB: {data['qib_subscription_times']:.2f}x | Total: {data['total_subscription_times']:.2f}x")
#                     else:
#                         no_change_count += 1
#                         logger.info(f"⏭ No change detected (update_time: {data.get('update_time', 'N/A')}) - Skipping record (no change count: {no_change_count})")
#                 else:
#                     logger.warning("Failed to fetch data, retrying...")
                
#                 # Wait for next interval
#                 if iteration > 0:
#                     logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
#                     time.sleep(self.interval_seconds)
                    
#         except KeyboardInterrupt:
#             logger.info("\nMonitoring stopped by user")
#             self._print_summary()
#         except Exception as e:
#             logger.error(f"Unexpected error: {e}")
#             self._print_summary()
    
#     def _print_summary(self):
#         """Print summary of collected data"""
#         try:
#             if not self.csv_path.exists():
#                 logger.info("No data collected")
#                 return
            
#             df = pd.read_csv(self.csv_path)
            
#             if df.empty:
#                 logger.info("No data collected")
#                 return
            
#             logger.info("\n" + "=" * 60)
#             logger.info("Monitoring Summary")
#             logger.info("=" * 60)
#             logger.info(f"Total records: {len(df)}")
#             logger.info(f"First record: {df.iloc[0]['datetime']}")
#             logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
#             # Latest subscription
#             latest = df.iloc[-1]
#             logger.info(f"\nLatest Subscriptions:")
#             logger.info(f"  QIB: {latest['qib_subscription_times']:.2f}x")
#             logger.info(f"  Total: {latest['total_subscription_times']:.2f}x")
#             logger.info(f"  Update Time: {latest['update_time']}")
            
#             # Calculate changes
#             if len(df) > 1:
#                 first = df.iloc[0]
#                 qib_change = latest['qib_subscription_times'] - first['qib_subscription_times']
#                 total_change = latest['total_subscription_times'] - first['total_subscription_times']
                
#                 logger.info(f"\nChange from first to latest:")
#                 logger.info(f"  QIB: {qib_change:+.2f}x")
#                 logger.info(f"  Total: {total_change:+.2f}x")
            
#             # Max and min
#             max_qib = df['qib_subscription_times'].max()
#             min_qib = df['qib_subscription_times'].min()
#             max_total = df['total_subscription_times'].max()
#             min_total = df['total_subscription_times'].min()
            
#             logger.info(f"\nQIB Subscription Range:")
#             logger.info(f"  Max: {max_qib:.2f}x")
#             logger.info(f"  Min: {min_qib:.2f}x")
            
#             logger.info(f"\nTotal Subscription Range:")
#             logger.info(f"  Max: {max_total:.2f}x")
#             logger.info(f"  Min: {min_total:.2f}x")
            
#             logger.info(f"\nData saved to: {self.csv_path}")
#             logger.info("=" * 60)
            
#         except Exception as e:
#             logger.error(f"Error generating summary: {e}")
    
#     def generate_report(self):
#         """Generate a report from collected data"""
#         try:
#             if not self.csv_path.exists():
#                 logger.warning("No data file found")
#                 return
            
#             df = pd.read_csv(self.csv_path)
            
#             if df.empty:
#                 logger.warning("No data in file")
#                 return
            
#             # Convert datetime
#             df['datetime'] = pd.to_datetime(df['datetime'])
            
#             # Create report
#             report = {
#                 'total_records': len(df),
#                 'start_time': df.iloc[0]['datetime'],
#                 'end_time': df.iloc[-1]['datetime'],
#                 'duration_hours': (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds() / 3600,
                
#                 'qib_final': df.iloc[-1]['qib_subscription_times'],
#                 'qib_start': df.iloc[0]['qib_subscription_times'],
#                 'qib_change': df.iloc[-1]['qib_subscription_times'] - df.iloc[0]['qib_subscription_times'],
#                 'qib_max': df['qib_subscription_times'].max(),
#                 'qib_min': df['qib_subscription_times'].min(),
                
#                 'total_final': df.iloc[-1]['total_subscription_times'],
#                 'total_start': df.iloc[0]['total_subscription_times'],
#                 'total_change': df.iloc[-1]['total_subscription_times'] - df.iloc[0]['total_subscription_times'],
#                 'total_max': df['total_subscription_times'].max(),
#                 'total_min': df['total_subscription_times'].min(),
#             }
            
#             # Save report
#             report_path = self.output_dir / f"leap_ipo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
#             with open(report_path, 'w') as f:
#                 json.dump(report, f, indent=2, default=str)
            
#             logger.success(f"Report generated: {report_path}")
            
#             # Print report
#             logger.info("\n" + "=" * 60)
#             logger.info("LEAP IPO Subscription Report")
#             logger.info("=" * 60)
#             logger.info(f"Records: {report['total_records']}")
#             logger.info(f"Duration: {report['duration_hours']:.2f} hours")
#             logger.info(f"QIB Subscription: {report['qib_final']:.2f}x")
#             logger.info(f"QIB Change: {report['qib_change']:+.2f}x")
#             logger.info(f"Total Subscription: {report['total_final']:.2f}x")
#             logger.info(f"Total Change: {report['total_change']:+.2f}x")
#             logger.info("=" * 60)
            
#             return report
            
#         except Exception as e:
#             logger.error(f"Error generating report: {e}")
#             return None


# def main():
#     """Main execution function"""
#     import argparse
    
#     parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
#     parser.add_argument('--interval', type=int, default=300, 
#                        help='Refresh interval in seconds (default: 300)')
#     parser.add_argument('--once', action='store_true',
#                        help='Fetch once and exit (will save even if no change)')
#     parser.add_argument('--report', action='store_true',
#                        help='Generate report from existing data and exit')
#     parser.add_argument('--output', type=str, default=None,
#                        help='Output directory for CSV files')
    
#     args = parser.parse_args()
    
#     # Setup logger
#     setup_logger()
    
#     # Set output directory
#     output_dir = Path(args.output) if args.output else None
    
#     # Initialize monitor
#     monitor = LEAPIPOMonitor(
#         output_dir=output_dir,
#         interval_seconds=args.interval
#     )
    
#     # Handle report generation
#     if args.report:
#         monitor.generate_report()
#         return
    
#     # Handle one-time fetch
#     if args.once:
#         data = monitor.fetch_data()
#         if data:
#             # Force append even if no change (for testing)
#             monitor.append_to_csv(data)
#             logger.success("Data fetched and saved")
#             print(json.dumps(data, indent=2))
#         return
    
#     # Run continuous monitoring
#     monitor.run()


# if __name__ == "__main__":
#     main()

# monitor_leap_ipo.py - Updated with 5x counter logic

"""
Real-time monitor for LEAP IPO subscription data from NSE API
"""
import sys
import json
import time
import csv
import requests
from pathlib import Path
from datetime import datetime
from loguru import logger
import pandas as pd
from typing import Optional, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import DATA_DIR
from src.utils import setup_logger


class LEAPIPOMonitor:
    """Real-time monitor for LEAP IPO subscription data"""
    
    # NSE API endpoint
    API_URL = "https://www.nseindia.com/api/ipo-active-category?symbol=LEAP"
    
    # Headers to mimic browser
    HEADERS = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'referer': 'https://www.nseindia.com/market-data/issue-information?symbol=LEAP&series=EQ&type=Active',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
    }
    
    def __init__(self, output_dir: Path = None, interval_seconds: int = 300):
        """
        Initialize the monitor
        
        Args:
            output_dir: Directory to save CSV files
            interval_seconds: Refresh interval in seconds (default: 300 = 5 minutes)
        """
        self.output_dir = output_dir or DATA_DIR / "leap_ipo_monitor"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.interval_seconds = interval_seconds
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
        # CSV file path
        self.csv_path = self.output_dir / f"leap_ipo_subscription_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Last recorded data for change detection
        self.last_data = None
        self.last_update_time = None
        self.last_qib_subscription = None
        self.last_total_subscription = None
        
        # Counter for tracking times QIB > 5x
        self.qib_above_5x_counter = 0  # Total count of times QIB > 5x
        self.qib_above_5x_consecutive = 0  # Consecutive times QIB > 5x
        self.qib_above_5x_previous = False  # Previous state
        
        # Initialize CSV with headers if it doesn't exist
        self._initialize_csv()
        
        # Load last record if exists
        self._load_last_record()
        
        logger.info(f"LEAP IPO Monitor initialized")
        logger.info(f"CSV file: {self.csv_path}")
        logger.info(f"Refresh interval: {interval_seconds} seconds ({interval_seconds/60:.1f} minutes)")
    
    def _initialize_csv(self):
        """Initialize CSV file with headers"""
        headers = [
            'timestamp',
            'datetime',
            'update_time',
            'qib_category',
            'qib_no_of_share_offered',
            'qib_no_of_shares_bid',
            'qib_subscription_times',
            'qib_above_5x_counter',
            'qib_above_5x_consecutive',
            'nii_no_of_share_offered',
            'nii_no_of_shares_bid',
            'nii_subscription_times',
            'rii_no_of_share_offered',
            'rii_no_of_shares_bid',
            'rii_subscription_times',
            'total_no_of_share_offered',
            'total_no_of_shares_bid',
            'total_subscription_times',
            'api_response_raw'
        ]
        
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.debug(f"Created CSV file: {self.csv_path}")
    
    def _load_last_record(self):
        """Load the last recorded data for change detection"""
        try:
            if not self.csv_path.exists():
                return
            
            df = pd.read_csv(self.csv_path)
            
            if df.empty:
                return
            
            last_row = df.iloc[-1]
            
            self.last_update_time = last_row.get('update_time', '')
            self.last_qib_subscription = float(last_row.get('qib_subscription_times', 0))
            self.last_total_subscription = float(last_row.get('total_subscription_times', 0))
            
            # Load counter values if they exist
            if 'qib_above_5x_counter' in df.columns:
                self.qib_above_5x_counter = int(last_row.get('qib_above_5x_counter', 0))
            
            if 'qib_above_5x_consecutive' in df.columns:
                self.qib_above_5x_consecutive = int(last_row.get('qib_above_5x_consecutive', 0))
            
            # Determine previous state
            if self.last_qib_subscription > 5:
                self.qib_above_5x_previous = True
            
            logger.debug(f"Loaded last record: update_time={self.last_update_time}, qib={self.last_qib_subscription:.2f}x, total={self.last_total_subscription:.2f}x")
            logger.debug(f"Counter state: total_above_5x={self.qib_above_5x_counter}, consecutive={self.qib_above_5x_consecutive}")
            
        except Exception as e:
            logger.debug(f"Could not load last record: {e}")
    
    def _init_session(self):
        """Initialize session with NSE to get cookies"""
        try:
            # First visit main page
            self.session.get("https://www.nseindia.com", timeout=30)
            logger.debug("Session initialized with NSE")
        except Exception as e:
            logger.warning(f"Failed to initialize session: {e}")
    
    def _safe_int_convert(self, value):
        """Safely convert string to int, handling empty strings and non-numeric values"""
        if not value or value == '' or value == 'null':
            return 0
        try:
            # Remove commas if present
            cleaned = str(value).replace(',', '').strip()
            return int(float(cleaned)) if cleaned else 0
        except (ValueError, TypeError):
            return 0
    
    def _safe_float_convert(self, value):
        """Safely convert string to float, handling empty strings and non-numeric values"""
        if not value or value == '' or value == 'null':
            return 0.0
        try:
            cleaned = str(value).replace(',', '').strip()
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _update_counter(self, qib_subscription: float) -> tuple:
        """
        Update the counter logic for QIB > 5x
        
        Args:
            qib_subscription: Current QIB subscription times
            
        Returns:
            Tuple of (total_count, consecutive_count)
        """
        is_above_5x = qib_subscription > 5
        
        if is_above_5x:
            # Increment total counter
            self.qib_above_5x_counter += 1
            
            # Update consecutive counter
            if self.qib_above_5x_previous:
                # Already above 5x, increment consecutive
                self.qib_above_5x_consecutive += 1
            else:
                # Just crossed above 5x, start new consecutive count
                self.qib_above_5x_consecutive = 1
            
            # Update previous state
            self.qib_above_5x_previous = True
            
            logger.debug(f"QIB > 5x: total_count={self.qib_above_5x_counter}, consecutive={self.qib_above_5x_consecutive}")
        else:
            # Below 5x, reset consecutive counter
            if self.qib_above_5x_previous:
                # Just dropped below 5x
                self.qib_above_5x_consecutive = 0
                self.qib_above_5x_previous = False
                logger.debug(f"QIB dropped below 5x, resetting consecutive counter")
            else:
                # Already below 5x, maintain state
                self.qib_above_5x_consecutive = 0
        
        return self.qib_above_5x_counter, self.qib_above_5x_consecutive
    
    def _has_data_changed(self, new_data: Dict[str, Any]) -> bool:
        """
        Check if the data has changed compared to last recorded data
        
        Args:
            new_data: New data dictionary
            
        Returns:
            True if data has changed, False otherwise
        """
        # Get new values
        new_update_time = new_data.get('update_time', '')
        new_qib = new_data.get('qib_subscription_times', 0)
        new_total = new_data.get('total_subscription_times', 0)
        
        # Check if update_time is different (most reliable)
        if self.last_update_time and new_update_time != self.last_update_time:
            logger.debug(f"Update time changed: {self.last_update_time} -> {new_update_time}")
            return True
        
        # Check if QIB subscription changed significantly (more than 0.001x)
        if self.last_qib_subscription is not None:
            qib_diff = abs(new_qib - self.last_qib_subscription)
            if qib_diff > 0.001:  # Only record if change is significant
                logger.debug(f"QIB subscription changed: {self.last_qib_subscription:.2f}x -> {new_qib:.2f}x (diff: {qib_diff:.3f}x)")
                return True
        
        # Check if Total subscription changed significantly
        if self.last_total_subscription is not None:
            total_diff = abs(new_total - self.last_total_subscription)
            if total_diff > 0.001:
                logger.debug(f"Total subscription changed: {self.last_total_subscription:.2f}x -> {new_total:.2f}x (diff: {total_diff:.3f}x)")
                return True
        
        # Check if it's the first record
        if self.last_update_time is None:
            logger.debug("First record, saving...")
            return True
        
        # No significant changes detected
        return False
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch LEAP IPO data from NSE API
        
        Returns:
            Dictionary with extracted data or None if failed
        """
        try:
            logger.debug("Fetching LEAP IPO data...")
            
            # Get data from API
            response = self.session.get(
                self.API_URL,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API returned status {response.status_code}")
                logger.debug(f"Response: {response.text[:200]}")
                return None
            
            data = response.json()
            
            # Get data items - the API uses 'dataList' field
            items = data.get('dataList', [])
            
            if not items:
                logger.warning("No dataList found in response")
                return None
            
            # Skip the first item (it's the header row)
            if len(items) > 0 and items[0].get('category') == 'Category':
                items = items[1:]
            
            # Extract data by category
            qib_data = None
            nii_data = None
            rii_data = None
            total_data = None
            
            for item in items:
                category = item.get('category', '')
                
                # Extract QIB data
                if 'Qualified Institutional' in category or category == 'QIBs':
                    qib_data = {
                        'category': category,
                        'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
                        'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
                        'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
                    }
                
                # Extract NII data (the main NII category with the total)
                elif 'Non Institutional Investors' in category and 'Bid amount of more than Ten Lakh' in category and 'upto Ten Lakh' not in category:
                    nii_data = {
                        'category': category,
                        'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
                        'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
                        'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
                    }
                
                # Extract RII data
                elif 'Retail Individual Investors' in category and 'Cut Off' not in category and 'Price bids' not in category:
                    rii_data = {
                        'category': category,
                        'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
                        'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
                        'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
                    }
                
                # Extract Total data
                elif category == 'Total':
                    total_data = {
                        'category': category,
                        'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
                        'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
                        'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
                    }
            
            # If QIB not found, try to find by srNo
            if not qib_data:
                for item in items:
                    if item.get('srNo') == '1' or item.get('srNo') == 1:
                        qib_data = {
                            'category': item.get('category', 'QIB'),
                            'no_of_share_offered': self._safe_int_convert(item.get('noOfShareOffered', 0)),
                            'no_of_shares_bid': self._safe_int_convert(item.get('noOfSharesBid', 0)),
                            'subscription_times': self._safe_float_convert(item.get('noOfTotalMeant', 0))
                        }
                        break
            
            if not qib_data:
                logger.warning("QIB data not found in response")
                return None
            
            # Get update time
            update_time = data.get('updateTime', '')
            
            # Calculate totals if not available
            if total_data:
                total_offered = total_data['no_of_share_offered']
                total_bid = total_data['no_of_shares_bid']
                total_subscription = total_data['subscription_times']
            else:
                # Calculate from individual categories
                total_offered = (
                    qib_data.get('no_of_share_offered', 0) +
                    (nii_data.get('no_of_share_offered', 0) if nii_data else 0) +
                    (rii_data.get('no_of_share_offered', 0) if rii_data else 0)
                )
                total_bid = (
                    qib_data.get('no_of_shares_bid', 0) +
                    (nii_data.get('no_of_shares_bid', 0) if nii_data else 0) +
                    (rii_data.get('no_of_shares_bid', 0) if rii_data else 0)
                )
                total_subscription = total_bid / total_offered if total_offered > 0 else 0
            
            # Update counter
            qib_subscription = qib_data['subscription_times']
            counter_total, counter_consecutive = self._update_counter(qib_subscription)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': update_time,
                'qib_category': qib_data['category'],
                'qib_no_of_share_offered': qib_data['no_of_share_offered'],
                'qib_no_of_shares_bid': qib_data['no_of_shares_bid'],
                'qib_subscription_times': qib_data['subscription_times'],
                'qib_above_5x_counter': counter_total,
                'qib_above_5x_consecutive': counter_consecutive,
                'nii_no_of_share_offered': nii_data['no_of_share_offered'] if nii_data else 0,
                'nii_no_of_shares_bid': nii_data['no_of_shares_bid'] if nii_data else 0,
                'nii_subscription_times': nii_data['subscription_times'] if nii_data else 0,
                'rii_no_of_share_offered': rii_data['no_of_share_offered'] if rii_data else 0,
                'rii_no_of_shares_bid': rii_data['no_of_shares_bid'] if rii_data else 0,
                'rii_subscription_times': rii_data['subscription_times'] if rii_data else 0,
                'total_no_of_share_offered': total_offered,
                'total_no_of_shares_bid': total_bid,
                'total_subscription_times': total_subscription,
                'api_response_raw': json.dumps(data)
            }
            
            # Display status with counter info
            status_emoji = "🔥" if qib_subscription > 5 else "📊"
            logger.info(f"{status_emoji} QIB: {qib_subscription:.2f}x | Total: {total_subscription:.2f}x | 5x Count: {counter_total} | Consecutive: {counter_consecutive}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.debug(f"Response: {response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def append_to_csv(self, data: Dict[str, Any]):
        """
        Append data to CSV file
        
        Args:
            data: Data dictionary to append
        """
        try:
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                row = [
                    data['timestamp'],
                    data['datetime'],
                    data['update_time'],
                    data['qib_category'],
                    data['qib_no_of_share_offered'],
                    data['qib_no_of_shares_bid'],
                    data['qib_subscription_times'],
                    data['qib_above_5x_counter'],
                    data['qib_above_5x_consecutive'],
                    data['nii_no_of_share_offered'],
                    data['nii_no_of_shares_bid'],
                    data['nii_subscription_times'],
                    data['rii_no_of_share_offered'],
                    data['rii_no_of_shares_bid'],
                    data['rii_subscription_times'],
                    data['total_no_of_share_offered'],
                    data['total_no_of_shares_bid'],
                    data['total_subscription_times'],
                    data['api_response_raw']
                ]
                writer.writerow(row)
            
            # Update last recorded values
            self.last_update_time = data['update_time']
            self.last_qib_subscription = data['qib_subscription_times']
            self.last_total_subscription = data['total_subscription_times']
            
            logger.debug(f"Appended data to CSV: {data['datetime']}")
            
        except Exception as e:
            logger.error(f"Error appending to CSV: {e}")
    
    def run(self):
        """
        Run the monitoring loop
        """
        logger.info("=" * 60)
        logger.info("LEAP IPO Real-time Monitor Started")
        logger.info("=" * 60)
        logger.info(f"Monitoring: LEAP IPO Subscription Data")
        logger.info(f"Output file: {self.csv_path}")
        logger.info(f"Refresh interval: {self.interval_seconds} seconds")
        logger.info("Counter: Tracking times QIB subscription > 5x")
        logger.info("Only appending when data changes (update_time or subscription values)")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Initialize session
        self._init_session()
        
        iteration = 0
        no_change_count = 0
        
        try:
            while True:
                iteration += 1
                logger.debug(f"\n--- Iteration {iteration} ---")
                
                # Fetch data
                data = self.fetch_data()
                
                if data:
                    # Check if data has changed
                    if self._has_data_changed(data):
                        # Append to CSV
                        self.append_to_csv(data)
                        no_change_count = 0
                        
                        # Display update with emoji
                        qib = data['qib_subscription_times']
                        total = data['total_subscription_times']
                        counter = data['qib_above_5x_counter']
                        consecutive = data['qib_above_5x_consecutive']
                        
                        if qib > 5:
                            logger.success(f"✓ Recorded: [{data['datetime']}] QIB: {qib:.2f}x (🔥 >5x) | Total: {total:.2f}x | Count: {counter} | Consecutive: {consecutive}")
                        else:
                            logger.info(f"✓ Recorded: [{data['datetime']}] QIB: {qib:.2f}x | Total: {total:.2f}x | Count: {counter} | Consecutive: {consecutive}")
                    else:
                        no_change_count += 1
                        logger.info(f"⏭ No change detected (update_time: {data.get('update_time', 'N/A')}) - Skipping record (no change count: {no_change_count})")
                else:
                    logger.warning("Failed to fetch data, retrying...")
                
                # Wait for next interval
                if iteration > 0:
                    logger.debug(f"Waiting {self.interval_seconds} seconds until next refresh...")
                    time.sleep(self.interval_seconds)
                    
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")
            self._print_summary()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self._print_summary()
    
    def _print_summary(self):
        """Print summary of collected data"""
        try:
            if not self.csv_path.exists():
                logger.info("No data collected")
                return
            
            df = pd.read_csv(self.csv_path)
            
            if df.empty:
                logger.info("No data collected")
                return
            
            logger.info("\n" + "=" * 60)
            logger.info("Monitoring Summary")
            logger.info("=" * 60)
            logger.info(f"Total records: {len(df)}")
            logger.info(f"First record: {df.iloc[0]['datetime']}")
            logger.info(f"Last record: {df.iloc[-1]['datetime']}")
            
            # Latest subscription
            latest = df.iloc[-1]
            logger.info(f"\nLatest Subscriptions:")
            logger.info(f"  QIB: {latest['qib_subscription_times']:.2f}x")
            logger.info(f"  Total: {latest['total_subscription_times']:.2f}x")
            logger.info(f"  Update Time: {latest['update_time']}")
            
            # Counter summary
            logger.info(f"\nQIB > 5x Counter Summary:")
            logger.info(f"  Total times > 5x: {latest['qib_above_5x_counter']}")
            logger.info(f"  Current consecutive: {latest['qib_above_5x_consecutive']}")
            
            # Calculate changes
            if len(df) > 1:
                first = df.iloc[0]
                qib_change = latest['qib_subscription_times'] - first['qib_subscription_times']
                total_change = latest['total_subscription_times'] - first['total_subscription_times']
                counter_change = latest['qib_above_5x_counter'] - first['qib_above_5x_counter']
                
                logger.info(f"\nChange from first to latest:")
                logger.info(f"  QIB: {qib_change:+.2f}x")
                logger.info(f"  Total: {total_change:+.2f}x")
                logger.info(f"  5x Count: {counter_change:+.0f}")
            
            # Max and min
            max_qib = df['qib_subscription_times'].max()
            min_qib = df['qib_subscription_times'].min()
            max_total = df['total_subscription_times'].max()
            min_total = df['total_subscription_times'].min()
            max_counter = df['qib_above_5x_counter'].max()
            
            logger.info(f"\nQIB Subscription Range:")
            logger.info(f"  Max: {max_qib:.2f}x")
            logger.info(f"  Min: {min_qib:.2f}x")
            
            logger.info(f"\nTotal Subscription Range:")
            logger.info(f"  Max: {max_total:.2f}x")
            logger.info(f"  Min: {min_total:.2f}x")
            
            logger.info(f"\nMax 5x Counter: {max_counter}")
            
            logger.info(f"\nData saved to: {self.csv_path}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
    
    def generate_report(self):
        """Generate a report from collected data"""
        try:
            if not self.csv_path.exists():
                logger.warning("No data file found")
                return
            
            df = pd.read_csv(self.csv_path)
            
            if df.empty:
                logger.warning("No data in file")
                return
            
            # Convert datetime
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Create report
            report = {
                'total_records': len(df),
                'start_time': df.iloc[0]['datetime'],
                'end_time': df.iloc[-1]['datetime'],
                'duration_hours': (df.iloc[-1]['datetime'] - df.iloc[0]['datetime']).total_seconds() / 3600,
                
                'qib_final': df.iloc[-1]['qib_subscription_times'],
                'qib_start': df.iloc[0]['qib_subscription_times'],
                'qib_change': df.iloc[-1]['qib_subscription_times'] - df.iloc[0]['qib_subscription_times'],
                'qib_max': df['qib_subscription_times'].max(),
                'qib_min': df['qib_subscription_times'].min(),
                
                'total_final': df.iloc[-1]['total_subscription_times'],
                'total_start': df.iloc[0]['total_subscription_times'],
                'total_change': df.iloc[-1]['total_subscription_times'] - df.iloc[0]['total_subscription_times'],
                'total_max': df['total_subscription_times'].max(),
                'total_min': df['total_subscription_times'].min(),
                
                'qib_above_5x_total': df.iloc[-1]['qib_above_5x_counter'],
                'qib_above_5x_consecutive': df.iloc[-1]['qib_above_5x_consecutive'],
                'qib_above_5x_max_counter': df['qib_above_5x_counter'].max(),
            }
            
            # Save report
            report_path = self.output_dir / f"leap_ipo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.success(f"Report generated: {report_path}")
            
            # Print report
            logger.info("\n" + "=" * 60)
            logger.info("LEAP IPO Subscription Report")
            logger.info("=" * 60)
            logger.info(f"Records: {report['total_records']}")
            logger.info(f"Duration: {report['duration_hours']:.2f} hours")
            logger.info(f"QIB Subscription: {report['qib_final']:.2f}x")
            logger.info(f"QIB Change: {report['qib_change']:+.2f}x")
            logger.info(f"Total Subscription: {report['total_final']:.2f}x")
            logger.info(f"Total Change: {report['total_change']:+.2f}x")
            logger.info(f"Times QIB > 5x: {report['qib_above_5x_total']}")
            logger.info(f"Consecutive QIB > 5x: {report['qib_above_5x_consecutive']}")
            logger.info("=" * 60)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LEAP IPO Real-time Monitor')
    parser.add_argument('--interval', type=int, default=300, 
                       help='Refresh interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true',
                       help='Fetch once and exit (will save even if no change)')
    parser.add_argument('--report', action='store_true',
                       help='Generate report from existing data and exit')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for CSV files')
    
    args = parser.parse_args()
    
    # Setup logger
    setup_logger()
    
    # Set output directory
    output_dir = Path(args.output) if args.output else None
    
    # Initialize monitor
    monitor = LEAPIPOMonitor(
        output_dir=output_dir,
        interval_seconds=args.interval
    )
    
    # Handle report generation
    if args.report:
        monitor.generate_report()
        return
    
    # Handle one-time fetch
    if args.once:
        data = monitor.fetch_data()
        if data:
            # Force append even if no change (for testing)
            monitor.append_to_csv(data)
            logger.success("Data fetched and saved")
            print(json.dumps(data, indent=2))
        return
    
    # Run continuous monitoring
    monitor.run()


if __name__ == "__main__":
    main()