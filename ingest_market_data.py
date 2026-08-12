# """
# Market data ingestion script
# """
# import sys
# from pathlib import Path
# from datetime import datetime, timedelta
# from loguru import logger
# from tqdm import tqdm
# import pandas as pd
# import sqlite3

# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent))

# from src.market_data.nse import NSEDownloader
# from src.market_data.bse import BSEDownloader
# from src.market_data.normalizer import DataNormalizer
# from src.market_data.database import MarketDatabase
# from src.market_data.holidays import get_trading_days, is_trading_day
# from src.config import DATA_DIR
# from src.utils import setup_logger


# def ingest_market_data():
#     """Main ingestion function"""
#     logger.info("=" * 60)
#     logger.info("Market Data Ingestion System")
#     logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     logger.info("=" * 60)
    
#     # Setup directories
#     data_dir = DATA_DIR / "bhavcopy"
#     db_path = Path(__file__).parent / "database" / "market_data.db"
    
#     # Initialize components
#     nse_downloader = NSEDownloader(data_dir)
#     bse_downloader = BSEDownloader(data_dir)
#     normalizer = DataNormalizer()
#     db = MarketDatabase(db_path)
    
#     # Define date range (2026-01-01 to yesterday)
#     start_date = datetime(2026, 1, 1)
#     end_date = datetime.now() - timedelta(days=1)  # Yesterday
    
#     # Get actual trading days
#     trading_days = get_trading_days(start_date, end_date)
    
#     logger.info(f"Found {len(trading_days)} trading days from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
#     # Process each trading day
#     successful_days = 0
#     for date in tqdm(trading_days, desc="Downloading bhavcopies"):
#         date_str = date.strftime('%Y-%m-%d')
#         nse_available = False
#         bse_available = False
        
#         # Download NSE
#         try:
#             nse_file = nse_downloader.download_bhavcopy(date)
#             if nse_file and nse_file.exists():
#                 df_nse = nse_downloader.parse_bhavcopy(nse_file)
#                 if not df_nse.empty:
#                     normalized = normalizer.normalize(df_nse, 'NSE')
#                     db.insert_daily_prices(normalized)
#                     nse_available = True
#                     logger.debug(f"NSE data inserted for {date_str}")
#         except Exception as e:
#             logger.debug(f"NSE error for {date_str}: {e}")
        
#         # Download BSE
#         try:
#             bse_file = bse_downloader.download_bhavcopy(date)
#             if bse_file and bse_file.exists():
#                 df_bse = bse_downloader.parse_bhavcopy(bse_file)
#                 if not df_bse.empty:
#                     normalized = normalizer.normalize(df_bse, 'BSE')
#                     db.insert_daily_prices(normalized)
#                     bse_available = True
#                     logger.debug(f"BSE data inserted for {date_str}")
#         except Exception as e:
#             logger.debug(f"BSE error for {date_str}: {e}")
        
#         # Update market status
#         if nse_available or bse_available:
#             db.update_market_status(date, nse_available, bse_available)
#             successful_days += 1
        
#         # Small delay to be respectful
#         time.sleep(0.5)
    
#     # Summary
#     logger.success(f"Market data ingestion completed!")
#     logger.info(f"Database: {db_path}")
#     logger.info(f"Successfully processed {successful_days} out of {len(trading_days)} trading days")
    
#     # Get stats
#     with sqlite3.connect(db_path) as conn:
#         count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
#         dates = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices").fetchone()[0]
        
#         logger.info(f"Total records: {count:,}")
#         logger.info(f"Trading days with data: {dates}")
        
#         # Show NSE/BSE split
#         nse_count = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'NSE'").fetchone()[0]
#         bse_count = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
#         logger.info(f"NSE records: {nse_count:,}")
#         logger.info(f"BSE records: {bse_count:,}")

# if __name__ == "__main__":
#     import time
#     setup_logger()
#     ingest_market_data()

# ingest_market_data.py

