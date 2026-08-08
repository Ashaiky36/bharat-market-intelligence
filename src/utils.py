"""
Utility functions for the IPO scraper
"""
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from pathlib import Path
import pandas as pd


def setup_logger(log_file: Optional[Path] = None) -> None:
    """
    Setup logger configuration
    """
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=True
    )
    
    # Add file handler if log_file is provided
    if log_file:
        logger.add(
            log_file,
            format=log_format,
            level="DEBUG",
            rotation="10 MB",
            retention="30 days"
        )


def parse_chittorgarh_date(date_str: str) -> Optional[datetime]:
    """
    Parse date strings from Chittorgarh API
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        # Try ISO format
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # Try DD-MMM-YYYY format
        return datetime.strptime(date_str, "%d-%b-%Y")
    except Exception as e:
        logger.warning(f"Failed to parse date '{date_str}': {e}")
        return None


def clean_price(price_str: str) -> Optional[float]:
    """
    Clean price string and convert to float
    
    Args:
        price_str: Price string with possible formatting
        
    Returns:
        float value or None if conversion fails
    """
    if not price_str or not str(price_str).strip():
        return None
    
    try:
        # Remove currency symbols, commas, and extra spaces
        cleaned = str(price_str).replace('₹', '').replace(',', '').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def clean_percentage(perc_str: str) -> Optional[float]:
    """
    Clean percentage string and convert to float
    
    Args:
        perc_str: Percentage string with HTML tags and formatting
        
    Returns:
        float value or None if conversion fails
    """
    if not perc_str:
        return None
    
    try:
        # Remove HTML tags
        import re
        cleaned = re.sub(r'<[^>]+>', '', perc_str).strip()
        
        # Remove % sign and spaces
        cleaned = cleaned.replace('%', '').strip()
        
        return float(cleaned) if cleaned else None
    except (ValueError, AttributeError):
        return None


def safe_json_extract(data: Dict[str, Any], keys: list, default=None):
    """
    Safely extract nested values from JSON data
    
    Args:
        data: Dictionary to extract from
        keys: List of keys for nested access
        default: Default value if any key is missing
        
    Returns:
        Extracted value or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def calculate_percentage_change(initial: float, current: float) -> Optional[float]:
    """
    Calculate percentage change between two values
    
    Args:
        initial: Initial value
        current: Current value
        
    Returns:
        Percentage change or None if calculation fails
    """
    try:
        if not initial or initial == 0:
            return None
        return ((current - initial) / initial) * 100
    except (TypeError, ZeroDivisionError):
        return None


def format_currency(value: float) -> str:
    """
    Format a number as Indian currency
    
    Args:
        value: Number to format
        
    Returns:
        Formatted currency string
    """
    if not value:
        return "N/A"
    
    try:
        # Format with Indian numbering system
        from decimal import Decimal
        from decimal import getcontext
        
        getcontext().prec = 2
        d = Decimal(str(value))
        
        if d >= 10000000:  # 1 crore
            return f"₹{d/10000000:.2f} Cr"
        elif d >= 100000:  # 1 lakh
            return f"₹{d/100000:.2f} L"
        else:
            return f"₹{d:,.2f}"
    except Exception:
        return f"₹{value:,.2f}"


def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """
    Decorator to retry a function on failure
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator


def save_dataframe_to_csv(df: pd.DataFrame, filepath: Path, **kwargs) -> None:
    """
    Save DataFrame to CSV with error handling
    
    Args:
        df: DataFrame to save
        filepath: Path to save the CSV
        **kwargs: Additional arguments for to_csv
    """
    try:
        df.to_csv(filepath, index=False, **kwargs)
        logger.success(f"Data saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        raise


# Import sys for logger setup
import sys