from src.fpedia.scraper import Scraper
from src.fpedia.data_proc import FpediaDataProcessor as DataProcessor
from src.fpedia.convenienza_calculator import ConvenienzaCalculator

from src.fpedia import config
from loguru import logger
import pandas as pd

def main():

    logger.info("+++++++++++++ Starting FPEDIA analysis +++++++++++++")

    # 1. Scrape data
    scraper = Scraper()
    scraper.scrape()
    
    # 2. Process data
    data_processor = DataProcessor()
    raw_df = data_processor.load_csv()
    df_processed = data_processor.process_data(raw_df)
    data_processor.save_parquet(df_processed, config.PROCESSED_GIOCATORI_PARQUET)
    
    # 3. Calculate convenience
    df = pd.read_parquet(config.PROCESSED_GIOCATORI_PARQUET)
    calculator = ConvenienzaCalculator()
    df = calculator.calculate_convenienza(df)
    calculator.save_excel(df)

    logger.info("------------- FPEDIA analysis complete -------------")


if __name__ == "__main__":
    main()