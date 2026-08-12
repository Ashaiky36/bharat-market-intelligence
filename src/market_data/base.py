"""
Base classes for market data ingestion
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
from pathlib import Path


class MarketDataDownloader(ABC):
    """Base class for exchange data downloaders"""
    
    def __init__(self, data_dir: Path):
        """
        Initialize downloader
        
        Args:
            data_dir: Directory to store raw data files
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def download_bhavcopy(self, date: datetime) -> Optional[Path]:
        """
        Download bhavcopy for a specific date
        
        Args:
            date: Date to download
            
        Returns:
            Path to downloaded file or None if failed
        """
        pass
    
    @abstractmethod
    def parse_bhavcopy(self, file_path: Path) -> pd.DataFrame:
        """
        Parse bhavcopy file into standardized format
        
        Args:
            file_path: Path to bhavcopy file
            
        Returns:
            DataFrame with market data
        """
        pass
    
    @abstractmethod
    def get_exchange_name(self) -> str:
        """Get exchange name (NSE/BSE)"""
        pass


class DataNormalizer(ABC):
    """Base class for data normalization"""
    
    @abstractmethod
    def normalize(self, df: pd.DataFrame, exchange: str) -> pd.DataFrame:
        """
        Normalize exchange-specific data to common schema
        
        Args:
            df: Exchange-specific DataFrame
            exchange: Exchange name
            
        Returns:
            Normalized DataFrame with common schema
        """
        pass