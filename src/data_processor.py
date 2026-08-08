"""
Data processing and analysis utilities
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from loguru import logger
from pathlib import Path
from .config import OUTPUT_CSV, RETURN_PERIODS
# import pandas_ta as ta
import ta


class DataProcessor:
    """Process and analyze IPO data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with IPO DataFrame
        
        Args:
            df: DataFrame from ChittorgarhScraper
        """
        self.df = df
        self._clean_data()
        self._add_technical_indicators()
    
    def _clean_data(self) -> None:
        """Clean and prepare data"""
        if self.df.empty:
            logger.warning("Empty DataFrame provided")
            return
        
        # Convert numeric columns
        numeric_columns = [
            'issue_price', 'listing_close_price', 'current_price',
            'listing_day_gain_percent', 'current_gain_percent'
        ]
        
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Clean percentage columns
        percentage_columns = ['listing_day_gain_percent', 'current_gain_percent']
        for col in percentage_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].round(2)
        
        # Add return period columns
        for days in RETURN_PERIODS:
            col = f'return_{days}d'
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').round(2)
        
        logger.info(f"Cleaned data: {len(self.df)} rows, {len(self.df.columns)} columns")
    
    def _add_technical_indicators(self) -> None:
        """Add technical indicators for IPOs with historical data"""
        # This is a placeholder for future technical analysis
        # You can add more indicators based on your needs
        pass
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Calculate summary statistics for the IPO data
        
        Returns:
            Dictionary with summary statistics
        """
        if self.df.empty:
            return {"error": "No data available"}
        
        summary = {
            "total_ipos": len(self.df),
            "mainboard_ipos": len(self.df[self.df.get('issue_category', '') == 'Mainboard']),
            "sme_ipos": len(self.df[self.df.get('issue_category', '') == 'SME']),
        }
        
        # Calculate average returns
        for days in RETURN_PERIODS:
            col = f'return_{days}d'
            if col in self.df.columns:
                summary[f'avg_return_{days}d'] = self.df[col].mean()
                summary[f'median_return_{days}d'] = self.df[col].median()
        
        # Calculate listing day statistics
        if 'listing_day_gain_percent' in self.df.columns:
            gains = self.df['listing_day_gain_percent'].dropna()
            summary['listing_day_avg_gain'] = gains.mean()
            summary['listing_day_median_gain'] = gains.median()
            summary['positive_listings'] = len(gains[gains > 0])
            summary['negative_listings'] = len(gains[gains < 0])
            summary['flat_listings'] = len(gains[gains == 0])
        
        return summary
    
    def get_top_performers(self, period: str = 'listing_day_gain_percent', n: int = 10) -> pd.DataFrame:
        """
        Get top performing IPOs for a given period
        
        Args:
            period: Column name for performance metric
            n: Number of top performers to return
            
        Returns:
            DataFrame with top performers
        """
        if period not in self.df.columns:
            logger.warning(f"Column '{period}' not found in data")
            return pd.DataFrame()
        
        top_df = self.df.nlargest(n, period)
        columns_to_show = ['company_name', 'nse_symbol', 'issue_price', period]
        return top_df[columns_to_show]
    
    def get_bottom_performers(self, period: str = 'listing_day_gain_percent', n: int = 10) -> pd.DataFrame:
        """
        Get bottom performing IPOs for a given period
        
        Args:
            period: Column name for performance metric
            n: Number of bottom performers to return
            
        Returns:
            DataFrame with bottom performers
        """
        if period not in self.df.columns:
            logger.warning(f"Column '{period}' not found in data")
            return pd.DataFrame()
        
        bottom_df = self.df.nsmallest(n, period)
        columns_to_show = ['company_name', 'nse_symbol', 'issue_price', period]
        return bottom_df[columns_to_show]
    
    def filter_by_category(self, category: str) -> pd.DataFrame:
        """
        Filter IPOs by category
        
        Args:
            category: Issue category (Mainboard, SME, etc.)
            
        Returns:
            Filtered DataFrame
        """
        if 'issue_category' not in self.df.columns:
            logger.warning("issue_category column not found")
            return pd.DataFrame()
        
        return self.df[self.df['issue_category'].str.contains(category, case=False, na=False)]
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter IPOs by listing date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Filtered DataFrame
        """
        if 'listing_date' not in self.df.columns:
            logger.warning("listing_date column not found")
            return pd.DataFrame()
        
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            mask = (self.df['listing_date'] >= start) & (self.df['listing_date'] <= end)
            return self.df[mask]
        except Exception as e:
            logger.error(f"Error filtering by date range: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, filepath: Optional[Path] = None) -> None:
        """
        Export DataFrame to CSV
        
        Args:
            filepath: Path to save CSV file
        """
        if filepath is None:
            filepath = OUTPUT_CSV
        
        try:
            self.df.to_csv(filepath, index=False)
            logger.success(f"Data exported to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def generate_html_report(self, filepath: Optional[Path] = None) -> None:
        """
        Generate HTML report from the data
        
        Args:
            filepath: Path to save HTML report
        """
        try:
            import weasyprint
            from jinja2 import Template
            
            # Create HTML template
            template_str = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>IPO Performance Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #4CAF50; color: white; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                    .positive { color: green; }
                    .negative { color: red; }
                    .stats { margin: 20px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>IPO Performance Report</h1>
                
                <div class="stats">
                    <h2>Summary Statistics</h2>
                    <p>Total IPOs: {{ summary.total_ipos }}</p>
                    <p>Mainboard IPOs: {{ summary.mainboard_ipos }}</p>
                    <p>SME IPOs: {{ summary.sme_ipos }}</p>
                    <p>Average Listing Day Gain: {{ "%.2f"|format(summary.listing_day_avg_gain) }}%</p>
                    <p>Positive Listings: {{ summary.positive_listings }}</p>
                    <p>Negative Listings: {{ summary.negative_listings }}</p>
                </div>
                
                <h2>Top Performers</h2>
                {{ top_performers_html|safe }}
                
                <h2>All IPOs</h2>
                {{ all_ipos_html|safe }}
            </body>
            </html>
            """
            
            template = Template(template_str)
            
            # Generate summary
            summary = self.get_summary_statistics()
            
            # Generate HTML tables
            top_performers = self.get_top_performers()
            top_performers_html = top_performers.to_html(classes='table', index=False)
            all_ipos_html = self.df.to_html(classes='table', index=False)
            
            # Render template
            html_content = template.render(
                summary=summary,
                top_performers_html=top_performers_html,
                all_ipos_html=all_ipos_html
            )
            
            # Save HTML
            if filepath is None:
                filepath = Path(__file__).parent.parent / "reports" / "ipo_report.html"
                filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.success(f"HTML report generated: {filepath}")
            
        except ImportError as e:
            logger.warning(f"HTML report generation requires additional packages: {e}")
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")