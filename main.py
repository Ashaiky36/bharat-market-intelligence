# """
# Main entry point for the IPO scraper
# """
# import sys
# from pathlib import Path
# from loguru import logger
# import pandas as pd
# from datetime import datetime

# # Add src to path
# sys.path.insert(0, str(Path(__file__).parent))

# from src.scraper import ChittorgarhScraper
# from src.data_processor import DataProcessor
# from src.config import OUTPUT_CSV, DATA_DIR
# from src.utils import setup_logger


# def main():
#     """Main execution function"""
#     logger.info("=" * 60)
#     logger.info("IPO Metadata Scraper for Chittorgarh")
#     logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     logger.info("=" * 60)
    
#     try:
#         # Initialize scraper
#         # scraper = ChittorgarhScraper(impersonate="chrome151")
#         scraper = ChittorgarhScraper(impersonate="chrome110")
        
#         # Fetch IPO data
#         ipo_data = scraper.fetch_ipo_data()
        
#         if not ipo_data:
#             logger.error("No IPO data fetched. Exiting.")
#             return
        
#         logger.info(f"Fetched {len(ipo_data)} IPO records")
        
#         # Enrich with historical data (optional - can be time-consuming)
#         logger.info("Starting historical data enrichment (this may take a while)...")
#         enriched_data = scraper.enrich_with_historical_data(ipo_data)
        
#         # Create DataFrame
#         df = scraper.create_dataframe(enriched_data)
        
#         if df.empty:
#             logger.error("No data to process. Exiting.")
#             return
        
#         logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
#         # Process data
#         processor = DataProcessor(df)
        
#         # Generate summary statistics
#         summary = processor.get_summary_statistics()
#         logger.info("Summary Statistics:")
#         for key, value in summary.items():
#             if isinstance(value, (int, float)):
#                 logger.info(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
        
#         # Export to CSV
#         output_path = DATA_DIR / f"ipo_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         processor.export_to_csv(output_path)
        
#         # Generate HTML report (optional)
#         try:
#             reports_dir = Path(__file__).parent / "reports"
#             reports_dir.mkdir(exist_ok=True)
#             processor.generate_html_report(reports_dir / f"ipo_report_{datetime.now().strftime('%Y%m%d')}.html")
#         except Exception as e:
#             logger.warning(f"Could not generate HTML report: {e}")
        
#         # Display top performers
#         logger.info("\nTop 5 IPOs by Listing Day Gain:")
#         top_performers = processor.get_top_performers(n=5)
#         if not top_performers.empty:
#             print(top_performers.to_string(index=False))
        
#         logger.success(f"\nScraping completed successfully! Data saved to: {output_path}")
        
#     except KeyboardInterrupt:
#         logger.warning("Scraping interrupted by user")
#         sys.exit(0)
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         logger.exception("Full traceback:")
#         sys.exit(1)


# if __name__ == "__main__":
#     main()

"""
Main entry point for the IPO scraper with market data integration
"""
import sys
from pathlib import Path
from loguru import logger
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper import ChittorgarhScraper
from src.data_processor import DataProcessor
from src.ipo_analyzer import IPOAnalyzer
from src.config import DATA_DIR
from src.utils import setup_logger


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("IPO Metadata Scraper with Market Data Integration")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # Initialize scraper
        scraper = ChittorgarhScraper(impersonate="chrome110")
        
        # Fetch IPO data
        ipo_data = scraper.fetch_ipo_data()
        
        if not ipo_data:
            logger.error("No IPO data fetched. Exiting.")
            return
        
        logger.info(f"Fetched {len(ipo_data)} IPO records")
        
        # Initialize IPO analyzer with market database
        db_path = Path(__file__).parent / "database" / "market_data.db"
        analyzer = IPOAnalyzer(db_path)
        
        # Analyze all IPOs using market database
        logger.info("Analyzing IPO performance using market database...")
        enriched_data = analyzer.analyze_all_ipos(ipo_data)
        
        # Create DataFrame
        df = scraper.create_dataframe(enriched_data)
        
        if df.empty:
            logger.error("No data to process. Exiting.")
            return
        
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        # Process data
        processor = DataProcessor(df)
        
        # Generate summary statistics
        summary = processor.get_summary_statistics()
        logger.info("Summary Statistics:")
        for key, value in summary.items():
            if isinstance(value, (int, float)):
                logger.info(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
        
        # Export to CSV
        output_path = DATA_DIR / f"ipo_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        processor.export_to_csv(output_path)
        
        # Display top performers
        logger.info("\nTop 5 IPOs by Listing Day Gain:")
        top_performers = processor.get_top_performers(n=5)
        if not top_performers.empty:
            print(top_performers.to_string(index=False))
        
        logger.success(f"\nScraping completed successfully! Data saved to: {output_path}")
        
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()