# # # calculate_ipo_returns.py

# # """
# # Calculate IPO returns using the market database
# # """
# # import sys
# # from pathlib import Path
# # from datetime import datetime, timedelta
# # from loguru import logger
# # import pandas as pd
# # import sqlite3

# # # Add src to path
# # sys.path.insert(0, str(Path(__file__).parent))

# # from src.scraper import ChittorgarhScraper
# # from src.market_data.database import MarketDatabase
# # from src.market_data.holidays import get_trading_days, is_trading_day
# # from src.config import DATA_DIR
# # from src.utils import setup_logger


# # class IPOReturnCalculator:
# #     """Calculate returns for IPOs using market data"""
    
# #     def __init__(self, db_path: Path):
# #         self.db = MarketDatabase(db_path)
# #         self.conn = sqlite3.connect(db_path)
        
# #     def get_price_at_date(self, symbol: str, exchange: str, target_date: datetime) -> pd.Series:
# #         """
# #         Get price for a symbol on or after a specific date
# #         """
# #         query = """
# #         SELECT date, close, open, high, low, volume
# #         FROM daily_prices
# #         WHERE symbol = ? AND exchange = ? AND date >= ?
# #         ORDER BY date ASC
# #         LIMIT 1
# #         """
        
# #         df = pd.read_sql_query(
# #             query, 
# #             self.conn, 
# #             params=[symbol, exchange, target_date.strftime('%Y-%m-%d')]
# #         )
        
# #         if df.empty:
# #             return None
        
# #         return df.iloc[0]
    
# #     def get_current_price(self, symbol: str, exchange: str) -> pd.Series:
# #         """
# #         Get the latest available price for a symbol
# #         """
# #         query = """
# #         SELECT date, close, open, high, low, volume
# #         FROM daily_prices
# #         WHERE symbol = ? AND exchange = ?
# #         ORDER BY date DESC
# #         LIMIT 1
# #         """
        
# #         df = pd.read_sql_query(query, self.conn, params=[symbol, exchange])
        
# #         if df.empty:
# #             return None
        
# #         return df.iloc[0]
    
# #     def calculate_returns(self, ipo_data: dict) -> dict:
# #         """
# #         Calculate all returns for a single IPO
        
# #         Args:
# #             ipo_data: IPO data dictionary
            
# #         Returns:
# #             Dictionary with return metrics
# #         """
# #         results = {}
        
# #         # Get listing details
# #         listing_date = ipo_data.get('listing_date')
# #         issue_price = ipo_data.get('issue_price', 0)
# #         nse_symbol = ipo_data.get('nse_symbol')
# #         bse_code = ipo_data.get('bse_scrip_code')
# #         company_name = ipo_data.get('company_name')
        
# #         if not listing_date:
# #             logger.warning(f"No listing date for {company_name}")
# #             return results
        
# #         results['company_name'] = company_name
# #         results['issue_price'] = issue_price
# #         results['listing_date'] = listing_date
        
# #         # Check both exchanges
# #         exchanges_to_check = []
        
# #         if nse_symbol:
# #             exchanges_to_check.append(('NSE', nse_symbol))
        
# #         if bse_code:
# #             exchanges_to_check.append(('BSE', str(bse_code)))
        
# #         for exchange, symbol in exchanges_to_check:
# #             exchange_results = {}
            
# #             # Get listing day price (first available trading day)
# #             listing_day = self.get_price_at_date(symbol, exchange, listing_date)
            
# #             if listing_day is None:
# #                 logger.debug(f"No listing price for {symbol} on {exchange}")
# #                 continue
            
# #             listing_price = listing_day['close']
# #             listing_date_actual = listing_day['date']
            
# #             exchange_results['listing_price'] = listing_price
# #             exchange_results['listing_date_actual'] = listing_date_actual
            
# #             # Calculate listing day gain
# #             if issue_price and issue_price > 0:
# #                 exchange_results['listing_gain'] = ((listing_price - issue_price) / issue_price) * 100
            
# #             # Define periods to calculate
# #             periods = {
# #                 'day_2': 2,
# #                 'day_5': 5,
# #                 'day_10': 10,
# #                 'day_15': 15,
# #                 'day_30': 30,
# #                 'day_60': 60,
# #                 'day_90': 90,
# #             }
            
# #             # Get all trading days after listing
# #             query = """
# #             SELECT date, close
# #             FROM daily_prices
# #             WHERE symbol = ? AND exchange = ? AND date >= ?
# #             ORDER BY date ASC
# #             """
            
# #             df = pd.read_sql_query(
# #                 query,
# #                 self.conn,
# #                 params=[symbol, exchange, listing_date_actual.strftime('%Y-%m-%d')]
# #             )
            
# #             if df.empty:
# #                 logger.debug(f"No subsequent prices for {symbol} on {exchange}")
# #                 continue
            
