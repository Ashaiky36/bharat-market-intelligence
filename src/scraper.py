"""
Main scraper for Chittorgarh IPO data using curl_cffi
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from curl_cffi import requests
from .config import HEADERS, CHITTORGARH_API_URL, RETURN_PERIODS, YFINANCE_MAX_RETRIES, YFINANCE_RETRY_DELAY
from .utils import (
    parse_chittorgarh_date, 
    clean_price, 
    clean_percentage,
    safe_json_extract,
    setup_logger,
    retry_on_failure
)
import pandas as pd
import yfinance as yf
import time


class ChittorgarhScraper:
    """Main scraper class for Chittorgarh IPO data"""
    
    def __init__(self, impersonate: str = "chrome110", timeout: int = 30):
        """
        Initialize the scraper
        
        Args:
            impersonate: Browser to impersonate (chrome151, edge151, etc.)
            timeout: Request timeout in seconds
        """
        self.impersonate = impersonate
        self.timeout = timeout
        self.session = self._create_session()
        self.ipo_data = []
        
        # Setup logger
        setup_logger()
        logger.info(f"Initialized scraper with impersonation: {impersonate}")
    
    def _create_session(self):
        """Create a curl_cffi session with proper impersonation"""
        try:
            # Use Session for persistent cookies
            session = requests.Session()
            session.headers.update(HEADERS)
            
            # Test the session with a lightweight request
            logger.info("Testing session with API endpoint...")
            test_response = session.get(
                CHITTORGARH_API_URL,
                impersonate=self.impersonate,
                timeout=self.timeout,
                params={"v": "08-43"}  # Add timestamp parameter to avoid cache
            )
            
            if test_response.status_code == 200:
                logger.success("Session established successfully")
            else:
                logger.warning(f"Session test returned status {test_response.status_code}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    @retry_on_failure(max_retries=3, delay=2)
    def fetch_ipo_data(self) -> List[Dict[str, Any]]:
        """
        Fetch IPO data from Chittorgarh API
        
        Returns:
            List of IPO data dictionaries
        """
        try:
            logger.info("Fetching IPO data from Chittorgarh...")
            
            # Add timestamp to avoid caching
            # params = {"v": datetime.now().strftime("%H-%M")}
            params = {"search": "", "v": "08-43"}
            
            response = self.session.get(
                CHITTORGARH_API_URL,
                params=params,
                impersonate=self.impersonate,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"API returned status {response.status_code}")
                logger.debug(f"Response: {response.text[:500]}")
                return []
            
            # Parse JSON response
            data = response.json()
            
            # Check if response has the expected structure
            if not data.get('reportTableData'):
                logger.warning("No reportTableData found in response")
                logger.debug(f"Response keys: {data.keys()}")
                return []
            
            ipo_list = data['reportTableData']
            logger.info(f"Found {len(ipo_list)} IPOs in the response")
            
            # Process each IPO
            processed_data = []
            for ipo in ipo_list:
                processed = self._process_ipo_record(ipo)
                if processed:
                    processed_data.append(processed)
            
            self.ipo_data = processed_data
            logger.success(f"Successfully processed {len(processed_data)} IPOs")
            
            return processed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response.text[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error fetching IPO data: {e}")
            raise
    
    def _process_ipo_record(self, ipo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single IPO record and extract relevant fields
        
        Args:
            ipo: Raw IPO data from API
            
        Returns:
            Processed IPO data dictionary
        """
        try:
            # Extract basic fields
            company = ipo.get('Company', '').strip()
            if not company:
                return None
            
            # Parse dates
            opening_date = parse_chittorgarh_date(ipo.get('Opening Date', ''))
            listing_date = parse_chittorgarh_date(ipo.get('Listing Date', ''))
            
            # Get listing price details
            issue_price = clean_price(ipo.get('Issue Price (Rs.)', ''))
            close_price = clean_price(ipo.get('Close Price on Listing (Rs.)', ''))
            
            # Get symbols
            nse_symbol = ipo.get('NSE Symbol', '').strip()
            bse_scrip_code = ipo.get('BSE Scrip Code', '')
            
            # Processed data
            processed = {
                'company_name': company,
                'issue_category': ipo.get('Issue Category', '').strip(),
                'opening_date': opening_date,
                'listing_date': listing_date,
                'listing_exchange': ipo.get('Listing At', '').strip(),
                'isin': ipo.get('ISIN', '').strip(),
                'bse_scrip_code': bse_scrip_code,
                'nse_symbol': nse_symbol,
                'issue_price': issue_price,
                'listing_close_price': close_price,
                'url_slug': ipo.get('~urlrewrite_folder_name', '').strip(),
                'raw_data': ipo
            }
            
            # Calculate listing day gain/loss if we have both prices
            if issue_price and close_price and issue_price > 0:
                listing_gain = ((close_price - issue_price) / issue_price) * 100
                processed['listing_day_gain_percent'] = listing_gain
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing IPO record: {e}")
            return None
    
    def enrich_with_historical_data(self, ipo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich IPO data with historical price data using yfinance
        
        Args:
            ipo_data: List of processed IPO data
            
        Returns:
            Enriched IPO data with historical metrics
        """
        if not ipo_data:
            logger.warning("No IPO data to enrich")
            return ipo_data
        
        enriched_data = []
        
        for ipo in ipo_data:
            try:
                # Skip if no listing date or symbol
                if not ipo.get('listing_date') or not ipo.get('nse_symbol'):
                    logger.warning(f"Skipping {ipo.get('company_name')}: Missing listing date or symbol")
                    enriched_data.append(ipo)
                    continue
                
                nse_symbol = f"{ipo['nse_symbol']}.NS"  # NSE suffix for yfinance
                listing_date = ipo['listing_date']
                
                # Calculate periods for analysis
                periods_to_fetch = RETURN_PERIODS + [90, 180, 365]  # Add longer periods
                
                # Fetch historical data
                historical_data = self._fetch_historical_data(
                    nse_symbol, 
                    listing_date, 
                    max(periods_to_fetch)
                )
                
                if historical_data is None or historical_data.empty:
                    logger.warning(f"No historical data found for {nse_symbol}")
                    enriched_data.append(ipo)
                    continue
                
                # Calculate returns for different periods
                for days in periods_to_fetch:
                    period_key = f"return_{days}d"
                    ipo[period_key] = self._calculate_period_return(
                        historical_data, 
                        listing_date, 
                        days
                    )
                
                # Add current price
                current_price = self._get_current_price(historical_data)
                if current_price:
                    ipo['current_price'] = current_price
                    
                    # Calculate current gain/loss from issue price
                    if ipo.get('issue_price'):
                        ipo['current_gain_percent'] = (
                            (current_price - ipo['issue_price']) / ipo['issue_price']
                        ) * 100
                
                enriched_data.append(ipo)
                logger.debug(f"Enriched {ipo['company_name']} with historical data")
                
                # Be respectful with rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error enriching {ipo.get('company_name', 'Unknown')}: {e}")
                enriched_data.append(ipo)
        
        return enriched_data
    
    @retry_on_failure(max_retries=YFINANCE_MAX_RETRIES, delay=YFINANCE_RETRY_DELAY)
    def _fetch_historical_data(self, symbol: str, start_date: datetime, max_days: int) -> pd.DataFrame:
        """
        Fetch historical data from yfinance
        
        Args:
            symbol: NSE symbol with .NS suffix
            start_date: Listing date
            max_days: Number of days to fetch
            
        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            # Calculate end date (today)
            end_date = datetime.now()
            
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(
                start=start_date - pd.Timedelta(days=max_days),
                end=end_date
            )
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def _calculate_period_return(self, data: pd.DataFrame, listing_date: datetime, days: int) -> Optional[float]:
        """
        Calculate return for a specific period from listing date
        
        Args:
            data: Historical OHLCV data
            listing_date: IPO listing date
            days: Number of days to calculate return for
            
        Returns:
            Percentage return or None if not available
        """
        try:
            # Get listing day close price
            listing_date_normalized = listing_date.strftime('%Y-%m-%d')
            
            # Find the listing day data
            if listing_date_normalized not in data.index.strftime('%Y-%m-%d'):
                # Try to find the closest date
                closest_date = data.index[data.index >= listing_date]
                if closest_date.empty:
                    return None
                listing_date_idx = closest_date[0]
            else:
                listing_date_idx = listing_date
            
            listing_price = data.loc[listing_date_idx, 'Close']
            
            # Calculate target date
            target_date = listing_date + pd.Timedelta(days=days)
            target_date_str = target_date.strftime('%Y-%m-%d')
            
            # Find the closest date to target
            available_dates = data.index[data.index >= pd.Timestamp(target_date)]
            if available_dates.empty:
                return None
            
            actual_target_date = available_dates[0]
            target_price = data.loc[actual_target_date, 'Close']
            
            # Calculate return
            if listing_price > 0:
                return ((target_price - listing_price) / listing_price) * 100
            
            return None
            
        except Exception as e:
            logger.debug(f"Error calculating period return: {e}")
            return None
    
    def _get_current_price(self, data: pd.DataFrame) -> Optional[float]:
        """
        Get the latest available price
        
        Args:
            data: Historical OHLCV data
            
        Returns:
            Latest closing price or None
        """
        try:
            if data.empty:
                return None
            
            # Get the last row (most recent data)
            last_row = data.iloc[-1]
            return last_row['Close']
            
        except Exception as e:
            logger.debug(f"Error getting current price: {e}")
            return None
    
    def create_dataframe(self, ipo_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a pandas DataFrame from IPO data
        
        Args:
            ipo_data: List of IPO data dictionaries
            
        Returns:
            DataFrame with all IPO data
        """
        if not ipo_data:
            logger.warning("No data to create DataFrame")
            return pd.DataFrame()
        
        # Flatten the data for DataFrame
        flattened_data = []
        for ipo in ipo_data:
            # Remove raw_data to avoid duplication
            ipo_copy = {k: v for k, v in ipo.items() if k != 'raw_data'}
            
            # Convert dates to string for CSV
            if 'opening_date' in ipo_copy and ipo_copy['opening_date']:
                ipo_copy['opening_date'] = ipo_copy['opening_date'].strftime('%Y-%m-%d')
            if 'listing_date' in ipo_copy and ipo_copy['listing_date']:
                ipo_copy['listing_date'] = ipo_copy['listing_date'].strftime('%Y-%m-%d')
            
            flattened_data.append(ipo_copy)
        
        df = pd.DataFrame(flattened_data)
        
        # Reorder columns for better readability
        priority_columns = [
            'company_name', 'issue_category', 'nse_symbol', 'bse_scrip_code',
            'isin', 'issue_price', 'listing_close_price', 'listing_day_gain_percent',
            'current_price', 'current_gain_percent', 'listing_date', 'opening_date',
            'listing_exchange'
        ]
        
        # Add return columns
        return_columns = [f'return_{d}d' for d in RETURN_PERIODS]
        priority_columns.extend(return_columns)
        
        # Add remaining columns
        existing_columns = [col for col in priority_columns if col in df.columns]
        other_columns = [col for col in df.columns if col not in existing_columns]
        
        # Reorder
        df = df[existing_columns + other_columns]
        
        # Sort by listing date (most recent first)
        if 'listing_date' in df.columns:
            df = df.sort_values('listing_date', ascending=False)
        
        return df