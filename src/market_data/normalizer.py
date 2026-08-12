"""
Data normalizer for exchange-specific data
"""
import pandas as pd
from typing import Optional
from loguru import logger
from .base import DataNormalizer


class DataNormalizer(DataNormalizer):
    """Normalize exchange data to common schema"""
    
    COMMON_SCHEMA = {
        'date': 'datetime64[ns]',
        'exchange': 'object',
        'symbol': 'object',
        'security_id': 'object',
        'open': 'float64',
        'high': 'float64',
        'low': 'float64',
        'close': 'float64',
        'volume': 'int64',
        'previous_close': 'float64',
        'isin': 'object'
    }
    
    def normalize(self, df: pd.DataFrame, exchange: str) -> pd.DataFrame:
        """
        Normalize DataFrame to common schema
        
        Args:
            df: Exchange-specific DataFrame
            exchange: Exchange name
            
        Returns:
            Normalized DataFrame
        """
        if df.empty:
            return df
        
        try:
            # Ensure required columns exist
            required_cols = ['date', 'symbol', 'close']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                logger.error(f"Missing required columns: {missing}")
                return pd.DataFrame()
            
            # Create normalized DataFrame
            normalized = pd.DataFrame()
            
            # Copy existing columns
            for col, dtype in self.COMMON_SCHEMA.items():
                if col in df.columns:
                    normalized[col] = df[col]
                elif col == 'exchange':
                    normalized[col] = exchange
                else:
                    normalized[col] = None
            
            # Ensure data types
            for col, dtype in self.COMMON_SCHEMA.items():
                if col in normalized.columns:
                    try:
                        normalized[col] = normalized[col].astype(dtype)
                    except Exception as e:
                        logger.debug(f"Could not convert {col} to {dtype}: {e}")
            
            # Set security_id as string
            if 'security_id' in normalized.columns:
                normalized['security_id'] = normalized['security_id'].astype(str)
            
            # Ensure symbol is uppercase and stripped
            if 'symbol' in normalized.columns:
                normalized['symbol'] = normalized['symbol'].str.upper().str.strip()
            
            # Remove rows with invalid close price
            normalized = normalized[normalized['close'].notna()]
            normalized = normalized[normalized['close'] > 0]
            
            # Remove duplicates (keep latest if duplicate)
            if 'date' in normalized.columns and 'symbol' in normalized.columns:
                normalized = normalized.drop_duplicates(
                    subset=['date', 'exchange', 'symbol'], 
                    keep='first'
                )
            
            logger.debug(f"Normalized {len(normalized)} records for {exchange}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            return pd.DataFrame()