# #             # Calculate returns for each period
# #             for period_name, days in periods.items():
# #                 if len(df) > days:
# #                     target_row = df.iloc[days]
# #                     target_price = target_row['close']
                    
# #                     if listing_price > 0:
# #                         exchange_results[f'{period_name}_return'] = ((target_price - listing_price) / listing_price) * 100
# #                         exchange_results[f'{period_name}_date'] = target_row['date']
# #                         exchange_results[f'{period_name}_price'] = target_price
            
# #             # Calculate current return
# #             current = self.get_current_price(symbol, exchange)
# #             if current is not None:
# #                 exchange_results['current_price'] = current['close']
# #                 exchange_results['current_date'] = current['date']
                
# #                 if listing_price > 0:
# #                     exchange_results['current_return'] = ((current['close'] - listing_price) / listing_price) * 100
            
# #             results[exchange] = exchange_results
        
# #         return results
    
# #     def calculate_all_returns(self, ipo_list: list) -> pd.DataFrame:
# #         """
# #         Calculate returns for all IPOs
        
# #         Args:
# #             ipo_list: List of IPO data dictionaries
            
# #         Returns:
# #             DataFrame with all return metrics
# #         """
# #         all_results = []
        
# #         logger.info(f"Calculating returns for {len(ipo_list)} IPOs...")
        
# #         for ipo in ipo_list:
# #             results = self.calculate_returns(ipo)
            
# #             if results:
# #                 # Flatten results for DataFrame
# #                 flat_result = {
# #                     'company_name': results.get('company_name'),
# #                     'issue_price': results.get('issue_price'),
# #                     'listing_date': results.get('listing_date'),
# #                 }
                
# #                 # Add NSE results
# #                 if 'NSE' in results:
# #                     nse = results['NSE']
# #                     for key, value in nse.items():
# #                         flat_result[f'NSE_{key}'] = value
                
# #                 # Add BSE results
# #                 if 'BSE' in results:
# #                     bse = results['BSE']
# #                     for key, value in bse.items():
# #                         flat_result[f'BSE_{key}'] = value
                
# #                 all_results.append(flat_result)
        
# #         if all_results:
# #             df = pd.DataFrame(all_results)
# #             logger.info(f"Calculated returns for {len(df)} IPOs")
# #             return df
# #         else:
# #             return pd.DataFrame()


# # def main():
# #     """Main execution function"""
# #     logger.info("=" * 60)
# #     logger.info("IPO Return Calculator")
# #     logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# #     logger.info("=" * 60)
    
# #     try:
# #         # Step 1: Fetch IPO data from Chittorgarh
# #         logger.info("Fetching IPO data from Chittorgarh...")
# #         scraper = ChittorgarhScraper(impersonate="chrome110")
# #         ipo_data = scraper.fetch_ipo_data()
        
# #         if not ipo_data:
# #             logger.error("No IPO data fetched. Exiting.")
# #             return
        
# #         logger.info(f"Fetched {len(ipo_data)} IPO records")
        
# #         # Step 2: Calculate returns
# #         db_path = Path(__file__).parent / "database" / "market_data.db"
# #         calculator = IPOReturnCalculator(db_path)
        
# #         logger.info("Calculating returns...")
# #         returns_df = calculator.calculate_all_returns(ipo_data)
        
# #         if returns_df.empty:
# #             logger.error("No returns calculated. Exiting.")
# #             return
        
# #         # Step 3: Save results
# #         output_path = DATA_DIR / f"ipo_returns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# #         returns_df.to_csv(output_path, index=False)
# #         logger.success(f"Returns saved to {output_path}")
        
# #         # Step 4: Display summary
# #         logger.info("\n" + "=" * 60)
# #         logger.info("Summary Statistics")
# #         logger.info("=" * 60)
        
# #         # Show top performers
# #         if 'NSE_listing_gain' in returns_df.columns:
# #             top_nse = returns_df.nlargest(10, 'NSE_listing_gain')[['company_name', 'NSE_listing_gain']]
# #             logger.info("\nTop 10 IPOs by Listing Day Gain (NSE):")
# #             for _, row in top_nse.iterrows():
# #                 logger.info(f"  {row['company_name']}: {row['NSE_listing_gain']:.2f}%")
        
# #         # Show average returns
# #         avg_cols = [col for col in returns_df.columns if '_return' in col]
# #         if avg_cols:
# #             logger.info("\nAverage Returns:")
# #             for col in avg_cols:
# #                 avg = returns_df[col].mean()
# #                 if pd.notna(avg):
# #                     logger.info(f"  {col}: {avg:.2f}%")
        
# #         logger.success("\nIPO return calculation completed!")
        
# #     except Exception as e:
# #         logger.error(f"An error occurred: {e}")
# #         logger.exception("Full traceback:")
# #         sys.exit(1)


# # if __name__ == "__main__":
# #     setup_logger()
# #     main()

