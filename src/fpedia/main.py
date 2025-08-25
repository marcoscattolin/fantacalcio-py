from src.fpedia.scraper import Scraper
from src.fpedia.data_proc import FpediaDataProcessor as DataProcessor
from src.fpedia.convenienza_calculator import calcola_convenienza
from src import config
import os
from loguru import logger

def main():

    logger.info("+++++++++++++ Starting FPEDIA analysis +++++++++++++")

    scraper = Scraper()
    scraper.scrape()
    
    data_processor = DataProcessor()
    raw_df = data_processor.load_dataframe()
    df_processed = data_processor.process_data(raw_df)
    
    df = calcola_convenienza(df_processed)
    df = df.sort_values(by="Convenienza Potenziale", ascending=False)

    # Define a comprehensive and ordered list of columns for the final output
    output_columns = [
        # Key Info
        "Nome",
        "Ruolo",
        "Squadra",
        # Calculated Indexes
        "Convenienza Potenziale",
        "Convenienza",
        "Punteggio",
        # Current Season Stats
        f"Fantamedia anno {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}",
        f"Presenze campionato corrente",
        # Previous Season Stats
        f"Fantamedia anno {config.ANNO_CORRENTE-2}-{config.ANNO_CORRENTE-1}",
        "Partite giocate",
        # Qualitative Info
        "Trend",
        "Skills",
        "Consigliato prossima giornata",
        "Buon investimento",
        "Resistenza infortuni",
        "Infortunato",
        # Legacy
        f"FM su tot gare {config.ANNO_CORRENTE-1}-{config.ANNO_CORRENTE}",
        "Presenze previste",
        "Gol previsti",
        "Assist previsti",
        "Ruolo",
        "Skills",
        "Buon investimento",
        "Resistenza infortuni",
        "Consigliato prossima giornata",
        "Nuovo acquisto",
        "Infortunato",
        "Squadra",
        "Trend",
        "Presenze campionato corrente",
    ]
    final_columns = [col for col in output_columns if col in df.columns]

    output_path = os.path.join(config.OUTPUT_DIR, "fpedia_analysis.xlsx")
    df[final_columns].to_excel(output_path, index=False)

    logger.info(f"Results saved to {output_path}, shape: {df.shape}")

    logger.info("------------- FPEDIA analysis complete -------------")


if __name__ == "__main__":
    main()