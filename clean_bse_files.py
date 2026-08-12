# # clean_bse_files.py

# """
# Clean corrupt BSE files and re-download valid ones
# """
# import sys
# from pathlib import Path
# from datetime import datetime
# from loguru import logger
# import pandas as pd

# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent))

# from src.market_data.bse import BSEDownloader
# from src.market_data.database import MarketDatabase
# from src.market_data.normalizer import DataNormalizer
# from src.config import DATA_DIR
# from src.utils import setup_logger


# def clean_bse_files():
#     """Clean corrupt BSE files and re-download"""
#     logger.info("=" * 60)
#     logger.info("BSE File Cleanup and Re-download")
#     logger.info("=" * 60)
    
#     # Setup
#     data_dir = DATA_DIR / "bhavcopy"
#     bse_dir = data_dir / "bse"
#     db_path = Path(__file__).parent / "database" / "market_data.db"
    
#     # Initialize components
#     downloader = BSEDownloader(data_dir)
#     normalizer = DataNormalizer()
#     db = MarketDatabase(db_path)
    
#     # Find all BSE files
#     bse_files = list(bse_dir.glob("EQ*.csv"))
    
#     logger.info(f"Found {len(bse_files)} BSE files")
    
#     valid_count = 0
#     corrupt_count = 0
#     re_downloaded_count = 0
#     success_count = 0
    
#     for file_path in bse_files:
#         try:
#             # Check if file is valid
#             is_valid = downloader._validate_bse_file(file_path)
            
#             if is_valid:
#                 logger.debug(f"Valid: {file_path.name}")
#                 valid_count += 1
#                 continue
#             else:
#                 logger.warning(f"Corrupt: {file_path.name}")
#                 corrupt_count += 1
                
#                 # Delete corrupt file
#                 file_path.unlink()
#                 logger.debug(f"Deleted: {file_path.name}")
                
#                 # Try to re-download
#                 date_str = file_path.stem.replace('EQ', '')
#                 try:
#                     date = datetime.strptime(date_str[:8], '%d%m%Y')
                    
#                     logger.info(f"Re-downloading BSE data for {date.strftime('%Y-%m-%d')}")
#                     new_file = downloader.download_bhavcopy(date, force=True)
                    
#                     if new_file and downloader._validate_bse_file(new_file):
#                         logger.success(f"Successfully re-downloaded: {new_file.name}")
#                         re_downloaded_count += 1
                        
#                         # Parse and insert into database
#                         df = downloader.parse_bhavcopy(new_file)
#                         if not df.empty:
#                             normalized = normalizer.normalize(df, 'BSE')
#                             db.insert_daily_prices(normalized)
#                             logger.debug(f"Inserted {len(df)} BSE records into database")
#                             success_count += 1
#                     else:
#                         logger.warning(f"Failed to re-download BSE data for {date.strftime('%Y-%m-%d')}")
                        
#                 except Exception as e:
#                     logger.error(f"Error processing {file_path.name}: {e}")
                
#         except Exception as e:
#             logger.error(f"Error processing {file_path}: {e}")
    
#     # Summary
#     logger.info("\n" + "=" * 60)
#     logger.info("Summary")
#     logger.info("=" * 60)
#     logger.info(f"Total BSE files: {len(bse_files)}")
#     logger.info(f"Valid files: {valid_count}")
#     logger.info(f"Corrupt files: {corrupt_count}")
#     logger.info(f"Re-downloaded: {re_downloaded_count}")
#     logger.info(f"Successfully inserted: {success_count}")
    
#     # Get database stats
#     with sqlite3.connect(db_path) as conn:
#         bse_records = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
#         bse_days = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
#         logger.info(f"BSE records in database: {bse_records:,}")
#         logger.info(f"BSE trading days in database: {bse_days}")


# if __name__ == "__main__":
#     import sqlite3
#     setup_logger()
#     clean_bse_files()

# clean_bse_files.py

"""
Clean corrupt BSE files and re-download valid ones
"""
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
import pandas as pd
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.market_data.bse import BSEDownloader
from src.market_data.database import MarketDatabase
from src.market_data.normalizer import DataNormalizer
from src.market_data.holidays import get_trading_days
from src.config import DATA_DIR
from src.utils import setup_logger