# # calculate_ipo_returns.py

# """
# Calculate IPO returns using the market database
# """
# import sys
# from pathlib import Path
# from datetime import datetime, timedelta
# from loguru import logger
# import pandas as pd
# import sqlite3
# import numpy as np

# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent))

# from src.scraper import ChittorgarhScraper
# from src.market_data.database import MarketDatabase
# from src.market_data.holidays import get_trading_days, is_trading_day
# from src.config import DATA_DIR
# from src.utils import setup_logger


# class IPOReturnCalculator:
#     """Calculate returns for IPOs using market data"""
    
#     def __init__(self, db_path: Path):
#         self.db = MarketDatabase(db_path)
#         self.conn = sqlite3.connect(db_path)
#         # Enable dictionary cursor for easier access
#         self.conn.row_factory = sqlite3.Row
        
#     def _ensure_datetime(self, date_value):
#         """
#         Convert various date formats to datetime object
#         """
#         if date_value is None:
#             return None
        
#         if isinstance(date_value, datetime):
#             return date_value
        
#         if isinstance(date_value, str):
#             try:
#                 # Try common date formats
#                 for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d-%b-%Y', '%d-%m-%Y']:
#                     try:
#                         return datetime.strptime(date_value, fmt)
#                     except ValueError:
#                         continue
                
#                 # Try pandas to_datetime as fallback
#                 return pd.to_datetime(date_value).to_pydatetime()
                
#             except Exception as e:
#                 logger.error(f"Could not parse date '{date_value}': {e}")
#                 return None
        
#         return date_value
    
#     def get_price_at_date(self, symbol: str, exchange: str, target_date) -> pd.Series:
#         """
#         Get price for a symbol on or after a specific date
#         """
#         # Ensure target_date is datetime
#         target_date = self._ensure_datetime(target_date)
#         if target_date is None:
#             logger.error(f"Invalid target date for {symbol}")
#             return None
        
#         query = """
#         SELECT date, close, open, high, low, volume
#         FROM daily_prices
#         WHERE symbol = ? AND exchange = ? AND date >= ?
#         ORDER BY date ASC
#         LIMIT 1
#         """
        
#         try:
#             df = pd.read_sql_query(
#                 query, 
#                 self.conn, 
#                 params=[symbol, exchange, target_date.strftime('%Y-%m-%d')]
#             )
            
#             if df.empty:
#                 return None
            
#             # Convert date to datetime
#             df['date'] = pd.to_datetime(df['date'])
#             return df.iloc[0]
            
#         except Exception as e:
#             logger.error(f"Error getting price for {symbol} on {exchange}: {e}")
#             return None
    
#     def get_current_price(self, symbol: str, exchange: str) -> pd.Series:
#         """
#         Get the latest available price for a symbol
#         """
#         query = """
#         SELECT date, close, open, high, low, volume
#         FROM daily_prices
#         WHERE symbol = ? AND exchange = ?
#         ORDER BY date DESC
#         LIMIT 1
#         """
        
#         try:
#             df = pd.read_sql_query(query, self.conn, params=[symbol, exchange])
            
#             if df.empty:
#                 return None
            
#             df['date'] = pd.to_datetime(df['date'])
#             return df.iloc[0]
            
#         except Exception as e:
#             logger.error(f"Error getting current price for {symbol}: {e}")
#             return None
    
#     def calculate_returns(self, ipo_data: dict) -> dict:
#         """
#         Calculate all returns for a single IPO
        
#         Args:
#             ipo_data: IPO data dictionary
            
#         Returns:
#             Dictionary with return metrics
#         """
#         results = {}
        
#         # Get listing details
#         listing_date = ipo_data.get('listing_date')
#         issue_price = ipo_data.get('issue_price', 0)
#         nse_symbol = ipo_data.get('nse_symbol')
#         bse_code = ipo_data.get('bse_scrip_code')
#         company_name = ipo_data.get('company_name')
        
#         if not listing_date:
#             logger.warning(f"No listing date for {company_name}")
#             return results
        
#         # Ensure listing_date is datetime
#         listing_date = self._ensure_datetime(listing_date)
#         if listing_date is None:
#             logger.warning(f"Invalid listing date for {company_name}")
#             return results
        
#         results['company_name'] = company_name
#         results['issue_price'] = issue_price
#         results['listing_date'] = listing_date
        
#         # Check both exchanges
#         exchanges_to_check = []
        
#         if nse_symbol and nse_symbol.strip():
#             exchanges_to_check.append(('NSE', nse_symbol.strip()))
        
#         if bse_code and str(bse_code).strip():
#             exchanges_to_check.append(('BSE', str(bse_code).strip()))
        
#         if not exchanges_to_check:
#             logger.warning(f"No exchange symbols found for {company_name}")
#             return results
        
#         for exchange, symbol in exchanges_to_check:
#             exchange_results = {}
            
