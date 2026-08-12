"""
IPO performance analyzer using market database
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger
import sqlite3
from .market_data.database import MarketDatabase


class IPOAnalyzer:
    """Analyze IPO performance using market data"""
    
    def __init__(self, db_path: Path):
        """
        Initialize analyzer
        
        Args:
            db_path: Path to market database
        """
        self.db = MarketDatabase(db_path)
        self.performance_cache = {}
    
    def analyze_ipo(
        self,
        symbol: str,
        exchange: str,
        listing_date: datetime,
        issue_price: float,
        ipo_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single IPO's performance
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE/BSE)
            listing_date: Listing date
            issue_price: Issue price
            ipo_id: Optional IPO ID for database storage
            
        Returns:
            Performance metrics
        """
        try:
            # Get price data from listing date onward
            df = self.db.get_prices_for_symbol(
                symbol=symbol,
                exchange=exchange,
                start_date=listing_date
            )
            
            if df.empty:
                logger.warning(f"No price data found for {symbol} on {exchange}")
                return {}
            
            # Convert dates and set index
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Get listing price (first available close)
            listing_price = df.iloc[0]['close']
            
            # Calculate performance metrics
            performance = {
                'symbol': symbol,
                'exchange': exchange,
                'listing_date': listing_date,
                'issue_price': issue_price,
                'listing_price': listing_price,
                'listing_gain_percent': ((listing_price - issue_price) / issue_price) * 100
            }
            
            # Calculate period returns
            periods = [
                (2, 'day_2'), (5, 'day_5'), (10, 'day_10'), (15, 'day_15'),
                (30, 'month_1'), (60, 'month_2'), (90, 'month_3')
            ]
            
            for days, prefix in periods:
                metric = self._calculate_period_return(df, days)
                if metric:
                    performance[f'{prefix}_date'] = metric['date']
                    performance[f'{prefix}_price'] = metric['price']
                    performance[f'{prefix}_return'] = metric['return']
            
            # Calculate current return
            current = self._get_current_return(df, listing_price)
            if current:
                performance['current_date'] = current['date']
                performance['current_price'] = current['price']
                performance['current_return'] = current['return']
            
            # Store in cache
            cache_key = f"{exchange}_{symbol}_{listing_date.strftime('%Y%m%d')}"
            self.performance_cache[cache_key] = performance
            
            # Store in database if ipo_id provided
            if ipo_id:
                self._store_performance(ipo_id, exchange, symbol, performance)
            
            return performance
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {}
    
    def _calculate_period_return(self, df: pd.DataFrame, days: int) -> Optional[Dict]:
        """
        Calculate return after N trading days
        
        Args:
            df: Price data sorted by date
            days: Number of trading days
            
        Returns:
            Dictionary with date, price, and return
        """
        if len(df) < days + 1:
            return None
        
        try:
            # Get listing price (first row)
            listing_price = df.iloc[0]['close']
            
            # Get target row (Nth trading day)
            target_idx = min(days, len(df) - 1)
            target_row = df.iloc[target_idx]
            
            target_date = target_row['date']
            target_price = target_row['close']
            
            if listing_price <= 0:
                return None
            
            return {
                'date': target_date,
                'price': target_price,
                'return': ((target_price - listing_price) / listing_price) * 100
            }
            
        except Exception as e:
            logger.debug(f"Error calculating {days}-day return: {e}")
            return None
    
    def _get_current_return(self, df: pd.DataFrame, listing_price: float) -> Optional[Dict]:
        """
        Calculate current return from listing price
        
        Args:
            df: Price data
            listing_price: Listing price
            
        Returns:
            Dictionary with date, price, and return
        """
        try:
            if df.empty or listing_price <= 0:
                return None
            
            # Get last row (most recent)
            last_row = df.iloc[-1]
            
            return {
                'date': last_row['date'],
                'price': last_row['close'],
                'return': ((last_row['close'] - listing_price) / listing_price) * 100
            }
            
        except Exception as e:
            logger.debug(f"Error calculating current return: {e}")
            return None
    
    def _store_performance(
        self,
        ipo_id: int,
        exchange: str,
        symbol: str,
        performance: Dict[str, Any]
    ):
        """
        Store performance metrics in database
        
        Args:
            ipo_id: IPO ID
            exchange: Exchange
            symbol: Symbol
            performance: Performance metrics
        """
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Build query dynamically based on available data
                columns = [
                    'ipo_id', 'exchange', 'symbol', 'security_id',
                    'listing_price'
                ]
                placeholders = ['?', '?', '?', '?', '?']
                values = [
                    ipo_id, exchange, symbol, symbol,
                    performance.get('listing_price', 0)
                ]
                
                # Add period data
                period_mappings = [
                    ('day_2', 'day_2_return', 'day_2_date', 'day_2_price'),
                    ('day_5', 'day_5_return', 'day_5_date', 'day_5_price'),
                    ('day_10', 'day_10_return', 'day_10_date', 'day_10_price'),
                    ('day_15', 'day_15_return', 'day_15_date', 'day_15_price'),
                    ('month_1', 'month_1_return', 'month_1_date', 'month_1_price'),
                    ('month_2', 'month_2_return', 'month_2_date', 'month_2_price'),
                    ('month_3', 'month_3_return', 'month_3_date', 'month_3_price'),
                    ('current', 'current_return', 'current_date', 'current_price'),
                ]
                
                for prefix, ret_col, date_col, price_col in period_mappings:
                    if f'{prefix}_return' in performance:
                        columns.extend([ret_col, date_col, price_col])
                        placeholders.extend(['?', '?', '?'])
                        values.extend([
                            performance.get(f'{prefix}_return'),
                            performance.get(f'{prefix}_date'),
                            performance.get(f'{prefix}_price')
                        ])
                
                # Build INSERT OR REPLACE query
                query = f"""
                INSERT OR REPLACE INTO ipo_performance 
                ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """
                
                conn.execute(query, values)
                conn.commit()
                
                logger.debug(f"Stored performance for IPO {ipo_id} on {exchange}")
                
        except Exception as e:
            logger.error(f"Error storing performance: {e}")
    
    def analyze_all_ipos(self, ipo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze all IPOs in the dataset
        
        Args:
            ipo_data: List of IPO data dictionaries
            
        Returns:
            List with performance metrics added
        """
        results = []
        
        for ipo in ipo_data:
            try:
                # Determine exchange and symbol
                nse_symbol = ipo.get('nse_symbol')
                bse_code = ipo.get('bse_scrip_code')
                
                if nse_symbol and ipo.get('listing_date'):
                    # Try NSE first
                    performance = self.analyze_ipo(
                        symbol=nse_symbol,
                        exchange='NSE',
                        listing_date=ipo['listing_date'],
                        issue_price=ipo.get('issue_price', 0),
                        ipo_id=ipo.get('ipo_id')
                    )
                    
                    if performance:
                        ipo['nse_performance'] = performance
                
                if bse_code and ipo.get('listing_date'):
                    # Try BSE
                    performance = self.analyze_ipo(
                        symbol=str(bse_code),
                        exchange='BSE',
                        listing_date=ipo['listing_date'],
                        issue_price=ipo.get('issue_price', 0),
                        ipo_id=ipo.get('ipo_id')
                    )
                    
                    if performance:
                        ipo['bse_performance'] = performance
                
                results.append(ipo)
                
            except Exception as e:
                logger.error(f"Error analyzing IPO {ipo.get('company_name')}: {e}")
                results.append(ipo)
        
        return results