def clean_bse_files():
    """Clean corrupt BSE files and re-download"""
    logger.info("=" * 60)
    logger.info("BSE File Cleanup and Re-download")
    logger.info("=" * 60)
    
    # Setup
    data_dir = DATA_DIR / "bhavcopy"
    bse_dir = data_dir / "bse"
    db_path = Path(__file__).parent / "database" / "market_data.db"
    
    # Initialize components
    downloader = BSEDownloader(data_dir)
    normalizer = DataNormalizer()
    db = MarketDatabase(db_path)
    
    # Step 1: Clean up existing BSE directory
    logger.info("Cleaning up BSE directory...")
    
    # Remove all existing CSV files (they're corrupt)
    csv_files = list(bse_dir.glob("*.csv"))
    zip_files = list(bse_dir.glob("*.zip"))
    
    logger.info(f"Found {len(csv_files)} CSV files and {len(zip_files)} ZIP files")
    
    # Move corrupt files to backup
    backup_dir = bse_dir / "backup_corrupt"
    backup_dir.mkdir(exist_ok=True)
    
    for file in csv_files:
        try:
            if file.name != "EQ01012026.csv":  # Keep if valid
                shutil.move(str(file), str(backup_dir / file.name))
                logger.debug(f"Moved {file.name} to backup")
        except Exception as e:
            logger.debug(f"Could not move {file.name}: {e}")
    
    # Also move any old zip files
    for file in zip_files:
        try:
            if not file.name.startswith("EQ"):  # Keep our extracted files
                shutil.move(str(file), str(backup_dir / file.name))
                logger.debug(f"Moved {file.name} to backup")
        except Exception as e:
            logger.debug(f"Could not move {file.name}: {e}")
    
    # Step 2: Get all trading days in 2026
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    trading_days = get_trading_days(start_date, end_date)
    
    logger.info(f"Processing {len(trading_days)} trading days")
    
    successful_days = 0
    failed_days = 0
    
    # Step 3: Download BSE data for each trading day
    for date in trading_days:
        try:
            logger.info(f"Downloading BSE data for {date.strftime('%Y-%m-%d')}")
            
            # Download with force=True to ensure fresh download
            file_path = downloader.download_bhavcopy(date, force=True)
            
            if file_path and file_path.exists():
                # Parse and insert into database
                df = downloader.parse_bhavcopy(file_path)
                if not df.empty:
                    normalized = normalizer.normalize(df, 'BSE')
                    rows = db.insert_daily_prices(normalized)
                    successful_days += 1
                    logger.success(f"✓ Inserted {rows} records for {date.strftime('%Y-%m-%d')}")
                else:
                    failed_days += 1
                    logger.warning(f"✗ No data parsed for {date.strftime('%Y-%m-%d')}")
            else:
                failed_days += 1
                logger.warning(f"✗ Download failed for {date.strftime('%Y-%m-%d')}")
                
        except Exception as e:
            failed_days += 1
            logger.error(f"✗ Error processing {date.strftime('%Y-%m-%d')}: {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    logger.info(f"Total trading days: {len(trading_days)}")
    logger.info(f"Successful downloads: {successful_days}")
    logger.info(f"Failed downloads: {failed_days}")
    
    # Get database stats
    with sqlite3.connect(db_path) as conn:
        bse_records = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
        bse_days = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices WHERE exchange = 'BSE'").fetchone()[0]
        logger.info(f"BSE records in database: {bse_records:,}")
        logger.info(f"BSE trading days in database: {bse_days}")
        
        # Check NSE records for comparison
        nse_records = conn.execute("SELECT COUNT(*) FROM daily_prices WHERE exchange = 'NSE'").fetchone()[0]
        nse_days = conn.execute("SELECT COUNT(DISTINCT date) FROM daily_prices WHERE exchange = 'NSE'").fetchone()[0]
        logger.info(f"NSE records in database: {nse_records:,}")
        logger.info(f"NSE trading days in database: {nse_days}")


if __name__ == "__main__":
    import sqlite3
    setup_logger()
    clean_bse_files()