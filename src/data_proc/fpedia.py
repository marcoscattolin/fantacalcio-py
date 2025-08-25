from src.data_proc import DataProcessor
from loguru import logger
import pandas as pd
from src import config


NUMERIC_COLS = [
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
    


class FpediaDataProcessor(DataProcessor):

    def load_dataframe(self) -> pd.DataFrame:
        """
        Load CSV files into pandas DataFrames with error handling.
        
        Returns:
            Tuple containing (fpedia_df, fstats_df)
        """
        logger.info("Starting data loading process...")
        
        df = self._load_dataframe(
            config.GIOCATORI_CSV, 
            "FPEDIA", 
            sep=","
        )
        
        logger.info("Data loading completed")
        return df

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
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
            df = self._process_numeric_columns(df, NUMERIC_COLS)
            df = self._process_skills_column(df)
            
            logger.info(f"FPEDIA data processed successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error processing FPEDIA data: {e}")
            return df


if __name__ == "__main__":

    data_processor = FpediaDataProcessor()
    df_fpedia = data_processor.load_dataframe()
    df_fpedia = data_processor.process_data(df_fpedia)
    print(df_fpedia.head())