#             # Get listing day price (first available trading day)
#             listing_day = self.get_price_at_date(symbol, exchange, listing_date)
            
#             if listing_day is None:
#                 logger.debug(f"No listing price for {symbol} on {exchange}")
#                 continue
            
#             # Ensure dates are datetime objects
#             listing_price = float(listing_day['close'])
#             listing_date_actual = self._ensure_datetime(listing_day['date'])
            
#             if listing_date_actual is None:
#                 logger.debug(f"Invalid listing date for {symbol} on {exchange}")
#                 continue
            
#             exchange_results['listing_price'] = listing_price
#             exchange_results['listing_date_actual'] = listing_date_actual
            
#             # Calculate listing day gain
#             if issue_price and float(issue_price) > 0:
#                 issue_price_float = float(issue_price)
#                 exchange_results['listing_gain'] = ((listing_price - issue_price_float) / issue_price_float) * 100
            
#             # Define periods to calculate (in trading days)
#             periods = {
#                 'day_2': 2,
#                 'day_5': 5,
#                 'day_10': 10,
#                 'day_15': 15,
#                 'day_30': 30,
#                 'day_60': 60,
#                 'day_90': 90,
#             }
            
#             # Get all trading days after listing
#             query = """
#             SELECT date, close
#             FROM daily_prices
#             WHERE symbol = ? AND exchange = ? AND date >= ?
#             ORDER BY date ASC
#             """
            
#             try:
#                 df = pd.read_sql_query(
#                     query,
#                     self.conn,
#                     params=[symbol, exchange, listing_date_actual.strftime('%Y-%m-%d')]
#                 )
                
#                 if df.empty:
#                     logger.debug(f"No subsequent prices for {symbol} on {exchange}")
#                     continue
                
#                 # Convert date to datetime
#                 df['date'] = pd.to_datetime(df['date'])
                
#                 # Calculate returns for each period
#                 for period_name, days in periods.items():
#                     if len(df) > days:
#                         target_row = df.iloc[days]
#                         target_price = float(target_row['close'])
#                         target_date = self._ensure_datetime(target_row['date'])
                        
#                         if listing_price > 0 and target_date:
#                             exchange_results[f'{period_name}_return'] = ((target_price - listing_price) / listing_price) * 100
#                             exchange_results[f'{period_name}_date'] = target_date
#                             exchange_results[f'{period_name}_price'] = target_price
#                         elif target_date:
#                             exchange_results[f'{period_name}_date'] = target_date
#                             exchange_results[f'{period_name}_price'] = target_price
                
#                 # Calculate current return
#                 current = self.get_current_price(symbol, exchange)
#                 if current is not None:
#                     current_price = float(current['close'])
#                     current_date = self._ensure_datetime(current['date'])
                    
#                     if current_date:
#                         exchange_results['current_price'] = current_price
#                         exchange_results['current_date'] = current_date
                        
#                         if listing_price > 0:
#                             exchange_results['current_return'] = ((current_price - listing_price) / listing_price) * 100
                
#                 results[exchange] = exchange_results
                
#             except Exception as e:
#                 logger.error(f"Error calculating returns for {symbol} on {exchange}: {e}")
#                 continue
        
#         return results
    
#     def calculate_all_returns(self, ipo_list: list) -> pd.DataFrame:
#         """
#         Calculate returns for all IPOs
        
#         Args:
#             ipo_list: List of IPO data dictionaries
            
#         Returns:
#             DataFrame with all return metrics
#         """
#         all_results = []
        
#         logger.info(f"Calculating returns for {len(ipo_list)} IPOs...")
        
#         for idx, ipo in enumerate(ipo_list, 1):
#             # Progress indicator
#             if idx % 10 == 0:
#                 logger.debug(f"Processing IPO {idx}/{len(ipo_list)}")
            
#             results = self.calculate_returns(ipo)
            
#             if results:
#                 # Flatten results for DataFrame
#                 flat_result = {
#                     'company_name': results.get('company_name'),
#                     'issue_price': results.get('issue_price'),
#                     'listing_date': results.get('listing_date'),
#                 }
                
#                 # Add NSE results
#                 if 'NSE' in results:
#                     nse = results['NSE']
#                     for key, value in nse.items():
#                         if isinstance(value, datetime):
#                             flat_result[f'NSE_{key}'] = value.strftime('%Y-%m-%d')
#                         else:
#                             flat_result[f'NSE_{key}'] = value
                
#                 # Add BSE results
#                 if 'BSE' in results:
#                     bse = results['BSE']
#                     for key, value in bse.items():
#                         if isinstance(value, datetime):
#                             flat_result[f'BSE_{key}'] = value.strftime('%Y-%m-%d')
#                         else:
#                             flat_result[f'BSE_{key}'] = value
                
#                 all_results.append(flat_result)
        
