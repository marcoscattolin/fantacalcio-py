from src.commons.data_proc import DataProcessor
from loguru import logger
import pandas as pd
from src import config


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

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns according to the predefined mapping.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with renamed columns
        """

        # Rename columns for clarity and consistency
        rename_map = {
            "name": "Nome",
            "team": "Squadra",
            "fantacalcioPosition": "Ruolo",  # Using the specific fantacalcio role
            "appearances": "presences",
            "pagella": "avg",
            "fantacalcioRanking": "fanta_avg",
        }
        df = df.rename(columns=rename_map)

        return df

    def _process_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        
        # Define the list of columns that should be numeric, using the NEW names
        numeric_cols = [
            "goals",
            "assists",
            "yellowCards",
            "redCards",
            "xgFromOpenPlays",
            "xA",
            "presences",
            "avg",
            "fanta_avg",
            "fantacalcioFantaindex",
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            else:
                # This warning should now only appear for genuinely missing columns
                logger.warning(
                    f"Column '{col}' not found in FSTATS data. It will be created with value 0."
                )
        
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
            df = self._process_numeric_columns(df)
            
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
