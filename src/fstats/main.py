from src.fstats.scraper import Scraper
from src.fstats.data_proc import FstatsDataProcessor as DataProcessor
from src.fstats.convenienza_calculator import ConvenienzaCalculator
from src.fstats import config
from loguru import logger
import pandas as pd


def main():
    """
    Main script to run the entire Fantacalcio analysis pipeline.
    It now runs two separate pipelines for FPEDIA and FSTATS,
    generating both performance-based and potential-based convenience indexes.
    """

    logger.info("+++++++++++++ Starting FSTATS analysis +++++++++++++")
    
    # 1. Scrape data
    scraper = Scraper()
    scraper.scrape()
    
    # 2. Process data
    data_processor = DataProcessor()
    raw_df = data_processor.load_dataframe()
    df_processed = data_processor.process_data(raw_df)
    data_processor.save_parquet(df_processed, config.PROCESSED_PLAYERS_PARQUET)

    # 3. Calculate convenience
    df = pd.read_parquet(config.PROCESSED_PLAYERS_PARQUET)
    calculator = ConvenienzaCalculator()
    df = calculator.calculate_convenienza(df)
    calculator.save_excel(df)

    logger.info("------------- FSTATS analysis complete -------------")

if __name__ == "__main__":
    main()
