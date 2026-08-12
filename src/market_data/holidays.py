"""
Trading holidays for NSE and BSE
"""
from datetime import datetime, timedelta

# Trading holidays for 2026
TRADING_HOLIDAYS_2026 = {
    "2026-01-15",  # Municipal Corporation Election - Maharashtra
    "2026-01-26",  # Republic Day
    "2026-02-11",  # Dr. Babasaheb Ambedkar Jayanti (observed)
    "2026-03-03",  # Holi
    "2026-03-26",  # Shri Ram Navami
    "2026-03-31",  # Shri Mahavir Jayanti
    "2026-04-03",  # Good Friday
    "2026-04-14",  # Dr. Baba Saheb Ambedkar Jayanti
    "2026-05-01",  # Maharashtra Day
    "2026-05-28",  # Bakri Id
    "2026-06-26",  # Muharram
    "2026-08-15",  # Independence Day
    "2026-09-14",  # Ganesh Chaturthi
    "2026-10-02",  # Mahatma Gandhi Jayanti
    "2026-10-20",  # Dussehra
    "2026-11-10",  # Diwali-Balipratipada
    "2026-11-24",  # Prakash Gurpurb Sri Guru Nanak Dev
    "2026-12-25",  # Christmas
}

def is_trading_day(date: datetime) -> bool:
    """
    Check if a given date is a trading day
    
    Args:
        date: Date to check
        
    Returns:
        True if trading day, False otherwise
    """
    # Check weekend (Saturday=5, Sunday=6)
    if date.weekday() >= 5:
        return False
    
    # Check holiday
    date_str = date.strftime("%Y-%m-%d")
    if date_str in TRADING_HOLIDAYS_2026:
        return False
    
    return True

def get_last_trading_day(date: datetime) -> datetime:
    """
    Get the last trading day on or before the given date
    
    Args:
        date: Date to check from
        
    Returns:
        Last trading day
    """
    current = date
    while not is_trading_day(current):
        current -= timedelta(days=1)
    return current

def get_next_trading_day(date: datetime) -> datetime:
    """
    Get the next trading day on or after the given date
    
    Args:
        date: Date to check from
        
    Returns:
        Next trading day
    """
    current = date
    while not is_trading_day(current):
        current += timedelta(days=1)
    return current

def get_trading_days(start_date: datetime, end_date: datetime) -> list:
    """
    Get all trading days between two dates
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of trading days
    """
    trading_days = []
    current = start_date
    while current <= end_date:
        if is_trading_day(current):
            trading_days.append(current)
        current += timedelta(days=1)
    return trading_days