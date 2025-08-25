# data_processor.py
"""
Data processing module for Fantacalcio analysis.

This module handles loading, processing, and cleaning of data from FPEDIA and FSTATS sources.
"""

import pandas as pd
from loguru import logger
from typing import Tuple, List, Dict, Optional
from pathlib import Path
from src import config


# Constants for column names and processing
class ColumnNames:
    """Constants for column names used across different data sources."""
    
    # FPEDIA columns
    FPEDIA_NUMERIC_COLS = [
        f"Fantamedia anno {config.ANNO_CORRENTE-2}-{config.ANNO_CORRENTE-1}",
        "Partite giocate",
        f"Fantamedia anno {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}",
        "Presenze campionato corrente",
        "Punteggio",
        "Nuovo acquisto",
        "Buon investimento",
        "Consigliato prossima giornata",
        "Resistenza infortuni",
    ]
    
    # FSTATS columns (original names)
    FSTATS_ORIGINAL_COLS = [
        "name", "team", "fantacalcioPosition", "appearances", "pagella",
        "fantacalcioRanking", "goals", "assists", "yellowCards", "redCards",
        "xgFromOpenPlays", "xA", "fantacalcioFantaindex"
    ]
    
    # FSTATS columns (renamed)
    FSTATS_RENAMED_COLS = [
        "Nome", "Squadra", "Ruolo", "presences", "avg", "fanta_avg",
        "goals", "assists", "yellowCards", "redCards", "xgFromOpenPlays",
        "xA", "fantacalcioFantaindex"
    ]


class DataProcessor:
    """Main class for processing data from different sources."""
    
    def __init__(self):
        self.rename_map = {
            "name": "Nome",
            "team": "Squadra",
            "fantacalcioPosition": "Ruolo",
            "appearances": "presences",
            "pagella": "avg",
            "fantacalcioRanking": "fanta_avg",
        }
    
    def _load_dataframe(
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
    
    def _process_skills_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the Skills column, ensuring it exists and has valid values.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with processed Skills column
        """
        if "Skills" not in df.columns:
            df["Skills"] = "[]"
        else:
            df["Skills"] = df["Skills"].fillna("[]")
        
        return df
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns according to the predefined mapping.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with renamed columns
        """
        return df.rename(columns=self.rename_map)

    def process_fpedia_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and clean FPEDIA DataFrame.
        
        Args:
            df: Input DataFrame from FPEDIA
            
        Returns:
            Processed DataFrame
        """
        if df.empty:
            logger.warning("FPEDIA DataFrame is empty. Skipping processing.")
            return df
        
        logger.debug("Processing FPEDIA data...")
        
        try:
            df = self._process_numeric_columns(df, ColumnNames.FPEDIA_NUMERIC_COLS)
            df = self._process_skills_column(df)
            
            logger.info(f"FPEDIA data processed successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error processing FPEDIA data: {e}")
            return df
    
    def process_fstats_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and clean FSTATS DataFrame.
        
        Args:
            df: Input DataFrame from FSTATS
            
        Returns:
            Processed DataFrame
        """
        if df.empty:
            logger.warning("FSTATS DataFrame is empty. Skipping processing.")
            return df
        
        logger.debug("Processing FSTATS data...")
        
        try:
            df = self._rename_columns(df)
            df = self._process_numeric_columns(df, ColumnNames.FSTATS_RENAMED_COLS)
            
            logger.info(f"FSTATS data processed successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error processing FSTATS data: {e}")
            return df

    def load_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
            """
            Load CSV files into pandas DataFrames with error handling.
            
            Returns:
                Tuple containing (fpedia_df, fstats_df)
            """
            logger.info("Starting data loading process...")
            
            df_fpedia = self._load_dataframe(
                config.GIOCATORI_CSV, 
                "FPEDIA", 
                sep=","
            )
            df_fstats = self._load_dataframe(
                config.PLAYERS_CSV, 
                "FSTATS", 
                sep=";"
            )
            
            logger.info("Data loading completed")
            return df_fpedia, df_fstats

if __name__ == "__main__":
    
    data_processor = DataProcessor()
    df_fpedia, df_fstats = data_processor.load_dataframes()
    df_fpedia = data_processor.process_fpedia_data(df_fpedia)
    df_fstats = data_processor.process_fstats_data(df_fstats)
    print(df_fpedia.head())
    print(df_fstats.head())