#         if all_results:
#             df = pd.DataFrame(all_results)
            
#             # Convert date columns to datetime
#             date_columns = ['listing_date', 'NSE_listing_date_actual', 'BSE_listing_date_actual']
#             for col in date_columns:
#                 if col in df.columns:
#                     df[col] = pd.to_datetime(df[col], errors='coerce')
            
#             # Sort by listing date
#             if 'listing_date' in df.columns:
#                 df = df.sort_values('listing_date', ascending=False)
            
#             logger.info(f"Calculated returns for {len(df)} IPOs")
            
#             # Log success rate
#             nse_count = df['NSE_listing_price'].notna().sum()
#             bse_count = df['BSE_listing_price'].notna().sum()
#             logger.info(f"  NSE data: {nse_count}/{len(df)} IPOs")
#             logger.info(f"  BSE data: {bse_count}/{len(df)} IPOs")
            
#             return df
#         else:
#             logger.warning("No results calculated")
#             return pd.DataFrame()
    
#     def close(self):
#         """Close database connection"""
#         if hasattr(self, 'conn'):
#             self.conn.close()


# def main():
#     """Main execution function"""
#     logger.info("=" * 60)
#     logger.info("IPO Return Calculator")
#     logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     logger.info("=" * 60)
    
#     calculator = None
    
#     try:
#         # Step 1: Fetch IPO data from Chittorgarh
#         logger.info("Fetching IPO data from Chittorgarh...")
#         scraper = ChittorgarhScraper(impersonate="chrome110")
#         ipo_data = scraper.fetch_ipo_data()
        
#         if not ipo_data:
#             logger.error("No IPO data fetched. Exiting.")
#             return
        
#         logger.info(f"Fetched {len(ipo_data)} IPO records")
        
#         # Step 2: Calculate returns
#         db_path = Path(__file__).parent / "database" / "market_data.db"
        
#         if not db_path.exists():
#             logger.error(f"Database not found at {db_path}. Please run ingest_market_data.py first.")
#             return
        
#         calculator = IPOReturnCalculator(db_path)
        
#         logger.info("Calculating returns...")
#         returns_df = calculator.calculate_all_returns(ipo_data)
        
#         if returns_df.empty:
#             logger.error("No returns calculated. Exiting.")
#             return
        
#         # Step 3: Save results
#         output_path = DATA_DIR / f"ipo_returns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         returns_df.to_csv(output_path, index=False)
#         logger.success(f"Returns saved to {output_path}")
        
#         # Also save to Excel for better viewing
#         try:
#             excel_path = DATA_DIR / f"ipo_returns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
#             returns_df.to_excel(excel_path, index=False, engine='openpyxl')
#             logger.success(f"Returns saved to Excel: {excel_path}")
#         except Exception as e:
#             logger.debug(f"Could not save Excel file: {e}")
        
#         # Step 4: Display summary
#         logger.info("\n" + "=" * 60)
#         logger.info("Summary Statistics")
#         logger.info("=" * 60)
        
#         # Show top performers by NSE listing gain
#         if 'NSE_listing_gain' in returns_df.columns:
#             valid_gains = returns_df[returns_df['NSE_listing_gain'].notna()]
#             if not valid_gains.empty:
#                 top_nse = valid_gains.nlargest(10, 'NSE_listing_gain')[['company_name', 'NSE_listing_gain']]
#                 logger.info("\nTop 10 IPOs by Listing Day Gain (NSE):")
#                 for _, row in top_nse.iterrows():
#                     logger.info(f"  {row['company_name']}: {row['NSE_listing_gain']:.2f}%")
                
#                 # Show worst performers
#                 bottom_nse = valid_gains.nsmallest(5, 'NSE_listing_gain')[['company_name', 'NSE_listing_gain']]
#                 logger.info("\nBottom 5 IPOs by Listing Day Gain (NSE):")
#                 for _, row in bottom_nse.iterrows():
#                     logger.info(f"  {row['company_name']}: {row['NSE_listing_gain']:.2f}%")
        
#         # Show average returns for NSE
#         logger.info("\nAverage Returns (NSE):")
#         nse_return_cols = [col for col in returns_df.columns if 'NSE_' in col and '_return' in col and 'listing' not in col]
#         for col in nse_return_cols:
#             avg = returns_df[col].mean()
#             if pd.notna(avg):
#                 logger.info(f"  {col.replace('NSE_', '')}: {avg:.2f}%")
        
#         # Show average returns for BSE
#         if any('BSE_' in col for col in returns_df.columns):
#             logger.info("\nAverage Returns (BSE):")
#             bse_return_cols = [col for col in returns_df.columns if 'BSE_' in col and '_return' in col and 'listing' not in col]
#             for col in bse_return_cols:
#                 avg = returns_df[col].mean()
#                 if pd.notna(avg):
#                     logger.info(f"  {col.replace('BSE_', '')}: {avg:.2f}%")
        