"""
Market data ingestion script with incremental updates
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger
from tqdm import tqdm
import pandas as pd
import sqlite3
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.market_data.nse import NSEDownloader
from src.market_data.bse import BSEDownloader
from src.market_data.normalizer import DataNormalizer
from src.market_data.database import MarketDatabase
from src.market_data.holidays import get_trading_days, is_trading_day, get_last_trading_day
from src.config import DATA_DIR
from src.utils import setup_logger


def ingest_market_data(force_full: bool = False):
    """
    Main ingestion function with incremental update support
    
    Args:
        force_full: If True, reprocess all dates
    """
    logger.info("=" * 60)
    logger.info("Market Data Ingestion System")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Setup directories
    data_dir = DATA_DIR / "bhavcopy"
    db_path = Path(__file__).parent / "database" / "market_data.db"
    
    # Initialize components
    nse_downloader = NSEDownloader(data_dir)
    bse_downloader = BSEDownloader(data_dir)
    normalizer = DataNormalizer()
    db = MarketDatabase(db_path)
    
    # Define date range
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now() - timedelta(days=1)  # Yesterday
    
    # Get existing dates
    existing_nse_dates = set(db.get_available_dates('NSE'))
    existing_bse_dates = set(db.get_available_dates('BSE'))
    
    logger.info(f"Existing data: NSE={len(existing_nse_dates)} days, BSE={len(existing_bse_dates)} days")
    
    # Get all trading days
    all_trading_days = get_trading_days(start_date, end_date)
    
    # Determine which dates need processing
    # dates_to_process = []
    # for date in all_trading_days:
    #     date_str = date.strftime('%Y-%m-%d')
    

    dates_to_process = []
    for date in all_trading_days:
        # Check if the date is a string, and convert it to a datetime object if it is
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
            
        date_str = date.strftime('%Y-%m-%d')    
        
        if force_full:
            dates_to_process.append(date)
        else:
            # Check if we have both NSE and BSE data
            has_nse = date_str in existing_nse_dates
            has_bse = date_str in existing_bse_dates
            
            # If missing either, process this date
            if not has_nse or not has_bse:
                dates_to_process.append(date)
    
    if not dates_to_process:
        logger.success("All data is up to date! No processing needed.")
        return
    
    logger.info(f"Processing {len(dates_to_process)} dates (missing data)")
    
    # Process each date
    successful_days = 0
    for date in tqdm(dates_to_process, desc="Downloading bhavcopies"):
        date_str = date.strftime('%Y-%m-%d')
        nse_available = False
        bse_available = False
        
        # Check if NSE data already exists
        if date_str in existing_nse_dates and not force_full:
            logger.debug(f"NSE data already exists for {date_str}, skipping")
            nse_available = True
        else:
            # Download NSE
            try:
                nse_file = nse_downloader.download_bhavcopy(date)
                if nse_file and nse_file.exists():
                    df_nse = nse_downloader.parse_bhavcopy(nse_file)
                    if not df_nse.empty:
                        normalized = normalizer.normalize(df_nse, 'NSE')
                        db.insert_daily_prices(normalized)
                        nse_available = True
                        logger.debug(f"NSE data inserted for {date_str}")
            except Exception as e:
                logger.debug(f"NSE error for {date_str}: {e}")
        
        # Check if BSE data already exists
        if date_str in existing_bse_dates and not force_full:
            logger.debug(f"BSE data already exists for {date_str}, skipping")
            bse_available = True
        else:
            # Download BSE
            try:
                bse_file = bse_downloader.download_bhavcopy(date)
                if bse_file and bse_file.exists():
                    df_bse = bse_downloader.parse_bhavcopy(bse_file)
                    if not df_bse.empty:
                        normalized = normalizer.normalize(df_bse, 'BSE')
                        db.insert_daily_prices(normalized)
                        bse_available = True
                        logger.debug(f"BSE data inserted for {date_str}")
            except Exception as e:
                logger.debug(f"BSE error for {date_str}: {e}")
        
        # Update market status
        if nse_available or bse_available:
            db.update_market_status(date, nse_available, bse_available)
            successful_days += 1
        
        # Small delay to be respectful
        time.sleep(0.5)
    
    # Summary
    logger.success(f"Market data ingestion completed!")
    logger.info(f"Database: {db_path}")
    logger.info(f"Successfully processed {successful_days} days")
    
    # Get stats
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0]
        dates = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices").fetchone()[0]
        
        logger.info(f"Total records: {count:,}")
        logger.info(f"Trading days with data: {dates}")
        
        # Show NSE/BSE split
        nse_count = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'NSE'").fetchone()[0]
        bse_count = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
        nse_days = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices WHERE exchange = 'NSE'").fetchone()[0]
        bse_days = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
        
        logger.info(f"NSE: {nse_count:,} records, {nse_days} days")
        logger.info(f"BSE: {bse_count:,} records, {bse_days} days")

if __name__ == "__main__":
    import sys
    import time
    setup_logger()
    
    # Check for --full flag
    force_full = '--full' in sys.argv
    if force_full:
        logger.warning("Force full re-download enabled")
    
    ingest_market_data(force_full=force_full)