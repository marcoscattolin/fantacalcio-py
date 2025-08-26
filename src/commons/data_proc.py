# data_processor.py
"""
Data processing module for Fantacalcio analysis.

This module handles loading, processing, and cleaning of data from FPEDIA and FSTATS sources.
"""

import pandas as pd
from loguru import logger
from typing import List
from pathlib import Path


class DataProcessor:
    """Main class for processing data from different sources."""
    
    def load_csv(
        self, 
        file_path: str, 
        source_name: str, 
        sep: str = ","
    ) -> pd.DataFrame:
        """
        Load a single CSV file into a DataFrame.
        
        Args:
            file_path: Path to the CSV file
            source_name: Name of the data source for logging
            sep: CSV separator character
            
        Returns:
            Loaded DataFrame or empty DataFrame if loading fails
        """
        file_path_obj = Path(file_path)
        
        if not self._is_file_valid(file_path_obj):
            logger.warning(f"{source_name} file not found or empty: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, sep=sep)
            logger.debug(f"{source_name} DataFrame loaded successfully with {len(df)} rows")
            return df
        except pd.errors.EmptyDataError:
            logger.warning(f"{source_name} file is empty: {file_path}")
            return pd.DataFrame()
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing {source_name} file {file_path}: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected error loading {source_name} file {file_path}: {e}")
            return pd.DataFrame()
    
    def load_parquet(self, file_path: str) -> pd.DataFrame:
        """
        Load a PARQUET file into a DataFrame.
        """
        return pd.read_parquet(file_path)

    def _is_file_valid(self, file_path: Path) -> bool:
        """
        Check if a file exists and is not empty.
        
        Args:
            file_path: Path object to check
            
        Returns:
            True if file is valid, False otherwise
        """
        return file_path.exists() and file_path.stat().st_size > 0
    
    def _process_numeric_columns(self, df: pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
        """
        Convert specified columns to numeric type with error handling.
        
        Args:
            df: Input DataFrame
            numeric_cols: List of column names to convert
            
        Returns:
            DataFrame with processed numeric columns
        """
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                logger.warning(f"Column '{col}' not found. Creating with default value 0.")
                df[col] = 0
        
        return df
    
    
    def save_parquet(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Save a DataFrame to a PARQUET file.
        
        Args:
            df: Input DataFrame
            file_path: Path to the PARQUET file
        """
        df.to_parquet(file_path, index=False)
    