#         logger.success("\nIPO return calculation completed!")
        
#     except KeyboardInterrupt:
#         logger.warning("Calculation interrupted by user")
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         logger.exception("Full traceback:")
#     finally:
#         if calculator:
#             calculator.close()


# if __name__ == "__main__":
#     setup_logger()
#     main()

"""
Calculate IPO returns using the market database
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd
import sqlite3
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper import ChittorgarhScraper
from src.market_data.database import MarketDatabase
from src.market_data.holidays import get_trading_days, is_trading_day
from src.config import DATA_DIR
from src.utils import setup_logger


class IPOReturnCalculator:
    """Calculate returns for IPOs using market data"""
    
    def __init__(self, db_path: Path):
        self.db = MarketDatabase(db_path)
        self.conn = sqlite3.connect(db_path)
        # Enable dictionary cursor for easier access
        self.conn.row_factory = sqlite3.Row
        
    def _ensure_datetime(self, date_value):
        """
        Convert various date formats to datetime object
        """
        if date_value is None:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d-%b-%Y', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(date_value, fmt)
                    except ValueError:
                        continue
                
                # Try pandas to_datetime as fallback
                return pd.to_datetime(date_value).to_pydatetime()
                
            except Exception as e:
                logger.debug(f"Could not parse date '{date_value}': {e}")
                return None
        
        return date_value
    
    def get_price_at_date(self, symbol: str, exchange: str, target_date) -> pd.Series:
        """
        Get price for a symbol on or after a specific date
        """
        # Ensure target_date is datetime
        target_date = self._ensure_datetime(target_date)
        if target_date is None:
            logger.debug(f"Invalid target date for {symbol}")
            return None
        
        query = """
        SELECT date, close, open, high, low, volume
        FROM daily_prices
        WHERE symbol = ? AND exchange = ? AND date >= ?
        ORDER BY date ASC
        LIMIT 1
        """
        
        try:
            df = pd.read_sql_query(
                query, 
                self.conn, 
                params=[symbol, exchange, target_date.strftime('%Y-%m-%d')]
            )
            
            if df.empty:
                return None
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            return df.iloc[0]
            
        except Exception as e:
            logger.debug(f"Error getting price for {symbol} on {exchange}: {e}")
            return None
    
    def get_current_price(self, symbol: str, exchange: str) -> pd.Series:
        """
        Get the latest available price for a symbol
        """
        query = """
        SELECT date, close, open, high, low, volume
        FROM daily_prices
        WHERE symbol = ? AND exchange = ?
        ORDER BY date DESC
        LIMIT 1
        """
        
        try:
            df = pd.read_sql_query(query, self.conn, params=[symbol, exchange])
            
            if df.empty:
                return None
            
            df['date'] = pd.to_datetime(df['date'])
            return df.iloc[0]
            
        except Exception as e:
            logger.debug(f"Error getting current price for {symbol}: {e}")
            return None
    
    def calculate_returns(self, ipo_data: dict) -> dict:
        """
        Calculate all returns for a single IPO
        
        Args:
            ipo_data: IPO data dictionary
            
        Returns:
            Dictionary with return metrics
        """
        results = {}
        
        # Get listing details
        listing_date = ipo_data.get('listing_date')
        issue_price = ipo_data.get('issue_price', 0)
        nse_symbol = ipo_data.get('nse_symbol')
        bse_code = ipo_data.get('bse_scrip_code')
        company_name = ipo_data.get('company_name')
        
        if not listing_date:
            logger.debug(f"No listing date for {company_name}")
            return results
        
        # Ensure listing_date is datetime
        listing_date = self._ensure_datetime(listing_date)
        if listing_date is None:
            logger.debug(f"Invalid listing date for {company_name}")
            return results
        
        results['company_name'] = company_name
        results['issue_price'] = issue_price
        results['listing_date'] = listing_date
        
        # Check both exchanges
        exchanges_to_check = []
        
        if nse_symbol and nse_symbol.strip():
            exchanges_to_check.append(('NSE', nse_symbol.strip()))
        
        if bse_code and str(bse_code).strip():
            exchanges_to_check.append(('BSE', str(bse_code).strip()))
        
        if not exchanges_to_check:
            logger.debug(f"No exchange symbols found for {company_name}")
            return results
        
        for exchange, symbol in exchanges_to_check:
            exchange_results = {}
            
            # Get listing day price (first available trading day)
            listing_day = self.get_price_at_date(symbol, exchange, listing_date)
            
            if listing_day is None:
                logger.debug(f"No listing price for {symbol} on {exchange}")
                continue
            
            # Ensure dates are datetime objects
            listing_price = float(listing_day['close'])
            listing_date_actual = self._ensure_datetime(listing_day['date'])
            
            if listing_date_actual is None:
                logger.debug(f"Invalid listing date for {symbol} on {exchange}")
                continue
            
            exchange_results['listing_price'] = listing_price
            exchange_results['listing_date_actual'] = listing_date_actual
            
            # Calculate listing day gain
            if issue_price and float(issue_price) > 0:
                issue_price_float = float(issue_price)
                exchange_results['listing_gain'] = ((listing_price - issue_price_float) / issue_price_float) * 100
            
            # Define periods to calculate (in trading days)
            periods = {
                'day_2': 2,
                'day_5': 5,
                'day_10': 10,
                'day_15': 15,
                'day_30': 30,
                'day_60': 60,
                'day_90': 90,
            }
            
            # Get all trading days after listing
            query = """
            SELECT date, close
            FROM daily_prices
            WHERE symbol = ? AND exchange = ? AND date >= ?
            ORDER BY date ASC
            """
            
            try:
                df = pd.read_sql_query(
                    query,
                    self.conn,
                    params=[symbol, exchange, listing_date_actual.strftime('%Y-%m-%d')]
                )
                
                if df.empty:
                    logger.debug(f"No subsequent prices for {symbol} on {exchange}")
                    continue
                
                # Convert date to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Calculate returns for each period
                for period_name, days in periods.items():
                    if len(df) > days:
                        target_row = df.iloc[days]
                        target_price = float(target_row['close'])
                        target_date = self._ensure_datetime(target_row['date'])
                        
                        if listing_price > 0 and target_date:
                            exchange_results[f'{period_name}_return'] = ((target_price - listing_price) / listing_price) * 100
                            exchange_results[f'{period_name}_date'] = target_date
                            exchange_results[f'{period_name}_price'] = target_price
                        elif target_date:
                            exchange_results[f'{period_name}_date'] = target_date
                            exchange_results[f'{period_name}_price'] = target_price
                
                # Calculate current return
                current = self.get_current_price(symbol, exchange)
                if current is not None:
                    current_price = float(current['close'])
                    current_date = self._ensure_datetime(current['date'])
                    
                    if current_date:
                        exchange_results['current_price'] = current_price
                        exchange_results['current_date'] = current_date
                        
                        if listing_price > 0:
                            exchange_results['current_return'] = ((current_price - listing_price) / listing_price) * 100
                
                results[exchange] = exchange_results
                
            except Exception as e:
                logger.debug(f"Error calculating returns for {symbol} on {exchange}: {e}")
                continue
        
        return results
    
    def calculate_all_returns(self, ipo_list: list) -> pd.DataFrame:
        """
        Calculate returns for all IPOs
        
        Args:
            ipo_list: List of IPO data dictionaries
            
        Returns:
            DataFrame with all return metrics
        """
        all_results = []
        
        logger.info(f"Calculating returns for {len(ipo_list)} IPOs...")
        
        for idx, ipo in enumerate(ipo_list, 1):
            # Progress indicator
            if idx % 10 == 0:
                logger.debug(f"Processing IPO {idx}/{len(ipo_list)}")
            
            results = self.calculate_returns(ipo)
            
            if results:
                # Flatten results for DataFrame
                flat_result = {
                    'company_name': results.get('company_name'),
                    'issue_price': results.get('issue_price'),
                    'listing_date': results.get('listing_date'),
                }
                
                # Add NSE results
                if 'NSE' in results:
                    nse = results['NSE']
                    for key, value in nse.items():
                        if isinstance(value, datetime):
                            flat_result[f'NSE_{key}'] = value.strftime('%Y-%m-%d')
                        else:
                            flat_result[f'NSE_{key}'] = value
                
                # Add BSE results (if available)
                if 'BSE' in results:
                    bse = results['BSE']
                    for key, value in bse.items():
                        if isinstance(value, datetime):
                            flat_result[f'BSE_{key}'] = value.strftime('%Y-%m-%d')
                        else:
                            flat_result[f'BSE_{key}'] = value
                
                all_results.append(flat_result)
        
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Convert date columns to datetime
            date_columns = ['listing_date', 'NSE_listing_date_actual', 'BSE_listing_date_actual']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Sort by listing date
            if 'listing_date' in df.columns:
                df = df.sort_values('listing_date', ascending=False)
            
            logger.info(f"Calculated returns for {len(df)} IPOs")
            
            # Log success rate - handle missing columns gracefully
            nse_count = df['NSE_listing_price'].notna().sum() if 'NSE_listing_price' in df.columns else 0
            bse_count = df['BSE_listing_price'].notna().sum() if 'BSE_listing_price' in df.columns else 0
            
            logger.info(f"  NSE data: {nse_count}/{len(df)} IPOs")
            if bse_count > 0:
                logger.info(f"  BSE data: {bse_count}/{len(df)} IPOs")
            else:
                logger.info("  BSE data: Not available (skipped)")
            
            return df
        else:
            logger.warning("No results calculated")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("IPO Return Calculator")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    calculator = None
    
    try:
        # Step 1: Fetch IPO data from Chittorgarh
        logger.info("Fetching IPO data from Chittorgarh...")
        scraper = ChittorgarhScraper(impersonate="chrome110")
        ipo_data = scraper.fetch_ipo_data()
        
        if not ipo_data:
            logger.error("No IPO data fetched. Exiting.")
            return
        
        logger.info(f"Fetched {len(ipo_data)} IPO records")
        
        # Step 2: Calculate returns
        db_path = Path(__file__).parent / "database" / "market_data.db"
        
        if not db_path.exists():
            logger.error(f"Database not found at {db_path}. Please run ingest_market_data.py first.")
            return
        
        calculator = IPOReturnCalculator(db_path)
        
        logger.info("Calculating returns...")
        returns_df = calculator.calculate_all_returns(ipo_data)
        
        if returns_df.empty:
            logger.error("No returns calculated. Exiting.")
            return
        
        # Step 3: Save results
        output_path = DATA_DIR / f"ipo_returns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        returns_df.to_csv(output_path, index=False)
        logger.success(f"Returns saved to {output_path}")
        
        # Also save to Excel for better viewing
        try:
            excel_path = DATA_DIR / f"ipo_returns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            returns_df.to_excel(excel_path, index=False, engine='openpyxl')
            logger.success(f"Returns saved to Excel: {excel_path}")
        except Exception as e:
            logger.debug(f"Could not save Excel file: {e}")
        
        # Step 4: Display summary
        logger.info("\n" + "=" * 60)
        logger.info("Summary Statistics")
        logger.info("=" * 60)
        
        # Show top performers by NSE listing gain
        if 'NSE_listing_gain' in returns_df.columns:
            valid_gains = returns_df[returns_df['NSE_listing_gain'].notna()]
            if not valid_gains.empty:
                top_nse = valid_gains.nlargest(10, 'NSE_listing_gain')[['company_name', 'NSE_listing_gain']]
                logger.info("\nTop 10 IPOs by Listing Day Gain (NSE):")
                for _, row in top_nse.iterrows():
                    logger.info(f"  {row['company_name']}: {row['NSE_listing_gain']:.2f}%")
                
                # Show worst performers
                bottom_nse = valid_gains.nsmallest(5, 'NSE_listing_gain')[['company_name', 'NSE_listing_gain']]
                logger.info("\nBottom 5 IPOs by Listing Day Gain (NSE):")
                for _, row in bottom_nse.iterrows():
                    logger.info(f"  {row['company_name']}: {row['NSE_listing_gain']:.2f}%")
        
        # Show average returns for NSE
        if any('NSE_' in col for col in returns_df.columns):
            logger.info("\nAverage Returns (NSE):")
            nse_return_cols = [col for col in returns_df.columns if 'NSE_' in col and '_return' in col and 'listing' not in col and col != 'NSE_current_return']
            for col in nse_return_cols:
                avg = returns_df[col].mean()
                if pd.notna(avg):
                    logger.info(f"  {col.replace('NSE_', '')}: {avg:.2f}%")
        
        # Show average returns for BSE (if available)
        if any('BSE_' in col for col in returns_df.columns):
            bse_cols = [col for col in returns_df.columns if 'BSE_' in col and '_return' in col and 'listing' not in col and col != 'BSE_current_return']
            if bse_cols:
                logger.info("\nAverage Returns (BSE):")
                for col in bse_cols:
                    avg = returns_df[col].mean()
                    if pd.notna(avg):
                        logger.info(f"  {col.replace('BSE_', '')}: {avg:.2f}%")
        
        # Show summary of data coverage
        logger.info("\n" + "-" * 60)
        logger.info("Data Coverage Summary:")
        logger.info("-" * 60)
        
        # Count IPOs with NSE data
        nse_count = returns_df['NSE_listing_price'].notna().sum() if 'NSE_listing_price' in returns_df.columns else 0
        bse_count = returns_df['BSE_listing_price'].notna().sum() if 'BSE_listing_price' in returns_df.columns else 0
        
        logger.info(f"  IPOs with NSE listing price: {nse_count}/{len(returns_df)}")
        if bse_count > 0:
            logger.info(f"  IPOs with BSE listing price: {bse_count}/{len(returns_df)}")
        else:
            logger.info("  BSE data: Not available in database")
        
        # Count IPOs with current price
        current_count = returns_df['NSE_current_price'].notna().sum() if 'NSE_current_price' in returns_df.columns else 0
        logger.info(f"  IPOs with current price: {current_count}/{len(returns_df)}")
        
        logger.success("\nIPO return calculation completed!")
        
    except KeyboardInterrupt:
        logger.warning("Calculation interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.exception("Full traceback:")
    finally:
        if calculator:
            calculator.close()


if __name__ == "__main__":
    setup_logger()
    main()