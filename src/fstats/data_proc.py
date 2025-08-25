from src.commons.data_proc import DataProcessor
from loguru import logger
import pandas as pd
from src import config


 # FSTATS columns (original names)
ORIGINAL_COLS = [
        "name", "team", "fantacalcioPosition", "appearances", "pagella",
        "fantacalcioRanking", "goals", "assists", "yellowCards", "redCards",
        "xgFromOpenPlays", "xA", "fantacalcioFantaindex"
    ]
    
RENAMED_COLS = [
        "Nome", "Squadra", "Ruolo", "presences", "avg", "fanta_avg",
        "goals", "assists", "yellowCards", "redCards", "xgFromOpenPlays",
        "xA", "fantacalcioFantaindex"
    ]

class FstatsDataProcessor(DataProcessor):

    def load_dataframe(self) -> pd.DataFrame:
        """
        Load CSV files into pandas DataFrames with error handling.
        
        Returns:
            Tuple containing (fpedia_df, fstats_df)
        """
        logger.info("Starting data loading process...")
        
        
        df = self._load_dataframe(
            config.PLAYERS_CSV, 
            "FSTATS", 
            sep=";"
        )
        
        logger.info("Data loading completed")
        return df

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
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
            df = self._process_numeric_columns(df, RENAMED_COLS)
            
            logger.info(f"FSTATS data processed successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error processing FSTATS data: {e}")
            return df


if __name__ == "__main__":

    data_processor = FstatsDataProcessor()
    df_fpedia = data_processor.load_dataframe()
    df_fpedia = data_processor.process_data(df_fpedia)
    print(df_fpedia.head())
