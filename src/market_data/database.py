"""
SQLite database operations for market data
"""
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from loguru import logger


class MarketDatabase:
    """SQLite database for market data"""
    
    def __init__(self, db_path: Path):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Daily prices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_prices (
                    date TEXT,
                    exchange TEXT,
                    symbol TEXT,
                    security_id TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    previous_close REAL,
                    isin TEXT,
                    PRIMARY KEY (date, exchange, symbol)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol ON daily_prices(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_prices_exchange ON daily_prices(exchange)")
            
            # IPO master table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ipo_master (
                    ipo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    issue_category TEXT,
                    issue_price REAL,
                    listing_date TEXT,
                    listing_price REAL,
                    nse_symbol TEXT,
                    bse_code TEXT,
                    isin TEXT,
                    sector TEXT,
                    industry TEXT,
                    url_slug TEXT,
                    created_at TEXT
                )
            """)
            
            # IPO performance table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ipo_performance (
                    ipo_id INTEGER,
                    exchange TEXT,
                    symbol TEXT,
                    security_id TEXT,
                    listing_price REAL,
                    
                    day_2_return REAL, day_2_date TEXT, day_2_price REAL,
                    day_5_return REAL, day_5_date TEXT, day_5_price REAL,
                    day_10_return REAL, day_10_date TEXT, day_10_price REAL,
                    day_15_return REAL, day_15_date TEXT, day_15_price REAL,
                    
                    month_1_return REAL, month_1_date TEXT, month_1_price REAL,
                    month_2_return REAL, month_2_date TEXT, month_2_price REAL,
                    month_3_return REAL, month_3_date TEXT, month_3_price REAL,
                    
                    current_return REAL, current_date TEXT, current_price REAL,
                    
                    PRIMARY KEY (ipo_id, exchange)
                )
            """)
            
            # Market status table (to track which dates we have)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_status (
                    date TEXT PRIMARY KEY,
                    nse_available INTEGER,
                    bse_available INTEGER,
                    created_at TEXT
                )
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def insert_daily_prices(self, df: pd.DataFrame) -> int:
        """
        Insert daily prices into database
        
        Args:
            df: DataFrame with daily prices
            
        Returns:
            Number of rows inserted
        """
        if df.empty:
            return 0
        
        try:
            # Convert date to string
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # Replace NaN with None for SQLite
            df = df.where(pd.notnull(df), None)
            
            # Insert using executemany
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Use INSERT OR REPLACE to handle duplicates
                query = """
                INSERT OR REPLACE INTO daily_prices (
                    date, exchange, symbol, security_id, open, high, low, close,
                    volume, previous_close, isin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = df[[
                    'date', 'exchange', 'symbol', 'security_id', 'open', 'high',
                    'low', 'close', 'volume', 'previous_close', 'isin'
                ]].values.tolist()
                
                cursor.executemany(query, values)
                conn.commit()
                
                logger.info(f"Inserted {len(values)} rows into daily_prices")
                return len(values)
                
        except Exception as e:
            logger.error(f"Error inserting daily prices: {e}")
            return 0
    
    def get_prices_for_symbol(
        self, 
        symbol: str, 
        exchange: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Get prices for a specific symbol
        
        Args:
            symbol: Symbol to query
            exchange: Exchange (NSE/BSE)
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            DataFrame with price data
        """
        query = """
        SELECT * FROM daily_prices
        WHERE symbol = ? AND exchange = ?
        """
        params = [symbol, exchange]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.strftime('%Y-%m-%d'))
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.strftime('%Y-%m-%d'))
        
        query += " ORDER BY date ASC"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting prices for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_trading_days(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """
        Get list of trading days between two dates
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of trading days
        """
        query = """
        SELECT DISTINCT date FROM daily_prices
        WHERE date >= ? AND date <= ?
        ORDER BY date ASC
        """
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(
                    query, 
                    conn, 
                    params=[start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
                )
            
            return pd.to_datetime(df['date']).tolist()
            
        except Exception as e:
            logger.error(f"Error getting trading days: {e}")
            return []
    
    def update_market_status(self, date: datetime, nse_available: bool, bse_available: bool):
        """
        Update market status for a specific date
        
        Args:
            date: Date to update
            nse_available: Whether NSE data is available
            bse_available: Whether BSE data is available
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO market_status (date, nse_available, bse_available, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                date.strftime('%Y-%m-%d'),
                1 if nse_available else 0,
                1 if bse_available else 0,
                datetime.now().isoformat()
            ))
            conn.commit()
            

    def get_available_dates(self, exchange: Optional[str] = None) -> List[str]:
        """
        Get list of dates already in the database
        
        Args:
            exchange: Optional exchange filter (NSE/BSE)
            
        Returns:
            List of date strings in YYYY-MM-DD format
        """
        query = "SELECT DISTINCT date FROM daily_prices"
        params = []
        
        if exchange:
            query += " WHERE exchange = ?"
            params.append(exchange)
        
        query += " ORDER BY date"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df['date'].tolist()
        except Exception as e:
            logger.error(f"Error getting available dates: {e}")
            return []

    def get_last_processed_date(self, exchange: Optional[str] = None) -> Optional[datetime]:
        """
        Get the latest date in the database
        
        Args:
            exchange: Optional exchange filter
            
        Returns:
            Latest date or None
        """
        query = "SELECT MAX(date) FROM daily_prices"
        params = []
        
        if exchange:
            query += " WHERE exchange = ?"
            params.append(exchange)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute(query, params).fetchone()
                if result and result[0]:
                    return datetime.strptime(result[0], '%Y-%m-%d')
                return None
        except Exception as e:
            logger.error(f"Error getting last processed date: {e}")
            return None            